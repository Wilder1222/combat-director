#!/usr/bin/env python3
"""Read-only, offline mechanism catalog lookup (Python 3.10+, stdlib)."""
from __future__ import annotations

import argparse
import json
import re
import sys
import unicodedata
from pathlib import Path, PurePosixPath

CATALOG = Path(__file__).resolve().parents[1] / 'library/catalog.json'
KINDS = ('design', 'abilities')
SCOPES = ('duel', 'group', 'escape', 'chase', 'ranged', 'sparring')
FIELDS = {'id', 'kind', 'title', 'scope', 'tags', 'summary', 'requires',
          'excludes', 'path', 'provenance'}


def require(condition, message):
    if not condition:
        raise ValueError(message)


def text_value(value):
    return isinstance(value, str) and bool(value.strip())


def card_path(root, entry):
    relative = PurePosixPath(entry['path'])
    require(not relative.is_absolute() and '\\' not in entry['path']
            and ':' not in entry['path'] and '..' not in relative.parts,
            f"{entry['id']}: invalid relative path")
    require(len(relative.parts) == 2 and relative.parts[0] == entry['kind']
            and relative.suffix == '.md', f"{entry['id']}: invalid card location")
    candidate = root.joinpath(*relative.parts)
    require(not candidate.is_symlink() and not candidate.parent.is_symlink()
            and candidate.resolve().is_relative_to(root.resolve()),
            f"{entry['id']}: card path escapes library or is a link")
    require(candidate.is_file() and candidate.stat().st_size > 0,
            f"{entry['id']}: missing or empty card")
    return candidate


def load_catalog(path=CATALOG):
    """Validate index and file references without loading every card's body."""
    path = Path(path)
    data = json.loads(path.read_text(encoding='utf-8'))
    require(isinstance(data, dict) and set(data) == {'version', 'entries'},
            'catalog must contain version and entries')
    require(type(data['version']) is int and data['version'] == 1,
            'unsupported catalog version')
    require(isinstance(data['entries'], list), 'entries must be an array')
    ids, paths = set(), set()
    for entry in data['entries']:
        require(isinstance(entry, dict) and set(entry) == FIELDS, 'invalid entry fields')
        for field in ('id', 'kind', 'title', 'summary', 'path', 'provenance'):
            require(text_value(entry[field]), f'entry needs nonempty {field}')
        require(re.fullmatch(r'[a-z0-9]+(?:-[a-z0-9]+)*', entry['id']), 'invalid card ID')
        require(entry['id'] not in ids, f"duplicate ID: {entry['id']}")
        ids.add(entry['id'])
        require(entry['kind'] in KINDS, f"{entry['id']}: unknown kind")
        for field in ('scope', 'tags', 'requires', 'excludes'):
            values = entry[field]
            require(isinstance(values, list) and values and all(text_value(v) for v in values),
                    f"{entry['id']}: {field} must be a nonempty string array")
            require(len(values) == len(set(values)), f"{entry['id']}: duplicate {field}")
        require(set(entry['scope']) <= set(SCOPES), f"{entry['id']}: unknown scope")
        resolved = card_path(path.parent, entry).resolve()
        require(resolved not in paths, f"{entry['id']}: duplicate card path")
        paths.add(resolved)
    return data


def normalize(text):
    return unicodedata.normalize('NFKC', text).casefold()


def search(catalog, kind, query='', scope=None):
    require(kind in KINDS, 'unknown kind')
    require(scope is None or scope in SCOPES, 'unknown scope')
    terms = list(dict.fromkeys(t for t in re.split(r'[\s,，、;；]+', normalize(query)) if t))
    matches = []
    for entry in catalog['entries']:
        if entry['kind'] != kind or scope is not None and scope not in entry['scope']:
            continue
        # Exclusions and provenance are not positive evidence of suitability.
        haystack = normalize(' '.join([entry['id'], entry['title'], entry['summary'],
                                      *entry['tags'], *entry['requires']]))
        matched = [term for term in terms if term in haystack]
        if terms and not matched:
            continue
        matches.append({**entry, 'status': 'candidate', 'matched_terms': matched})
    matches.sort(key=lambda item: (-len(item['matched_terms']), item['id']))
    return {'status': 'candidates' if matches else 'no_match',
            'filters': {'kind': kind, 'query': query, 'scope': scope},
            'notice': '仅为关键词候选；使用前核对前提、排除条件和用户设定。零命中可原创。',
            'matches': matches}


def read_card(catalog, card_id, path=CATALOG):
    entry = next((item for item in catalog['entries'] if item['id'] == card_id), None)
    require(entry is not None, f'unknown card ID: {card_id}')
    return card_path(Path(path).parent, entry).read_text(encoding='utf-8')


def main(argv=None):
    parser = argparse.ArgumentParser(description=__doc__)
    sub = parser.add_subparsers(dest='command', required=True)
    sub.add_parser('validate', help='check index types, IDs and local references')
    lookup = sub.add_parser('search', help='search metadata only; results are candidates')
    lookup.add_argument('kind', choices=KINDS)
    lookup.add_argument('--query', default='')
    lookup.add_argument('--scope', choices=SCOPES)
    show = sub.add_parser('show', help='read one selected card')
    show.add_argument('id')
    args = parser.parse_args(argv)
    try:
        catalog = load_catalog()
        if args.command == 'validate':
            print(f"PASS: {len(catalog['entries'])} mechanism cards; index and references valid")
        elif args.command == 'show':
            print(read_card(catalog, args.id), end='')
        else:
            print(json.dumps(search(catalog, args.kind, args.query, args.scope),
                             ensure_ascii=False, indent=2))
    except (ValueError, OSError) as error:
        print(f'FAIL: {error}', file=sys.stderr)
        return 1
    return 0


if __name__ == '__main__':
    # Keep JSON and Chinese card text usable in Windows pipes regardless of locale.
    sys.stdout.reconfigure(encoding='utf-8')
    sys.stderr.reconfigure(encoding='utf-8')
    raise SystemExit(main())
