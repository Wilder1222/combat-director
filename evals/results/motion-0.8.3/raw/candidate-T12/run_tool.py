from pathlib import Path
import sys, json, hashlib, io, contextlib, runpy, time
OUT = Path(__file__).resolve().parent
ROOT = OUT.parents[1]
TOOL = ROOT/'candidate'/'skills'/'combat-director'/'scripts'/'combat_tool.py'
args = sys.argv[1:]
seen = {Path(__file__).resolve()}
active = True
def audit(event,args):
    if event == 'open' and active and isinstance(args[0], (str,bytes)):
        p=Path(args[0]).absolute()
        mode=args[1]
        if str(p).lower().startswith(str(ROOT).lower()) and (not isinstance(mode,str) or not any(x in mode for x in 'wax')):
            seen.add(p)
sys.addaudithook(audit)
run = json.loads((OUT/'run.json').read_text(encoding='utf-8-sig'))
start=time.perf_counter()
capture=io.StringIO()
code=0
try:
    with contextlib.redirect_stdout(capture),contextlib.redirect_stderr(capture):
        sys.argv=[str(TOOL)]+args
        try:
            runpy.run_path(str(TOOL),run_name='__main__')
        except SystemExit as e:
            code=e.code if isinstance(e.code,int) else 1
finally:
    active=False
    elapsed=time.perf_counter()-start
    existing={x['path']:x for x in run['files_read']}
    for p in sorted(seen):
        if p.is_file() and p != OUT/'run.json':
            existing[str(p.resolve())]={'path':str(p.resolve()),'sha256':hashlib.sha256(p.read_bytes()).hexdigest()}
    run['files_read']=list(existing.values())
    run['commands'].append({'command':'python -B '+str(Path(__file__).resolve())+' '+' '.join(args),'underlying_command':'python -B '+str(TOOL)+' '+' '.join(args),'exit_code':code,'elapsed_seconds':round(elapsed,4),'result':capture.getvalue().strip()[:3000]})
    (OUT/'run.json').write_text(json.dumps(run,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
print(capture.getvalue(),end='')
raise SystemExit(code)
