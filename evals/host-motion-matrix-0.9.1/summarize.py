"""Audit terminal runs and readable source evidence without grading prose by keywords."""
from pathlib import Path
import hashlib
import json
import zipfile

ROOT = Path(__file__).resolve().parents[2]
RESULTS = ROOT / 'evals/results/host-motion-matrix-0.9.1'


def sha(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


def strings(value):
    if isinstance(value, str):
        yield value
    elif isinstance(value, dict):
        for item in value.values():
            yield from strings(item)
    elif isinstance(value, list):
        for item in value:
            yield from strings(item)


def main(authority=None, results=None, archive=None):
    authority = authority or Path(__file__).with_name('cases.json')
    results = results or RESULTS
    cases = json.loads(authority.read_text(encoding='utf-8'))['cases']
    archive = archive or ROOT / 'dist/combat-director-0.9.1.zip'
    with zipfile.ZipFile(archive) as z:
        expected = {n: z.read(n) for n in z.namelist() if n.startswith('skills/') and not n.endswith('/')}
    rows = []
    for case in cases:
        directory = results / case['id']
        run = json.loads((directory / 'run.json').read_text(encoding='utf-8'))
        if run['status'] != 'terminal':
            raise ValueError('Still active: ' + case['id'])
        if run['case'] != case:
            raise ValueError('Request changed: ' + case['id'])
        request = (directory / 'request.txt').read_text(encoding='utf-8')
        if request != case['request'] + '\n':
            raise ValueError('Submitted request drift: ' + case['id'])
        project = Path(run['cwd'])
        drift = [n for n, content in expected.items() if (project / '.agents' / n).read_bytes() != content]
        sources = {n.removeprefix('skills/combat-director/'): b.decode('utf-8').replace('\r\n', '\n')
                   for n, b in expected.items() if n.endswith('.md')}
        commands, matches, messages, usage = [], [], [], None
        for line in (directory / 'events.jsonl').read_text(encoding='utf-8').splitlines():
            event = json.loads(line)
            if event['type'] == 'turn.completed':
                usage = event.get('usage')
            if event['type'] != 'item.completed':
                continue
            item = event.get('item', {})
            if item.get('type') == 'agent_message':
                messages.append(item.get('text', ''))
            if item.get('type') != 'command_execution':
                continue
            output = item.get('aggregated_output', '')
            commands.append({'item_id': item['id'], 'command': item['command'], 'exit_code': item.get('exit_code'),
                             'replacement_characters': output.count('\ufffd')})
            if item.get('exit_code') != 0:
                continue
            decoded = []
            for part in output.splitlines():
                try:
                    decoded.extend(strings(json.loads(part)))
                except ValueError:
                    pass
            for name, source in sources.items():
                method = ('decoded_json' if any(s.replace('\r\n', '\n') == source for s in decoded)
                          else 'plain_complete_text' if source in output.replace('\r\n', '\n') else None)
                if method:
                    matches.append({'item_id': item['id'], 'source': name, 'method': method,
                                    'normalized_complete_text_match': True})
        answer_path = directory / 'answer.md'
        answer = answer_path.read_text(encoding='utf-8').strip() if answer_path.exists() else None
        low, high = (200, 360) if case['length'] == 'normal' else (1, 160)
        artifact_errors = [a['path'] for a in run['artifacts'] if sha(directory / a['path']) != a['sha256']]
        rows.append({'id': case['id'], 'family': case['family'], 'length': case['length'],
                     'exit_code': run['exit_code'], 'candidate_files_checked': len(expected), 'candidate_drift': drift,
                     'artifact_hash_errors': artifact_errors, 'commands': commands, 'source_matches': matches,
                     'answer': answer, 'answer_characters': len(answer) if answer else None,
                     'length_within_requested_range': bool(answer and low <= len(answer) <= high),
                     'messages': messages, 'usage': usage, 'elapsed_seconds': run['elapsed_seconds'],
                     'files': [{'path': p.relative_to(results).as_posix(), 'sha256': sha(p)}
                               for p in sorted(directory.iterdir()) if p.is_file()]})
    report = {'format': 'combat-host-motion-matrix-audit/1', 'date': '2026-09-29',
              'request_authority_sha256': sha(authority), 'archive_sha256': sha(archive), 'runs': rows,
              'limits': 'Single invocation per cell. Complete-text matches establish readable source content in command output; unmatched files may still have partial reads. Semantic review is separate. No media generated.'}
    target = results / 'audit.json'
    if target.exists():
        raise ValueError('Preserve existing audit; make a new revision instead.')
    target.write_text(json.dumps(report, ensure_ascii=False, indent=2)+'\n', encoding='utf-8')
    print(json.dumps([{'id': r['id'], 'exit_code': r['exit_code'], 'characters': r['answer_characters'],
                       'sources': sorted({m['source'] for m in r['source_matches']}),
                       'drift': r['candidate_drift'], 'hash_errors': r['artifact_hash_errors']} for r in rows], ensure_ascii=False))


if __name__ == '__main__':
    main()
