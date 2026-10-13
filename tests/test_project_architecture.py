"""Exercise source ownership and checkout isolation across maintenance modules."""
import hashlib
import importlib.util
import json
import shutil
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
spec = importlib.util.spec_from_file_location('architecture_project', ROOT / 'scripts/project.py')
project = importlib.util.module_from_spec(spec)
spec.loader.exec_module(project)


class SourceReceiptTests(unittest.TestCase):
    def setUp(self):
        self.temporary = tempfile.TemporaryDirectory(prefix='combat-source-test-')
        self.addCleanup(self.temporary.cleanup)
        self.root = Path(self.temporary.name).resolve()

    def batch(self, relative, receipt_name, name_key):
        folder = self.root / relative
        folder.mkdir(parents=True)
        source = folder / 'source.txt'
        source.write_bytes(b'immutable source\r\n')
        row = {name_key: source.name, 'sha256': hashlib.sha256(source.read_bytes()).hexdigest(),
               'bytes': source.stat().st_size}
        receipt = folder / receipt_name
        receipt.write_text(json.dumps({'files': [row]}), encoding='utf-8')
        return source, receipt

    def test_snapshots_and_attachment_batches_share_fingerprint_checks(self):
        sources = [self.batch('sources/upstream/arvin-seedance', 'manifest.json', 'name'),
                   self.batch('sources/upstream/xianxia-combat-skill', 'source-manifest.json', 'path'),
                   self.batch('sources/attachments/test', 'manifest.json', 'name')]
        self.assertEqual(project.verify_sources(self.root), [
            {'manifest': 'sources/attachments/test/manifest.json', 'files_checked': 1}])
        for source, _ in sources:
            with self.subTest(source=source.relative_to(self.root)):
                original = source.read_bytes()
                source.write_bytes(original + b'changed')
                try:
                    with self.assertRaisesRegex(ValueError, 'Source fingerprint changed'):
                        project.verify_sources(self.root)
                finally:
                    source.write_bytes(original)

    def test_escaping_duplicate_and_invalid_fingerprint_receipts_are_rejected(self):
        _, receipt = self.batch('sources/attachments/test', 'manifest.json', 'name')
        original = json.loads(receipt.read_text(encoding='utf-8'))
        rows = [
            [{**original['files'][0], 'name': '../source.txt'}],
            original['files'] * 2,
            [{**original['files'][0], 'bytes': True}],
            [{**original['files'][0], 'sha256': 'invalid'}],
        ]
        for row in rows:
            with self.subTest(row=row):
                receipt.write_text(json.dumps({'files': row}), encoding='utf-8')
                with self.assertRaises(ValueError):
                    project.verify_sources(self.root)


class ProjectCheckoutTests(unittest.TestCase):
    def setUp(self):
        self.temporary = tempfile.TemporaryDirectory(prefix='combat-architecture-test-')
        self.addCleanup(self.temporary.cleanup)
        self.root = Path(self.temporary.name).resolve() / 'checkout'
        self.root.mkdir()
        self.other = Path(self.temporary.name).resolve() / 'unrelated-cwd'
        self.other.mkdir()
        for folder in ('skills', '.codex-plugin', 'sources/upstream', 'sources/editorial',
                       'sources/attachments', 'scripts/combat_project'):
            shutil.copytree(ROOT / folder, self.root / folder,
                            ignore=shutil.ignore_patterns('__pycache__'))
        for name in ('scripts/project.py', 'scripts/build_arvin_library.py', 'scripts/arvin_items.py',
                     'scripts/generated_files.py', 'scripts/validate_content.py',
                     'docs/implementation/arvin-library-coverage.json'):
            target = self.root / name
            target.parent.mkdir(parents=True, exist_ok=True)
            shutil.copy2(ROOT / name, target)

    def cli(self, command):
        return subprocess.run([sys.executable, '-X', 'utf8', self.root / 'scripts/project.py', command],
                              cwd=self.other, capture_output=True, encoding='utf-8')

    def test_copied_cli_builds_from_an_unrelated_working_directory(self):
        for command in ('validate', 'validate-release', 'build'):
            with self.subTest(command=command):
                result = self.cli(command)
                self.assertEqual(result.returncode, 0, result.stderr)
        archive = Path(result.stdout.strip())
        self.assertTrue(archive.is_relative_to(self.root))
        self.assertTrue(archive.is_file())
        before = archive.read_bytes()
        repeated = self.cli('build')
        self.assertEqual(repeated.returncode, 0, repeated.stderr)
        self.assertEqual(archive.read_bytes(), before)

    def test_copied_cli_uses_its_own_validator_and_imported_packages(self):
        # A caller's package/module cache must not hide changed copied validators.
        validator = self.root / 'scripts/validate_content.py'
        validator.write_text(validator.read_text(encoding='utf-8') +
                             "\ndef validate_links(*args, **kwargs):\n"
                             "    return ['copied content validator sentinel'], 0\n", encoding='utf-8')
        result = self.cli('validate')
        self.assertEqual(result.returncode, 1)
        self.assertIn('copied content validator sentinel', result.stderr)

    def test_runtime_validation_reads_the_requested_schema_module(self):
        project.validate(ROOT)
        schema = self.root / 'skills/combat-director/scripts/combat_schema.py'
        schema.write_text(schema.read_text(encoding='utf-8') +
                          "\ndef audit_schema(*args):\n"
                          "    raise ValueError('copied schema module sentinel')\n", encoding='utf-8')
        with self.assertRaisesRegex(ValueError, 'copied schema module sentinel'):
            project.validate(self.root)

    def test_attachment_corruption_blocks_build_without_replacing_previous_archive(self):
        archive = project.build(self.root)
        before = archive.read_bytes()
        receipt = next((self.root / 'sources/attachments').glob('*/manifest.json'))
        source = receipt.parent / json.loads(receipt.read_text(encoding='utf-8'))['files'][0]['name']
        source.write_bytes(source.read_bytes() + b'changed source')
        with self.assertRaisesRegex(ValueError, 'Source fingerprint changed'):
            project.build(self.root)
        self.assertEqual(archive.read_bytes(), before)
        self.assertEqual(list(archive.parent.glob('.combat-release-*')), [])

    def test_optional_python_syntax_failure_preserves_previous_archive(self):
        archive = project.build(self.root)
        before = archive.read_bytes()
        optional = self.root / 'skills/combat-director/scripts/sample_video.py'
        optional.write_bytes(optional.read_bytes() + b'\ninvalid syntax ***\n')
        with self.assertRaisesRegex(ValueError, 'Invalid Python release resource: .*sample_video.py'):
            project.build(self.root)
        self.assertEqual(archive.read_bytes(), before)
        self.assertEqual(list(archive.parent.glob('.combat-release-*')), [])

    def test_core_cli_missing_import_preserves_previous_archive(self):
        archive = project.build(self.root)
        before = archive.read_bytes()
        cli = self.root / 'skills/combat-director/scripts/combat_tool.py'
        text = cli.read_text(encoding='utf-8').replace(
            'import argparse\n', 'import _combat_director_unavailable_dependency_for_test\nimport argparse\n', 1)
        compile(text, str(cli), 'exec')  # Valid syntax alone cannot establish core importability.
        cli.write_text(text, encoding='utf-8')
        with self.assertRaisesRegex(ValueError, 'Core CLI cannot be imported: .*combat_tool.py'):
            project.build(self.root)
        self.assertEqual(archive.read_bytes(), before)
        self.assertEqual(list(archive.parent.glob('.combat-release-*')), [])


if __name__ == '__main__':
    unittest.main()
