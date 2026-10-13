"""Run local release checks and save reproducible evidence (no installation)."""
from __future__ import annotations

import argparse
import json
import sys
import shutil
from pathlib import Path

from project import verify_sources
from combat_project.reporting import CheckRunner, input_fingerprints, sha
from combat_project.release_smoke import check_archive

ROOT=Path(__file__).resolve().parents[1]


def main(argv=None):
    parser=argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--report', type=Path, default=ROOT/'outputs/validation/release-validation.json',
                        help='Current report destination; frozen historical evidence is protected')
    args=parser.parse_args(argv)
    target=args.report.resolve()
    if target.is_relative_to((ROOT/'docs/implementation').resolve()):
        parser.error('Historical implementation evidence is frozen; choose a current report destination')
    run=CheckRunner(ROOT)
    results=run.records
    version=None
    error=None
    try:
        checked_inputs=input_fingerprints(ROOT)
        version=json.loads((ROOT/'.codex-plugin/plugin.json').read_text(encoding='utf-8'))['version']
        run('pinned source and formal release preflight',[sys.executable,'scripts/project.py','validate-release'])
        source_batches=verify_sources(ROOT)
        run('unittest',[sys.executable,'-m','unittest','discover','-s','tests','-v'])
        run('content and original case structure',[sys.executable,'-X','utf8','scripts/validate_content.py'])
        # Optional media dependencies are isolated from core execution. Exercise
        # the real media regression in the installed interpreter that has Pillow.
        if __import__('importlib.util', fromlist=['find_spec']).find_spec('PIL') is None:
            media_python = shutil.which('python')
            if media_python and Path(media_python).resolve() != Path(sys.executable).resolve():
                run('optional real media tests',[media_python,'-X','utf8','-m','unittest','discover',
                    '-s','tests','-p','test_sample_video.py','-v'])
        run('standard schemas',[sys.executable,'scripts/check_schemas.py'])
        run('package structure',[sys.executable,'scripts/project.py','validate'])
        run('build archive',[sys.executable,'scripts/project.py','build'])
        for skill,script in [('skill-creator','quick_validate.py'),('plugin-creator','validate_plugin.py')]:
            validator=Path.home()/'.codex/skills/.system'/skill/'scripts'/script
            if validator.exists():
                skill_target=ROOT/'skills/combat-director' if skill=='skill-creator' else ROOT
                run(skill,[sys.executable,'-X','utf8',validator,skill_target])
            else:
                results.append({'check':skill,'passed':None,'status':'not_available'})
        archive=ROOT/'dist'/f'combat-director-{version}.zip'
        first_archive_hash=sha(archive)
        run('repeat archive build',[sys.executable,'scripts/project.py','build'])
        if sha(archive)!=first_archive_hash: raise ValueError('Archive rebuild is not byte-identical')
        archive_files=check_archive(ROOT,archive,run)
        if input_fingerprints(ROOT)!=checked_inputs:
            raise ValueError('Validation inputs changed while checks were running; rerun on stable inputs')
        report={'version':version,'python':sys.version,'platform':sys.platform,'checks':results,
                'checked_input_sha256':checked_inputs,
                'rebuild_reproducible':True,'source_hashes_unchanged':True,'source_batches':source_batches,
                'archive':str(archive.relative_to(ROOT)),
                'archive_sha256':sha(archive),'archive_files':archive_files,'archive_reproducible':True,
                'scope':'Local checks only; does not prove host discovery or video quality.'}
    except (ValueError,OSError,KeyError) as exc:
        error=str(exc)
        report={'version':version,'checks':results,'error':error}
    target.parent.mkdir(parents=True,exist_ok=True)
    target.write_text(json.dumps(report,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
    print(('FAIL: '+error if error else f'PASS: {len(results)} release checks')+f'\nEvidence: {target}')
    return 1 if error else 0


if __name__=='__main__':raise SystemExit(main())
