import hashlib, json, pathlib, runpy, sys
root = pathlib.Path(r'D:\Temp\combat-library-behavior-j75bzt8f\candidate\skills\combat-director').resolve()
out = pathlib.Path(r'D:\Temp\combat-library-behavior-j75bzt8f\runs\candidate-L07')
seen = set()
def audit(event, args):
    if event == 'open' and isinstance(args[0], (str, bytes)):
        p = pathlib.Path(args[0]).resolve()
        if p.is_relative_to(root):
            seen.add(str(p))
sys.addaudithook(audit)
label, *argv = sys.argv[1:]
target = root / 'scripts' / 'library_tool.py'
sys.path.insert(0, str(target.parent))
sys.argv = [str(target), *argv]
code = 0
try:
    runpy.run_path(str(target), run_name='__main__')
except SystemExit as exc:
    code = exc.code or 0
finally:
    records = []
    for name in sorted(seen):
        p = pathlib.Path(name)
        if not p.is_file():
            continue
        records.append({'path': name, 'sha256': hashlib.sha256(p.read_bytes()).hexdigest(), 'reading': 'script_internal_read', 'direct_full_read': False})
    (out / (label + '-inputs.json')).write_text(json.dumps(records, ensure_ascii=False, indent=2), encoding='utf-8')
sys.exit(code)

