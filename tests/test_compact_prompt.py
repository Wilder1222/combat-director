import copy
import json
import os
import re
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

    def test_grouped_shots_export_verbatim_and_keep_review_binding(self):
        projection = copy.deepcopy(self.projection)
        for index, section in enumerate(projection['sections']):
            section['text'] = ('【画面与动作】' + section['text'] +
                               '\n【摄影】同侧跟随双方，保留接点与落脚。' +
                               '\n【衔接】从已经改变的站位继续，不重复上一击。')
            if index == 0:
                section['text'] += '\n【声音】碰撞声在两件兵器相抵时出现。'
            else:
                section['text'] += '\n【眼神】视线转向对手尚在回收的兵器。'
        projection = self.review_projection(projection)
        result = tool.deliverables(self.plan, 'generic', prompt_style='detailed', projection=projection)
        for section in projection['sections']:
            self.assertEqual(result['prompt.txt'].count(section['text']), 1)
        self.assertEqual(json.loads(result['prompt-projection.json']), projection)
        projection['sections'][0]['text'] += '\n【光影】接点闪光照亮邻近手背。'
        with self.assertRaisesRegex(ValueError, 'expression_digest'):
            tool.deliverables(self.plan, 'generic', prompt_style='detailed', projection=projection)

    def test_detailed_one_take_has_one_shot_and_continuous_beat_intervals(self):
        projection = self.detailed_projection()
        rendered = compact.render(self.plan, projection, detailed=True)
        self.assertEqual(rendered.count('（镜长'), 1)
        self.assertIn('全镜0–15秒（镜长15秒）', rendered)
        for interval in ('0–4.5秒（镜内节拍4.5秒）', '4.5–7秒（镜内节拍2.5秒）',
                         '7–12.5秒（镜内节拍5.5秒）', '12.5–15秒（镜内节拍2.5秒）'):
            self.assertIn(interval, rendered)
        legacy = compact.render(self.plan, projection)
        self.assertNotIn('镜内节拍', legacy)
        self.assertNotIn('全镜', legacy)

    def test_detailed_multi_shot_keeps_per_shot_duration(self):
        plan = tool.read_json(ROOT/'tests/fixtures/timing-30.plan.json')
        projection = compact.prepare(plan)
        projection['opening'] = '【整体风格】测试用三维动作片。'
        projection['closing'] = '【连续性】仅验证导出结构，不验证视频效果。'
        for section in projection['sections']:
            section['text'] = '【画面与动作】测试段落 ' + section['section_id'] + ' 保留自身事件。'
        compiled = compact.inspect(plan, projection)
        receipt = copy.deepcopy(self.projection['review'])
        for key in ('plan_id', 'source_digest', 'expression_digest'):
            receipt[key] = compiled[key]
        projection = compact.apply_review(plan, projection, receipt)
        rendered = compact.render(plan, projection, detailed=True)
        self.assertNotIn('镜内节拍', rendered)
        self.assertNotIn('全镜', rendered)
        self.assertEqual(rendered.count('（镜长'), len(plan['sections']))
        beats = {beat['id']: beat for beat in plan['beats']}
        for section in plan['sections']:
            start = beats[section['beat_ids'][0]]['start']
            end = beats[section['beat_ids'][-1]]['end']
            self.assertIn(f'{start:g}–{end:g}秒（镜长{end-start:g}秒）', rendered)

    def test_all_prompt_modes_expose_every_node_inside_grouped_sections(self):
        # Six timed facts are grouped into four sections. Outer section times
        # alone previously hid the 2-second and 10-second node boundaries.
        expected = [
            '节点1：0–2秒（占时2秒）',
            '节点2：2–4.5秒（占时2.5秒）',
            '节点3：4.5–7秒（占时2.5秒）',
            '节点4：7–10秒（占时3秒）',
            '节点5：10–12.5秒（占时2.5秒）',
            '节点6：12.5–15秒（占时2.5秒）',
        ]
        original_plan = copy.deepcopy(self.plan)
        original_projection = copy.deepcopy(self.projection)
        detailed = self.detailed_projection()
        candidates = {
            'full': tool.deliverables(self.plan, 'generic')['prompt.txt'],
            'compact': tool.deliverables(self.plan, 'generic', prompt_style='compact',
                                        projection=self.projection)['prompt.txt'],
            'detailed': tool.deliverables(self.plan, 'generic', prompt_style='detailed',
                                         projection=detailed)['prompt.txt'],
        }
        for style, rendered in candidates.items():
            with self.subTest(style=style):
                self.assertEqual(re.findall(r'^节点\d+：[^\n]+$', rendered, re.MULTILINE), expected)
                if style == 'detailed':
                    self.assertEqual(rendered.count('（镜长'), 1)
                if style != 'full':
                    projection = detailed if style == 'detailed' else self.projection
                    for section in projection['sections']:
                        self.assertEqual(rendered.count(section['text']), 1)
        self.assertEqual(self.plan, original_plan)
        self.assertEqual(self.projection, original_projection)

    def test_node_time_changes_invalidate_previously_reviewed_projection(self):
        changed = copy.deepcopy(self.plan)
        changed['beats'][0]['end'] = 1.8
        changed['beats'][1]['start'] = 1.8
        for detailed in (False, True):
            with self.subTest(detailed=detailed), self.assertRaisesRegex(ValueError, 'source is stale'):
                compact.render(changed, self.projection, detailed=detailed)

    def test_authored_local_slow_motion_timing_survives_node_annotations(self):
        projection = self.detailed_projection()
        local_window = '【时间与速度】接触瞬间微慢镜0.25秒，随后恢复实速，继续原退势。'
        lines = projection['sections'][0]['text'].splitlines()
        lines = [local_window if line.startswith('【时间与速度】') else line for line in lines]
        projection['sections'][0]['text'] = '\n'.join(lines)
        projection = self.review_projection(projection)
        rendered = compact.render(self.plan, projection, detailed=True)
        self.assertEqual(rendered.count(local_window), 1)
        self.assertEqual(rendered.count('0.25秒'), 1)
        self.assertNotIn('0.9–1.15秒', rendered)
        self.assertNotIn('成片占时', rendered)
        self.assertNotIn('已含在节点', rendered)
        self.assertIn('节点1：0–2秒（占时2秒）', rendered)

    def test_each_authored_action_duration_survives_both_prompt_projections(self):
        projection = self.detailed_projection()
        action_chain = ('【画面与动作】A侧让0.15秒、拨挡0.2秒、进身0.25秒、'
                        '出拳0.15秒；接触瞬间微慢镜0.25秒，恢复实速收拳0.2秒，'
                        '随原步势稳住支撑0.8秒。B同时收臂0.2秒，承力退移0.8秒。')
        projection['sections'][0]['text'] = action_chain + '\n【摄影】沿原侧跟住动作，接点前收稳。'
        projection = self.review_projection(projection)
        for style in ('compact', 'detailed'):
            with self.subTest(style=style):
                rendered = tool.deliverables(self.plan, 'generic', prompt_style=style,
                                             projection=projection)['prompt.txt']
                self.assertEqual(rendered.count(action_chain), 1)
                self.assertIn('节点1：0–2秒（占时2秒）', rendered)
                self.assertNotIn('成片占时', rendered)
                self.assertNotIn('已含在节点', rendered)

    def test_full_prompt_projects_action_event_durations_without_local_clock_ranges(self):
        plan = tool.read_json(ROOT/'tests/fixtures/action-transfer.plan.json')
        rendered = tool.deliverables(plan, 'generic')['prompt.txt']
        self.assertEqual(re.findall(r'耗时([0-9.]+)秒：([AB])', rendered),
                         [('1.8', 'B'), ('2', 'A'), ('3', 'A'),
                          ('3', 'B'), ('3', 'A'), ('1.4', 'B')])
        self.assertNotIn('0.2–2秒：B', rendered)
        self.assertNotIn('13–14.4秒：B', rendered)

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
