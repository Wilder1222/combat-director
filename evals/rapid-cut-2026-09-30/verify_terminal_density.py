"""Verify timing facts in the terminal-density text probe, not rendered motion."""
from decimal import Decimal as D
import hashlib
import json
from pathlib import Path
import re

from check_timing import inspect

BASE = Path(__file__).resolve().parent
TARGET = BASE / "transfer/terminal-density"


def main():
    answer = TARGET / "answer.md"
    text = answer.read_text(encoding="utf-8")
    timing = inspect(answer, D("6"), 12)
    shots = {s["id"]: s for s in timing["shots"]}
    checks = []

    def check(name, passed):
        checks.append({"check": name, "passed": bool(passed)})

    check("shot_table_numbering_duration_and_continuity", timing["passed"])
    check("seven_fast_five_long", timing["fast_shots"] == 7 and len(shots) == 12)
    contacts = []
    for event, start in enumerate((3, 6, 9), 1):
        roles = ("来路", "命中点", "反馈")
        check(f"event_{event}_three_consecutive_roles", all(
            f"{event:02}{role}" in shots[f"S{start + offset:02}"]["description"]
            for offset, role in enumerate(roles)))
        hit = shots[f"S{start + 1:02}"]
        # Extract from the actual shot row, not its prose summary.
        match = re.search(r"(?<![\d.])(\d+\.\d+)秒", hit["description"])
        contact = D(match.group(1)) if match else D("-1")
        check(f"event_{event}_contact_inside_shot", D(hit["start"]) <= contact < D(hit["end"]))
        contacts.append(contact)
    intervals = [b - a for a, b in zip(contacts, contacts[1:])]
    check("two_actual_contact_intervals_1_10_seconds", intervals == [D("1.10"), D("1.10")])
    windows = [(D(shots[s]["start"]), D(shots[s]["end"])) for s in ("S01", "S12")]
    gaps = [windows[0][0], windows[1][0] - windows[0][1], D("6") - windows[-1][1]]
    check("main_reset_window_gap_at_most_5_seconds", max(gaps) <= D("5"))
    # The text explicitly calls these windows fully readable; this checks their
    # arithmetic, not whether moving images would actually be readable.
    micros = [(D(a), D(b)) for a, b in re.findall(r"(\d+\.\d+)—(\d+\.\d+)秒", text.split("|镜号")[0])]
    check("exactly_two_nonoverlapping_micro_intervals", len(micros) == 2 and
          D("0") <= micros[0][0] < micros[0][1] <= micros[1][0] < micros[1][1] <= D("6"))
    check("final_contact_in_final_micro", len(micros) == 2 and micros[1][0] <= contacts[-1] < micros[1][1])
    # Synthetic timing negatives: missing readable reset and contact past cut.
    check("reject_missing_final_reset", D("6") - windows[0][1] > D("5"))
    final_hit = shots["S10"]
    check("reject_contact_after_hit_shot", not (D(final_hit["start"]) <= D("3.85") < D(final_hit["end"])))

    result = {
        "source": str(answer), "sha256": hashlib.sha256(answer.read_bytes()).hexdigest(),
        "scope": "text_timing_role_labels_and_declared_read_windows_only",
        "actual_contact_times": [str(t) for t in contacts],
        "actual_contact_intervals": [str(t) for t in intervals],
        "max_main_reference_gap": str(max(gaps)),
        "read_window_semantics": "manually declared; not verified from media",
        "checks": checks, "passed": all(c["passed"] for c in checks),
        "audio_observed": False, "generated_media": False,
    }
    (TARGET / "timing.json").write_text(json.dumps(timing, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    (TARGET / "checks.json").write_text(json.dumps(result, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    print(json.dumps(result, ensure_ascii=False))
    return 0 if result["passed"] else 1


if __name__ == "__main__":
    raise SystemExit(main())
