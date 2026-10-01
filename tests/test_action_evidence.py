import copy
import importlib.util
import tempfile
import unittest
from pathlib import Path

ROOT=Path(__file__).resolve().parents[1]
SKILL=ROOT/'skills/combat-director'
spec=importlib.util.spec_from_file_location('action_tool',SKILL/'scripts/combat_tool.py')
tool=importlib.util.module_from_spec(spec)
spec.loader.exec_module(tool)
from combat_review import plan_digest


class ActionEvidenceTests(unittest.TestCase):
    def setUp(self):
        self.plan=tool.read_json(ROOT/'tests/fixtures/action-transfer.plan.json')

    def test_forward_or_duplicate_event_reference(self):
        for mutate in (lambda p:p['beats'][0]['action_events'][0].update(response_to='E6'),
                       lambda p:p['beats'][0]['action_events'][1].update(id='E1')):
            p=copy.deepcopy(self.plan);mutate(p)
            with self.assertRaises(ValueError): tool.validate(p,require_review=False)

    def test_wrong_owner_and_missing_transfer(self):
        p=copy.deepcopy(self.plan)
        p['beats'][0]['action_events'][0]['weapon_id']='STAFF'
        with self.assertRaisesRegex(ValueError,'not held'): tool.validate(p,require_review=False)
        p=copy.deepcopy(self.plan)
        p['beats'][1]['action_events'][1]['transfers']=[]
        with self.assertRaisesRegex(ValueError,'transfer event'): tool.validate(p,require_review=False)

    def test_structured_state_has_one_authority(self):
        p=copy.deepcopy(self.plan)
        p['beats'][-1]['after']['A']='突然回到巷中'
        with self.assertRaisesRegex(ValueError,'after differs'): tool.validate(p,require_review=False)

    def test_ability_cost_prevents_next_hand_use(self):
        p=tool.read_json(ROOT/'tests/fixtures/ability-restrictions.plan.json')
        p['beats'][-1]['action_events'][0]['hands_used']=['right']
        with self.assertRaisesRegex(ValueError,'right hand restricted'): tool.validate(p,require_review=False)
        p=tool.read_json(ROOT/'tests/fixtures/ability-restrictions.plan.json')
        p['beats'][1]['state_delta']['actors']['A']['constraints']=[]
        with self.assertRaisesRegex(ValueError,'cost missing'): tool.validate(p,require_review=False)

    def test_action_details_reach_prompt(self):
        text=tool.prompt(self.plan)
        self.assertIn(self.plan['weapon_profiles'][0]['visible_traits'],text)
        self.assertIn(self.plan['beats'][1]['action_events'][1]['trajectory']['path'],text)
        self.assertIn('A左手持' + self.plan['weapon_profiles'][1]['name'],text)
        self.assertNotIn('"caused_by"',text)
        p=tool.read_json(ROOT/'tests/fixtures/three-actors.plan.json')
        self.assertIn(p['cast'][2]['description'],tool.prompt(p))

    def profile(self,limit=15):
        return {'display_name':'合成夹具','platform':'synthetic','model':'fixture','entry':'test',
                'mode':'single','account_scope':'synthetic-only','claims':{
                    'max_duration':{'status':'supported','value':limit,'source':'synthetic fixture, not provider evidence',
                                    'scope':'synthetic-only','checked_at':'2026-09-20','expires_at':'2026-09-30'}}}

    def test_capability_known_unknown_expired(self):
        p=tool.read_json(ROOT/'tests/fixtures/timing-30.plan.json')
        self.assertEqual(tool.assess_profile(p,self.profile(), '2026-09-21')['status'],'conflict')
        self.assertEqual(tool.assess_profile(p,self.profile(30),'2026-09-21')['status'],'compatible')
        self.assertEqual(tool.assess_profile(p,self.profile(30),'2026-10-01')['status'],'needs_verification')
        profile=self.profile();profile['claims']['max_duration']={'status':'unknown'}
        self.assertEqual(tool.assess_profile(p,profile,'2026-09-21')['status'],'needs_verification')
        with tempfile.TemporaryDirectory() as tmp:
            with self.assertRaisesRegex(ValueError,'platform conflict'):
                tool.export(p,'generic',tmp,profile_override=self.profile(),as_of='2026-09-21')
            self.assertEqual(list(Path(tmp).iterdir()),[])

    def test_invalid_evidence_is_not_compatible(self):
        for value in (True,0,float('nan')):
            profile=self.profile(value)
            with self.assertRaises(ValueError): tool.assess_profile(self.plan,profile,'2026-09-21')
        profile=self.profile();del profile['claims']['max_duration']['source']
        with self.assertRaises(ValueError): tool.assess_profile(self.plan,profile,'2026-09-21')

    def take(self):
        r=tool.review_template(self.plan,'synthetic-take')
        r['media'].update(evidence_kind='synthetic',observation_method='frames',location='synthetic://frame',covered_ranges=[{'start':15,'end':15}])
        r['observed_end_state']=copy.deepcopy(self.plan['beats'][-1]['after'])
        r['observed_end_state']['A']='南口内侧，左手密函，右手空，木杖在脚边；其他姿态unknown'
        r.update(state_evidence='Synthetic test endpoint; no real media reviewed.',decision='accept_with_deviation',
                 decision_by='synthetic-test',decision_reason='Keep observed empty hand as next origin.',
                 deviations=[{'time':15,'observation':'木杖提前落地','impact':'下一段右手空','repair':'从落杖后的状态继续设计'}])
        return r

    def test_accepted_observation_is_next_origin(self):
        schema=tool.read_json(SKILL/'assets/take-review.schema.json');r=self.take()
        seed=tool.continuation_seed(r,self.plan,schema)
        self.assertIn('右手空',seed['initial_state']['A'])
        self.assertEqual(seed['evidence_kind'],'synthetic')
        next_plan=copy.deepcopy(self.plan)
        with self.assertRaisesRegex(ValueError,'accepted observed state'):
            tool.check_continuation(next_plan,r,self.plan,schema)
        next_plan['initial_state']=copy.deepcopy(seed['initial_state'])
        tool.check_continuation(next_plan,r,self.plan,schema)
        self.assertEqual(next_plan['initial_state']['A'],r['observed_end_state']['A'])

    def test_rejected_or_unobserved_take_never_seeds(self):
        schema=tool.read_json(SKILL/'assets/take-review.schema.json')
        for decision in ('reject','repair','pending'):
            r=self.take();r['decision']=decision
            with self.assertRaises(ValueError):tool.continuation_seed(r,self.plan,schema)
        r=tool.review_template(self.plan,'unseen')
        tool.validate_take(r,self.plan,schema)
        r.update(decision='accept',decision_by='test',decision_reason='test',state_evidence='claim')
        with self.assertRaisesRegex(ValueError,'unobserved'):tool.validate_take(r,self.plan,schema)

    def test_partial_frames_never_prove_audio_or_full_video(self):
        schema=tool.read_json(SKILL/'assets/take-review.schema.json');r=self.take()
        r['media']['audio_observed']=True
        with self.assertRaisesRegex(ValueError,'audio'):tool.validate_take(r,self.plan,schema)
        r=self.take();r['media'].update(observation_method='full_video',evidence_kind='actual_media')
        with self.assertRaisesRegex(ValueError,'coverage'):tool.validate_take(r,self.plan,schema)
        r=self.take();r['plan_digest']='0'*64
        with self.assertRaisesRegex(ValueError,'another plan revision'):tool.validate_take(r,self.plan,schema)


if __name__=='__main__':unittest.main()
