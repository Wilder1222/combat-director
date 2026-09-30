#!/usr/bin/env python3
"""Validate local resources and build a minimal Codex plugin archive."""

from __future__ import annotations

import argparse
import json
import importlib.util
import os
import re
import sys
import tempfile
import zipfile
from pathlib import Path
from urllib.parse import unquote, urlsplit

ROOT = Path(__file__).resolve().parents[1]


def validate(root: Path) -> list[Path]:
    """Return the validated release allowlist; never include private sources."""
    manifest_path = root / '.codex-plugin/plugin.json'
    manifest = json.loads(manifest_path.read_text(encoding='utf-8'))
    if manifest.get('name') != 'combat-director':
        raise ValueError('Unexpected plugin name')
    if not re.fullmatch(r'\d+\.\d+\.\d+', manifest.get('version', '')):
        raise ValueError('Expected a numeric release version')
    if manifest.get('skills') != './skills/':
        raise ValueError('Plugin must point to ./skills/')
    skill = root / 'skills/combat-director'
    entry = skill / 'SKILL.md'
    text = entry.read_text(encoding='utf-8')
    frontmatter = re.match(r'\A---\n(.*?)\n---\n', text, re.S)
    if not frontmatter or 'name: combat-director' not in frontmatter[1]:
        raise ValueError('Missing skill frontmatter or incorrect name')
    if not re.search(r'^description: \S', frontmatter[1], re.M):
        raise ValueError('Missing skill description')
    if f'version: "{manifest["version"]}"' not in frontmatter[1]:
        raise ValueError('Skill and plugin versions differ')
    ui = (skill / 'agents/openai.yaml').read_text(encoding='utf-8')
    if '$combat-director' not in ui:
        raise ValueError('UI prompt must invoke the skill')
    prompts = manifest.get('interface', {}).get('defaultPrompt')
    if not isinstance(prompts, list) or not 1 <= len(prompts) <= 3:
        raise ValueError('Expected 1-3 plugin starter prompts')
    if any(not isinstance(p, str) or not p.strip() or len(p) > 128 for p in prompts):
        raise ValueError('Invalid plugin starter prompt')
    files = [manifest_path]
    for path in sorted(skill.rglob('*')):
        if path.is_symlink():
            raise ValueError(f'Symlink is not a release resource: {path}')
        if not path.is_file() or '__pycache__' in path.parts:
            continue
        if path.suffix not in {'.md', '.yaml', '.json', '.txt', '.py'}:
            raise ValueError(f'Unexpected release file type: {path}')
        files.append(path)
        if path.suffix != '.md':
            continue
        content = path.read_text(encoding='utf-8')
        if '[TODO:' in content:
            raise ValueError(f'Unfinished scaffold: {path}')
        for target in re.findall(r'\[[^\]]*\]\(([^)]+)\)', content):
            target = target.strip('<>')
            if urlsplit(target).scheme or target.startswith('#'):
                continue
            resource = (path.parent / unquote(target.split('#')[0])).resolve()
            if not resource.is_relative_to(skill.resolve()):
                raise ValueError(f'Skill link escapes package: {path}: {target}')
            if not resource.is_file():
                raise ValueError(f'Broken skill link: {path}: {target}')
    # Import from this root so extracted release packages are checked independently.
    import importlib.util
    spec = importlib.util.spec_from_file_location('release_combat_tool', skill / 'scripts/combat_tool.py')
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    for schema_path in sorted((skill / 'assets').glob('*.schema.json')):
        module.audit_schema(module.read_json(schema_path))
    for path in sorted((skill / 'examples').glob('*.plan.json')):
        plan = module.read_json(path)
        module.validate(plan)
        saved = path.with_name(path.name.replace('.plan.json', '.prompt.txt'))
        if saved.read_text(encoding='utf-8') != module.prompt(plan):
            raise ValueError(f'Prompt out of sync: {saved}')
    for path in sorted((skill / 'examples').glob('*.compact.json')):
        plan = module.read_json(path.with_name(path.name.replace('.compact.json', '.plan.json')))
        module.validate(plan)
        rendered = module.compact_prompt(plan, module.read_json(path))
        saved = path.with_suffix('.txt')
        if saved.read_text(encoding='utf-8') != rendered:
            raise ValueError(f'Compact prompt out of sync: {saved}')
    library_spec = importlib.util.spec_from_file_location('release_library_tool', skill / 'scripts/library_tool.py')
    library = importlib.util.module_from_spec(library_spec)
    library_spec.loader.exec_module(library)
    catalog = library.load_catalog(skill / 'library/catalog.json')
    library.load_items(catalog, skill / 'library/items.json')
    return files


def build(root: Path) -> Path:
    files = validate_release(root)
    manifest = json.loads(files[0].read_text(encoding='utf-8'))
    dist = root / 'dist'
    dist.mkdir(exist_ok=True)
    output = dist / f"{manifest['name']}-{manifest['version']}.zip"
    # A partial write/CRC failure must not replace the previous verified ZIP.
    fd, temporary = tempfile.mkstemp(prefix='.combat-release-', suffix='.zip', dir=dist)
    os.close(fd)
    temporary = Path(temporary)
    try:
        write_archive(root, files, temporary)
        # Keep an identical verified archive in place. Apart from preserving its
        # mtime, this avoids unnecessary Windows replacement contention with
        # readers of the previous build. Changed bytes still require os.replace.
        if not output.exists() or output.read_bytes() != temporary.read_bytes():
            os.replace(temporary, output)
    finally:
        temporary.unlink(missing_ok=True)
    return output


def validate_release(root: Path) -> list[Path]:
    """Repository release preflight; runtime-only validation stays independent."""
    generator = root / 'scripts/build_arvin_library.py'
    if not generator.is_file():
        raise ValueError('Formal builds require the repository generator and pinned sources')
    spec = importlib.util.spec_from_file_location('project_arvin_builder', generator)
    builder = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(builder)
    builder.check_outputs(root, builder.render(root))
    motion_generator = root / 'scripts/build_motion_examples.py'
    if not motion_generator.is_file():
        raise ValueError('Formal builds require the motion example generator and reviewed sources')
    motion_spec = importlib.util.spec_from_file_location('project_motion_builder', motion_generator)
    motion_builder = importlib.util.module_from_spec(motion_spec)
    motion_spec.loader.exec_module(motion_builder)
    motion_builder.check_outputs(root, motion_builder.render(root))
    files = validate(root)
    return files


def write_archive(root: Path, files: list[Path], output: Path):
    with zipfile.ZipFile(output, 'w', compression=zipfile.ZIP_DEFLATED, compresslevel=9) as archive:
        for path in files:
            # Build bytes depend on contents, not local mtimes or Windows attributes.
            info = zipfile.ZipInfo(path.relative_to(root).as_posix(), date_time=(1980, 1, 1, 0, 0, 0))
            info.create_system = 3
            info.external_attr = 0o100644 << 16
            info.compress_type = zipfile.ZIP_DEFLATED
            archive.writestr(info, path.read_bytes(), compresslevel=9)
    with zipfile.ZipFile(output) as archive:
        if archive.testzip() is not None:
            raise ValueError('Archive integrity check failed')
        expected = {p.relative_to(root).as_posix() for p in files}
        if set(archive.namelist()) != expected:
            raise ValueError('Archive does not match release allowlist')


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('command', choices=['validate', 'validate-release', 'build'])
    args = parser.parse_args()
    try:
        if args.command == 'build':
            print(build(ROOT))
        elif args.command == 'validate-release':
            print(f'PASS: {len(validate_release(ROOT))} release files; pinned sources and generated outputs valid')
        else:
            print(f'PASS: {len(validate(ROOT))} release files; resource links valid')
    except (ValueError, OSError, zipfile.BadZipFile) as error:
        print(f'FAIL: {error}', file=sys.stderr)
        return 1
    return 0


if __name__ == '__main__':
    raise SystemExit(main())
