"""Audited JSON Schema subset; unsupported assertions fail closed."""
from __future__ import annotations

import math
import re

ANNOTATIONS = {'$schema', '$id', 'title', 'description', 'default', 'examples', '$comment'}
SUPPORTED = ANNOTATIONS | {'$defs', '$ref', 'type', 'const', 'enum', 'properties', 'required',
    'additionalProperties', 'items', 'minItems', 'maxItems', 'uniqueItems', 'minLength',
    'maxLength', 'pattern', 'minimum', 'maximum', 'exclusiveMinimum', 'exclusiveMaximum'}
KINDS = {'object', 'array', 'string', 'boolean', 'number', 'integer', 'null'}


def require(condition, message):
    if not condition:
        raise ValueError(message)


def resolve(schema, ref):
    require(isinstance(ref, str) and ref.startswith('#/'), f'unsupported $ref: {ref}')
    value = schema
    try:
        for token in ref[2:].split('/'):
            value = value[token.replace('~1', '/').replace('~0', '~')]
    except (KeyError, TypeError):
        raise ValueError(f'unresolved $ref: {ref}') from None
    return value


def audit_schema(rule, root=None, path='$schema'):
    root = rule if root is None else root
    require(isinstance(rule, (dict, bool)), f'{path}: schema must be object or boolean')
    if isinstance(rule, bool):
        return
    require(not (set(rule) - SUPPORTED), f'{path}: unsupported schema keywords {sorted(set(rule) - SUPPORTED)}')
    if 'type' in rule:
        kinds = rule['type'] if isinstance(rule['type'], list) else [rule['type']]
        require(bool(kinds) and set(kinds) <= KINDS, f'{path}: unsupported type')
    if '$ref' in rule:
        resolve(root, rule['$ref'])
    for group in ('properties', '$defs'):
        for key, child in rule.get(group, {}).items():
            audit_schema(child, root, f'{path}.{group}.{key}')
    for key in ('items', 'additionalProperties'):
        if key in rule:
            audit_schema(rule[key], root, f'{path}.{key}')


def same_json(a, b):
    # JSON numbers compare by value; booleans must not equal 0/1.
    if isinstance(a, bool) or isinstance(b, bool):
        return type(a) is type(b) and a == b
    if isinstance(a, dict) and isinstance(b, dict):
        return a.keys() == b.keys() and all(same_json(a[k], b[k]) for k in a)
    if isinstance(a, list) and isinstance(b, list):
        return len(a) == len(b) and all(same_json(x, y) for x, y in zip(a, b))
    return a == b


def check_schema(value, rule, schema=None, location='$'):
    schema = rule if schema is None else schema
    audit_schema(schema)
    if rule is not schema:
        audit_schema(rule, schema)
    _check(value, rule, schema, location, 0)


def _check(value, rule, schema, location, depth):
    require(depth < 100, f'{location}: schema recursion limit')
    if isinstance(rule, bool):
        require(rule, f'{location}: forbidden by schema')
        return
    if '$ref' in rule:
        _check(value, resolve(schema, rule['$ref']), schema, location, depth + 1)
    number = type(value) in (int, float) and math.isfinite(value)
    valid = {'object': isinstance(value, dict), 'array': isinstance(value, list),
             'string': isinstance(value, str), 'boolean': isinstance(value, bool),
             'number': number, 'integer': number and int(value) == value, 'null': value is None}
    kinds = rule.get('type')
    if kinds is not None:
        kinds = kinds if isinstance(kinds, list) else [kinds]
        require(any(valid[k] for k in kinds), f'{location}: expected {kinds}')
    if 'const' in rule:
        require(same_json(value, rule['const']), f'{location}: incorrect constant')
    if 'enum' in rule:
        require(any(same_json(value, item) for item in rule['enum']), f'{location}: invalid choice')
    if isinstance(value, str):
        require(len(value) >= rule.get('minLength', 0), f'{location}: text too short')
        if rule.get('minLength', 0) > 0:
            require(bool(value.strip()), f'{location}: blank text')
        require(len(value) <= rule.get('maxLength', math.inf), f'{location}: text too long')
        if 'pattern' in rule:
            require(re.search(rule['pattern'], value) is not None, f'{location}: pattern mismatch')
    if number:
        require(value >= rule.get('minimum', -math.inf), f'{location}: below minimum')
        require(value <= rule.get('maximum', math.inf), f'{location}: above maximum')
        require(value > rule.get('exclusiveMinimum', -math.inf), f'{location}: below exclusive minimum')
        require(value < rule.get('exclusiveMaximum', math.inf), f'{location}: above exclusive maximum')
    if isinstance(value, list):
        require(len(value) >= rule.get('minItems', 0), f'{location}: too few items')
        require(len(value) <= rule.get('maxItems', math.inf), f'{location}: too many items')
        if rule.get('uniqueItems'):
            require(not any(same_json(v, other) for i, v in enumerate(value) for other in value[:i]),
                    f'{location}: duplicate items')
        for i, item in enumerate(value):
            _check(item, rule.get('items', True), schema, f'{location}[{i}]', depth + 1)
    if isinstance(value, dict):
        missing = set(rule.get('required', [])) - value.keys()
        require(not missing, f'{location}: missing required fields {sorted(missing)}')
        props = rule.get('properties', {})
        for key, item in value.items():
            _check(item, props.get(key, rule.get('additionalProperties', True)), schema,
                   f'{location}.{key}', depth + 1)
