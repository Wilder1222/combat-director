"""Take review and continuation seed. Acceptance never rewrites a source plan."""
from __future__ import annotations

import copy
from combat_schema import check_schema, require
from combat_handoff import compile_handoff, digest
from combat_state import is_v2, profiles_for, validate_world, state_text_v2


def plan_digest(plan):
    return digest(compile_handoff(plan))


def validate_take(review, plan, schema):
    check_schema(review, schema, schema)
    require(review['plan_id'] == plan['id'], 'take review plan_id mismatch')
    require(review['plan_digest'] == plan_digest(plan), 'take review uses another plan revision')
    cast = {a['id'] for a in plan['cast']}
    require(set(review['observed_end_state']) == cast | {'environment','camera_side'}, 'observed state must include every actor and environment; use unknown for unseen facts')
    media = review['media']
    method = media['observation_method']
    if method == 'unobserved' or media['evidence_kind'] == 'unobserved':
        require(method == media['evidence_kind'] == 'unobserved' and review['decision'] == 'pending',
                'unobserved media cannot be accepted or presented as a review')
    require(not media['audio_observed'] or (method == 'full_video' and media['evidence_kind'] == 'actual_media'),
            'audio observation cannot be inferred from frames, user report or synthetic fixture')
    require((method == 'user_report') == (media['evidence_kind'] == 'user_report'), 'user report must preserve source label')
    if method not in ('user_report','unobserved'):
        require(bool(media['location'].strip()), 'media observation needs a media locator')
    elapsed=0
    for span in media['covered_ranges']:
        require(0 <= span['start'] <= span['end'] <= plan['duration'], 'observation range outside plan')
        if method == 'full_video':
            require(abs(span['start'] - elapsed) < 1e-6, 'full_video coverage has a gap/overlap')
            elapsed=span['end']
    if method == 'full_video':
        require(abs(elapsed-plan['duration']) < 1e-6, 'full_video must cover full duration')
    known = {b['id'] for b in plan['beats']} | {e['id'] for b in plan['beats'] for e in b.get('action_events',[])}
    if is_v2(plan):
        known |= set(plan['action_initial_state']['pending_events'])
    completed, incomplete = set(review['completed_events']), set(review['incomplete_events'])
    require((completed | incomplete) <= known, 'review names unknown planned event')
    require(not completed & incomplete, 'same event cannot be completed and incomplete')
    for issue in review['deviations']:
        require(0 <= issue['time'] <= plan['duration'], 'deviation timestamp outside plan')
    if review['decision'] in ('accept', 'accept_with_deviation'):
        require(bool(review['decision_by'].strip()) and bool(review['decision_reason'].strip()), 'acceptance needs attributed decision')
        require(bool(review['state_evidence'].strip()), 'accepted end state needs observation evidence')
    if review['decision'] == 'accept':
        require(not review['deviations'] and not incomplete, 'accept with deviation must be explicit')
    if review['decision'] == 'accept_with_deviation':
        require(bool(review['deviations']), 'accept_with_deviation needs recorded deviation')
    extended = is_v2(plan)
    require((review['format'] == 'combat-take-review/2') == extended,
            'review format must match legacy or extended state contract')
    if extended:
        require('observed_action_state' in review and 'action_state_evidence' in review,
                'extended review needs structured observation or explicit null unknown')
        observed = review['observed_action_state']
        if observed is not None:
            require(method != 'unobserved' and bool(review['action_state_evidence'].strip()),
                    'structured observation needs actual attributed evidence')
            from pathlib import Path
            import json
            action_schema = json.loads((Path(__file__).resolve().parents[1] / 'assets/combat-plan.schema.json').read_text(encoding='utf-8'))
            weapons = {w['id']: w for w in plan['weapon_profiles']}
            profiles = profiles_for(plan)
            validate_world(observed, profiles, weapons, {a['id']: a for a in plan['abilities']}, action_schema)
            for pending_id, pending in observed['pending_events'].items():
                references = {pending_id, pending['source_event_id']}
                require(not (pending['phase'] == 'pending' and references & completed),
                        'completed event contradicts observed pending state')
                require(not (pending['phase'] == 'completed' and references & incomplete),
                        'incomplete event contradicts observed completed state')
            require(review['observed_end_state'] == state_text_v2(observed, weapons, review['observed_end_state']['camera_side'], profiles),
                    'observed text must project the observed structured state')
    else:
        require('observed_action_state' not in review and 'action_state_evidence' not in review,
                'legacy review cannot silently add structured observation')
    return review


def continuation_seed(review, plan, schema):
    validate_take(review, plan, schema)
    require(review['decision'] in ('accept','accept_with_deviation'), 'rejected, pending or repair take cannot seed continuity')
    seed = {'format':'combat-continuation/2' if is_v2(plan) else 'combat-continuation/1',
            'source_plan_id':plan['id'], 'source_plan_digest':plan_digest(plan),
            'take_id':review['take_id'],'decision':review['decision'],'evidence_kind':review['media']['evidence_kind'],
            'observation_method':review['media']['observation_method'],
            'initial_state':copy.deepcopy(review['observed_end_state']),
            'unresolved':['Do not fill unknown from planned state.'],
            'review_digest':digest(review)}
    if is_v2(plan):
        seed['action_initial_state'] = copy.deepcopy(review['observed_action_state'])
        seed['body_profiles'] = copy.deepcopy(list(profiles_for(plan).values()))
        seed['incomplete_events'] = copy.deepcopy(review['incomplete_events'])
        seed['action_state_evidence'] = review['action_state_evidence']
        if seed['action_initial_state'] is None:
            seed['unresolved'].append('Structured end state is unknown; do not copy planned state into continuation.')
    return seed


def check_continuation(next_plan, review, source_plan, schema):
    seed=continuation_seed(review,source_plan,schema)
    require(next_plan['initial_state'] == seed['initial_state'], 'next initial_state must use accepted observed state, not planned ending')
    if is_v2(next_plan):
        require(seed.get('action_initial_state') is not None, 'structured observation unknown; cannot invent next action state')
        require(next_plan['action_initial_state'] == seed['action_initial_state'],
                'next action_initial_state must use observed items, bodies, contacts, effects, formations and pending events')
        require(profiles_for(next_plan) == {p['id']: p for p in seed['body_profiles']}, 'next body identities differ from observed identities')
    return seed


def review_template(plan, take_id):
    template = {'format':'combat-take-review/2' if is_v2(plan) else 'combat-take-review/1', 'take_id':take_id, 'plan_id':plan['id'],
            'plan_digest':plan_digest(plan),
            'media':{'id':take_id,'location':'','sha256':'','evidence_kind':'unobserved',
                     'observation_method':'unobserved','covered_ranges':[],'audio_observed':False},
            'completed_events':[],'incomplete_events':[],'unexpected_events':[],
            'observed_end_state':{k:'unknown' for k in plan['initial_state']}, 'state_evidence':'',
            'deviations':[],'decision':'pending','decision_by':'','decision_reason':''}
    if is_v2(plan):
        template.update(observed_action_state=None, action_state_evidence='')
    return template
