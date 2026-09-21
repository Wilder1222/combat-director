import json
import runpy
import sys
from pathlib import Path

ROOT = Path(r'D:\Temp\combat-director-evals-20260921\final-e02')
SKILL = Path(r'D:\study\projects\combat-director\evals\candidates\0.5.0\skills\combat-director')
INPUT = Path(r'D:\study\projects\combat-director\evals\baselines\0.2.0\skills\combat-director\examples\grounded-15.plan.json')
seen = set()
enabled = True

def audit(event, args):
    if not enabled or event != 'open' or not isinstance(args[0], (str, bytes)):
        return
    mode = args[1]
    if isinstance(mode, str) and any(c in mode for c in 'wax'):
        return
    path = Path(args[0]).absolute()
    if path == INPUT or path.is_relative_to(SKILL) or path.is_relative_to(ROOT):
        seen.add(str(path))

sys.dont_write_bytecode = True
sys.addaudithook(audit)
command = sys.argv[1:]
sys.argv = [str(SKILL / 'scripts' / 'combat_tool.py'), *command]
exit_code = 0
try:
    runpy.run_path(sys.argv[0], run_name='__main__')
except SystemExit as exc:
    exit_code = exc.code or 0
finally:
    enabled = False
    with (ROOT / 'work' / 'tool-reads.jsonl').open('a', encoding='utf-8') as stream:
        stream.write(json.dumps({'command': command, 'exit_code': exit_code, 'read_files': sorted(seen)}, ensure_ascii=False) + '\n')
sys.exit(exit_code)
