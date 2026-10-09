"""Original independent counterexamples plus bounded, explicitly repaired variants."""
import copy
import hashlib
import json
import unittest
from pathlib import Path

from test_xianxia_contract import tool, item, operation, event, ability, effect, make_plan, expected_from
from combat_action import state_text, action_text
from combat_state import validate_state_plan

FIXTURES = Path(__file__).resolve().parent / 'fixtures/state-audit'


def projection(plan, state):
    return state_text(state, {w['id']: w for w in plan['weapon_profiles']},
                      plan['beats'][0]['camera']['side'], plan.get('body_profiles'))


def grip(body='A', hand='right', items=('STAFF', 'LETTER'), kind='grip', casting=False, aid=''):
    return {'body_id': body, 'hand': hand, 'item_ids': list(items), 'kind': kind, 'ability_id': aid,
            'allows_casting': casting, 'phase': 'active', 'basis': 'Explicit two-hilt/finger grip from current setting.'}


class IndependentStateRegressionTests(unittest.TestCase):
    def plan(self, name):
        return tool.read_json(FIXTURES / (name + '.plan.json'))

    def valid(self, plan):
        return tool.validate(plan, require_review=False)

    def test_original_eight_inputs_match_independent_expectations_unchanged(self):
        manifest = tool.read_json(FIXTURES / 'cases.json')
        self.assertEqual(len(manifest['cases']), 8)
        for case in manifest['cases']:
            with self.subTest(case=case['id']):
                path = FIXTURES / case['file']
                self.assertEqual(hashlib.sha256(path.read_bytes()).hexdigest(), case['sha256'])
                plan = tool.read_json(path)
                if case['expected'] == 'accepted':
                    self.valid(plan)
                else:
                    with self.assertRaises(ValueError):
                        self.valid(plan)

    def test_remote_stop_releases_control_but_preserves_physical_item(self):
        p = self.plan('remote_item_after_control_ability_end')
        free = copy.deepcopy(p['action_initial_state']['items']['S'])
        free.update(controller_id='', control_mode='none', control_ability_id='', control_basis='')
        p['beats'][0]['action_events'][0]['state_ops'] = [operation('item', 'S', free)]
        p['beats'][0]['action_events'] = p['beats'][0]['action_events'][:1]
        final = copy.deepcopy(p['action_initial_state']); final['items']['S'] = free; final['active_abilities'] = []
        p['beats'][0]['after'] = projection(p, final)
        self.valid(p)
        state = validate_state_plan(p)[0]['after']
        self.assertEqual(state['items']['S']['location'], 'middle stair')
        self.assertEqual(state['items']['S']['status'], 'active')
        self.assertEqual(state['items']['S']['control_mode'], 'none')

    def test_new_contact_explicitly_interrupts_then_actor_maintains_pair(self):
        p = self.plan('contact_blocks_hand_mid_existing_event')
        p['beats'][0]['action_events'][1]['interrupts'] = [{'event_id': 'LONG_SWING', 'reason': 'Wrist clamp stops the free swing.'}]
        p['beats'][0]['action_events'].append(event('PRESS_UNDER_CLAMP', 1, 2, hands=['right'], contact_ids=['C1']))
        self.valid(p)
        snapshot = validate_state_plan(p)[0]
        self.assertEqual(snapshot['interrupted_events']['LONG_SWING']['time'], 1)
        self.assertEqual(snapshot['after']['contacts']['C1']['phase'], 'active')
        self.assertIn('0–1秒', action_text(p, p['beats']))
        self.assertNotIn('0–3秒', action_text(p, p['beats']))

    def test_explicit_exit_interruption_cancels_later_endpoint_callbacks(self):
        p = self.plan('body_exits_mid_existing_active_event')
        long, leave = p['beats'][0]['action_events']
        ghost = copy.deepcopy(p['action_initial_state']['items']['S']); ghost['location'] = 'ghost later location'
        long['state_ops'] = [operation('item', 'S', ghost)]
        leave['interrupts'] = [{'event_id': 'LONG_ACTION', 'reason': 'Body dissolves, so its action stops here.'}]
        self.valid(p)
        final = validate_state_plan(p)[0]['after']
        self.assertEqual(final['actors']['A']['status'], 'exited')
        self.assertEqual(final['items']['S']['location'], 'north steps')
        # Reusing the interruption ID or naming a future event cannot remove checks.
        bad = copy.deepcopy(p); bad['beats'][0]['action_events'][1]['interrupts'][0]['event_id'] = 'NOT_RUNNING'
        with self.assertRaisesRegex(ValueError, 'currently running|declared event'):
            self.valid(bad)

    def test_same_body_item_contact_can_slide_and_end_then_new_pair_can_form(self):
        p = self.plan('active_contact_same_id_replaces_endpoint')
        slide = copy.deepcopy(p['action_initial_state']['contacts']['C1'])
        slide['endpoints'][0]['part'] = 'forearm beside the original wrist'
        p['beats'][0]['action_events'][0]['state_ops'][0]['value'] = slide
        final = copy.deepcopy(p['action_initial_state']); final['contacts']['C1'] = slide
        p['beats'][0]['after'] = projection(p, final)
        self.valid(p)
        release = copy.deepcopy(slide); release['phase'] = 'released'
        new_pair = copy.deepcopy(slide); new_pair['endpoints'][1]['body_id'] = 'C'
        e = p['beats'][0]['action_events'][0]
        e['state_ops'] = [operation('contact', 'C1', release, 'end'), operation('contact', 'C2', new_pair, 'create')]
        final['contacts'] = {'C1': release, 'C2': new_pair}; p['beats'][0]['after'] = projection(p, final)
        self.valid(p)

    def test_ongoing_across_two_segments_keeps_origin_and_completion_is_linked(self):
        p = self.plan('ongoing_continuation_preserves_original_event')
        self.valid(p)
        next_segment = copy.deepcopy(p)
        next_segment['beats'][0]['action_events'][0]['id'] = 'E2'
        self.valid(next_segment)
        self.assertEqual(validate_state_plan(next_segment)[0]['after']['pending_events']['P']['source_event_id'], 'E0')
        completed = copy.deepcopy(p['action_initial_state']['pending_events']['P']); completed['phase'] = 'completed'
        e = next_segment['beats'][0]['action_events'][0]
        e.update(completion='complete', state_ops=[operation('pending', 'P', completed)])
        final = copy.deepcopy(p['action_initial_state']); final['pending_events']['P'] = completed
        next_segment['beats'][0]['after'] = projection(next_segment, final)
        self.valid(next_segment)
        bad = copy.deepcopy(next_segment); bad['beats'][0]['action_events'][0]['state_ops'][0]['value']['source_event_id'] = 'E2'
        with self.assertRaisesRegex(ValueError, 'immutable'):
            self.valid(bad)

    def test_two_items_one_hand_requires_scoped_grip_and_cannot_expand(self):
        def configure(p):
            p['action_initial_state']['items']['LETTER'] = item([('A', 'right')], controller='A', mode='held')
            p['action_initial_state']['hand_exceptions'] = {'H': grip()}
        p = make_plan([event('STAFF_USE', 0, 1, hands=['right'], weapon='STAFF'),
                       event('LETTER_USE', 1, 2, hands=['right'], weapon='LETTER')], configure)
        self.valid(p)
        self.assertIn('fixture-text-336、fixture-text-339', p['initial_state']['A'])
        for mutation in ('remove', 'wrong_item', 'wrong_hand'):
            bad = copy.deepcopy(p)
            if mutation == 'remove': bad['action_initial_state']['hand_exceptions'] = {}
            elif mutation == 'wrong_item': bad['action_initial_state']['hand_exceptions']['H']['item_ids'] = ['STAFF']
            else: bad['action_initial_state']['hand_exceptions']['H']['hand'] = 'left'
            with self.subTest(mutation=mutation), self.assertRaisesRegex(ValueError, 'scoped grip exception'):
                self.valid(bad)

    def test_ability_grip_ends_with_activation_and_requires_release_or_new_grip(self):
        def configure(p):
            p['abilities'] = [ability()]
            p['action_initial_state']['active_abilities'] = [{'ability_id': 'Q', 'body_id': 'A'}]
            p['action_initial_state']['items']['LETTER'] = item([('A', 'right')], controller='A', mode='held')
            p['action_initial_state']['hand_exceptions'] = {'H': grip(kind='ability', aid='Q')}
        stop = event('STOP', 0, 1, ability_use={'ability_id': 'Q', 'phase': 'end', 'visible_cost': '', 'restrictions_added': []})
        p = make_plan([stop], configure)
        with self.assertRaisesRegex(ValueError, 'exception needs active ability'):
            self.valid(p)
        ended = copy.deepcopy(p['action_initial_state']['hand_exceptions']['H']); ended['phase'] = 'ended'
        stop['state_ops'] = [operation('hand_exception', 'H', ended, 'end'), operation('item', 'LETTER', item(location='floor'))]
        p['beats'][0]['action_events'] = [stop]
        final = copy.deepcopy(p['action_initial_state'])
        final['active_abilities'] = []; final['hand_exceptions']['H'] = ended; final['items']['LETTER'] = item(location='floor')
        p['beats'][0]['after'] = projection(p, final)
        self.valid(p)
        self.assertEqual(validate_state_plan(p)[0]['after']['items']['LETTER']['location'], 'floor')

    def test_finger_casting_exception_is_explicit_and_does_not_free_other_hand(self):
        def configure(p):
            p['abilities'] = [ability()]
            shield = effect('sustained', 'active', controller='A')
            shield['occupied_hands'] = [{'body_id': 'A', 'hand': 'right'}]
            p['action_initial_state']['effects']['SHIELD'] = shield
            p['action_initial_state']['hand_exceptions'] = {'H': grip(items=['STAFF'], casting=True)}
        p = make_plan([event('FINGER_CAST_AND_SWORD', 0, 1, hands=['right'], weapon='STAFF')], configure)
        self.valid(p)
        bad = copy.deepcopy(p); bad['action_initial_state']['hand_exceptions']['H']['allows_casting'] = False
        bad['initial_state'] = projection(bad, bad['action_initial_state'])
        bad['beats'][0]['before'] = copy.deepcopy(bad['initial_state']); bad['beats'][0]['after'] = copy.deepcopy(bad['initial_state'])
        with self.assertRaisesRegex(ValueError, 'hand maintains'):
            self.valid(bad)
        bad = copy.deepcopy(p); bad['action_initial_state']['hand_exceptions']['H']['hand'] = 'left'
        bad['initial_state'] = projection(bad, bad['action_initial_state'])
        bad['beats'][0]['before'] = copy.deepcopy(bad['initial_state']); bad['beats'][0]['after'] = copy.deepcopy(bad['initial_state'])
        with self.assertRaisesRegex(ValueError, 'hand maintains'):
            self.valid(bad)


class IndependentRoundTwoRegressionTests(unittest.TestCase):
    fixtures = Path(__file__).resolve().parent / 'fixtures/state-audit-round2'

    def plan(self, name):
        return tool.read_json(self.fixtures / (name + '.plan.json'))

    def valid(self, plan):
        return tool.validate(plan, require_review=False)

    def test_original_round_two_triggers_unchanged(self):
        manifest = tool.read_json(self.fixtures / 'cases.json')
        self.assertEqual(len(manifest['cases']), 4)
        for case in manifest['cases']:
            with self.subTest(case=case['id']):
                path = self.fixtures / case['file']
                self.assertEqual(hashlib.sha256(path.read_bytes()).hexdigest(), case['sha256'])
                p = tool.read_json(path)
                if case['expected'] == 'accepted': self.valid(p)
                else:
                    with self.assertRaises(ValueError): self.valid(p)

    def test_canceled_interrupter_never_truncates_projection_or_completed_pickup(self):
        p = self.plan('canceled_future_interrupt_does_not_fire')
        self.valid(p)
        snapshot = validate_state_plan(p)[0]
        self.assertEqual(set(snapshot['interrupted_events']), {'STOP_A'})
        self.assertEqual(snapshot['after']['items']['S']['holders'], [{'body_id': 'A', 'hand': 'right'}])
        text = action_text(p, p['beats'])
        self.assertIn('0–3秒：A', text)
        self.assertNotIn('0–2秒：A', text)
        self.assertNotIn('由STOP_A打断', text)
        self.assertNotIn('2秒停止LONG', text)
        self.assertIn('由STOP_B打断', text)
        self.assertIn('由A右手持握', text)

    def test_canceled_known_callback_keeps_unexecuted_dynamic_conditions_unchecked(self):
        p = self.plan('canceled_callback_still_requires_declared_ability')
        p['abilities'] = [ability('Q')]
        p['beats'][0]['ability_ids'] = ['Q']
        # A legal declaration, but ending Q would fail dynamically because Q
        # was never active. This endpoint is canceled before it can execute.
        use = p['beats'][0]['action_events'][0]['ability_use']
        use.update(ability_id='Q', phase='end')
        self.valid(p)
        self.assertEqual(validate_state_plan(p)[0]['after']['active_abilities'], [])
        # Same separation for future contact state. A declared pair is already
        # released; its canceled end callback must not execute/reopen it.
        p['beats'][0]['action_events'][0].pop('ability_use')
        pair = {'endpoints': [{'body_id': 'A', 'part': 'wrist', 'item_id': '', 'blocks': ['right']},
                              {'body_id': 'B', 'part': 'palm', 'item_id': '', 'blocks': ['left']}],
                'phase': 'released', 'mechanism': 'former wrist grip', 'release_condition': 'already released'}
        p['action_initial_state']['contacts']['C0'] = pair
        p['beats'][0]['action_events'][0]['state_ops'] = [operation('contact', 'C0', pair, 'end')]
        p['initial_state'] = projection(p, p['action_initial_state'])
        p['beats'][0]['before'] = copy.deepcopy(p['initial_state']); p['beats'][0]['after'] = copy.deepcopy(p['initial_state'])
        self.valid(p)

    def test_cast_permission_applies_on_start_and_during_new_resource_occupation(self):
        p = self.plan('grip_only_exception_does_not_allow_casting')
        with self.assertRaisesRegex(ValueError, 'allows_casting'):
            self.valid(p)
        permitted = copy.deepcopy(p)
        permitted['action_initial_state']['hand_exceptions']['H']['allows_casting'] = True
        permitted['initial_state'] = projection(permitted, permitted['action_initial_state'])
        permitted['beats'][0]['before'] = copy.deepcopy(permitted['initial_state'])
        final = copy.deepcopy(permitted['action_initial_state']); final['active_abilities'] = [{'ability_id': 'K', 'body_id': 'A'}]
        permitted['beats'][0]['after'] = projection(permitted, final)
        self.valid(permitted)
        # Activation with a genuinely empty left hand uses the normal rule and
        # does not inherit the right-hand grip-only restriction.
        empty_hand = copy.deepcopy(p); empty_hand['beats'][0]['action_events'][0]['hands_used'] = ['left']
        self.valid(empty_hand)
        # An initially empty casting hand can become occupied during the
        # interval; the live-transition check must enforce the same scope.
        def configure(q):
            q['abilities'] = [ability()]
        cast = event('LONG_CAST', 0, 3, hands=['left'], ability_use={
            'ability_id': 'Q', 'phase': 'activate', 'visible_cost': '', 'restrictions_added': []})
        delivery = event('DELIVER', .1, 1, actor='B', target='A', hands=['right'], weapon='LETTER',
                         operations=[operation('item', 'LETTER', item([('A', 'left')], controller='A', mode='held'))])
        during = make_plan([cast, delivery], configure)
        with self.assertRaisesRegex(ValueError, 'allows_casting'):
            self.valid(during)
        during['action_initial_state']['hand_exceptions'] = {'FINGER': grip(hand='left', items=['LETTER'], casting=True)}
        during['initial_state'] = projection(during, during['action_initial_state'])
        during['beats'][0]['before'] = copy.deepcopy(during['initial_state'])
        final = copy.deepcopy(during['action_initial_state'])
        final['items']['LETTER'] = item([('A', 'left')], controller='A', mode='held')
        final['active_abilities'] = [{'ability_id': 'Q', 'body_id': 'A'}]
        during['beats'][0]['after'] = projection(during, final)
        self.valid(during)

    def test_canceled_values_still_reject_bad_declared_references(self):
        p = self.plan('canceled_callback_still_requires_domain_schema')
        known = copy.deepcopy(p['action_initial_state']['items']['S'])
        known.update(holders=[{'body_id': 'A', 'hand': 'right'}], location='', controller_id='A', control_mode='held')
        p['beats'][0]['action_events'][0]['state_ops'][0]['value'] = known
        self.valid(p)
        for key, value in [('controller_id', 'MISSING_BODY'), ('control_ability_id', 'MISSING_ABILITY')]:
            bad = copy.deepcopy(p); bad['beats'][0]['action_events'][0]['state_ops'][0]['value'][key] = value
            with self.subTest(key=key), self.assertRaisesRegex(ValueError, 'undeclared'):
                self.valid(bad)


class IndependentDeviceTriggerTests(unittest.TestCase):
    fixtures = Path(__file__).resolve().parent / 'fixtures/state-audit-round3'

    def plan(self):
        return tool.read_json(self.fixtures / 'ordinary_held_device_trigger.plan.json')

    def valid(self, plan):
        return tool.validate(plan, require_review=False)

    def refresh(self, p):
        p['initial_state'] = projection(p, p['action_initial_state'])
        p['beats'][0]['before'] = copy.deepcopy(p['initial_state'])
        final = copy.deepcopy(p['action_initial_state'])
        final['active_abilities'] = [{'ability_id': 'SWITCH', 'body_id': 'A'}]
        p['beats'][0]['after'] = projection(p, final)

    def test_original_untyped_device_input_is_unchanged_and_compatible(self):
        case = tool.read_json(self.fixtures / 'cases.json')['cases'][0]
        path = self.fixtures / case['file']
        self.assertEqual(hashlib.sha256(path.read_bytes()).hexdigest(), case['sha256'])
        self.valid(self.plan())

    def test_explicit_item_trigger_is_exact_and_independent_takes_priority(self):
        p = self.plan()
        p['abilities'][0]['trigger_spec'] = {'kind': 'held-item', 'source_item_id': 'S'}
        self.valid(p)
        # The same non-supernatural capability is explicitly independent: it
        # cannot use the device compatibility interpretation to avoid casting.
        independent = copy.deepcopy(p)
        independent['abilities'][0]['trigger_spec'] = {'kind': 'independent', 'source_item_id': ''}
        with self.assertRaisesRegex(ValueError, 'allows_casting'):
            self.valid(independent)
        allowed = copy.deepcopy(independent)
        allowed['action_initial_state']['hand_exceptions'] = {'H': grip(items=['S'], casting=True)}
        self.refresh(allowed)
        self.valid(allowed)
        # Fantasy alone is also not the decision: a declared grip-operated
        # enchanted device uses its own item trigger without independent seals.
        enchanted = copy.deepcopy(p); enchanted['abilities'][0]['supernatural'] = True
        self.valid(enchanted)

    def test_item_trigger_requires_declared_source_selected_item_and_actual_body_grip(self):
        p = self.plan(); p['abilities'][0]['trigger_spec'] = {'kind': 'held-item', 'source_item_id': 'S'}
        missing = copy.deepcopy(p); missing['abilities'][0]['trigger_spec']['source_item_id'] = 'NOT_DECLARED'
        with self.assertRaisesRegex(ValueError, 'undeclared trigger source'):
            self.valid(missing)
        wrong_selection = copy.deepcopy(p); wrong_selection['beats'][0]['action_events'][0]['weapon_id'] = ''
        with self.assertRaisesRegex(ValueError, 'same held source'):
            self.valid(wrong_selection)
        wrong_hand = copy.deepcopy(p); wrong_hand['beats'][0]['action_events'][0]['hands_used'] = ['left']
        with self.assertRaisesRegex(ValueError, 'actual grip'):
            self.valid(wrong_hand)
        wrong_body = copy.deepcopy(p)
        wrong_body['action_initial_state']['items']['S'].update(holders=[{'body_id': 'B', 'hand': 'right'}], controller_id='B')
        self.refresh(wrong_body)
        with self.assertRaisesRegex(ValueError, 'actual grip'):
            self.valid(wrong_body)
        wrong_ability_owner = copy.deepcopy(p); wrong_ability_owner['abilities'][0]['owner'] = 'B'
        with self.assertRaisesRegex(ValueError, 'owner mismatch'):
            self.valid(wrong_ability_owner)

    def test_non_supernatural_flag_does_not_free_occupied_independent_hand(self):
        p = self.plan(); p['beats'][0]['action_events'][0]['weapon_id'] = ''
        with self.assertRaisesRegex(ValueError, 'allows_casting'):
            self.valid(p)
        # An untyped two-item grip is intentionally outside the narrow legacy
        # one-device compatibility case; new declarations bind their source.
        multi = self.plan()
        multi['weapon_profiles'].append({'id': 'T', 'name': 'second device', 'type': 'device', 'visible_traits': 'small', 'owner_id': 'A', 'mount': 'held'})
        multi['action_initial_state']['items']['T'] = item([('A', 'right')], controller='A', mode='held')
        multi['action_initial_state']['hand_exceptions'] = {'H': grip(items=['S', 'T'], casting=False)}
        self.refresh(multi)
        with self.assertRaisesRegex(ValueError, 'allows_casting'):
            self.valid(multi)
        multi['abilities'][0]['trigger_spec'] = {'kind': 'held-item', 'source_item_id': 'S'}
        self.valid(multi)

    def test_trigger_structure_requires_extended_contract_and_binds_fact_digest(self):
        p = self.plan()
        before = tool.compile_handoff(p)['scopes'][0]['input_digest']
        p['abilities'][0]['trigger_spec'] = {'kind': 'held-item', 'source_item_id': 'S'}
        self.assertNotEqual(tool.compile_handoff(p)['scopes'][0]['input_digest'], before)
        legacy = tool.read_json(Path(__file__).resolve().parent / 'fixtures/action-transfer.plan.json')
        legacy['rules']['fantasy'] = True
        legacy['abilities'] = [ability('Q') | {'trigger_spec': {'kind': 'independent', 'source_item_id': ''}}]
        with self.assertRaisesRegex(ValueError, 'trigger_spec needs'):
            self.valid(legacy)


class EmptyHandProjectionRegressionTests(unittest.TestCase):
    def test_original_empty_hand_input_never_invents_grip_or_finger_permission(self):
        fixtures = Path(__file__).resolve().parent / 'fixtures/state-audit-round4'
        case = tool.read_json(fixtures / 'cases.json')['cases'][0]
        path = fixtures / case['file']
        self.assertEqual(hashlib.sha256(path.read_bytes()).hexdigest(), case['sha256'])
        p = tool.read_json(path)
        tool.validate(p, require_review=False)
        self.assertFalse(p['action_initial_state'].get('hand_exceptions'))
        text = action_text(p, p['beats'])
        self.assertIn('此处为独立施术。', text)
        self.assertNotIn('持物手', text)
        self.assertNotIn('分指许可', text)


if __name__ == '__main__':
    unittest.main()
