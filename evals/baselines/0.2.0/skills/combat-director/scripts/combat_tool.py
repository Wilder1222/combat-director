#!/usr/bin/env python3
"""Offline combat-plan validation and text export (Python 3.10+, standard library)."""
from __future__ import annotations

import argparse
import json
import math
import sys
from pathlib import Path

SKILL = Path(__file__).resolve().parents[1]
EPS = 1e-6
TRACKS = ('action', 'expression', 'emotion', 'camera', 'vfx', 'environment', 'sound', 'continuity')
LABELS = ('动作', '表情', '情绪', '运镜', '特效', '环境反馈', '声音', '连续性')


def read_json(path):
    return json.loads(Path(path).read_text(encoding='utf-8-sig'),
                      parse_constant=lambda s: (_ for _ in ()).throw(ValueError(f'Non-finite number: {s}')))


def require(condition, message):
    if not condition:
        raise ValueError(message)


def check_schema(value, rule, schema, location='$'):
    """Validate only the JSON Schema keywords used by the bundled schema."""
    if '$ref' in rule:
        rule = schema['$defs'][rule['$ref'].split('/')[-1]]
    kind = rule.get('type')
    valid = {'object': isinstance(value, dict), 'array': isinstance(value, list),
             'string': isinstance(value, str), 'boolean': isinstance(value, bool),
             'number': type(value) in (int, float) and math.isfinite(value)}
    if kind:
        require(valid[kind], f'{location}: expected {kind}')
    if 'const' in rule:
        require(value == rule['const'], f'{location}: incorrect constant')
    if 'enum' in rule:
        require(value in rule['enum'], f'{location}: invalid choice')
    if kind == 'string':
        require(len(value.strip()) >= rule.get('minLength', 0), f'{location}: empty text')
    if kind == 'number':
        require(value >= rule.get('minimum', -math.inf), f'{location}: below minimum')
        require(value > rule.get('exclusiveMinimum', -math.inf), f'{location}: must be positive')
    if kind == 'array':
        require(len(value) >= rule.get('minItems', 0), f'{location}: too few items')
        for i, item in enumerate(value):
            check_schema(item, rule['items'], schema, f'{location}[{i}]')
    if kind == 'object':
        require(set(rule.get('required', [])) <= value.keys(), f'{location}: missing required fields')
        props = rule.get('properties', {})
        for key, item in value.items():
            if key in props:
                check_schema(item, props[key], schema, f'{location}.{key}')
            else:
                extra = rule.get('additionalProperties', True)
                require(extra is not False, f'{location}: unknown field {key}')
                if isinstance(extra, dict):
                    check_schema(item, extra, schema, f'{location}.{key}')


def unique(items, label):
    ids = [item['id'] for item in items]
    require(len(ids) == len(set(ids)), f'{label}: duplicate IDs')
    return set(ids)


def validate(plan, max_duration=None):
    schema = read_json(SKILL / 'assets/combat-plan.schema.json')
    check_schema(plan, schema, schema)
    if max_duration is not None:
        require(type(max_duration) in (int, float) and math.isfinite(max_duration) and max_duration > 0,
                'max-duration must be positive and finite')
        require(plan['duration'] <= max_duration + EPS, 'single-generation duration exceeds confirmed limit')
    cast = unique(plan['cast'], 'cast')
    require(len(cast) >= 2, 'at least two participants required')
    ability_ids = unique(plan['abilities'], 'abilities')
    abilities = {a['id']: a for a in plan['abilities']}
    ranks = {'person': 0, 'arena': 1, 'landscape': 2}
    for a in plan['abilities']:
        require(a['owner'] in cast, 'ability owner not in cast')
        require(ranks[a['scale']] <= ranks[plan['rules']['max_scale']], 'ability exceeds scale limit')
        require(plan['rules']['fantasy'] or not a['supernatural'], 'supernatural ability forbidden')
    timing = plan['timing']
    require(timing['lead_in'] + timing['tail_out'] < plan['duration'], 'no action window left')
    require(timing['lead_in'] <= timing['result_at'] <= plan['duration'] - timing['tail_out'] + EPS,
            'result timing exceeds action window')
    unique(plan['references'], 'references')
    for ref in plan['references']:
        require(ref['status'] != 'bound' or bool(ref['binding_evidence'].strip()), 'bound reference needs evidence')
        require(set(ref['actors']) <= cast, 'reference names unknown actor')
    unique(plan['beats'], 'beats')
    state_keys = cast | {'environment', 'camera_side'}
    prior = plan['initial_state']
    require(set(prior) == state_keys, 'initial state must include all participants, environment and camera side')
    elapsed = 0
    shots = set()
    for index, beat in enumerate(plan['beats']):
        require(abs(beat['start'] - elapsed) <= EPS, 'timeline gap or overlap')
        require(beat['end'] > beat['start'], 'beat must have positive duration')
        require(set(beat['actors']) == cast, 'every participant needs action and performance')
        require(set(beat['before']) == set(beat['after']) == state_keys, 'state keys incomplete')
        require(beat['before'] == prior, 'state inheritance mismatch')
        camera = beat['camera']
        require(camera['side'] == beat['after']['camera_side'], 'camera and state sides disagree')
        if camera['side'] != prior['camera_side']:
            require(bool(camera['axis_bridge'].strip()), 'axis change needs visible bridge')
        if index == 0:
            require(camera['transition'] == 'start', 'first beat must start camera path')
        else:
            require(camera['transition'] != 'start', 'camera cannot restart mid-sequence')
            same = camera['shot_id'] == plan['beats'][index-1]['camera']['shot_id']
            require(same == (camera['transition'] == 'continuous'), 'shot ID / transition mismatch')
        if plan['camera_mode'] == 'one-take':
            require(camera['transition'] in ('start', 'continuous'), 'one-take forbids cuts')
        shots.add(camera['shot_id'])
        require(set(beat['ability_ids']) <= ability_ids, 'unknown ability')
        for aid in beat['ability_ids']:
            owner = abilities[aid]['owner']
            require(bool(beat['actors'][owner]['action']), 'ability owner must act')
        prior, elapsed = beat['after'], beat['end']
    require(abs(elapsed - plan['duration']) <= EPS, 'timeline must cover full duration')
    if plan['camera_mode'] == 'one-take':
        require(len(shots) == 1, 'one-take needs one shot ID')
    unique(plan['sections'], 'sections')
    flattened = [bid for section in plan['sections'] for bid in section['beat_ids']]
    require(flattened == [b['id'] for b in plan['beats']], 'sections must cover beats once in order')
    return plan


def fmt(value):
    return f'{value:g}'


def prompt(plan):
    beats = {b['id']: b for b in plan['beats']}
    blocks = [f'<{label}>\n{plan["headers"][key]}' for key, label in
              [('goal', '创作目标'), ('cast', '人物与目标'), ('scene', '场景与规则'), ('budget', '时间预算')]]
    for section in plan['sections']:
        first, last = beats[section['beat_ids'][0]], beats[section['beat_ids'][-1]]
        lines = [f'<时间段 {fmt(first["start"])}至{fmt(last["end"])}秒>']
        lines.extend(f'<{label}> {section["summary"][key]}' for key, label in zip(TRACKS, LABELS))
        blocks.append('\n'.join(lines))
    blocks.append('<全程连续性>\n' + plan['headers']['continuity'])
    return '\n\n'.join(blocks) + '\n'


def deliverables(plan, platform):
    profiles = read_json(SKILL / 'assets/platform-profiles.json')['profiles']
    require(platform in profiles, f'unknown platform: {platform}')
    profile = profiles[platform]
    director = ['# 六轨导演稿', '', '时间及状态独立于六轨；表情与情绪合为表演轨。', '']
    for beat in plan['beats']:
        director += [f'## {beat["id"]} · {fmt(beat["start"])}–{fmt(beat["end"])} 秒',
                     f'目的：{beat["intent"]}', '',
                     '1. 人物攻防：' + '；'.join(f'{a}：{v["action"]}' for a, v in beat['actors'].items()),
                     '2. 表演情绪：' + '；'.join(f'{a}：{v["performance"]}' for a, v in beat['actors'].items()) + '。' + beat['emotion'],
                     f'3. 摄影机：{beat["camera"]["shot_id"]} / {beat["camera"]["transition"]} / {beat["camera"]["path"]}',
                     '4. 特效：' + beat['vfx'], '5. 环境反馈：' + beat['environment'], '6. 声音：' + beat['sound'],
                     '', '起始状态：' + json.dumps(beat['before'], ensure_ascii=False),
                     '结束状态：' + json.dumps(beat['after'], ensure_ascii=False), '']
    handoff = f'# {profile["display_name"]}交接\n\n状态：{profile["status"]}。本工具没有查询平台或提交生成。\n\n'
    handoff += f'目标：{fmt(plan["duration"])} 秒，{plan["aspect_ratio"]}，单次生成，{plan["camera_mode"]}。\n\n'
    handoff += '\n'.join('- 待核验：' + x for x in profile['checks'])
    handoff += '\n\n参考记录：\n' + ('\n'.join(f'- {r["id"]}: {r["status"]}；用途：{r["controls"]}；排除：{r["excludes"]}' for r in plan['references']) or '- 无素材记录；不声称已绑定。')
    handoff += '\n\n若当前入口不能满足单次时长，停止提交并说明冲突；不得以拼接冒充单次。\n'
    card = '# 战斗设计卡\n\n' + plan['headers']['goal'] + '\n\n' + plan['headers']['cast']
    card += '\n\n规则：\n' + plan['headers']['scene'] + '\n\n时间预算：\n' + plan['headers']['budget']
    card += '\n\n来源：' + plan['provenance'] + '\n'
    review = '# 验收表（待实际视频）\n\n未生成、未观看视频；本表不是验收通过证明。\n\n'
    review += '| 检查项 | 时间码/证据 | 问题 | 最小修复 | 复测结果 |\n| --- | --- | --- | --- | --- |\n'
    review += '\n'.join(f'| {x} | 待观察 | 待观察 | 待确定 | 未验证 |' for x in ['身份与持物', '攻防因果', '双方表演', '空间与机位', '能力限制与代价', '环境继承', '声音', '目标时长与结尾']) + '\n'
    return {'design-card.md': card, 'director.md': '\n'.join(director), 'prompt.txt': prompt(plan),
            'handoff.md': handoff, 'review.md': review,
            'combat-plan.json': json.dumps(plan, ensure_ascii=False, indent=2, allow_nan=False) + '\n'}


def export(plan, platform, out_dir, force=False, source_path=None, max_duration=None):
    validate(plan, max_duration)
    output = Path(out_dir).absolute()
    for ancestor in (output, *output.parents):
        require(not ancestor.is_symlink() and not getattr(ancestor, 'is_junction', lambda: False)(),
                'output must not traverse a link or junction')
    payloads = deliverables(plan, platform)
    for name in payloads:
        path = output / name
        require(not path.is_symlink(), 'refusing linked output file')
        require(not path.exists() or path.is_file(), 'output target is not a file')
        require(source_path is None or path.resolve() != Path(source_path).resolve(), 'refusing to overwrite source plan')
        require(force or not path.exists(), f'output exists: {path}; use --force to replace')
    output.mkdir(parents=True, exist_ok=True)
    for name, content in payloads.items():
        (output / name).write_text(content, encoding='utf-8')
    return list(payloads)


def main(argv=None):
    parser = argparse.ArgumentParser(description=__doc__)
    sub = parser.add_subparsers(dest='command', required=True)
    for command in ('validate', 'render'):
        p = sub.add_parser(command)
        p.add_argument('plan', type=Path)
        p.add_argument('--max-duration', type=float)
        if command == 'render':
            p.add_argument('--platform', choices=('generic', 'libtv', 'xiaoyunque', 'flova'), default='generic')
            p.add_argument('--out-dir', type=Path, required=True)
            p.add_argument('--force', action='store_true')
    args = parser.parse_args(argv)
    try:
        plan = read_json(args.plan)
        validate(plan, args.max_duration)
        if args.command == 'render':
            export(plan, args.platform, args.out_dir, args.force, args.plan, args.max_duration)
            print(f'Exported 6 text files: {args.out_dir}')
        else:
            print(f'VALID: {plan["id"]}; {len(plan["beats"])} beats, {len(plan["sections"])} sections')
        return 0
    except (ValueError, OSError) as error:
        print(f'INVALID: {error}', file=sys.stderr)
        return 1


if __name__ == '__main__':
    raise SystemExit(main())
