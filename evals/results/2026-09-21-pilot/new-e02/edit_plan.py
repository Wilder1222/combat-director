import copy
import hashlib
import json
from pathlib import Path

SOURCE = Path(r'D:\study\projects\combat-director\evals\baselines\0.2.0\skills\combat-director\examples\grounded-15.plan.json')
OUT = Path(r'D:\Temp\combat-director-evals-20260921\new-e02')
raw = SOURCE.read_bytes()
p = json.loads(raw.decode('utf-8-sig'))
p['schema_version'] = '1.1'
p['id'] = 'grounded-15-wooden-staff'
p['provenance'] += ' 本次仅按用户要求将A兵器改为木杖，并同步接触、缴械、声音、效果、状态及摘要；保留原结尾和时长；木杖尺寸是本次可改创作假设。'
p['editorial_reviews'] = {}
p['cast'][0]['prop'] = '约1.2米实心圆木杖，木纹清楚、两端圆钝，无刃、无护手、无金属包头'
p['cast'][0]['hand'] = '右手，握后段，全程不换手；左手只保持身体平衡'
p['headers']['cast'] = '\n'.join(
    f"{a['id']} {a['description']}；兵器：{a['prop']}；持械：{a['hand']}。目标：{a['goal']}。表演基调：" +
    ('警惕克制，视线关注对方身体与持械手。' if a['id'] == 'A' else '前段积极压迫，失位后急促戒备。')
    for a in p['cast'])
p['headers']['goal'] = p['headers']['goal'].replace('无能量剑气', '无能量光波')
p['headers']['continuity'] += '\nA的木杖全程由右手握后段，左手不接杖；杖端圆钝，没有刃口、护手或金属包头。杖身斜向拨开刀身，不正面硬吃连续劈砍；接触有木质闷响和少量刮痕，没有金属火花或清脆双金属撞击声。已有刮痕一直保留，木杖完整不折断。B落刀后右手为空，不再次持刀。'
p['headers']['scene'] += '\n修订假设：A使用约1.2米的实心圆木杖，右手握后段；其余人物、场景、能力和结尾继承输入计划。'

p['initial_state'] = {
    'A': '官道中线偏西，面向B，双脚前后站稳，右手握木杖后段，杖身斜举身前，左手空；衣着完整，杖身无刮痕',
    'B': '官道中部偏北，面向A，前脚承重，右手短刀准备前压；衣着完整',
    'environment': '初始场景完整；远处石桥；道路北缘碎石带',
    'camera_side': '南侧'
}
p['headers']['scene'] += '\n开场位置：A在官道中线偏西，面向B，双脚前后站稳，右手握杖后段斜举身前、左手空；B在官道中部偏北，面向A，前脚承重，右手短刀准备前压。两人衣着完整，木杖开场无刮痕。'

actions = [
    ('0至0.2秒保持斜举木杖的戒备；随后向前短进半步，右手用杖身前段斜接短刀刀身并向外拨开，接触后屈肘缓冲、脚步轻退，左手空着平衡',
     '0至0.2秒看住A；随后向A逼近，右手短刀斜向挥来，与木杖前段发生一次清楚接触，被斜拨后收刀'),
    ('沿道路中线向西南退两步，右手各用杖身前段斜拨一次来刀，每次接触后把杖收回身前并恢复重心，左手始终空着',
     '右手短刀两次分开跟进，刀身每次被杖拨偏后收回；从A北侧继续压迫，第二次跟步使身体靠近道路北缘'),
    ('在道路中线偏西南站稳，向南略侧身，右手以斜置杖身拨开下一次前压的刀身，目光从刀尖转到B重心，左手空着平衡',
     '持刀前进一步，刀身被斜杖拨到外侧后停住前冲，把身体与短刀收回，重心仍偏前'),
    ('趁B回收，向东北短进一步，右手使圆钝杖端沿直线逼近B上胸前的防线；接触B横置刀身后及时收杖，以杖的距离优势迫其实际后退，左手空着平衡',
     '右手横置短刀挡开近身的杖端，同时后退一步让开杖的前伸范围，后脚实际踩进北缘碎石带，仍握住短刀'),
    ('保持右手握杖后段，见B试图回刀便以杖身前段向外斜拨刀身，再用同一段木杖短促击压B右前臂近腕处；看见B松手落刀便屈肘收杖停手，不追击',
     '在碎石上勉强回刀，刀身被斜拨后右前臂近腕处受木杖短促击压，后脚压到松石滑动，失衡时右手手指松开；短刀脱手落在身侧，随后一膝触地，左手撑地'),
    ('右手持木杖从B让出的道路南侧空隙通过，两步后转身面向B，14.4秒前站到安全距离，圆钝杖端略放低但不放下木杖；最后0.6秒只保留呼吸与衣摆回落',
     '留在北缘碎石带旁原位一膝触地，右手为空、左手撑地，抬头看A；短刀仍在身侧，没有立即捡刀发动新回合')
]
vfx = [
    '木杖与刀身斜接处出现浅刮痕，不产生火花；没有能量效果',
    '接触仅加深少量木质刮痕，木杖不折断，不产生火花或光线',
    '没有新增效果；木杖既有刮痕保留，接触与身体停顿清楚',
    '木杖与刀身接触没有火花；杖身完整，人物运动保持清楚',
    '前臂只表现受力回缩，不出现伤口、血液或能量波；落刀只带起一点尘土',
    '无新增特效，只保留衣摆和浮尘变化；木杖刮痕仍在'
]
sounds = [
    '一次刀身碰木杖的短促木质闷响，随后衣料与脚步声；没有金属对撞声。无台词与背景音乐。',
    '两次分开的木质闷响与刀身擦木声，退步摩擦夯土。无台词与背景音乐。',
    '一次短促碰木闷响后露出双方呼吸声。无台词与背景音乐。',
    '刀身接杖的闷响，随后退步与碎石滚动声。无台词与背景音乐。',
    '刀身擦木声、木杖触及衣袖前臂的轻闷响，随后松石滑动、短刀落到夯土地面的闷响和B急促呼吸；声音按事件顺序。无台词与背景音乐。',
    '脚步停止后只剩呼吸和轻微竹林风声。无台词与背景音乐。'
]
environments = [
    '接触后的鞋底轻退带起少量浮尘；木杖前段留下浅刮痕；双方仍在官道',
    'A向西南后退的两道鞋底擦痕保留；木杖刮痕加深少许，B从北侧逼近碎石带',
    '衣摆迟于身体回落，既有尘土继续飘动，木杖刮痕不消失',
    'B后脚进入北缘碎石带，碎石因落脚滚动，南侧通路逐渐空出',
    'B后脚下松石可见滑动；短刀松手到落地轨迹完整，掉落点在B身侧夯土上，溅起少量尘土',
    '短刀仍在B身侧原掉落点，后退擦痕与滚开的碎石保留；最后0.6秒尘土沉降'
]
states = [
    ('官道中线偏西，面向B，接刀后轻退、重心回到双脚之间，右手握木杖后段，杖身仍在身前，左手空；杖前段有浅刮痕，衣着完整',
     '官道中部偏北，面向A，右手短刀拨偏后收回，前脚承重，继续逼近；衣着完整'),
    ('官道中线偏西南，面向B，后退两步后站稳，右手握木杖后段收回身前，左手空；木杖完整、有既有刮痕，衣着完整',
     '道路北侧靠近碎石带，面向A，跟进后重心偏前，右手短刀收在身前；衣着完整'),
    ('官道中线偏西南，向南略侧身仍面向B，双脚站稳，右手木杖斜在身前，握后段、左手空；木杖完整、既有刮痕保留，衣着完整',
     '道路北侧碎石带前，面向A，前压后收回上身与右手短刀，重心仍偏前；衣着完整'),
    ('从中线偏西南向东北前进一步，面向B，重心稳在前后脚之间，右手握木杖后段收回身前、左手空；杖身完整、既有刮痕保留，衣着完整',
     '实际后退至北缘碎石带，面向A，后脚踩住碎石、重心不稳，右手仍握短刀；衣着完整'),
    ('B南侧通路前停止攻击，面向B，双脚站稳，右手握木杖后段收于身前保持警戒、左手空；杖身完整、刮痕保留，衣着完整',
     '北侧碎石带旁一膝触地，抬头朝A，左手撑地、右手空，短刀在身侧夯土原掉落点；无开放伤口，衣着完整'),
    ('已从B南侧空隙通过并转身面向B，14.4秒前在安全距离站稳，右手仍握木杖后段、圆钝杖端略放低，左手空；杖身完整、刮痕保留，衣着完整',
     '北侧碎石带旁原位一膝触地，面向A，左手撑地、右手空，短刀仍在身侧夯土原掉落点；无开放伤口，衣着完整')
]
prior = copy.deepcopy(p['initial_state'])
for i, b in enumerate(p['beats']):
    b['actors']['A']['action'], b['actors']['B']['action'] = actions[i]
    b['vfx'], b['sound'], b['environment'] = vfx[i], sounds[i], environments[i]
    b['before'] = copy.deepcopy(prior)
    b['after'] = {'A': states[i][0], 'B': states[i][1], 'environment': prior['environment'] + '；' + environments[i], 'camera_side': '南侧'}
    prior = copy.deepcopy(b['after'])
p['beats'][4]['actors']['B']['performance'] = '右前臂受力时短暂皱眉，失衡后眼睛追向落刀；左手张开撑地，呼吸急促'
p['beats'][4]['actors']['A']['performance'] = '目光从B持刀前臂转到落刀，再回到B面部，呼气后停手警戒'

for sec in p['sections']:
    selected = [b for b in p['beats'] if b['id'] in sec['beat_ids']]
    s = sec['summary']
    s['action'] = '随后，'.join('A：' + b['actors']['A']['action'] + '；B：' + b['actors']['B']['action'] + '。' for b in selected)
    s['vfx'] = '；'.join(b['vfx'] for b in selected)
    s['sound'] = '；'.join(b['sound'].replace('。无台词与背景音乐。', '').rstrip('。') for b in selected) + '。无台词与背景音乐。'
    s['environment'] = '；'.join(b['environment'] for b in selected)
    s['continuity'] = '此段结束：A：' + selected[-1]['after']['A'] + '；B：' + selected[-1]['after']['B'] + '。保留既有环境变化，机位保持南侧。'
p['sections'][2]['summary']['expression'] = 'A：视线由B持刀前臂转到落刀再回到B面部，呼气停手；B：右前臂受力时短暂皱眉，失衡后追看落刀，左手张开撑地，呼吸急促'

OUT.mkdir(parents=True, exist_ok=True)
(OUT / 'revised-unreviewed.plan.json').write_text(json.dumps(p, ensure_ascii=False, indent=2) + '\n', encoding='utf-8')
(OUT / 'source-integrity.json').write_text(json.dumps({'source': str(SOURCE), 'sha256_before': hashlib.sha256(raw).hexdigest()}, indent=2) + '\n', encoding='utf-8')
print('Wrote revised-unreviewed.plan.json and source-integrity.json')
