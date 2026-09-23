import copy
import importlib.util
import json
import os
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path
from unittest.mock import patch

ROOT = Path(__file__).resolve().parents[1]
SCRIPT = ROOT / 'skills/combat-director/scripts/library_tool.py'
spec = importlib.util.spec_from_file_location('library_tool', SCRIPT)
library = importlib.util.module_from_spec(spec)
spec.loader.exec_module(library)


class LibraryTests(unittest.TestCase):
    def setUp(self):
        self.catalog = library.load_catalog()

    def test_filter_separates_ordinary_cloth_from_supernatural_field(self):
        ordinary = library.search(self.catalog, 'design', '袈裟伏魔功')
        magic = library.search(self.catalog, 'abilities', '袈裟伏魔功')
        self.assertEqual([m['id'] for m in ordinary['matches']], ['cloth-redirection'])
        self.assertEqual([m['id'] for m in magic['matches']], ['cloth-field'])
        self.assertEqual(magic['matches'][0]['status'], 'candidate')
        self.assertTrue(magic['matches'][0]['requires'])

    def test_group_filter_and_ranked_query(self):
        result = library.search(self.catalog, 'design', '回廊，撤离', 'group')
        self.assertEqual([m['id'] for m in result['matches']], ['corridor-exit'])
        self.assertEqual(result['matches'][0]['matched_terms'], ['回廊', '撤离'])
        self.assertEqual(library.search(self.catalog, 'abilities', '六脉神剑', 'group')['matches'], [])

    def test_no_match_never_inserts_default(self):
        result = library.search(self.catalog, 'design', '量子传送门')
        self.assertEqual(result['status'], 'no_match')
        self.assertEqual(result['matches'], [])
        self.assertEqual(library.search(self.catalog, 'design', '全套原著能力')['matches'], [])

    def test_empty_query_lists_filtered_candidates(self):
        matches = library.search(self.catalog, 'abilities', scope='ranged')['matches']
        self.assertEqual([m['id'] for m in matches], ['finger-lines'])

    def test_search_does_not_read_card_bodies(self):
        original = Path.read_text
        reads = []
        def tracked(path, *args, **kwargs):
            reads.append(path)
            return original(path, *args, **kwargs)
        with patch.object(Path, 'read_text', tracked):
            library.search(library.load_catalog(), 'design', '太极剑')
        self.assertEqual(reads, [library.CATALOG])

    def test_show_reads_only_chosen_card_and_rejects_unknown_id(self):
        with patch.object(Path, 'read_text', return_value='chosen card') as read:
            self.assertEqual(library.read_card(self.catalog, 'round-sword'), 'chosen card')
            self.assertEqual(read.call_count, 1)
        with self.assertRaisesRegex(ValueError, 'unknown card ID'):
            library.read_card(self.catalog, '../catalog')

    def test_duplicate_id_and_invalid_metadata_rejected(self):
        mutations = [lambda d: d['entries'].append(copy.deepcopy(d['entries'][0])),
                     lambda d: d['entries'][0].update(requires=[]),
                     lambda d: d['entries'][0].update(scope=['unknown']),
                     lambda d: d['entries'][0].update(kind=['design']),
                     lambda d: d.update(version=True)]
        for mutation in mutations:
            with self.subTest(mutation=mutation):
                self.check_bad_catalog(mutation)

    def test_missing_duplicate_and_escaping_paths_rejected(self):
        for path in ('design/missing.md', '../outside.md', 'C:/outside.md',
                     '/outside.md', 'design\\outside.md', 'abilities/round-sword.md'):
            with self.subTest(path=path):
                self.check_bad_catalog(lambda d: d['entries'][0].update(path=path))
        self.check_bad_catalog(lambda d: d['entries'][1].update(path=d['entries'][0]['path']))

    def check_bad_catalog(self, mutation):
        with tempfile.TemporaryDirectory() as temp:
            root = Path(temp)
            for entry in self.catalog['entries']:
                card = root / entry['path']
                card.parent.mkdir(exist_ok=True)
                card.write_text('fixture', encoding='utf-8')
            data = copy.deepcopy(self.catalog)
            mutation(data)
            path = root / 'catalog.json'
            path.write_text(json.dumps(data, ensure_ascii=False), encoding='utf-8')
            with self.assertRaises(ValueError):
                library.load_catalog(path)

    def test_cli_works_outside_repository_without_writes(self):
        with tempfile.TemporaryDirectory() as temp:
            result = subprocess.run([sys.executable, SCRIPT, 'search', 'abilities',
                                     '--query', '六脉神剑', '--scope', 'ranged'],
                                    cwd=temp, capture_output=True, encoding='utf-8',
                                    env={**os.environ, 'PYTHONUTF8': '0', 'PYTHONIOENCODING': 'ascii'})
            self.assertEqual(result.returncode, 0, result.stderr)
            self.assertEqual(json.loads(result.stdout)['matches'][0]['id'], 'finger-lines')
            self.assertIn('六脉神剑', result.stdout)
            self.assertEqual(list(Path(temp).iterdir()), [])


if __name__ == '__main__':
    unittest.main()
