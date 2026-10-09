"""Verify single-entry discovery in a fresh local Codex app-server connection.

Only initialize and skills/list are sent. No chat, turn, model call, or media
generation is started. This host check is outside the distributed skill.
"""
from __future__ import annotations

import argparse
import hashlib
import json
import os
from pathlib import Path
import queue
import shutil
import subprocess
import threading
import time


def discover(cwd: Path):
    executable = shutil.which('codex')
    if not executable:
        raise ValueError('Codex CLI is unavailable')
    command = [executable, 'app-server', '--stdio']
    options = {}
    if os.name == 'nt':
        options['creationflags'] = subprocess.CREATE_NO_WINDOW
        if executable.lower().endswith(('.cmd', '.bat')):
            command = ['cmd.exe', '/d', '/c', executable, 'app-server', '--stdio']
    process = subprocess.Popen(command, cwd=cwd, stdin=subprocess.PIPE,
                               stdout=subprocess.PIPE, stderr=subprocess.PIPE,
                               text=True, encoding='utf-8', **options)
    messages = queue.Queue()
    def reader(stream, destination):
        for line in stream:
            destination.put(line)
    threading.Thread(target=reader, args=(process.stdout, messages), daemon=True).start()
    # Drain diagnostics without exposing potentially unrelated plugin details.
    diagnostics = queue.Queue()
    threading.Thread(target=reader, args=(process.stderr, diagnostics), daemon=True).start()
    def send(value):
        process.stdin.write(json.dumps(value)+'\n')
        process.stdin.flush()
    def response(identifier):
        deadline = time.monotonic()+40
        while time.monotonic() < deadline:
            if process.poll() is not None and messages.empty():
                raise ValueError('App-server terminated before the response')
            try:
                line = messages.get(timeout=min(1, deadline-time.monotonic()))
            except queue.Empty:
                continue
            try:
                value = json.loads(line)
            except json.JSONDecodeError:
                continue
            if value.get('id') == identifier:
                if 'error' in value:
                    raise ValueError('App-server rejected metadata request: '+str(value['error']))
                return value['result']
        raise ValueError('App-server metadata response timed out')
    try:
        send({'id': 1, 'method': 'initialize', 'params': {
            'clientInfo': {'name': 'combat_integration_verifier', 'version': '0.11.0'},
            'capabilities': {'experimentalApi': True}}})
        response(1)
        send({'method': 'initialized', 'params': {}})
        send({'id': 2, 'method': 'skills/list', 'params': {
            'cwds': [str(cwd)], 'forceReload': True}})
        return response(2)
    finally:
        process.stdin.close()
        try:
            process.wait(timeout=5)
        except subprocess.TimeoutExpired:
            process.terminate()
            try:
                process.wait(timeout=5)
            except subprocess.TimeoutExpired:
                process.kill()
                process.wait()


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--cwd', type=Path, default=Path(__file__).resolve().parents[1])
    parser.add_argument('--out', type=Path, required=True)
    args = parser.parse_args()
    root = args.cwd.resolve()
    response = discover(root)
    relevant, errors = [], []
    for entry in response.get('data', []):
        for skill in entry.get('skills', []):
            name = skill.get('name', '').split(':')[-1]
            if name in {'combat-director', 'xianxia-combat'}:
                relevant.append(skill)
        errors.extend(error for error in entry.get('errors', [])
                      if any(name in json.dumps(error) for name in ('combat-director', 'xianxia-combat')))
    enabled = [skill for skill in relevant if skill.get('enabled', True)]
    expected = root/'skills/combat-director/SKILL.md'
    expected_sha = hashlib.sha256(expected.read_bytes()).hexdigest()
    correct = len(enabled) == 1 and enabled[0].get('name', '').split(':')[-1] == 'combat-director'
    cached_sha = None
    if correct:
        cached = Path(enabled[0]['path'])
        cached_sha = hashlib.sha256(cached.read_bytes()).hexdigest()
        correct = cached_sha == expected_sha and not errors
    result = {'format': 'combat-host-discovery/1', 'passed': correct,
              'scope': 'fresh metadata-only process; no conversation or media execution',
              'skills': relevant, 'target_errors': errors,
              'expected_entry_sha256': expected_sha, 'cached_entry_sha256': cached_sha}
    args.out.parent.mkdir(parents=True, exist_ok=True)
    args.out.write_text(json.dumps(result, ensure_ascii=False, indent=2)+'\n', encoding='utf-8')
    print(json.dumps({'passed': correct, 'related_enabled': len(enabled),
                      'entry_sha256_matches': cached_sha == expected_sha}, ensure_ascii=False))
    return 0 if correct else 1


if __name__ == '__main__':
    raise SystemExit(main())
