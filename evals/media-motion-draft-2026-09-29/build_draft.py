"""Build a reviewable draft experiment. This script cannot submit generation tasks."""
from pathlib import Path
import csv
import hashlib
import json
import random

ROOT = Path(__file__).resolve().parent


def digest(data):
    return hashlib.sha256(data).hexdigest()


def main():
    source = ROOT / 'scenes.json'
    design = json.loads(source.read_text(encoding='utf-8'))
    prompts = ROOT / 'prompts'
    prompts.mkdir(exist_ok=True)
    files = []
    for scene in design['scenes']:
        for condition in ('D', 'B'):
            text = scene['base_prompt'] + ('\n'+scene['blur_addition'] if condition == 'B' else '') + '\n'
            path = prompts / (scene['id']+'-'+condition+'.txt')
            if path.exists() and path.read_text(encoding='utf-8') != text:
                raise ValueError('Draft exists with different content; create a new revision instead: '+str(path))
            path.write_text(text, encoding='utf-8')
            files.append({'scene': scene['id'], 'condition': condition, 'path': path.relative_to(ROOT).as_posix(), 'sha256': digest(path.read_bytes())})
    blocks = [(scene['id'], repeat) for scene in design['scenes'] for repeat in range(1, design['provisional_design']['repeats_per_condition']+1)]
    rng = random.Random(design['provisional_design']['order_seed'])
    rng.shuffle(blocks)
    runs = []
    for scene, repeat in blocks:
        conditions = ['D', 'B']
        rng.shuffle(conditions)
        for condition in conditions:
            prompt = next(p for p in files if p['scene'] == scene and p['condition'] == condition)
            runs.append({'run_id': f'MX{len(runs)+1:03}', 'scene': scene, 'repeat': repeat,
                         'pair_id': scene+'-'+str(repeat), 'condition': condition,
                         'prompt_path': prompt['path'], 'prompt_sha256': prompt['sha256'],
                         'status': 'not_submitted', 'seed': None, 'task_id': None,
                         'submitted_at': None, 'submitted_text': None,
                         'rewriter_status': 'unknown', 'returned_rewrite': None,
                         'original_media': None, 'original_media_sha256': None,
                         'actual_settings': None, 'error_or_refusal': None,
                         'postprocessed_versions': [], 'retry_of': None})
    manifest = {'format': 'combat-motion-media-draft-manifest/1', 'status': 'draft_not_submittable',
                'source_sha256': digest(source.read_bytes()), 'design': design['provisional_design'],
                'entry': {'platform': None, 'model': None, 'revision': None, 'entry': None, 'account_scope': None,
                          'capabilities_checked_at': None, 'capability_evidence': [], 'generation_authorization': None},
                'prompts': files, 'runs': runs,
                'review': 'Assign separate opaque review IDs only after raw media is available; withhold this manifest and prompt files from blinded reviewers.',
                'scope': 'Planned samples only. No API credentials, service calls, generated media or effect claims.'}
    target = ROOT / 'draft-manifest.json'
    if target.exists():
        old = json.loads(target.read_text(encoding='utf-8'))
        if old != manifest:
            raise ValueError('Existing manifest differs; preserve it and create a new experiment revision.')
    target.write_text(json.dumps(manifest, ensure_ascii=False, indent=2)+'\n', encoding='utf-8')
    with (ROOT / 'submission-order.csv').open('w', encoding='utf-8-sig', newline='') as f:
        writer = csv.DictWriter(f, fieldnames=['run_id', 'scene', 'repeat', 'pair_id', 'condition', 'prompt_path', 'status'])
        writer.writeheader()
        writer.writerows({k: r[k] for k in writer.fieldnames} for r in runs)
    print(json.dumps({'draft_prompts': len(files), 'planned_runs': len(runs), 'submitted': 0}, ensure_ascii=False))


if __name__ == '__main__':
    main()
