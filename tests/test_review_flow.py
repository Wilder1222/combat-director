import copy
import importlib.util
import tempfile
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
SKILL = ROOT / 'skills/combat-director'
spec = importlib.util.spec_from_file_location('review_tool', SKILL / 'scripts/combat_tool.py')
tool = importlib.util.module_from_spec(spec)
spec.loader.exec_module(tool)


class ReviewFlowTests(unittest.TestCase):
    def setUp(self):
        self.plan = tool.read_json(SKILL / 'examples/epic-30.plan.json')

    def receipt(self, plan):
        # Synthetic unit-test attestation; not a real editorial review.
        return {'plan_id': plan['id'], 'reviews': [
            {k: s[k] for k in ('scope', 'input_digest', 'expression_digest')} |
            {'reviewer': 'synthetic-test', 'method': 'agent', 'checks': {
                k: 'Synthetic structural fixture, not quality evidence.' for k in
                ('identity_action', 'camera_timing', 'ability_cost', 'continuity')}}
            for s in tool.compile_handoff(plan)['scopes']]}

    def test_authority_edits_cannot_silently_export_old_prompt(self):
        changes = [lambda p: p['cast'][0].update(prop='木杖'),
                   lambda p: p['beats'][0]['actors']['A'].update(action='停下并放下兵器'),
                   lambda p: p['beats'][0]['camera'].update(path='固定侧面机位，快移杖端轻微模糊'),
                   lambda p: p['abilities'][0].update(cost='右手不能再持剑')]
        for change in changes:
            p = copy.deepcopy(self.plan)
            change(p)
            with self.assertRaisesRegex(ValueError, 'stale'):
                tool.prompt(p)
            with tempfile.TemporaryDirectory() as tmp:
                with self.assertRaisesRegex(ValueError, 'stale'):
                    tool.export(p, 'generic', tmp)
                self.assertEqual(list(Path(tmp).iterdir()), [])

    def test_summary_edit_invalidates_its_attestation(self):
        p = tool.read_json(SKILL / 'examples/grounded-15.plan.json')
        p['sections'][0]['summary']['camera'] = '在2秒处切至北侧特写'
        status = {s['scope']: s['status'] for s in tool.readiness(p)}
        self.assertEqual(status['P01'], 'stale')
        self.assertEqual(status['P02'], 'ready')
        with self.assertRaisesRegex(ValueError, 'P01=stale'):
            tool.prompt(p)
        q = tool.read_json(SKILL / 'examples/grounded-15.plan.json')
        self.assertIn('不切镜', tool.prompt(q))

    def test_scope_dependencies_include_prior_results(self):
        self.plan['beats'][0]['actors']['A']['action'] += '。抬眼'
        statuses = {s['scope']: s['status'] for s in tool.readiness(self.plan)}
        self.assertEqual(statuses['P01'], 'stale')
        self.assertEqual(statuses['P02'], 'ready')
        self.plan['beats'][0]['after']['environment'] += '；落石'
        statuses = {s['scope']: s['status'] for s in tool.readiness(self.plan)}
        self.assertEqual(statuses['P02'], 'stale')

    def test_camera_facts_and_expression_have_separate_export_dependencies(self):
        p = tool.read_json(SKILL / 'examples/motion-staff-12.plan.json')
        original_summary = p['sections'][1]['summary']['camera']
        p['beats'][1]['camera']['path'] = '摄影机沿南侧缓慢横移，保持交接杖端可辨。'
        scope = tool.compile_handoff(p)['scopes'][2]
        self.assertEqual(scope['facts']['beats'][0]['camera']['path'], p['beats'][1]['camera']['path'])
        # Compilation does not invent a revised prose summary from camera facts.
        self.assertEqual(scope['expression']['camera'], original_summary)
        self.assertEqual({x['scope']: x['status'] for x in tool.readiness(p)}['P02'], 'stale')
        with tempfile.TemporaryDirectory() as tmp:
            with self.assertRaisesRegex(ValueError, 'P02=stale'):
                tool.export(p, 'generic', tmp)
            self.assertEqual(list(Path(tmp).iterdir()), [])
            p['sections'][1]['summary']['camera'] = '南侧缓慢横移，交接与回收过程可辨。'
            # This fixture tests binding/export, not whether the new prose is good.
            p = tool.apply_review(p, self.receipt(p))
            tool.export(p, 'generic', tmp)
            handoff = tool.read_json(Path(tmp) / 'prompt-handoff.json')['scopes'][2]
            self.assertEqual(handoff['expression']['camera'], p['sections'][1]['summary']['camera'])
            self.assertIn('<运镜> ' + p['sections'][1]['summary']['camera'], (Path(tmp) / 'prompt.txt').read_text(encoding='utf-8'))
            p['sections'][1]['summary']['camera'] += ' 改为固定机位。'
            with self.assertRaisesRegex(ValueError, 'P02=stale'):
                tool.prompt(p)

    def test_formatting_and_provenance_do_not_invalidate(self):
        self.plan['provenance'] += '；补充来源说明'
        self.plan['cast'][0]['description'] = '  ' + self.plan['cast'][0]['description'] + '\r\n'
        self.plan['duration'] = float(self.plan['duration'])
        tool.validate(self.plan)

    def test_final_state_invalidates_global_story_ending(self):
        self.plan['beats'][-1]['after']['A'] += '；已离开场景'
        self.assertEqual(tool.readiness(self.plan)[0]['status'], 'stale')

    def test_legacy_migration_requires_explicit_review(self):
        old = tool.read_json(ROOT / 'evals/baselines/0.2.0/skills/combat-director/examples/epic-30.plan.json')
        before = copy.deepcopy(old)
        updated = tool.migrate(old)
        self.assertEqual(old, before)
        self.assertEqual(updated['editorial_reviews'], {})
        with self.assertRaisesRegex(ValueError, 'needs_semantic_review'):
            tool.prompt(updated)
        receipt = self.receipt(updated)
        reviewed = tool.apply_review(updated, receipt)
        tool.validate(reviewed)
        self.assertEqual(updated['editorial_reviews'], {})
        updated['sections'][0]['summary']['action'] += ' changed'
        with self.assertRaisesRegex(ValueError, 'expression_digest changed'):
            tool.apply_review(updated, receipt)

    def test_invalid_or_incomplete_receipts_are_rejected(self):
        for mutate in (lambda r: r.update(plan_id='wrong'),
                       lambda r: r['reviews'][0].update(reviewer=''),
                       lambda r: r['reviews'][0]['checks'].update(camera_timing=True),
                       lambda r: r['reviews'].append(copy.deepcopy(r['reviews'][0]))):
            r = self.receipt(self.plan)
            mutate(r)
            with self.assertRaises(ValueError):
                tool.apply_review(self.plan, r)

    def test_schema_assertions_are_audited(self):
        for schema in ({'type': 'string', 'maxLength': 1},
                       {'type': 'string', 'unknownConstraint': 1}):
            with self.assertRaises(ValueError):
                tool.check_schema('abcd', schema, schema)
        with self.assertRaisesRegex(ValueError, 'incorrect constant'):
            tool.check_schema(True, {'const': 1}, {'const': 1})
        rule = {'$defs': {'text': {'type': 'string'}}, '$ref': '#/$defs/text', 'maxLength': 1}
        with self.assertRaisesRegex(ValueError, 'too long'):
            tool.check_schema('ab', rule, rule)

    def test_compiled_handoff_preserves_authority_and_is_independent(self):
        h = tool.compile_handoff(self.plan)
        self.assertEqual(h['scopes'][1]['facts']['beats'][0], self.plan['beats'][0])
        h['scopes'][1]['facts']['beats'][0]['actors']['A']['action'] = 'changed'
        self.assertNotEqual(h['scopes'][1]['facts']['beats'][0], self.plan['beats'][0])
        text = tool.prompt(self.plan)
        self.assertIn(self.plan['abilities'][0]['end_condition'], text)
        self.assertIn(self.plan['abilities'][0]['cost'], text)


if __name__ == '__main__':
    unittest.main()
