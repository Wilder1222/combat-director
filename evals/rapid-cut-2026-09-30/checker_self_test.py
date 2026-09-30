"""Small adversarial fixtures for the evaluation table reader, not scene semantics."""
from decimal import Decimal
import json
from pathlib import Path
import tempfile

from check_timing import inspect


valid = '| S01 | 0.0—0.3 | action |\n| S02 | 0.3—0.6 | action |'
cases = [
    ('split_columns', valid, True),
    ('inline', '| S01 0.0—0.3 / 0.3 | action |\n| S02 0.3—0.6 / 0.3 | action |', True),
    ('numeric_ids', '| 1 | 0.0—0.3 | 0.3 | action |\n| 2 | 0.3—0.6 | 0.3 | action |', True),
    ('chinese_comma', '|S01 0.0—0.3，0.3秒|action|\n|S02 0.3—0.6，0.3秒|action|', True),
    ('slash_id', '| S01 / 0.0—0.3 / 0.3 | action |\n| S02 / 0.3—0.6 / 0.3 | action |', True),
    ('exclude_summary_range', valid + '\n|10.6—16.0|six-track summary|', True),
    ('gap', valid.replace('0.3—0.6', '0.4—0.6'), False),
    ('duplicate', valid.replace('S02', 'S01'), False),
    ('bad_duration', '|S01|0.0—0.5|action|\n|S02|0.5—0.6|action|', False),
    ('wrong_declared_duration', '|S01|0.0—0.3|0.4|action|\n|S02|0.3—0.6|0.3|action|', False),
    ('unparsed', 'No shot table.', False),
]
results = []
with tempfile.TemporaryDirectory(prefix='combat-checker-') as folder:
    fixture = Path(folder) / 'case.md'
    for name, text, expected in cases:
        fixture.write_text(text, encoding='utf-8')
        result = inspect(fixture, Decimal('0.6'), 2)
        results.append({'case': name, 'expected_pass': expected,
                        'observed_pass': result['passed'], 'errors': result['errors']})
        assert result['passed'] == expected, (name, result)
Path(__file__).with_name('checker-self-check.json').write_text(
    json.dumps(results, ensure_ascii=False, indent=2) + '\n', encoding='utf-8')
print(f'PASS: {len(results)} checker fixtures')
