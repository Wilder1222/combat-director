from pathlib import Path
import json, hashlib, copy
ROOT = Path(r'D:\Temp\combat-motion-eval-e1dsw32j')
OUT = ROOT/'results'/'candidate-T12'
SKILL = ROOT/'candidate'/'skills'/'combat-director'
source = SKILL/'examples'/'grounded-15.plan.json'
original = json.loads(source.read_text(encoding='utf-8-sig'))
plan = copy.deepcopy(original)
plan['id'] = 'grounded-15-fixed-south'
plan['provenance'] += ' 本修订按用户要求只调整摄影机与运动成像表达：全片南侧固定双人全身；保留全部原交手、人物、状态、时长与结尾。已完成情况以本次文本复核凭证为准。'
plan['editorial_reviews'] = {}
fixed = '南侧固定双人全身机位；机位、朝向、焦距和画框全片不变，不平移、不推进后退、不摇摄、不变焦。开拍前取景覆盖双方从开场至通过后的全部行走范围、头脚、完整兵器运动范围、北缘碎石带与落刀点；人物移动发生在同一画框内，远处石桥与静止地面保持稳定。'
blur = '正常速度与一致成像观感；快移剑尖、刀尖只沿实际运动方向呈少量短暂自然边缘模糊，转动时沿短弧线；双方持械手、接触关系、受力和回收仍可连续追踪。模糊随相对画面的运动变化，收势后不留下悬浮拖尾；火花和浮尘按原有环境反馈独立结束。'
plan['headers']['goal'] += '\n全片为南侧固定双人全身画面，正常速度，保持全部交手；不以慢放、定格或切镜换取接触可读。'
plan['headers']['scene'] = plan['headers']['scene'].replace('主要机位保持场景南侧，人物位置变化通过可见移动完成', fixed)
plan['headers']['continuity'] += '\n' + blur
paths = [
    fixed + 'B01中B起刀、A迎接、首次接触和接触后轻退都在画内；快移剑尖与刀尖允许沿挥动弧线少量自然模糊，右手握持、交刃和分离后的回收可追踪；背景不随挥刀横拖。',
    '延续同一南侧固定双人全身画框，机位、朝向与焦距不动；A两次后退及B跟进均在画内，石桥与静止地面稳定。兵器快移端部可有顺实际短弧轨迹的少量自然模糊；两次接触各自分开可辨，收剑、恢复重心及B持刀回收可连续追踪，不靠跟拍维持构图。',
    '延续同一南侧固定双人全身画框，机位、朝向与焦距不动；双脚、双方持械手和交接区同时入画，背景稳定。迎挡时快移剑尖、刀尖可有局部短弧自然模糊，接触、侧身受力和B收回身体仍可追踪；运动减缓后模糊随之收束，不单独关闭某一帧模糊。',
    '延续同一南侧固定双人全身画框，机位、朝向与焦距不动；A前进一步、B实际后退到北缘碎石带及双方落脚全在预留画面内，石桥与静止地面稳定。快移兵器端部沿实际挥动方向保留少量短暂自然模糊，交接、回收及B踩入碎石的因果可追踪。',
    '延续同一南侧固定双人全身画框，机位、朝向与焦距不动；同时保留双方头脚、交刃区、B松手位置和身侧落刀点。最后交接的快移刃端可有局部短弧自然模糊；落刀仅顺真实下落轨迹有少量短暂模糊，交接带偏持刀手、手指松开、脱手落地、一膝触地及A收势可连续追踪；背景稳定，落地静止后刀不留拖尾。',
    '延续同一南侧固定双人全身画框直到15秒，机位、朝向、焦距和构图不动；A通过、两步转身后的安全距离与B原位一膝触地均留在画内，落刀点始终可见，背景稳定。A转身时剑尖若快移仅有沿真实轨迹的少量自然模糊，转身、收剑警戒与握持可追踪；14.4秒前收势后刃端无持续拖尾，最后0.6秒保留呼吸、衣摆与尘土自然变化。'
]
for beat, path in zip(plan['beats'], paths):
    beat['camera']['path'] = path
summaries = [
    '南侧固定双人全身，机位、朝向、焦距与画框全片不变；双方头脚、完整兵器运动范围和北缘碎石带均入画，石桥与静止地面稳定。B01首次交接及B02两次交接全部保留；快移剑尖、刀尖沿真实挥动弧线允许少量短暂自然模糊，握持、各次接触、A轻退与两次退步、收剑恢复重心及B跟进回收均可追踪；不切镜、不慢放。',
    '延续同一南侧固定双人全身画框，机位、朝向与焦距不动，双脚、持械手和交接区可见，背景稳定。快移兵器端部只沿真实短弧产生少量自然模糊；A站稳侧身迎挡、接触受力与B收回身体连续可追踪，动作减缓后模糊随之收束，保持正常速度与一致成像观感。',
    '延续同一南侧固定双人全身画框，机位、朝向与焦距不动；A进步、B后退踩入碎石、双方全身和身侧落刀点同时留在画内，静止背景稳定。两次交接与回收可追踪，快移刃端仅顺真实挥动弧线有少量自然模糊；最后交接带偏B持刀手、松指脱手到落地、一膝触地及A停攻全过程可追踪，落刀模糊沿真实下落轨迹且落地静止后不留拖尾。',
    '延续同一南侧固定双人全身画框至15秒，机位、朝向、焦距与构图不动；A通过后两步转身至安全距离、B原位一膝触地及落刀均在画内，背景稳定。转身时快移剑尖允许沿真实轨迹的少量自然模糊，转身和收剑警戒可追踪；14.4秒前收势后没有持续拖尾，最后0.6秒保留呼吸、衣摆与尘土自然变化，正常速度、不切镜。'
]
for section, camera in zip(plan['sections'], summaries):
    section['summary']['camera'] = camera
# Scope preservation is a field-level comparison, not a media claim.
checks = {}
for key in ['schema_version','template','duration','aspect_ratio','generation','camera_mode','rules','timing','anchors','cast','abilities','references','initial_state']:
    assert plan[key] == original[key], key
    checks[key] = 'unchanged'
for old, new in zip(original['beats'], plan['beats']):
    a, b = copy.deepcopy(old), copy.deepcopy(new)
    a['camera'].pop('path'); b['camera'].pop('path')
    assert a == b, old['id']
checks['beats'] = 'All 6 beats identical except camera.path; actions, performance, timings, before/after, vfx, environment and sound preserved.'
for old, new in zip(original['sections'], plan['sections']):
    a, b = copy.deepcopy(old), copy.deepcopy(new)
    a['summary'].pop('camera'); b['summary'].pop('camera')
    assert a == b, old['id']
checks['sections'] = 'All 4 sections identical except summary.camera; grouping and all action/ending expressions preserved.'
(OUT/'revision.plan.json').write_text(json.dumps(plan,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
(OUT/'preservation-check.json').write_text(json.dumps(checks,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
paths_read = [ROOT/'tasks'/'T12'/'request.txt', SKILL/'SKILL.md', source, SKILL/'references'/'contract.md', SKILL/'references'/'motion-blur.md', SKILL/'scripts'/'combat_tool.py', SKILL/'assets'/'combat-plan.schema.json', SKILL/'references'/'platforms.md', Path(__file__)]
run = {'task_original': (ROOT/'tasks'/'T12'/'request.txt').read_text(encoding='utf-8-sig').strip(), 'model_exact_id':'未知','timing':{'overall_start':'未知','overall_duration':'未知'}, 'read_log_scope':'本任务读取的输入、技能快照、执行脚本和复核/导出产物；标准库运行时不列入文档清单。', 'files_read':[{'path':str(p.resolve()),'sha256':hashlib.sha256(p.read_bytes()).hexdigest()} for p in paths_read], 'commands':[{'command':'Get-Content -Raw -LiteralPath <request.txt>; Get-Content -Raw -LiteralPath <SKILL.md>','exit_code':0,'result':'Read user request and designated skill.'}, {'command':'Get-Content -Raw -LiteralPath <grounded-15.plan.json>; Get-Content -Raw -LiteralPath <references/contract.md>; Get-Content -Raw -LiteralPath <references/motion-blur.md>','exit_code':0,'result':'Read original plan, review/export contract and motion imaging guidance.'}, {'command':'Get-Content -Raw -LiteralPath <scripts/combat_tool.py>; Get-Content -Raw -LiteralPath <assets/combat-plan.schema.json>; Get-Content -Raw -LiteralPath <references/platforms.md>','exit_code':0,'result':'Read exporter and schema; combined display truncated; read offline handoff boundaries.'}, {'command':'New-Item -ItemType Directory <output>; Set-Content <output/build_revision.py>; python -B <output/build_revision.py>','exit_code':0,'result':'Created revised plan; all 6 beat actions/timings/states and 4 section non-camera expressions unchanged.'}], 'status':'revision_prepared'}
(OUT/'run.json').write_text(json.dumps(run,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
print('Prepared revision.plan.json; preservation check PASS')
