"""Archive only explicitly confirmed-terminal review batches and audit logs."""
from pathlib import Path
import hashlib
import json
import re
import shutil
import sys


ROOT = Path(__file__).resolve().parents[2]
RESULTS = ROOT / 'evals/results/library-0.9.0'
WORK = Path('D:/Temp/combat-library-behavior-j75bzt8f/reviews')


def sha(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


def entries(value, pointer=''):
    if isinstance(value, dict):
        path = value.get('path') or value.get('file') or value.get('file_path')
        digest = value.get('sha256') or value.get('hash')
        if isinstance(path, str) and isinstance(digest, str) and re.fullmatch(r'[a-fA-F0-9]{64}', digest):
            yield pointer, path, digest.lower()
        for key, child in value.items():
            yield from entries(child, pointer + '/' + key)
    elif isinstance(value, list):
        for index, child in enumerate(value):
            yield from entries(child, pointer + '/' + str(index))


def main():
    target = RESULTS / 'review-audit.json'
    old = json.loads(target.read_text(encoding='utf-8')) if target.exists() else {'batches': []}
    names = sorted({b['batch'] for b in old['batches']} | set(sys.argv[1:]))
    batches, errors = [], []
    for name in names:
        if name not in ('L01-L03', 'L04-L06', 'L07-L09'):
            raise ValueError('Unexpected review batch')
        source = WORK / name
        for required in ('review.json', 'review.md', 'run.json'):
            if not (source / required).is_file():
                raise ValueError('Missing completed artifact: ' + str(source / required))
        first, last = int(name[1:3]), int(name[-2:])
        allowed = {str((RESULTS / 'anonymous-input' / f'L{i:02}' / filename).resolve()).lower()
            for i in range(first, last+1) for filename in ('request.txt', 'A.md', 'B.md')}
        allowed |= {str((RESULTS / 'anonymous-input/reference' / filename).resolve()).lower()
            for filename in ('upstream-source.md', 'LICENSE', 'provenance.json')}
        checks = []
        log = json.loads((source / 'run.json').read_text(encoding='utf-8-sig'))
        for pointer, raw_path, expected in entries(log):
            path = Path(raw_path)
            if not path.is_absolute():
                path = RESULTS / 'anonymous-input' / path
            path = path.resolve()
            internal = path.is_relative_to(source.resolve())
            in_scope = str(path).lower() in allowed or internal
            actual = sha(path) if path.is_file() else None
            mutable_log = internal and path.name == 'run.json'
            passed = in_scope and (actual == expected or mutable_log)
            entry = {'pointer': pointer, 'path': str(path), 'expected_sha256': expected,
                'actual_sha256': actual, 'scope_allowed': in_scope,
                'historical_mutable_log': mutable_log, 'passed': passed}
            checks.append(entry)
            if not passed:
                errors.append({'batch': name, **entry})
        if not checks:
            errors.append({'batch': name, 'error': 'No parseable path/hash records; manual audit needed.'})
        archived = []
        for file in source.rglob('*'):
            if not file.is_file():
                continue
            dest = RESULTS / 'reviews' / name / file.relative_to(source)
            dest.parent.mkdir(parents=True, exist_ok=True)
            if dest.exists() and dest.read_bytes() != file.read_bytes():
                raise ValueError('Archived review changed: ' + str(dest))
            if not dest.exists():
                shutil.copyfile(file, dest)
            archived.append({'path': dest.relative_to(RESULTS).as_posix(), 'sha256': sha(dest)})
        batches.append({'batch': name, 'checks': checks, 'archived': archived})
    record = {'format': 'combat-library-review-audit/1', 'confirmed_terminal_batches': names,
        'batches': batches, 'errors': errors, 'passed': not errors,
        'scope': 'Hashes, declared input scope and exact artifact preservation. Self-reported reading is not OS-level tracing or proof of judgment quality.'}
    target.write_text(json.dumps(record, ensure_ascii=False, indent=2)+'\n', encoding='utf-8')
    print(json.dumps({'batches': len(batches), 'path_hash_pairs': sum(len(b['checks']) for b in batches), 'errors': errors}, ensure_ascii=False))
    return 0 if not errors else 1


if __name__ == '__main__':
    raise SystemExit(main())
