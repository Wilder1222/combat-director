"""Check extracted release behavior without using repository runtime imports."""
from __future__ import annotations

import hashlib
import json
import sys
import tempfile
import zipfile
from pathlib import Path


def check_archive(root: Path, archive: Path, run) -> list[dict]:
    archive_files=[]
    with tempfile.TemporaryDirectory(prefix='combat-release-') as tmp:
        unpacked=Path(tmp)/'unpacked'
        with zipfile.ZipFile(archive) as z:
            if z.testzip() is not None: raise ValueError('CRC failure')
            for info in z.infolist():
                if info.date_time!=(1980,1,1,0,0,0): raise ValueError('Archive embeds local modification time')
                archive_files.append({'path':info.filename,'sha256':hashlib.sha256(z.read(info)).hexdigest()})
            for name in z.namelist():
                target=(unpacked/name).resolve()
                if not target.is_relative_to(unpacked.resolve()): raise ValueError('Archive path escape')
            z.extractall(unpacked)
        cli=unpacked/'skills/combat-director/scripts/combat_tool.py'
        library_cli=unpacked/'skills/combat-director/scripts/library_tool.py'
        entries=list((unpacked/'skills').rglob('SKILL.md'))
        if entries != [unpacked/'skills/combat-director/SKILL.md']:
            raise ValueError('Detached package exposes more than the single Skill')
        state_plan=root/'tests/fixtures/state-audit-round3/ordinary_held_device_trigger.plan.json'
        state_check="import sys,json;sys.path.insert(0,sys.argv[1]);import combat_tool as t;p=t.read_json(sys.argv[2]);t.validate(p,require_review=False);print(json.dumps({'valid':True,'schema_version':p['schema_version']},ensure_ascii=False))"
        run('unpacked 1.3 held device state',[sys.executable,'-X','utf8','-c',state_check,
            unpacked/'skills/combat-director/scripts',state_plan],cwd=tmp)
        run('unpacked optional media help',[sys.executable,'-X','utf8',
            unpacked/'skills/combat-director/scripts/sample_video.py','--help'],cwd=tmp)
        run('unpacked library validation',[sys.executable,library_cli,'validate'],cwd=tmp)
        candidates=run('unpacked library lookup',[sys.executable,library_cli,'search','design',
            '--query','回廊 撤离','--scope','group'],cwd=tmp)
        if [item['id'] for item in json.loads(candidates['stdout'])['matches']] != ['corridor-exit']:
            raise ValueError('Packaged library lookup mismatch')
        run('unpacked library card',[sys.executable,library_cli,'show','finger-lines'],cwd=tmp)
        named=run('unpacked named technique',[sys.executable,library_cli,'search','techniques',
            '--query','乌龙摆尾','--school','八卦掌','--detail','detailed'],cwd=tmp)
        if [item['id'] for item in json.loads(named['stdout'])['matches']] != ['arvin-tech-bagua']:
            raise ValueError('Packaged named move lookup mismatch')
        compact=run('unpacked compact first page',[sys.executable,library_cli,'search','all'],cwd=tmp)
        if len(compact['stdout']) > 6000:
            raise ValueError('Compact card first page exceeds initial 6000-character budget')
        item_page=run('unpacked name-only item',[sys.executable,library_cli,'items','--query','小内返'],cwd=tmp)
        item=json.loads(item_page['stdout'])['matches'][0]
        if item['detail'] != 'name_only' or item['source_lines'] != [1808]:
            raise ValueError('Packaged source detail is incorrect')
        item_read=run('unpacked selected source row',[sys.executable,library_cli,'item',item['id'],'--source'],cwd=tmp)
        if 'Ko-uchi-gaeshi' not in json.loads(item_read['stdout'])['item']['aliases']:
            raise ValueError('Packaged item lost literal alias')
        item_missing=run('unpacked detail filter',[sys.executable,library_cli,'items','--query','小内返',
            '--min-detail','description'],cwd=tmp)
        if json.loads(item_missing['stdout'])['total'] != 0:
            raise ValueError('Packaged name-only item was promoted by adaptation')
        raw_card=run('unpacked expanded card',[sys.executable,library_cli,'show','arvin-tech-bagua','--source'],cwd=tmp)
        if '### 原文' not in raw_card['stdout']:
            raise ValueError('Packaged source expansion missing')
        run('unpacked imported character',[sys.executable,library_cli,'show','arvin-character-baige'],cwd=tmp)
        missing=run('unpacked missing weapon detail',[sys.executable,library_cli,'search','techniques',
            '--school','长柄镰刀','--detail','detailed'],cwd=tmp)
        if json.loads(missing['stdout'])['matches']:
            raise ValueError('Packaged outline was promoted to detailed technique')
        for label,kind,query,flag,value,wanted in [
            ('school choreography','choreography','顶心肘','--school','八极拳','arvin-choreography-baji-pairs'),
            ('character effects','effects','白鸽','--character','白鸽','arvin-effects-character-signatures')]:
            result=run('unpacked '+label,[sys.executable,library_cli,'search',kind,
                '--query',query,flag,value],cwd=tmp)
            if wanted not in [item['id'] for item in json.loads(result['stdout'])['matches']]:
                raise ValueError('Packaged cross-category filter lost a known result: '+label)
        facet_result=run('unpacked category facets',[sys.executable,library_cli,'stats'],cwd=tmp)
        if 'group' not in json.loads(facet_result['stdout'])['facets_by_kind']['camera']['scope']:
            raise ValueError('Packaged camera scopes mismatch')
        packaged=root/'tests/fixtures'
        if any('/examples/' in f['path'] or '/fixtures/' in f['path'] for f in archive_files):
            raise ValueError('Case or fixture leaked into release')
        for plan in packaged.glob('*.plan.json'):
            if plan.name == 'legacy-v1.plan.json': continue
            run('unpacked '+plan.name,[sys.executable,cli,'validate',plan],cwd=tmp)
        plan=packaged/'action-transfer.plan.json'
        run('unpacked render',[sys.executable,cli,'render',plan,'--out-dir',Path(tmp)/'render'],cwd=tmp)
        if len(list((Path(tmp)/'render').iterdir()))!=7: raise ValueError('Unexpected export count')
        compact_cli=unpacked/'skills/combat-director/scripts/combat_prompt.py'
        compact_plan=packaged/'single-take.plan.json'
        projection=packaged/'single-take.compact.json'
        run('unpacked compact review',[sys.executable,compact_cli,'validate',compact_plan,projection],cwd=tmp)
        run('unpacked compact render',[sys.executable,cli,'render',compact_plan,
            '--prompt-style','compact','--prompt-file',projection,'--out-dir',Path(tmp)/'compact'],cwd=tmp)
        if len(list((Path(tmp)/'compact').iterdir()))!=8: raise ValueError('Unexpected compact export count')
        pending=Path(tmp)/'pending.review.json'
        run('take template',[sys.executable,cli,'review-template',plan,'--take-id','pending-test','--out',pending],cwd=tmp)
        run('pending review structure',[sys.executable,cli,'review-take',pending,'--plan',plan],cwd=tmp)
        run('pending cannot continue',[sys.executable,cli,'continuation-seed',pending,'--plan',plan,'--out',Path(tmp)/'forbidden.json'],1,cwd=tmp)
        run('known platform conflict',[sys.executable,cli,'assess-profile',packaged/'timing-30.plan.json',
            '--profile',root/'tests/fixtures/limit-15.json','--as-of','2026-09-21'],1,cwd=tmp)
        run('legacy migration',[sys.executable,cli,'migrate',root/'tests/fixtures/legacy-v1.plan.json','--out',Path(tmp)/'migrated.json'],cwd=tmp)
        run('unreviewed migration cannot render',[sys.executable,cli,'render',Path(tmp)/'migrated.json','--out-dir',Path(tmp)/'blocked'],1,cwd=tmp)
    return archive_files
