"""Local text-fixture geometry and timing checks; no biomechanical/media claim."""
import hashlib
import json
import math
import re
from decimal import Decimal as D
from pathlib import Path

from check_timing import inspect

BASE = Path(__file__).resolve().parent / 'transfer/near-miss'
answer = BASE / 'answer.md'
text = answer.read_text(encoding='utf-8')
timing = inspect(answer, D('4.6'), 9)
rows = {s['id']: s for s in timing['shots']}


def segment_distance(point, start, end):
    direction = [b-a for a, b in zip(start, end)]
    denominator = sum(d*d for d in direction)
    t = max(0, min(1, sum((p-a)*d for p, a, d in zip(point, start, direction)) / denominator)) if denominator else 0
    return math.dist(point, [a+t*d for a, d in zip(start, direction)])


def triplet(value):
    return tuple(float(v) for v in value.split(','))


shape = re.search(r'刀段两端\(([^)]+)\)/\(([^)]+)\)，A头部包络中心\(([^)]+)\)、半径([\d.]+)', rows['S04']['description'])
assert shape, 'Required geometry must come from the actual shot row'
start, end, head = [triplet(shape[i]) for i in (1, 2, 3)]
head_radius = float(shape[4])
band = re.search(r'z([\d.]+)—([\d.]+)', rows['S03']['description'])
assert band
lower, upper = map(float, band.groups())
blade_radius = (upper-lower)/2
clearance = segment_distance(head, start, end)-head_radius-blade_radius
checks = []


def check(name, passed):
    checks.append({'name': name, 'passed': bool(passed)})


check('nine_shots_timing_and_duration_ranges', timing['passed'])
check('five_fast_four_long', timing['fast_shots'] == 5 and len(rows) == 9)
check('authored_head_to_whole_blade_clearance_0_225m', math.isclose(clearance, .225, abs_tol=1e-9))
check('horizontal_sweep_above_declared_whole_body_envelope', math.isclose(lower-1.26, .225, abs_tol=1e-9))
# Synthetic negative: raising the head before the blade has passed. The tip is
# clear, while the blade middle intersects the same head sphere.
raised = (head[0], head[1], 1.45)
tip_clearance = math.dist(raised, end)-head_radius-blade_radius
middle_clearance = segment_distance(raised, start, end)-head_radius-blade_radius
check('negative_tip_only_check_would_miss_collision', tip_clearance > 0 and middle_clearance < 0)
check('negative_lowered_blade_rejects_original_low_pose',
      segment_distance(head, (start[0], start[1], 1.2), (end[0], end[1], 1.2))-head_radius-blade_radius < 0)
release = re.search(r'([\d.]+)秒前完成清空', rows['S05']['description'])
rise = re.search(r'保持低姿至([\d.]+)秒', rows['S05']['description'])
stable = re.search(r'([\d.]+)秒前稳住', rows['S05']['description'])
assert release and rise and stable
check('declared_clearance_before_rise_before_counter',
      D(release[1]) <= D(rise[1]) < D(stable[1]) <= D(rows['S06']['start']))
contact = D(re.search(r'([\d.]+)秒剑中外段真实', rows['S07']['description'])[1])
check('single_declared_contact_inside_its_shot', D(rows['S07']['start']) <= contact < D(rows['S07']['end']))
micro = [(D(a), D(b)) for a, b in re.findall(r'(\d+\.\d+)—(\d+\.\d+)秒', text.split('|镜号')[0])]
check('two_micro_intervals_and_final_contact_containment', len(micro) == 2 and
      D(0) <= micro[0][0] < micro[0][1] <= micro[1][0] <= contact < micro[1][1] <= D('4.6'))
gap = D(rows['S09']['start'])-D(rows['S01']['end'])
check('declared_read_window_gap_three_seconds', gap == D('3.0'))
result = {
    'source': str(answer), 'sha256': hashlib.sha256(answer.read_bytes()).hexdigest(),
    'scope': 'authored local blade/head primitive, declared whole-body height bound, shot timing and declared read windows only',
    'independent_review': False, 'generated_media': False,
    'clearance_m': round(clearance, 6),
    'synthetic_raised_head': {'tip_clearance_m': tip_clearance, 'whole_blade_clearance_m': middle_clearance},
    'checks': checks, 'passed': all(c['passed'] for c in checks),
}
(BASE/'timing.json').write_text(json.dumps(timing, ensure_ascii=False, indent=2)+'\n', encoding='utf-8')
(BASE/'checks.json').write_text(json.dumps(result, ensure_ascii=False, indent=2)+'\n', encoding='utf-8')
print(json.dumps(result, ensure_ascii=False))
raise SystemExit(0 if result['passed'] else 1)
