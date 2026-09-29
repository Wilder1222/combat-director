"""Archive completed independent review batches and verify declared input hashes."""
from pathlib import Path
import json
import shutil
import sys
from archive_runs import RESULTS, pairs, read, sha


def main():
    work = Path(read(RESULTS / 'snapshot.json')['workspace'])
    batches = {'M01-M04': ['M01', 'M02', 'M03', 'M04'],
               'E05-E08': ['E05/attempt2', 'E06/attempt2', 'E07', 'E08'],
               'E09-E12': ['E09', 'E12']}
    registry = RESULTS / 'review-audit.json'
    old = read(registry) if registry.exists() else {'confirmed_terminal_batches': []}
    names = sorted(set(old['confirmed_terminal_batches']) | set(sys.argv[1:]))
    records, errors = [], []
    for name in names:
        if name not in batches:
            raise ValueError('Unexpected review batch')
        source = (work / 'reviews' / name).resolve()
        for required in ('review.json', 'review.md', 'run.json'):
            if not (source / required).is_file():
                raise ValueError('Missing completed review artifact')
        allowed = {(work / 'runs' / case / filename).resolve()
                   for case in batches[name] for filename in ('request.txt', 'answer.md', 'run.json')}
        for case in batches[name]:
            allowed.update(p.resolve() for p in (work / 'runs' / case).glob('*.png'))
        skill = work / 'candidate/skills/combat-director'
        if name == 'M01-M04':
            allowed.update((skill / p).resolve() for p in ('SKILL.md', 'references/motion-blur.md', 'references/platforms.md', 'references/prompt-craft.md'))
        else:
            allowed.update(p.resolve() for p in skill.rglob('*') if p.is_file())
            for case in batches[name]:
                allowed.update(p.resolve() for p in (work / 'runs' / case).rglob('*') if p.is_file())
        checks = []
        for pointer, raw_path, expected in pairs(read(source / 'run.json')):
            path = Path(raw_path)
            if not path.is_absolute():
                path = source / path
            path = path.resolve()
            scoped = path in allowed or path.is_relative_to(source)
            actual = sha(path) if path.is_file() else None
            mutable = path == source / 'run.json'
            passed = scoped and (actual == expected or mutable)
            check = {'pointer': pointer, 'path': str(path), 'expected_sha256': expected,
                     'actual_sha256': actual, 'scope_allowed': scoped, 'historical_mutable_log': mutable, 'passed': passed}
            checks.append(check)
            if not passed:
                errors.append({'batch': name, **check})
        if not checks:
            errors.append({'batch': name, 'error': 'No parseable path/hash records'})
        archived = []
        for path in sorted(source.rglob('*')):
            if not path.is_file():
                continue
            dest = RESULTS / 'reviews' / name / path.relative_to(source)
            dest.parent.mkdir(parents=True, exist_ok=True)
            if dest.exists() and dest.read_bytes() != path.read_bytes():
                raise ValueError('Archived review changed')
            if not dest.exists():
                shutil.copyfile(path, dest)
            archived.append({'path': dest.relative_to(RESULTS).as_posix(), 'sha256': sha(dest)})
        records.append({'batch': name, 'checks': checks, 'archived': archived})
    record = {'format': 'combat-extension-review-audit/1', 'confirmed_terminal_batches': names,
              'batches': records, 'errors': errors, 'passed': not errors,
              'limits': 'Declared reads and byte preservation; not OS access tracing or semantic grading.'}
    registry.write_text(json.dumps(record, ensure_ascii=False, indent=2)+'\n', encoding='utf-8')
    print(json.dumps({'batches': names, 'path_hash_pairs': sum(len(r['checks']) for r in records), 'errors': errors}, ensure_ascii=False))
    return 0 if not errors else 1


if __name__ == '__main__':
    raise SystemExit(main())
