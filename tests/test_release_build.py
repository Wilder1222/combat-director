"""Every formal build must enforce the same generated-source preflight."""
import hashlib
import importlib.util
import json
import shutil
import subprocess
import sys
import tempfile
import unittest
import zipfile
from pathlib import Path
from unittest.mock import patch

ROOT=Path(__file__).resolve().parents[1]
spec=importlib.util.spec_from_file_location('release_project_test',ROOT/'scripts/project.py')
project=importlib.util.module_from_spec(spec)
spec.loader.exec_module(project)


class ReleaseBuildTests(unittest.TestCase):
    def setUp(self):
        self.temp=tempfile.TemporaryDirectory(prefix='combat-build-test-')
        self.root=Path(self.temp.name).resolve()
        self.assertTrue(self.root.is_relative_to(Path(tempfile.gettempdir()).resolve()))
        self.addCleanup(self.temp.cleanup)
        for folder in ('skills','.codex-plugin','sources/upstream','sources/editorial/0.8.3'):
            shutil.copytree(ROOT/folder,self.root/folder,ignore=shutil.ignore_patterns('__pycache__'))
        for name in ('scripts/project.py','scripts/build_arvin_library.py','scripts/arvin_items.py','scripts/generated_files.py','scripts/build_motion_examples.py',
                     'sources/editorial/library-base.json','sources/editorial/arvin-facets.json',
                     'sources/editorial/arvin-generated.json','docs/implementation/arvin-library-coverage.json'):
            path=self.root/name;path.parent.mkdir(parents=True,exist_ok=True);shutil.copy2(ROOT/name,path)
        version=json.loads((self.root/'.codex-plugin/plugin.json').read_text(encoding='utf-8'))['version']
        self.archive=self.root/'dist'/f'combat-director-{version}.zip'
        self.archive.parent.mkdir()
        with zipfile.ZipFile(self.archive,'w') as z:z.writestr('previous.txt','previous verified artifact')

    def test_all_drift_paths_are_rejected_without_overwriting_previous_zip(self):
        changes={
            'skills/combat-director/library/techniques/arvin-tech-bagua.md':lambda s:s+'manual edit\n',
            'skills/combat-director/library/catalog.json':lambda s:s.replace('短弧接引','changed title'),
            'skills/combat-director/library/items.json':lambda s:s.replace('Ko-uchi-gaeshi','invented alias'),
            'skills/combat-director/library/index.md':lambda s:s+'manual navigation edit\n',
            'scripts/arvin_items.py':lambda s:s.replace("'meaning': 'motion_path", "'meaning': 'changed motion_path"),
            'scripts/build_arvin_library.py':lambda s:s.replace('接住来势后移步转腰','改配方但未重建时'),
            'sources/upstream/arvin-seedance/SKILL.md':lambda s:s+'changed source\n',
            'sources/editorial/arvin-facets.json':lambda s:s.replace('"八极拳"','"太极拳"'),
            'skills/combat-director/examples/motion-staff-12.prompt.txt':lambda s:s+'unreviewed edit\n',
            'sources/editorial/0.8.3/motion-staff-12.plan.json':lambda s:s.replace('固定双人全身机位','跟拍双人全身机位'),
        }
        original_zip=self.archive.read_bytes()
        for name,mutation in changes.items():
            with self.subTest(name=name):
                path=self.root/name;before=path.read_bytes()
                changed=mutation(before.decode('utf-8')).encode('utf-8')
                self.assertNotEqual(changed,before)
                path.write_bytes(changed)
                try:
                    with self.assertRaises(ValueError):project.build(self.root)
                    self.assertEqual(original_zip,self.archive.read_bytes())
                    self.assertEqual(list(self.archive.parent.glob('.combat-release-*')),[])
                finally:path.write_bytes(before)

    def test_valid_build_is_reproducible(self):
        path=project.build(self.root)
        first=hashlib.sha256(path.read_bytes()).hexdigest()
        self.assertEqual(path,project.build(self.root))
        self.assertEqual(first,hashlib.sha256(path.read_bytes()).hexdigest())
        with zipfile.ZipFile(path) as z:
            self.assertIsNone(z.testzip())
            self.assertIn('skills/combat-director/library/catalog.json',z.namelist())
            self.assertIn('skills/combat-director/library/items.json',z.namelist())
            self.assertIn('skills/combat-director/library/techniques/index.md',z.namelist())
            self.assertFalse(any(n.startswith('sources/') for n in z.namelist()))

    def test_recipe_rename_rebuilds_and_retires_the_old_generated_card(self):
        source=self.root/'scripts/build_arvin_library.py'
        source.write_text(source.read_text(encoding='utf-8').replace("('baji-pairs',", "('baji-short',"),encoding='utf-8')
        facets=self.root/'sources/editorial/arvin-facets.json'
        data=json.loads(facets.read_text(encoding='utf-8'))
        data['entries']['arvin-choreography-baji-short']=data['entries'].pop('arvin-choreography-baji-pairs')
        facets.write_text(json.dumps(data,ensure_ascii=False),encoding='utf-8')
        result=subprocess.run([sys.executable,'-X','utf8','scripts/build_arvin_library.py'],
                              cwd=self.root,capture_output=True,encoding='utf-8')
        self.assertEqual(result.returncode,0,result.stderr)
        library=self.root/'skills/combat-director/library/choreography'
        self.assertFalse((library/'arvin-choreography-baji-pairs.md').exists())
        self.assertTrue((library/'arvin-choreography-baji-short.md').exists())
        archive=project.build(self.root)
        with zipfile.ZipFile(archive) as z:
            self.assertFalse(any(n.endswith('/arvin-choreography-baji-pairs.md') for n in z.namelist()))

    def test_identical_build_preserves_archive_without_replacement(self):
        path=project.build(self.root)
        before=path.read_bytes()
        timestamp=path.stat().st_mtime_ns
        with patch.object(project.os,'replace',side_effect=PermissionError('archive in use')) as replace:
            self.assertEqual(project.build(self.root),path)
        replace.assert_not_called()
        self.assertEqual(path.read_bytes(),before)
        self.assertEqual(path.stat().st_mtime_ns,timestamp)
        self.assertEqual(list(path.parent.glob('.combat-release-*')),[])

    def test_changed_archive_replacement_failure_keeps_previous_bytes(self):
        path=project.build(self.root)
        before=path.read_bytes()
        reference=self.root/'skills/combat-director/references/quality.md'
        reference.write_text(reference.read_text(encoding='utf-8')+'\nChanged review guidance.\n',encoding='utf-8')
        with patch.object(project.os,'replace',side_effect=PermissionError('archive in use')) as replace:
            with self.assertRaisesRegex(PermissionError,'archive in use'):project.build(self.root)
        replace.assert_called_once()
        self.assertEqual(path.read_bytes(),before)
        self.assertEqual(list(path.parent.glob('.combat-release-*')),[])

    def test_zip_write_or_crc_failure_keeps_previous_zip(self):
        before=self.archive.read_bytes()
        with patch.object(project.zipfile.ZipFile,'writestr',side_effect=OSError('disk full')):
            with self.assertRaisesRegex(OSError,'disk full'):project.build(self.root)
        self.assertEqual(before,self.archive.read_bytes())
        with patch.object(project.zipfile.ZipFile,'testzip',return_value='bad-entry'):
            with self.assertRaisesRegex(ValueError,'integrity'):project.build(self.root)
        self.assertEqual(before,self.archive.read_bytes())
        self.assertEqual(list(self.archive.parent.glob('.combat-release-*')),[])

    def test_runtime_structure_validation_does_not_require_sources(self):
        with tempfile.TemporaryDirectory(prefix='combat-runtime-test-') as tmp:
            unpacked=Path(tmp).resolve()
            self.assertTrue(unpacked.is_relative_to(Path(tempfile.gettempdir()).resolve()))
            for folder in ('skills','.codex-plugin'):
                shutil.copytree(self.root/folder,unpacked/folder,ignore=shutil.ignore_patterns('__pycache__'))
            self.assertGreater(len(project.validate(unpacked)),100)
            with self.assertRaisesRegex(ValueError,'require the repository'):
                project.build(unpacked)


if __name__=='__main__':unittest.main()
