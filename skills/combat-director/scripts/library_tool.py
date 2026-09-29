#!/usr/bin/env python3
"""Read-only, offline combat library lookup (Python 3.10+, stdlib)."""
from __future__ import annotations

import argparse
import importlib.util
import json
import re
import sys
import unicodedata
from pathlib import Path, PurePosixPath
from collections import Counter

CATALOG = Path(__file__).resolve().parents[1] / 'library/catalog.json'
KINDS = ('design', 'abilities', 'techniques', 'characters', 'choreography',
         'camera', 'effects', 'styles', 'scenes')
DETAILS = ('original', 'detailed', 'outline')
SCOPES = ('duel', 'group', 'escape', 'chase', 'ranged', 'sparring')
FIELDS = {'id', 'kind', 'title', 'scope', 'tags', 'summary', 'requires',
          'excludes', 'path', 'provenance', 'detail', 'schools', 'characters',
          'names', 'source'}
_spec = importlib.util.spec_from_file_location('combat_library_items', Path(__file__).with_name('library_items.py'))
items = importlib.util.module_from_spec(_spec)
_old_bytecode = sys.dont_write_bytecode
try:
    sys.dont_write_bytecode = True
    _spec.loader.exec_module(items)
finally:
    sys.dont_write_bytecode = _old_bytecode


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
    require(type(data['version']) is int and data['version'] == 2,
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
        require(entry['detail'] in DETAILS, f"{entry['id']}: unknown detail")
        for field in ('scope', 'tags', 'requires', 'excludes'):
            values = entry[field]
            require(isinstance(values, list) and values and all(text_value(v) for v in values),
                    f"{entry['id']}: {field} must be a nonempty string array")
            require(len(values) == len(set(values)), f"{entry['id']}: duplicate {field}")
        require(set(entry['scope']) <= set(SCOPES), f"{entry['id']}: unknown scope")
        for field in ('schools', 'characters', 'names'):
            values = entry[field]
            require(isinstance(values, list) and all(text_value(v) for v in values),
                    f"{entry['id']}: {field} must be a string array")
            require(len(values) == len(set(values)), f"{entry['id']}: duplicate {field}")
        source = entry['source']
        if entry['detail'] == 'original':
            require(source is None, f"{entry['id']}: original card must not claim imported source")
        else:
            require(isinstance(source, dict) and set(source) == {'repository', 'commit', 'path', 'ranges'},
                    f"{entry['id']}: missing source provenance")
            require(source['repository'] == 'https://github.com/wangarvin007-commits/-skills'
                    and source['path'] == 'seedance-combat-prompt/SKILL.md'
                    and isinstance(source['commit'], str)
                    and re.fullmatch(r'[0-9a-f]{40}', source['commit']),
                    f"{entry['id']}: invalid source identity")
            require(isinstance(source['ranges'], list) and source['ranges']
                    and all(isinstance(pair, list) and len(pair) == 2
                            and all(type(n) is int for n in pair)
                            and 1 <= pair[0] <= pair[1] for pair in source['ranges']),
                    f"{entry['id']}: invalid source ranges")
        resolved = card_path(path.parent, entry).resolve()
        require(resolved not in paths, f"{entry['id']}: duplicate card path")
        paths.add(resolved)
    return data


def normalize(text):
    return unicodedata.normalize('NFKC', text).casefold()


def search(catalog, kind, query='', scope=None, *, school=None, character=None,
           detail=None, limit=12, offset=0):
    require(kind in (*KINDS, 'all'), 'unknown kind')
    require(scope is None or scope in SCOPES, 'unknown scope')
    require(detail is None or detail in DETAILS, 'unknown detail')
    require(type(limit) is int and 1 <= limit <= 100, 'limit must be 1..100')
    require(type(offset) is int and offset >= 0, 'offset must be a nonnegative integer')
    require(isinstance(query, str), 'query must be a string')
    for value in (school, character):
        require(value is None or text_value(value), 'facet must be a nonempty string')
    terms = list(dict.fromkeys(t for t in re.split(r'[\s,，、;；]+', normalize(query)) if t))
    matches = []
    for entry in catalog['entries']:
        if kind != 'all' and entry['kind'] != kind or scope is not None and scope not in entry['scope']:
            continue
        if detail is not None and entry['detail'] != detail:
            continue
        if school is not None and normalize(school) not in map(normalize, entry['schools']):
            continue
        if character is not None and normalize(character) not in map(normalize, entry['characters']):
            continue
        # Exclusions and provenance are not positive evidence of suitability.
        haystack = normalize(' '.join([entry['id'], entry['title'], entry['summary'],
                                      *entry['tags'], *entry['requires'], *entry['names']]))
        matched = [term for term in terms if term in haystack]
        if terms and not matched:
            continue
        matched_names = [name for name in entry['names'] if any(t in normalize(name) for t in terms)]
        matches.append({**{k:v for k,v in entry.items() if k != 'names'},
                        'status': 'candidate', 'matched_terms': matched,
                        'matched_names': matched_names[:10], 'matched_names_total':len(matched_names)})
    matches.sort(key=lambda item: (-len(item['matched_terms']), item['id']))
    total = len(matches)
    return {'status': 'candidates' if total else 'no_match',
            'filters': {'kind': kind, 'query': query, 'scope': scope,
                        'school':school, 'character':character, 'detail':detail},
            'total':total, 'limit':limit, 'offset':offset,
            'next_offset':offset+limit if offset+limit < total else None,
            'notice': '仅为关键词候选；detailed表示卡内含动作说明，不保证每个列名都有细节。核对前提、版本和用户设定；零命中可原创。',
            'matches': matches[offset:offset+limit]}


def stats(catalog):
    entries = catalog['entries']
    return {'cards':len(entries),
            'by_kind':dict(sorted(Counter(e['kind'] for e in entries).items())),
            'by_detail':dict(sorted(Counter(e['detail'] for e in entries).items())),
            'schools':sorted({s for e in entries for s in e['schools']}),
            'characters':sorted({c for e in entries for c in e['characters']}),
            'facets_by_kind':{
                kind:{field:sorted({value for e in entries if e['kind']==kind for value in e[field]})
                      for field in ('schools','characters','scope')}
                for kind in KINDS},
            'facet_notice':'筛选值表示已记录的关联；空数组表示未记录该类关联，不证明语义不适用。场面标签是改编候选，不是视频验证。'}


def load_items(catalog, path=CATALOG.with_name('items.json')):
    return items.load_items(catalog, path)


def compact_search(result):
    """Display projection only; ranking, filters and paging remain unchanged."""
    fields = ('id', 'kind', 'title', 'summary', 'detail', 'matched_names', 'matched_names_total')
    return {**result, 'matches': [{k: entry[k] for k in fields} for entry in result['matches']]}


def read_card(catalog, card_id, path=CATALOG, *, source=True):
    entry = next((item for item in catalog['entries'] if item['id'] == card_id), None)
    require(entry is not None, f'unknown card ID: {card_id}')
    body = card_path(Path(path).parent, entry).read_text(encoding='utf-8')
    if source or not entry['source']:
        return body
    return re.split(r'^### 原文 ', body, maxsplit=1, flags=re.MULTILINE)[0].rstrip() + \
        f'\n\n逐招查询：`items --card {card_id}`；原文展开：`show {card_id} --source`。\n'


def main(argv=None):
    parser = argparse.ArgumentParser(description=__doc__)
    sub = parser.add_subparsers(dest='command', required=True)
    sub.add_parser('validate', help='check index types, IDs and local references')
    sub.add_parser('stats', help='list categories, schools and character variants')
    lookup = sub.add_parser('search', help='search metadata only; results are candidates')
    lookup.add_argument('kind', choices=(*KINDS, 'all'))
    lookup.add_argument('--query', default='')
    lookup.add_argument('--scope', choices=SCOPES)
    lookup.add_argument('--school', help='exact school facet; use stats for values')
    lookup.add_argument('--character', help='exact character variant; use stats for values')
    lookup.add_argument('--detail', choices=DETAILS)
    lookup.add_argument('--limit', type=int, default=12)
    lookup.add_argument('--offset', type=int, default=0)
    lookup.add_argument('--full', action='store_true', help='include all card metadata and provenance')
    show = sub.add_parser('show', help='read one selected card')
    show.add_argument('id')
    show.add_argument('--source', action='store_true', help='include complete attributed source excerpts')
    item_search = sub.add_parser('items', help='search named source items, without reading whole cards')
    item_search.add_argument('--query', default='')
    item_search.add_argument('--kind', choices=(*items.KINDS, 'all'), default='all')
    item_search.add_argument('--card', dest='card_id')
    item_search.add_argument('--school')
    item_search.add_argument('--character')
    level = item_search.add_mutually_exclusive_group()
    level.add_argument('--detail', choices=items.DETAILS, help='exact source detail level')
    level.add_argument('--min-detail', choices=items.DETAILS, help='minimum source detail level')
    item_search.add_argument('--limit', type=int, default=12)
    item_search.add_argument('--offset', type=int, default=0)
    item_show = sub.add_parser('item', help='read selected source rows plus separate project context')
    item_show.add_argument('id')
    item_show.add_argument('--source', action='store_true', help='include verbatim selected source rows')
    args = parser.parse_args(argv)
    try:
        catalog = load_catalog()
        if args.command == 'validate':
            data = load_items(catalog)
            print(f"PASS: {len(catalog['entries'])} combat cards; {len(data['entries'])} source items; indexes and references valid")
        elif args.command == 'stats':
            print(json.dumps(stats(catalog), ensure_ascii=False, indent=2))
        elif args.command == 'show':
            print(read_card(catalog, args.id, source=args.source), end='')
        elif args.command in ('items', 'item'):
            data = load_items(catalog)
            if args.command == 'item':
                result = items.read_item(data, catalog, args.id, source=args.source)
            else:
                result = items.search_items(data, catalog, args.query, kind=args.kind, card_id=args.card_id,
                    school=args.school, character=args.character, detail=args.detail, min_detail=args.min_detail,
                    limit=args.limit, offset=args.offset)
            print(json.dumps(result, ensure_ascii=False, indent=2))
        else:
            result = search(catalog, args.kind, args.query, args.scope,
                                    school=args.school, character=args.character,
                                    detail=args.detail, limit=args.limit, offset=args.offset)
            print(json.dumps(result if args.full else compact_search(result), ensure_ascii=False, indent=2))
    except (ValueError, OSError) as error:
        print(f'FAIL: {error}', file=sys.stderr)
        return 1
    return 0


if __name__ == '__main__':
    # Keep JSON and Chinese card text usable in Windows pipes regardless of locale.
    sys.stdout.reconfigure(encoding='utf-8')
    sys.stderr.reconfigure(encoding='utf-8')
    raise SystemExit(main())
