"""Read installed package and fresh app-server discovery; no model turn or installation."""
import argparse
import hashlib
import json
import os
from pathlib import Path
import queue
import subprocess
import threading
import time
import zipfile

ROOT = Path(__file__).resolve().parents[2]


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--cli', type=Path, required=True)
    parser.add_argument('--cache', type=Path, required=True)
    args = parser.parse_args()
    archive = ROOT / 'dist/combat-director-0.10.0.zip'
    output = ROOT / 'docs/implementation/host-installed-0.10.0.json'
    expected = args.cache / 'skills/combat-director/SKILL.md'
    env = {**os.environ, 'PYTHONUTF8': '1'}
    flags = subprocess.CREATE_NO_WINDOW if os.name == 'nt' else 0
    listing = subprocess.run([str(args.cli), 'plugin', 'list', '--marketplace', 'personal', '--json'],
                             check=True, capture_output=True, encoding='utf-8', env=env, creationflags=flags)
    installed = [p for p in json.loads(listing.stdout)['installed'] if p['name'] == 'combat-director']
    compared = []
    with zipfile.ZipFile(archive) as z:
        for info in z.infolist():
            if info.is_dir():
                continue
            path = args.cache / info.filename
            if not path.resolve().is_relative_to(args.cache.resolve()):
                raise ValueError('Archive path escape')
            wanted = hashlib.sha256(z.read(info)).hexdigest()
            actual = hashlib.sha256(path.read_bytes()).hexdigest()
            if actual != wanted:
                raise ValueError('Installed file mismatch: ' + info.filename)
            compared.append({'path': info.filename, 'sha256': actual})
    process = subprocess.Popen([str(args.cli), 'app-server', '--stdio'], cwd=ROOT, env=env,
                               stdin=subprocess.PIPE, stdout=subprocess.PIPE, stderr=subprocess.PIPE,
                               text=True, encoding='utf-8', creationflags=flags)
    incoming = queue.Queue()
    threading.Thread(target=lambda: [incoming.put(line) for line in process.stdout], daemon=True).start()
    threading.Thread(target=lambda: list(process.stderr), daemon=True).start()

    def send(value):
        process.stdin.write(json.dumps(value) + '\n')
        process.stdin.flush()

    def response(identifier):
        deadline = time.monotonic() + 30
        while time.monotonic() < deadline:
            try:
                value = json.loads(incoming.get(timeout=max(.01, deadline - time.monotonic())))
            except queue.Empty:
                break
            if value.get('id') == identifier:
                if 'error' in value:
                    raise ValueError(str(value['error']))
                return value['result']
        raise TimeoutError('app-server response timed out')

    found, errors, error = [], [], None
    try:
        send({'id': 1, 'method': 'initialize', 'params': {'clientInfo': {'name': 'combat-install-check', 'version': '0.10.0'}}})
        response(1)
        send({'method': 'initialized', 'params': {}})
        send({'id': 2, 'method': 'skills/list', 'params': {'cwds': [str(ROOT)], 'forceReload': True}})
        result = response(2)
        for item in result['data']:
            errors.extend(item.get('errors', []))
            found.extend(s for s in item['skills'] if s['name'].split(':')[-1] == 'combat-director'
                         or 'combat-director' in s['path'])
    except (ValueError, OSError, KeyError, TimeoutError) as exc:
        error = str(exc)
    finally:
        process.stdin.close()
        try:
            process.wait(timeout=5)
        except subprocess.TimeoutExpired:
            process.terminate()
            process.wait(timeout=5)
    matches = [s for s in found if Path(s['path']).resolve() == expected.resolve() and s['enabled']]
    passed = (error is None and len(matches) == 1 and len(found) == 1 and len(installed) == 1
              and installed[0]['version'] == '0.10.0' and installed[0]['enabled'])
    report = {'date': '2026-09-30', 'version': '0.10.0', 'passed': passed,
              'installed': installed, 'combat_discovery': found, 'other_skill_error_count': len(errors),
              'cache': str(args.cache), 'archive_sha256': hashlib.sha256(archive.read_bytes()).hexdigest(),
              'compared_file_count': len(compared), 'files': compared, 'error': error,
              'previous_source_backup': r'C:\Users\ww\plugins\combat-director-backup-20260930-0.8.1',
              'limits': 'Fresh local CLI app-server discovery only. Existing desktop turn was not reloaded; no model or media generation.'}
    output.write_text(json.dumps(report, ensure_ascii=False, indent=2) + '\n', encoding='utf-8')
    print(json.dumps({'passed': passed, 'files': len(compared), 'matches': len(matches), 'error': error}))
    return 0 if passed else 1


if __name__ == '__main__':
    raise SystemExit(main())
