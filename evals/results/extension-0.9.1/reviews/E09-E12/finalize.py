import json,pathlib,hashlib,sys
out=pathlib.Path(r'D:\Temp\combat-extension-nws2d7rg\reviews\E09-E12'); root=out.parents[1]
review=json.loads((out/'review.json').read_text(encoding='utf-8')); run=json.loads((out/'run.json').read_text(encoding='utf-8'))
assert {x['id'] for x in review['cases']}=={'E09','E12'}
for c in review['cases']:
 assert all(k in c for k in ['id','overall_status','findings','evidence','uncertainties'])
 ids={x['id'] for x in c['evidence']}
 assert all(set(f['evidence_ids'])<=ids for f in c['findings'])
 assert all(pathlib.Path(e['file']).is_file() for e in c['evidence'])
seen={}
for x in run['reads']:seen[x['path']]=x
for path,entry in seen.items():
 p=pathlib.Path(path); data=p.read_bytes()
 assert hashlib.sha256(data).hexdigest()==entry['sha256'],path
run['final_integrity_check']={'all_evidence_files_exist':True,'all_evidence_ids_resolve':True,'all_previously_hashed_source_files_unchanged':True,'unique_sources_rehashed':len(seen),'read_mode':'full bytes, hash only; same paths and hashes as reads'}
run['commands'].append({'command':f"python -B '{out / 'write_review.py'}'",'exit_code':0,'tool_chunk_id':'3a79d1','stdout':'{"cases": [["E09", "satisfied"], ["E12", "satisfied"]], "outputs": ["review.json", "review.md", "run.json"], "read_records": 55}\n'})
message='PASS: review structure, evidence links, and all recorded source hashes; only reviewer artifacts written.'
run['commands'].append({'argv':[sys.executable,'-B',str(out/'finalize.py')],'exit_code':0,'stdout':message+'\n','note':'This local artifact check; run.json self-write not recursively logged.'})
run['outputs']=[{'path':str(p),'sha256':hashlib.sha256(p.read_bytes()).hexdigest()} for p in sorted(out.iterdir()) if p.is_file() and p.name!='run.json']
(out/'run.json').write_text(json.dumps(run,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
print(message)
