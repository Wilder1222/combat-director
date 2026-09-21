"""Optional visible-action contract; relational checks, not a physics engine."""
from __future__ import annotations

import copy
from combat_schema import require


def validate_action(plan):
    enabled = any(k in plan for k in ('weapon_profiles', 'action_initial_state'))
    has_events = any('action_events' in b or 'state_delta' in b for b in plan['beats'])
    if not enabled:
        require(not has_events, 'action events need weapon_profiles and action_initial_state')
        return []
    require(all(k in plan for k in ('weapon_profiles', 'action_initial_state')), 'incomplete action contract')
    actors = {a['id'] for a in plan['cast']}
    weapons = {w['id']: w for w in plan['weapon_profiles']}
    require(len(weapons) == len(plan['weapon_profiles']), 'duplicate weapon IDs')
    require(all(w['owner_id'] in actors for w in weapons.values()), 'unknown weapon owner')
    state = copy.deepcopy(plan['action_initial_state'])
    require(set(state['actors']) == actors, 'action_initial_state must include every actor')
    _check_items(state, weapons)
    camera_side = plan['initial_state']['camera_side']
    require(plan['initial_state'] == state_text(state, weapons, camera_side), 'initial_state must be derived from action_initial_state')
    for aid, actor in state['actors'].items():
        for item in actor['held_items'].values():
            if item:
                require(weapons[item]['owner_id'] == aid, 'initial item owner mismatch')
    abilities = {a['id']: a for a in plan['abilities']}
    active = set()
    seen = {}
    snapshots = []
    for beat in plan['beats']:
        label = beat['id']
        require('action_events' in beat and 'state_delta' in beat, f'{label}: action contract missing')
        before = copy.deepcopy(state)
        require(beat['before'] == state_text(before, weapons, camera_side), f'{label}: before differs from structured state')
        local = {}
        expected_hands = {a: copy.deepcopy(v['held_items']) for a, v in state['actors'].items()}
        added = {a: set() for a in actors}
        for event in beat['action_events']:
            eid, actor, target = event['id'], event['actor_id'], event['target_id']
            require(eid not in seen, f'{label}/{eid}: duplicate event')
            require(actor in actors and (not target or target in actors), f'{eid}: unknown participant')
            require(beat['start'] <= event['start'] < event['end'] <= beat['end'], f'{eid}: event outside beat')
            if local:
                require(event['start'] >= list(local.values())[-1]['start'], f'{eid}: event order')
            parent = event['response_to']
            if parent:
                require(parent in seen and seen[parent]['start'] <= event['start'], f'{eid}: response must name an earlier event')
            restrictions = set(state['actors'][actor]['constraints']) | added[actor]
            for hand in event['hands_used']:
                require(f'no_{hand}_hand' not in restrictions, f'{eid}: {hand} hand restricted')
            require(not ('no_running' in restrictions and event['movement'] == 'run'), f'{eid}: running restricted')
            wid = event['weapon_id']
            if wid:
                require(wid in weapons, f'{eid}: unknown weapon')
                profile = weapons[wid]
                if profile['mount'] == 'held':
                    held = {expected_hands[actor][h] for h in event['hands_used']}
                    require(wid in held, f'{eid}: selected weapon not held by the declared hand')
                else:
                    require(profile['owner_id'] == actor, f'{eid}: mounted weapon belongs to another actor')
            for transfer in event['transfers']:
                item, src, dst = transfer['item_id'], transfer['from_actor'], transfer['to_actor']
                require(item in weapons and weapons[item]['mount'] == 'held', f'{eid}: invalid transferred item')
                require(src in actors and src in (actor, target), f'{eid}: transfer source not involved')
                require(expected_hands[src][transfer['from_hand']] == item, f'{eid}: transfer source does not hold item')
                expected_hands[src][transfer['from_hand']] = ''
                if dst:
                    require(dst in actors and dst in (actor, target), f'{eid}: transfer target not involved')
                    require(transfer['to_hand'] in ('left', 'right'), f'{eid}: recipient hand required')
                    require(not expected_hands[dst][transfer['to_hand']], f'{eid}: recipient hand occupied')
                    expected_hands[dst][transfer['to_hand']] = item
                else:
                    require(transfer['to_hand'] == '' and bool(transfer['destination'].strip()), f'{eid}: dropped item needs location')
            use = event.get('ability_use')
            if use:
                aid = use['ability_id']
                require(aid in abilities and abilities[aid]['owner'] == actor, f'{eid}: invalid ability owner')
                require(aid in beat['ability_ids'], f'{eid}: ability missing from beat declaration')
                phase = use['phase']
                if phase == 'activate':
                    require(aid not in active, f'{eid}: ability already active')
                    active.add(aid)
                else:
                    require(aid in active, f'{eid}: ability not activated')
                if phase in ('consume', 'end'):
                    active.remove(aid)
                added[actor].update(use['restrictions_added'])
                require(not use['restrictions_added'] or bool(use['visible_cost'].strip()), f'{eid}: cost needs visible expression')
            seen[eid] = event
            local[eid] = event
        delta = beat['state_delta']
        require(set(delta['actors']) <= actors, f'{label}: unknown state actor')
        require(set(delta['environment']) <= state['environment'].keys(), f'{label}: undeclared environment anchor')
        require(set(delta['caused_by']) <= local.keys(), f'{label}: delta needs local event evidence')
        if delta['actors'] or delta['environment']:
            require(bool(delta['caused_by']), f'{label}: unexplained state change')
        for actor, changes in delta['actors'].items():
            require(any(actor in (local[e]['actor_id'], local[e]['target_id']) for e in delta['caused_by']),
                    f'{label}/{actor}: state change has no involving event')
            prior = state['actors'][actor]
            for key in ('damage', 'constraints'):
                if key in changes:
                    require(set(prior[key]) <= set(changes[key]), f'{label}/{actor}: {key} silently reset')
            prior.update(copy.deepcopy(changes))
        state['environment'].update(delta['environment'])
        for actor in actors:
            require(state['actors'][actor]['held_items'] == expected_hands[actor],
                    f'{label}/{actor}: held_items change needs transfer event and matching delta')
            require(added[actor] <= set(state['actors'][actor]['constraints']), f'{label}/{actor}: ability cost missing from state')
        _check_items(state, weapons)
        camera_side = beat['camera']['side']
        require(beat['after'] == state_text(state, weapons, camera_side), f'{label}: after differs from structured state')
        snapshots.append({'beat_id': label, 'before': before, 'after': copy.deepcopy(state),
                          'active_abilities': sorted(active)})
    return snapshots


def describe_actor(s, names):
    restrictions = {'no_right_hand':'右手不能继续动作','no_left_hand':'左手不能继续动作','no_running':'不能奔跑'}
    return (f'{s["zone"]}；{s["facing"]}；{s["support"]}；'
            f'左手{names.get(s["held_items"]["left"], "空")}，右手{names.get(s["held_items"]["right"], "空")}；'
            '损伤：'+('、'.join(s['damage']) or '无')+'；限制：'+('、'.join(restrictions[x] for x in s['constraints']) or '无'))


def state_text(state, weapons, camera_side):
    names = {wid:w['name'] for wid,w in weapons.items()}
    return {a:describe_actor(v,names) for a,v in state['actors'].items()} | {
        'environment':'；'.join(f'{k}：{v}' for k,v in state['environment'].items()), 'camera_side':camera_side}


def _check_items(state, weapons):
    held = [v for a in state['actors'].values() for v in a['held_items'].values() if v]
    require(len(held) == len(set(held)), 'one item cannot be held in multiple hands; use contact for temporary joint control')
    require(set(held) <= weapons.keys(), 'unknown held item')
    require(all(weapons[item]['mount'] == 'held' for item in held), 'mounted weapon cannot occupy a hand')


def action_text(plan, selected):
    if 'weapon_profiles' not in plan:
        return ''
    weapons = {w['id']: w for w in plan['weapon_profiles']}
    events = {e['id']: e for b in plan['beats'] for e in b['action_events']}
    lines = []
    for beat in selected:
        for e in beat['action_events']:
            weapon = weapons.get(e['weapon_id'])
            item = f'用{weapon["name"]}（{weapon["type"]}，{weapon["visible_traits"]}）' if weapon else ''
            parent = events.get(e['response_to'])
            response = f'回应{parent["actor_id"]}此前的动作；' if parent else ''
            t = e['trajectory']
            lines.append(f'{e["start"]:g}–{e["end"]:g}秒：{e["actor_id"]}{item}，{e["action"]}；{response}'
                         f'路径从{t["start"]}经{t["path"]}到{t["end"]}，画面方向{t["screen_direction"]}；'
                         f'接触/避让：{e["contact"]}；结果：{e["outcome"]}。')
            if e.get('ability_use'):
                use = e['ability_use']
                phase = {'activate': '发动', 'sustain': '维持', 'consume': '消耗结束', 'end': '结束'}[use['phase']]
                lines.append(f'{e["actor_id"]}的能力{phase}；可见代价：{use["visible_cost"] or "此时无新增代价"}。')
        delta = beat['state_delta']
        if delta['actors'] or delta['environment']:
            labels = {'zone': '位置', 'facing': '朝向', 'support': '支撑', 'damage': '损伤', 'constraints': '限制'}
            restrictions = {'no_right_hand': '右手不能继续动作', 'no_left_hand': '左手不能继续动作', 'no_running': '不能奔跑'}
            parts = []
            for actor, values in delta['actors'].items():
                for key, value in values.items():
                    if key == 'held_items':
                        for hand, item in value.items():
                            parts.append(f'{actor}{"左手" if hand == "left" else "右手"}{"持" + weapons[item]["name"] if item else "空着"}')
                    else:
                        wording = '、'.join(restrictions.get(v, v) for v in value) if isinstance(value, list) else value
                        parts.append(f'{actor}{labels[key]}：{wording or "无"}')
            parts.extend(f'{anchor}：{value}' for anchor, value in delta['environment'].items())
            lines.append('本拍之后：' + '；'.join(parts) + '。')
    return '\n'.join(lines)
