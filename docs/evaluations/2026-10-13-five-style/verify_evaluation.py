"""Audit frozen text artifacts and human-transcribed timing ledgers.

This is not a semantic combat validator or an independent quality evaluator.
Run --freeze once to record the source snapshot; ordinary runs never replace it.
"""

import argparse
import hashlib
import json
import re
from decimal import Decimal
from pathlib import Path

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[2]
INSTALLED = Path(r"C:\Users\ww\.codex\plugins\cache\personal\combat-director\0.11.0")
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
    return sum((Decimal(value) for value in values), Decimal(0))


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--freeze", action="store_true")
    args = parser.parse_args()
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
            "head": "f2463f7542895b4ee366dac688087e6ea0d4a2d5",
            "version": "0.11.0", "runtime": runtime,
            "sources": [{"path": name, "sha256": sha(ROOT / name)} for name in SOURCES],
            "prompts": [{"path": item["prompt"], "sha256": item["prompt_sha256"]}
                        for item in data["rounds"]],
            "source_scope": "Hashes cover complete files; only task-relevant sections were read. SO-YEON original input was not available; its project adaptation was used.",
        })

    manifest = json.loads(manifest_path.read_text(encoding="utf-8"))
    errors, rounds = [], []
    for source in manifest["runtime"] + manifest["sources"]:
        if sha(ROOT / source["path"]) != source["sha256"]:
            errors.append("Source changed: " + source["path"])
    entry = manifest["runtime"][0]
    if entry["sha256"] != entry["installed_sha256"]:
        errors.append("Project and installed skill entry differ.")

    pattern = re.compile(r"节点(\d+)：([\d.]+)–([\d.]+)秒（[^）]*占时([\d.]+)秒）")
    for item in data["rounds"]:
        prompt = HERE / item["prompt"]
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
            used = total(item["critical_routes"][index])
            if used > duration:
                overflows.append({"node": number, "overflow": str(used - duration)})
        if cursor != Decimal(item["duration"]):
            local_errors.append("Total duration mismatch")
        for tag in ("【画面与动作】", "【摄影】"):
            if body.count(tag) != item["node_count"]:
                local_errors.append("Node tag count mismatch: " + tag)
        if item["camera"] == "multi_shot":
            mirrors = re.findall(r"镜\d+／节点\d+：[\d.]+–[\d.]+秒（镜长([\d.]+)秒", body)
            if len(mirrors) != len(nodes) or any(Decimal(d) != nodes[i][3] for i, d in enumerate(mirrors)):
                local_errors.append("Shot span mismatch")
        elif f"全镜0–{item['duration']}秒，镜长{item['duration']}秒" not in body:
            local_errors.append("Missing full single-shot duration")
        expected = [(x["node"], Decimal(x["overflow"])) for x in item["expected_overflows"]]
        found = [(x["node"], Decimal(x["overflow"])) for x in overflows]
        if found != expected:
            local_errors.append("Unexpected critical-route overflows")
        branch_results = []
        for branch in item["branches"]:
            completion = Decimal(branch["trigger_offset"]) + total(branch["durations"])
            overflow = completion - spans[branch["node"]]
            if overflow != Decimal(branch["expected_overflow"]):
                local_errors.append("Branch timing mismatch: " + branch["actor"])
            carry = branch["carryover"]
            if carry and (Decimal(carry["duration"]) != overflow or carry["node"] != branch["node"] + 1
                          or carry["required_phrase"] not in body):
                local_errors.append("Invalid explicit carryover")
            branch_results.append({"actor": branch["actor"], "node": branch["node"],
                                   "completion_from_node_start": str(completion),
                                   "overflow": str(overflow), "explicit_carryover": bool(carry)})
        raw = sum(item["scores"].values())
        if set(item["scores"]) != set(data["weights"]) or any(
            not 0 <= value <= data["weights"][key] for key, value in item["scores"].items()
        ) or raw != item["raw_score"] or item["score"] != (min(raw, 79) if item["hard_fail"] else raw):
            local_errors.append("Invalid score arithmetic")
        if item["hard_fail"] != bool(overflows or any(
            Decimal(x["overflow"]) > 0 and not x["explicit_carryover"] for x in branch_results
        )):
            local_errors.append("Hard-failure classification mismatch")
        rounds.append({"round": item["round"], "score": item["score"], "nodes": len(nodes),
                       "duration": str(cursor), "critical_route_overflows": overflows,
                       "branches": branch_results, "text_verdict": "fail" if item["hard_fail"] else "strong_candidate",
                       "artifact_errors": local_errors})
        errors.extend(f"Round {item['round']}: {error}" for error in local_errors)

    for path in HERE.iterdir():
        if path.suffix in (".txt", ".md", ".json", ".py"):
            for number, line in enumerate(path.read_text(encoding="utf-8").splitlines(), 1):
                if line.rstrip() != line:
                    errors.append(f"Trailing whitespace: {path.name}:{number}")
    result = {"artifact_audit_passed": not errors, "all_prompts_passed_text_review": False,
              "installed_runtime_files_matching": sum(x["sha256"] == x["installed_sha256"] for x in manifest["runtime"]),
              "runtime_files_snapshotted": len(manifest["runtime"]), "node_count": sum(x["nodes"] for x in rounds),
              "scope": "File integrity, tags, node/shot structure, score arithmetic, and human-transcribed route calculations only.",
              "media_quality_verified": False, "rounds": rounds, "errors": errors}
    save(HERE / "validation.json", result)
    print(json.dumps(result, ensure_ascii=False, indent=2))
    return 0 if not errors else 1


if __name__ == "__main__":
    raise SystemExit(main())
