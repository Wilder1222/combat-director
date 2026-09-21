import copy
import importlib.util
import json
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
SKILL = ROOT / 'skills/combat-director'
SCRIPT = SKILL / 'scripts/combat_tool.py'
spec = importlib.util.spec_from_file_location('combat_tool', SCRIPT)
tool = importlib.util.module_from_spec(spec)
spec.loader.exec_module(tool)


class CombatTests(unittest.TestCase):
    def setUp(self):
        self.plan = tool.read_json(SKILL / 'examples/epic-30.plan.json')

    def invalid(self, plan=None):
        with self.assertRaises(ValueError):
            tool.validate(self.plan if plan is None else plan)

    def test_three_examples_and_prompt_sync(self):
        for path in sorted((SKILL / 'examples').glob('*.plan.json')):
            with self.subTest(path=path.name):
                plan = tool.read_json(path)
                tool.validate(plan)
                self.assertEqual(tool.prompt(plan), path.with_name(path.name.replace('.plan.json', '.prompt.txt')).read_text(encoding='utf-8'))

    def test_gap(self):
        self.plan['beats'][1]['start'] += .1
        self.invalid()

    def test_overlap(self):
        self.plan['beats'][1]['start'] -= .1
        self.invalid()

    def test_zero_beat(self):
        self.plan['beats'][0]['end'] = 0
        self.invalid()

    def test_nonfinite_and_bool(self):
        for bad in (float('nan'), float('inf'), True):
            with self.subTest(value=bad):
                self.plan['duration'] = bad
                self.invalid()

    def test_total_duration(self):
        self.plan['beats'][-1]['end'] = 31
        self.invalid()

    def test_result_and_handles(self):
        for field, value in [('result_at', 30), ('lead_in', 30), ('tail_out', 30)]:
            with self.subTest(field=field):
                p=copy.deepcopy(self.plan)
                p['timing'][field]=value
                self.invalid(p)

    def test_confirmed_limit(self):
        with self.assertRaises(ValueError):
            tool.validate(self.plan,15)
        for bad in (True, 0, float('nan')):
            with self.assertRaises(ValueError):
                tool.validate(self.plan,bad)
        tool.validate(self.plan,30)

    def test_duplicate_ids(self):
        for key in ('cast','beats','sections','abilities'):
            with self.subTest(key=key):
                p=copy.deepcopy(self.plan)
                p[key][1]['id']=p[key][0]['id']
                self.invalid(p)

    def test_missing_opponent(self):
        del self.plan['beats'][0]['actors']['B']
        self.invalid()

    def test_missing_performance(self):
        self.plan['beats'][0]['actors']['B']['performance']=' '
        self.invalid()

    def test_inheritance(self):
        self.plan['beats'][1]['before']['A']='突然移到出口'
        self.invalid()

    def test_axis_change(self):
        self.plan['beats'][0]['camera']['side']='北侧'
        self.plan['beats'][0]['after']['camera_side']='北侧'
        self.invalid()

    def test_one_take_cuts(self):
        self.plan['camera_mode']='one-take'
        self.invalid()

    def test_one_take_shot_change(self):
        p=tool.read_json(SKILL/'examples/grounded-15.plan.json')
        p['beats'][1]['camera']['shot_id']='S02'
        self.invalid(p)

    def test_unknown_ability(self):
        self.plan['beats'][0]['ability_ids']=['UNDECLARED']
        self.invalid()

    def test_ability_owner(self):
        self.plan['abilities'][0]['owner']='C'
        self.invalid()

    def test_ability_limits(self):
        self.plan['rules']['max_scale']='person'
        self.invalid()
        self.plan['rules']['max_scale']='arena'
        self.plan['rules']['fantasy']=False
        self.invalid()

    def test_section_coverage(self):
        for bad in (['B01'], ['B02','B01'], ['B01','B01']):
            with self.subTest(value=bad):
                p=copy.deepcopy(self.plan)
                p['sections'][0]['beat_ids']=bad
                self.invalid(p)

    def test_false_binding_and_frame_actor(self):
        r={'id':'ref1','kind':'first-frame','status':'bound','actors':['A'],'controls':'身份','excludes':'动作','binding_evidence':''}
        self.plan['references']=[r]
        self.invalid()
        r['binding_evidence']='用户已提供的绑定记录'
        tool.validate(self.plan)
        r['actors']=['C']
        self.invalid()

    def test_twelve_exports_no_source_mutation(self):
        with tempfile.TemporaryDirectory() as tmp:
            for path in (SKILL/'examples').glob('*.plan.json'):
                for platform in ('generic','libtv','xiaoyunque','flova'):
                    with self.subTest(plan=path.name,platform=platform):
                        plan=tool.read_json(path)
                        original=copy.deepcopy(plan)
                        out=Path(tmp)/path.stem/platform
                        files=tool.export(plan,platform,out)
                        self.assertEqual(len(files),6)
                        self.assertEqual(plan,original)
                        self.assertEqual(tool.read_json(out/'combat-plan.json'),original)
                        self.assertIn('待核验',(out/'handoff.md').read_text(encoding='utf-8'))

    def test_export_no_overwrite_then_force(self):
        with tempfile.TemporaryDirectory() as tmp:
            out=Path(tmp)
            target=out/'prompt.txt'
            target.write_text('user edit',encoding='utf-8')
            with self.assertRaises(ValueError):
                tool.export(self.plan,'generic',out)
            self.assertEqual(list(out.iterdir()),[target])
            self.assertEqual(target.read_text(encoding='utf-8'),'user edit')
            tool.export(self.plan,'generic',out,force=True)
            self.assertEqual(target.read_text(encoding='utf-8'),tool.prompt(self.plan))

    def test_export_source_protected(self):
        with tempfile.TemporaryDirectory() as tmp:
            source=Path(tmp)/'combat-plan.json'
            with self.assertRaises(ValueError):
                tool.export(self.plan,'generic',tmp,force=True,source_path=source)
            self.assertFalse(source.exists())

    def test_symlink_rejected(self):
        with tempfile.TemporaryDirectory() as tmp:
            source=Path(tmp)/'original.txt'
            source.write_text('keep',encoding='utf-8')
            out=Path(tmp)/'out'
            out.mkdir()
            try:
                (out/'prompt.txt').symlink_to(source)
            except OSError:
                self.skipTest('OS does not permit symlink creation')
            with self.assertRaises(ValueError):
                tool.export(self.plan,'generic',out,force=True)
            self.assertEqual(source.read_text(encoding='utf-8'),'keep')

    def test_schema_rejects_unknown_and_wrong_types(self):
        for key,value in [('duration','30'),('unexpected','x'),('beats',{})]:
            p=copy.deepcopy(self.plan)
            p[key]=value
            self.invalid(p)

    def test_cli(self):
        source=SKILL/'examples/epic-30.plan.json'
        result=subprocess.run([sys.executable,str(SCRIPT),'validate',str(source)],capture_output=True)
        self.assertEqual(result.returncode,0,result.stderr)
        result=subprocess.run([sys.executable,str(SCRIPT),'validate',str(source),'--max-duration','15'],capture_output=True)
        self.assertEqual(result.returncode,1)
        with tempfile.TemporaryDirectory() as tmp:
            bad=Path(tmp)/'bad.json'
            bad.write_text('{"duration":NaN}',encoding='utf-8')
            result=subprocess.run([sys.executable,str(SCRIPT),'validate',str(bad)],capture_output=True)
            self.assertEqual(result.returncode,1)
            self.assertNotIn(b'Traceback',result.stderr)
            out=Path(tmp)/'out'
            result=subprocess.run([sys.executable,str(SCRIPT),'render',str(source),'--platform','xiaoyunque','--out-dir',str(out)],capture_output=True)
            self.assertEqual(result.returncode,0,result.stderr)
            self.assertEqual(len(list(out.iterdir())),6)


if __name__=='__main__':
    unittest.main()
