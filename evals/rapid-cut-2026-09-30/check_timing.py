"""Recompute a generated Markdown shot table; this does not judge action semantics."""
from __future__ import annotations

import argparse
from collections import Counter
from decimal import Decimal
import hashlib
import json
from pathlib import Path
import re


def inspect(path: Path, expected_duration: Decimal, expected_shots: int | None):
    text = path.read_text(encoding="utf-8")
    # Match complete table rows, never shot ranges embedded in the prose summary.
    row_pattern = re.compile(
        r"^\|[ \t]*\*{0,2}S?(\d+)\*{0,2}(?:[ \t]*[|/／][ \t]*|[ \t]+)"
        r"(\d+(?:\.\d+)?)\s*[—–−-]\s*(\d+(?:\.\d+)?)\s*(?:秒|s)?"
        r"(?:\s*[/／|，,]\s*(\d+(?:\.\d+)?)(?:秒|s)?)?\s*\|(.+)\|\s*$",
        re.M,
    )
    shots = []
    errors = []
    end = Decimal("0")
    for index, start, stop, declared, description in row_pattern.findall(text):
        index, start, stop = int(index), Decimal(start), Decimal(stop)
        duration = stop - start
        if declared and Decimal(declared) != duration:
            errors.append(f"S{index:02}: written duration {declared} differs from interval {duration}")
        if index != len(shots) + 1:
            errors.append(f"S{index:02}: unexpected or duplicate shot number")
        if start != end:
            errors.append(f"S{index:02}: time gap/overlap, previous end={end}, start={start}")
        if not (Decimal("0.2") <= duration <= Decimal("0.4") or
                Decimal("0.6") <= duration <= Decimal("1.2")):
            errors.append(f"S{index:02}: duration {duration} outside requested ranges")
        shots.append({"id": f"S{index:02}", "start": str(start), "end": str(stop),
                      "duration": str(duration), "description": description.strip()})
        end = stop
    if not shots:
        errors.append("No supported shot table found; this is not a passing result")
    if expected_shots is not None and len(shots) != expected_shots:
        errors.append(f"Expected {expected_shots} shots, found {len(shots)}")
    if end != expected_duration:
        errors.append(f"Expected duration {expected_duration}, found {end}")
    counts = Counter(Decimal(s["duration"]) for s in shots)
    return {"source": str(path), "sha256": hashlib.sha256(path.read_bytes()).hexdigest(),
            "scope": "shot_numbering_time_continuity_duration_ranges_only",
            "expected_duration": str(expected_duration), "expected_shots": expected_shots,
            "shot_count": len(shots), "duration": str(end),
            "duration_counts": {str(d): n for d, n in sorted(counts.items())},
            "fast_shots": sum(n for d, n in counts.items() if d <= Decimal("0.4")),
            "passed": not errors, "errors": errors, "shots": shots}


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("answer", type=Path)
    parser.add_argument("--expected-duration", type=Decimal, required=True)
    parser.add_argument("--expected-shots", type=int)
    parser.add_argument("--out", type=Path, required=True)
    args = parser.parse_args()
    result = inspect(args.answer, args.expected_duration, args.expected_shots)
    args.out.write_text(json.dumps(result, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    print(json.dumps({k: v for k, v in result.items() if k != "shots"}, ensure_ascii=False))
    return 0 if result["passed"] else 1


if __name__ == "__main__":
    raise SystemExit(main())
