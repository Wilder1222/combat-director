import pathlib,json,hashlib
ROOT=pathlib.Path(r'D:\Temp\combat-extension-nws2d7rg'); OUT=ROOT/'reviews/E09-E12'
targets=[('runs/E09/answer.md',1,21),('runs/E09/answer.md',100,130),('candidate/skills/combat-director/scripts/combat_tool.py',1,48),('candidate/skills/combat-director/scripts/combat_handoff.py',1,240)]
for rel,start,end in targets:
 p=ROOT/rel; raw=p.read_bytes(); s=raw.decode('utf-8-sig'); lines=s.splitlines()
 with (OUT/'reads.jsonl').open('a',encoding='utf-8') as f:f.write(json.dumps({'path':str(p),'sha256':hashlib.sha256(raw).hexdigest(),'bytes':len(raw),'read_range':{'bytes':[0,len(raw)],'lines':[1,len(lines)]},'displayed_lines':[start,min(end,len(lines))],'purpose':'selected evidence; full decode for hash and slicing'},ensure_ascii=False)+'\n')
 print('FILE',rel)
 for i in range(start,min(end,len(lines))+1):print(f'{i}: {lines[i-1]}')
