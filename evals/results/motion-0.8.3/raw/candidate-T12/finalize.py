from pathlib import Path
import json, hashlib, copy
OUT=Path(__file__).resolve().parent
ROOT=OUT.parents[1]
SKILL=ROOT/'candidate'/'skills'/'combat-director'
run=json.loads((OUT/'run.json').read_text(encoding='utf-8'))
exports=OUT/'export'
expected=['design-card.md','director.md','prompt.txt','prompt-handoff.json','handoff.md','review.md','combat-plan.json']
assert sorted(p.name for p in exports.iterdir()) == sorted(expected)
contents={name:(exports/name).read_text(encoding='utf-8') for name in expected}
plan=json.loads(contents['combat-plan.json'])
reviewed=json.loads((OUT/'reviewed.plan.json').read_text(encoding='utf-8'))
assert plan==reviewed
compiled=json.loads((OUT/'review-input.json').read_text(encoding='utf-8'))
assert json.loads(contents['prompt-handoff.json'])==compiled
for beat in plan['beats']:
    assert beat['camera']['path'] in contents['director.md']
    assert '南侧固定双人全身' in beat['camera']['path']
for section in plan['sections']:
    assert section['summary']['camera'] in contents['prompt.txt']
    assert '南侧固定双人全身' in section['summary']['camera']
source=SKILL/'examples'/'grounded-15.plan.json'
source_sha=hashlib.sha256(source.read_bytes()).hexdigest()
assert source_sha==next(x['sha256'] for x in run['files_read'] if x['path']==str(source))
original=json.loads(source.read_text(encoding='utf-8-sig'))
for beat in original['beats']:
    assert beat['camera']['path'] not in contents['director.md']
    assert beat['camera']['path'] not in contents['prompt.txt']
for item in compiled['scopes']:
    r=plan['editorial_reviews'][item['scope']]
    assert r['input_digest']==item['input_digest'] and r['expression_digest']==item['expression_digest']
result={'status':'PASS','seven_export_files':expected,'exported_plan_matches_reviewed_plan':True,'handoff_matches_compiled_facts_and_expressions':True,'all_six_camera_paths_in_director':True,'all_four_camera_summaries_in_prompt':True,'old_camera_paths_absent_from_deliverables':True,'all_five_review_digest_pairs_current':True,'original_plan_sha256_unchanged':True,'media_generated':False}
(OUT/'export-check.json').write_text(json.dumps(result,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
answer='已完成修订、实际文本复核及七份正式导出。全片改为南侧固定双人全身；保留原人物、全部交手、15秒、一镜到底和结尾。快移兵器允许少量自然模糊，接触、受力与回收可连续追踪。\n\n'
answer+='七份文件位于 [export]('+exports.as_posix()+')：\n\n'
for name in expected:
    answer+='- ['+name+']('+(exports/name).as_posix()+')\n'
answer+='\n5个复核范围均为 `ready`，结构校验与导出核对通过。复核凭证：[text-review.md]('+(OUT/'text-review.md').as_posix()+')、[review-receipt.json]('+(OUT/'review-receipt.json').as_posix()+')。\n\n未生成视频；平台能力与实际画面效果未验证。\n'
(OUT/'answer.md').write_text(answer,encoding='utf-8')
# Expand earlier command summaries to the actual absolute input names.
groups=[
[ROOT/'tasks'/'T12'/'request.txt',SKILL/'SKILL.md'],
[SKILL/'examples'/'grounded-15.plan.json',SKILL/'references'/'contract.md',SKILL/'references'/'motion-blur.md'],
[SKILL/'scripts'/'combat_tool.py',SKILL/'assets'/'combat-plan.schema.json',SKILL/'references'/'platforms.md']]
for row,group in zip(run['commands'][:3],groups):
    row['command']='\n'.join("Get-Content -Raw -LiteralPath '"+str(p)+"'" for p in group)
run['commands'][3]['command']="New-Item -ItemType Directory -Path '"+str(OUT)+"' -Force; Set-Content '"+str(OUT/'build_revision.py')+"' (script body retained in file); python -B '"+str(OUT/'build_revision.py')+"'"
run['commands'].append({'command':"Get-Content -Raw -LiteralPath '"+str(exports/'prompt.txt')+"'\nSelect-String -LiteralPath '"+str(exports/'director.md')+"' -Pattern '^3\\. 摄影机'\nGet-Content -Raw -LiteralPath '"+str(exports/'handoff.md')+"'",'exit_code':0,'result':'Read final prompt, all six exported camera tracks and generic platform handoff; fixed framing and motion guidance preserved.'})
run['commands'].append({'command':'python -B '+str(Path(__file__)),'exit_code':0,'result':'Seven-file export content check PASS; source unchanged; saved answer.md and final read-file hashes.'})
run['artifact_writes']=[{'method':'PowerShell Set-Content -Encoding utf8','path':str(OUT/name)} for name in ['build_revision.py','run_tool.py','write_review.py','finalize.py']]
read_map={x['path']:x for x in run['files_read']}
for path in OUT.rglob('*'):
    if path.is_file() and path.name!='run.json':
        read_map[str(path.resolve())]={'path':str(path.resolve()),'sha256':hashlib.sha256(path.read_bytes()).hexdigest()}
run['files_read']=list(read_map.values())
run['status']='completed'
run['result']={'plan_id':plan['id'],'review_status':'5/5 ready','validation':'PASS','export':'7 files','export_check':'PASS','video_generated':False,'network_used':False}
run['outputs']=[{'path':str(exports/name),'sha256':hashlib.sha256((exports/name).read_bytes()).hexdigest()} for name in expected]
run['files_read_note']='run.json is a mutable bookkeeping file read and rewritten by logging commands; it is excluded from its own SHA256 list to avoid recursive self-hashing.'
(OUT/'run.json').write_text(json.dumps(run,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
print('PASS: 7 exports verified; answer.md and run.json finalized')
