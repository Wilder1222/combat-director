import sys
import runpy
import json
import hashlib
from pathlib import Path

root = Path(r'D:\Temp\combat-library-behavior-j75bzt8f\baseline\skills\combat-director').resolve()
out = Path(r'D:\Temp\combat-library-behavior-j75bzt8f\runs\baseline-L02')
seen = set()
active = True

def audit(event, args):
    if active and event == 'open' and args and isinstance(args[0], (str, bytes)):
        try:
            p = Path(args[0]).resolve()
            p.relative_to(root)
            seen.add(str(p))
        except (ValueError, TypeError, OSError):
            pass

sys.addaudithook(audit)
command_args = sys.argv[1:]
sys.argv = [str(root / 'scripts' / 'library_tool.py')] + command_args
code = 0
try:
    runpy.run_path(sys.argv[0], run_name='__main__')
except SystemExit as ex:
    code = ex.code if isinstance(ex.code, int) else (0 if ex.code is None else 1)
finally:
    active = False
    records = []
    for name in sorted(seen):
        p = Path(name)
        if p.is_file():
            records.append({'path': str(p), 'sha256': hashlib.sha256(p.read_bytes()).hexdigest(), 'read_mode': 'script_internal_read'})
    (out / 'script-input-evidence.json').write_text(json.dumps(records, ensure_ascii=False, indent=2), encoding='utf-8')
sys.exit(code)
