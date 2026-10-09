#!/usr/bin/env python3
"""Verify source coverage and version-bound migration evidence; never grade media."""

from __future__ import annotations

import argparse
import ast
import copy
import hashlib
import json
from pathlib import Path
import re
import sys


ROOT = Path(__file__).resolve().parents[1]
INVENTORY = 'docs/implementation/xianxia-integration-inventory.json'
COMPLETION = 'docs/implementation/xianxia-integration-completion.json'
SNAPSHOT = 'sources/upstream/xianxia-combat-skill'
TERMINAL = {'verified', 'redesigned_verified', 'historical_scope_retained_verified'}
PENDING = {'pending_current_semantic_review', 'pending_host_discovery', 'pending_release'}


def digest(data: bytes) -> str:
    return hashlib.sha256(data).hexdigest()


def read_json(path: Path):
    return json.loads(path.read_text(encoding='utf-8'))


def local_file(root: Path, name: str) -> Path:
    if not isinstance(name, str) or not name or '\\' in name or re.match(r'^[A-Za-z]:', name):
        raise ValueError(f'Expected a portable relative path: {name!r}')
    relative = Path(name)
    if relative.is_absolute() or '..' in relative.parts:
        raise ValueError(f'Path must remain inside the repository: {name}')
    result = root / relative
    if result.is_symlink() or not result.resolve().is_relative_to(root.resolve()) or not result.is_file():
        raise ValueError(f'Missing, escaping or symlinked evidence file: {name}')
    return result


def source_lines(path: Path) -> list[str]:
    # The original inventory hashes CRLF as CRLF. Text-mode universal-newline
    # conversion would make exact source slices unverifiable on Windows.
    return path.read_bytes().decode('utf-8').splitlines(keepends=True)


def span_bytes(lines: list[str], start: int, end: int) -> bytes:
    if type(start) is not int or type(end) is not int or not 1 <= start <= end <= len(lines):
        raise ValueError(f'Invalid line range {start!r}-{end!r}; file has {len(lines)} lines')
    return ''.join(lines[start - 1:end]).encode('utf-8')


def python_symbols(path: Path) -> dict[str, tuple[int, int]]:
    tree = ast.parse(path.read_bytes().decode('utf-8'))
    symbols = {}

    def visit(nodes, parents=()):
        for node in nodes:
            if isinstance(node, (ast.ClassDef, ast.FunctionDef, ast.AsyncFunctionDef)):
                name = '.'.join((*parents, node.name))
                symbols[name] = (node.lineno, node.end_lineno)
                if isinstance(node, ast.ClassDef):
                    visit(node.body, (*parents, node.name))
    visit(tree.body)
    return symbols


def canonical_digest(value) -> str:
    return digest(json.dumps(value, ensure_ascii=False, sort_keys=True,
                             separators=(',', ':')).encode('utf-8'))


def json_pointer(value, pointer: str):
    if not pointer.startswith('/'):
        raise ValueError('Review citation must use an absolute JSON pointer')
    for component in pointer[1:].split('/'):
        component = component.replace('~1', '/').replace('~0', '~')
        value = value[int(component)] if isinstance(value, list) else value[component]
    return value


def retained_spans(value) -> set[tuple]:
    """Find exact locations actually represented in a cited review record."""
    found = set()
    if isinstance(value, dict):
        if all(key in value for key in ('path', 'line_start', 'line_end', 'sha256')):
            found.add((value['path'], value['line_start'], value['line_end'], value['sha256']))
        for child in value.values():
            found.update(retained_spans(child))
    elif isinstance(value, list):
        for child in value:
            found.update(retained_spans(child))
    return found


def validate(root: Path, inventory=None, completion=None, *, full_evidence=False) -> dict:
    """Check integrity separately from unfulfilled gates; do not update status."""
    root = root.resolve()
    inventory = read_json(root / INVENTORY) if inventory is None else inventory
    completion = read_json(root / COMPLETION) if completion is None else completion
    errors, pending = [], []
    stats = {'source_files': 0, 'content_units': 0, 'features': 0,
             'source_test_methods': 0, 'target_spans': 0, 'records': 0}
    cache, records, sources = {}, {}, {}

    def fail(message):
        errors.append(message)

    def bytes_for(name):
        if name not in cache:
            path = local_file(root, name)
            data = path.read_bytes()
            cache[name] = (data, data.decode('utf-8').splitlines(keepends=True))
        return cache[name]

    def check_span(value, label, historical=False):
        try:
            data, lines = bytes_for(value['path'])
            slice_data = span_bytes(lines, value['line_start'], value['line_end'])
            if digest(data) != value['sha256']:
                if historical:
                    pending.append(f'{label}: reviewed historical target differs from current bytes')
                else:
                    fail(f'{label}: target file fingerprint changed: {value["path"]}')
            elif digest(slice_data) != value['slice_sha256_utf8']:
                fail(f'{label}: line slice fingerprint changed: {value["path"]}')
            if value.get('symbol'):
                symbol_range = python_symbols(root / value['path']).get(value['symbol'])
                if symbol_range != (value['line_start'], value['line_end']):
                    fail(f'{label}: callable no longer occupies accepted range: {value["symbol"]}')
            stats['target_spans'] += 1
        except (OSError, UnicodeError, SyntaxError, KeyError, ValueError) as exc:
            fail(f'{label}: {exc}')

    if completion.get('format') != 'combat-xianxia-integration-evidence/1':
        fail('Unexpected completion evidence format')
    if inventory.get('completion_evidence', {}).get('path') != COMPLETION:
        fail('Inventory does not bind its completion evidence file')
    elif inventory['completion_evidence'].get('sha256') != digest((root / COMPLETION).read_bytes()):
        fail('Completion evidence fingerprint differs from inventory binding')
    if inventory.get('source', {}).get('baseline_commit') != completion.get('source_commit'):
        fail('Source commit differs between inventory and evidence')
    if completion.get('media_validation') != {
        'new_video_generated': False, 'generated_motion_quality_verified': False,
        'generated_audio_quality_verified': False,
        'synthetic_media_tool_tests_are_quality_evidence': False,
    }:
        fail('Completion record must preserve the explicit media evidence boundary')

    try:
        manifest = read_json(local_file(root, SNAPSHOT + '/source-manifest.json'))
        manifest_files = {item['path']: item for item in manifest['files']}
        for item in inventory['source_files']:
            name = item['path']
            if name in sources:
                fail('Duplicate source file: ' + name)
            sources[name] = item
            actual = local_file(root, SNAPSHOT + '/' + name).read_bytes()
            if digest(actual) != item['sha256'] or len(actual) != item['bytes']:
                fail('Pinned source bytes changed: ' + name)
            if len(actual.decode('utf-8').splitlines()) != item['line_count']:
                fail('Pinned source line count changed: ' + name)
            retained = manifest_files.get(name)
            if retained is None or retained['sha256'] != item['sha256'] or retained['bytes'] != item['bytes']:
                fail('Source receipt and original inventory differ: ' + name)
            if item.get('source_snapshot_status') != 'verified':
                fail('Source snapshot has not been verified: ' + name)
        if set(manifest_files) != set(sources) or len(sources) != 70:
            fail('The 70-file source scope is not complete')
        stats['source_files'] = len(sources)
    except (OSError, UnicodeError, KeyError, ValueError) as exc:
        fail('Source manifest: ' + str(exc))

    proofs = completion.get('proofs', {})
    for key, proof in proofs.items():
        if proof.get('status') == 'pending':
            pending.append('Required proof pending: ' + key)
            continue
        if proof.get('status') != 'verified' or not proof.get('scope'):
            fail('Proof must have an explicit verified scope: ' + key)
        if not proof.get('source_report_sha256') or not proof.get('snapshot'):
            fail('Proof lacks its version-bound reviewed report snapshot: ' + key)
        origin = proof.get('source_report')
        if origin:
            try:
                path = local_file(root, origin)
            except ValueError:
                # Private reports are optional only when their reviewed values
                # are explicitly retained in this public evidence snapshot.
                if full_evidence or proof.get('origin_optional_after_snapshot') is not True:
                    fail('Proof report missing: ' + origin)
            else:
                if digest(path.read_bytes()) != proof['source_report_sha256']:
                    fail('Original proof report changed: ' + origin)
        if canonical_digest(proof.get('snapshot')) != proof.get('snapshot_sha256'):
            fail('Retained proof snapshot fingerprint changed: ' + key)
        for name, expected in proof.get('bound_files', {}).items():
            try:
                if digest(local_file(root, name).read_bytes()) != expected:
                    fail(f'{key}: reviewed implementation changed: {name}')
            except (OSError, ValueError) as exc:
                fail(f'{key}: {exc}')

    if full_evidence:
        for original in inventory.get('destination_baseline', {}).get('protected_existing_modifications', []):
            name = 'outputs/current/xianxia-integration/baseline/' + original['path']
            try:
                if digest(local_file(root, name).read_bytes()) != original['working_file_sha256']:
                    fail('Protected original working bytes changed: ' + original['path'])
            except (OSError, ValueError) as exc:
                fail('Protected original working bytes: ' + str(exc))
        for kind in ('forward_artifacts_optional_local_bindings', 'state_input_optional_local_bindings'):
            for name, expected in completion.get(kind, {}).items():
                try:
                    if digest(local_file(root, name).read_bytes()) != expected:
                        fail(f'{kind}: original local input/artifact changed: {name}')
                except (OSError, ValueError) as exc:
                    fail(f'{kind}: {exc}')
        for artifact in completion.get('retained_private_artifacts', []):
            try:
                path = local_file(root, artifact['path'])
                if digest(path.read_bytes()) != artifact['sha256'] or path.stat().st_size != artifact['bytes']:
                    fail('Historical private original changed: ' + artifact['path'])
            except (OSError, ValueError) as exc:
                fail('Historical private original: ' + str(exc))

    for record in completion.get('migration_records', []):
        key = record.get('id')
        if not key or key in records:
            fail('Missing or duplicate migration record identity: ' + str(key))
            continue
        records[key] = record
        if not record.get('decision') or not record.get('conditions_and_exceptions'):
            fail('Migration record lacks a semantic decision or conditions: ' + key)
        if not record.get('sources') or not record.get('targets'):
            fail('Archive alone is not semantic migration: ' + key)
        if record.get('status') in PENDING:
            pending.append('Migration record pending: ' + key)
        elif record.get('status') not in TERMINAL:
            fail('Unknown migration completion state: ' + key)
        for source in record.get('sources', []):
            if not source['path'].startswith(SNAPSHOT + '/'):
                # Existing Combat Director baseline preservation is a separate
                # scope and may be represented by its retained proof snapshot.
                if record.get('source_scope') != 'protected_combat_baseline':
                    fail('Migration source is not a pinned xianxia source: ' + key)
                elif full_evidence:
                    check_span(source, key + '/protected baseline source')
                continue
            check_span(source, key + '/source')
        for target in record.get('targets', []):
            check_span(target, key + '/target', record.get('status') == 'pending_current_semantic_review')
            if target['path'].startswith(('sources/', 'outputs/', 'dist/')):
                fail('Historical archive cannot be the only accepted semantic target: ' + key)
        for proof_key in record.get('proof_ids', []):
            if proof_key not in proofs:
                fail(f'{key}: missing referenced proof: {proof_key}')
            elif proofs[proof_key].get('status') == 'pending' and record.get('status') in TERMINAL:
                fail(f'{key}: terminal claim depends on a pending proof: {proof_key}')
        if not record.get('review_citations'):
            fail('Migration record has no actual reviewed evidence citation: ' + key)
        accepted_spans, admitted_implementations = set(), set()
        for citation in record.get('review_citations', []):
            try:
                proof = proofs[citation['proof_id']]
                if proof.get('status') == 'pending':
                    if record.get('status') in TERMINAL:
                        fail('Migration record falsely closes a pending review citation: ' + key)
                    continue
                reviewed = json_pointer(proof['snapshot'], citation['pointer'])
                if canonical_digest(reviewed) != citation['record_sha256']:
                    fail('Migration review citation does not match its retained record: ' + key)
                accepted_spans.update(retained_spans(reviewed))
                if isinstance(reviewed, dict):
                    admitted_implementations.update(
                        str(item).split(' ', 1)[0] for item in reviewed.get('implementation', []))
            except (KeyError, IndexError, TypeError, ValueError) as exc:
                fail(f'{key}: invalid review evidence citation: {exc}')
        for coverage_id in record.get('coverage_ids', []):
            parent_record = records.get(coverage_id)
            if parent_record is None:
                fail(f'{key}: cited semantic rule record missing: {coverage_id}')
            else:
                accepted_spans.update(retained_spans(parent_record['targets']))
        for target in record.get('targets', []):
            location = (target['path'], target['line_start'], target['line_end'], target['sha256'])
            admitted = location in accepted_spans
            if key.startswith('ENGINE-') and target.get('symbol'):
                module_symbol = Path(target['path']).stem + '.' + target['symbol']
                admitted = admitted or (module_symbol in admitted_implementations
                    and proofs.get('state_relations', {}).get('bound_files', {}).get(target['path']) == target['sha256'])
            if key.startswith('RESEARCH-') and target['path'] == 'skills/combat-director/references/sources.md':
                # Historical research is rebound by its reviewed C IDs; this
                # additional provenance table belongs to the fully read current
                # source authority, not to an archived target with a new hash.
                admitted = admitted or (proofs.get('semantic_current', {}).get('bound_files', {}).get(target['path']) == target['sha256'])
            if record.get('status') not in PENDING and not admitted:
                fail(f'{key}: target location is absent from cited semantic/code evidence: {target["path"]}:{target["line_start"]}')
    stats['records'] = len(records)

    units = inventory.get('content_units', [])
    unit_ids, partition = set(), {name: [] for name in sources}
    for unit in units:
        identity, name = unit.get('id'), unit.get('source_path')
        if not identity or identity in unit_ids:
            fail('Missing or duplicate content unit: ' + str(identity))
        unit_ids.add(identity)
        if name not in sources:
            fail('Unit references missing source file: ' + str(identity))
            continue
        partition[name].append(unit)
        try:
            data = span_bytes(source_lines(root / SNAPSHOT / name),
                              unit['source_start_line'], unit['source_end_line'])
            if digest(data) != unit['source_slice_sha256_utf8']:
                fail('Exact source slice changed: ' + identity)
        except (OSError, UnicodeError, KeyError, ValueError) as exc:
            fail(f'{identity}: {exc}')
        references = unit.get('migration_record_ids', [])
        if not references:
            fail('Source unit has no explicit semantic disposition: ' + identity)
        matched = False
        for key in references:
            if key not in records:
                fail(f'{identity}: missing migration evidence record: {key}')
                continue
            for source in records[key].get('sources', []):
                if (source['path'] == SNAPSHOT + '/' + name
                        and source['line_start'] <= unit['source_end_line']
                        and source['line_end'] >= unit['source_start_line']):
                    matched = True
        if not matched:
            fail('Unit disposition does not address its own source range: ' + identity)
        if unit.get('status') in PENDING:
            pending.append('Content unit pending: ' + identity)
        elif unit.get('status') not in TERMINAL:
            fail('Source unit still lacks an implemented disposition: ' + identity)
        if unit.get('status') in TERMINAL and any(records.get(k, {}).get('status') in PENDING for k in references):
            fail('Source unit falsely closes pending semantic evidence: ' + identity)
        if unit.get('kind') == 'test_method':
            stats['source_test_methods'] += 1
            if not unit.get('retained_test_symbols'):
                fail('Source test lacks an explicit retained/redesigned test counterpart: ' + identity)
            for target in unit.get('retained_test_symbols', []):
                check_span(target, identity + '/retained test')
    if len(units) != 508 or stats['source_test_methods'] != 45:
        fail('Original 508 source units or 45 test methods are not fully accounted for')
    for name, pieces in partition.items():
        ordered = sorted(pieces, key=lambda item: item['source_start_line'])
        cursor = 1
        for piece in ordered:
            if piece['source_start_line'] != cursor:
                fail(f'{name}: gap or overlap at {piece["id"]}; expected line {cursor}')
            cursor = piece['source_end_line'] + 1
        if cursor != sources[name]['line_count'] + 1:
            fail(name + ': units do not reach the final source line')
        if {u['id'] for u in pieces} != set(sources[name].get('content_unit_ids', [])):
            fail(name + ': file/unit index differs')
    stats['content_units'] = len(units)

    features = inventory.get('feature_families', [])
    expected_features = {f'X{i:02d}' for i in range(1, 55)}
    if {feature.get('id') for feature in features} != expected_features or len(features) != 54:
        fail('Original 54 capability groups are not complete')
    for feature in features:
        key = feature['id']
        accepted = feature.get('acceptance_evidence', [])
        if not accepted or any(record_id not in records for record_id in accepted):
            fail('Capability lacks concrete semantic migration evidence: ' + key)
        complete = accepted and all(records.get(i, {}).get('status') in TERMINAL for i in accepted)
        if feature.get('semantic_coverage_verified') is True and not complete:
            fail('Capability falsely claims pending evidence is verified: ' + key)
        if feature.get('status') in PENDING:
            pending.append('Capability pending: ' + key)
        elif feature.get('status') not in TERMINAL or not feature.get('semantic_coverage_verified'):
            fail('Capability is not implemented and reviewed: ' + key)
    stats['features'] = len(features)

    entry = inventory.get('single_entry', {})
    if (entry.get('plugin'), entry.get('skill'), entry.get('invocation')) != (
            'combat-director', 'combat-director', '$combat-director'):
        fail('Single-entry identity drift')
    if entry.get('legacy_skill_retained') is not False or entry.get('alias_skill_retained') is not False:
        fail('Legacy or alias Skill may not remain active')
    paths = sorted(p.relative_to(root).as_posix() for p in (root / 'skills').rglob('SKILL.md'))
    if paths != ['skills/combat-director/SKILL.md']:
        fail('Repository runtime does not expose exactly one Skill')
    for required in ('semantic_current', 'state_relations', 'blind_forward', 'release', 'host_discovery'):
        if required not in proofs:
            fail('Required completion gate missing: ' + required)
    if proofs.get('host_discovery', {}).get('status') == 'verified':
        host = proofs['host_discovery'].get('snapshot', {})
        if (host.get('passed') is not True or host.get('enabled_combat_entries') != 1
                or host.get('primary_name') != 'combat-director' or host.get('legacy_enabled') is not False
                or host.get('cached_entry_sha256') != digest((root / 'skills/combat-director/SKILL.md').read_bytes())):
            fail('Host proof does not establish one enabled entry matching current source')
    if inventory.get('implementation_completed'):
        if pending or errors or inventory.get('status') != 'complete':
            fail('Implementation is marked complete while integrity or required gates remain open')
    elif not pending:
        pending.append('All evidence is present; coordinator has not accepted final completion')
    return {'format': 'combat-integration-integrity-check/1', 'passed': not errors and not pending,
            'integrity_passed': not errors, 'errors': errors,
            'pending': sorted(set(pending)), 'counts': stats,
            'scope': 'Exact source/target coverage and retained version-bound evidence only; no generated-motion or audio quality claim.',
            'local_originals_required': full_evidence}


def self_test(root: Path) -> dict:
    """Inject meaningful record corruption without editing repository files."""
    inventory = read_json(root / INVENTORY)
    completion = read_json(root / COMPLETION)
    def false_completion(i, c):
        i.update(implementation_completed=True, status='complete')
        c['proofs']['host_discovery']['status'] = 'pending'

    mutations = [
        ('missing source unit', lambda i, c: i['content_units'].pop()),
        ('source slice corruption', lambda i, c: i['content_units'][0].update(source_slice_sha256_utf8='0' * 64)),
        ('unit partition overlap', lambda i, c: i['content_units'][1].update(source_start_line=2)),
        ('missing semantic counterpart', lambda i, c: i['content_units'][0].update(migration_record_ids=[])),
        ('missing target file', lambda i, c: c['migration_records'][0]['targets'][0].update(path='skills/combat-director/missing-proof.md')),
        ('invalid review citation', lambda i, c: c['migration_records'][0]['review_citations'][0].update(pointer='/missing/record')),
        ('false completion', false_completion),
    ]
    results = []
    for name, mutate in mutations:
        changed_inventory, changed_completion = copy.deepcopy(inventory), copy.deepcopy(completion)
        mutate(changed_inventory, changed_completion)
        result = validate(root, changed_inventory, changed_completion)
        results.append({'case': name, 'rejected': bool(result['errors'])})
    return {'passed': all(case['rejected'] for case in results), 'cases': results,
            'files_modified': False, 'media_reviewed': False}


def main(argv=None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--root', type=Path, default=ROOT)
    parser.add_argument('--allow-pending', action='store_true', help='Check integrity while required coordinator gates remain open')
    parser.add_argument('--full-evidence', action='store_true', help='Also require private original reports, prompt/state inputs and retained historical clips on this host')
    parser.add_argument('--self-test', action='store_true', help='Read-only corruption checks against the retained inventory')
    parser.add_argument('--report', type=Path, help='Save the integrity result; never alters the inventory or gate state')
    args = parser.parse_args(argv)
    try:
        result = self_test(args.root) if args.self_test else validate(args.root, full_evidence=args.full_evidence)
        if args.report:
            args.report.parent.mkdir(parents=True, exist_ok=True)
            args.report.write_text(json.dumps(result, ensure_ascii=False, indent=2) + '\n', encoding='utf-8')
        display = result
        if not args.self_test:
            display = {key: result[key] for key in ('passed', 'integrity_passed', 'counts', 'scope', 'local_originals_required')}
            display.update(error_count=len(result['errors']), errors=result['errors'][:20],
                           pending_count=len(result['pending']),
                           required_pending=[item for item in result['pending'] if item.startswith('Required proof pending:')])
            if args.report:
                display['report'] = str(args.report)
        print(json.dumps(display, ensure_ascii=False, indent=2))
        return 0 if result['passed'] or (args.allow_pending and result.get('integrity_passed')) else 1
    except (OSError, UnicodeError, KeyError, TypeError, ValueError) as exc:
        print('FAIL: ' + str(exc), file=sys.stderr)
        return 1


if __name__ == '__main__':
    raise SystemExit(main())
