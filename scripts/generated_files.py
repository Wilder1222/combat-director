"""Manage only recorded Arvin outputs, with staged writes and recovery.

The ownership manifest is outside the runtime package. Unknown or manually
edited files are never adopted, overwritten or retired automatically.
"""
from __future__ import annotations

import hashlib
import json
import os
import re
import shutil
import tempfile
from pathlib import Path, PurePosixPath

MANIFEST = 'sources/editorial/arvin-generated.json'
LOCK = 'sources/editorial/.arvin-generated.lock'
SPECIAL = {'skills/combat-director/library/catalog.json',
           'skills/combat-director/library/items.json',
           'skills/combat-director/library/index.md',
           'docs/implementation/arvin-library-coverage.json'}
CARD = re.compile(r'skills/combat-director/library/(?:techniques|characters|choreography|camera|effects|styles|scenes)/arvin-[a-z0-9-]+\.md')
NAV = re.compile(r'skills/combat-director/library/(?:design|abilities|techniques|characters|choreography|camera|effects|styles|scenes)/index\.md')


def digest(data):
    return hashlib.sha256(data).hexdigest()


def json_bytes(data):
    return (json.dumps(data, ensure_ascii=False, indent=2)+'\n').encode('utf-8')


def safe_path(root, name, *, internal=False):
    if not isinstance(name, str):
        raise ValueError('Invalid managed path: '+str(name))
    relative = PurePosixPath(name)
    if relative.as_posix() != name or relative.is_absolute() or '..' in relative.parts:
        raise ValueError('Invalid managed path: '+str(name))
    if not (name in SPECIAL or CARD.fullmatch(name) or NAV.fullmatch(name) or internal and name in (MANIFEST, LOCK)):
        raise ValueError('Path is not generator-owned: '+name)
    root = Path(root).resolve()
    path = root.joinpath(*relative.parts)
    if path.resolve() != path or not path.resolve().is_relative_to(root):
        raise ValueError('Linked or escaping managed path: '+name)
    if any(p.is_symlink() for p in (path, *path.parents)):
        raise ValueError('Symlink in managed path: '+name)
    if path.exists() and not path.is_file():
        raise ValueError('Managed path is not a regular file: '+name)
    return path


def file_bytes(path):
    return path.read_bytes() if path.exists() else None


def owned_files(root):
    path = safe_path(root, MANIFEST, internal=True)
    if not path.exists():
        return {}
    data = json.loads(path.read_text(encoding='utf-8'))
    if not isinstance(data, dict) or set(data) != {'version','generator','files'} or type(data['version']) is not int or data['version'] != 1 or data['generator'] != 'arvin-library' or not isinstance(data['files'], dict):
        raise ValueError('Invalid generated ownership manifest')
    for name, sha in data['files'].items():
        safe_path(root, name)
        if not isinstance(sha, str) or not re.fullmatch(r'[a-f0-9]{64}', sha):
            raise ValueError('Invalid managed hash: '+name)
    return data['files']


def desired_bytes(root, outputs):
    desired = {}
    for name, content in outputs.items():
        safe_path(root, name)
        if not isinstance(content, str) or not content:
            raise ValueError('Empty generated output: '+name)
        desired[name] = content.encode('utf-8')
    manifest = {'version':1, 'generator':'arvin-library',
                'files':{n:digest(desired[n]) for n in sorted(desired)}}
    desired[MANIFEST] = json_bytes(manifest)
    return desired


def unlocked(root):
    if safe_path(root, LOCK, internal=True).exists():
        raise ValueError('Generated update is pending; inspect or run build_arvin_library.py --recover')


def plan(root, outputs):
    """Preflight everything; return a read-only change plan and original bytes."""
    root = Path(root).resolve()
    unlocked(root)
    old = owned_files(root)
    desired = desired_bytes(root, outputs)
    actual_cards = {p.relative_to(root).as_posix() for p in (root/'skills/combat-director/library').glob('*/arvin-*.md')}
    unknown = actual_cards - set(old) - set(outputs)
    if unknown:
        raise ValueError('Unmanaged generated-looking files; preserve and review: '+', '.join(sorted(unknown)))
    before = {}
    for name in sorted(set(old) | set(desired)):
        value = file_bytes(safe_path(root, name, internal=True))
        before[name] = value
        if name == MANIFEST:
            continue
        if name in old:
            if value is not None and digest(value) != old[name]:
                raise ValueError('Manually modified generated output; preserve and review: '+name)
        elif value is not None:
            raise ValueError('Unowned output already exists; preserve and review: '+name)
    changes = {'create':[], 'update':[], 'retire':[]}
    for name in sorted(before):
        value = desired.get(name)
        if value == before[name]:
            continue
        kind = 'retire' if value is None else 'create' if before[name] is None else 'update'
        changes[kind].append(name)
    return changes, before, desired


def check(root, outputs):
    changes, _, _ = plan(root, outputs)
    stale = [name for group in changes.values() for name in group]
    if stale:
        raise ValueError('Generated library out of sync: '+', '.join(stale[:12]))


def stage_path(root, path):
    base = safe_path(root, MANIFEST, internal=True).parent
    path = Path(path)
    if path.parent != base or not path.name.startswith('.arvin-stage-') or path.resolve() != path or path.is_symlink():
        raise ValueError('Invalid generated recovery directory')
    return path


def remove_stage(root, stage):
    stage = stage_path(root, stage)
    # The resolved recursive-delete target is verified inside sources/editorial.
    if stage.exists():
        shutil.rmtree(stage)


def restore(root, stage):
    """Validate the whole journal before restoring; keep backups for retries."""
    stage = stage_path(root, stage)
    journal = json.loads((stage/'journal.json').read_text(encoding='utf-8'))
    prepared = []
    for row in journal:
        name = row['path']
        path = safe_path(root, name, internal=True)
        if name == LOCK:
            raise ValueError('Lock cannot be a generated output')
        current = file_bytes(path)
        current_sha = digest(current) if current is not None else None
        if current_sha not in (row['before'], row['after']):
            raise ValueError('Recovery would overwrite a later edit: '+name)
        data = None
        if row['before'] is not None:
            backup = stage/'backup'/name
            if backup.resolve() != backup or not backup.resolve().is_relative_to(stage):
                raise ValueError('Invalid recovery backup: '+name)
            data = backup.read_bytes()
            if digest(data) != row['before']:
                raise ValueError('Recovery backup hash mismatch: '+name)
        prepared.append((path, current, data))
    for i, (path, current, data) in enumerate(prepared):
        if current == data:
            continue
        if data is None:
            path.unlink()
        else:
            candidate = stage/f'restore-{i}'
            candidate.write_bytes(data)
            path.parent.mkdir(parents=True, exist_ok=True)
            os.replace(candidate, path)


def recover(root):
    root = Path(root).resolve()
    lock = safe_path(root, LOCK, internal=True)
    if not lock.exists():
        raise ValueError('No pending generated update')
    record = json.loads(lock.read_text(encoding='utf-8'))
    stage = stage_path(root, root/record['stage'])
    restore(root, stage)
    lock.unlink()
    remove_stage(root, stage)


def apply(root, outputs):
    """Stage first, commit per-file, and roll back on an ordinary I/O failure."""
    root = Path(root).resolve()
    changes, before, desired = plan(root, outputs)
    names = [n for group in changes.values() for n in group]
    if not names:
        return changes
    base = safe_path(root, MANIFEST, internal=True).parent
    base.mkdir(parents=True, exist_ok=True)
    stage = stage_path(root, Path(tempfile.mkdtemp(prefix='.arvin-stage-', dir=base)))
    lock = safe_path(root, LOCK, internal=True)
    acquired = False
    started = False
    keep_recovery = False
    try:
        journal = []
        for name in names:
            old, new = before[name], desired.get(name)
            journal.append({'path':name, 'before':digest(old) if old is not None else None,
                            'after':digest(new) if new is not None else None})
            for folder, value in (('backup', old), ('new', new)):
                if value is not None:
                    path = stage/folder/name
                    path.parent.mkdir(parents=True, exist_ok=True)
                    path.write_bytes(value)
                    if path.read_bytes() != value:
                        raise OSError('Staged bytes differ: '+name)
        (stage/'journal.json').write_bytes(json_bytes(journal))
        with lock.open('x', encoding='utf-8') as handle:
            acquired = True
            handle.write(json_bytes({'stage':stage.relative_to(root).as_posix()}).decode('utf-8'))
        for name, value in before.items():
            if file_bytes(safe_path(root, name, internal=True)) != value:
                raise ValueError('Output changed during generation: '+name)
        # Install the ownership manifest last; old hashes remain until commit.
        for name in sorted(names, key=lambda n:(n == MANIFEST, n)):
            target = safe_path(root, name, internal=True)
            started = True
            if name in desired:
                target.parent.mkdir(parents=True, exist_ok=True)
                os.replace(stage/'new'/name, target)
            else:
                target.unlink()
        for name in names:
            if file_bytes(safe_path(root, name, internal=True)) != desired.get(name):
                raise OSError('Installed bytes differ: '+name)
    except Exception as error:
        if started:
            try:
                restore(root, stage)
            except Exception as recovery_error:
                keep_recovery = True
                raise OSError(f'Update failed: {error}; recovery pending: {stage}; run --recover. {recovery_error}') from error
        raise
    except BaseException:
        # Interrupts retain the journal/lock for explicit recovery.
        keep_recovery = acquired
        raise
    finally:
        if not keep_recovery:
            if acquired:
                lock.unlink()
            remove_stage(root, stage)
    return changes
