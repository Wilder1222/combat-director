import hashlib
import json
from pathlib import Path
import runpy
import sys

root = Path(r'D:\Temp\combat-library-behavior-j75bzt8f\candidate\skills\combat-director').resolve()
out = Path(r'D:\Temp\combat-library-behavior-j75bzt8f\runs\candidate-L08').resolve()
tag, *args = sys.argv[1:]
script = root / 'scripts' / 'library_tool.py'
observed = set()
recording = True

def audit(event, values):
    if not recording or event != 'open':
        return
    raw = values[0]
    if not isinstance(raw, (str, bytes)):
        return
    try:
        p = Path(raw).resolve()
        p.relative_to(root)
    except (ValueError, OSError, TypeError):
        return
    observed.add(str(p))

sys.addaudithook(audit)
sys.argv = [str(script), *args]
sys.path.insert(0, str(script.parent))
exit_code = 0
try:
    runpy.run_path(str(script), run_name='__main__')
except SystemExit as e:
    exit_code = e.code if isinstance(e.code, int) else (0 if e.code is None else 1)
except BaseException:
    exit_code = 1
    raise
finally:
    recording = False
    evidence = []
    for name in sorted(observed):
        p = Path(name)
        if p.is_file():
            evidence.append({'path': name, 'sha256': hashlib.sha256(p.read_bytes()).hexdigest(), 'read_mode': 'script_internal_read'})
    (out / ('runtime-' + tag + '.json')).write_text(json.dumps({'script': str(script), 'arguments': args, 'exit_code': exit_code, 'files': evidence}, ensure_ascii=False, indent=2), encoding='utf-8')
sys.exit(exit_code)
