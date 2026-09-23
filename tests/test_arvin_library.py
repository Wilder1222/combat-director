"""Source coverage and behavioral retrieval checks; no video-quality claims."""
import copy
import importlib.util
import json
import shutil
import tempfile
import unittest
from pathlib import Path
from unittest.mock import patch

ROOT = Path(__file__).resolve().parents[1]


def module(name, relative):
    spec = importlib.util.spec_from_file_location(name, ROOT/relative)
    result = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(result)
    return result


builder = module('arvin_builder', 'scripts/build_arvin_library.py')
library = module('arvin_lookup', 'skills/combat-director/scripts/library_tool.py')


class ArvinLibraryTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.catalog = library.load_catalog()

    def test_named_move_is_located_inside_school_without_reading_cards(self):
        with patch.object(Path, 'read_text', side_effect=AssertionError('body read')):
            result = library.search(self.catalog, 'techniques', '乌龙摆尾', school='八卦掌')
        self.assertEqual([e['id'] for e in result['matches']], ['arvin-tech-bagua'])
        self.assertIn('乌龙摆尾', result['matches'][0]['matched_names'])
        self.assertEqual(result['matches'][0]['detail'], 'detailed')

    def test_cross_kind_school_and_character_filters_preserve_known_results(self):
        cases=[('techniques','乌龙摆尾',{'school':'八卦掌'},'arvin-tech-bagua'),
               ('characters','阿乌',{'character':'白鸽'},'arvin-character-baige'),
               ('choreography','顶心肘',{'school':'八极拳'},'arvin-choreography-baji-pairs'),
               ('effects','白鸽',{'character':'白鸽'},'arvin-effects-character-signatures')]
        for kind,query,filters,wanted in cases:
            with self.subTest(kind=kind):
                self.assertIn(wanted,[e['id'] for e in library.search(self.catalog,kind,query,**filters)['matches']])
        self.assertEqual(library.search(self.catalog,'choreography','顶心肘',school='柔道')['total'],0)
        self.assertEqual(library.search(self.catalog,'effects','白鸽',character='不存在的角色')['total'],0)
        self.assertEqual(library.search(self.catalog,'effects',character='绯雪·冰霜')['total'],0)

    def test_category_facets_and_reviewed_camera_scopes(self):
        facets=library.stats(self.catalog)['facets_by_kind']
        self.assertIn('八极拳',facets['choreography']['schools'])
        self.assertIn('白鸽',facets['effects']['characters'])
        self.assertIn('group',facets['camera']['scope'])
        group=library.search(self.catalog,'camera',scope='group',limit=100)
        ids={e['id'] for e in group['matches']}
        self.assertIn('arvin-camera-spec',ids)
        self.assertNotIn('arvin-camera-pattern-k',ids)
        self.assertEqual(facets['camera']['characters'],[])

    def test_same_move_name_preserves_school_variants(self):
        results = [library.search(self.catalog, 'techniques', '白蛇吐信', school=s)
                   for s in ('八卦掌','杨式55式太极剑','峨眉白猿二十四剑')]
        self.assertEqual([r['total'] for r in results], [1,1,1])
        self.assertEqual(len({r['matches'][0]['id'] for r in results}), 3)
        self.assertEqual(results[1]['matches'][0]['detail'], 'outline')

    def test_fire_character_and_frost_weapon_do_not_merge(self):
        fire = library.search(self.catalog, 'characters', character='绯雪·火焰')
        frost = library.search(self.catalog, 'techniques', school='绯雪樱灼流单太刀')
        self.assertEqual([e['id'] for e in fire['matches']], ['arvin-character-feixue-fire'])
        self.assertEqual([e['id'] for e in frost['matches']], ['arvin-tech-feixue-frost'])
        self.assertEqual(frost['matches'][0]['detail'], 'outline')
        self.assertEqual(library.search(self.catalog,'techniques',character='绯雪·火焰')['total'],0)

    def test_outline_is_never_promoted_to_supplied_detail(self):
        for school in ('长柄镰刀','梦想一心太刀','高级轻功','醉拳'):
            with self.subTest(school=school):
                self.assertEqual(library.search(self.catalog,'techniques',school=school,detail='detailed')['matches'],[])
                self.assertEqual(library.search(self.catalog,'techniques',school=school,detail='outline')['total'],1)

    def test_romanized_move_and_camera_table_names_are_retrievable(self):
        result = library.search(self.catalog, 'techniques', 'Tomoe-nage', school='柔道')
        self.assertEqual(result['total'],1)
        self.assertIn('Tomoe-nage',result['matches'][0]['matched_names'])
        names = next(e['names'] for e in self.catalog['entries'] if e['id']=='arvin-camera-moves15')
        self.assertGreaterEqual(len(names),15)
        self.assertEqual(library.search(self.catalog,'camera',names[0])['matches'][0]['id'],'arvin-camera-moves15')

    def test_paging_visits_each_result_once_and_reports_out_of_range(self):
        seen=[];offset=0
        while True:
            page=library.search(self.catalog,'scenes',limit=3,offset=offset)
            seen += [e['id'] for e in page['matches']]
            if page['next_offset'] is None:break
            offset=page['next_offset']
        self.assertEqual(len(seen),20)
        self.assertEqual(len(set(seen)),20)
        outside=library.search(self.catalog,'scenes',offset=20)
        self.assertEqual(outside['status'],'candidates')
        self.assertEqual(outside['matches'],[])
        self.assertEqual(library.search(self.catalog,'all','完全没有这个条目')['status'],'no_match')
        for kwargs in ({'limit':0},{'limit':101},{'offset':-1},{'offset':True},{'limit':True},{'character':''}):
            with self.subTest(kwargs=kwargs),self.assertRaises(ValueError):
                library.search(self.catalog,'all',**kwargs)

    def test_source_hashes_and_generated_artifacts_are_reproducible(self):
        first=builder.render(ROOT)
        self.assertEqual(first,builder.render(ROOT))
        builder.check_outputs(ROOT,first)
        # A manual edit is detected, not blessed by updating a stored hash.
        name=next(k for k in first if k.endswith('.md'))
        changed={name:first[name]+'edited\n'}
        with self.assertRaisesRegex(ValueError,'out of sync'):
            builder.check_outputs(ROOT,changed)

    def test_tampered_source_is_rejected_before_outputs_are_built(self):
        with tempfile.TemporaryDirectory() as tmp:
            root=Path(tmp)
            dest=root/'sources/upstream/arvin-seedance'
            shutil.copytree(ROOT/'sources/upstream/arvin-seedance',dest)
            p=dest/'SKILL.md';p.write_bytes(p.read_bytes()+b'changed')
            with self.assertRaisesRegex(ValueError,'hash mismatch'):
                builder.render(root)
            self.assertFalse((root/'skills').exists())

    def test_every_overview_family_and_scene_is_sourced_once(self):
        entries=self.catalog['entries']
        overview=[e for e in entries if e['kind']=='techniques' and e['source']['ranges'][0][0] in range(568,604)]
        self.assertEqual(sorted(e['source']['ranges'][0][0] for e in overview),list(range(568,604)))
        scenes=[e for e in entries if e['kind']=='scenes']
        self.assertEqual(sorted(e['source']['ranges'][0][0] for e in scenes),list(range(3019,3039)))
        source=(ROOT/'sources/upstream/arvin-seedance/SKILL.md').read_text(encoding='utf-8').splitlines()
        for e in entries:
            if not e['source']:continue
            body=library.read_card(self.catalog,e['id'])
            for a,b in e['source']['ranges']:
                self.assertIn('\n'.join(source[a-1:b]),body)

    def test_source_metadata_rejects_missing_identity_and_invalid_ranges(self):
        imported=next(i for i,e in enumerate(self.catalog['entries']) if e['source'])
        original=Path.read_text
        for mutation in (lambda e:e.update(source=None),
                         lambda e:e['source'].update(commit='main'),
                         lambda e:e['source'].update(ranges=[[True,2]]),
                         lambda e:e['source'].update(ranges=[[3,2]]),
                         lambda e:e.update(names=['x','x'])):
            data=copy.deepcopy(self.catalog);mutation(data['entries'][imported])
            def read(path,*a,**kw):
                return json.dumps(data,ensure_ascii=False) if path==library.CATALOG else original(path,*a,**kw)
            with self.subTest(mutation=mutation),patch.object(Path,'read_text',read),self.assertRaises(ValueError):
                library.load_catalog()


if __name__=='__main__':unittest.main()
