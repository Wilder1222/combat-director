"""Source-item extraction policy for the pinned Arvin text, not martial advice.

Named rows and reference lists are distinct. An action-column label is only a
candidate for movement detail; reviewed exceptions below keep vague rows from
being promoted. Project adaptation text is never used to grade source detail.
"""
from __future__ import annotations

import hashlib
import json
import re
import unicodedata
from collections import Counter

KINDS = {'techniques', 'characters', 'choreography'}
LEVELS = ('name_only', 'description', 'motion_path')
NAME_COLUMNS = {
    '招式', '核心招式', '突进招式', '中文名', '招名', '腿法名', '身法名称',
    '投技', '关节技', '降服技', '截法', '招牌踢法', '技法', '六大开',
    '化劲技法', '破局技法', '绽放技法', '拐点技法', '擒拿动作', '摔技动作',
    '零碎动作', '反制方式', '配合类型', '化劲类型', '手法',
}
REFERENCE_COLUMNS = {'可选招式（按武学分）', '典型招式', '专属招式', '核心技法'}
ALIAS_COLUMNS = {'罗马音', '传统口诀名'}
MOTION_COLUMNS = {
    '动作描述', '动作描述（执行级）', '核心动作（执行级）', '执行级描述',
    '攻击轨迹', '攻击/防御轨迹', '动作细节', '具体动作', '发力方式',
}
SCHOOL_COLUMNS = {'武学', '武学来源'}
SCHOOL_ALIASES = {'太极': '太极拳', '咏春': '咏春拳', '八极': '八极拳', '擒拿手': '擒拿'}
# Reviewed column roles in this immutable source, not keyword-based inference.
TABLE_MOTION_COLUMNS = {1363: {'描述'}, 1384: {'描述'}, 2867: {'描述'}}
ROW_MOTION_COLUMNS = {
    **{n: {'描述'} for n in (1314, 1315, 1317, 1318, 1319, 1320, 1321)},
    **{n: {'打戏价值'} for n in (1800, 1824, 1829, 1831, 1832, 1853, 1871)},
    2212: {'打戏视觉签名'},
}
DETAIL_OVERRIDES = {
    **{n: ('description', '只有命名组合或节奏/劲力概括，没有展开肢体路径。')
       for n in (818, 859, 868, 873, 893, 977, 985, 1081, 1424, 2574)},
    **{n: ('description', '只给策略、风格或效果，未说明具体的动作/接触路径。')
       for n in (987, 988, 1126, 1207, 1366, 1473, 1991)},
    **{n: ('description', '只描述控制位置，未展开进入该位置的动作。')
       for n in (956, 1039, 1877, 1878)},
    1881: ('description', '动作描述仅写“袈裟固变体”，没有动作路径。'),
}


def clean(value):
    return re.sub(r'[*`★]', '', value).strip()


def normalized(value):
    return unicodedata.normalize('NFKC', value).casefold()


def split_names(value, separators='/、'):
    """Split listed alternatives, keeping parenthetical qualifiers intact."""
    names, buffer, depth = [], [], 0
    for char in clean(value):
        if char in '(（[':
            depth += 1
        elif char in ')）]':
            depth = max(0, depth - 1)
        if char in separators and not depth:
            if ''.join(buffer).strip():
                names.append(''.join(buffer).strip())
            buffer = []
        else:
            buffer.append(char)
    if ''.join(buffer).strip():
        names.append(''.join(buffer).strip())
    return list(dict.fromkeys(names))


def table_rows(lines):
    sections, section = {}, ''
    for line, value in enumerate(lines, 1):
        if re.match(r'^#{1,6}\s', value):
            section = re.sub(r'^#+\s*', '', value)
        sections[line] = section
    tables = []
    for i, value in enumerate(lines[:-1]):
        if not value.startswith('|') or not re.fullmatch(r'\|[\s:|-]+\|', lines[i + 1]):
            continue
        headers = [clean(cell) for cell in value.strip('|').split('|')]
        rows = []
        for j in range(i + 2, len(lines)):
            if not lines[j].startswith('|'):
                break
            rows.append((j + 1, [clean(cell) for cell in lines[j].strip('|').split('|')]))
        tables.append({'line': i + 1, 'headers': headers, 'rows': rows,
                       'section': sections[i + 1]})
    return tables


def meaningful(value):
    return value.strip() not in ('', '-', '—', '/', '无', '待补', '待补充')


def source_level(fields, name_column, shared, origin, line, header):
    if origin in ('overview', 'reference'):
        return 'name_only', []
    descriptions = [field['column'] for field in fields
                    if field['column'] not in {name_column, '#', '路数', '编号', *ALIAS_COLUMNS,
                                                *SCHOOL_COLUMNS}
                    and meaningful(field['value'])]
    roles = MOTION_COLUMNS | TABLE_MOTION_COLUMNS.get(header, set()) | ROW_MOTION_COLUMNS.get(line, set())
    motion = [name for name in descriptions if name in roles]
    level = 'motion_path' if motion and not shared else 'description' if descriptions else 'name_only'
    if line in DETAIL_OVERRIDES:
        level = DETAIL_OVERRIDES[line][0]
    return level, motion if level == 'motion_path' else descriptions if level == 'description' else []


def build_items(lines, cards, source):
    """Emit literal items, aliases, context and exact row evidence."""
    tables = table_rows(lines)
    records, table_coverage = {}, []
    used_overrides, used_promotions = set(), set()

    def add(card, name, aliases, fields, line, header, section, column, origin, shared=False):
        explicit = [field['value'] for field in fields if field['column'] in SCHOOL_COLUMNS]
        schools = sorted({SCHOOL_ALIASES.get(s, s) for value in explicit for s in split_names(value)})
        if not explicit and len(card['schools']) == 1:
            schools = card['schools'][:]
        # A shared card's facets do not establish the school of every row.
        characters = card['characters'][:] if len(card['characters']) == 1 else []
        identity = json.dumps([card['id'], normalized(name), sorted(map(normalized, schools))],
                              ensure_ascii=False, separators=(',', ':'))
        item_id = card['id'] + '-item-' + hashlib.sha256(identity.encode('utf-8')).hexdigest()[:12]
        level, basis_columns = source_level(fields, column, shared, origin, line, header)
        evidence = {'line': line, 'header_line': header, 'section': section, 'origin': origin,
                    'name_column': column, 'shared_row': shared, 'detail': level,
                    'detail_columns': basis_columns, 'fields': fields,
                    'source_text': lines[line - 1],
                    'assessment_note': DETAIL_OVERRIDES[line][1] if line in DETAIL_OVERRIDES else
                    '逐行复核：指定描述列包含具体移动或接触路径；不表示完整可执行动作。' if line in ROW_MOTION_COLUMNS else ''}
        if line in DETAIL_OVERRIDES:
            used_overrides.add(line)
        if line in ROW_MOTION_COLUMNS:
            used_promotions.add(line)
        if item_id not in records:
            records[item_id] = {'id': item_id, 'card_id': card['id'], 'name': name,
                                'aliases': [], 'schools': schools, 'characters': characters,
                                'detail': level, 'evidence': []}
        record = records[item_id]
        if record['name'] != name and normalized(record['name']) != normalized(name):
            raise ValueError('Source item ID collision: ' + item_id)
        record['aliases'] = list(dict.fromkeys([*record['aliases'], *[a for a in aliases if a != name]]))
        if evidence not in record['evidence']:
            record['evidence'].append(evidence)
        record['detail'] = max((record['detail'], level), key=LEVELS.index)

    for card in cards:
        if not card['source'] or card['kind'] not in KINDS:
            continue
        allowed = {n for start, end in card['source']['ranges'] for n in range(start, end + 1)}
        for table in tables:
            selected = [(line, cells) for line, cells in table['rows'] if line in allowed]
            if not selected:
                continue
            headers = table['headers']
            overview = table['line'] == 566
            primary = [i for i, name in enumerate(headers) if name in NAME_COLUMNS]
            references = [i for i, name in enumerate(headers) if name in REFERENCE_COLUMNS]
            combinations = [i for i, name in enumerate(headers) if name == '典型连招组合']
            if overview:
                primary, references, combinations = [1], [], []
            columns = [(i, 'overview' if overview else 'named') for i in primary]
            columns += [(i, 'reference') for i in references]
            columns += [(i, 'combination') for i in combinations]
            table_coverage.append({'card_id': card['id'], 'header_line': table['line'],
                                   'rows': [n for n, _ in selected],
                                   'indexed_columns': [headers[i] for i, _ in columns],
                                   'reason': 'explicit named rows, move references or combinations' if columns
                                   else 'context, camera, effects or other non-item table; retained in card'})
            for line, cells in selected if columns else []:
                if len(cells) != len(headers):
                    raise ValueError(f'Item table row {line} has {len(cells)} cells; expected {len(headers)}')
                fields = [{'column': key, 'value': value} for key, value in zip(headers, cells)]
                for index, origin in columns:
                    names = split_names(cells[index], '、' if overview else '/')
                    aliases = [cells[i] for i, key in enumerate(headers) if key in ALIAS_COLUMNS and meaningful(cells[i])]
                    for name in names:
                        add(card, name, aliases if len(names) == 1 else [], fields, line,
                            table['line'], table['section'], headers[index], origin, len(names) > 1)
    if used_overrides != set(DETAIL_OVERRIDES):
        raise ValueError('Stale source-detail overrides: ' + str(set(DETAIL_OVERRIDES) - used_overrides))
    if used_promotions != set(ROW_MOTION_COLUMNS):
        raise ValueError('Stale source-detail promotions: ' + str(set(ROW_MOTION_COLUMNS) - used_promotions))
    items = sorted(records.values(), key=lambda item: item['id'])
    for item in items:
        item['evidence'].sort(key=lambda ev: (ev['line'], ev['name_column']))
    data = {'version': 1, 'source': source, 'entries': items}
    coverage = {'items': len(items), 'by_detail': dict(sorted(Counter(i['detail'] for i in items).items())),
                'cards_with_items': len({i['card_id'] for i in items}),
                'scope': 'Explicit named rows, move-reference columns and combinations in techniques, characters and choreography. Incidental names in prose are not inferred.',
                'detail_policy': {'levels': list(LEVELS), 'motion_columns': sorted(MOTION_COLUMNS),
                                  'table_motion_columns': {str(k): sorted(v) for k, v in TABLE_MOTION_COLUMNS.items()},
                                  'row_motion_columns': {str(k): sorted(v) for k, v in ROW_MOTION_COLUMNS.items()},
                                  'meaning': 'motion_path means the source provides some explicit body/weapon movement or contact/force path; it is not completeness, safety, factual accuracy, capability permission or video validation.',
                                  'reference_lists': 'Names only; a shared row does not supply individual movement detail.',
                                  'overrides': {str(k): {'detail': v[0], 'reason': v[1]} for k, v in DETAIL_OVERRIDES.items()}},
                'tables': table_coverage}
    return data, coverage


def navigation(cards, items):
    outputs = {}
    counts = Counter(item['card_id'] for item in items)
    kinds = sorted({card['kind'] for card in cards})
    root = ['# 战斗资料库导航', '',
            '先按任务选择分类，再读一张卡的改编与来源边界。无需先打开整个catalog；卡内原文按需展开。', '',
            '点名招式时优先使用 `library_tool.py items --query "招名"`，再用返回ID执行 `item`。方法见[检索流程](../references/library-workflow.md)。', '',
            '| 分类 | 卡数 | 命名条目 |', '| --- | --- | --- |']
    for kind in kinds:
        selected = [card for card in cards if card['kind'] == kind]
        root.append(f'| [{kind}]({kind}/index.md) | {len(selected)} | {sum(counts[c["id"]] for c in selected)} |')
        body = [f'# {kind}分类导航', '', '[返回总导航](../index.md) · [检索与来源规则](../../references/library-workflow.md)', '',
                '先按标题/流派选卡，读改编段；需要原文时按卡内来源行读取。详情等级在逐条检索中确认，不能由整卡等级代替。', '',
                '| 卡片 | 内容层级 | 命名条目 |', '| --- | --- | --- |']
        for card in selected:
            body.append(f'| [{card["title"]}]({card["id"]}.md) | {card["detail"]} | {counts[card["id"]]} |')
        outputs[f'skills/combat-director/library/{kind}/index.md'] = '\n'.join(body) + '\n'
    outputs['skills/combat-director/library/index.md'] = '\n'.join(root) + '\n'
    return outputs
