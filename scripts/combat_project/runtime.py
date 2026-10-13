"""Validate the runtime allowlist without requiring repository source archives."""
from __future__ import annotations

import re
import subprocess
import sys
from pathlib import Path
from urllib.parse import unquote, urlsplit

from .loading import load_module, read_json


def _validate_core_cli(root: Path, skill: Path):
    """Check core imports in a fresh interpreter; media dependencies stay optional."""
    cli = skill / 'scripts/combat_tool.py'
    resource = cli.relative_to(root).as_posix()
    try:
        result = subprocess.run([sys.executable, '-X', 'utf8', str(cli.resolve()), '--help'],
                                cwd=root.resolve(), capture_output=True, encoding='utf-8',
                                timeout=30)
    except subprocess.TimeoutExpired as error:
        raise ValueError(f'Core CLI import check timed out: {resource}') from error
    if result.returncode:
        detail = (result.stderr or result.stdout).strip()
        raise ValueError(f'Core CLI cannot be imported: {resource}\n{detail}')


def validate(root: Path, content_validator) -> list[Path]:
    """Return the validated release allowlist; never include private sources."""
    root = Path(root)
    manifest_path = root / '.codex-plugin/plugin.json'
    manifest = read_json(manifest_path)
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
        if path.suffix == '.py':
            # Compile every shipped Python resource without executing optional
            # media tools or depending on their locally installed libraries.
            try:
                compile(path.read_bytes(), str(path), 'exec')
            except (SyntaxError, UnicodeError, ValueError) as error:
                resource = path.relative_to(root).as_posix()
                raise ValueError(f'Invalid Python release resource: {resource}: {error}') from error
        if path.suffix == '.md' and '[TODO:' in path.read_text(encoding='utf-8'):
            raise ValueError(f'Unfinished scaffold: {path}')
    link_errors, _ = content_validator.validate_links(root, scan_paths=['skills/combat-director'])
    if link_errors:
        raise ValueError('\n'.join(link_errors))
    # A repository link must remain available after runtime extraction.
    for path in files:
        if path.suffix != '.md':
            continue
        content = content_validator.without_fenced_code(path.read_text(encoding='utf-8'))
        for target in re.findall(r'\[[^\]\n]+\]\(([^)\n]+)\)', content):
            if urlsplit(target).scheme:
                continue
            resource = (path.parent / unquote(target.partition('#')[0])).resolve()
            if not resource.is_relative_to(skill.resolve()):
                raise ValueError(f'Skill link escapes package: {path}: {target}')
    _validate_core_cli(root, skill)
    # Load the audited subset directly. Importing the main CLI would reuse cached
    # sibling modules when multiple copied packages are checked in one process.
    schema_checker = load_module(skill / 'scripts/combat_schema.py', 'release_schema')
    for schema_path in sorted((skill / 'assets').glob('*.schema.json')):
        schema_checker.audit_schema(read_json(schema_path))
    library = load_module(skill / 'scripts/library_tool.py', 'release_library_tool')
    catalog = library.load_catalog(skill / 'library/catalog.json')
    library.load_items(catalog, skill / 'library/items.json')
    return files
