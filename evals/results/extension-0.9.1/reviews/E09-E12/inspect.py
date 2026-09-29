import sys,json,hashlib,pathlib,difflib
ROOT=pathlib.Path(r'D:\Temp\combat-extension-nws2d7rg')
OUT=ROOT/'reviews/E09-E12'
ledger=OUT/'reads.jsonl'
def read(rel):
 p=ROOT/rel
 raw=p.read_bytes(); s=raw.decode('utf-8-sig')
 with ledger.open('a',encoding='utf-8') as f: f.write(json.dumps({'path':str(p),'sha256':hashlib.sha256(raw).hexdigest(),'bytes':len(raw),'read_range':{'bytes':[0,len(raw)],'lines':[1,len(s.splitlines())]},'purpose':sys.argv[1]},ensure_ascii=False)+'\n')
 return s
def diff(a,b,path='$'):
 if type(a)!=type(b): print(path,repr(a),'->',repr(b)); return
 if isinstance(a,dict):
  for k in sorted(a.keys()|b.keys()):
   if k not in a or k not in b: print(path+'.'+k,repr(a.get(k)),'->',repr(b.get(k)))
   else: diff(a[k],b[k],path+'.'+k)
 elif isinstance(a,list):
  for i in range(max(len(a),len(b))):
   if i>=len(a) or i>=len(b): print(path+f'[{i}]',repr(a[i] if i<len(a) else None),'->',repr(b[i] if i<len(b) else None))
   else: diff(a[i],b[i],path+f'[{i}]')
 elif a!=b: print(path,repr(a),'->',repr(b))
mode=sys.argv[1]
if mode=='diff':
 a=json.loads(read('runs/E09/original.plan.json')); b=json.loads(read('runs/E09/revised.plan.json'))
 diff(a,b)
 print('PROMPT DIFF')
 print(''.join(difflib.unified_diff(read('runs/E09/original.prompt.txt').splitlines(True),read('runs/E09/export/prompt.txt').splitlines(True))))
elif mode=='lines':
 for rel in sys.argv[2:]:
  print('\nFILE:',rel)
  for i,line in enumerate(read(rel).splitlines(),1): print(f'{i}: {line}')
elif mode=='keys':
 for rel in sys.argv[2:]:
  obj=json.loads(read(rel)); print(rel); print(json.dumps(obj,ensure_ascii=False,indent=2))
