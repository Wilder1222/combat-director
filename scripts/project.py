#!/usr/bin/env python3
"""Validate local resources and build a minimal Codex plugin archive."""

from __future__ import annotations

import argparse
import hashlib
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
RELEASE_RECEIPT = '.codex-plugin/release-manifest.json'


def content_validator():
    path = Path(__file__).resolve().with_name('validate_content.py')
    spec = importlib.util.spec_from_file_location('project_content_validator', path)
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


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
    entries = sorted((root / 'skills').rglob('SKILL.md'))
    if entries != [entry]:
        raise ValueError('Release must expose exactly one combat-director Skill')
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
        if any(part in {'examples', 'fixtures', 'tests', 'evals'} for part in path.relative_to(skill).parts):
            raise ValueError(f'Creative cases and test fixtures are not release resources: {path}')
        files.append(path)
        if path.suffix != '.md':
            continue
        content = path.read_text(encoding='utf-8')
        if '[TODO:' in content:
            raise ValueError(f'Unfinished scaffold: {path}')
    validator = content_validator()
    link_errors, _ = validator.validate_links(root, scan_paths=['skills/combat-director'])
    if link_errors:
        raise ValueError('\n'.join(link_errors))
    # A valid repository link must also remain available after runtime extraction.
    for path in files:
        if path.suffix != '.md':
            continue
        content = validator.without_fenced_code(path.read_text(encoding='utf-8'))
        for target in re.findall(r'\[[^\]\n]+\]\(([^)\n]+)\)', content):
            if urlsplit(target).scheme:
                continue
            resource = (path.parent / unquote(target.partition('#')[0])).resolve()
            if not resource.is_relative_to(skill.resolve()):
                raise ValueError(f'Skill link escapes package: {path}: {target}')
    # Import from this root so extracted release packages are checked independently.
    import importlib.util
    spec = importlib.util.spec_from_file_location('release_combat_tool', skill / 'scripts/combat_tool.py')
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    for schema_path in sorted((skill / 'assets').glob('*.schema.json')):
        module.audit_schema(module.read_json(schema_path))
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
    if output.exists():
        verify_archive(output, manifest)
    # A partial write/CRC failure must not replace the previous verified ZIP.
    fd, temporary = tempfile.mkstemp(prefix='.combat-release-', suffix='.zip', dir=dist)
    os.close(fd)
    temporary = Path(temporary)
    try:
        write_archive(root, files, temporary)
        with tempfile.TemporaryDirectory(prefix='combat-package-check-') as directory:
            staging = Path(directory).resolve()
            with zipfile.ZipFile(temporary) as archive:
                for name in archive.namelist():
                    if not (staging / name).resolve().is_relative_to(staging):
                        raise ValueError('Archive path escapes staging root')
                archive.extractall(staging)
            validate(staging)
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
    snapshot = root / 'sources/upstream/xianxia-combat-skill'
    if snapshot.exists():
        receipt = json.loads((snapshot / 'source-manifest.json').read_text(encoding='utf-8'))
        for item in receipt['files']:
            path = snapshot / item['path']
            if (path.is_symlink() or not path.resolve().is_relative_to(snapshot.resolve())
                    or hashlib.sha256(path.read_bytes()).hexdigest() != item['sha256']
                    or path.stat().st_size != item['bytes']):
                raise ValueError('Pinned xianxia source changed: ' + item['path'])
    files = validate(root)
    return files


def write_archive(root: Path, files: list[Path], output: Path):
    payload = {path.relative_to(root).as_posix(): path.read_bytes() for path in files}
    identity = json.loads((root / '.codex-plugin/plugin.json').read_text(encoding='utf-8'))
    receipt = {'format': 'combat-release/1', 'plugin': identity['name'],
               'version': identity['version'],
               'files': {name: hashlib.sha256(data).hexdigest() for name, data in payload.items()}}
    payload[RELEASE_RECEIPT] = (json.dumps(receipt, ensure_ascii=False, sort_keys=True, indent=2)+'\n').encode('utf-8')
    with zipfile.ZipFile(output, 'w', compression=zipfile.ZIP_DEFLATED, compresslevel=9) as archive:
        for name, data in sorted(payload.items()):
            # Build bytes depend on contents, not local mtimes or Windows attributes.
            info = zipfile.ZipInfo(name, date_time=(1980, 1, 1, 0, 0, 0))
            info.create_system = 3
            info.external_attr = 0o100644 << 16
            info.compress_type = zipfile.ZIP_DEFLATED
            archive.writestr(info, data, compresslevel=9)
    with zipfile.ZipFile(output) as archive:
        if archive.testzip() is not None:
            raise ValueError('Archive integrity check failed')
        expected = set(payload)
        if set(archive.namelist()) != expected:
            raise ValueError('Archive does not match release allowlist')
    verify_archive(output, identity)


def verify_archive(path: Path, identity: dict):
    """Only replace an intact artifact produced by this build contract."""
    try:
        with zipfile.ZipFile(path) as archive:
            if archive.testzip() is not None:
                raise ValueError('Archive integrity check failed')
            receipt = json.loads(archive.read(RELEASE_RECEIPT))
            if (receipt.get('format') != 'combat-release/1'
                    or receipt.get('plugin') != identity['name']
                    or receipt.get('version') != identity['version']):
                raise ValueError('Archive identity mismatch')
            expected = receipt.get('files')
            if not isinstance(expected, dict) or set(archive.namelist()) != set(expected) | {RELEASE_RECEIPT}:
                raise ValueError('Archive contains unrecognized files')
            if len(archive.namelist()) != len(expected) + 1:
                raise ValueError('Archive contains duplicate entries')
            for name, digest in expected.items():
                if hashlib.sha256(archive.read(name)).hexdigest() != digest:
                    raise ValueError('Archive contains edited files: ' + name)
    except (KeyError, json.JSONDecodeError, zipfile.BadZipFile) as error:
        raise ValueError('Existing artifact is not a recognized build; preserve it before rebuilding') from error


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
