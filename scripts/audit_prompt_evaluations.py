"""Audit frozen prompt cohorts and human-transcribed timing ledgers.

This is not a semantic combat validator or an independent quality evaluator.
Ordinary runs are read-only. Use --out for a separate current receipt and
--source-revision to inspect historical source bytes without changing snapshots.
"""

import argparse
import hashlib
import json
import re
import subprocess
from decimal import Decimal
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
INSTALLED = Path.home() / ".codex/plugins/cache/personal/combat-director/0.11.0"
RUNTIME = [
    "SKILL.md", "references/prompt-construction.md", "references/library-workflow.md",
    "references/genre-routing.md", "references/choreography.md",
    "references/camera-and-rhythm.md", "references/style-and-materials.md",
    "references/powers-and-formations.md", "references/movement-and-projectiles.md",
    "references/sound-and-performance.md", "library/abilities/static-contact-awakening.md",
]
SOURCES = [
    "sources/attachments/2026-09-21/grounded-15.prompt.txt",
    "sources/attachments/2026-09-21/epic-30.prompt.txt",
    "sources/attachments/2026-09-21/colossus-30.prompt.txt",
    "sources/attachments/2026-09-22/3-双人打斗第二弹.txt",
    "sources/attachments/user-prompts/7-7.30.extracted.txt",
    "sources/attachments/user-prompts/8-8.2.extracted.txt",
    "docs/implementation/2026-10-11-user-reference-map.md",
    "docs/implementation/2026-10-12-reference-benchmark.md",
    "docs/implementation/2026-10-13-static-contact-node-timing.md",
]


def sha(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


def save(path, value):
    path.write_text(json.dumps(value, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")


def total(values):
    if any(isinstance(value, bool) for value in values):
        raise ValueError("Action durations cannot be booleans")
    numbers = [Decimal(str(value)) for value in values]
    if any(not number.is_finite() or number < 0 for number in numbers):
        raise ValueError("Action durations must be finite and non-negative")
    return sum(numbers, Decimal(0))


def main(argv=None, *, default_directory=None):
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("directory", nargs="?", type=Path, default=default_directory)
    parser.add_argument("--source-revision", help="Read source blobs at this local Git revision")
    parser.add_argument("--out", type=Path, help="Write a current receipt under project outputs/, outside the frozen cohort")
    parser.add_argument("--freeze", action="store_true")
    args = parser.parse_args(argv)
    if args.directory is None:
        parser.error("Supply a cohort directory")
    HERE = args.directory.resolve()
    if not HERE.is_relative_to(ROOT):
        parser.error("Cohort directory must be inside the project")
    if args.out and (not args.out.resolve().is_relative_to(ROOT / "outputs")
                     or args.out.resolve().is_relative_to(HERE)):
        parser.error("Write current receipts under project outputs/, outside the frozen cohort")
    data = json.loads((HERE / "evaluation.json").read_text(encoding="utf-8"))
    manifest_path = HERE / "manifest.json"
    if args.freeze:
        if manifest_path.exists():
            raise SystemExit("Refusing to replace an existing source snapshot.")
        runtime = []
        for name in RUNTIME:
            rel = "skills/combat-director/" + name
            cache = INSTALLED / rel
            runtime.append({"path": rel, "sha256": sha(ROOT / rel),
                            "installed_sha256": sha(cache) if cache.exists() else None})
        save(manifest_path, {
            "date": data["date"], "timezone": data["timezone"],
            "head": subprocess.check_output(["git", "rev-parse", "HEAD"], cwd=ROOT).decode().strip(),
            "version": "0.11.0", "runtime": runtime,
            "sources": [{"path": name, "sha256": sha(ROOT / name)} for name in SOURCES],
            "prompts": [{"path": item["prompt"], "sha256": item["prompt_sha256"]}
                        for item in data["rounds"]],
            "source_scope": "Hashes cover complete files; only task-relevant sections were read. SO-YEON original input was not available; its project adaptation was used.",
        })

    manifest = json.loads(manifest_path.read_text(encoding="utf-8"))
    errors, rounds = [], []
    for source in manifest["runtime"] + manifest["sources"]:
        source_path = (ROOT / source["path"]).resolve()
        if not source_path.is_relative_to(ROOT):
            errors.append("Source path escapes project: " + source["path"])
            continue
        if args.source_revision:
            blob = subprocess.check_output(["git", "show", args.source_revision + ":" + source["path"]], cwd=ROOT)
            actual_sha = hashlib.sha256(blob).hexdigest()
        else:
            actual_sha = sha(source_path)
        if actual_sha != source["sha256"]:
            errors.append("Source changed: " + source["path"])
    for frozen_prompt in manifest.get("prompts", []):
        prompt_path = (HERE / frozen_prompt["path"]).resolve()
        if not prompt_path.is_relative_to(HERE):
            errors.append("Frozen prompt path escapes cohort: " + frozen_prompt["path"])
        elif sha(prompt_path) != frozen_prompt["sha256"]:
            errors.append("Frozen prompt fingerprint mismatch: " + frozen_prompt["path"])
    entry = manifest["runtime"][0]
    baseline = None
    if "baseline" in data:
        baseline_path = (HERE / data["baseline"]).resolve()
        if not baseline_path.is_relative_to(ROOT):
            raise ValueError("Baseline path escapes project")
        baseline = json.loads(baseline_path.read_text(encoding="utf-8"))
        for old in baseline["rounds"]:
            if sha(baseline_path.parent / old["prompt"]) != old["prompt_sha256"]:
                errors.append("Frozen baseline prompt changed: " + old["prompt"])
    elif entry["sha256"] != entry.get("installed_sha256"):
        errors.append("Recorded baseline project and installed entry differ")

    pattern = re.compile(r"节点(\d+)：([\d.]+)–([\d.]+)秒（[^）]*占时([\d.]+)秒）")
    for item in data["rounds"]:
        prompt = HERE / item["prompt"]
        if not prompt.resolve().is_relative_to(HERE):
            raise ValueError("Prompt path escapes cohort")
        body = prompt.read_text(encoding="utf-8")
        local_errors = []
        if sha(prompt) != item["prompt_sha256"]:
            local_errors.append("Prompt fingerprint mismatch")
        if not (HERE / item["review"]).exists():
            local_errors.append("Missing review")
        for tag in ("【全局画面】", "【画质】", "【风格】"):
            if body.count(tag) != 1:
                local_errors.append("Invalid global tag: " + tag)
        nodes = [(int(n), Decimal(s), Decimal(e), Decimal(d)) for n, s, e, d in pattern.findall(body)]
        if len(nodes) != item["node_count"] or len(nodes) != len(item["critical_routes"]):
            local_errors.append("Node count mismatch")
        cursor, spans, overflows = Decimal(0), {}, []
        for index, (number, start, end, duration) in enumerate(nodes):
            if number != index + 1 or start != cursor or end - start != duration or duration <= 0:
                local_errors.append("Invalid node span: " + str(number))
            cursor, spans[number] = end, duration
            used = total(item["critical_routes"][index]) if index < len(item["critical_routes"]) else Decimal(0)
            if used > duration:
                overflows.append({"node": number, "overflow": str(used - duration)})
            if "response_routes" in item:
                if len(item["response_routes"]) != len(nodes):
                    local_errors.append("Response route count mismatch")
                elif total(item["response_routes"][index]) > duration:
                    local_errors.append("Response route overflow: " + str(number))
        if cursor != Decimal(str(item["duration"])):
            local_errors.append("Total duration mismatch")
        node_matches = list(pattern.finditer(body))
        for index, match in enumerate(node_matches):
            stop = node_matches[index + 1].start() if index + 1 < len(node_matches) else len(body)
            segment = body[match.start():stop]
            for tag in ("【画面与动作】", "【摄影】"):
                if segment.count(tag) != 1:
                    local_errors.append("Node tag count mismatch: " + str(index + 1) + tag)
        if item["camera"] == "multi_shot":
            mirrors = re.findall(r"镜\d+／节点\d+：[\d.]+–[\d.]+秒（镜长([\d.]+)秒", body)
            if len(mirrors) != len(nodes) or any(Decimal(d) != nodes[i][3] for i, d in enumerate(mirrors)):
                local_errors.append("Shot span mismatch")
            if item.get("shot_count", len(mirrors)) != len(mirrors):
                local_errors.append("Registered shot count mismatch")
        elif f"全镜0–{item['duration']}秒，镜长{item['duration']}秒" not in body:
            local_errors.append("Missing full single-shot duration")
        elif item.get("shot_count", 1) != 1:
            local_errors.append("Single-shot count mismatch")
        expected = [(x["node"], Decimal(str(x["overflow"]))) for x in item.get("expected_overflows", [])]
        found = [(x["node"], Decimal(x["overflow"])) for x in overflows]
        if found != expected:
            local_errors.append("Unexpected critical-route overflows")
        branch_results = []
        for branch in item["branches"]:
            completion = Decimal(str(branch["trigger_offset"])) + total(branch["durations"])
            overflow = completion - spans[branch["node"]]
            if overflow != Decimal(str(branch["expected_overflow"])):
                local_errors.append("Branch timing mismatch: " + branch["actor"])
            carry = branch["carryover"]
            if carry and (Decimal(str(carry["duration"])) != overflow or carry["node"] != branch["node"] + 1
                          or carry["required_phrase"] not in body):
                local_errors.append("Invalid explicit carryover")
            branch_results.append({"actor": branch["actor"], "node": branch["node"],
                                   "completion_from_node_start": str(completion),
                                   "overflow": str(overflow), "explicit_carryover": bool(carry)})
        raw = sum(item["scores"].values())
        if set(item["scores"]) != set(data["weights"]) or any(
            not 0 <= value <= data["weights"][key] for key, value in item["scores"].items()
        ) or raw != item.get("raw_score", item["score"]) or item["score"] != (min(raw, 79) if item["hard_fail"] else raw):
            local_errors.append("Invalid score arithmetic")
        if baseline and item["old_score"] != baseline["rounds"][item["round"] - 1]["score"]:
            local_errors.append("Baseline score mismatch")
        numeric_hard_fail = bool(overflows or any(
            Decimal(x["overflow"]) > 0 and not x["explicit_carryover"] for x in branch_results
        ))
        if (numeric_hard_fail and not item["hard_fail"]) or (
            item["hard_fail"] and not numeric_hard_fail and not item.get("hard_failure_reasons")
        ):
            local_errors.append("Hard-failure classification mismatch")
        rounds.append({"round": item["round"], "score": item["score"], "old_score": item.get("old_score"),
                       "score_delta": item["score"] - item["old_score"] if baseline else None,
                       "nodes": len(nodes), "shots_registered": item.get("shot_count", len(nodes) if item["camera"] == "multi_shot" else 1),
                       "duration": str(cursor), "critical_route_overflows": overflows,
                       "branches": branch_results, "text_verdict": "fail" if item["hard_fail"] else "strong_candidate",
                       "artifact_errors": local_errors})
        errors.extend(f"Round {item['round']}: {error}" for error in local_errors)

    for path in HERE.iterdir():
        if path.suffix in (".txt", ".md", ".json", ".py"):
            for number, line in enumerate(path.read_text(encoding="utf-8").splitlines(), 1):
                if line.rstrip() != line:
                    errors.append(f"Trailing whitespace: {path.name}:{number}")
    counterexamples = None
    if baseline:
        old_second = baseline["rounds"][1]
        old_body = (baseline_path.parent / old_second["prompt"]).read_text(encoding="utf-8")
        old_spans = {int(n): Decimal(d) for n, s, e, d in pattern.findall(old_body)}
        old_primary_overflow = total(old_second["critical_routes"][4]) - old_spans[5]
        old_branch = old_second["branches"][0]
        old_branch_overflow = Decimal(str(old_branch["trigger_offset"])) + total(old_branch["durations"]) - old_spans[6]
        if old_primary_overflow != Decimal("0.2") or old_branch_overflow != Decimal("1.2"):
            errors.append("Frozen baseline counterexamples were not detected")
        counterexamples = {"round2_node5_overflow": str(old_primary_overflow), "round2_node6_branch_overflow": str(old_branch_overflow)}
    result = {"artifact_audit_passed": not errors,
              "all_prompts_passed_text_review": not any(x["hard_fail"] for x in data["rounds"]),
              "source_revision": args.source_revision or "worktree",
              "recorded_installation_matches_snapshot_entry": entry["sha256"] == entry.get("installed_sha256"),
              "installed_runtime_files_matching": sum(x["sha256"] == x["installed_sha256"] for x in manifest["runtime"]),
              "runtime_files_snapshotted": len(manifest["runtime"]), "node_count": sum(x["nodes"] for x in rounds),
              "registered_shot_count": sum(x["shots_registered"] for x in rounds),
              "baseline_prompts_unchanged": not any("Frozen baseline" in error for error in errors),
              "baseline_counterexamples": counterexamples,
              "scope": "File integrity, tags, node/shot structure, score arithmetic, and human-transcribed route calculations only.",
              "media_quality_verified": False, "rounds": rounds, "errors": errors}
    if baseline:
        result.update({"execution_skill": "modified_workspace_skill",
                       "installed_entry_matches_workspace": entry["sha256"] == entry.get("installed_sha256"),
                       "installation_comparison_scope": "Frozen manifest bytes, not the current installed plugin"})
    if args.out:
        args.out.resolve().parent.mkdir(parents=True, exist_ok=True)
        save(args.out.resolve(), result)
    print(json.dumps(result, ensure_ascii=False, indent=2))
    return 0 if not errors else 1


if __name__ == "__main__":
    raise SystemExit(main())
