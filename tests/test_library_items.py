"""Item provenance, compact retrieval and read-only package behavior."""
import copy
import importlib.util
import json
import os
import shutil
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path
from unittest.mock import patch

ROOT = Path(__file__).resolve().parents[1]
SKILL = ROOT/'skills/combat-director'
spec = importlib.util.spec_from_file_location('item_test_library', SKILL/'scripts/library_tool.py')
library = importlib.util.module_from_spec(spec)
spec.loader.exec_module(library)


class ItemTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.catalog = library.load_catalog()
        cls.data = library.load_items(cls.catalog)
        cls.source = (ROOT/'sources/upstream/arvin-seedance/SKILL.md').read_text(encoding='utf-8').splitlines()

    def search(self, query='', **kwargs):
        return library.items.search_items(self.data, self.catalog, query, **kwargs)

    def test_name_only_is_findable_but_not_action_detail(self):
        item = self.search('小内返')['matches'][0]
        self.assertEqual(item['source_lines'], [1808])
        self.assertEqual(item['detail'], 'name_only')
        self.assertEqual(self.search('小内返', min_detail='description')['status'], 'no_match')
        selected = library.items.read_item(self.data, self.catalog, item['id'], source=True)
        self.assertEqual(selected['item']['aliases'], ['Ko-uchi-gaeshi'])
        self.assertEqual(selected['source']['evidence'][0]['source_text'], self.source[1807])
        self.assertNotEqual(selected['project_adaptation']['summary'], '')
        self.assertEqual(selected['source']['evidence'][0]['detail_columns'], [])

    def test_named_action_has_literal_source_and_school_variants_do_not_merge(self):
        item = self.search('乌龙摆尾', kind='techniques', school='八卦掌')['matches'][0]
        self.assertEqual(item['source_lines'], [571, 2231])
        self.assertEqual(item['detail'], 'motion_path')
        read = library.items.read_item(self.data, self.catalog, item['id'], source=True)
        self.assertIn(self.source[2230], [e['source_text'] for e in read['source']['evidence']])
        schools = ('八卦掌', '杨式55式太极剑', '峨眉白猿二十四剑')
        variants = [self.search('白蛇吐信', kind='techniques', school=s)['matches'][0] for s in schools]
        self.assertEqual(len({v['id'] for v in variants}), 3)
        self.assertEqual([v['detail'] for v in variants], ['motion_path', 'name_only', 'name_only'])

    def test_alias_collision_preserves_both_source_names(self):
        result = self.search('Hane-goshi', kind='techniques', school='柔道')
        self.assertEqual({m['name'] for m in result['matches']}, {'跳腰', '针腰'})
        self.assertEqual(len({m['id'] for m in result['matches']}), 2)

    def test_source_semantics_are_not_inferred_only_from_column_title(self):
        sparse = self.search('崩袈裟固', kind='techniques')['matches'][0]
        explicit = self.search('体落', kind='techniques', school='柔道')['matches'][0]
        self.assertEqual(sparse['detail'], 'description')
        self.assertEqual(explicit['detail'], 'motion_path')
        e = next(e for e in library.items.read_item(self.data, self.catalog, explicit['id'])['source']['evidence']
                 if e['line'] == 1800)
        self.assertEqual(e['detail_columns'], ['打戏价值'])

    def test_shared_card_facets_do_not_give_every_row_every_school(self):
        result = self.search('乌龙摆尾', kind='characters', character='凛羽')
        self.assertEqual(result['matches'][0]['schools'], ['八卦掌'])
        self.assertEqual(self.search('乌龙摆尾', character='凛羽', school='柔道')['total'], 0)
        read = library.items.read_item(self.data, self.catalog, result['matches'][0]['id'])
        self.assertGreater(len(read['card_context']['schools']), 1)
        self.assertEqual(read['item']['schools'], ['八卦掌'])

    def test_all_evidence_matches_pinned_source_and_row_location(self):
        for item in self.data['entries']:
            for ev in item['evidence']:
                self.assertEqual(ev['source_text'], self.source[ev['line']-1])
                columns = [f['column'] for f in ev['fields']]
                expected = [library.re.sub(r'[*`★]', '', c).strip()
                            for c in self.source[ev['header_line']-1].strip('|').split('|')]
                self.assertEqual(columns, expected)

    def test_item_search_and_read_do_not_load_card_bodies(self):
        original = Path.read_text
        reads = []
        def track(path, *args, **kwargs):
            reads.append(path)
            return original(path, *args, **kwargs)
        with patch.object(Path, 'read_text', track):
            catalog = library.load_catalog()
            data = library.load_items(catalog)
            found = library.items.search_items(data, catalog, '小内返')['matches'][0]
            library.items.read_item(data, catalog, found['id'], source=True)
        self.assertEqual(reads, [library.CATALOG, library.CATALOG.with_name('items.json')])

    def test_paging_and_filters_keep_no_match_distinct_from_exhaustion(self):
        seen, offset = [], 0
        while True:
            page = self.search(card_id='arvin-tech-judo', limit=7, offset=offset)
            seen.extend(m['id'] for m in page['matches'])
            if page['next_offset'] is None:
                break
            offset = page['next_offset']
        self.assertEqual(len(seen), page['total'])
        self.assertEqual(len(set(seen)), page['total'])
        end = self.search(card_id='arvin-tech-judo', offset=len(seen))
        self.assertEqual(end['status'], 'candidates')
        self.assertEqual(end['matches'], [])
        self.assertEqual(self.search('量子传送门')['status'], 'no_match')
        for options in ({'limit': True}, {'offset': -1}, {'detail': 'detailed'},
                        {'min_detail': 'unknown'}, {'detail': 'name_only', 'min_detail': 'description'},
                        {'card_id': '../outside'}, {'school': ''}):
            with self.subTest(options=options), self.assertRaises(ValueError):
                self.search(**options)
        with self.assertRaisesRegex(ValueError, 'unknown item ID'):
            library.items.read_item(self.data, self.catalog, '../outside')

    def test_tampered_item_provenance_and_metadata_are_rejected(self):
        mutations = [
            lambda d: d.update(version=True),
            lambda d: d['entries'].append(copy.deepcopy(d['entries'][0])),
            lambda d: d['source'].update(commit='main'),
            lambda d: d['entries'][0].update(card_id='unknown'),
            lambda d: d['entries'][0].update(id='escaped-item'),
            lambda d: d['entries'][0].update(aliases=['invented alias']),
            lambda d: d['entries'][0].update(detail='unknown'),
            lambda d: d['entries'][0]['evidence'][0].update(line=1),
            lambda d: d['entries'][0]['evidence'][0].update(shared_row='false'),
            lambda d: d['entries'][0]['evidence'][0].update(source_text='| forged |'),
            lambda d: d['entries'][0]['evidence'][0].update(detail_columns=['not a source column']),
        ]
        with tempfile.TemporaryDirectory() as temp:
            path = Path(temp)/'items.json'
            for change in mutations:
                data = copy.deepcopy(self.data)
                change(data)
                path.write_text(json.dumps(data, ensure_ascii=False), encoding='utf-8')
                with self.subTest(change=change), self.assertRaises(ValueError):
                    library.load_items(self.catalog, path)

    def test_compact_card_projection_preserves_ranking_and_source_expand(self):
        full = library.search(self.catalog, 'all')
        short = library.compact_search(full)
        self.assertEqual([r['id'] for r in full['matches']], [r['id'] for r in short['matches']])
        self.assertEqual(full['next_offset'], short['next_offset'])
        self.assertLessEqual(len(json.dumps(short, ensure_ascii=False, indent=2)), 6000)
        for name in ('arvin-tech-bagua', 'arvin-character-baige'):
            compact = library.read_card(self.catalog, name, source=False)
            body = library.read_card(self.catalog, name, source=True)
            self.assertIn('MIT', compact)
            self.assertIn('第三方说明', compact)
            self.assertNotIn('````text', compact)
            self.assertIn('````text', body)
            self.assertLess(len(compact), len(body))

    def test_packaged_cli_is_utf8_and_read_only_outside_repository(self):
        with tempfile.TemporaryDirectory() as temp:
            folder = Path(temp)
            package = folder/'package'
            shutil.copytree(SKILL/'library', package/'library')
            (package/'scripts').mkdir()
            for name in ('library_tool.py', 'library_items.py'):
                shutil.copy2(SKILL/'scripts'/name, package/'scripts'/name)
            before = {p.relative_to(folder): p.read_bytes() for p in folder.rglob('*') if p.is_file()}
            cli = package/'scripts/library_tool.py'
            env = {**os.environ, 'PYTHONUTF8': '0', 'PYTHONIOENCODING': 'ascii'}
            query = subprocess.run([sys.executable, cli, 'items', '--query', '小内返'],
                                   cwd=folder, env=env, capture_output=True, encoding='utf-8')
            self.assertEqual(query.returncode, 0, query.stderr)
            item_id = json.loads(query.stdout)['matches'][0]['id']
            show = subprocess.run([sys.executable, cli, 'item', item_id, '--source'],
                                  cwd=folder, env=env, capture_output=True, encoding='utf-8')
            self.assertEqual(show.returncode, 0, show.stderr)
            self.assertEqual(json.loads(show.stdout)['item']['name'], '小内返')
            after = {p.relative_to(folder): p.read_bytes() for p in folder.rglob('*') if p.is_file()}
            self.assertEqual(before, after)


if __name__ == '__main__':
    unittest.main()
