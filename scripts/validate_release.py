"""Run local release checks and save reproducible evidence (no installation)."""
from __future__ import annotations

import hashlib
import json
import os
import subprocess
import sys
import tempfile
import zipfile
from pathlib import Path

ROOT=Path(__file__).resolve().parents[1]


def sha(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


def main():
    results=[]
    def run(label,args,expected=0,cwd=ROOT):
        # Pin child-process encoding on Windows as well as the capture decoder.
        proc=subprocess.run([str(a) for a in args],cwd=cwd,capture_output=True,
                            env={**os.environ,'PYTHONUTF8':'1'},encoding='utf-8',errors='strict')
        record={'check':label,'exit_code':proc.returncode,'expected_exit_code':expected,
                'passed':proc.returncode==expected,'stdout':proc.stdout,'stderr':proc.stderr}
        results.append(record)
        if not record['passed']:
            raise ValueError(f'{label}: {proc.stdout}\n{proc.stderr}')
        return record
    version=json.loads((ROOT/'.codex-plugin/plugin.json').read_text(encoding='utf-8'))['version']
    out=ROOT/'docs/implementation';out.mkdir(parents=True,exist_ok=True)
    error=None
    try:
        examples=ROOT/'skills/combat-director/examples'
        prior={p.name:sha(p) for p in examples.iterdir() if p.suffix in ('.json','.txt')}
        run('rebuild original examples',[sys.executable,'scripts/rebuild_examples.py'])
        run('rebuild action examples',[sys.executable,'scripts/build_action_examples.py'])
        current={p.name:sha(p) for p in examples.iterdir() if p.suffix in ('.json','.txt')}
        if prior != current: raise ValueError('Rebuild changed checked-in artifacts; review the generated difference')
        source=ROOT/'sources/attachments/2026-09-21'
        for item in json.loads((source/'manifest.json').read_text(encoding='utf-8'))['files']:
            if sha(source/item['name'])!=item['sha256']: raise ValueError('Source attachment changed: '+item['name'])
        run('unittest',[sys.executable,'-m','unittest','discover','-s','tests','-v'])
        run('standard schemas',[sys.executable,'scripts/check_schemas.py'])
        run('package structure',[sys.executable,'scripts/project.py','validate'])
        run('build archive',[sys.executable,'scripts/project.py','build'])
        for skill,script in [('skill-creator','quick_validate.py'),('plugin-creator','validate_plugin.py')]:
            validator=Path.home()/'.codex/skills/.system'/skill/'scripts'/script
            if validator.exists():
                target=ROOT/'skills/combat-director' if skill=='skill-creator' else ROOT
                run(skill,[sys.executable,'-X','utf8',validator,target])
            else:
                results.append({'check':skill,'passed':None,'status':'not_available'})
        archive=ROOT/'dist'/f'combat-director-{version}.zip'
        first_archive_hash=sha(archive)
        run('repeat archive build',[sys.executable,'scripts/project.py','build'])
        if sha(archive)!=first_archive_hash: raise ValueError('Archive rebuild is not byte-identical')
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
            packaged=unpacked/'skills/combat-director/examples'
            for plan in packaged.glob('*.plan.json'):
                run('unpacked '+plan.name,[sys.executable,cli,'validate',plan],cwd=tmp)
            plan=packaged/'alley-letter-15.plan.json'
            run('unpacked render',[sys.executable,cli,'render',plan,'--out-dir',Path(tmp)/'render'],cwd=tmp)
            if len(list((Path(tmp)/'render').iterdir()))!=7: raise ValueError('Unexpected export count')
            pending=Path(tmp)/'pending.review.json'
            run('take template',[sys.executable,cli,'review-template',plan,'--take-id','pending-test','--out',pending],cwd=tmp)
            run('pending review structure',[sys.executable,cli,'review-take',pending,'--plan',plan],cwd=tmp)
            run('pending cannot continue',[sys.executable,cli,'continuation-seed',pending,'--plan',plan,'--out',Path(tmp)/'forbidden.json'],1,cwd=tmp)
            fixture=ROOT/'evals/fixtures/synthetic-accepted-drop.review.json'
            run('accepted synthetic continuation',[sys.executable,cli,'continuation-seed',fixture,'--plan',plan,'--out',Path(tmp)/'seed.json'],cwd=tmp)
            run('known platform conflict',[sys.executable,cli,'assess-profile',packaged/'epic-30.plan.json',
                '--profile',ROOT/'evals/fixtures/synthetic-limit-15.json','--as-of','2026-09-21'],1,cwd=tmp)
            run('legacy migration',[sys.executable,cli,'migrate',ROOT/'evals/baselines/0.2.0/skills/combat-director/examples/grounded-15.plan.json','--out',Path(tmp)/'migrated.json'],cwd=tmp)
            run('unreviewed migration cannot render',[sys.executable,cli,'render',Path(tmp)/'migrated.json','--out-dir',Path(tmp)/'blocked'],1,cwd=tmp)
        report={'version':version,'python':sys.version,'platform':sys.platform,'checks':results,
                'rebuild_reproducible':True,'source_hashes_unchanged':True,'archive':str(archive.relative_to(ROOT)),
                'archive_sha256':sha(archive),'archive_files':archive_files,'archive_reproducible':True,
                'scope':'Local checks only; does not prove host discovery or video quality.'}
    except (ValueError,OSError) as exc:
        error=str(exc)
        report={'version':version,'checks':results,'error':error}
    target=out/f'validation-{version}.json'
    target.write_text(json.dumps(report,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
    print(('FAIL: '+error if error else f'PASS: {len(results)} release checks')+f'\nEvidence: {target}')
    return 1 if error else 0


if __name__=='__main__':raise SystemExit(main())
