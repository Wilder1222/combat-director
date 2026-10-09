"""Bind authored compact prose to a reviewed plan; no automatic semantic rewriting."""
from __future__ import annotations

import argparse
import copy
import json
import re
import sys
from pathlib import Path

from combat_handoff import compile_handoff, digest
from combat_schema import require

SHOT_LABELS = ('整体风格', '战斗人物', '环境空间关系', '前中后景与远近层次', '景别与远近景切换', '武器样式', '行为逻辑', '人物行动轨迹', '身体与武器动作轨迹', '空间环境交互', '招式', '技能与能力边界', '法阵', '法术效果', '手印变化', '命中效果', '战斗特效', '光影', '运镜', '切镜', '动态模糊', '时间与速度', '面部微表情', '眼神', '情绪')
GROUPED_SHOT_LABELS = ('画面与动作', '摄影', '衔接', '声音')


CHECKS = ('event_coverage', 'scene_camera', 'identity_ability', 'rhythm', 'constraints')
FIELDS = {'format', 'plan_id', 'source_digest', 'opening', 'sections', 'closing', 'review'}


def prepare(plan):
    return {'format': 'combat-prompt/1', 'plan_id': plan['id'],
            'source_digest': digest(compile_handoff(plan)), 'opening': '',
            'sections': [{'section_id': s['id'], 'text': ''} for s in plan['sections']],
            'closing': '', 'review': None}


def inspect(plan, projection):
    require(isinstance(projection, dict) and set(projection) == FIELDS, 'invalid compact prompt fields')
    require(projection['format'] == 'combat-prompt/1', 'unsupported compact prompt format')
    require(projection['plan_id'] == plan['id'], 'compact prompt plan_id mismatch')
    require(projection['source_digest'] == digest(compile_handoff(plan)),
            'compact prompt source is stale; reconcile against current plan')
    for key in ('opening', 'closing'):
        require(isinstance(projection[key], str) and bool(projection[key].strip()), f'compact {key} is empty')
    sections = projection['sections']
    require(isinstance(sections, list), 'compact sections must be a list')
    for section in sections:
        require(isinstance(section, dict) and set(section) == {'section_id', 'text'}, 'invalid compact section')
        require(isinstance(section['section_id'], str), 'compact section_id must be a string')
        require(isinstance(section['text'], str) and bool(section['text'].strip()), 'compact section text is empty')
    require([s['section_id'] for s in sections] == [s['id'] for s in plan['sections']],
            'compact sections must cover original sections once in order')
    expression = {k: projection[k] for k in ('opening', 'sections', 'closing')}
    return {'plan_id': plan['id'], 'source_digest': projection['source_digest'],
            'expression_digest': digest(expression), 'expression': copy.deepcopy(expression),
            'source': compile_handoff(plan), 'required_checks': list(CHECKS)}


def check_receipt(compiled, receipt):
    require(isinstance(receipt, dict) and set(receipt) == {
        'plan_id', 'source_digest', 'expression_digest', 'reviewer', 'method', 'checks'},
        'invalid compact review receipt fields')
    for key in ('plan_id', 'source_digest', 'expression_digest'):
        require(receipt[key] == compiled[key], f'compact review {key} is stale or mismatched')
    require(isinstance(receipt['reviewer'], str) and bool(receipt['reviewer'].strip()), 'compact reviewer missing')
    require(receipt['method'] in ('human', 'agent'), 'compact review method must be human or agent')
    require(isinstance(receipt['checks'], dict) and set(receipt['checks']) == set(CHECKS), 'compact review checks incomplete')
    require(all(isinstance(v, str) and bool(v.strip()) for v in receipt['checks'].values()),
            'compact checks need evidence explanations, not booleans')


def apply_review(plan, projection, receipt):
    check_receipt(inspect(plan, projection), receipt)
    result = copy.deepcopy(projection)
    result['review'] = copy.deepcopy(receipt)
    return result


def check_shot_details(text, section_id):
    """Check authored per-shot structure without inventing missing creative details."""
    headings = list(re.finditer(r'^【([^】\r\n]+)】', text, re.MULTILINE))
    labels = [m.group(1) for m in headings]
    require(bool(labels), f'{section_id}: each shot needs relevant Chinese type labels')
    require(all(label in SHOT_LABELS + GROUPED_SHOT_LABELS for label in labels),
            f'{section_id}: use unnumbered Chinese type labels')
    require(len(labels) == len(set(labels)), f'{section_id}: duplicate shot labels')
    require(not text[:headings[0].start()].strip(), f'{section_id}: place prose under its shot labels')
    for index, heading in enumerate(headings):
        end = headings[index + 1].start() if index + 1 < len(headings) else len(text)
        value = text[heading.end():end].strip()
        require(bool(value) and value.rstrip('。；;') not in ('同上', '沿用设定', '略', '待补充'),
                f'{section_id}: {heading.group(1)} needs authored shot-specific content')


def render(plan, projection, detailed=False):
    compiled = inspect(plan, projection)
    check_receipt(compiled, projection['review'])
    beats = {b['id']: b for b in plan['beats']}
    blocks = [projection['opening'].strip() if detailed
              else '【战斗设置】\n' + projection['opening'].strip()]
    one_take_details = detailed and plan['camera_mode'] == 'one-take'
    if one_take_details:
        start, end = plan['beats'][0]['start'], plan['beats'][-1]['end']
        blocks.append(f'全镜{start:g}–{end:g}秒（镜长{end-start:g}秒）')
    action_label = '连续动作' if plan['camera_mode'] == 'one-take' else '动作分镜'
    for source, section in zip(plan['sections'], projection['sections']):
        start = beats[source['beat_ids'][0]]['start']
        end = beats[source['beat_ids'][-1]]['end']
        if detailed:
            check_shot_details(section['text'], section['section_id'])
        interval_label = '镜内节拍' if one_take_details else '镜长'
        heading = f'{start:g}–{end:g}秒（{interval_label}{end-start:g}秒）'
        if not detailed:
            heading = f'【{action_label}】' + heading
        blocks.append(heading + '\n' + section['text'].strip())
    blocks.append(projection['closing'].strip() if detailed
                  else '【连续性】\n' + projection['closing'].strip())
    return '\n\n'.join(blocks) + '\n'


def main(argv=None):
    # Import here to avoid a circular dependency with the main exporter.
    from combat_tool import read_json, validate, write_artifact
    parser = argparse.ArgumentParser(description=__doc__)
    sub = parser.add_subparsers(dest='command', required=True)
    for name in ('prepare', 'compile', 'apply-review', 'validate'):
        p = sub.add_parser(name)
        p.add_argument('plan', type=Path)
        if name != 'prepare':
            p.add_argument('projection', type=Path)
        if name != 'validate':
            p.add_argument('--out', type=Path, required=True)
        if name == 'apply-review':
            p.add_argument('--receipt', type=Path, required=True)
    args = parser.parse_args(argv)
    try:
        plan = read_json(args.plan)
        validate(plan, require_review=args.command == 'validate')
        if args.command == 'prepare':
            value = prepare(plan)
        else:
            projection = read_json(args.projection)
            if args.command == 'compile':
                value = inspect(plan, projection)
            elif args.command == 'apply-review':
                value = apply_review(plan, projection, read_json(args.receipt))
            else:
                render(plan, projection)
                print('VALID compact review binding; semantics and media are not automatically verified')
                return 0
        # write_artifact never overwrites existing input or output files.
        write_artifact(value, args.out, args.plan)
        print(f'Written: {args.out}')
        return 0
    except (ValueError, OSError) as error:
        print(f'INVALID: {error}', file=sys.stderr)
        return 1


if __name__ == '__main__':
    raise SystemExit(main())
