import hashlib
import json
import pathlib
import re
import sys
import traceback

sys.stdout.reconfigure(encoding="utf-8")
OUT = pathlib.Path(__file__).resolve().parent
log = json.loads((OUT / "run.json").read_text(encoding="utf-8"))
initial_command = r"""@'
import pathlib, hashlib, json, sys, traceback
out = pathlib.Path(r'D:\Temp\combat-extension-nws2d7rg\runs\M01')
skill = pathlib.Path(r'D:\Temp\combat-extension-nws2d7rg\candidate\skills\combat-director\SKILL.md')
log = {'request': None, 'inputs': [], 'commands': [], 'image_views': [], 'outputs': []}
code = 0
try:
    data = skill.read_bytes()
    body = data.decode('utf-8-sig')
    log['inputs'].append({'path': str(skill), 'sha256': hashlib.sha256(data).hexdigest(), 'read_mode': 'full', 'script_internal_read': True, 'actual_image_view': False})
    rendered = 'FILE: ' + str(skill) + '\nSHA-256: ' + hashlib.sha256(data).hexdigest() + '\n\n' + body
except Exception:
    code = 1
    rendered = traceback.format_exc()
(out / 'lookup-1.txt').write_text(rendered, encoding='utf-8')
log['commands'].append({'command': "PowerShell here-string piped to python -B - (script captured below)", 'script': '''import pathlib, hashlib, json, sys, traceback; read SKILL.md fully; initialize run.json; write lookup-1.txt''', 'process_argv': sys.orig_argv, 'exit_code': code, 'tool_output': str(out / 'lookup-1.txt')})
(out / 'run.json').write_text(json.dumps(log, ensure_ascii=False, indent=2), encoding='utf-8')
print(rendered)
sys.exit(code)
'@ | python -B -"""
code = 0
try:
    answer = (OUT / "answer.md").read_text(encoding="utf-8")
    prompts = re.findall(r"```text\n(.*?)\n```", answer, re.S)
    assert len(prompts) == 2, "Expected two prompts"
    extra = prompts[1][len(prompts[0]):]
    assert prompts[1].startswith(prompts[0]), "Prompt B base text differs"
    assert extra.startswith("\n<局部运动模糊>") and extra.endswith("</局部运动模糊>"), "Unexpected added text"
    log["commands"][0]["command"] = initial_command
    log["commands"][0].pop("script", None)
    log["commands"][0]["output_note"] = "lookup-1.txt preserves the script's emitted text in UTF-8. The first tool transport displayed mojibake; SKILL.md was reread in command 2 with explicit UTF-8 stdout."
    for item in log["inputs"]:
        item["content_exposed_to_agent"] = True
    log["inputs"][0]["content_exposed_to_agent"] = "Attempted full output; transport mojibake. A successful complete reread is recorded separately."
    log["read_coverage_summary"] = {"full_reads": len(log["inputs"]), "fragment_reads": 0, "hash_only_reads": 0, "script_internal_reads": len(log["inputs"]), "actual_image_views": 0}
    log["scope"] = {"frozen_skill": r"D:\Temp\combat-extension-nws2d7rg\candidate\skills\combat-director", "output_directory": str(OUT), "network_used": False, "platform_tasks_submitted": False, "media_generated": False, "subagents_started": False, "skill_modified": False}
    log["verification"] = {"prompt_count": 2, "B_base_exactly_equals_A": True, "B_only_addition": extra.strip(), "media_results_verified": False}
    log["outputs"] = [{"path": str(OUT / "answer.md"), "sha256": hashlib.sha256((OUT / "answer.md").read_bytes()).hexdigest()}]
    log["status"] = "completed_offline_text_delivery"
    result = "PASS: two prompts present; B consists of the identical A text plus only the local motion blur paragraph. Offline answer and read/command record completed. No image viewing, network, platform submission, or media generation occurred."
except Exception:
    code = 1
    result = traceback.format_exc()
lookup = OUT / f"lookup-{len(log['commands']) + 1}.txt"
lookup.write_text(result, encoding="utf-8")
log["commands"].append({"command_argv": sys.orig_argv, "exit_code": code, "tool_output": str(lookup)})
(OUT / "run.json").write_text(json.dumps(log, ensure_ascii=False, indent=2), encoding="utf-8")
print(result)
sys.exit(code)
