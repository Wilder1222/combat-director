"""Prepare anonymous, traceable answers from completed frozen-library runs.

This is evaluation tooling, not part of the distributable skill. It changes
only line endings and explicit condition/version paths; raw evidence is kept.
"""
from pathlib import Path
import hashlib
import json


ROOT = Path(__file__).resolve().parents[2]
RESULTS = ROOT / 'evals/results/library-0.9.0'


def digest(data):
    return hashlib.sha256(data).hexdigest()


def main():
    completed = set(json.loads((RESULTS / 'completed-runs.json').read_text(encoding='utf-8-sig')))
    mapping = json.loads((RESULTS / 'blind-mapping.json').read_text(encoding='utf-8-sig'))['mapping']
    records = []
    for case in mapping:
        # A pair is ready only after both executions are authoritatively terminal.
        if not all(Path(item['raw_run']).name in completed for item in case['answers'].values()):
            continue
        for label, item in case['answers'].items():
            source = RESULTS / item['raw_run'] / 'answer.md'
            raw = source.read_bytes()
            content = raw.decode('utf-8-sig').replace('\r\n', '\n')
            changes = []
            for condition in ('baseline', 'candidate'):
                for root in (
                    'D:/Temp/combat-library-behavior-j75bzt8f/' + condition + '/',
                    'D:\\Temp\\combat-library-behavior-j75bzt8f\\' + condition + '\\',
                ):
                    count = content.count(root)
                    if count:
                        content = content.replace(root, '[frozen-package]/')
                        changes.append({'from': root, 'to': '[frozen-package]/', 'count': count})
            for version in ('0.8.0', '0.9.0'):
                count = content.count(version)
                if count:
                    content = content.replace(version, '[version withheld]')
                    changes.append({'from': version, 'to': '[version withheld]', 'count': count})
            target = RESULTS / 'anonymous-input' / case['case'] / f'{label}.md'
            data = content.encode('utf-8')
            if target.exists() and target.read_bytes() != data:
                raise ValueError(f'Existing anonymous answer changed: {target}')
            target.parent.mkdir(parents=True, exist_ok=True)
            target.write_bytes(data)
            records.append({
                'case': case['case'], 'label': label,
                'source': source.relative_to(RESULTS).as_posix(),
                'source_sha256': digest(raw),
                'target': target.relative_to(RESULTS).as_posix(),
                'target_sha256': digest(data),
                'normalization': 'UTF-8 without BOM; LF newlines',
                'redactions': changes,
            })
    report = {
        'format': 'anonymous-library-inputs/1',
        'prepared_pairs': len(records) // 2,
        'records': records,
        'limits': 'Answers may reveal retrieval capabilities or wording. Labels conceal condition names, not every inferable implementation difference. No creative wording or error is repaired.',
    }
    (RESULTS / 'anonymous-preparation.json').write_text(json.dumps(report, ensure_ascii=False, indent=2) + '\n', encoding='utf-8')
    print(json.dumps({'prepared_pairs': report['prepared_pairs'], 'answers': len(records)}))


if __name__ == '__main__':
    main()
