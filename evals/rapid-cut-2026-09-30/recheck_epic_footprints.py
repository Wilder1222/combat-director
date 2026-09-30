"""Targeted regression for the authored 44-shot fixture, not a general prose validator."""
from decimal import Decimal as D
import hashlib
import json
from pathlib import Path
import re

ROOT = Path(__file__).resolve().parent
BASE = ROOT / 'revised/epic'
answer = BASE / 'answer.md'
text = answer.read_text(encoding='utf-8')
old = (BASE / 'before-footprint-repair/answer.md').read_text(encoding='utf-8')

def row(source, number):
    return next(line for line in source.splitlines() if line.startswith(f'|S{number:02} '))

def point(pattern, source):
    match = re.search(pattern + r'\(([-\d.]+),([-\d.]+)\)', source)
    if not match:
        raise ValueError(f'Missing fixture coordinates: {pattern}')
    return tuple(D(v) for v in match.groups())

# These assumptions must be visible in the copyable draft.
assert '长0.30米、宽0.24米' in text and '额外保留0.08米' in text
hx, hy, margin = D('.15'), D('.12'), D('.08')
west, east, south, north = D('3.2'), D('3.6'), D('-1.45'), D('-.95')
checks = []

def check(name, actual, expected, **evidence):
    checks.append(dict(name=name, actual=actual, expected=expected,
                       passed=actual == expected, evidence=evidence))

def overlap(p):
    x, y = p
    return (max(D(0), min(x+hx,east)-max(x-hx,west)),
            max(D(0), min(y+hy,north)-max(y-hy,south)))

def midpoint(a, b):
    return tuple((x+y)/2 for x,y in zip(a,b))

left = point('向东南撤到', row(text,25))
right = point('A右脚在', row(text,25))
mid = point('中点随之变为', row(text,25))
prior_left = point('向东南撤到', row(old,25))
dx, dy = overlap(prior_left)
check('prior_S25_overlap_under_declared_sole_assumption', dx > 0 and dy > 0, True,
      overlap_x=dx, overlap_y=dy, area=dx*dy, classification='new_assumption_exposes_prior_underspecification')
check('S25_midpoint_matches_feet', midpoint(left,right)==mid, True, midpoint=mid)
check('P10e_matches_S25', f'A({mid[0]},{mid[1]})' in text, True)
check('S25_whole_sole_and_margin', left[1]+hy+margin <= south, True,
      clearance=south-left[1]-hy, required=margin)
end_left = point('微调0.05米至', row(text,27))
end_right = point('右脚收至', row(text,27))
check('S27_midpoint_matches_P11', midpoint(end_left,end_right)==(D('4.1'),D('-1.8')),True)
# Linear axis-aligned translation: extrema occur at endpoints; no sampling approximation.
check('S27_entire_left_path_south_of_expanded_hole', max(left[1],end_left[1])+hy+margin <= south,True,
      minimum_clearance=south-max(left[1],end_left[1])-hy)
check('S27_entire_right_path_south_of_expanded_hole',max(right[1],end_right[1])+hy+margin <= south,True)
check('negative_sole_outside_but_margin_short', D('-1.60')+hy+margin <= south,False,
      classification='synthetic_negative',clearance=south-D('-1.60')-hy)
check('negative_safe_endpoints_cross_hole',
      not (west < D('3.4') < east and south < D('-1.2') < north),False,
      classification='synthetic_negative',path='(2.8,-1.2) to (4.0,-1.2), midpoint inside hole')

prior_receipt=json.loads((BASE/'before-footprint-repair/geometry.json').read_text(encoding='utf-8'))
for c in prior_receipt['checks']:
    if c['name']=='S25 A midpoint':
        c.update(actual=str(mid), expected=str(mid),passed=True)
prior_receipt.update(source=str(answer.relative_to(ROOT)),sha256=hashlib.sha256(answer.read_bytes()).hexdigest(),
                    scope='Prior manually transcribed coordinate checks plus targeted S25/S27 extraction and axis-aligned sole/path arithmetic; not whole-scene geometry, biomechanics, reach, video or independent review.',
                    footprint_checks=checks,
                    prior_answer_sha256=hashlib.sha256((BASE/'before-footprint-repair/answer.md').read_bytes()).hexdigest(),
                    passed=all(c['passed'] for c in checks+prior_receipt['checks']))
(BASE/'geometry.json').write_text(json.dumps(prior_receipt,ensure_ascii=False,indent=2,default=str)+'\n',encoding='utf-8')
print(json.dumps({'passed':prior_receipt['passed'],'new_checks':len(checks),'prior_coordinate_checks':len(prior_receipt['checks'])}))
raise SystemExit(0 if prior_receipt['passed'] else 1)
