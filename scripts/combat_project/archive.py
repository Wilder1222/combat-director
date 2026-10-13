"""Build deterministic archives with receipts and protected atomic replacement."""
from __future__ import annotations

import hashlib
import json
import os
import tempfile
import zipfile
from pathlib import Path

RELEASE_RECEIPT = '.codex-plugin/release-manifest.json'


def build(root: Path, release_validator, runtime_validator) -> Path:
    root = Path(root)
    files = release_validator(root)
    manifest = json.loads(files[0].read_text(encoding='utf-8'))
    dist = root / 'dist'
    dist.mkdir(exist_ok=True)
    output = dist / f"{manifest['name']}-{manifest['version']}.zip"
    if output.exists():
        verify_archive(output, manifest)
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
            runtime_validator(staging)
        # Preserve identical archives and their mtime; readers may hold them open
        # on Windows. Changed bytes still require atomic replacement.
        if not output.exists() or output.read_bytes() != temporary.read_bytes():
            os.replace(temporary, output)
    finally:
        temporary.unlink(missing_ok=True)
    return output


def write_archive(root: Path, files: list[Path], output: Path):
    payload = {path.relative_to(root).as_posix(): path.read_bytes() for path in files}
    identity = json.loads((root / '.codex-plugin/plugin.json').read_text(encoding='utf-8'))
    receipt = {'format': 'combat-release/1', 'plugin': identity['name'],
               'version': identity['version'],
               'files': {name: hashlib.sha256(data).hexdigest() for name, data in payload.items()}}
    payload[RELEASE_RECEIPT] = (json.dumps(receipt, ensure_ascii=False, sort_keys=True, indent=2)+'\n').encode('utf-8')
    with zipfile.ZipFile(output, 'w', compression=zipfile.ZIP_DEFLATED, compresslevel=9) as archive:
        for name, data in sorted(payload.items()):
            info = zipfile.ZipInfo(name, date_time=(1980, 1, 1, 0, 0, 0))
            info.create_system = 3
            info.external_attr = 0o100644 << 16
            info.compress_type = zipfile.ZIP_DEFLATED
            archive.writestr(info, data, compresslevel=9)
    with zipfile.ZipFile(output) as archive:
        if archive.testzip() is not None:
            raise ValueError('Archive integrity check failed')
        if set(archive.namelist()) != set(payload):
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
