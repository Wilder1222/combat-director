import sys,json,pathlib,hashlib,subprocess,os
sys.path.insert(0,str(pathlib.Path(__file__).parent))
# Standalone audit; no writes outside the reviewer directory.
ROOT=pathlib.Path(r'D:\Temp\combat-extension-nws2d7rg'); OUT=ROOT/'reviews/E09-E12'; ledger=OUT/'reads.jsonl'
def read(rel, purpose='independent_check'):
 p=ROOT/rel; raw=p.read_bytes(); s=raw.decode('utf-8-sig')
 with ledger.open('a',encoding='utf-8') as f:f.write(json.dumps({'path':str(p),'sha256':hashlib.sha256(raw).hexdigest(),'bytes':len(raw),'read_range':{'bytes':[0,len(raw)],'lines':[1,len(s.splitlines())]},'purpose':purpose},ensure_ascii=False)+'\n')
 return s.replace('\r\n','\n')
original=json.loads(read('runs/E09/original.plan.json')); revised=json.loads(read('runs/E09/revised.plan.json'))
checks={}
checks['export_plan_equals_revised']=revised==json.loads(read('runs/E09/export/combat-plan.json'))
checks['verified_plan_equals_revised']=revised==json.loads(read('runs/E09/revised.verified.plan.json'))
checks['plan_export_bytes_equal']=(ROOT/'runs/E09/revised.plan.json').read_bytes()==(ROOT/'runs/E09/export/combat-plan.json').read_bytes()
checks['untouched_beats']={original['beats'][i]['id']:original['beats'][i]==revised['beats'][i] for i in [0,1,2,5]}
checks['untouched_sections']={original['sections'][i]['id']:original['sections'][i]==revised['sections'][i] for i in [0,1,3]}
checks['all_cameras_equal']=all(a['camera']==b['camera'] for a,b in zip(original['beats'],revised['beats']))
checks['all_state_transitions_equal']=all(a['after']==b['before'] for a,b in zip(revised['beats'],revised['beats'][1:]))
checks['P03_entry_unchanged']=original['beats'][3]['before']==revised['beats'][3]['before']
checks['P03_exit_unchanged']=original['beats'][4]['after']==revised['beats'][4]['after']
checks['final_state_unchanged']=original['beats'][-1]['after']==revised['beats'][-1]['after']
answer=read('runs/E09/answer.md'); prompt=read('runs/E09/export/prompt.txt')
checks['answer_prompt_equals_export']=answer.split('```text\n')[1].split('\n```')[0].strip()==prompt.strip()
a=read('runs/E09/original.prompt.txt'); x='<时间段 7至12.5秒>'; y='<时间段 12.5至15秒>'
checks['prompt_outside_P03_unchanged']=a.split(x)[0]==prompt.split(x)[0] and a.split(y)[1]==prompt.split(y)[1]
log=json.loads(read('runs/E09/run.json'))
checks['original_hashes_match_record']={pathlib.Path(x['path']).name:hashlib.sha256((ROOT/'runs/E09'/pathlib.Path(x['path']).name).read_bytes()).hexdigest()==x['sha256'] for x in log.get('inputs',[]) if pathlib.Path(x['path']).name in ('original.plan.json','original.prompt.txt')}
print(json.dumps(checks,ensure_ascii=False,indent=2)); (OUT/'independent-checks.json').write_text(json.dumps(checks,ensure_ascii=False,indent=2),encoding='utf-8')
print('REVISED RELEVANT FACTS')
for b in revised['beats'][3:]:print(json.dumps(b,ensure_ascii=False,indent=2))
print('REVISED SECTIONS'); print(json.dumps(revised['sections'],ensure_ascii=False,indent=2))
print('HANDOFF TOP-LEVEL AND REVIEW INPUT'); h=json.loads(read('runs/E09/export/prompt-handoff.json')); print(list(h)); print(json.dumps({k:v for k,v in h.items() if k not in ('sections','scopes')},ensure_ascii=False)[:800])
for rel in ['runs/E09/request.txt','runs/E12/request.txt']:
 print(rel,read(rel).strip())
commands=[]
for sub,filename in [('status','original.plan.json'),('status','revised.draft.plan.json'),('status','revised.plan.json'),('validate','revised.plan.json')]:
 cmd=[sys.executable,'-B',str(ROOT/'candidate/skills/combat-director/scripts/combat_tool.py'),sub,str(ROOT/'runs/E09'/filename)]
 p=subprocess.run(cmd,cwd=OUT,capture_output=True,text=True,encoding='utf-8',env={**os.environ,'PYTHONIOENCODING':'utf-8'})
 name=sub+'-'+filename+'.txt'; (OUT/name).write_text(p.stdout+p.stderr,encoding='utf-8'); commands.append({'argv':cmd,'cwd':str(OUT),'exit_code':p.returncode,'stdout':p.stdout,'stderr':p.stderr,'output':name}); print('COMMAND',cmd,'EXIT',p.returncode); print(p.stdout,p.stderr)
(OUT/'validation-commands.json').write_text(json.dumps(commands,ensure_ascii=False,indent=2),encoding='utf-8')

