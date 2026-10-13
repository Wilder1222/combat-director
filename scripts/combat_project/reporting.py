"""Capture check evidence with consistent UTF-8 child-process encoding."""
from __future__ import annotations

import hashlib
import os
import subprocess
from pathlib import Path


def sha(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def input_fingerprints(root: Path) -> dict[str, str]:
    """Bind checks to runtime, maintenance code, fixtures and editorial inputs."""
    paths = set()
    for folder in ('skills/combat-director', 'scripts', 'tests', 'sources/editorial', '.codex-plugin'):
        paths.update(path for path in (root / folder).rglob('*')
                     if path.is_file() and path.suffix in {'.py', '.json', '.yaml', '.md', '.txt'}
                     and '__pycache__' not in path.parts)
    for folder in ('sources/upstream', 'sources/attachments'):
        paths.update(path for path in (root / folder).rglob('*')
                     if path.is_file() and '__pycache__' not in path.parts)
    return {path.relative_to(root).as_posix(): sha(path) for path in sorted(paths)}


class CheckRunner:
    def __init__(self, root: Path):
        self.root = root
        self.records = []

    def __call__(self, label, args, expected=0, cwd=None):
        process = subprocess.run([str(arg) for arg in args],
                                 cwd=self.root if cwd is None else cwd,
                                 capture_output=True, env={**os.environ, 'PYTHONUTF8': '1'},
                                 encoding='utf-8', errors='strict')
        record = {'check': label, 'exit_code': process.returncode,
                  'expected_exit_code': expected, 'passed': process.returncode == expected,
                  'stdout': process.stdout, 'stderr': process.stderr}
        self.records.append(record)
        if not record['passed']:
            raise ValueError(f'{label}: {process.stdout}\n{process.stderr}')
        return record
