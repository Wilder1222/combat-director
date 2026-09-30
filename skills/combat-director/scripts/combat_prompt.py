"""Bind authored compact prose to a reviewed plan; no automatic semantic rewriting."""
from __future__ import annotations

import argparse
import copy
import json
import sys
from pathlib import Path

from combat_handoff import compile_handoff, digest
from combat_schema import require

CHECKS = ('event_coverage', 'scene_camera', 'identity_ability', 'rhythm', 'constraints')
FIELDS = {'format', 'plan_id', 'source_digest', 'opening', 'sections', 'closing', 'review'}


def prepare(plan):
    return {'format': 'combat-prompt/1', 'plan_id': plan['id'],
            'source_digest': digest(compile_handoff(plan)), 'opening': '',
            'sections': [{'section_id': s['id'], 'text': ''} for s in plan['sections']],
            'closing': '', 'review': None}


def inspect(plan, projection):
    require(isinstance(projection, dict) and set(projection) == FIELDS, 'invalid compact prompt fields')
    require(projection['format'] == 'combat-prompt/1', 'unsupported compact prompt format')
    require(projection['plan_id'] == plan['id'], 'compact prompt plan_id mismatch')
    require(projection['source_digest'] == digest(compile_handoff(plan)),
            'compact prompt source is stale; reconcile against current plan')
    for key in ('opening', 'closing'):
        require(isinstance(projection[key], str) and bool(projection[key].strip()), f'compact {key} is empty')
    sections = projection['sections']
    require(isinstance(sections, list), 'compact sections must be a list')
    for section in sections:
        require(isinstance(section, dict) and set(section) == {'section_id', 'text'}, 'invalid compact section')
        require(isinstance(section['section_id'], str), 'compact section_id must be a string')
        require(isinstance(section['text'], str) and bool(section['text'].strip()), 'compact section text is empty')
    require([s['section_id'] for s in sections] == [s['id'] for s in plan['sections']],
            'compact sections must cover original sections once in order')
    expression = {k: projection[k] for k in ('opening', 'sections', 'closing')}
    return {'plan_id': plan['id'], 'source_digest': projection['source_digest'],
            'expression_digest': digest(expression), 'expression': copy.deepcopy(expression),
            'source': compile_handoff(plan), 'required_checks': list(CHECKS)}


def check_receipt(compiled, receipt):
    require(isinstance(receipt, dict) and set(receipt) == {
        'plan_id', 'source_digest', 'expression_digest', 'reviewer', 'method', 'checks'},
        'invalid compact review receipt fields')
    for key in ('plan_id', 'source_digest', 'expression_digest'):
        require(receipt[key] == compiled[key], f'compact review {key} is stale or mismatched')
    require(isinstance(receipt['reviewer'], str) and bool(receipt['reviewer'].strip()), 'compact reviewer missing')
    require(receipt['method'] in ('human', 'agent'), 'compact review method must be human or agent')
    require(isinstance(receipt['checks'], dict) and set(receipt['checks']) == set(CHECKS), 'compact review checks incomplete')
    require(all(isinstance(v, str) and bool(v.strip()) for v in receipt['checks'].values()),
            'compact checks need evidence explanations, not booleans')


def apply_review(plan, projection, receipt):
    check_receipt(inspect(plan, projection), receipt)
    result = copy.deepcopy(projection)
    result['review'] = copy.deepcopy(receipt)
    return result


def render(plan, projection):
    compiled = inspect(plan, projection)
    check_receipt(compiled, projection['review'])
    beats = {b['id']: b for b in plan['beats']}
    blocks = [projection['opening'].strip()]
    for source, section in zip(plan['sections'], projection['sections']):
        start = beats[source['beat_ids'][0]]['start']
        end = beats[source['beat_ids'][-1]]['end']
        blocks.append(f'{start:g}–{end:g}秒：{section["text"].strip()}')
    blocks.append(projection['closing'].strip())
    return '\n\n'.join(blocks) + '\n'


def main(argv=None):
    # Import here to avoid a circular dependency with the main exporter.
    from combat_tool import read_json, validate, write_artifact
    parser = argparse.ArgumentParser(description=__doc__)
    sub = parser.add_subparsers(dest='command', required=True)
    for name in ('prepare', 'compile', 'apply-review', 'validate'):
        p = sub.add_parser(name)
        p.add_argument('plan', type=Path)
        if name != 'prepare':
            p.add_argument('projection', type=Path)
        if name != 'validate':
            p.add_argument('--out', type=Path, required=True)
        if name == 'apply-review':
            p.add_argument('--receipt', type=Path, required=True)
    args = parser.parse_args(argv)
    try:
        plan = read_json(args.plan)
        validate(plan, require_review=args.command == 'validate')
        if args.command == 'prepare':
            value = prepare(plan)
        else:
            projection = read_json(args.projection)
            if args.command == 'compile':
                value = inspect(plan, projection)
            elif args.command == 'apply-review':
                value = apply_review(plan, projection, read_json(args.receipt))
            else:
                render(plan, projection)
                print('VALID compact review binding; semantics and media are not automatically verified')
                return 0
        # write_artifact never overwrites existing input or output files.
        write_artifact(value, args.out, args.plan)
        print(f'Written: {args.out}')
        return 0
    except (ValueError, OSError) as error:
        print(f'INVALID: {error}', file=sys.stderr)
        return 1


if __name__ == '__main__':
    raise SystemExit(main())
