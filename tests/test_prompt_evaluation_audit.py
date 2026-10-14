"""Check frozen-score integrity and time arithmetic, not combat/media quality."""
from contextlib import redirect_stderr, redirect_stdout
import hashlib
import importlib.util
import io
import json
from pathlib import Path
import subprocess
import sys
import tempfile
import unittest

ROOT = Path(__file__).resolve().parents[1]
SPEC = importlib.util.spec_from_file_location("prompt_evaluation_audit", ROOT / "scripts/audit_prompt_evaluations.py")
AUDIT = importlib.util.module_from_spec(SPEC)
SPEC.loader.exec_module(AUDIT)


class EvaluationAuditTests(unittest.TestCase):
    def setUp(self):
        folder = ROOT / "outputs"
        folder.mkdir(exist_ok=True)
        self.temp = tempfile.TemporaryDirectory(prefix="audit-fixture-", dir=folder)
        self.addCleanup(self.temp.cleanup)
        self.here = Path(self.temp.name).resolve()
        self.assertTrue(self.here.is_relative_to(folder.resolve()))
        source = self.here / "source.txt"
        source.write_bytes(b"synthetic frozen source\n")
        source_sha = AUDIT.sha(source)
        self.prompt = self.here / "prompt.txt"
        self.prompt.write_text(
            "2秒\n【全局画面】双人\n【画质】轮廓\n【风格】二维\n【摄影】全局选择\n"
            "镜1／节点1：0–2秒（镜长2秒，占时2秒）\n"
            "【画面与动作】进身1秒、回收1秒，对手同窗退步2秒。\n【摄影】侧面\n", encoding="utf-8")
        (self.here / "review.md").write_text("Synthetic review, no media claim.\n", encoding="utf-8")
        self.data = {"weights": {"C": 20}, "rounds": [{
            "round": 1, "prompt": "prompt.txt", "review": "review.md", "prompt_sha256": AUDIT.sha(self.prompt),
            "duration": "2", "node_count": 1, "shot_count": 1, "camera": "multi_shot",
            "critical_routes": [["1", "1"]], "response_routes": [["2"]],
            "branches": [], "scores": {"C": 20}, "score": 20, "hard_fail": False}]}
        self.manifest = {"runtime": [{"path": source.relative_to(ROOT).as_posix(),
                                     "sha256": source_sha, "installed_sha256": source_sha}], "sources": [],
                         "prompts": [{"path": "prompt.txt", "sha256": AUDIT.sha(self.prompt)}]}
        self.write()

    def write(self):
        for name, value in (("evaluation.json", self.data), ("manifest.json", self.manifest)):
            (self.here / name).write_text(json.dumps(value) + "\n", encoding="utf-8")

    def run_audit(self, extra=()):
        self.write()
        output = io.StringIO()
        with redirect_stdout(output):
            code = AUDIT.main([str(self.here), *extra])
        return code, json.loads(output.getvalue())

    def test_global_camera_is_not_an_extra_node_and_run_is_read_only(self):
        original = {p.name: p.read_bytes() for p in self.here.iterdir()}
        code, report = self.run_audit()
        self.assertEqual(code, 0)
        self.assertTrue(report["artifact_audit_passed"])
        self.assertEqual(original, {p.name: p.read_bytes() for p in self.here.iterdir()})

    def test_changed_prompt_bytes_fail_even_when_structure_is_valid(self):
        self.prompt.write_bytes(self.prompt.read_bytes() + b"extra\n")
        code, report = self.run_audit()
        self.assertEqual(code, 1)
        self.assertIn("Prompt fingerprint mismatch", report["rounds"][0]["artifact_errors"])
        self.data["rounds"][0]["prompt_sha256"] = AUDIT.sha(self.prompt)
        code, report = self.run_audit()
        self.assertEqual(code, 1)
        self.assertIn("Frozen prompt fingerprint mismatch: prompt.txt", report["errors"])

    def test_primary_and_response_overflow_cannot_hide_behind_correct_node_sum(self):
        for key in ("critical_routes", "response_routes"):
            with self.subTest(key=key):
                self.data["rounds"][0][key] = [["1.2", "1"]]
                code, report = self.run_audit()
                self.assertEqual(code, 1)
                self.assertFalse(report["artifact_audit_passed"])
                self.data["rounds"][0][key] = [["1", "1"]]

    def test_trigger_offset_cannot_be_removed_by_parallel_label(self):
        self.data["rounds"][0]["branches"] = [{"node": 1, "actor": "B", "trigger_offset": "1.2",
            "durations": ["1", "1"], "expected_overflow": "1.2", "carryover": None}]
        code, report = self.run_audit()
        self.assertEqual(code, 1)
        self.assertEqual(report["rounds"][0]["branches"][0]["completion_from_node_start"], "3.2")

    def test_numeric_json_durations_do_not_create_binary_float_overflows(self):
        body = self.prompt.read_text(encoding="utf-8").replace("2秒", "0.3秒")
        body = body.replace("进身1秒、回收1秒", "进身0.1秒、回收0.2秒")
        self.prompt.write_text(body, encoding="utf-8")
        item = self.data["rounds"][0]
        item.update(duration=0.3, critical_routes=[[0.1, 0.2]], response_routes=[[0.3]],
                    prompt_sha256=AUDIT.sha(self.prompt), branches=[{"node": 1, "actor": "B",
                    "trigger_offset": 0.1, "durations": [0.2], "expected_overflow": 0.0, "carryover": None}])
        self.manifest["prompts"][0]["sha256"] = AUDIT.sha(self.prompt)
        self.assertEqual(self.run_audit()[0], 0)

    def test_score_arithmetic_and_unknown_hard_failure_are_rejected(self):
        self.data["rounds"][0]["score"] = 19
        self.assertEqual(self.run_audit()[0], 1)
        self.data["rounds"][0]["score"] = 20
        self.data["rounds"][0]["hard_fail"] = True
        self.assertEqual(self.run_audit()[0], 1)

    def test_invalid_durations_and_frozen_output_are_rejected(self):
        self.assertEqual(AUDIT.total([0.2, 0.3]), AUDIT.Decimal("0.5"))
        for values in (["-0.2", "2.2"], ["NaN"], ["Infinity"], [True]):
            with self.assertRaises(ValueError):
                AUDIT.total(values)
        with self.assertRaises(SystemExit), redirect_stderr(io.StringIO()):
            self.run_audit(("--out", str(self.here / "validation.json")))
        with self.assertRaises(SystemExit), redirect_stderr(io.StringIO()):
            self.run_audit(("--out", str(ROOT / "docs/evaluations/2026-10-13-five-style/validation.json")))

    def test_both_compatibility_entries_preserve_historical_outcomes(self):
        original = {}
        for folder, revision in (("2026-10-13-five-style", "f2463f7542895b4ee366dac688087e6ea0d4a2d5"),
                                 ("2026-10-13-five-style-retest", None)):
            directory = ROOT / "docs/evaluations" / folder
            for name in ("evaluation.json", "manifest.json", "validation.json"):
                original[str(directory / name)] = hashlib.sha256((directory / name).read_bytes()).hexdigest()
            command = [sys.executable, "-X", "utf8", str(directory / "verify_evaluation.py")]
            if revision:
                command.extend(["--source-revision", revision])
            process = subprocess.run(command, cwd=self.here, capture_output=True, text=True, encoding="utf-8")
            self.assertEqual(process.returncode, 0, process.stderr)
            report = json.loads(process.stdout)
            self.assertTrue(report["artifact_audit_passed"])
            self.assertEqual(report["all_prompts_passed_text_review"], revision is None)
            if revision:
                self.assertEqual(report["rounds"][1]["score"], 79)
                self.assertEqual(report["rounds"][1]["critical_route_overflows"][0]["overflow"], "0.2")
            else:
                self.assertEqual(report["baseline_counterexamples"]["round2_node6_branch_overflow"], "1.2")
                self.assertEqual(report["execution_skill"], "modified_workspace_skill")
                self.assertFalse(report["installed_entry_matches_workspace"])
        self.assertEqual(original, {p: hashlib.sha256(Path(p).read_bytes()).hexdigest() for p in original})


if __name__ == "__main__":
    unittest.main()
