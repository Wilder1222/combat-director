"""Summarize actual CLI events, including failures and exact decoded source reads."""
from pathlib import Path
import hashlib
import json
import zipfile

ROOT = Path(__file__).resolve().parents[2]
RESULTS = ROOT / 'evals/results/host-0.9.1'


def sha(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


def main():
    rows = []
    with zipfile.ZipFile(ROOT / 'dist/combat-director-0.9.1.zip') as archive:
        expected = {p: archive.read(p) for p in archive.namelist() if p.startswith('skills/') and not p.endswith('/')}
        for run in sorted(RESULTS.iterdir()):
            if not run.is_dir():
                continue
            metadata = json.loads((run / 'run.json').read_text(encoding='utf-8'))
            if metadata['status'] != 'terminal':
                raise ValueError('Unfinished run: ' + run.name)
            project = Path(metadata['cwd'])
            drift = [name for name, content in expected.items() if (project / '.agents' / name).read_bytes() != content]
            events = [json.loads(line) for line in (run / 'events.jsonl').read_text(encoding='utf-8').splitlines()]
            commands, decoded_matches, messages, usage = [], [], [], None
            skill = Path(metadata['candidate_skill'])
            motion_text = (skill.parent / 'references/motion-blur.md').read_text(encoding='utf-8')
            skill_text = skill.read_text(encoding='utf-8')
            for event in events:
                item = event.get('item', {})
                if event['type'] == 'turn.completed':
                    usage = event.get('usage')
                if event['type'] != 'item.completed':
                    continue
                if item.get('type') == 'agent_message':
                    messages.append(item.get('text', ''))
                if item.get('type') == 'command_execution':
                    output = item.get('aggregated_output', '')
                    commands.append({'item_id': item['id'], 'command': item['command'],
                                     'exit_code': item.get('exit_code'), 'replacement_characters': output.count('\ufffd')})
                    if item.get('exit_code') != 0:
                        continue
                    for line in output.splitlines():
                        try:
                            decoded = json.loads(line)
                        except ValueError:
                            continue
                        for label, text in [('SKILL.md', skill_text), ('references/motion-blur.md', motion_text)]:
                            if decoded == text or isinstance(decoded, dict) and decoded.get(label) == text:
                                decoded_matches.append({'item_id': item['id'], 'file': label, 'normalized_text_exact_match': True})
            answer = (run / 'answer.md').read_text(encoding='utf-8').strip() if (run / 'answer.md').is_file() else None
            rows.append({'run_id': run.name, 'case_id': metadata['case']['id'], 'exit_code': metadata['exit_code'],
                         'cli_version': metadata['cli_version'], 'catalog': metadata['catalog'],
                         'candidate_files_checked': len(expected), 'candidate_drift': drift,
                         'commands': commands, 'decoded_source_matches': decoded_matches,
                         'answer': answer, 'answer_characters': len(answer) if answer else None,
                         'messages': messages, 'usage': usage, 'elapsed_seconds': metadata['elapsed_seconds'],
                         'evidence_files': [{'path': p.relative_to(RESULTS).as_posix(), 'sha256': sha(p)} for p in sorted(run.iterdir()) if p.is_file()]})
    report = {'format': 'combat-host-routing-summary/1', 'date': '2026-09-29', 'runs': rows,
              'selected_final_runs': ['H01-attempt4', 'H02-attempt4', 'H03'],
              'prior_attempts': 'Preserved model incompatibility, sandbox access/working-directory failures, same-name plugin fallback, and text-decoding failures. They are not candidate passes.',
              'conditions': 'Final runs use bundled CLI 0.154.0-alpha.6.2, inherited model settings, read-only unelevated Windows sandbox, plugin discovery disabled for this invocation, and an isolated project directory inheriting the existing temporary-root ACL.',
              'limits': ['No change to ordinary installed plugin version.', 'Final output alone is not source-loading evidence.',
                         'No general routing success rate, all-host compatibility, media quality, or performance comparison.']}
    (RESULTS / 'summary.json').write_text(json.dumps(report, ensure_ascii=False, indent=2)+'\n', encoding='utf-8')
    print(json.dumps([{'run': r['run_id'], 'exit': r['exit_code'], 'characters': r['answer_characters'], 'decoded_matches': r['decoded_source_matches'], 'drift': r['candidate_drift']} for r in rows], ensure_ascii=False))


if __name__ == '__main__':
    main()
