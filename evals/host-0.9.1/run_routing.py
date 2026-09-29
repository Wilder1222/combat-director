"""Run one actual-host routing case; retain raw events and ordinary host defaults."""
from pathlib import Path
import argparse
import hashlib
import json
import os
import subprocess
import sys
import time
import uuid
import zipfile

ROOT = Path(__file__).resolve().parents[2]
CLI = Path('C:/Users/ww/AppData/Roaming/npm/node_modules/@openai/codex/node_modules/@openai/codex-win32-x64/vendor/x86_64-pc-windows-msvc/bin/codex.exe')


def sha(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


def main(authority=None, results=None, archive=None):
    parser = argparse.ArgumentParser()
    parser.add_argument('case')
    parser.add_argument('--cli', type=Path, default=CLI)
    parser.add_argument('--attempt', choices=['attempt2', 'attempt3', 'attempt4'])
    parser.add_argument('--windows-sandbox', choices=['unelevated'])
    parser.add_argument('--disable-existing-combat-plugin', action='store_true')
    parser.add_argument('--disable-plugins', action='store_true')
    args = parser.parse_args()
    authority = authority or Path(__file__).with_name('routing-cases.json')
    cases = json.loads(authority.read_text(encoding='utf-8'))
    case = next(c for c in cases['cases'] if c['id'] == args.case)
    run_id = case['id'] + ('-'+args.attempt if args.attempt else '')
    result = (results or ROOT / 'evals/results/host-0.9.1') / run_id
    if result.exists():
        raise SystemExit('Case evidence exists; inspect the existing handle before any new attempt.')
    result.mkdir(parents=True)
    # Python 3.13 mkdtemp uses mode 0700 on Windows, excluding the sandbox identity.
    # Inherit the already configured D:/Temp ACL; do not alter any existing ACL.
    work = Path('D:/Temp') / ('combat-routing-'+case['id'].lower()+'-'+uuid.uuid4().hex[:12])
    work.mkdir(mode=0o777)
    project = work / 'project'
    archive = archive or ROOT / 'dist/combat-director-0.9.1.zip'
    with zipfile.ZipFile(archive) as z:
        for entry in z.infolist():
            if entry.is_dir() or not entry.filename.startswith('skills/combat-director/'):
                continue
            dest = project / '.agents' / entry.filename
            if not dest.resolve().is_relative_to(project.resolve()):
                raise ValueError('Unsafe archive path')
            dest.parent.mkdir(parents=True, exist_ok=True)
            dest.write_bytes(z.read(entry.filename))
    skill = project / '.agents/skills/combat-director/SKILL.md'
    (result / 'request.txt').write_text(case['request']+'\n', encoding='utf-8')
    command = [str(args.cli), '-c', 'approval_policy="never"', 'exec', '--ephemeral',
               '--sandbox', 'read-only', '--skip-git-repo-check', '--json', '--color', 'never',
               '--cd', str(project), '--output-last-message', str(result / 'answer.md'), '-']
    if args.windows_sandbox:
        command[1:1] = ['-c', 'windows.sandbox="'+args.windows_sandbox+'"']
    if args.disable_existing_combat_plugin:
        command[1:1] = ['-c', 'plugins."combat-director@personal".enabled=false']
    if args.disable_plugins:
        command[1:1] = ['--disable', 'plugins']
    version = subprocess.run([str(args.cli), '--version'], capture_output=True, text=True, encoding='utf-8', creationflags=subprocess.CREATE_NO_WINDOW)
    metadata = {'case': case, 'run_id': run_id, 'date': '2026-09-29', 'status': 'starting', 'command': command,
                'cwd': str(project), 'archive_sha256': sha(archive), 'candidate_skill': str(skill),
                'candidate_skill_sha256': sha(skill), 'request_sha256': sha(result / 'request.txt'),
                'cli_version': version.stdout.strip(), 'model': 'inherited host configuration; no override',
                'catalog': 'Plugin discovery disabled for this invocation only; ordinary host and project skills remain available.' if args.disable_plugins else ('Requested disabling existing combat plugin for this invocation only; actual selection must be checked.' if args.disable_existing_combat_plugin else 'Normal host configuration and other skills remain available; path collisions must be reported.'),
                'limits': 'Read-only ephemeral model task; no media generation. Discovery and answer text alone do not establish which skill was read.'}
    manifest = result / 'run.json'
    manifest.write_text(json.dumps(metadata, ensure_ascii=False, indent=2)+'\n', encoding='utf-8')
    started = time.monotonic()
    with (result / 'events.jsonl').open('w', encoding='utf-8') as stdout, (result / 'stderr.txt').open('w', encoding='utf-8') as stderr:
        process = subprocess.Popen(command, stdin=subprocess.PIPE, stdout=stdout, stderr=stderr,
                                   cwd=project, env=os.environ.copy(), text=True, encoding='utf-8',
                                   creationflags=subprocess.CREATE_NO_WINDOW)
        metadata.update(status='running', pid=process.pid)
        manifest.write_text(json.dumps(metadata, ensure_ascii=False, indent=2)+'\n', encoding='utf-8')
        print(json.dumps({'case': case['id'], 'pid': process.pid, 'evidence': str(result)}, ensure_ascii=False), flush=True)
        process.communicate(case['request']+'\n')
    metadata.update(status='terminal', exit_code=process.returncode, elapsed_seconds=round(time.monotonic()-started, 3),
                    candidate_skill_sha256_after=sha(skill))
    metadata['artifacts'] = [{'path': p.name, 'sha256': sha(p)} for p in sorted(result.iterdir()) if p.is_file() and p != manifest]
    manifest.write_text(json.dumps(metadata, ensure_ascii=False, indent=2)+'\n', encoding='utf-8')
    print(json.dumps({'case': case['id'], 'exit_code': process.returncode, 'elapsed_seconds': metadata['elapsed_seconds']}, ensure_ascii=False))
    return process.returncode


if __name__ == '__main__':
    raise SystemExit(main())
