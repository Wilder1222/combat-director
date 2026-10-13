"""Historical evidence stays immutable while current checks get new reports."""
import importlib.util
import json
import shutil
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path
from unittest.mock import patch


ROOT = Path(__file__).resolve().parents[1]


def load(name, path):
    spec = importlib.util.spec_from_file_location(name, path)
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


integration = load('maintenance_integration_test', ROOT / 'scripts/validate_integration.py')
reporting = load('maintenance_reporting_test', ROOT / 'scripts/combat_project/reporting.py')


class CurrentReportTests(unittest.TestCase):
    def test_source_drift_changes_fingerprints_and_generated_reports_do_not(self):
        with tempfile.TemporaryDirectory(prefix='combat-input-test-') as directory:
            root = Path(directory)
            source = root / 'sources/upstream/fixture/original.bin'
            attachment = root / 'sources/attachments/fixture/manifest.json'
            output = root / 'outputs/validation/report.json'
            for path, data in ((source, b'source'), (attachment, b'{}'), (output, b'{}')):
                path.parent.mkdir(parents=True, exist_ok=True)
                path.write_bytes(data)
            before = reporting.input_fingerprints(root)
            self.assertEqual(set(before), {source.relative_to(root).as_posix(),
                                          attachment.relative_to(root).as_posix()})
            output.write_bytes(b'changed generated report')
            self.assertEqual(reporting.input_fingerprints(root), before)
            for path in (source, attachment):
                original = path.read_bytes()
                path.write_bytes(original + b'changed input')
                self.assertNotEqual(reporting.input_fingerprints(root), before)
                path.write_bytes(original)

    def test_failed_check_is_recorded_with_utf8_and_expected_failure_can_pass(self):
        run = reporting.CheckRunner(ROOT)
        command = [sys.executable, '-c', "import sys;print('接点');sys.exit(3)"]
        with patch.dict('os.environ', {'PYTHONUTF8': '0'}):
            accepted = run('expected rejection', command, expected=3)
            with self.assertRaisesRegex(ValueError, 'unexpected rejection'):
                run('unexpected rejection', command)
        self.assertTrue(accepted['passed'])
        self.assertEqual(accepted['stdout'].strip(), '接点')
        self.assertEqual(len(run.records), 2)
        self.assertFalse(run.records[-1]['passed'])

    def test_current_release_cannot_overwrite_frozen_evidence(self):
        report = ROOT / 'docs/implementation/release-validation.json'
        before = report.read_bytes()
        process = subprocess.run([sys.executable, '-X', 'utf8',
                                  str(ROOT / 'scripts/validate_release.py'), '--report', str(report)],
                                 cwd=ROOT, capture_output=True, encoding='utf-8')
        self.assertEqual(process.returncode, 2, process.stderr)
        self.assertIn('frozen', process.stderr)
        self.assertEqual(report.read_bytes(), before)


@unittest.skipUnless(shutil.which('git'), 'Historical revision audits require Git')
class HistoricalRevisionTests(unittest.TestCase):
    def setUp(self):
        temporary = tempfile.TemporaryDirectory(prefix='combat-history-test-')
        self.addCleanup(temporary.cleanup)
        self.root = Path(temporary.name).resolve()
        self.assertTrue(self.root.is_relative_to(Path(tempfile.gettempdir()).resolve()))
        self.git('init', '-q')
        self.git('config', 'user.name', 'Fixture')
        self.git('config', 'user.email', 'fixture@example.invalid')
        self.marker = self.root / 'marker.json'
        self.marker.write_text('{"reviewed": true}', encoding='utf-8')
        self.git('add', 'marker.json')
        self.git('commit', '-qm', 'Historical fixture')
        self.commit = self.git('rev-parse', 'HEAD').strip()

    def git(self, *args):
        process = subprocess.run(['git', *args], cwd=self.root, capture_output=True,
                                 encoding='utf-8', check=True)
        return process.stdout

    def test_revision_reads_committed_bytes_and_labels_scope_without_touching_checkout(self):
        self.marker.write_text('{"reviewed": false}', encoding='utf-8')
        before = self.marker.read_bytes()

        def inspect(snapshot):
            self.assertNotEqual(snapshot, self.root)
            return {'passed': json.loads((snapshot / 'marker.json').read_text())['reviewed']}

        with patch.object(integration, 'validate', side_effect=inspect) as validate:
            result = integration.validate_revision(self.root, self.commit)
        validate.assert_called_once()
        self.assertTrue(result['passed'])
        self.assertEqual(result['audited_revision'], self.commit)
        self.assertEqual(result['audited_tree'], 'historical_git_snapshot')
        self.assertFalse(result['current_checkout_verified'])
        self.assertFalse(result['current_host_verified'])
        self.assertEqual(self.marker.read_bytes(), before)

    def test_unknown_or_option_like_revision_is_rejected(self):
        for revision in ('missing-revision', '--output=unwanted'):
            with self.subTest(revision=revision), self.assertRaises(ValueError):
                integration.validate_revision(self.root, revision)
        self.assertEqual(self.git('status', '--short'), '')

    def test_revision_reads_raw_blobs_despite_export_attributes(self):
        (self.root / '.gitattributes').write_text('marker.json export-ignore\nraw.txt export-subst\n',
                                                encoding='utf-8')
        literal = b'$Format:%H$\n'
        (self.root / 'raw.txt').write_bytes(literal)
        self.git('add', '.gitattributes', 'raw.txt')
        self.git('commit', '-qm', 'Export attributes fixture')
        revision = self.git('rev-parse', 'HEAD').strip()
        # Unversioned attributes must not be allowed to hide reviewed files.
        (self.root / '.git/info/attributes').write_text('marker.json export-ignore\n', encoding='utf-8')

        def inspect(snapshot):
            self.assertTrue((snapshot / 'marker.json').is_file())
            self.assertEqual((snapshot / 'raw.txt').read_bytes(), literal)
            return {'passed': True}

        with patch.object(integration, 'validate', side_effect=inspect):
            result = integration.validate_revision(self.root, revision)
        self.assertEqual(result['audited_revision'], revision)
        self.assertTrue(result['passed'])

    def test_revision_ignores_local_git_replacement_objects(self):
        self.marker.write_text('{"reviewed": false}', encoding='utf-8')
        self.git('add', 'marker.json')
        self.git('commit', '-qm', 'Replacement fixture')
        replacement = self.git('rev-parse', 'HEAD').strip()
        self.git('replace', self.commit, replacement)

        def inspect(snapshot):
            self.assertTrue(json.loads((snapshot / 'marker.json').read_text())['reviewed'])
            return {'passed': True}

        with patch.object(integration, 'validate', side_effect=inspect):
            result = integration.validate_revision(self.root, self.commit)
        self.assertEqual(result['audited_revision'], self.commit)
        self.assertTrue(result['passed'])
        self.assertFalse(json.loads(self.marker.read_text())['reviewed'])

    def test_revision_cannot_claim_unversioned_original_evidence(self):
        with patch.object(integration, 'validate_revision') as validate:
            with self.assertRaises(SystemExit) as rejected:
                integration.main(['--root', str(self.root), '--revision', self.commit, '--full-evidence'])
        self.assertEqual(rejected.exception.code, 2)
        validate.assert_not_called()


if __name__ == '__main__':
    unittest.main()
