"""Map archived anonymous judgments back to frozen conditions, without regrading."""
from collections import Counter
from pathlib import Path
import hashlib
import json

ROOT = Path(__file__).resolve().parents[2]
RESULTS = ROOT / 'evals/results/library-0.9.0'


def read(name):
    return json.loads((RESULTS / name).read_text(encoding='utf-8-sig'))


def main():
    mapping = {v['case']: v['answers'] for v in read('blind-mapping.json')['mapping']}
    audit = read('review-audit.json')
    assert audit['passed'] and len(audit['confirmed_terminal_batches']) == 3
    rows, sources = [], []
    for batch in audit['confirmed_terminal_batches']:
        path = Path('reviews') / batch / 'review.json'
        source = read(path)
        sources.append({'path': path.as_posix(), 'sha256': hashlib.sha256((RESULTS / path).read_bytes()).hexdigest()})
        for case in source.get('cases', source.get('questions', [])):
            case_id = case.get('case_id', case.get('question_id', case.get('id')))
            answers = case.get('answers', case.get('responses'))
            comparison = case['comparison']
            preferred = comparison.get('winner', comparison.get('preference'))
            grades = {mapping[case_id][label]['condition']: value['overall_status'] for label, value in answers.items()}
            rows.append({'id': case_id, 'grades': grades,
                         'preference': mapping[case_id][preferred]['condition'] if preferred in ('A', 'B') else preferred,
                         'reason': comparison['reason'], 'review': path.as_posix()})
    assert sorted(r['id'] for r in rows) == [f'L{i:02}' for i in range(1, 10)]
    record = {'format': 'combat-library-behavior-summary/1', 'aggregation_date': '2026-09-29',
              'method': 'Mechanical mapping of the three archived independent reviews; no parent regrading.',
              'cases': sorted(rows, key=lambda r: r['id']), 'sources': sources,
              'counts': {condition: dict(Counter(r['grades'][condition] for r in rows)) for condition in ('baseline', 'candidate')},
              'preferences': dict(Counter(r['preference'] for r in rows)),
              'limits': ['Nine paired single draws; no general success-rate or superiority estimate.',
                         'Anonymous presentation only partially blinds capability and wording.',
                         'Source-card metadata beyond reviewer inputs is covered separately by parent-source-supplement.json.',
                         'No media quality, engine behavior, exact token usage or latency measured.']}
    (RESULTS / 'summary.json').write_text(json.dumps(record, ensure_ascii=False, indent=2)+'\n', encoding='utf-8')
    print(json.dumps({'counts': record['counts'], 'preferences': record['preferences']}, ensure_ascii=False))


if __name__ == '__main__':
    main()
