import copy
import json
import os
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
SKILL = ROOT / 'skills/combat-director'
sys.path.insert(0, str(SKILL / 'scripts'))
import combat_tool as tool
import combat_prompt as compact


class CompactPromptTests(unittest.TestCase):
    def setUp(self):
        self.plan = tool.read_json(ROOT/'tests/fixtures/single-take.plan.json')
        self.projection = tool.read_json(ROOT/'tests/fixtures/single-take.compact.json')

    def test_export_and_legacy_compatibility(self):
        full = tool.deliverables(self.plan, 'generic')
        short = tool.deliverables(self.plan, 'generic', prompt_style='compact', projection=self.projection)
        self.assertEqual(len(full), 7)
        self.assertEqual(len(short), 8)
        self.assertEqual(full['prompt.txt'], tool.prompt(self.plan))
        self.assertEqual(short['prompt.txt'], compact.render(self.plan, self.projection))
        for key in full.keys() - {'prompt.txt'}:
            self.assertEqual(full[key], short[key])

    def detailed_projection(self):
        projection = copy.deepcopy(self.projection)
        for section in projection['sections']:
            original = section['text']
            section['text'] = '\n'.join(f'【{label}】{original} / authored {index}'
                                       for index, label in enumerate(compact.SHOT_LABELS))
        return self.review_projection(projection)

    def review_projection(self, projection):
        compiled = compact.inspect(self.plan, projection)
        receipt = copy.deepcopy(self.projection['review'])
        receipt['expression_digest'] = compiled['expression_digest']
        return compact.apply_review(self.plan, projection, receipt)

    def test_detailed_export_preserves_each_reviewed_shot_and_omits_handoff(self):
        projection = self.detailed_projection()
        projection['opening'] = '公共模块\n【整体风格】写实武侠，共用稳定风格。'
        projection = self.review_projection(projection)
        result = tool.deliverables(self.plan, 'generic', prompt_style='detailed', projection=projection)
        self.assertTrue(result['prompt.txt'].startswith(projection['opening'] + '\n\n'))
        self.assertEqual(result['prompt.txt'].count(projection['opening']), 1)
        self.assertEqual(set(result), {'prompt.txt', 'prompt-projection.json', 'combat-plan.json'})
        for section in projection['sections']:
            self.assertIn(section['text'], result['prompt.txt'])
        self.assertEqual(json.loads(result['prompt-projection.json']), projection)
        self.assertEqual(json.loads(result['combat-plan.json']), self.plan)
        with self.assertRaisesRegex(ValueError, 'platform profiles'):
            tool.deliverables(self.plan, 'libtv', prompt_style='detailed', projection=projection)

    def test_detailed_unlabeled_duplicate_empty_or_global_only_never_writes_output(self):
        valid = self.detailed_projection()
        first, second = compact.SHOT_LABELS[:2]
        original = valid['sections'][1]['text']
        variants = [
            'Unlabeled shot prose',
            original.replace(f'【{second}】', f'【{first}】'),
            '\n'.join([f'【{first}】', *original.splitlines()[1:]]),
            '\n'.join([f'【{first}】同上', *original.splitlines()[1:]]),
        ]
        for text in variants:
            projection = copy.deepcopy(valid)
            projection['opening'] += '\n' + original
            projection['sections'][1]['text'] = text
            projection = self.review_projection(projection)
            with tempfile.TemporaryDirectory() as tmp:
                target = Path(tmp) / 'out'
                with self.assertRaises(ValueError):
                    tool.export(self.plan, 'generic', target, prompt_style='detailed', projection=projection)
                self.assertFalse(target.exists())

    def test_detailed_accepts_different_subsets_and_order_per_shot(self):
        projection = self.detailed_projection()
        for index, section in enumerate(projection['sections']):
            lines = section['text'].splitlines()
            section['text'] = '\n'.join(lines[index:index + 3][::-1])
        projection = self.review_projection(projection)
        result = tool.deliverables(self.plan, 'generic', prompt_style='detailed', projection=projection)
        for section in projection['sections']:
            self.assertIn(section['text'], result['prompt.txt'])
        self.assertNotIn('【法阵】', result['prompt.txt'])

    def test_source_changes_invalidate(self):
        for target, key in [('headers', 'scene'), ('headers', 'continuity'), ('initial_state', 'environment')]:
            plan = copy.deepcopy(self.plan)
            plan[target][key] += ' changed'
            with self.subTest(target=target, key=key), self.assertRaisesRegex(ValueError, 'source is stale'):
                compact.render(plan, self.projection)
        for mutate in (
            lambda p: p['beats'][0]['camera'].update(path='changed camera'),
            lambda p: p['beats'][0]['actors']['A'].update(action='changed event'),
            lambda p: p['rules'].update(fantasy=True),
            lambda p: p['cast'][0].update(hand='left'),
            lambda p: p['references'].append({'id': 'new reference'}),
        ):
            plan = copy.deepcopy(self.plan)
            mutate(plan)
            with self.assertRaisesRegex(ValueError, 'source is stale'):
                compact.render(plan, self.projection)

    def test_prose_change_requires_new_review(self):
        self.projection['sections'][0]['text'] += ' changed'
        with self.assertRaisesRegex(ValueError, 'expression_digest'):
            compact.render(self.plan, self.projection)

    def test_missing_and_invalid_review(self):
        for bad in (None, {}, {'checks': True}):
            self.projection['review'] = bad
            with self.subTest(bad=bad), self.assertRaises(ValueError):
                compact.render(self.plan, self.projection)

    def test_missing_duplicate_reordered_empty_sections(self):
        original = copy.deepcopy(self.projection)
        variants = [original['sections'][:-1], original['sections'][::-1],
                    original['sections'] + [original['sections'][0]],
                    [{'section_id': 'P01', 'text': ''}], None, [None]]
        for sections in variants:
            self.projection['sections'] = sections
            with self.subTest(sections=sections), self.assertRaises(ValueError):
                compact.inspect(self.plan, self.projection)

    def test_unknown_fields_and_empty_headers_rejected(self):
        for key, value in [('opening', ''), ('closing', '  '), ('unexpected', 'x'), ('format', 'combat-prompt/2')]:
            p = copy.deepcopy(self.projection)
            p[key] = value
            with self.subTest(key=key), self.assertRaises(ValueError):
                compact.inspect(self.plan, p)

    def test_receipt_needs_current_hashes_and_explanations(self):
        receipt = copy.deepcopy(self.projection['review'])
        for key, value in [('reviewer', ''), ('method', 'automatic'), ('source_digest', 'old'),
                           ('checks', {k: True for k in compact.CHECKS})]:
            bad = copy.deepcopy(receipt)
            bad[key] = value
            with self.subTest(key=key), self.assertRaises(ValueError):
                compact.apply_review(self.plan, self.projection, bad)
        draft = copy.deepcopy(self.projection)
        draft['review'] = None
        self.assertEqual(compact.apply_review(self.plan, draft, receipt), self.projection)
        self.assertIsNone(draft['review'])

    def test_style_fail_closed_and_no_partial_output(self):
        for style, projection in [('compact', None), ('full', self.projection), ('unknown', None)]:
            with tempfile.TemporaryDirectory() as tmp:
                target = Path(tmp) / 'out'
                with self.assertRaises(ValueError):
                    tool.export(self.plan, 'generic', target, prompt_style=style, projection=projection)
                self.assertFalse(target.exists())

    def test_source_prompt_protected_even_with_force(self):
        with tempfile.TemporaryDirectory() as tmp:
            target = Path(tmp)
            source = target / 'prompt-projection.json'
            source.write_text('original', encoding='utf-8')
            with self.assertRaisesRegex(ValueError, 'source prompt'):
                tool.export(self.plan, 'generic', target, force=True, prompt_style='compact',
                            projection=self.projection, projection_path=source)
            self.assertEqual(source.read_text(), 'original')
            self.assertEqual(list(target.iterdir()), [source])

    def test_cli_roundtrip_outside_repository(self):
        with tempfile.TemporaryDirectory() as tmp:
            plan = ROOT/'tests/fixtures/single-take.plan.json'
            projection = ROOT/'tests/fixtures/single-take.compact.json'
            env = {**os.environ, 'PYTHONUTF8': '1'}
            receipt = Path(tmp) / 'receipt.json'
            receipt.write_text(json.dumps(self.projection['review']), encoding='utf-8')
            detailed = Path(tmp) / 'detailed.json'
            detailed.write_text(json.dumps(self.detailed_projection()), encoding='utf-8')
            commands = [
                [SKILL / 'scripts/combat_tool.py', 'render', plan, '--prompt-style', 'detailed',
                 '--prompt-file', detailed, '--out-dir', Path(tmp) / 'detailed'],
                [SKILL / 'scripts/combat_prompt.py', 'validate', plan, projection],
                [SKILL / 'scripts/combat_tool.py', 'render', plan, '--prompt-style', 'compact',
                 '--prompt-file', projection, '--out-dir', Path(tmp) / 'render'],
                [SKILL / 'scripts/combat_prompt.py', 'prepare', plan, '--out', Path(tmp) / 'draft.json'],
                [SKILL / 'scripts/combat_prompt.py', 'compile', plan, projection, '--out', Path(tmp) / 'inspect.json'],
                [SKILL / 'scripts/combat_prompt.py', 'apply-review', plan, projection, '--receipt', receipt,
                 '--out', Path(tmp) / 'reviewed.json'],
            ]
            for command in commands:
                result = subprocess.run([sys.executable, *map(str, command)], cwd=tmp,
                                        capture_output=True, text=True, encoding='utf-8', env=env)
                self.assertEqual(result.returncode, 0, result.stderr)
            self.assertEqual({p.name for p in (Path(tmp) / 'detailed').iterdir()},
                             {'prompt.txt', 'prompt-projection.json', 'combat-plan.json'})
            inspection = tool.read_json(Path(tmp) / 'inspect.json')
            self.assertIn('source', inspection)
            draft = tool.read_json(Path(tmp) / 'draft.json')
            self.assertIsNone(draft['review'])
            with self.assertRaises(ValueError):
                compact.render(self.plan, draft)


if __name__ == '__main__':
    unittest.main()
