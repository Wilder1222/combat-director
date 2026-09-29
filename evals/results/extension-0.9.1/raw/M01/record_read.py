import hashlib
import json
import pathlib
import sys
import traceback

sys.stdout.reconfigure(encoding="utf-8")
OUT = pathlib.Path(__file__).resolve().parent
LOG = OUT / "run.json"
log = json.loads(LOG.read_text(encoding="utf-8"))
lookup_number = len(log["commands"]) + 1
lookup = OUT / f"lookup-{lookup_number}.txt"
code = 0
pieces = []
try:
    for name in sys.argv[1:]:
        path = pathlib.Path(name).resolve()
        raw = path.read_bytes()
        digest = hashlib.sha256(raw).hexdigest()
        text = raw.decode("utf-8-sig")
        log["inputs"].append({"path": str(path), "sha256": digest,
                              "read_mode": "full", "script_internal_read": True,
                              "actual_image_view": False})
        pieces.append(f"FILE: {path}\nSHA-256: {digest}\n\n{text}")
        if path.name == "request.txt":
            log["request"] = {"path": str(path), "sha256": digest, "text": text}
except Exception:
    code = 1
    pieces.append(traceback.format_exc())
rendered = "\n\n".join(pieces)
lookup.write_text(rendered, encoding="utf-8")
log["commands"].append({"command_argv": sys.orig_argv, "exit_code": code,
                         "tool_output": str(lookup)})
LOG.write_text(json.dumps(log, ensure_ascii=False, indent=2), encoding="utf-8")
print(rendered)
sys.exit(code)
