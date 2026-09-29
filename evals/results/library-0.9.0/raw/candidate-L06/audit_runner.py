import hashlib
import json
from pathlib import Path
import runpy
import sys

skill_root = Path(sys.argv[1]).resolve()
audit_path = Path(sys.argv[2]).resolve()
target = skill_root / "scripts" / "library_tool.py"
cli_args = sys.argv[3:]
events = set()
recording = True

def audit(event, args):
    if not recording or event != "open":
        return
    value = args[0]
    if not isinstance(value, (str, bytes)):
        return
    try:
        path = Path(value).resolve()
        path.relative_to(skill_root)
    except (TypeError, ValueError, OSError):
        return
    mode = args[1]
    if mode is None or "r" in str(mode):
        events.add(str(path))

sys.addaudithook(audit)
sys.argv = [str(target), *cli_args]
sys.path.insert(0, str(target.parent))
code = 0
try:
    runpy.run_path(str(target), run_name="__main__")
except SystemExit as exc:
    code = exc.code if isinstance(exc.code, int) else (0 if exc.code is None else 1)
finally:
    recording = False
    records = []
    for name in sorted(events):
        path = Path(name)
        if path.is_file():
            records.append({"path": name, "sha256": hashlib.sha256(path.read_bytes()).hexdigest(), "read_mode": "script_internal_read"})
    audit_path.write_text(json.dumps({"script": str(target), "arguments": cli_args, "exit_code": code, "reads": records}, ensure_ascii=False, indent=2), encoding="utf-8")
sys.exit(code)

