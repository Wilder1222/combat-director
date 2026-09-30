"""Positive/negative text fixtures; no media or semantic pass is implied."""
from decimal import Decimal
import hashlib
import json
from pathlib import Path
import tempfile

from check_sequence import inspect_sequence

ROOT = Path(__file__).resolve().parents[2]
SOURCE = ROOT / "skills/combat-director/examples/flower-path-44.md"


def main():
    original = SOURCE.read_text(encoding="utf-8")

    def replace(old, new):
        assert old in original, f"Fixture anchor missing: {old}"
        return original.replace(old, new, 1)

    cases = [
        ("complete_44", original, True, ""),
        ("no_table", "No shot table", False, "No supported shot table"),
        ("missing_event", replace("E01/反馈", "—"), False, "expected exactly one"),
        ("duplicate_first_touch", replace("首触 3.30；", "首触 3.30；首触 3.31；"), False, "exactly one first touch"),
        ("continued_contact_recounted", replace("E01/反馈", "E01/命中点"), False, "expected exactly one"),
        ("wrong_chain_order", replace("E01/来路", "E01/反馈"), False, "expected exactly one"),
        ("unknown_role", replace("E01/来路", "E01/新撞"), False, "unsupported or ambiguous"),
        ("touch_outside_shot", replace("首触 3.30；", "首触 3.70；"), False, "first touch outside"),
        ("stop_before_touch", replace("Hit Stop 3.30—3.34", "Hit Stop 3.29—3.34"), False, "start at declared first touch"),
        ("stop_beyond_shot", replace("Hit Stop 3.30—3.34", "Hit Stop 3.30—3.80"), False, "outside shot"),
        ("read_title_but_late_window", replace("读位 4.80—6.00", "读位 5.90—6.00").replace("读位 0.00—1.20", "读位 0.00—0.80"), False, "exceeding 5s"),
        ("empty_read_window", replace("读位 4.80—6.00", "读位 4.80—4.80"), False, "outside shot or empty"),
        ("read_outside_shot", replace("读位 4.80—6.00", "读位 4.70—6.00"), False, "outside shot"),
        ("missing_micro", replace("微慢 开场 0.20—0.70", "开场速度未定义"), False, "Exactly two"),
        ("micro_outside_duration", replace("微慢 终局 27.90—28.45", "微慢 终局 28.30—30.10"), False, "invalid/overlapping"),
        ("third_micro", original + "\n微慢 中段 12.00—12.20\n", False, "Exactly two"),
        ("phase_gap", replace("节奏段 连爆与改局 8.00—22.00", "节奏段 连爆与改局 8.90—22.00"), False, "tile duration"),
        ("phase_inside_shot", replace("节奏段 拉升 0.00—8.00", "节奏段 拉升 0.00—7.90"), False, "shot boundaries"),
        ("wrong_declared_duration", replace("| S01 | 0.00—1.20 | 1.20 |", "| S01 | 0.00—1.20 | 1.10 |"), False, "written duration"),
    ]
    results = []
    with tempfile.TemporaryDirectory() as folder:
        p = Path(folder) / "candidate.md"
        for name, text, expected, error in cases:
            p.write_text(text, encoding="utf-8")
            result = inspect_sequence(p, Decimal(30), 44)
            good = result["passed"] == expected and (not error or any(error in e for e in result["errors"]))
            if name == "complete_44":
                good = good and len(result["events"]) == 10 and len(result["contacts"]) == 10
                good = good and result["fast_shots"] == 21 and result["long_shots"] == 23
                good = good and [s["shots"] for s in result["phases"]] == [10, 20, 14]
                good = good and result["contact_gaps"][-3:] == ["2.68", "1.40", "1.40"]
                good = good and result["max_unreadable_gap"] == "3.60"
            results.append({"case": name, "expected_acceptance": expected, "passed": good, "observed_errors": result["errors"]})
    report = {
        "source_sha256": hashlib.sha256(SOURCE.read_bytes()).hexdigest(),
        "checker_sha256": hashlib.sha256(Path(__file__).with_name("check_sequence.py").read_bytes()).hexdigest(),
        "scope": "synthetic_text_checker_regression_only", "passed": all(r["passed"] for r in results), "cases": results,
    }
    Path(__file__).with_name("sequence-self-check.json").write_text(json.dumps(report, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    print(json.dumps({"passed": report["passed"], "cases": len(results), "failures": [r for r in results if not r["passed"]]}, ensure_ascii=False))
    return 0 if report["passed"] else 1


if __name__ == "__main__":
    raise SystemExit(main())
