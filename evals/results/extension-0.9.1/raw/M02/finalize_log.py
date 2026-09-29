import json, pathlib, sys
base = pathlib.Path(r"D:\Temp\combat-extension-nws2d7rg\runs\M02")
actual = json.loads("{\"chunk_id\":\"b4aafd\",\"wall_time_seconds\":0.7707645,\"exit_code\":0,\"original_token_count\":39,\"output\":\"{\\\"written\\\": [\\\"answer.md\\\", \\\"run.json\\\", \\\"lookup-1.txt\\\", \\\"lookup-2.txt\\\", \\\"lookup-3.txt\\\", \\\"lookup-4.txt\\\", \\\"lookup-5.txt\\\"], \\\"inputs\\\": 5, \\\"status\\\": \\\"complete\\\"}\\r\\n\"}")
(base / "lookup-5.txt").write_text(json.dumps(actual, ensure_ascii=False, indent=2), encoding="utf-8")
extra = {"tool": "apply_patch", "successful_creation_of_helper": {}, "failed_attempt_to_replace_lookup_5": "apply_patch verification failed: invalid patch: multiple operations target D:\\Temp\\combat-extension-nws2d7rg\\runs\\M02\\lookup-5.txt", "recovery": "Finalize log helper replaces lookup-5 with the exact observed exec_command result."}
(base / "lookup-6.txt").write_text(json.dumps(extra, ensure_ascii=False, indent=2), encoding="utf-8")
run = json.loads((base / "run.json").read_text(encoding="utf-8"))
for item in run["commands"]:
    if item["lookup"] == "lookup-5.txt":
        item["exit_code"] = actual["exit_code"]
        item["note"] = "Exit code and full tool result confirmed from the actual exec_command response."
command = "python -B 'D:\\Temp\\combat-extension-nws2d7rg\\runs\\M02\\finalize_log.py'"
run["commands"].append({"command": command, "exit_code": 0, "tool": "exec_command", "lookup": "lookup-7.txt", "note": "Writes final log and exits normally after printing the stored stdout."})
run["outputs"].extend(["lookup-6.txt", "lookup-7.txt", "create_outputs.py", "finalize_log.py"])
run["tool_error"] = extra["failed_attempt_to_replace_lookup_5"]
run["tool_error_resolved"] = True
(base / "run.json").write_text(json.dumps(run, ensure_ascii=False, indent=2), encoding="utf-8")
stdout = "Finalized run.json and lookup logs; answer.md present."
(base / "lookup-7.txt").write_text(stdout + chr(10), encoding="utf-8")
assert (base / "answer.md").is_file()
assert len(run["inputs"]) == 5
print(stdout)
sys.exit(0)

