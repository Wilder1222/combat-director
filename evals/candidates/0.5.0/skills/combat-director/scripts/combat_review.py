"""Take review and continuation seed. Acceptance never rewrites a source plan."""
from __future__ import annotations

import copy
from combat_schema import check_schema, require
from combat_handoff import compile_handoff, digest


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
    return review


def continuation_seed(review, plan, schema):
    validate_take(review, plan, schema)
    require(review['decision'] in ('accept','accept_with_deviation'), 'rejected, pending or repair take cannot seed continuity')
    return {'format':'combat-continuation/1','source_plan_id':plan['id'], 'source_plan_digest':plan_digest(plan),
            'take_id':review['take_id'],'decision':review['decision'],'evidence_kind':review['media']['evidence_kind'],
            'observation_method':review['media']['observation_method'],
            'initial_state':copy.deepcopy(review['observed_end_state']),
            'unresolved':['Do not fill unknown from planned state.'],
            'review_digest':digest(review)}


def check_continuation(next_plan, review, source_plan, schema):
    seed=continuation_seed(review,source_plan,schema)
    require(next_plan['initial_state'] == seed['initial_state'], 'next initial_state must use accepted observed state, not planned ending')
    return seed


def review_template(plan, take_id):
    return {'format':'combat-take-review/1', 'take_id':take_id, 'plan_id':plan['id'],
            'plan_digest':plan_digest(plan),
            'media':{'id':take_id,'location':'','sha256':'','evidence_kind':'unobserved',
                     'observation_method':'unobserved','covered_ranges':[],'audio_observed':False},
            'completed_events':[],'incomplete_events':[],'unexpected_events':[],
            'observed_end_state':{k:'unknown' for k in plan['initial_state']}, 'state_evidence':'',
            'deviations':[],'decision':'pending','decision_by':'','decision_reason':''}
