"""Cross-check bundled schemas with Draft 2020-12 (development dependency)."""
import json
import sys
from pathlib import Path
from jsonschema import Draft202012Validator

ROOT = Path(__file__).resolve().parents[1]
SKILL = ROOT / 'skills/combat-director'
sys.path.insert(0, str(SKILL / 'scripts'))
from combat_schema import audit_schema


def main():
    schemas = {}
    for path in sorted((SKILL / 'assets').glob('*.schema.json')):
        schema = json.loads(path.read_text(encoding='utf-8'))
        Draft202012Validator.check_schema(schema)
        audit_schema(schema)
        schemas[path.name] = schema
    count = 0
    for path in sorted((ROOT / 'tests/fixtures').glob('*.plan.json')):
        plan = json.loads(path.read_text(encoding='utf-8'))
        schema_name = 'combat-plan-v1.schema.json' if plan['schema_version'] == '1.0' else 'combat-plan.schema.json'
        Draft202012Validator(schemas[schema_name]).validate(plan)
        count += 1
    print(f'PASS: {len(schemas)} schemas; {count} engineering fixtures; Draft 2020-12 + subset audit')


if __name__ == '__main__':
    main()
