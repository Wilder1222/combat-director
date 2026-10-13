"""Check pinned source receipts and generated outputs before formal builds."""
from __future__ import annotations

import hashlib
import re
from pathlib import Path, PurePosixPath

from .loading import load_module, read_json

SNAPSHOTS = (
    ('sources/upstream/arvin-seedance', 'manifest.json', 'name'),
    ('sources/upstream/xianxia-combat-skill', 'source-manifest.json', 'path'),
)


def _source_file(root: Path, folder: Path, name: str) -> Path:
    if not isinstance(name, str) or not name or '\\' in name or ':' in name:
        raise ValueError(f'Invalid source receipt path: {name!r}')
    relative = PurePosixPath(name)
    if relative.is_absolute() or '..' in relative.parts or relative.as_posix() != name:
        raise ValueError(f'Invalid source receipt path: {name!r}')
    target = folder.joinpath(*relative.parts)
    if not target.resolve().is_relative_to(folder.resolve()):
        raise ValueError(f'Source receipt path escapes its batch: {name}')
    for path in (target, *target.parents):
        if path == root:
            break
        if path.is_symlink() or getattr(path, 'is_junction', lambda: False)():
            raise ValueError(f'Linked source receipt resource: {name}')
    if not target.is_file():
        raise ValueError(f'Missing source receipt resource: {name}')
    return target


def verify_manifest(root: Path, manifest: Path, name_key: str) -> int:
    """Verify one immutable batch, including receipt paths and duplicate rows."""
    manifest = _source_file(root, manifest.parent, manifest.name)
    receipt = read_json(manifest)
    files = receipt.get('files') if isinstance(receipt, dict) else None
    if not isinstance(files, list):
        raise ValueError(f'Invalid source receipt: {manifest.relative_to(root)}')
    seen = set()
    for item in files:
        if not isinstance(item, dict):
            raise ValueError('Invalid source receipt row')
        name = item.get(name_key)
        path = _source_file(root, manifest.parent, name)
        if name in seen:
            raise ValueError(f'Duplicate source receipt path: {name}')
        seen.add(name)
        expected = item.get('sha256')
        size = item.get('bytes')
        if (not isinstance(expected, str) or not re.fullmatch(r'[a-f0-9]{64}', expected)
                or type(size) is not int or size < 0):
            raise ValueError(f'Invalid source receipt fingerprint: {name}')
        data = path.read_bytes()
        if hashlib.sha256(data).hexdigest() != expected or len(data) != size:
            raise ValueError(f'Source fingerprint changed: {path.relative_to(root).as_posix()}')
    return len(files)


def verify_sources(root: Path) -> list[dict]:
    """Verify fixed snapshots and attachments; return attachment report rows."""
    root = Path(root).resolve()
    for relative, receipt_name, name_key in SNAPSHOTS:
        folder = root / relative
        if folder.exists() or folder.is_symlink():
            verify_manifest(root, folder / receipt_name, name_key)
    batches = []
    attachments = root / 'sources/attachments'
    if attachments.is_symlink() or getattr(attachments, 'is_junction', lambda: False)():
        raise ValueError('Linked source attachment directory')
    for manifest in sorted(attachments.glob('*/manifest.json')):
        count = verify_manifest(root, manifest, 'name')
        batches.append({'manifest': manifest.relative_to(root).as_posix(), 'files_checked': count})
    return batches


def validate_generated(root: Path):
    root = Path(root)
    generator = root / 'scripts/build_arvin_library.py'
    if not generator.is_file():
        raise ValueError('Formal builds require the repository generator and pinned sources')
    builder = load_module(generator, 'project_arvin_builder')
    builder.check_outputs(root, builder.render(root))
