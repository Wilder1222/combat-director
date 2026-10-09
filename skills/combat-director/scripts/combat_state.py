"""Replay the optional 1.3 state contract. Checks relations, never physical truth.

Item holders are authoritative in v2; hand descriptions are projections. Operations
take effect at event.end. At equal timestamps, endings precede new starts.
"""
from __future__ import annotations

import copy
import json
from pathlib import Path
from combat_schema import check_schema, require

FORMAT = 'combat-action-state/2'
DOMAINS = {'body': 'actors', 'item': 'items', 'contact': 'contacts', 'effect': 'effects',
           'formation': 'formations', 'pending': 'pending_events', 'hand_exception': 'hand_exceptions'}
DEFINITIONS = {'body': 'body_state', 'item': 'item_state', 'contact': 'contact_state',
               'effect': 'effect_state', 'formation': 'formation_state', 'pending': 'pending_state',
               'hand_exception': 'hand_exception'}


def is_v2(plan):
    return plan.get('action_initial_state', {}).get('format') == FORMAT


def profiles_for(plan):
    profiles = plan.get('body_profiles')
    if profiles is None:
        return {a['id']: {'id': a['id'], 'identity_id': a['id'], 'kind': 'original',
                         'can_interact': True, 'source': 'cast identity'} for a in plan['cast']}
    result = {b['id']: b for b in profiles}
    require(len(result) == len(profiles), 'duplicate body IDs')
    identities = {a['id'] for a in plan['cast']}
    require({b['identity_id'] for b in profiles} == identities, 'body identities must cover exactly cast')
    return result


def hand_items(state):
    result = {b: {'left': [], 'right': []} for b in state['actors']}
    for item, data in state['items'].items():
        for holder in data['holders']:
            body, hand = holder['body_id'], holder['hand']
            require(body in result, 'item holder names unknown body')
            result[body][hand].append(item)
    return result


def _hand_exception(state, body, hand, items, casting=False):
    return any(rule['phase'] == 'active' and rule['body_id'] == body and rule['hand'] == hand and
               set(items) <= set(rule['item_ids']) and (not casting or rule['allows_casting'])
               for rule in state.get('hand_exceptions', {}).values())


def _trigger_kind(state, event, ability):
    """Use declared trigger structure; a narrow untyped device compatibility case.

    No trigger/action prose is parsed. Compatibility applies only to ordinary,
    selected held items with a single item in every participating grip hand.
    """
    explicit = ability.get('trigger_spec')
    if explicit:
        return explicit['kind']
    wid, body = event['weapon_id'], event['actor_id']
    if not ability['supernatural'] and wid and event.get('weapon_mode', 'held') == 'held' and event['hands_used']:
        held = hand_items(state)[body]
        if all(held[hand] == [wid] for hand in event['hands_used']):
            return 'held-item'
    return 'independent'


def _live(state, body):
    return body in state['actors'] and state['actors'][body]['status'] == 'active'


def _dependency_active(state, name):
    kind, separator, key = name.partition(':')
    require(separator and kind in ('ability', 'body', 'effect', 'formation', 'contact'),
            f'invalid dependency {name}')
    if kind == 'ability':
        aid, marker, body = key.partition('@')
        require(marker and aid and body, 'ability dependency needs ability:ID@BODY instance')
        return {'ability_id': aid, 'body_id': body} in state['active_abilities']
    if kind == 'body':
        return _live(state, key)
    field = DOMAINS[kind]
    return key in state[field] and state[field][key]['phase'] not in ('ended', 'released')


def validate_world(state, profiles, weapons, abilities, schema):
    """Validate one authoritative snapshot, also used for observed state input."""
    check_schema(state, schema['$defs']['action_state_v2'], schema)
    require(set(state['actors']) == set(profiles), 'structured state must include every body')
    require(set(state['items']) == set(weapons), 'item state must cover every weapon exactly once')
    for activation in state['active_abilities']:
        aid, body = activation['ability_id'], activation['body_id']
        require(aid in abilities and body in profiles, 'unknown active ability/body')
        require(abilities[aid]['owner'] == profiles[body]['identity_id'], 'active ability owner mismatch')
        require(_live(state, body), 'active ability maintained by inactive body')
    hands = hand_items(state)
    for key, rule in state.get('hand_exceptions', {}).items():
        body = rule['body_id']
        require(body in profiles and set(rule['item_ids']) <= set(weapons), f'{key}: unknown exception body/item')
        require(rule['item_ids'] or rule['allows_casting'], f'{key}: empty item scope only valid for explicit casting exception')
        if rule['phase'] == 'active':
            require(_live(state, body), f'{key}: active hand exception on inactive body')
            if rule['kind'] == 'ability':
                aid = rule['ability_id']
                require(aid in abilities and abilities[aid]['owner'] == profiles[body]['identity_id'],
                        f'{key}: hand exception ability owner mismatch')
                require({'ability_id': aid, 'body_id': body} in state['active_abilities'],
                        f'{key}: hand exception needs active ability')
            else:
                require(not rule['ability_id'], f'{key}: mechanical grip cannot imply an active ability')
    for body, hand_map in hands.items():
        for hand, held in hand_map.items():
            require(len(held) <= 1 or _hand_exception(state, body, hand, held),
                    f'{body}/{hand}: hand already holds another item; explicit scoped grip exception required')
    for wid, item in state['items'].items():
        if item['holders']:
            require(not item['location'], f'{wid}: held item cannot also have free location')
        else:
            require(bool(item['location'].strip()), f'{wid}: unheld item needs a location')
        require(item['status'] == 'active' or not item['holders'], f'{wid}: terminal item still held')
        require(item['status'] == 'active' or item['control_mode'] == 'none', f'{wid}: terminal item still controlled')
        for holder in item['holders']:
            body = holder['body_id']
            require(_live(state, body) and profiles[body]['can_interact'], f'{wid}: holder cannot interact')
        require(weapons[wid]['mount'] == 'held' or not item['holders'], f'{wid}: mounted weapon occupies hand')
        controller, mode = item['controller_id'], item['control_mode']
        require((mode in ('held', 'remote')) == bool(controller), f'{wid}: controller/mode mismatch')
        if controller:
            require(_live(state, controller), f'{wid}: controller is not active')
        if mode == 'held':
            require(controller in {h['body_id'] for h in item['holders']}, f'{wid}: held control needs possession')
        if mode in ('remote', 'autonomous'):
            require(bool(item['control_basis'].strip()), f'{wid}: exceptional control needs explicit basis')
            aid = item['control_ability_id']
            require(aid in abilities, f'{wid}: exceptional control needs declared ability')
            if controller:
                require(abilities[aid]['owner'] == profiles[controller]['identity_id'], f'{wid}: wrong control ability owner')
                require({'ability_id': aid, 'body_id': controller} in state['active_abilities'],
                        f'{wid}: remote control needs active ability on controlling body')
        else:
            require(not item['control_ability_id'], f'{wid}: unused control ability')
    for cid, contact in state['contacts'].items():
        require(len(contact['endpoints']) == 2, f'{cid}: contact must pair exactly two endpoints')
        require(contact['endpoints'][0] != contact['endpoints'][1], f'{cid}: identical contact endpoints')
        for endpoint in contact['endpoints']:
            body, item = endpoint['body_id'], endpoint['item_id']
            require(body in profiles, f'{cid}: unknown contact body')
            require(not item or item in weapons, f'{cid}: unknown contact item')
            if contact['phase'] == 'active':
                require(_live(state, body) and profiles[body]['can_interact'], f'{cid}: contact body cannot interact')
                if item:
                    require(any(item in held for held in hands[body].values()) or state['items'][item]['controller_id'] == body,
                            f'{cid}: contact item has no possession/control relation')
    for eid, effect in state['effects'].items():
        require(effect['owner_id'] in profiles, f'{eid}: unknown effect owner')
        require(not effect['ability_id'] or effect['ability_id'] in abilities, f'{eid}: unknown effect ability')
        if effect['ability_id']:
            require(abilities[effect['ability_id']]['owner'] == profiles[effect['owner_id']]['identity_id'],
                    f'{eid}: effect ability owner mismatch')
        require(not effect['item_id'] or effect['item_id'] in weapons, f'{eid}: unknown projectile item')
        if effect['phase'] != 'ended':
            if effect['controller_id']:
                require(_live(state, effect['controller_id']), f'{eid}: inactive effect controller')
            require(all(_dependency_active(state, dep) for dep in effect['dependencies']),
                    f'{eid}: interrupted dependency needs explicit effect disposition')
            for occupied in effect.get('occupied_hands', []):
                require(_live(state, occupied['body_id']), f'{eid}: hand maintenance by inactive body')
            if effect['item_id']:
                item = state['items'][effect['item_id']]
                require(not item['holders'] and item['location'] == effect['location'],
                        f'{eid}: physical projectile position differs from the same item')
    for fid, formation in state['formations'].items():
        require(not formation['owner_id'] or formation['owner_id'] in profiles, f'{fid}: unknown formation owner')
        attachment = formation['attachment']
        kind, key = attachment['kind'], attachment['id']
        if kind == 'body':
            require(key in profiles, f'{fid}: unknown attachment body')
            if formation['phase'] != 'ended':
                require(_live(state, key), f'{fid}: formation attached to inactive body')
        elif kind == 'item':
            require(key in weapons, f'{fid}: unknown attachment item')
        elif kind == 'anchor':
            require(key in state['environment'], f'{fid}: unknown attachment anchor')
        else:
            require(not key, f'{fid}: world attachment cannot name another entity')
        if formation['phase'] != 'ended':
            require(all(_dependency_active(state, dep) for dep in formation['dependencies']),
                    f'{fid}: interrupted dependency needs explicit formation disposition')
            if formation['phase'] == 'partial':
                phases = {node['phase'] for node in formation['nodes'].values()}
                require('active' in phases and 'broken' in phases, f'{fid}: partial formation needs intact and broken nodes')
    for pid, pending in state['pending_events'].items():
        require(pending['actor_id'] in profiles and (not pending['target_id'] or pending['target_id'] in profiles),
                f'{pid}: unknown pending participant')
    return hands


def state_text_v2(state, weapons, camera_side, body_profiles=None):
    from combat_action import describe_actor
    profiles = body_profiles or {b: {'identity_id': b} for b in state['actors']}
    if isinstance(profiles, list):
        profiles = {b['id']: b for b in profiles}
    names = {wid: w['name'] for wid, w in weapons.items()}
    hands = hand_items(state)
    actors = {}
    for body, data in state['actors'].items():
        identity = profiles[body]['identity_id']
        text = describe_actor(data | {'held_items': hands[body]}, names)
        text = f'{body}（{data["status"]}）：{text}'
        actors.setdefault(identity, []).append(text)
    environment = ['；'.join(f'{k}：{v}' for k, v in state['environment'].items())]
    # These are deterministic read projections; no caller-authored summaries.
    for field, label in (('items', '物件'), ('contacts', '接点'), ('effects', '效应'),
                         ('formations', '阵法'), ('pending_events', '未完事件'), ('hand_exceptions', '手部例外')):
        if state.get(field):
            environment.append(label + '：' + json.dumps(state[field], ensure_ascii=False, sort_keys=True, separators=(',', ':')))
    if state['active_abilities']:
        environment.append('维持能力：' + '、'.join(f'{a["ability_id"]}@{a["body_id"]}' for a in state['active_abilities']))
    return {a: ' | '.join(lines) for a, lines in actors.items()} | {
        'environment': '；'.join(environment), 'camera_side': camera_side}


def _participants(event):
    return ({event['actor_id'], event['target_id']} | set(event.get('participant_ids', []))) - {''}


def _validate_declarations(plan, profiles, weapons, abilities, schema):
    """Check every authored declaration, including callbacks later canceled.

    This deliberately does not test current possession, activation, lifecycle or
    previous entity phase: those are evaluated only when a transition executes.
    """
    check_schema(plan, schema)
    state = plan['action_initial_state']
    events = {e['id']: e for b in plan['beats'] for e in b.get('action_events', [])}
    namespaces = {domain: set(state.get(field, {})) for domain, field in DOMAINS.items()}
    for event in events.values():
        for op in event.get('state_ops', []):
            if op['operation'] == 'create':
                namespaces[op['domain']].add(op['id'])
    bodies, items = set(profiles), set(weapons)
    origins = set(events) | {p['source_event_id'] for p in state['pending_events'].values()}
    for aid, profile in abilities.items():
        if 'trigger_spec' in profile:
            trigger = profile['trigger_spec']
            if trigger['kind'] == 'held-item':
                require(trigger['source_item_id'] in items, f'{aid}: undeclared trigger source item')
            else:
                require(not trigger['source_item_id'], f'{aid}: independent trigger cannot bind a held-item source')

    def body(key, label, optional=False):
        require((optional and not key) or key in bodies, f'{label}: undeclared body reference {key}')

    def item(key, label, optional=False):
        require((optional and not key) or key in items, f'{label}: undeclared item reference {key}')

    def ability(key, label, owner=None, optional=False):
        require((optional and not key) or key in abilities, f'{label}: undeclared ability reference {key}')
        if key and owner:
            require(abilities[key]['owner'] == profiles[owner]['identity_id'], f'{label}: ability owner mismatch')

    def dependency(value, label):
        kind, colon, key = value.partition(':')
        require(colon and kind in ('ability', 'body', 'effect', 'formation', 'contact'), f'{label}: invalid dependency declaration')
        if kind == 'ability':
            aid, marker, bid = key.partition('@')
            require(marker and aid and bid, f'{label}: ability dependency needs ID@BODY')
            body(bid, label); ability(aid, label, bid)
        else:
            require(key in namespaces[kind], f'{label}: undeclared dependency {value}')

    for beat in plan['beats']:
        for event in beat.get('action_events', []):
            label = event['id']
            require(_participants(event) <= bodies, f'{label}: undeclared participant')
            item(event['weapon_id'], label, optional=True)
            for cid in event.get('contact_ids', []):
                require(cid in namespaces['contact'], f'{label}: undeclared contact ID')
            if event.get('continues'):
                require(event['continues'] in namespaces['pending'], f'{label}: undeclared pending ID')
            for interruption in event.get('interrupts', []):
                require(interruption['event_id'] in events and interruption['event_id'] != label,
                        f'{label}: interruption needs another declared event')
            use = event.get('ability_use')
            if use:
                ability(use['ability_id'], label, event['actor_id'])
                require(use['ability_id'] in beat['ability_ids'], f'{label}: ability missing from beat declaration')
                trigger = abilities[use['ability_id']].get('trigger_spec')
                if trigger and trigger['kind'] == 'held-item':
                    require(event['weapon_id'] == trigger['source_item_id'] and event.get('weapon_mode', 'held') == 'held',
                            f'{label}: held-item trigger must select the same held source item')
                require(not use['restrictions_added'] or bool(use['visible_cost'].strip()), f'{label}: cost needs visible expression')
            for op in event.get('state_ops', []):
                domain, key, value = op['domain'], op['id'], op['value']
                check_schema(value, schema['$defs'][DEFINITIONS[domain]], schema, f'{label}/{domain}/{key}')
                require(key in namespaces[domain], f'{label}: undeclared {domain} ID {key}')
                if domain == 'body':
                    body(key, label)
                elif domain == 'item':
                    item(key, label)
                    for holder in value['holders']:
                        body(holder['body_id'], label)
                    body(value['controller_id'], label, optional=True)
                    ability(value['control_ability_id'], label, value['controller_id'] or None, optional=True)
                elif domain == 'contact':
                    require(len(value['endpoints']) == 2, f'{label}: contact declaration must pair exactly two endpoints')
                    for endpoint in value['endpoints']:
                        body(endpoint['body_id'], label); item(endpoint['item_id'], label, optional=True)
                elif domain == 'effect':
                    body(value['owner_id'], label); body(value['controller_id'], label, optional=True)
                    ability(value['ability_id'], label, value['owner_id'], optional=True)
                    item(value['item_id'], label, optional=True)
                    for occupied in value.get('occupied_hands', []):
                        body(occupied['body_id'], label)
                    for dep in value['dependencies']:
                        dependency(dep, label)
                elif domain == 'formation':
                    body(value['owner_id'], label, optional=True)
                    kind, attached = value['attachment']['kind'], value['attachment']['id']
                    if kind == 'body': body(attached, label)
                    elif kind == 'item': item(attached, label)
                    elif kind == 'anchor': require(attached in state['environment'], f'{label}: undeclared attachment anchor')
                    else: require(not attached, f'{label}: world attachment cannot name another entity')
                    for dep in value['dependencies']:
                        dependency(dep, label)
                elif domain == 'pending':
                    body(value['actor_id'], label); body(value['target_id'], label, optional=True)
                    require(value['source_event_id'] in origins, f'{label}: undeclared pending source event')
                else:
                    body(value['body_id'], label)
                    require(set(value['item_ids']) <= items, f'{label}: undeclared exception items')
                    ability(value['ability_id'], label, value['body_id'], optional=True)


def _apply_operations(state, event, profiles, weapons, abilities, schema):
    participants = _participants(event)
    prior_effects = copy.deepcopy(state['effects'])
    changed = set()
    for op in event.get('state_ops', []):
        domain, key, operation = op['domain'], op['id'], op['operation']
        require((domain, key) not in changed, f'{event["id"]}: duplicate operation for entity')
        changed.add((domain, key))
        field = DOMAINS[domain]
        current = state.get(field, {}).get(key)
        if operation == 'create':
            require(current is None and domain not in ('item', 'body'), f'{key}: entity already exists or needs declaration')
        else:
            require(current is not None, f'{key}: unknown state entity')
        value = copy.deepcopy(op['value'])
        check_schema(value, schema['$defs'][DEFINITIONS[domain]], schema)
        if domain == 'body':
            require(key in participants, f'{key}: body operation participant missing')
            require(all(value[k] == current[k] for k in current if k != 'status'),
                    f'{key}: body operation only changes lifecycle; pose/cost uses state_delta')
            require(current['status'] != 'exited', f'{key}: exited body cannot silently return')
            require(operation != 'end' or value['status'] == 'exited', f'{key}: body end needs exited status')
        elif domain == 'item':
            old_holders = {(h['body_id'], h['hand']) for h in current['holders']}
            new_holders = {(h['body_id'], h['hand']) for h in value['holders']}
            require({b for b, _ in old_holders ^ new_holders} <= participants,
                    f'{key}: grip change participant missing')
            if not old_holders and new_holders:
                require(op.get('from_location') == current['location'], f'{key}: pickup needs matching source location')
            if current['controller_id'] != value['controller_id']:
                require(event['actor_id'] in {current['controller_id'], value['controller_id']} or
                        event['target_id'] == current['controller_id'], f'{key}: control transfer has no involving actor')
            require(current['status'] == 'active', f'{key}: terminal item cannot reappear')
            require(operation != 'end' or value['status'] != 'active', f'{key}: item end needs terminal status')
        elif domain == 'contact':
            people = {e['body_id'] for e in value['endpoints']}
            require(bool(people & participants), f'{key}: contact operation has no participant')
            if current:
                require(current['phase'] == 'active', f'{key}: released contact cannot reopen with same ID')
                old_pair = [(e['body_id'], e['item_id']) for e in current['endpoints']]
                new_pair = [(e['body_id'], e['item_id']) for e in value['endpoints']]
                require(sorted(new_pair) == sorted(old_pair), f'{key}: stable contact cannot replace body/item endpoints; end old pair and create new')
            if operation == 'end':
                require(value['phase'] == 'released', f'{key}: contact end needs released pair')
        elif domain in ('effect', 'formation'):
            owner = value['owner_id']
            require(not owner or owner in profiles, f'{key}: unknown state owner')
            if current:
                require(current['phase'] != 'ended', f'{key}: ended entity cannot reappear')
                require(owner == current['owner_id'], f'{key}: immutable state owner')
                require(not owner or owner in participants or current.get('controller_id') in participants,
                        f'{key}: state change has no involving body')
                if domain == 'formation':
                    require(set(value['nodes']) == set(current['nodes']), f'{key}: local node update cannot silently remove nodes')
            else:
                require(not owner or owner == event['actor_id'], f'{key}: creation owner must be acting body')
            require(operation != 'end' or value['phase'] == 'ended', f'{key}: end needs ended phase')
        elif domain == 'pending':
            require(value['actor_id'] in participants, f'{key}: pending event participant missing')
            if operation == 'create':
                require(value['source_event_id'] == event['id'], f'{key}: pending source event mismatch')
                require(value['phase'] == 'pending', f'{key}: new pending event cannot start completed')
                require(event.get('completion') == 'ongoing', f'{key}: new pending event needs ongoing completion declaration')
            else:
                require(current['phase'] == 'pending', f'{key}: completed pending ID cannot be reused')
                require(all(value[k] == current[k] for k in ('source_event_id', 'actor_id', 'target_id')),
                        f'{key}: pending source and participants are immutable')
            if operation == 'end' or value['phase'] == 'completed':
                require(value['phase'] == 'completed' and event.get('continues') == key,
                        f'{key}: completion must explicitly continue pending event')
        else:
            require(value['body_id'] in participants, f'{key}: hand exception needs involving body')
            if current:
                require(current['phase'] == 'active', f'{key}: ended hand exception cannot reopen')
                require((value['body_id'], value['hand']) == (current['body_id'], current['hand']),
                        f'{key}: hand exception cannot switch body/hand identity')
            require(operation != 'end' or value['phase'] == 'ended', f'{key}: exception end needs ended phase')
        state.setdefault(field, {})[key] = value
    for key, prior in prior_effects.items():
        if prior['phase'] == 'ended' or not any(not _dependency_active(state, dep) for dep in prior['dependencies']):
            continue
        expected = {'end': 'ended', 'fall': 'falling', 'freeze': 'frozen'}.get(prior['interruption'])
        if expected:
            require(state['effects'][key]['phase'] in (expected, 'ended'),
                    f'{key}: interruption must follow declared {prior["interruption"]} disposition')
    # All operations of one event form one atomic relation transition.
    validate_world(state, profiles, weapons, abilities, schema)


def _check_event_start(state, event, profiles, weapons, active_events, abilities):
    eid, body = event['id'], event['actor_id']
    require(_live(state, body), f'{eid}: acting body is not active')
    require(_participants(event) <= set(profiles), f'{eid}: unknown event participant')
    use = event.get('ability_use')
    trigger_kind = _trigger_kind(state, event, abilities[use['ability_id']]) if use else None
    if trigger_kind == 'held-item':
        wid = abilities[use['ability_id']].get('trigger_spec', {}).get('source_item_id', event['weapon_id'])
        item = state['items'][wid]
        require(event['hands_used'] and all({'body_id': body, 'hand': hand} in item['holders'] for hand in event['hands_used']),
                f'{eid}: held-item trigger needs the executing body actual grip of its source')
    restrictions = set(state['actors'][body]['constraints'])
    blocked = {}
    for cid, contact in state['contacts'].items():
        if contact['phase'] == 'active':
            for endpoint in contact['endpoints']:
                if endpoint['body_id'] == body:
                    for hand in endpoint['blocks']:
                        blocked.setdefault(hand, set()).add(cid)
    named_contacts = set(event.get('contact_ids', [])) | {op['id'] for op in event.get('state_ops', []) if op['domain'] == 'contact'}
    require(set(event.get('contact_ids', [])) <= set(state['contacts']), f'{eid}: unknown named contact')
    for hand in event['hands_used']:
        require(f'no_{hand}_hand' not in restrictions, f'{eid}: {hand} hand restricted')
        held = hand_items(state)[body][hand]
        if use and trigger_kind == 'independent' and held:
            require(_hand_exception(state, body, hand, held, casting=True),
                    f'{eid}: occupied casting hand needs explicit allows_casting permission')
        if hand in blocked:
            require(blocked[hand] <= named_contacts,
                    f'{eid}: hand has an active contact; name its maintained/changed pair')
        for effect_id, effect in state['effects'].items():
            if effect['phase'] == 'ended':
                continue
            occupied = {'body_id': body, 'hand': hand}
            if occupied in effect.get('occupied_hands', []):
                require(any(op['domain'] == 'effect' and op['id'] == effect_id for op in event.get('state_ops', [])) or
                        event.get('ability_use', {}).get('ability_id') == effect['ability_id'] or
                        _hand_exception(state, body, hand, hand_items(state)[body][hand], casting=True),
                        f'{eid}: hand maintains an active effect; explicit maintain/release mechanism needed')
    require(not ('no_running' in restrictions and event['movement'] == 'run'), f'{eid}: running restricted')
    for other in active_events.values():
        common_hand = body == other['actor_id'] and bool(set(event['hands_used']) & set(other['hands_used']))
        common_weapon = bool(event['weapon_id']) and event['weapon_id'] == other['weapon_id']
        if common_hand or common_weapon:
            group, prior = event.get('concurrency'), other.get('concurrency')
            require(group and prior and group['group'] == prior['group'] and group['basis'] == prior['basis'],
                    f'{eid}: conflicting concurrent hand/weapon use needs shared explicit mechanism')
    wid = event['weapon_id']
    if wid:
        require(wid in weapons and state['items'][wid]['status'] == 'active', f'{eid}: unknown/inactive weapon')
        mode = event.get('weapon_mode', 'held')
        item = state['items'][wid]
        if mode == 'held':
            if weapons[wid]['mount'] == 'mounted':
                require(weapons[wid]['owner_id'] == profiles[body]['identity_id'], f'{eid}: wrong mounted weapon owner')
            else:
                require(any(h['body_id'] == body and h['hand'] in event['hands_used'] for h in item['holders']),
                        f'{eid}: weapon not held by declared hand')
        elif mode == 'remote':
            require(item['control_mode'] == 'remote' and item['controller_id'] == body, f'{eid}: remote control not established')
        else:
            require(item['control_mode'] == 'autonomous' and not event['hands_used'], f'{eid}: autonomous use not established')
    if event.get('continues'):
        pending = state['pending_events'].get(event['continues'])
        require(pending and pending['phase'] == 'pending', f'{eid}: unknown/completed pending event')
        require(pending['actor_id'] == body and pending['target_id'] == event['target_id'], f'{eid}: pending participant changed')


def validate_state_plan(plan):
    require(plan['schema_version'] == '1.3', 'combat-action-state/2 requires Combat Plan 1.3')
    require('weapon_profiles' in plan, 'state contract needs weapon profiles')
    schema = json.loads((Path(__file__).resolve().parents[1] / 'assets/combat-plan.schema.json').read_text(encoding='utf-8'))
    profiles = profiles_for(plan)
    weapons = {w['id']: w for w in plan['weapon_profiles']}
    require(len(weapons) == len(plan['weapon_profiles']), 'duplicate weapon IDs')
    identities = {a['id'] for a in plan['cast']}
    require(all(w['owner_id'] in identities for w in weapons.values()), 'unknown weapon owner identity')
    abilities = {a['id']: a for a in plan['abilities']}
    state = copy.deepcopy(plan['action_initial_state'])
    validate_world(state, profiles, weapons, abilities, schema)
    _validate_declarations(plan, profiles, weapons, abilities, schema)
    camera_side = plan['initial_state']['camera_side']
    require(plan['initial_state'] == state_text_v2(state, weapons, camera_side, profiles), 'initial_state must be derived from structured state')
    seen, snapshots = {}, []
    for beat in plan['beats']:
        label = beat['id']
        require('action_events' in beat and 'state_delta' in beat, f'{label}: action contract missing')
        before = copy.deepcopy(state)
        require(beat['before'] == state_text_v2(state, weapons, camera_side, profiles), f'{label}: before differs from structured state')
        local, ticks = {}, []
        previous_start = beat['start']
        for index, event in enumerate(beat['action_events']):
            eid = event['id']
            require(eid not in seen, f'{eid}: duplicate event')
            require(beat['start'] <= event['start'] < event['end'] <= beat['end'], f'{eid}: event outside beat')
            require(event['start'] >= previous_start, f'{eid}: event order')
            parent = event['response_to']
            if parent:
                require(parent in seen and seen[parent]['start'] <= event['start'], f'{eid}: response must name earlier event')
            require(not event['transfers'], f'{eid}: v2 possession uses item state_ops, not legacy transfers')
            seen[eid] = local[eid] = event
            previous_start = event['start']
            ticks.extend(((event['start'], 1, index, event), (event['end'], 0, index, event)))
        active_events = {}
        interrupted_events = {}
        effective_ability_triggers = {}
        endpoint_writes = set()
        for _, ending, _, event in sorted(ticks, key=lambda tick: tick[:3]):
            if ending:
                _check_event_start(state, event, profiles, weapons, active_events, abilities)
                active_events[event['id']] = event
                continue
            if event['id'] in interrupted_events:
                continue  # Planned later endpoint has no live action or callbacks after explicit interruption.
            for interruption in event.get('interrupts', []):
                victim = active_events.get(interruption['event_id'])
                require(victim is not None and victim['id'] != event['id'], 'interruption must name another currently running event')
                require(victim['actor_id'] in _participants(event), 'interruption needs the affected body as participant')
                active_events.pop(victim['id'])
                interrupted_events[victim['id']] = {'time': event['end'], 'caused_by': event['id'], 'reason': interruption['reason']}
            for op in event.get('state_ops', []):
                key = (event['end'], op['domain'], op['id'])
                require(key not in endpoint_writes, f'{event["id"]}: same-time entity writes need one authoritative operation')
                endpoint_writes.add(key)
            use = event.get('ability_use')
            if use:
                aid, phase = use['ability_id'], use['phase']
                kind = _trigger_kind(state, event, abilities[aid])
                effective_ability_triggers[event['id']] = {
                    'kind': kind, 'source_item_id': abilities[aid].get('trigger_spec', {}).get('source_item_id', event['weapon_id']) if kind == 'held-item' else '',
                    'basis': 'declared' if 'trigger_spec' in abilities[aid] else 'legacy-held-device' if kind == 'held-item' else 'independent-default'}
                activation = {'ability_id': aid, 'body_id': event['actor_id']}
                require(aid in abilities and abilities[aid]['owner'] == profiles[event['actor_id']]['identity_id'],
                        f'{event["id"]}: invalid ability owner')
                require(aid in beat['ability_ids'], f'{event["id"]}: ability missing from beat')
                if phase == 'activate':
                    require(activation not in state['active_abilities'], f'{aid}: ability already active on body')
                    state['active_abilities'].append(activation)
                else:
                    require(activation in state['active_abilities'], f'{aid}: ability not active on body')
                if phase in ('consume', 'end'):
                    state['active_abilities'].remove(activation)
                require(not use['restrictions_added'] or bool(use['visible_cost'].strip()), 'cost needs visible expression')
                constraints = state['actors'][event['actor_id']]['constraints']
                constraints.extend(c for c in use['restrictions_added'] if c not in constraints)
            _apply_operations(state, event, profiles, weapons, abilities, schema)
            if event.get('completion') == 'ongoing':
                carried = state['pending_events'].get(event.get('continues'))
                ongoing = carried is not None and carried['phase'] == 'pending' if event.get('continues') else any(
                    p['source_event_id'] == event['id'] and p['phase'] == 'pending' for p in state['pending_events'].values())
                require(ongoing,
                        f'{event["id"]}: ongoing event needs pending trajectory/contact/next threat')
            if event.get('continues') and event.get('completion', 'complete') == 'complete':
                require(state['pending_events'][event['continues']]['phase'] == 'completed', f'{event["id"]}: completed event still pending')
            active_events.pop(event['id'])
            # Relations can change while another event is running. Recheck the
            # live interval after each transition, not only at its first frame.
            for running in active_events.values():
                if running['end'] <= event['end']:
                    continue  # No open interval remains for another event ending at this exact boundary.
                _check_event_start(state, running, profiles, weapons,
                                   {key: other for key, other in active_events.items() if key != running['id']}, abilities)
        delta = beat['state_delta']
        require(set(delta['actors']) <= set(profiles), f'{label}: unknown delta body')
        require(set(delta['environment']) <= set(state['environment']), f'{label}: undeclared environment anchor')
        require(set(delta['caused_by']) <= set(local), f'{label}: delta needs local evidence')
        if delta['actors'] or delta['environment']:
            require(bool(delta['caused_by']), f'{label}: unexplained state change')
        for body, patch in delta['actors'].items():
            require(any(body in _participants(local[eid]) for eid in delta['caused_by']), f'{body}: delta has no involving event')
            require(not ({'held_items', 'status'} & set(patch)), f'{body}: possession/lifecycle uses state_ops only')
            for field in ('damage', 'constraints'):
                if field in patch:
                    require(set(state['actors'][body][field]) <= set(patch[field]), f'{body}: {field} silently reset')
            state['actors'][body].update(copy.deepcopy(patch))
        state['environment'].update(delta['environment'])
        validate_world(state, profiles, weapons, abilities, schema)
        camera_side = beat['camera']['side']
        require(beat['after'] == state_text_v2(state, weapons, camera_side, profiles), f'{label}: after differs from structured state')
        snapshots.append({'beat_id': label, 'before': before, 'after': copy.deepcopy(state),
                          'active_abilities': sorted(state['active_abilities'], key=lambda a: (a['ability_id'], a['body_id'])),
                          'interrupted_events': interrupted_events,
                          'effective_ability_triggers': effective_ability_triggers})
    return snapshots


def describe_operation(op, weapons):
    label = {'body': '身体状态', 'item': '物件状态', 'contact': '成对接点', 'effect': '术法/在途攻击',
             'formation': '阵法', 'pending': '未完事件', 'hand_exception': '手部例外'}[op['domain']]
    name = weapons.get(op['id'], {}).get('name', op['id'])
    value = op['value']
    if op['domain'] == 'item':
        holders = '、'.join(f'{h["body_id"]}{"左" if h["hand"] == "left" else "右"}手' for h in value['holders'])
        details = (f'由{holders}持握' if holders else f'位于{value["location"]}')
        details += f'，控制方式{value["control_mode"]}，控制者{value["controller_id"] or "无"}，物件{value["status"]}'
    elif op['domain'] == 'contact':
        details = '与'.join(f'{e["body_id"]}的{e["part"]}' for e in value['endpoints']) + f'的接点{value["phase"]}'
    elif op['domain'] == 'effect':
        details = f'{value["phase"]}，位于{value["location"]}，沿{value["trajectory"]}，后续威胁{value["next_threat"] or "无"}'
    elif op['domain'] == 'formation':
        details = f'附着{value["attachment"]["kind"]}:{value["attachment"]["id"] or value["attachment"]["position"]}，朝向{value["orientation"]}，范围{value["range"]}，状态{value["phase"]}'
        details += '；节点' + '、'.join(f'{key}在{node["location"]}{node["phase"]}' for key, node in value['nodes'].items())
    elif op['domain'] == 'pending':
        details = f'{value["phase"]}，沿{value["trajectory"]}，接点{value["contact"]}，下一威胁{value["next_threat"]}'
    elif op['domain'] == 'hand_exception':
        details = f'{value["body_id"]}{value["hand"]}手，允许物件' + '、'.join(value['item_ids']) + f'，依据{value["basis"]}，状态{value["phase"]}'
    else:
        details = value['status']
    return f'{label}{name}：{op["reason"]}；{details}。'
