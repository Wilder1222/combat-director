"""Check declared event coverage and time windows in a Markdown shot table.

This is an evaluation helper, not a Combat Plan schema extension or a video judge.
Time/shot parsing is shared with check_timing.py. See sequence-checks.md for markers.
"""
from __future__ import annotations

import argparse
from collections import defaultdict
from decimal import Decimal as D
import json
from pathlib import Path
import re

from check_timing import inspect

NUMBER = r"\d+(?:\.\d+)?"
SPAN = rf"({NUMBER})[—–-]({NUMBER})"
ROLE = re.compile(r"\b(E\d+)/(来路|命中点|避让点|反馈)(?=\s|\|)")


def inspect_sequence(path: Path, duration: D, shot_count: int):
    timing = inspect(path, duration, shot_count)
    errors = list(timing["errors"])
    source = path.read_text(encoding="utf-8")
    shots = timing["shots"]
    events = defaultdict(list)
    contacts = []
    windows = []

    for shot in shots:
        label = shot["id"]
        start, end = D(shot["start"]), D(shot["end"])
        desc = shot["description"]
        roles = ROLE.findall(desc)
        if len(roles) > 1 or (re.search(r"\bE\d+/", desc) and not roles):
            errors.append(f"{label}: unsupported or ambiguous event role")
        event, role = roles[0] if len(roles) == 1 else (None, None)
        if event:
            events[event].append((label, role))
        points = re.findall(rf"首触\s+({NUMBER})(?=\s|；|;|\|)", desc)
        stops = re.findall(rf"Hit Stop\s+{SPAN}", desc)
        if role == "命中点":
            if len(points) != 1 or len(stops) != 1:
                errors.append(f"{label}: contact needs exactly one first touch and Hit Stop")
        elif points or stops or "首触" in desc or "Hit Stop" in desc:
            errors.append(f"{label}: contact marker outside a contact shot")
        for point in points:
            t = D(point)
            if not start <= t < end:
                errors.append(f"{label}: first touch outside shot")
            contacts.append({"event": event, "shot": label, "time": str(t)})
        for left, right in stops:
            a, b = D(left), D(right)
            if not start <= a < b <= end or b - a >= end - start:
                errors.append(f"{label}: Hit Stop outside shot or freezes whole shot")
            if len(points) == 1 and a != D(points[0]):
                errors.append(f"{label}: Hit Stop must start at declared first touch")
        reads = re.findall(rf"读位\s+{SPAN}", desc)
        if "读位" in desc and not reads and "读位" in desc.split("|")[-1]:
            errors.append(f"{label}: unsupported read-window marker")
        for left, right in reads:
            a, b = D(left), D(right)
            if not start <= a < b <= end:
                errors.append(f"{label}: read window outside shot or empty")
            else:
                windows.append({"shot": label, "start": str(a), "end": str(b)})

    if not events:
        errors.append("No event roles found; unsupported/missing evidence is not a pass")
    for event, rows in events.items():
        roles = [role for _, role in rows]
        if roles not in (["来路", "命中点", "反馈"], ["来路", "避让点", "反馈"]):
            errors.append(f"{event}: expected exactly one approach/contact-or-miss/feedback chain")
        indices = [int(label[1:]) for label, _ in rows]
        if any(b != a + 1 for a, b in zip(indices, indices[1:])):
            errors.append(f"{event}: three-shot chain is not consecutive")

    if not windows:
        errors.append("No readable-space windows declared")
    cursor = D(0)
    gaps = []
    for window in sorted(windows, key=lambda w: D(w["start"])):
        a, b = D(window["start"]), D(window["end"])
        gaps.append(max(D(0), a - cursor))
        cursor = max(cursor, b)
    gaps.append(max(D(0), duration - cursor))
    max_gap = max(gaps)
    if max_gap > D(5):
        errors.append(f"Space unreadable for {max_gap}s, exceeding 5s (includes head/tail)")

    micros = re.findall(rf"^微慢\s+(\S+)\s+{SPAN}\s*$", source, re.M)
    if len(re.findall(r"^微慢\s+", source, re.M)) != len(micros):
        errors.append("Unsupported micro-slow marker")
    if len(micros) != 2 or {name for name, _, _ in micros} != {"开场", "终局"}:
        errors.append("Exactly two labeled micro-slow windows required: 开场 and 终局")
    prior_end = D(0)
    for name, left, right in micros:
        a, b = D(left), D(right)
        if not prior_end <= a < b <= duration:
            errors.append(f"{name}: invalid/overlapping micro-slow window")
        prior_end = b
    if len(micros) == 2 and [m[0] for m in micros] != ["开场", "终局"]:
        errors.append("Micro-slow labels must follow opening then finale")

    phases = re.findall(rf"^节奏段\s+(\S+)\s+{SPAN}\s*$", source, re.M)
    if len(re.findall(r"^节奏段\s+", source, re.M)) != len(phases):
        errors.append("Unsupported rhythm-phase marker")
    if not phases:
        errors.append("No rhythm phases declared")
    phase_stats = []
    cursor = D(0)
    boundaries = {D(s["start"]) for s in shots} | {D(s["end"]) for s in shots}
    for name, left, right in phases:
        a, b = D(left), D(right)
        if a != cursor or b <= a or a not in boundaries or b not in boundaries:
            errors.append(f"{name}: phases must tile duration at shot boundaries")
        cursor = b
        contained = [s for s in shots if a <= D(s["start"]) and D(s["end"]) <= b]
        phase_stats.append({
            "name": name, "start": left, "end": right, "shots": len(contained),
            "fast_shots": sum(D(s["duration"]) <= D("0.4") for s in contained),
            "shots_per_second": str((D(len(contained)) / (b-a)).quantize(D("0.001"))) if b > a else None,
            "new_contacts": [c for c in contacts if a <= D(c["time"]) < b],
        })
    if cursor != duration:
        errors.append("Rhythm phases do not cover full duration")

    contact_gaps = [str(D(b["time"]) - D(a["time"])) for a, b in zip(contacts, contacts[1:])]
    return {
        "source": str(path), "sha256": timing["sha256"],
        "scope": "declared_text_timing_event_mapping_and_read_windows_only",
        "not_verified": ["unwritten_events", "spatial_axis", "reach_and_collision", "readability", "video_and_audio"],
        "passed": not errors, "errors": errors,
        "shot_count": timing["shot_count"], "duration": timing["duration"],
        "fast_shots": timing["fast_shots"], "long_shots": timing["shot_count"] - timing["fast_shots"],
        "duration_counts": timing["duration_counts"],
        "events": dict(events), "contacts": contacts, "contact_gaps": contact_gaps,
        "read_windows": windows, "max_unreadable_gap": str(max_gap),
        "micro_slow_windows": micros, "phases": phase_stats,
    }


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("answer", type=Path)
    parser.add_argument("--expected-duration", type=D, required=True)
    parser.add_argument("--expected-shots", type=int, required=True)
    parser.add_argument("--out", type=Path, required=True)
    args = parser.parse_args()
    result = inspect_sequence(args.answer, args.expected_duration, args.expected_shots)
    args.out.parent.mkdir(parents=True, exist_ok=True)
    args.out.write_text(json.dumps(result, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    print(json.dumps({k: result[k] for k in ("passed", "shot_count", "duration", "fast_shots", "max_unreadable_gap", "errors")}, ensure_ascii=False))
    return 0 if result["passed"] else 1


if __name__ == "__main__":
    raise SystemExit(main())
