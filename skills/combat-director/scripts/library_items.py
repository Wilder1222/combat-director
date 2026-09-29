"""Versioned source-item lookup. Reads indexes only; never executes source text."""
from __future__ import annotations

import hashlib
import json
import re
import unicodedata
from pathlib import Path

DETAILS = ('name_only', 'description', 'motion_path')
KINDS = ('techniques', 'characters', 'choreography')
FIELDS = {'id', 'card_id', 'name', 'aliases', 'schools', 'characters', 'detail', 'evidence'}
EVIDENCE_FIELDS = {'line', 'header_line', 'section', 'origin', 'name_column', 'shared_row',
                   'detail', 'detail_columns', 'fields', 'source_text', 'assessment_note'}


def require(condition, message):
    if not condition:
        raise ValueError(message)


def normalize(value):
    return unicodedata.normalize('NFKC', value).casefold()


def strings(value):
    return (isinstance(value, list) and all(isinstance(v, str) and v.strip() for v in value)
            and len(value) == len(set(value)))


def identity(card_id, name, schools):
    key = json.dumps([card_id, normalize(name), sorted(map(normalize, schools))],
                     ensure_ascii=False, separators=(',', ':'))
    return card_id + '-item-' + hashlib.sha256(key.encode('utf-8')).hexdigest()[:12]


def load_items(catalog, path):
    """Validate packaged provenance and references, not martial semantics."""
    path = Path(path)
    require(not path.is_symlink(), 'item index must not be a symlink')
    data = json.loads(path.read_text(encoding='utf-8'))
    require(isinstance(data, dict) and set(data) == {'version', 'source', 'entries'}, 'invalid item index')
    require(type(data['version']) is int and data['version'] == 1, 'unsupported item index version')
    source = data['source']
    require(isinstance(source, dict) and set(source) == {'repository', 'commit', 'path', 'sha256'},
            'invalid item source')
    require(all(isinstance(value, str) for value in source.values())
            and source['repository'] == 'https://github.com/wangarvin007-commits/-skills'
            and source['path'] == 'seedance-combat-prompt/SKILL.md'
            and re.fullmatch(r'[a-f0-9]{40}', source['commit'])
            and re.fullmatch(r'[a-f0-9]{64}', source['sha256']), 'invalid item source identity')
    require(isinstance(data['entries'], list), 'items must be an array')
    cards = {card['id']: card for card in catalog['entries']}
    ids = set()
    for item in data['entries']:
        require(isinstance(item, dict) and set(item) == FIELDS, 'invalid item fields')
        require(all(isinstance(item[k], str) and item[k].strip() for k in ('id', 'card_id', 'name', 'detail')),
                'item identity and detail must be strings')
        require(item['id'] not in ids, 'duplicate item ID')
        ids.add(item['id'])
        require(item['card_id'] in cards, 'item references unknown card')
        card = cards[item['card_id']]
        require(card['kind'] in KINDS and card['source']
                and all(card['source'][k] == source[k] for k in ('repository', 'commit', 'path')),
                'item and card source mismatch')
        for field in ('aliases', 'schools', 'characters'):
            require(strings(item[field]), 'invalid item ' + field)
        require(set(item['characters']) <= set(card['characters']), 'item character outside card context')
        require(item['id'] == identity(item['card_id'], item['name'], item['schools']), 'unstable item ID')
        require(item['detail'] in DETAILS, 'unknown item detail')
        evidence = item['evidence']
        require(isinstance(evidence, list) and evidence, 'item needs source evidence')
        locations, aliases = set(), set()
        for ev in evidence:
            require(isinstance(ev, dict) and set(ev) == EVIDENCE_FIELDS, 'invalid item evidence fields')
            require(type(ev['line']) is int and type(ev['header_line']) is int
                    and 1 <= ev['header_line'] < ev['line']
                    and any(a <= ev['line'] <= b for a, b in card['source']['ranges']),
                    'item source row outside card ranges')
            require(all(isinstance(ev[k], str) for k in
                        ('section', 'origin', 'name_column', 'detail', 'source_text', 'assessment_note')),
                    'invalid evidence text')
            require(ev['origin'] in ('overview', 'named', 'reference', 'combination')
                    and type(ev['shared_row']) is bool and ev['detail'] in DETAILS, 'invalid evidence type')
            require((ev['line'], ev['name_column']) not in locations, 'duplicate item evidence')
            locations.add((ev['line'], ev['name_column']))
            require(strings(ev['detail_columns']), 'invalid evidence detail columns')
            cells = ev['fields']
            require(isinstance(cells, list) and cells and all(isinstance(f, dict)
                    and set(f) == {'column', 'value'} and isinstance(f['column'], str) and f['column']
                    and isinstance(f['value'], str) for f in cells), 'invalid evidence cells')
            columns = [f['column'] for f in cells]
            require(len(set(columns)) == len(columns) and ev['name_column'] in columns
                    and set(ev['detail_columns']) <= set(columns), 'invalid evidence column references')
            raw = ev['source_text']
            require(raw.startswith('|') and raw.endswith('|') and '\n' not in raw and '\r' not in raw,
                    'invalid literal source row')
            cleaned = [re.sub(r'[*`★]', '', value).strip() for value in raw.strip('|').split('|')]
            require(cleaned == [f['value'] for f in cells], 'evidence cells differ from literal source row')
            name_cell = next(f['value'] for f in cells if f['column'] == ev['name_column'])
            require(normalize(item['name']) in normalize(name_cell), 'item name absent from source cell')
            aliases.update(f['value'] for f in cells if f['column'] in ('罗马音', '传统口诀名'))
            require((ev['detail'] == 'name_only') == (not ev['detail_columns']), 'detail needs matching evidence basis')
            if ev['origin'] in ('overview', 'reference'):
                require(ev['detail'] == 'name_only', 'reference list must not imply individual action detail')
            if ev['shared_row']:
                require(ev['detail'] != 'motion_path', 'shared alternatives must not imply individual movement detail')
        require(set(item['aliases']) <= aliases, 'alias absent from source columns')
        require(item['detail'] == max((e['detail'] for e in evidence), key=DETAILS.index),
                'item detail differs from its evidence')
    return data


def search_items(data, catalog, query='', *, kind='all', card_id=None, school=None,
                 character=None, detail=None, min_detail=None, limit=12, offset=0):
    require(kind in (*KINDS, 'all'), 'unknown item kind')
    require(isinstance(query, str), 'query must be a string')
    require(type(limit) is int and 1 <= limit <= 100, 'limit must be 1..100')
    require(type(offset) is int and offset >= 0, 'offset must be a nonnegative integer')
    require(detail is None or detail in DETAILS, 'unknown item detail')
    require(min_detail is None or min_detail in DETAILS, 'unknown minimum detail')
    require(detail is None or min_detail is None, 'choose detail or min_detail, not both')
    for value in (school, character, card_id):
        require(value is None or isinstance(value, str) and value.strip(), 'facet must be nonempty text')
    cards = {c['id']: c for c in catalog['entries']}
    require(card_id is None or card_id in cards, 'unknown card ID')
    terms = list(dict.fromkeys(t for t in re.split(r'[\s,，、;；]+', normalize(query)) if t))
    matches = []
    for item in data['entries']:
        card = cards[item['card_id']]
        if kind != 'all' and card['kind'] != kind or card_id is not None and item['card_id'] != card_id:
            continue
        if detail is not None and detail != item['detail']:
            continue
        if min_detail is not None and DETAILS.index(item['detail']) < DETAILS.index(min_detail):
            continue
        if any(value is not None and normalize(value) not in map(normalize, item[field])
               for value, field in ((school, 'schools'), (character, 'characters'))):
            continue
        names = [item['name'], *item['aliases']]
        matched = [t for t in terms if any(t in normalize(n) for n in names)]
        if terms and not matched:
            continue
        exact = any(normalize(query) == normalize(n) for n in names) if query else False
        compact = {k: item[k] for k in ('id', 'card_id', 'name', 'detail', 'schools', 'characters')}
        compact.update(kind=card['kind'], matched_names=[n for n in names if any(t in normalize(n) for t in terms)],
                       source_lines=sorted({e['line'] for e in item['evidence']}))
        matches.append(((-int(exact), -len(matched), -DETAILS.index(item['detail']), item['id']), compact))
    matches.sort(key=lambda row: row[0])
    total = len(matches)
    return {'status': 'candidates' if total else 'no_match',
            'filters': {'kind': kind, 'query': query, 'card_id': card_id, 'school': school,
                        'character': character, 'detail': detail, 'min_detail': min_detail},
            'total': total, 'limit': limit, 'offset': offset,
            'next_offset': offset + limit if offset + limit < total else None,
            'notice': '详情等级只描述源文供给，不证明动作完整、事实正确或能力获准；同名与别名歧义分别保留。',
            'matches': [row[1] for row in matches[offset:offset + limit]]}


def read_item(data, catalog, item_id, *, source=False):
    item = next((i for i in data['entries'] if i['id'] == item_id), None)
    require(item is not None, 'unknown item ID: ' + item_id)
    card = next(c for c in catalog['entries'] if c['id'] == item['card_id'])
    evidence = []
    origin = data['source']
    for ev in item['evidence']:
        detail = {k: ev[k] for k in ('line', 'header_line', 'section', 'origin', 'shared_row',
                                    'detail', 'detail_columns', 'assessment_note')}
        if ev['origin'] in ('overview', 'reference'):
            # Do not dump a whole list of other moves as this move's description.
            detail['fields'] = []
            detail['scope_note'] = '此行仅证明名称出现；整行上下文请用 --source 展开。'
        else:
            detail['fields'] = ev['fields']
            if ev['shared_row']:
                detail['scope_note'] = '同一行含多个名称，描述属于共享行，不能保证逐个动作都已展开。'
        detail['url'] = f"{origin['repository']}/blob/{origin['commit']}/{origin['path']}#L{ev['line']}"
        if source:
            detail['source_text'] = ev['source_text']
        evidence.append(detail)
    return {'item': {k: item[k] for k in ('id', 'card_id', 'name', 'aliases', 'schools', 'characters', 'detail')},
            'source': {**origin, 'credit': 'Arvin', 'license': 'MIT',
                       'license_notice': 'references/third-party-notices.md', 'evidence': evidence},
            'card_context': {k: card[k] for k in ('id', 'title', 'kind', 'schools', 'characters')},
            'project_adaptation': {'scope': '整卡改编建议，不是该招原文，也不抬高来源详情等级。',
                                   'summary': card['summary'], 'requires': card['requires'], 'excludes': card['excludes']},
            'notice': '原文称谓、效果与固定数值未经独立核验；补写动作须标为本项目原创。按用户能力边界改编。'}
