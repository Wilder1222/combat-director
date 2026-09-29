import json,pathlib,hashlib,ast
ROOT=pathlib.Path(r'D:\Temp\combat-extension-nws2d7rg'); OUT=ROOT/'reviews/E09-E12'
# Record the bundled sources and schema used by the completed read-only commands.
queue=[ROOT/'candidate/skills/combat-director/scripts/combat_tool.py']; seen=set()
while queue:
 p=queue.pop()
 if p in seen:continue
 seen.add(p); raw=p.read_bytes(); s=raw.decode('utf-8-sig')
 record={'path':str(p),'sha256':hashlib.sha256(raw).hexdigest(),'bytes':len(raw),'read_range':{'bytes':[0,len(raw)],'lines':[1,len(s.splitlines())]},'purpose':'bundled validator dependency; source hash and import inventory, not full semantic review'}
 with (OUT/'reads.jsonl').open('a',encoding='utf-8') as f:f.write(json.dumps(record,ensure_ascii=False)+'\n')
 for node in ast.walk(ast.parse(s)):
  if isinstance(node,ast.ImportFrom) and node.module and node.level==0:
   target=p.parent/(node.module+'.py')
   if target.is_file():queue.append(target)
p=ROOT/'candidate/skills/combat-director/assets/combat-plan.schema.json'; raw=p.read_bytes()
with (OUT/'reads.jsonl').open('a',encoding='utf-8') as f:f.write(json.dumps({'path':str(p),'sha256':hashlib.sha256(raw).hexdigest(),'bytes':len(raw),'read_range':{'bytes':[0,len(raw)]},'purpose':'schema loaded by validate; reviewer hash-only inventory'},ensure_ascii=False)+'\n')
# Obtain exact line evidence for retest instructions without reprinting the long prompt.
p=ROOT/'runs/E09/answer.md'; raw=p.read_bytes(); lines=raw.decode('utf-8-sig').splitlines()
print('E09 answer retest lines')
for i,line in enumerate(lines,1):
 if i>=89:print(f'{i}: {line}')
print('Bundled dependencies:',*[str(p) for p in sorted(seen)],sep='\n')
