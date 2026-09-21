"""Offline capability/asset evidence checks; never queries a provider."""
from __future__ import annotations

from datetime import date
import math
import re
from combat_schema import require


def iso_day(value, label):
    try:
        return date.fromisoformat(value)
    except (ValueError, TypeError):
        raise ValueError(f'{label}: expected ISO date YYYY-MM-DD') from None


def assess_profile(plan, profile, as_of=None):
    require(isinstance(profile, dict), 'profile must be an object')
    today = date.today() if as_of is None else iso_day(as_of, 'as_of')
    unknown, conflicts = [], []
    for key in ('platform', 'model', 'entry', 'mode', 'account_scope'):
        require(isinstance(profile.get(key), str), f'profile.{key}: text required')
        if not profile[key].strip():
            unknown.append(f'{key}未核验')
    claims = profile.get('claims')
    require(isinstance(claims, dict), 'profile.claims required')
    needed = {'max_duration'}
    kinds = {r['kind'] for r in plan['references']}
    if 'first-frame' in kinds:
        needed.add('first_frame')
    if 'last-frame' in kinds:
        needed.add('last_frame')
    if any(r.get('asset', {}).get('media_type') == 'video' for r in plan['references']):
        needed.add('video_reference')
    for name in needed:
        claim = claims.get(name, {'status': 'unknown'})
        require(isinstance(claim, dict) and claim.get('status') in ('supported','unsupported','unknown'), f'{name}: invalid capability status')
        if claim['status'] == 'unknown':
            unknown.append(f'{name}未知')
            continue
        for field in ('source', 'scope', 'checked_at', 'expires_at'):
            require(isinstance(claim.get(field), str) and bool(claim[field].strip()), f'{name}: missing {field}')
        checked, expires = iso_day(claim['checked_at'], name), iso_day(claim['expires_at'], name)
        require(expires >= checked, f'{name}: expiry precedes check')
        if checked > today or expires < today:
            unknown.append(f'{name}证据不在有效日期内')
            continue
        if claim['status'] == 'unsupported':
            conflicts.append(f'{name}在该入口不支持')
        elif name == 'max_duration':
            value = claim.get('value')
            require(type(value) in (float,int) and math.isfinite(value) and value > 0, 'max_duration needs positive finite value')
            if plan['duration'] > value:
                conflicts.append(f'目标{plan["duration"]:g}秒超过已记录上限{value:g}秒')
    if profile['mode'] and profile['mode'] != plan['generation']:
        conflicts.append('配置生成模式与计划不一致')
    return {'status':'conflict' if conflicts else 'needs_verification' if unknown else 'compatible',
            'as_of':today.isoformat(),'conflicts':conflicts,'unknown':unknown,
            'evidence_scope':'仅检查所提供记录；没有查询平台或验证账号'}


def validate_reference(ref):
    if ref['status'] == 'planned':
        return
    asset = ref.get('asset')
    require(isinstance(asset, dict), f'{ref["id"]}: available/bound reference needs asset identity')
    require(bool(asset['id'].strip()) and bool(asset['location'].strip()), f'{ref["id"]}: incomplete asset identity')
    require(not asset['sha256'] or re.fullmatch('[a-f0-9]{64}',asset['sha256']), f'{ref["id"]}: invalid asset hash')
    if ref['status'] != 'bound':
        return
    binding = ref.get('binding')
    require(isinstance(binding, dict), f'{ref["id"]}: bound status needs binding receipt, not prose alone')
    require(binding['asset_id'] == asset['id'], f'{ref["id"]}: binding asset mismatch')
    require(all(binding[k].strip() for k in ('platform','model','entry','task_id','receipt')), f'{ref["id"]}: incomplete binding receipt')
    iso_day(binding['checked_at'], 'binding.checked_at')
    # A structured receipt still has a source; user statements are never promoted to tool verification.
    require(binding['verification'] in ('user_reported','tool_reported'), f'{ref["id"]}: missing verification source')
