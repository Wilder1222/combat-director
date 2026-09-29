"""Preserve confirmed-terminal executions; audit frozen inputs and declared reads."""
from pathlib import Path
import hashlib
import json
import re
import shutil
import sys

ROOT = Path(__file__).resolve().parents[2]
RESULTS = ROOT / 'evals/results/extension-0.9.1'


def read(path):
    return json.loads(path.read_text(encoding='utf-8-sig'))


def sha(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


def pairs(value, pointer=''):
    if isinstance(value, dict):
        path = value.get('path') or value.get('file') or value.get('file_path')
        digest = value.get('sha256') or value.get('hash')
        if isinstance(path, str) and isinstance(digest, str) and re.fullmatch(r'[a-fA-F0-9]{64}', digest):
            yield pointer, path, digest.lower()
        for key, child in value.items():
            yield from pairs(child, pointer + '/' + key)
    elif isinstance(value, list):
        for index, child in enumerate(value):
            yield from pairs(child, pointer + '/' + str(index))


def main():
    snapshot = read(RESULTS / 'snapshot.json')
    work = Path(snapshot['workspace'])
    case_inputs = {v['id']: v for v in snapshot['inputs']}
    registry = RESULTS / 'completed-runs.json'
    old = read(registry) if registry.exists() else {'confirmed_terminal_cases': []}
    names = sorted(set(old['confirmed_terminal_cases']) | set(sys.argv[1:]))
    if any(not re.fullmatch(r'(M0[1-4]|E0[5-9]|E12)(@attempt2)?', name) or name.split('@')[0] not in case_inputs for name in names):
        raise ValueError('Unknown case ID')
    errors, frozen_checks = [], []
    frozen = [(ROOT / snapshot['archive'], snapshot['archive_sha256']),
              (RESULTS / 'cases.json', snapshot['cases_sha256'])]
    frozen += [(work / 'candidate' / v['path'], v['sha256']) for v in snapshot['runtime_files']]
    for name, entry in case_inputs.items():
        frozen.append((work / 'runs' / name / 'request.txt', entry['request_sha256']))
        frozen += [(work / 'runs' / name / f['path'], f['sha256']) for f in entry['fixtures']]
    for path, expected in frozen:
        actual = sha(path) if path.is_file() else None
        check = {'path': str(path), 'expected_sha256': expected, 'actual_sha256': actual, 'passed': actual == expected}
        frozen_checks.append(check)
        if not check['passed']:
            errors.append(check)
    runs = []
    for name in names:
        case_id, _, attempt = name.partition('@')
        source = (work / 'runs' / case_id / attempt).resolve()
        for filename in ('answer.md', 'run.json'):
            if not (source / filename).is_file():
                raise ValueError('Missing completed artifact: ' + str(source / filename))
        checks = []
        for pointer, raw_path, expected in pairs(read(source / 'run.json')):
            path = Path(raw_path)
            if not path.is_absolute():
                path = source / path
            path = path.resolve()
            in_scope = path.is_relative_to(source) or path.is_relative_to((work / 'candidate').resolve())
            mutable = path == source / 'run.json'
            actual = sha(path) if path.is_file() else None
            passed = in_scope and (actual == expected or mutable)
            check = {'pointer': pointer, 'path': str(path), 'expected_sha256': expected,
                     'actual_sha256': actual, 'scope_allowed': in_scope,
                     'historical_mutable_log': mutable, 'passed': passed}
            checks.append(check)
            if not passed:
                errors.append({'case': name, **check})
        if not checks:
            errors.append({'case': name, 'error': 'No parseable path/hash records'})
        files = []
        for path in sorted(source.rglob('*')):
            if not path.is_file():
                continue
            dest = RESULTS / 'raw' / name.replace('@', '-') / path.relative_to(source)
            dest.parent.mkdir(parents=True, exist_ok=True)
            if dest.exists() and dest.read_bytes() != path.read_bytes():
                raise ValueError('Archived artifact changed: ' + str(dest))
            if not dest.exists():
                shutil.copyfile(path, dest)
            files.append({'path': dest.relative_to(RESULTS).as_posix(), 'sha256': sha(dest)})
        runs.append({'id': name, 'declared_reads_and_artifacts': checks, 'archived': files})
    record = {'format': 'combat-extension-audit/1', 'confirmed_terminal_cases': names,
              'frozen_input_checks': frozen_checks, 'runs': runs, 'errors': errors, 'passed': not errors,
              'limits': 'Terminal completion was confirmed by the parent before invocation. Hash/scope checks do not prove reading or semantic quality; logs are self-reported, not OS access tracing.'}
    (RESULTS / 'parent-audit.json').write_text(json.dumps(record, ensure_ascii=False, indent=2)+'\n', encoding='utf-8')
    registry.write_text(json.dumps({'confirmed_terminal_cases': names, 'review_status': 'not_complete'}, indent=2)+'\n', encoding='utf-8')
    print(json.dumps({'completed': names, 'frozen_checks': len(frozen_checks),
                      'declared_path_hash_pairs': sum(len(r['declared_reads_and_artifacts']) for r in runs),
                      'errors': errors}, ensure_ascii=False))
    return 0 if not errors else 1


if __name__ == '__main__':
    raise SystemExit(main())
