"""Query actual app-server skill discovery without creating a model turn."""
from pathlib import Path
import hashlib
import json
import os
import queue
import subprocess
import tempfile
import threading
import time
import zipfile


ROOT = Path(__file__).resolve().parents[2]
CLI = Path('C:/Users/ww/AppData/Roaming/npm/node_modules/@openai/codex/node_modules/@openai/codex-win32-x64/vendor/x86_64-pc-windows-msvc/bin/codex.exe')


def main():
    out = ROOT / 'docs/implementation/host-discovery-0.9.1.json'
    if out.exists():
        raise SystemExit('Evidence already exists; preserve it before a new run.')
    work = Path(tempfile.mkdtemp(prefix='combat-host-discovery-', dir='D:/Temp'))
    project = work / 'project'
    config_root = work / 'codex-config'
    config_root.mkdir()
    archive = ROOT / 'dist/combat-director-0.9.1.zip'
    expected_skill = project / '.agents/skills/combat-director/SKILL.md'
    with zipfile.ZipFile(archive) as z:
        for item in z.infolist():
            if item.is_dir() or not item.filename.startswith('skills/combat-director/'):
                continue
            target = project / '.agents' / item.filename
            if not target.resolve().is_relative_to(project.resolve()):
                raise ValueError('Unsafe archive path')
            target.parent.mkdir(parents=True, exist_ok=True)
            target.write_bytes(z.read(item.filename))
    env = {**os.environ, 'CODEX_HOME': str(config_root)}
    process = subprocess.Popen([str(CLI), 'app-server', '--stdio'], cwd=project,
        env=env, stdin=subprocess.PIPE, stdout=subprocess.PIPE, stderr=subprocess.PIPE,
        text=True, encoding='utf-8', errors='replace', creationflags=subprocess.CREATE_NO_WINDOW)
    incoming = queue.Queue()
    stderr = []
    messages, requests = [], []

    def read_stdout():
        for line in process.stdout:
            incoming.put(line)

    def read_stderr():
        stderr.extend(process.stderr.readlines())

    threading.Thread(target=read_stdout, daemon=True).start()
    threading.Thread(target=read_stderr, daemon=True).start()

    def send(message):
        requests.append(message)
        process.stdin.write(json.dumps(message) + '\n')
        process.stdin.flush()

    def response(identifier):
        deadline = time.monotonic() + 30
        while time.monotonic() < deadline:
            try:
                line = incoming.get(timeout=max(0.01, deadline-time.monotonic()))
            except queue.Empty:
                break
            value = json.loads(line)
            messages.append(value)
            if value.get('id') == identifier:
                if 'error' in value:
                    raise ValueError(str(value['error']))
                return value['result']
        raise TimeoutError('No response for request ' + str(identifier))

    error = None
    found, skill_errors = [], []
    try:
        send({'id': 1, 'method': 'initialize', 'params': {'clientInfo': {'name': 'combat-local-verification', 'version': '0.9.1'}}})
        response(1)
        send({'method': 'initialized', 'params': {}})
        send({'id': 2, 'method': 'skills/list', 'params': {'cwds': [str(project)], 'forceReload': True}})
        result = response(2)
        for entry in result['data']:
            skill_errors.extend(entry['errors'])
            found.extend(s for s in entry['skills'] if s['name'] == 'combat-director')
    except (OSError, ValueError, KeyError, TimeoutError) as exc:
        error = str(exc)
    finally:
        process.stdin.close()
        try:
            process.wait(timeout=5)
        except subprocess.TimeoutExpired:
            process.terminate()
            process.wait(timeout=5)
    raw = work / 'protocol-output.json'
    raw.write_text(json.dumps({'requests': requests, 'responses': messages, 'stderr': ''.join(stderr)}, ensure_ascii=False, indent=2) + '\n', encoding='utf-8')
    matches = [s for s in found if Path(s['path']).resolve() == expected_skill.resolve() and s['enabled']]
    report = {
        'format': 'combat-host-discovery/1', 'date': '2026-09-24',
        'workspace': str(work), 'cli': str(CLI), 'transport': 'local stdio',
        'method': 'initialize, initialized, skills/list',
        'expected_skill': str(expected_skill),
        'expected_skill_sha256': hashlib.sha256(expected_skill.read_bytes()).hexdigest(),
        'archive_sha256': hashlib.sha256(archive.read_bytes()).hexdigest(),
        'combat_matches': found, 'other_skill_error_count': len(skill_errors),
        'raw_protocol': str(raw), 'raw_sha256': hashlib.sha256(raw.read_bytes()).hexdigest(),
        'process_exit_code': process.returncode, 'error': error,
        'passed': error is None and len(matches) == 1,
        'limits': ['Standalone .agents/skills discovery only; plugin lifecycle has separate evidence.', 'Other user skills may be discovered; this is an isolated configuration, not a claim of an empty host catalog.', 'No model invocation, implicit selection, desktop refresh, credential access or media generation.'],
    }
    out.write_text(json.dumps(report, ensure_ascii=False, indent=2)+'\n', encoding='utf-8')
    print(json.dumps({'passed': report['passed'], 'matches': len(matches), 'error': error, 'report': str(out)}, ensure_ascii=False))
    return 0 if report['passed'] else 1


if __name__ == '__main__':
    raise SystemExit(main())
