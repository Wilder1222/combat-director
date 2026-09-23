#!/usr/bin/env python3
"""Build a standalone Markdown handoff and an unverified LibTV import candidate."""

from __future__ import annotations

import re
import zipfile
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
SOURCE = Path('adapters/libtv/combat-director-libtv/SKILL.md')


def build(root: Path) -> list[Path]:
    source = root / SOURCE
    if source.is_symlink():
        raise ValueError('Skill source must be a regular file')
    text = source.read_text(encoding='utf-8')
    match = re.fullmatch(r'---\n(.*?)\n---\n(\s*\S.*)', text, re.S)
    if not match:
        raise ValueError('Expected frontmatter followed by a non-empty body')
    metadata, body = match.groups()
    if not re.search(r'^name: combat-director-libtv$', metadata, re.M):
        raise ValueError('Unexpected skill name')
    if not re.search(r'^description: \S.+$', metadata, re.M):
        raise ValueError('Missing description')
    version = re.search(r'^  version: "(\d+\.\d+\.\d+-libtv\.\d+)"$', metadata, re.M)
    if not version:
        raise ValueError('Missing LibTV adapter version')
    # The first adapter deliberately has no external resource dependencies.
    if re.search(r'\[[^\]]*\]\([^)]+\)', body):
        raise ValueError('Standalone skill must not depend on linked resources')
    if '[TODO:' in text:
        raise ValueError('Unfinished scaffold')

    output = root / 'dist/libtv'
    output.mkdir(parents=True, exist_ok=True)
    stem = f'combat-director-libtv-{version[1]}'
    markdown = output / f'{stem}.md'
    content = output / f'{stem}.content.md'
    archive = output / f'{stem}.zip'
    data = text.encode('utf-8')
    markdown.write_bytes(data)
    content.write_bytes((body.strip() + '\n').encode('utf-8'))
    with zipfile.ZipFile(archive, 'w', compression=zipfile.ZIP_DEFLATED) as package:
        info = zipfile.ZipInfo('SKILL.md', date_time=(1980, 1, 1, 0, 0, 0))
        info.create_system = 3
        info.external_attr = 0o100644 << 16
        info.compress_type = zipfile.ZIP_DEFLATED
        package.writestr(info, data)
    with zipfile.ZipFile(archive) as package:
        if package.namelist() != ['SKILL.md'] or package.read('SKILL.md') != data:
            raise ValueError('Archive does not match the standalone source')
        if package.testzip() is not None:
            raise ValueError('Archive integrity check failed')
    return [markdown, content, archive]


if __name__ == '__main__':
    for path in build(ROOT):
        print(path)
    print('Local build only: LibTV import and generation remain unverified.')
