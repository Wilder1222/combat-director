"""Load repository helpers by explicit file location, independently of cwd."""
from __future__ import annotations

import hashlib
import importlib.util
import json
from pathlib import Path


def load_module(path: Path, label: str):
    path = Path(path).resolve()
    identity = hashlib.sha256(str(path).encode('utf-8')).hexdigest()[:16]
    spec = importlib.util.spec_from_file_location(f'{label}_{identity}', path)
    if spec is None or spec.loader is None:
        raise ValueError(f'Cannot load repository helper: {path}')
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


def read_json(path: Path):
    return json.loads(Path(path).read_text(encoding='utf-8-sig'),
                      parse_constant=lambda value: (_ for _ in ()).throw(
                          ValueError(f'Non-finite number: {value}')))
