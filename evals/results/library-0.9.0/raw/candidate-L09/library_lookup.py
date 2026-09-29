import hashlib
import json
import os
import runpy
import sys
from pathlib import Path

ROOT = Path(r'D:\Temp\combat-library-behavior-j75bzt8f\candidate\skills\combat-director')
OUT = Path(r'D:\Temp\combat-library-behavior-j75bzt8f\runs\candidate-L09')
tag, *arguments = sys.argv[1:]
reads = set()
capture = True

def audit(event, args):
    if not capture or event != 'open':
        return
    value = args[0]
    if not isinstance(value, (str, bytes, os.PathLike)):
        return
    path = Path(os.fsdecode(value)).resolve()
    if path.is_relative_to(ROOT):
        mode = args[1]
        if mode is None or 'r' in str(mode):
            reads.add(str(path))

sys.addaudithook(audit)
sys.argv = [str(ROOT / 'scripts' / 'library_tool.py'), *arguments]
try:
    runpy.run_path(sys.argv[0], run_name='__main__')
finally:
    capture = False
    entries = [{
        'path': value,
        'sha256': hashlib.sha256(Path(value).read_bytes()).hexdigest(),
        'read_mode': 'script_internal_read',
    } for value in sorted(reads) if Path(value).is_file()]
    (OUT / f'{tag}-internal-inputs.json').write_text(
        json.dumps(entries, ensure_ascii=False, indent=2), encoding='utf-8')
