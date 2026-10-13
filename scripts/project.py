#!/usr/bin/env python3
"""Validate local resources and build a minimal Codex plugin archive."""
from __future__ import annotations

import argparse
import hashlib
import importlib.util
import os
import sys
import zipfile
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]

# Explicit package loading keeps both file-based imports and copied CLI invocations
# independent of cwd and similarly named modules from another checkout.
_package_path = Path(__file__).resolve().with_name('combat_project')
_package_name = '_combat_project_' + hashlib.sha256(str(_package_path).encode('utf-8')).hexdigest()[:16]
if _package_name not in sys.modules:
    _spec = importlib.util.spec_from_file_location(_package_name, _package_path / '__init__.py',
                                                submodule_search_locations=[str(_package_path)])
    if _spec is None or _spec.loader is None:
        raise ValueError(f'Cannot load maintenance package: {_package_path}')
    _package = importlib.util.module_from_spec(_spec)
    sys.modules[_package_name] = _package
    _spec.loader.exec_module(_package)
_archive = __import__(_package_name + '.archive', fromlist=['archive'])
_loading = __import__(_package_name + '.loading', fromlist=['loading'])
_runtime = __import__(_package_name + '.runtime', fromlist=['runtime'])
_sources = __import__(_package_name + '.sources', fromlist=['sources'])
RELEASE_RECEIPT = _archive.RELEASE_RECEIPT


def content_validator():
    return _loading.load_module(Path(__file__).resolve().with_name('validate_content.py'),
                                'project_content_validator')


def validate(root: Path) -> list[Path]:
    """Validate runtime resources independently of repository source archives."""
    return _runtime.validate(root, content_validator())


def verify_sources(root: Path) -> list[dict]:
    """Shared build/release source check; return attachment evidence rows."""
    return _sources.verify_sources(root)


def validate_release(root: Path) -> list[Path]:
    """Repository release preflight; runtime-only validation stays independent."""
    _sources.validate_generated(root)
    verify_sources(root)
    return validate(root)


def build(root: Path) -> Path:
    return _archive.build(root, validate_release, validate)


def write_archive(root: Path, files: list[Path], output: Path):
    return _archive.write_archive(root, files, output)


def verify_archive(path: Path, identity: dict):
    return _archive.verify_archive(path, identity)


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
