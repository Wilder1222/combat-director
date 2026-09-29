from pathlib import Path
import json, hashlib
OUT=Path(__file__).resolve().parent
compiled=json.loads((OUT/'review-input.json').read_text(encoding='utf-8-sig'))
checks={
'headers':{
'identity_action':'逐项对照cast与总设定：A为青衣行者、右手直剑、通过后停手；B为黑衣拦路者、右手短刀、阻路。人物、服装与目标未改。与原计划逐字段比较确认6拍人物攻防、表演、声音和状态不变。',
'camera_timing':'总时长15秒、16:9、single、one-take与facts一致；0.2秒入点与0.6秒出点计入总长，result_at仍14.4。另对照六拍path：全为S01南侧固定双人全身，开场预留全部行走与兵器范围，不移动或变焦；所有主段已传递该意图。自然模糊局限快移端部，不靠慢放、定格或关一帧模糊换清楚。',
'ability_cost':'rules为fantasy=false、max_scale=person且abilities为空。少量刃端运动模糊属于成像，不添加剑气、分身或离体攻击；与原火花、浮尘分别表达。未编造快门数值或平台参数。',
'continuity':'initial_state仍A官道西侧、B中部、机位南侧；ending_state仍A通过后转身右手剑略低，B北侧原位一膝触地右手空、刀在身侧。固定画框预留终点空间；模糊随运动收束，最后0.6秒呼吸与尘土可继续。此为文本一致性复核，未验证视频或实际构图效果。'},
'P01':{
'identity_action':'对照B01的A迎接后轻退与B逼近一次交接、B02的A后退两步且每次收剑恢复重心与B连续跟进，摘要保留三次分开的交接；右手直剑/短刀未替换，双方表演仍紧张与主动压迫。',
'camera_timing':'P01覆盖B01 0-2秒与B02 2-4.5秒，S01由start转continuous。两拍原横移跟随已替换，摘要明确南侧固定双人全身与画框全片不变、静止背景稳定；快移端部短弧自然模糊允许，握持、接触与回收/退步可追踪。',
'ability_cost':'只保留交接处少量真实火花、浮尘与碰撞声，B02火花不拖成光线；快移刃端模糊不作为环境留存物，不添加超自然能力。',
'continuity':'B01.before等于initial_state，B02.before等于B01.after；段末摘要A道路中部站住且剑已收回、B北侧附近前压且短刀身前与B02.after逐项一致，并由B03.before继承。后退擦痕与尘土保留。'},
'P02':{
'identity_action':'4.5-7秒仅含B03。摘要保留A站稳侧身接压、目光转向重心，B短刀受挡后收回身体；未删交接或把恢复改成新攻击，双方呼吸与视线表达与细拍一致。',
'camera_timing':'B03仍S01/continuous/南侧，原小幅前跟已换同一固定双人全身框；摘要保留双脚、持械手和交接区，背景稳定。局部短弧模糊随动作减缓收束，接触、侧身受力及B身体回收可追踪；正常速度没有放慢或冻结。',
'ability_cost':'abilities与ability_ids为空，无新增效果；衣摆与尘土继续变化属于原环境反馈，与刃端运动减缓后的模糊收束无冲突。',
'continuity':'从B02.after的A剑已收回、B北侧前压出发；段末为A稳定侧身持右手剑、B靠近碎石前压后回收，摘要对应B03.after并由B04.before继承。'},
'P03':{
'identity_action':'逐句对照B04和B05：A进步交锋逼B实际后退踩入碎石，继而最后交接带偏B持刀手；B失衡松指、短刀掉到身侧、一膝触地，A见失位停攻。摘要保留两次交接、全部落刀因果，未新增伤亡或攻击。',
'camera_timing':'P03覆盖7-10与10-12.5秒，两拍均S01 continuous。原横移/后退拍落刀已完全替换为南侧固定全身；预留碎石带、松手到落地路径与双方头脚。模糊仅沿挥动短弧及落刀下落路径，接触与回收、松手到落地可追踪；刀落地静止后不留漂浮拖尾。',
'ability_cost':'只保留短小火花、碎石滚动和落刀一点尘土，无伤口或能量波；模糊没有被解释成新的兵器、残影实体或攻击效果。',
'continuity':'B04.before继承B03.after，B04.after仍B实际退到北缘且右手持刀，B05才松手；P03末A停攻右手剑警戒，B右手空、一膝触地、刀在身侧，与B05.after一致并传入B06.before。环境变化保留。'},
'P04':{
'identity_action':'对照B06与摘要：A从空隙通过、两步后转身、14.4秒前安全距离剑尖略低；B原位一膝触地抬头看A且不捡刀，不开启新回合。保持双方呼吸、B手掌支撑和落刀原位。',
'camera_timing':'P04为12.5-15秒S01 continuous，原后侧平移拉开已替换为同一南侧固定全身画框到结束；A最终位置、B和刀均在预留画框内。转身快移剑尖可少量自然模糊，转身与收势仍可追踪，14.4秒前收势后无持续拖尾；末0.6秒自然呼吸无定格。',
'ability_cost':'无新增能力或特效。落刀已停不产生长尾，衣摆与尘土的原有变化和呼吸/竹林风声继续，不将粒子沉降与曝光模糊混为一谈。',
'continuity':'B06.before等于B05.after；summary.continuity与B06.after的A通过转身、右手剑略低，B北侧原位一膝触地右手空相符；环境字段继续保留身侧落刀并在最后0.6秒沉尘，总设定结尾也一致。'}
}
receipt={'plan_id':compiled['plan_id'],'reviews':[]}
for item in compiled['scopes']:
    scope=item['scope']
    receipt['reviews'].append({'scope':scope,'input_digest':item['input_digest'],'expression_digest':item['expression_digest'],'reviewer':'Codex 本次文本复核 2026-09-23','method':'agent','checks':checks[scope]})
(OUT/'review-receipt.json').write_text(json.dumps(receipt,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
notes=['# 本次文本复核凭证','', '实际对照 review-input.json 中五个 scope 的 facts 与 expression，并对照原计划动作与结尾。仅为文字复核，未生成或查看视频；不证明平台执行或实际画面效果。','']
for item in receipt['reviews']:
    notes += ['## '+item['scope'],'','- 事实摘要哈希：'+item['input_digest'],'- 表达哈希：'+item['expression_digest'],'']
    notes += ['- '+name+'：'+value for name,value in item['checks'].items()]
    notes += ['']
(OUT/'text-review.md').write_text('\n'.join(notes),encoding='utf-8')
run=json.loads((OUT/'run.json').read_text(encoding='utf-8'))
for p in [OUT/'review-input.json',Path(__file__)]:
    run['files_read'].append({'path':str(p),'sha256':hashlib.sha256(p.read_bytes()).hexdigest()})
run['commands'] += [
{'command':"Get-Content -Raw -LiteralPath '"+str(OUT/'review-input.json')+"'",'exit_code':0,'result':'Read compiled review facts/expressions; display omitted part of P02, then read P02 separately.'},
{'command':"$review = Get-Content -Raw -LiteralPath '"+str(OUT/'review-input.json')+"' | ConvertFrom-Json\n$review.scopes | Where-Object { $_.scope -eq 'P02' } | ConvertTo-Json -Depth 50",'exit_code':0,'result':'Read full P02 facts and expression, including previously truncated subsection.'},
{'command':'python -B '+str(Path(__file__)),'exit_code':0,'result':'Stored specific semantic conclusions and current digest pairs for headers, P01, P02, P03, P04.'}]
(OUT/'run.json').write_text(json.dumps(run,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
print('Stored 5 actual text reviews in review-receipt.json and text-review.md')
