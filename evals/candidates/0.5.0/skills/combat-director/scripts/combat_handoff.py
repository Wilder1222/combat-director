"""Compile reviewable facts and bind editorial prose to the reviewed revision.

A review receipt is an attribution, not automated proof of semantic correctness.
"""
from __future__ import annotations

import copy
import hashlib
import json
from combat_schema import require

CHECKS = ('identity_action', 'camera_timing', 'ability_cost', 'continuity')
GLOBAL_KEYS = ('duration', 'aspect_ratio', 'generation', 'camera_mode', 'rules', 'timing',
               'cast', 'abilities', 'anchors', 'references', 'initial_state',
               'weapon_profiles', 'action_initial_state')


def normalized(value):
    if isinstance(value, dict):
        return {key: normalized(item) for key, item in value.items()}
    if isinstance(value, list):
        return [normalized(item) for item in value]
    if isinstance(value, str):
        return '\n'.join(line.rstrip() for line in value.replace('\r\n', '\n').strip().splitlines())
    if type(value) is float and value.is_integer():
        return int(value)
    return value


def digest(value):
    raw = json.dumps(normalized(value), sort_keys=True, ensure_ascii=False,
                     separators=(',', ':'), allow_nan=False).encode('utf-8')
    return hashlib.sha256(raw).hexdigest()


def compile_handoff(plan):
    facts = {key: copy.deepcopy(plan[key]) for key in GLOBAL_KEYS if key in plan}
    header_facts = copy.deepcopy(facts)
    header_facts['ending_state'] = copy.deepcopy(plan['beats'][-1]['after'])
    scopes = [{'scope': 'headers', 'facts': header_facts, 'expression': copy.deepcopy(plan['headers'])}]
    beats = {b['id']: b for b in plan['beats']}
    preceding = []
    for section in plan['sections']:
        selected = [copy.deepcopy(beats[bid]) for bid in section['beat_ids']]
        scopes.append({'scope': section['id'], 'facts': {'global': facts, 'beats': selected,
                       'inherited_states': copy.deepcopy(preceding)},
                       'expression': copy.deepcopy(section['summary'])})
        preceding.extend({key: copy.deepcopy(beat[key]) for key in
                          ('id', 'after', 'ability_ids', 'action_events', 'state_delta') if key in beat}
                         for beat in selected)
    for scope in scopes:
        scope['input_digest'] = digest(scope['facts'])
        scope['expression_digest'] = digest(scope['expression'])
    return {'format': 'combat-handoff/1', 'plan_id': plan['id'], 'scopes': scopes}


def readiness(plan):
    scopes = compile_handoff(plan)['scopes']
    reviews = plan.get('editorial_reviews', {})
    result = []
    for scope in scopes:
        review = reviews.get(scope['scope'])
        if not review:
            status = 'needs_semantic_review'
        elif any(review[key] != scope[key] for key in ('input_digest', 'expression_digest')):
            status = 'stale'
        else:
            status = 'ready'
        result.append({'scope': scope['scope'], 'status': status})
    return result


def require_ready(plan):
    require(plan.get('schema_version') != '1.0', 'legacy 1.0: migrate and review before render')
    bad = [f'{item["scope"]}={item["status"]}' for item in readiness(plan) if item['status'] != 'ready']
    require(not bad, 'editorial review required: ' + ', '.join(bad) + '; compile, revise, then apply-review')


def apply_review(plan, receipt):
    require(isinstance(receipt, dict), 'review receipt must be an object')
    require(set(receipt) == {'plan_id', 'reviews'}, 'review receipt needs plan_id and reviews only')
    require(receipt['plan_id'] == plan['id'], 'review plan_id mismatch')
    require(isinstance(receipt['reviews'], list) and bool(receipt['reviews']), 'empty review receipt')
    scopes = {s['scope']: s for s in compile_handoff(plan)['scopes']}
    changed = copy.deepcopy(plan)
    seen = set()
    for review in receipt['reviews']:
        require(isinstance(review, dict) and set(review) == {'scope', 'input_digest', 'expression_digest',
                'reviewer', 'method', 'checks'}, 'invalid review record fields')
        name = review['scope']
        require(isinstance(name, str) and name in scopes and name not in seen,
                f'unknown or duplicate review scope: {name}')
        seen.add(name)
        for key in ('input_digest', 'expression_digest'):
            require(review[key] == scopes[name][key], f'{name}: {key} changed since review; compile again')
        require(isinstance(review['reviewer'], str) and bool(review['reviewer'].strip()), f'{name}: missing reviewer')
        require(review['method'] in ('human', 'agent'), f'{name}: method must be human or agent')
        require(isinstance(review['checks'], dict) and set(review['checks']) == set(CHECKS), f'{name}: incomplete checks')
        require(all(isinstance(v, str) and bool(v.strip()) for v in review['checks'].values()),
                f'{name}: each check needs an evidence explanation, not a boolean')
        changed.setdefault('editorial_reviews', {})[name] = {k: v for k, v in review.items() if k != 'scope'}
    return changed


def hard_constraints(plan):
    mode = '一镜到底，全程连续，不切镜、不跳切' if plan['camera_mode'] == 'one-take' else '允许内部切镜'
    ranks = {'person': '人物级', 'arena': '场地级', 'landscape': '地貌级'}
    lines = [f'总时长{plan["duration"]:g}秒，{plan["aspect_ratio"]}，单次生成；{mode}。',
             f'幻想能力：{"允许" if plan["rules"]["fantasy"] else "禁止"}；尺度上限：{ranks[plan["rules"]["max_scale"]]}。',
             f'入点{plan["timing"]["lead_in"]:g}秒，出点{plan["timing"]["tail_out"]:g}秒，结果在{plan["timing"]["result_at"]:g}秒前落定，全部包含在总时长内。']
    for a in plan['cast']:
        lines.append(f'{a["id"]}：{a["description"]}；目标：{a["goal"]}；初始持物：{a["prop"]}；持械：{a["hand"]}。')
    for a in plan['abilities']:
        lines.append(f'{a["id"]}归属{a["owner"]}：触发{a["trigger"]}；表现{a["visual"]}；限制{a["limit"]}；代价{a["cost"]}；结束条件{a["end_condition"]}。')
    return '\n'.join(lines)
