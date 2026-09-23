"""Managed-file lifecycle and failure recovery, with no edits to the repository."""
import importlib.util
import json
import os
import tempfile
import unittest
from pathlib import Path
from unittest.mock import patch

ROOT = Path(__file__).resolve().parents[1]
spec = importlib.util.spec_from_file_location('managed_test', ROOT/'scripts/generated_files.py')
managed = importlib.util.module_from_spec(spec)
spec.loader.exec_module(managed)
OLD = 'skills/combat-director/library/techniques/arvin-old.md'
NEW = 'skills/combat-director/library/techniques/arvin-new.md'
CAT = 'skills/combat-director/library/catalog.json'


class GeneratedFilesTests(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory(prefix='combat-managed-test-')
        self.root = Path(self.temp.name).resolve()
        self.assertTrue(self.root.is_relative_to(Path(tempfile.gettempdir()).resolve()))
        self.addCleanup(self.temp.cleanup)
        self.initial = {OLD:'# Old card\n', CAT:'{"fixture":1}\n'}
        managed.apply(self.root, self.initial)

    def snapshot(self):
        return {p.relative_to(self.root).as_posix():p.read_bytes()
                for p in self.root.rglob('*') if p.is_file()}

    def test_rename_retires_only_recorded_unchanged_card(self):
        unrelated = self.root/'skills/combat-director/library/techniques/notes.md'
        unrelated.write_text('user notes', encoding='utf-8')
        newer = {NEW:'# New card\n', CAT:'{"fixture":2}\n'}
        changes = managed.apply(self.root, newer)
        self.assertIn(OLD, changes['retire'])
        self.assertFalse((self.root/OLD).exists())
        self.assertEqual((self.root/NEW).read_text(encoding='utf-8'), newer[NEW])
        self.assertEqual(unrelated.read_text(encoding='utf-8'), 'user notes')
        managed.check(self.root, newer)

    def test_preview_and_check_do_not_write(self):
        before = self.snapshot()
        next_outputs = {NEW:'# Next\n', CAT:'{}\n'}
        changes, _, _ = managed.plan(self.root, next_outputs)
        self.assertIn(OLD, changes['retire'])
        with self.assertRaisesRegex(ValueError, 'out of sync'):
            managed.check(self.root, next_outputs)
        self.assertEqual(before, self.snapshot())

    def test_manual_old_card_or_unknown_generated_card_blocks_before_writing(self):
        for edited in (True, False):
            with self.subTest(edited=edited):
                target = self.root/(OLD if edited else NEW)
                original = target.read_bytes() if target.exists() else None
                target.write_text('manual content', encoding='utf-8')
                before = self.snapshot()
                with self.assertRaisesRegex(ValueError, 'preserve and review'):
                    managed.apply(self.root, {CAT:'changed\n'})
                self.assertEqual(self.snapshot(), before)
                if original is None:target.unlink()
                else:target.write_bytes(original)

    def test_collision_with_unowned_desired_file_is_preserved(self):
        (self.root/NEW).write_text('mine', encoding='utf-8')
        before = self.snapshot()
        with self.assertRaisesRegex(ValueError, 'Unowned output'):
            managed.apply(self.root, {NEW:'replacement', CAT:'changed'})
        self.assertEqual(before, self.snapshot())

    def test_install_failure_rolls_back_updates_creates_and_retirements(self):
        before = self.snapshot()
        original = os.replace
        calls = 0
        def fail_manifest(src, dest):
            nonlocal calls
            calls += 1
            if Path(dest) == self.root/managed.MANIFEST and '.arvin-stage-' in str(src):
                if Path(src).parts[-3:] == ('sources','editorial','arvin-generated.json'):
                    raise OSError('injected manifest install failure')
            return original(src, dest)
        with patch.object(managed.os, 'replace', fail_manifest):
            with self.assertRaisesRegex(OSError, 'injected manifest'):
                managed.apply(self.root, {NEW:'# Created\n', CAT:'{"fixture":2}\n'})
        self.assertGreater(calls, 2)
        self.assertEqual(before, self.snapshot())
        managed.check(self.root, self.initial)

    def test_staging_failure_leaves_original_outputs_intact(self):
        before = self.snapshot()
        original = Path.write_bytes
        def fail_stage(path, data):
            if '.arvin-stage-' in str(path):raise OSError('staging failed')
            return original(path, data)
        with patch.object(Path, 'write_bytes', fail_stage), self.assertRaisesRegex(OSError,'staging failed'):
            managed.apply(self.root, {NEW:'new', CAT:'changed'})
        self.assertEqual(before, self.snapshot())

    def test_failed_rollback_retains_journal_and_explicit_recovery_works(self):
        before = self.snapshot()
        original = os.replace
        calls = 0
        def fail_after_first(src, dest):
            nonlocal calls
            calls += 1
            if calls >= 2:raise OSError('persistent I/O failure')
            return original(src, dest)
        with patch.object(managed.os,'replace',fail_after_first), self.assertRaisesRegex(OSError,'recovery pending'):
            managed.apply(self.root,{NEW:'new',CAT:'changed'})
        self.assertTrue((self.root/managed.LOCK).exists())
        with self.assertRaisesRegex(ValueError,'pending'):
            managed.check(self.root,self.initial)
        managed.recover(self.root)
        self.assertEqual(before,self.snapshot())

    def test_recovery_preserves_a_later_manual_edit(self):
        original = os.replace
        calls = 0
        def interrupt(src,dest):
            nonlocal calls
            calls += 1
            if calls == 2:raise KeyboardInterrupt()
            return original(src,dest)
        with patch.object(managed.os,'replace',interrupt), self.assertRaises(KeyboardInterrupt):
            managed.apply(self.root,{NEW:'new',CAT:'changed'})
        (self.root/CAT).write_text('later user edit',encoding='utf-8')
        before = self.snapshot()
        with self.assertRaisesRegex(ValueError,'later edit'):
            managed.recover(self.root)
        self.assertEqual(before,self.snapshot())

    def test_bad_managed_paths_and_forged_ownership_cannot_escape(self):
        for name in ('../outside.md','skills/combat-director/SKILL.md',
                     'C:/outside.md','skills/combat-director/library/design/round-sword.md'):
            with self.subTest(name=name),self.assertRaises(ValueError):
                managed.apply(self.root,{name:'do not write'})
        p=self.root/managed.MANIFEST;data=json.loads(p.read_text(encoding='utf-8'))
        data['files']['../outside.md']='0'*64;p.write_text(json.dumps(data),encoding='utf-8')
        before=self.snapshot()
        with self.assertRaises(ValueError):managed.apply(self.root,{})
        self.assertEqual(before,self.snapshot())

    def test_symlink_inside_root_is_not_a_managed_target(self):
        target=self.root/'actual.md';target.write_text('user file',encoding='utf-8')
        link=self.root/NEW
        try:link.symlink_to(target)
        except OSError:self.skipTest('symlink creation is unavailable')
        with self.assertRaises(ValueError):managed.apply(self.root,{NEW:'overwrite'})
        self.assertEqual(target.read_text(encoding='utf-8'),'user file')


if __name__=='__main__':unittest.main()
