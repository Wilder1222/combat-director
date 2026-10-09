"""Synthetic relational scenarios; none are observed media/physics evidence."""
import copy
import importlib.util
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
SKILL = ROOT / 'skills/combat-director'
spec = importlib.util.spec_from_file_location('xianxia_contract_tool', SKILL / 'scripts/combat_tool.py')
tool = importlib.util.module_from_spec(spec)
spec.loader.exec_module(tool)
from combat_action import state_text
from combat_state import validate_state_plan


def item(holders=(), location='', controller='', mode='none', ability='', basis=''):
    return {'holders': [{'body_id': b, 'hand': h} for b, h in holders], 'location': location,
            'controller_id': controller, 'control_mode': mode, 'control_ability_id': ability,
            'control_basis': basis, 'status': 'active'}


def operation(domain, key, value, action='update', **extra):
    return {'domain': domain, 'id': key, 'operation': action, 'value': copy.deepcopy(value),
            'reason': 'Synthetic explicitly modeled transition, not footage evidence.', **extra}


def event(key, start, end, actor='A', target='B', hands=(), weapon='', operations=(), **extra):
    return {'id': key, 'start': start, 'end': end, 'actor_id': actor, 'target_id': target,
            'response_to': '', 'hands_used': list(hands), 'weapon_id': weapon, 'movement': 'stationary',
            'action': 'Maintain visible causal exchange.', 'trajectory': {
                'start': 'south', 'path': 'east lane', 'end': 'north', 'screen_direction': 'rightward'},
            'contact': 'Explicit contact or separation.', 'outcome': 'Use modeled resulting relation.',
            'transfers': [], 'state_ops': list(operations), **extra}


def ability(key='Q', owner='A'):
    return {'id': key, 'owner': owner, 'trigger': 'declared trigger', 'limit': 'declared limitation',
            'cost': 'declared cost', 'end_condition': 'explicit stop', 'visual': 'visible route',
            'scale': 'person', 'supernatural': True}


def contact(a, apart, b, bpart, ablocks=(), bblocks=()):
    return {'endpoints': [{'body_id': a, 'part': apart, 'item_id': '', 'blocks': list(ablocks)},
                          {'body_id': b, 'part': bpart, 'item_id': '', 'blocks': list(bblocks)}],
            'phase': 'active', 'mechanism': 'maintained grip', 'release_condition': 'visible grip release'}


def effect(kind='projectile', phase='in_flight', dependencies=(), controller=''):
    return {'kind': kind, 'owner_id': 'A', 'controller_id': controller, 'ability_id': 'Q',
            'item_id': '', 'dependencies': list(dependencies), 'interruption': 'persist' if kind == 'projectile' else 'end',
            'phase': phase, 'location': 'east lane', 'trajectory': 'continues rightward', 'next_threat': 'B must evade'}


def pending(source='E1'):
    return {'actor_id': 'A', 'target_id': 'B', 'source_event_id': source, 'phase': 'pending',
            'trajectory': 'east lane rightward', 'contact': 'not yet reached target', 'next_threat': 'arriving arrow'}


def make_plan(events=None, modify=None, expected=None):
    plan = tool.read_json(ROOT / 'tests/fixtures/action-transfer.plan.json')
    plan['schema_version'] = '1.3'
    plan['editorial_reviews'] = {}
    state = plan['action_initial_state']
    for actor in state['actors'].values():
        actor.pop('held_items')
        actor['status'] = 'active'
    state.update(format='combat-action-state/2', items={
        'STAFF': item([('A', 'right')], controller='A', mode='held'),
        'LETTER': item([('B', 'right')], controller='B', mode='held')},
        contacts={}, effects={}, formations={}, pending_events={}, active_abilities=[])
    plan['rules']['fantasy'] = True
    if modify:
        modify(plan)
    beat = plan['beats'][0]
    beat.update(start=0, end=plan['duration'], action_events=events or [event('IDLE', 0, 1)],
                state_delta={'actors': {}, 'environment': {}, 'caused_by': []})
    plan['beats'] = [beat]
    section = plan['sections'][0]
    section['beat_ids'] = [beat['id']]
    plan['sections'] = [section]
    profiles = plan.get('body_profiles')
    weapons = {w['id']: w for w in plan['weapon_profiles']}
    plan['initial_state'] = state_text(state, weapons, plan['initial_state']['camera_side'], profiles)
    beat['before'] = copy.deepcopy(plan['initial_state'])
    finish = expected if expected is not None else state
    beat['after'] = state_text(finish, weapons, beat['camera']['side'], profiles)
    beat['ability_ids'] = [a['id'] for a in plan['abilities']]
    return plan


def expected_from(plan, events):
    state = copy.deepcopy(plan['action_initial_state'])
    for action in sorted(events, key=lambda e: e['end']):
        for op in action['state_ops']:
            field = {'item': 'items', 'body': 'actors', 'contact': 'contacts', 'effect': 'effects',
                     'formation': 'formations', 'pending': 'pending_events'}[op['domain']]
            state[field][op['id']] = copy.deepcopy(op['value'])
        use = action.get('ability_use')
        if use and use['phase'] == 'end':
            state['active_abilities'].remove({'ability_id': use['ability_id'], 'body_id': action['actor_id']})
    plan['beats'][0]['after'] = state_text(state, {w['id']: w for w in plan['weapon_profiles']},
                                         plan['beats'][0]['camera']['side'], plan.get('body_profiles'))
    return state


class XianxiaContractTests(unittest.TestCase):
    def assert_valid(self, plan):
        tool.validate(plan, require_review=False)

    def test_ground_pickup_shared_grip_partial_release_is_one_item(self):
        dropped = item(location='south floor')
        picked = item([('B', 'left')], controller='B', mode='held')
        shared = item([('B', 'left'), ('A', 'right')], controller='B', mode='held')
        released = item([('A', 'right')], controller='A', mode='held')
        events = [event('DROP', 0, 1, operations=[operation('item', 'STAFF', dropped)]),
                  event('PICK', 1, 2, actor='B', target='A', hands=['left'],
                        operations=[operation('item', 'STAFF', picked, from_location='south floor')]),
                  event('SHARE', 2, 3, operations=[operation('item', 'STAFF', shared)]),
                  event('RELEASE', 3, 4, actor='B', target='A', operations=[operation('item', 'STAFF', released)])]
        p = make_plan(events)
        expected = expected_from(p, events)
        self.assert_valid(p)
        self.assertEqual(validate_state_plan(p)[0]['after'], expected)
        self.assertEqual(len(expected['items']), 2)
        bad = copy.deepcopy(p)
        bad['beats'][0]['action_events'][1]['state_ops'][0]['from_location'] = 'wrong floor'
        with self.assertRaisesRegex(ValueError, 'source location'):
            self.assert_valid(bad)
        bad = copy.deepcopy(p)
        bad['beats'][0]['action_events'][1]['state_ops'][0]['value']['holders'][0]['hand'] = 'right'
        with self.assertRaisesRegex(ValueError, 'already holds'):
            self.assert_valid(bad)

    def test_held_possession_does_not_grant_remote_control(self):
        def change(p):
            p['abilities'] = [ability()]
            p['action_initial_state']['active_abilities'] = [{'ability_id': 'Q', 'body_id': 'A'}]
            p['action_initial_state']['items']['STAFF'] = item([('B', 'left')], controller='A', mode='remote',
                                                              ability='Q', basis='Bound original owner can turn the captured sword.')
        e = event('REMOTE', 0, 1, weapon='STAFF', weapon_mode='remote')
        p = make_plan([e], change)
        self.assert_valid(p)
        bad = copy.deepcopy(p)
        bad['beats'][0]['action_events'][0]['actor_id'] = 'B'
        with self.assertRaisesRegex(ValueError, 'remote control'):
            self.assert_valid(bad)
        bad = copy.deepcopy(p)
        bad['action_initial_state']['items']['STAFF']['control_basis'] = ''
        with self.assertRaisesRegex(ValueError, 'explicit basis'):
            self.assert_valid(bad)

    def test_simultaneous_two_hands_and_explicit_shared_use(self):
        events = [event('RIGHT', 0, 2, hands=['right'], weapon='STAFF'),
                  event('LEFT', 0, 2, hands=['left'])]
        p = make_plan(events)
        self.assert_valid(p)
        p['beats'][0]['action_events'][1]['hands_used'] = ['right']
        with self.assertRaisesRegex(ValueError, 'conflicting concurrent'):
            self.assert_valid(p)
        for e in p['beats'][0]['action_events']:
            e['concurrency'] = {'group': 'one-combined-action', 'basis': 'Established finger casting while holding staff.'}
        self.assert_valid(p)
        p['beats'][0]['action_events'][1]['concurrency']['basis'] = 'Different incompatible mechanism'
        with self.assertRaisesRegex(ValueError, 'conflicting concurrent'):
            self.assert_valid(p)

    def test_third_party_releases_one_pair_only(self):
        def change(p):
            p['cast'].append({'id': 'C', 'description': 'third participant', 'goal': 'break wrist grip', 'prop': 'none', 'hand': 'none'})
            p['action_initial_state']['actors']['C'] = copy.deepcopy(p['action_initial_state']['actors']['B'])
            p['beats'][0]['actors']['C'] = {'action': 'Break the wrist grip.', 'performance': 'Focused.'}
            p['action_initial_state']['contacts'] = {
                'WRIST': contact('A', 'right hand', 'B', 'left wrist', ['right'], ['left']),
                'OTHER': contact('A', 'left forearm', 'B', 'right hand', ['left'], ['right'])}
        p = make_plan(modify=change)
        released = copy.deepcopy(p['action_initial_state']['contacts']['WRIST'])
        released['phase'] = 'released'
        events = [event('BREAK', 0, 1, actor='C', target='A', participant_ids=['B'], operations=[operation('contact', 'WRIST', released, 'end')]),
                  event('RESUME', 1, 2, hands=['right'])]
        p['beats'][0]['action_events'] = events
        end = expected_from(p, events)
        self.assert_valid(p)
        self.assertEqual(end['contacts']['OTHER']['phase'], 'active')
        p['beats'][0]['action_events'][1]['hands_used'] = ['left']
        with self.assertRaisesRegex(ValueError, 'active contact'):
            self.assert_valid(p)

    def test_clone_exit_preserves_real_dropped_item_and_identity_count(self):
        def change(p):
            p['body_profiles'] = [
                {'id': 'A', 'identity_id': 'A', 'kind': 'original', 'can_interact': True, 'source': 'original'},
                {'id': 'SHADOW', 'identity_id': 'A', 'kind': 'clone', 'can_interact': True, 'source': 'separate interactive body'},
                {'id': 'B', 'identity_id': 'B', 'kind': 'original', 'can_interact': True, 'source': 'original'}]
            p['action_initial_state']['actors']['SHADOW'] = copy.deepcopy(p['action_initial_state']['actors']['A'])
            p['action_initial_state']['actors']['SHADOW']['status'] = 'inactive'
        p = make_plan(modify=change)
        active = copy.deepcopy(p['action_initial_state']['actors']['SHADOW']); active['status'] = 'active'
        exited = active | {'status': 'exited'}
        events = [event('SPAWN', 0, 1, participant_ids=['SHADOW'], operations=[operation('body', 'SHADOW', active)]),
                  event('HANDOVER', 1, 2, target='SHADOW', operations=[operation('item', 'STAFF', item([('SHADOW', 'right')], controller='SHADOW', mode='held'))]),
                  event('EXIT', 2, 3, actor='SHADOW', target='A', operations=[
                      operation('item', 'STAFF', item(location='north floor')),
                      operation('body', 'SHADOW', exited, 'end')])]
        p['beats'][0]['action_events'] = events
        end = expected_from(p, events)
        self.assert_valid(p)
        self.assertIn('SHADOW（exited）', p['beats'][0]['after']['A'])
        self.assertEqual(end['items']['STAFF']['location'], 'north floor')
        bad = copy.deepcopy(p)
        bad['beats'][0]['action_events'][2]['state_ops'].pop(0)
        with self.assertRaisesRegex(ValueError, 'holder cannot interact'):
            self.assert_valid(bad)

    def test_stop_supply_preserves_independent_arrow_and_disposes_dependent_shield(self):
        def change(p):
            p['abilities'] = [ability()]
            p['action_initial_state']['active_abilities'] = [{'ability_id': 'Q', 'body_id': 'A'}]
            p['action_initial_state']['effects'] = {
                'ARROW': effect(), 'SHIELD': effect('sustained', 'active', ['ability:Q@A'], 'A')}
        p = make_plan(modify=change)
        ended = copy.deepcopy(p['action_initial_state']['effects']['SHIELD']); ended['phase'] = 'ended'
        e = event('STOP', 0, 1, operations=[operation('effect', 'SHIELD', ended, 'end')],
                  ability_use={'ability_id': 'Q', 'phase': 'end', 'visible_cost': '', 'restrictions_added': []})
        p['beats'][0]['action_events'] = [e]
        end = expected_from(p, [e])
        self.assert_valid(p)
        self.assertEqual(end['effects']['ARROW']['phase'], 'in_flight')
        bad = copy.deepcopy(p)
        bad['beats'][0]['action_events'][0]['state_ops'] = []
        with self.assertRaisesRegex(ValueError, 'interruption|interrupted dependency'):
            self.assert_valid(bad)

    def test_formation_moves_with_attachment_and_only_local_node_breaks(self):
        def change(p):
            p['action_initial_state']['formations']['BOAT'] = {
                'owner_id': '', 'attachment': {'kind': 'item', 'id': 'LETTER', 'position': 'front deck'},
                'orientation': 'east', 'shape': 'ring', 'range': 'deck perimeter', 'function': 'blocks boarding',
                'maintenance': 'preset autonomous formation', 'dependencies': [], 'phase': 'active', 'nodes': {
                    'WEST': {'location': 'stern', 'phase': 'active', 'function': 'blocks rear'},
                    'EAST': {'location': 'bow', 'phase': 'active', 'function': 'blocks front'}}}
        p = make_plan(modify=change)
        partial = copy.deepcopy(p['action_initial_state']['formations']['BOAT'])
        partial['phase'] = 'partial'; partial['orientation'] = 'north'
        partial['nodes']['WEST']['phase'] = 'broken'
        e = event('LOCAL_BREAK', 0, 1, operations=[operation('formation', 'BOAT', partial)])
        p['beats'][0]['action_events'] = [e]
        end = expected_from(p, [e])
        self.assert_valid(p)
        self.assertEqual(end['formations']['BOAT']['nodes']['EAST']['phase'], 'active')
        bad = copy.deepcopy(p)
        bad['beats'][0]['action_events'][0]['state_ops'][0]['value']['nodes'].pop('EAST')
        with self.assertRaisesRegex(ValueError, 'silently remove nodes'):
            self.assert_valid(bad)

    def test_ongoing_event_carries_to_observed_continuation_not_plan_ending(self):
        e = event('FLIGHT', 0, 1, completion='ongoing', operations=[operation('pending', 'P1', pending('FLIGHT'), 'create')])
        p = make_plan([e]); expected_from(p, [e]); self.assert_valid(p)
        schema = tool.read_json(SKILL / 'assets/take-review.schema.json')
        review = tool.review_template(p, 'synthetic-2')
        self.assertIsNone(review['observed_action_state'])
        tool.validate_take(review, p, schema)
        review['media'].update(evidence_kind='synthetic', observation_method='frames', location='synthetic://endpoint')
        observed = copy.deepcopy(p['action_initial_state'])
        observed['pending_events']['P1'] = pending('FLIGHT')
        observed['pending_events']['P1']['trajectory'] = 'observed lower east lane'
        review.update(observed_action_state=observed, action_state_evidence='Synthetic endpoint differs from intended lane.',
                      observed_end_state=state_text(observed, {w['id']: w for w in p['weapon_profiles']}, p['beats'][0]['camera']['side']),
                      state_evidence='Synthetic observed endpoint.', decision='accept_with_deviation', decision_by='synthetic',
                      decision_reason='carry lower lane', incomplete_events=['FLIGHT'], deviations=[{
                          'time': 1, 'observation': 'lower lane', 'impact': 'next threat lower', 'repair': 'continue lower'}])
        seed = tool.continuation_seed(review, p, schema)
        self.assertEqual(seed['action_initial_state'], observed)
        contradiction = copy.deepcopy(review)
        contradiction['incomplete_events'] = []
        contradiction['completed_events'] = ['FLIGHT']
        with self.assertRaisesRegex(ValueError, 'contradicts observed pending'):
            tool.validate_take(contradiction, p, schema)
        next_plan = copy.deepcopy(p)
        next_plan['initial_state'] = seed['initial_state']
        with self.assertRaisesRegex(ValueError, 'observed items'):
            tool.check_continuation(next_plan, review, p, schema)
        next_plan['action_initial_state'] = copy.deepcopy(observed)
        tool.check_continuation(next_plan, review, p, schema)
        continuation = pending('FLIGHT') | {'phase': 'completed', 'trajectory': 'observed lower east lane'}
        next_events = [event('ARRIVE', 0, 1, continues='P1', operations=[operation('pending', 'P1', continuation, 'end')])]
        next_plan['beats'][0]['before'] = copy.deepcopy(next_plan['initial_state'])
        next_plan['beats'][0]['action_events'] = next_events
        expected_from(next_plan, next_events)
        self.assert_valid(next_plan)

    def test_new_state_changes_invalidate_fact_and_expression_review(self):
        p = make_plan()
        receipt = {'plan_id': p['id'], 'reviews': [{k: scope[k] for k in ('scope', 'input_digest', 'expression_digest')} | {
            'reviewer': 'synthetic', 'method': 'agent', 'checks': {key: 'Synthetic check only.' for key in
                ('identity_action', 'camera_timing', 'ability_cost', 'continuity')}} for scope in tool.compile_handoff(p)['scopes']]}
        p = tool.apply_review(p, receipt)
        self.assertEqual({x['status'] for x in tool.readiness(p)}, {'ready'})
        p['action_initial_state']['items']['STAFF']['control_basis'] = 'new mechanism'
        self.assertEqual({x['status'] for x in tool.readiness(p)}, {'stale'})

    def test_legacy_migration_never_invents_observation_or_new_state(self):
        old = tool.read_json(ROOT / 'tests/fixtures/action-transfer.plan.json')
        migrated = tool.migrate(old)
        self.assertEqual(migrated['schema_version'], '1.3')
        self.assertEqual(migrated['action_initial_state'], old['action_initial_state'])
        self.assertEqual(migrated['editorial_reviews'], {})
        self.assert_valid(migrated)
        migrated['beats'][0]['action_events'][0]['state_ops'] = []
        with self.assertRaisesRegex(ValueError, 'extended event fields'):
            self.assert_valid(migrated)

    def test_same_time_writes_cannot_overwrite_another_transfer(self):
        events = [event('ONE', 0, 1, operations=[operation('item', 'STAFF', item(location='east'))]),
                  event('TWO', 0, 1, operations=[operation('item', 'STAFF', item(location='west'))])]
        p = make_plan(events); expected_from(p, events)
        with self.assertRaisesRegex(ValueError, 'one authoritative operation'):
            self.assert_valid(p)

    def test_effect_hand_maintenance_and_autonomous_exception(self):
        def change(p):
            p['abilities'] = [ability()]
            shield = effect('sustained', 'active', controller='A')
            shield['occupied_hands'] = [{'body_id': 'A', 'hand': 'left'}]
            p['action_initial_state']['effects']['SHIELD'] = shield
        p = make_plan([event('CATCH', 0, 1, hands=['left'])], change)
        with self.assertRaisesRegex(ValueError, 'hand maintains'):
            self.assert_valid(p)
        p['action_initial_state']['effects']['SHIELD']['occupied_hands'] = []
        p['action_initial_state']['effects']['SHIELD']['kind'] = 'autonomous'
        p['initial_state'] = state_text(p['action_initial_state'], {w['id']: w for w in p['weapon_profiles']}, p['initial_state']['camera_side'])
        p['beats'][0]['before'] = copy.deepcopy(p['initial_state'])
        p['beats'][0]['after'] = copy.deepcopy(p['initial_state'])
        self.assert_valid(p)

    def test_same_identity_bodies_keep_independent_ability_activations(self):
        def change(p):
            p['abilities'] = [ability()]
            p['body_profiles'] = [
                {'id': 'A', 'identity_id': 'A', 'kind': 'original', 'can_interact': True, 'source': 'original'},
                {'id': 'SHADOW', 'identity_id': 'A', 'kind': 'clone', 'can_interact': True, 'source': 'independent casting body'},
                {'id': 'B', 'identity_id': 'B', 'kind': 'original', 'can_interact': True, 'source': 'original'}]
            p['action_initial_state']['actors']['SHADOW'] = copy.deepcopy(p['action_initial_state']['actors']['A'])
            p['action_initial_state']['active_abilities'] = [{'ability_id': 'Q', 'body_id': 'A'}, {'ability_id': 'Q', 'body_id': 'SHADOW'}]
            p['action_initial_state']['effects']['CLONE_SHIELD'] = effect('sustained', 'active', ['ability:Q@SHADOW'], 'SHADOW')
            p['action_initial_state']['effects']['CLONE_SHIELD']['owner_id'] = 'SHADOW'
        p = make_plan(modify=change)
        e = event('STOP_ORIGINAL', 0, 1, ability_use={'ability_id': 'Q', 'phase': 'end', 'visible_cost': '', 'restrictions_added': []})
        p['beats'][0]['action_events'] = [e]
        end = expected_from(p, [e])
        self.assert_valid(p)
        self.assertEqual(end['active_abilities'], [{'ability_id': 'Q', 'body_id': 'SHADOW'}])
        self.assertEqual(end['effects']['CLONE_SHIELD']['phase'], 'active')

    def test_observed_unknown_never_becomes_planned_structured_ending(self):
        p = make_plan()
        schema = tool.read_json(SKILL / 'assets/take-review.schema.json')
        review = tool.review_template(p, 'synthetic-unknown')
        review['media'].update(evidence_kind='synthetic', observation_method='frames', location='synthetic://occluded')
        review.update(state_evidence='Occluded synthetic endpoint; state unknown.', decision='accept',
                      decision_by='synthetic', decision_reason='accepted unknown endpoint')
        seed = tool.continuation_seed(review, p, schema)
        self.assertIsNone(seed['action_initial_state'])
        next_plan = copy.deepcopy(p); next_plan['initial_state'] = seed['initial_state']
        with self.assertRaisesRegex(ValueError, 'observation unknown'):
            tool.check_continuation(next_plan, review, p, schema)

    def test_schema_combinators_and_revision_gate(self):
        one = {'oneOf': [{'type': 'integer'}, {'type': 'number'}]}
        with self.assertRaisesRegex(ValueError, 'oneOf'):
            tool.check_schema(1, one)
        tool.check_schema('a', {'allOf': [{'type': 'string'}, {'minLength': 1}]})
        with self.assertRaisesRegex(ValueError, 'allOf'):
            tool.check_schema('', {'allOf': [{'type': 'string'}, {'minLength': 1}]})
        p = make_plan(); p['schema_version'] = '1.2'
        with self.assertRaisesRegex(ValueError, 'requires Combat Plan 1.3'):
            self.assert_valid(p)


if __name__ == '__main__':
    unittest.main()
