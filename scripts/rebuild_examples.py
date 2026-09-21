#!/usr/bin/env python3
"""Rebuild example plans from archived prompt attachments, with explicit editorial additions."""
from __future__ import annotations
import copy
import hashlib
import importlib.util
import json
import re
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
SKILL = ROOT / 'skills/combat-director'
SOURCE = ROOT / 'sources/attachments/2026-09-21'
spec = importlib.util.spec_from_file_location('combat_tool', SKILL / 'scripts/combat_tool.py')
tool = importlib.util.module_from_spec(spec)
spec.loader.exec_module(tool)

CONFIG = {
    'epic-30': {'template': 'epic', 'duration': 30, 'lead': .3, 'tail': .8,
                'splits': [3, 8, 13, 18.5, 24, None],
                'initial': ['戈壁西侧，面向B，右手银色直剑，准备接近', '东侧阻路，面向A，右手青色能量短刃'],
                'middle': [('交锋后稳住右脚，右手剑在身前', '接触后上身略退，收回右手短刃'),
                           ('三处印记外，双脚站稳，右手剑可见', '三处印记之间，追击被挡，收回短刃'),
                           ('圈外引导既有阵列，右手持剑', '圈中以右手短刃引出屏障'),
                           ('圈外退开，保留剑影能量，右手剑可见', '屏障破裂显露原身体，开始收拢青光'),
                           ('印记外缘接近最近印记，右手剑拨开飞石', '原站位风柱，核心转向落后')],
                'uses': [[], ['SWORD_GRID'], ['SWORD_GRID'], ['SWORD_GRID'], ['SWORD_GRID','CYAN_GUARD'],
                         ['SWORD_GRID','CYAN_GUARD'], ['SWORD_GRID','CYAN_GUARD'], ['WIND_FORM'], ['WIND_FORM'],
                         ['SWORD_GRID','SKY_SWORD','WIND_FORM'], ['SKY_SWORD','WIND_FORM']]},
    'grounded-15': {'template': 'grounded', 'duration': 15, 'lead': .2, 'tail': .6,
                    'splits': [2, None, 10, None],
                    'initial': ['官道西侧，面向B，右手直剑准备格挡', '官道中部，面向A，右手短刀准备前压'],
                    'middle': [('接刀后轻退，右手剑保持可见', '向A逼近，右手短刀完成接触'),
                               ('道路中部前进一步，右手剑在身前', '实际后退至北缘碎石带，右手仍持短刀')]},
    'colossus-30': {'template': 'colossus', 'duration': 30, 'lead': .3, 'tail': .8,
                    'splits': [None, 6.5, None, 18, None, None],
                    'initial': ['装卸场西侧，右手终端，朝东侧出口移动', '场地中央，四足着地，机械臂朝向A'],
                    'middle': [('沿北侧斜退避开机械臂，右手终端', '机械臂落在原前进位置，开始回收'),
                               ('红柱侧面，右手终端，左袖已有擦痕', '机械臂撞到挡板，机体惯性前移')]},
}

# Editorial per-beat refinements: these are additions, not recovered source data.
DETAILS = {
    'epic-30': {
        'environment': ['交锋脚步扬起少量浮尘，地面尚无印记', '前两处金白印记留在落点，尘土不遮挡脚步',
                        '第三处印记落地，与前两处保持可辨位置', '三处印记仍在，局部气流牵动细尘',
                        '三处印记围成的区域仍可辨认，细尘随阵列轻动', '两波冲击将尘土向外推，三处印记未被抹去',
                        '屏障碎片向外散，原角色与三处印记仍可辨认', '沙尘从原站位上升，孤岩与底部印记未全部遮没',
                        '脚步留下尘迹，碎石沿风柱切线掠过，落点连续', '三处印记加亮，尘土局部向上，既有阵列能量收回',
                        '尘土向外铺开，末尾0.8秒沉降，孤岩和角色仍可辨认'],
        'performance': [('盯住对手肩部与短刃，接触时下颌收紧','目光追随来剑，上身受力后回收呼吸'),
                        ('眼睛短扫地面落点，再回到对手','跟随A肩部，呼吸随着追赶加快'),
                        ('回身时目光锁定短刃，站稳后看印记','前压被挡，手臂收回时下颌变紧'),
                        ('视线越过剑锋锁定B，轻抿唇，呼吸加深','眼睛转向新出现的剑影，举刃准备防守'),
                        ('凝视阵列间隙，身体稳定，避免大幅动作','观察四周剑影，将短刃横在胸前'),
                        ('有力呼吸，视线追踪屏障裂纹','身体随两次接触震动，神情由自信转为戒备'),
                        ('随冲击后退仍盯住原角色，不提前看向天空','屏障破裂后短暂露出脸与身体，收拢青光'),
                        ('眉心收紧，停半拍呼吸后抬眼看核心','人形轮廓渐融入同色核心，方向仍朝A'),
                        ('沿路径观察印记与飞石，下颌紧绷','核心朝A缓慢转向，转向落后于移动'),
                        ('凝视剑尖落点后抬眼，支撑脚站稳','核心偏转但仍在三印记范围，未瞬移到A身前'),
                        ('明显呼气，肩部稍松，目光不离残余青光','缩小核心中留有人形轮廓，保持暂时受压状态')]
    },
    'grounded-15': {
        'environment': ['第一次交接带起少量浮尘，双方仍在官道', 'A后退擦痕保留，B逐步靠近北缘碎石带',
                        '衣摆迟于身体回落，既有尘土继续飘动', 'B脚步进入碎石带，碎石因落脚滚动',
                        '短刀松手到落地轨迹可见，掉落点留在B身侧', '落刀仍在原位，最后0.6秒尘土沉降'],
        'performance': [('盯住短刀和持刀手，接触后短呼气','眉眼压低，注意A上半身'),
                        ('退步时加快呼吸，眼睛不离对手','前压时呼吸逐渐加重，追随A肩部'),
                        ('抿唇后呼气，目光从刀尖转向对方重心','目光短追A侧移，收回身体时呼吸加重'),
                        ('迈步时锁定B支撑脚与道路空隙','退步时快速看向脚下碎石，身体努力恢复平衡'),
                        ('目光从落刀回到B，呼气后停手警戒','短暂惊讶，眼睛追向落刀，手掌准备支撑'),
                        ('肩部稍松，转身后仍看B，胸口起伏','目光追着A，呼吸更快，手掌支撑身体')]
    },
    'colossus-30': {
        'environment': ['机甲踩踏扬尘，空货架和出口可见', '机械臂接地压出痕迹，碎屑落回地面',
                        '悬架轻晃，绳索、导轨与红柱位置不变', '连续足印沿转向路线出现，没有无接触扬尘',
                        '防护挡板受撞变形，A左袖浅擦痕保留', '按钮触发后货架沿既有导轨下降，挡板变形保留',
                        '空货架落位后不移动，侧边旁路仍有空间', '出口与货架相对位置稳定，末尾0.8秒尘土沉降'],
        'performance': [('视线从出口转到机械臂，眉间收紧','琥珀灯持续亮起，机头跟随A'),
                        ('看清机械臂落点，后退时下颌紧绷','机械臂接地后开始减速回收，仍朝A'),
                        ('视线依次到货架、按钮、机甲，轻呼气','回收关节短暂减速，状态灯持续锁定'),
                        ('目光在机甲和按钮间切换，步伐变稳','机头先转，重心变化有延迟'),
                        ('避让时短呼气，眼睛仍追机械臂落点','碰撞后机身惯性前移，机械臂开始回收'),
                        ('按按钮后确认灯变，立刻看向出口','机头先追A，机体转向尚未完成'),
                        ('急促呼吸，回看一次间距再看出口','机械臂接触实体障碍，机头仍追踪A'),
                        ('长呼气，肩部稍松，确认出口前方','灯光仍亮，缓慢调整姿态表示威胁尚存')]
    }
}


def write_json(path, value):
    path.write_text(json.dumps(value, ensure_ascii=False, indent=2, allow_nan=False) + '\n', encoding='utf-8')


def rebuild(name, cfg):
    raw = (SOURCE / f'{name}.prompt.txt').read_text(encoding='utf-8-sig')
    text = raw.replace('此段结束：AB左前方', '此段结束：A位于B左前方')
    # Repair joined sentences while preserving archived originals.
    text = text.replace('随后，', '。随后，')
    if name == 'grounded-15':
        text = text.replace('短刀脱手落在身侧', '持刀手在交接中被剑格带偏，失衡时手指松开，短刀脱手落在身侧')
    chunks = re.split(r'<时间段 ([\d.]+)至([\d.]+)秒>\n', text)
    head = dict(re.findall(r'<([^>]+)>\n(.*?)(?=\n\n<|\Z)', chunks[0], re.S))
    headers = {k: head[label].strip() for k, label in [('goal','创作目标'),('cast','人物与目标'),('scene','场景与规则'),('budget','时间预算')]}
    headers['continuity'] = text.split('<全程连续性>\n')[1].strip()
    cast = []
    for line in headers['cast'].splitlines():
        match = re.match(r'([AB]) (.*?)：(.+?)；兵器：(.+?)；持械：(.+?)。目标：(.+?)。表演基调：(.+)', line)
        if not match:
            raise ValueError(f'Cannot parse cast: {line}')
        aid, label, appearance, prop, hand, goal, performance = match.groups()
        cast.append({'id':aid,'description':label+'：'+appearance,'goal':goal,'prop':prop,'hand':hand})
    abilities = []
    for line in headers['scene'].splitlines():
        m = re.match(r'能力(\w+)归属([AB])：(.+?)，表现为(.+?)；限制：(.+?)；代价：(.+?)。$', line)
        if m:
            aid, owner, trigger, visual, limit, cost = m.groups()
            ends = {'SWORD_GRID':'能量命中消散或被主动收回后结束','SKY_SWORD':'压制完成后不重复落剑','CYAN_GUARD':'屏障破裂后结束','WIND_FORM':'被巨剑压制后核心缩小，原角色仍在'}
            abilities.append({'id':aid,'owner':owner,'trigger':trigger,'visual':visual,'limit':limit,'cost':cost,
                              'end_condition':ends[aid],'scale':'arena','supernatural':True})
    anchors = re.search(r'空间锚点：(.+)', headers['scene'])[1].split('；')
    state = {'A':cfg['initial'][0],'B':cfg['initial'][1],'environment':'初始场景完整；'+ '；'.join(anchors),'camera_side':'南侧'}
    plan = {'schema_version':'1.2','editorial_reviews':{},'id':name,'provenance':'由2026-09-21用户附件提示词重建；细节拍时间、阶段状态及能力结束条件是本项目编辑补充，不是遗失原计划的恢复；未生成视频。',
            'template':cfg['template'],'duration':cfg['duration'],'aspect_ratio':'16:9','generation':'single',
            'camera_mode':'one-take' if name=='grounded-15' else 'multi-shot','headers':headers,
            'rules':{'fantasy':cfg['template']=='epic','max_scale':'arena' if cfg['template']!='grounded' else 'person'},
            'timing':{'lead_in':cfg['lead'],'tail_out':cfg['tail'],'result_at':cfg['duration']-cfg['tail']},
            'anchors':anchors,'cast':cast,'abilities':abilities,'references':[],'initial_state':copy.deepcopy(state),'beats':[],'sections':[]}
    middle_index = 0
    for group, offset in enumerate(range(1,len(chunks),3)):
        start, end = float(chunks[offset]), float(chunks[offset+1])
        body = chunks[offset+2].split('<全程连续性>')[0]
        tagged = dict(re.findall(r'<([^>]+)> ([^\n]+)', body))
        summary = {key:tagged[label] for key,label in zip(tool.TRACKS,tool.LABELS)}
        actions = summary['action'].split('。随后，')
        split = cfg['splits'][group]
        require_count = 2 if split is not None else 1
        if len(actions) != require_count:
            raise ValueError(f'Expected {require_count} action units in {name} group {group}')
        points = [start,split,end] if split is not None else [start,end]
        expressions = re.match(r'A：(.*?)；B：(.*)', summary['expression'])
        camera_parts = summary['camera'].split('；')
        result = summary['continuity'].removeprefix('此段结束：').removesuffix('。保留既有环境变化。')
        afinal,bfinal = result.split('；B',1)
        ids=[]
        for part, action in enumerate(actions):
            a_action,b_action=action.split('；对方',1)
            index=len(plan['beats'])
            bid=f'B{index+1:02d}'
            ids.append(bid)
            after=copy.deepcopy(state)
            environment=DETAILS[name]['environment'][index]
            if part == len(actions)-1:
                after.update(A=afinal.removeprefix('A'),B=bfinal)
            else:
                after.update(A=cfg['middle'][middle_index][0],B=cfg['middle'][middle_index][1])
                middle_index+=1
            after['environment'] += '；'+environment
            one=plan['camera_mode']=='one-take'
            sound_parts=summary['sound'].removesuffix('。无台词与背景音乐。').split('；')
            beat={'id':bid,'start':points[part],'end':points[part+1],'intent':summary['emotion'],
                  'actors':{'A':{'action':a_action,'performance':DETAILS[name]['performance'][index][0]},'B':{'action':b_action,'performance':DETAILS[name]['performance'][index][1]}},
                  'emotion':summary['emotion'],'camera':{'shot_id':'S01' if one else f'S{index+1:02d}',
                  'transition':'start' if index==0 else ('continuous' if one else 'cut'),'side':'南侧',
                  'path':camera_parts[min(part,len(camera_parts)-1)],'axis_bridge':''},
                  'vfx':summary['vfx'].split('；')[min(part,len(summary['vfx'].split('；'))-1)],
                  'environment':environment,
                  'sound':sound_parts[min(part,len(sound_parts)-1)]+'。无台词与背景音乐。','ability_ids':cfg.get('uses',[[]]*20)[index],
                  'before':copy.deepcopy(state),'after':after}
            plan['beats'].append(beat)
            state=copy.deepcopy(after)
        plan['sections'].append({'id':f'P{group+1:02d}','beat_ids':ids,'summary':summary})
    receipt = tool.read_json(ROOT/'sources/editorial/0.3.0'/f'{name}.review.json')
    plan = tool.apply_review(plan, receipt)
    tool.validate(plan)
    destination=SKILL/'examples'
    destination.mkdir(exist_ok=True)
    write_json(destination/f'{name}.plan.json',plan)
    (destination/f'{name}.prompt.txt').write_text(tool.prompt(plan),encoding='utf-8')
    print(f'{name}: {len(plan["beats"])} director beats / {len(plan["sections"])} prompt sections')


if __name__=='__main__':
    manifest=json.loads((SOURCE/'manifest.json').read_text(encoding='utf-8'))
    for entry in manifest['files']:
        actual=hashlib.sha256((SOURCE/entry['name']).read_bytes()).hexdigest()
        if actual!=entry['sha256']:
            raise SystemExit(f'Source snapshot changed: {entry["name"]}')
    for name,cfg in CONFIG.items():
        rebuild(name,cfg)
