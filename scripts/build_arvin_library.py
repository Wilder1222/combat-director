"""Build attributed, progressively loaded cards from the pinned MIT source.

The selections and adaptation notes below are editorial authority; generated
cards/catalog are outputs. No network access or model calls are used.
"""
from __future__ import annotations

import argparse
import hashlib
import importlib.util
import json
import re
from collections import Counter
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
PIN = 'c526a49bb8695f5333af90b56365dc492e24b6ff'
SOURCE_SHA = '011eed576c241a2180c776ddf6b8555331b482a951e7be35ed53928e7f0b87e0'
LICENSE_SHA = 'aff64252938164965416e9e29af9faf52b48f6d294ab41cf1a9b6bd886d41333'
URL = 'https://github.com/wangarvin007-commits/-skills'
SOURCE = 'seedance-combat-prompt/SKILL.md'
_managed_spec = importlib.util.spec_from_file_location('arvin_generated_files', Path(__file__).with_name('generated_files.py'))
managed = importlib.util.module_from_spec(_managed_spec)
_managed_spec.loader.exec_module(managed)
_items_spec = importlib.util.spec_from_file_location('arvin_source_items', Path(__file__).with_name('arvin_items.py'))
items_builder = importlib.util.module_from_spec(_items_spec)
_items_spec.loader.exec_module(items_builder)

# One overview row per family, followed by supplied detailed sections. Missing
# weapon supplements are deliberately not reconstructed as upstream material.
FAMILIES = [
    ('taiji', '太极拳', [(2274, 2302)], '接住来势后移步转腰，手臂与脚步同向改线；没有接触就不能借力。对手收招时改为护线，不追空手。'),
    ('baji', '八极拳', [(2304, 2326)], '先交代进入短距的脚步和身体空间，再写肘靠短发；被侧移让空后必须重立支撑，不能连续无代价撞击。'),
    ('wingchun', '咏春拳', [(2328, 2380)], '以窄幅护线、短距截手表现中线争夺；对手换到外侧时需转马追线，连拳之间保留手臂回收。'),
    ('bagua', '八卦掌', [(2221, 2271)], '以弧形步法换到外门，掌线随躯干转动；先画可用绕行空间，被柱墙封路就缩弧或退出。'),
    ('xingyi', '形意拳', [(2447, 2498)], '直线进步和拳路同向，突出一次整齐推进；让对方侧移破直线，收脚换角后才续攻。'),
    ('muaythai', '泰拳', [(2515, 2565)], '远处腿、中距拳、近处肘膝分层使用；进入近身需先交代双方手臂占用，出膝后有落脚和护架。'),
    ('sanda', '散打', [(2569, 2588)], '拳腿换距后才接摔；接腿必须展示抓到的瞬间与自身支撑，对手抽腿成功则回到拳腿交换。'),
    ('karate', '空手道', [(2418, 2431)], '用清楚的起动、短促直线和回收表现节拍，寸止是演出选择；对手可让线，不能把名称写成一击必胜。'),
    ('taekwondo', '跆拳道', [(2404, 2416)], '把旋转轴、支撑脚、起跳和落点写清；水平旋身与竖向翻腾分开，落地失位就失去追击窗口。'),
    ('tantui', '谭腿', [(1684, 1728)], '以拳线掩护腿线，区分弹、蹬、扫的轨迹；一腿收回形成下一步，不把十二路一次塞满。'),
    ('legs36', '36路腿法', [(1909, 1984)], '按高度、方向、支撑方式选两三种腿路；每次高低切换先明确重心和收腿，对方退距时允许踢空。'),
    ('capoeira', '巴西战舞', [(1631, 1681)], '用摇步、侧身、倒置出腿建立圆形节奏；翻转需要手撑或起跳条件，对方卡住落点时用收腿换位脱离。'),
    ('jiujitsu', '柔术', [(2433, 2445)], '从站立到倒地必须连续交代谁落在哪侧、哪只手可用；控制姿态仅作影视动作，不省略对方脱离和重新站起。'),
    ('judo', '柔道', [(1783, 1907)], '先展示接触、移步造成的失衡，再到转体和落地；对方重心未移动时不能凭抓衣直接飞出，落地后重新判断站位。'),
    ('aikido', '合气道', [(2383, 2402)], '来势、接触与转向依次可见；对方抽手或转身跟进会破坏引导，应转为护线退出，不能隔空控制。'),
    ('qinna36', '擒拿', [(1986, 2052)], '抓控是有开始与结束的中间态，写清占用哪只手；未抓牢或对方顺势转身时放弃控制，恢复正常攻防。'),
    ('hunggar', '洪拳', [(1730, 1780)], '桥手与稳固步架共同承接冲击；对手改变角度时移动脚步重建桥线，不能固定站桩挡住所有方向。'),
    ('caijia', '蔡拳', [(1523, 1573)], '以斜身、三角落步和短手换线表现偏门快打；每次绕线保留可见落脚点，对手跟转时改短打或退出。'),
    ('groundlegs', '少林旋风地堂腿', [(1576, 1627)], '低位进入、贴地转向、起身返回分成三拍；地面必须可支撑，对手退开或封住起身线时不能凭空弹回高位。'),
    ('choyleefut', '蔡李佛', [], '上游此处只有招名；若采用挂扫抛的手臂意象，需另写原创动作路径并标注补写，不能称已导入完整套路。'),
    ('jeetkune', '截拳道', [(2501, 2513)], '截击依赖看得见的起动信号与足够距离；对方假起动或及时停步时允许判断失误，保留防守回收。'),
    ('mantis', '螳螂拳', [], '上游此处只有招名；可另选混合连招中的角色化段落，不把其局部用法推广为完整门派定义。'),
    ('drunken', '醉拳', [], '上游此处只有招名；摇身和跌扑需要支撑与恢复路径，另写的动作应标为本项目创作。'),
    ('wuxia-step', '武侠身法', [(2194, 2220)], '名称为文学与作者创作意象；普通版本写步幅、遮线、落脚点，瞬移、踏空或分身须另获用户能力授权。'),
    ('taiyi-sword', '武当太乙玄门剑', [(685, 687)], '以圆转和曲线路径区别直刺；这里只提供名称与定位，局部角色动作可查剑神卡，不能声称完整剑谱已导入。'),
    ('wudang132', '武当六路132式总剑', [(685, 686), (688, 688)], '保留高低层次的视觉方向，滚身与翻起需空间；132式只属上游命名，当前仓库未提供132式全谱。'),
    ('yang55', '杨式55式太极剑', [(685, 686), (689, 689)], '取慢圆接引和剑尖换线的方向，具体身体路径须补写；55式只属上游命名，不能以十二个列名代替全谱。'),
    ('dugu', '独孤九剑', [(685, 686), (690, 690)], '以先展示习惯、再尝试破线的剧情逻辑改编；不是自动识破一切，破气等能力名称不能自动授权。'),
    ('huashan', '华山基础剑法', [(685, 686), (691, 691)], '取清楚的架势与直线起落，名称不能证明历史套路；细节另查剑神角色变体或标为原创补写。'),
    ('yunv', '玉女十九剑', [(685, 686), (692, 692)], '缠绕要有刃路和接触点，软转不等于剑身变成绳索；十九剑全谱未随仓库提供。'),
    ('whiteape', '峨眉白猿二十四剑', [(685, 686), (693, 693)], '藏锋与突然改变高低可作轮廓；纵跳要落点，猿形不能自动改角色身体形态。'),
    ('qinglong', '青龙剑32式', [(685, 686), (694, 694)], '开阔幅度依赖挥剑空间；长弧挥空后收锋重立，不能自动变成青龙实体或无距离清场。'),
    ('ziwu', '峨眉子午剑', [(685, 686), (695, 695)], '短距脆变需要先进入可触距离；侧滑与收锋分开可见，短促不是无起动和无限连刺。'),
    ('scythe', '长柄镰刀', [(697, 701)], '长柄旋转受墙柱限制，回镰要让出路径；专项文件缺失，名称中的远距飞斩不自动授予回旋飞行。'),
    ('musou', '梦想一心太刀', [(703, 707)], '作为上游游戏意象候选；单刀与雷电分开设置，刀路补写需标为改编，未核验官方招式或能力。'),
    ('feixue-frost', '绯雪樱灼流单太刀', [(709, 713)], '此卡是上游冰蓝粉樱轮廓，与火焰绯雪角色是两个版本；单刀、冰弓、时停分别核对用户授权，游戏设定未核验。'),
]

CHARACTERS = [
    ('taiji', '太极', 808, 839, ['太极拳', '八极拳', '咏春拳', '八卦掌'], '远近与圆直切换：先接引，再绕位，短距连打，贴身短发。', '对手拒绝接触时先追距离；一次只切换一项距离或手法，不能四武学同时开动。'),
    ('hongcha', '红茶', 841, 873, ['泰拳', '散打', '空手道', '八极拳'], '以肘膝、拳腿换距和短发保持前压，每轮有清晰重音。', '对方退出肘膝距离时必须跟步；追击跨步过大就暴露侧面。火色不自动授予燃烧能力。'),
    ('baige', '白鸽', 875, 916, ['巴西战舞', '36路腿法', '谭腿', '跆拳道', '截拳道', '少林旋风地堂腿'], '巴西战舞与高、中位腿法主攻；低位地堂腿仅作短暂换层。', '水平旋身与竖向翻转分别描述。对方封住落点时取消高踢，低位脱离后必须重新站稳；紫黑特效是可选角色签名。'),
    ('linyu', '凛羽', 918, 956, ['形意拳', '八卦掌', '擒拿', '合气道', '柔道', '柔术'], '直进与绕位主攻，抓控破招后回到快攻；控制是过渡。', '打→抓→打需实际接触才成立；抓空就撤回护线。保留软霜雾与冰女硬冰的材质区别，70/30仅是上游建议。'),
    ('leidian', '雷电', 958, 992, ['散打', '跆拳道', '空手道', '截拳道', '武侠身法', '咏春拳', '八极拳'], '用短路径、快速换距与连续短发形成速度角色。', '零前摇改成极短且可辨的起动；残影只是视觉轨迹，不新增分身。身体高速移动仍要接上落脚和回收。'),
    ('bale', '芭乐', 994, 1051, ['柔术', '蔡拳', '巴西战舞', '跆拳道', '形意拳'], '站立短打、翻转换位、地面控制三个状态分别有招式。', '状态切换必须有对手动作造成的转折；被压住支撑手时不能继续手撑翻转，落地位置持续继承。'),
    ('bingnv', '冰女', 1054, 1103, ['泰拳', '八极拳', '空手道', '擒拿', '洪拳'], '短发硬攻与硬冰封路相结合，实体结晶有接触面。', '冰只在用户允许时产生；先规定生长路径、范围、破坏与消退条件。冰封失败可退回普通护架。'),
    ('jianshen', '剑神', 1106, 1153, ['武当太乙玄门剑', '武当六路132式总剑', '杨式55式太极剑', '独孤九剑', '华山基础剑法', '玉女十九剑', '峨眉白猿二十四剑', '青龙剑32式', '峨眉子午剑'], '同一把剑切换慢圆、锐变、短促、缠绕与大弧的路径节奏。', '每段选一条主剑路、一种破线、一种收势即可。用剑神表里的角色变体，不称完整九剑原谱；紫霄神剑仅绑定此预设。'),
    ('feixue-fire', '绯雪·火焰', 1156, 1188, ['绯雪樱灼流单太刀', '火焰刀', '焚樱刀禅', '武侠身法'], '单刀前压与火红刀焰，沿刀路加压后收刀。', '明确这是作者火焰改编角色；禁止混入冰蓝粉樱版本的冰弓或时停。对手让线时需收刀换步，火焰预算单独声明。'),
]

# Each tuple is id, title, source ranges, adaptation (not universal mandates).
CHOREOGRAPHY = [
    ('entry', '突进与开场', [(1190, 1236)], '按原距离选突进，先看到出发点和进入路线；试探、退让或慢开场同样可用。'),
    ('school-chain', '武学节拍与连招', [(1237, 1261)], '每段选一条主运动线；下一招必须继承上一招的距离、手占用和落脚，允许被对手打断。'),
    ('hands', '手部动作与攻击部位', [(1262, 1276)], '变换手部形状必须有空间和回收；用少数可辨动作表达区别，避免把全表写成一次连打。'),
    ('kicks', '踢击高度与身体路径', [(1278, 1296)], '高度变化需要收腿、转髋和支撑交换；命中效果是候选，最终由双方位置决定。'),
    ('turning', '压制与逆转拐点', [(1298, 1322)], '拐点来自已展示的习惯、资源或地形；对手改变习惯时允许反转失败。'),
    ('breath', '终结前的呼吸与停顿', [(1323, 1333)], '停顿由收势、观察或重新支撑产生，时长随动作变化；不照搬固定生理秒数。'),
    ('space', '空间维度变化', [(1334, 1359)], '只在场地提供高低与移动路径时换层；保持出口与落点，不为凑次数瞬移。'),
    ('break', '终结第一段：改变平衡', [(1361, 1382)], '用一次可见改线或失衡创造窗口；对手站稳后窗口关闭，不自动进入终结。'),
    ('payoff', '终结第二段：集中输出', [(1383, 1429)], '只兑现此前建立的能力和空间；终结动作可被挡住或让开，效果强度不得替代因果。'),
    ('aftermath', '终结第三段：余波与结束', [(1430, 1438)], '余波留在接触位置，角色回收或撤离写完；普通场景用衣料、积水、尘土表达。'),
    ('redirection', '化劲与攻防转换', [(1439, 1480)], '接触、改向、失衡、接续依次可见；对方抽手或变向时重新判断，不用化劲二字代替过程。'),
    ('upper-lower', '上下肢配合', [(1481, 1521)], '手负责护线或牵制时不能同时做另一项抓握；腿的支撑和下一拍可用肢体持续继承。'),
    ('control-followup', '抓控、投摔与脱离后的衔接', [(2053, 2136)], '控制成功与失败各留一条出口；对手起身后重新定距，不把锁控和反击当作必然连续事件。'),
    ('baji-pairs', '八极两组短打连段', [(2138, 2154)], '选一组并明确对手如何回应；近身肘与肩的空间不能重叠，停顿由回收重立产生。'),
    ('mixed20', '混合二十手：拆段使用', [(2156, 2192)], '这是分阶段参考，不要求在短片里打满二十手。每次最多抽一阶段，门派切换需由接触与重心解释。'),
    ('rhythm', '连续轻击与重音节拍', [(437, 467), (491, 520)], '轻重对比服务动作可读性；只在重击因果节点做顿挫，不把每次接触都慢放。'),
    ('reaction', '攻守表情与身体反馈', [(468, 490)], '先有明确受力方向，再有肩背、衣料和脚步反应；对手保持主动判断，反馈不能证明受伤程度。'),
    ('escalation', '中段递进与攻守三态', [(2791, 2889)], '递进可选速度、空间、资源之一；防守、失衡和重建是状态变化，固定比例和恢复秒数不是生理事实。'),
]
CAMERA = [
    ('moves15', '十五种运镜与组合', [(90, 118)], '按当前运动线选一主运镜，连续镜头不能同时对向移动；不采用平台成功率或星级作为证据。'),
    ('spec', '镜头规格与动作可读性', [(129, 279)], '先确定景别、视角、运动、目标和接触点；规格是帮助看懂动作的选择，不是每次输出固定配方。'),
    ('weapons', '兵器镜头与挥动空间', [(742, 790)], '保留持械手、刃路、接触和回收；镜头切换不得藏住换手、换武器或穿墙。'),
    ('color', '冷暖与双方辨识', [(398, 404)], '可借冷暖区分双方，也可用明度、剪影与材质；不强迫所有角色改成双色能量。'),
]
PATTERNS = [
    ('a', '低仰蓄力', 283, 290), ('b', '攻击轨迹与拖尾', 292, 299),
    ('c', '接触点与双色效果', 301, 308), ('d', '全景余波收束', 310, 317),
    ('e', '不对称效果压迫', 319, 326), ('f', '翻摔全肢可见', 328, 335),
    ('g', '元素对峙', 337, 344), ('h', '角色与地面反馈', 346, 353),
    ('i', '攻击部位推进', 355, 362), ('j', '上勾动作的三段呈现', 364, 371),
    ('k', '重击交换链', 373, 380),
]
EFFECTS = [
    ('character-signatures', '角色特效签名与动态词库', [(69, 81), (2590, 2685)], '颜色、质感、形状与运动分别选择；角色预设可覆盖通用武学配色，特效不能赋予额外攻击或控制。'),
    ('trajectory', '特效起点、路径、终点与消退', [(2686, 2716)], '效果跟随实际肢体或兵器轨迹；接触结束后衰减，不保留无来源的第二条攻击线。'),
    ('intensity', '效果强弱与顿挫', [(2718, 2743)], '根据当前阶段分配视觉强度，不照搬15秒时间表；高潮也必须看得见角色和接触点。'),
    ('air', '空气、衣料、尘水与余波', [(2746, 2789)], '普通拳脚用衣摆、发丝、积水与尘粒；空气爆环、残影和气墙只在指定夸张风格中使用。'),
]

SCENE_NOTES = [
    '竹间留出一条直线与一处转身空地；湿青石使急停变慢，竹影用于辨方向。',
    '先显示巷口、墙面和水坑；狭巷限制长横扫，踏水波纹延续脚步位置。',
    '交代仙台边沿和两个稳定落点；云海不当实地，踏空需要明确能力。',
    '把广告投影和实墙区分开；窄巷只留短兵路径，积水承接霓虹颜色。',
    '沙地提供滑移与脚印，断旗位置固定；双方出沙尘后延续原移动方向。',
    '枯木之间预留回收空间；月光勾轮廓，雾仅遮线不代替人物位移。',
    '先声明真空下的推进、惯性和立足方式；没有地面不能套地面蹬步，声音作为配乐选择。',
    '断墙先建立可穿过缺口；碎石影响落脚，坍落须由接触引发。',
    '展示边界和中央空地；沙尘给步法留痕，看台只提供尺度与光影。',
    '木地板可见接触振动，柱与擂台边界限制退路；竹帘光带帮助保持轴线。',
    '把可踩的岩地与危险裂隙分开；冰和熔岩是环境条件，不默认受角色支配。',
    '先声明水下浮力、阻力和呼吸设定；出拳回收变慢，不能直接套陆地腾空落脚。',
    '车辆是已展示的掩体；干裂地面与沙尘影响抓地，绕车运动继承车辆朝向。',
    '山门台阶分层建立，玉石反光保留轮廓；背景飞剑不得自动加入角色攻击。',
    '古堡缺口与树根决定走线；逆月光留下人物剪影，移动不能穿过倒墙。',
    '先显示护栏、门口和可退空间；天台边缘持续存在，风影响衣料而不改变身体重力。',
    '甲板俯仰同时作用双方；人物借栏杆稳定必须有空手，滑步随船倾方向。',
    '先声明桥面与雾中边界；鬼火作光源或已授权能力，不能随剧情临时救场。',
    '绳圈与角柱持续限制退路；顶光区分护架和受力，擂台弹性反馈随落步。',
    '石柱决定视线和短暂遮挡；风沙方向持续一致，柱后重现不得更换手中武器。',
]


def clean(text):
    return re.sub(r'[*`★]', '', text).strip()


def table_names(lines, ranges):
    """Extract literal named items; never synthesize missing movement detail."""
    names = []
    for start, end in ranges:
        section = lines[start-1:end]
        for i, row in enumerate(section):
            if not row.startswith('|') or i+1 >= len(section) or not re.match(r'^\|[\s:|-]+\|$', section[i+1]):
                continue
            headers = [clean(c) for c in row.strip('|').split('|')]
            wanted = [j for j,h in enumerate(headers) if any(k in h for k in ('招式', '招名', '中文名', '罗马音', '技法名', '腿法名', '身法名称', '运镜名称', '投技', '关节技', '降服技', '截法', '招牌踢法'))]
            if not wanted:
                if headers[0] in ('维度', '#', '规则'):
                    continue
                wanted = [1 if headers[0] in ('#', '路数', '编号') and len(headers)>1 else 0]
            for data in section[i+2:]:
                if not data.startswith('|'):
                    break
                cells = [clean(c) for c in data.strip('|').split('|')]
                for j in wanted:
                    if j < len(cells) and cells[j]:
                        names.append(cells[j])
    return list(dict.fromkeys(names))


def verify_source(root):
    folder = root / 'sources/upstream/arvin-seedance'
    manifest = json.loads((folder/'manifest.json').read_text(encoding='utf-8'))
    if manifest['commit'] != PIN or manifest['repository'] != URL:
        raise ValueError('Unexpected upstream source pin')
    expected = {'SKILL.md': SOURCE_SHA, 'LICENSE': LICENSE_SHA}
    if {f['name'] for f in manifest['files']} != set(expected):
        raise ValueError('Unexpected upstream source files')
    for f in manifest['files']:
        data = (folder/f['name']).read_bytes()
        if len(data) != f['bytes'] or hashlib.sha256(data).hexdigest() != expected[f['name']] or f['sha256'] != expected[f['name']]:
            raise ValueError('Upstream source hash mismatch: '+f['name'])
    return (folder/'SKILL.md').read_text(encoding='utf-8').splitlines(), manifest


def render(root=ROOT):
    lines, manifest = verify_source(root)
    facets = json.loads((root/'sources/editorial/arvin-facets.json').read_text(encoding='utf-8'))
    if set(facets) != {'version', 'entries'} or type(facets['version']) is not int or facets['version'] != 1 or not isinstance(facets['entries'], dict):
        raise ValueError('Invalid editorial facets')
    used_facets = set()
    outputs = {}
    base = json.loads((root/'sources/editorial/library-base.json').read_text(encoding='utf-8'))
    entries = [{**e, 'detail':'original', 'schools':[], 'characters':[], 'names':[], 'source':None} for e in base['entries']]

    def add(slug, kind, title, ranges, note, *, schools=(), characters=(), detail='detailed', names=(), summary=None, scopes=('duel', 'sparring')):
        if any(type(a) is not int or type(b) is not int or not 1 <= a <= b <= len(lines) for a,b in ranges):
            raise ValueError('Invalid source range: '+slug)
        card_id = 'arvin-'+slug
        if card_id in facets['entries']:
            facet = facets['entries'][card_id]
            if set(facet) != {'schools','characters','scope','basis'} or not isinstance(facet['basis'], str) or not facet['basis'].strip():
                raise ValueError('Invalid facet record: '+card_id)
            for key in ('schools','characters','scope'):
                value = facet[key]
                if not isinstance(value, list) or any(not isinstance(s,str) or not s.strip() for s in value) or len(value) != len(set(value)):
                    raise ValueError('Invalid facet '+key+': '+card_id)
            schools, characters, scopes = facet['schools'], facet['characters'], facet['scope']
            used_facets.add(card_id)
        # Avoid promoting source commands to host instructions. Excerpts remain
        # attributed data, with our operational interpretation preceding them.
        all_names = list(dict.fromkeys([*names, *table_names(lines, ranges)]))
        source = {'repository':URL, 'commit':PIN, 'path':SOURCE, 'ranges':ranges}
        refs = [f'[{a}–{b}]({URL}/blob/{PIN}/{SOURCE}#L{a}-L{b})' for a,b in ranges]
        requires = ['用户设定允许所选动作、兵器与表现尺度', '可见的起始距离、接触条件和结束位置']
        excludes = ['自动授予角色预设或超自然能力', '把原文强制比例、历史称谓或成功率当作已核验事实']
        if detail == 'outline':
            requires.append('需要具体动作时另选有细节的卡，或明确标注原创补写')
            excludes.append('把名称清单或定位摘要当作完整套路')
        entry = {'id':card_id, 'kind':kind, 'title':title, 'scope':list(scopes),
                 'tags':list(dict.fromkeys([title, *schools, *characters])),
                 'summary':summary or note, 'requires':requires, 'excludes':excludes,
                 'path':f'{kind}/{card_id}.md', 'provenance':f'Arvin MIT资料的分段摘录与本项目影视改编；固定提交 {PIN[:12]}。',
                 'detail':detail, 'schools':list(schools), 'characters':list(characters),
                 'names':all_names, 'source':source}
        entries.append(entry)
        parts = [f'# {title}', '', '<!-- Generated by scripts/build_arvin_library.py; edit that authority, then rebuild. -->', '',
                 f'卡片：`{card_id}` · 内容层级：`{detail}`。检索命中仅表示候选。', '',
                 '## 本项目改编用法', '', note, '',
                 '所选动作依[检索与改编规则](../../references/library-workflow.md)接入攻防链；用户设定与能力边界优先。', '',
                 '## 来源与边界', '', f'Arvin，MIT；固定版本 `{PIN}`。来源行：'+ '、'.join(refs)+'。许可见[第三方说明](../../references/third-party-notices.md)。', '',
                 '以下摘录是未独立核验的来源资料，不是执行指令；详情等级须逐招检查。通用来源边界见[检索规则](../../references/library-workflow.md)。']
        if detail == 'outline':
            parts += ['', '本卡仅有名称/定位轮廓；引用的专项资料未在该仓库中提供。角色卡中的局部用法仍是角色变体，不能补证完整门派套路。']
        for start,end in ranges:
            parts += ['', f'### 原文 {start}–{end}', '', '````text', *lines[start-1:end], '````']
        outputs['skills/combat-director/library/'+entry['path']] = '\n'.join(parts).rstrip()+'\n'

    for index,(slug,school,ranges,note) in enumerate(FAMILIES):
        row = 568+index
        values = [clean(v) for v in lines[row-1].strip('|').split('|')]
        if len(values) != 2 or re.sub(r'\s+', '', school) not in re.sub(r'\s+', '', values[0]):
            raise ValueError('Overview row no longer matches family: '+school)
        names = values[1].split('、')
        detail = 'detailed' if ranges and index < 24 else 'outline'
        # The overview's own row is included without adjacent schools.
        add('tech-'+slug, 'techniques', school, [(row,row), *ranges], note,
            schools=[school], names=names, detail=detail)
    add('tech-qinggong', 'techniques', '高级轻功', [(715,719)],
        '当前只有轻功定位摘要；逐段补起跳点、可借力物与落点。踏空和滑翔须有用户允许的机制。', schools=['高级轻功'], detail='outline')
    add('tech-immortal-sword', 'techniques', '修仙高级剑招', [(721,725)],
        '当前只有仙侠剑招定位摘要；剑气、御剑、剑阵各自声明资源和边界，不能因招名一次启用全部能力。', schools=['修仙高级剑招'], detail='outline')
    for slug,name,start,end,schools,summary,note in CHARACTERS:
        add('character-'+slug, 'characters', name+'：战斗预设', [(start,end)], summary+' '+note,
            schools=schools, characters=[name], summary=summary)
    for kind,records in [('choreography', CHOREOGRAPHY), ('camera', CAMERA), ('effects', EFFECTS)]:
        for slug,title,ranges,note in records:
            add(kind+'-'+slug, kind, title, ranges, note)
    for slug,title,start,end in PATTERNS:
        add('camera-pattern-'+slug, 'camera', title, [(start,end)],
            '按该模式强调一个因果节点；镜头保持原空间轴线与完整回收。原文夸张效果和命中结果是可替换的演出选择。')
    for i,(start,end) in enumerate([(2972,2973),(2975,2976),(2978,2979),(2981,2982),(2984,2985)],1):
        title = re.sub(r'^#+\s*\d+\.\s*', '', lines[start-1])
        add('style-'+str(i), 'styles', title, [(start,end)],
            '提取材质、光源、轮廓、运动表现各一项再写场景，按用户参考替换；8K、引擎名和抽象质量词不构成画质保证。风格不改变角色的物理能力。',
            scopes=('duel','group','escape','chase','ranged','sparring'))
    for i,note in enumerate(SCENE_NOTES,1):
        line = 3018+i
        title = re.sub(r'^\d+\.\s*', '', lines[line-1])
        add('scene-'+str(i), 'scenes', title, [(line,line)], note,
            scopes=('duel','group','escape','chase','ranged','sparring'))
    catalog = {'version':2, 'entries':entries}
    if used_facets != set(facets['entries']):
        raise ValueError('Unknown editorial facet IDs: '+', '.join(sorted(set(facets['entries'])-used_facets)))
    known_schools = {row[1] for row in FAMILIES} | {'高级轻功','修仙高级剑招'} | {school for row in CHARACTERS for school in row[4]}
    known_characters = {row[1] for row in CHARACTERS}
    for entry in entries:
        if not set(entry['schools']) <= known_schools or not set(entry['characters']) <= known_characters or not entry['scope'] or not set(entry['scope']) <= {'duel','group','escape','chase','ranged','sparring'}:
            raise ValueError('Unknown editorial facet value: '+entry['id'])
    outputs['skills/combat-director/library/catalog.json'] = json.dumps(catalog, ensure_ascii=False, indent=2)+'\n'
    items, item_coverage = items_builder.build_items(lines, entries,
        {'repository': URL, 'commit': PIN, 'path': SOURCE, 'sha256': SOURCE_SHA})
    outputs['skills/combat-director/library/items.json'] = json.dumps(items, ensure_ascii=False, indent=2)+'\n'
    outputs.update(items_builder.navigation(entries, items['entries']))
    coverage = {'source_commit':PIN, 'source_sha256':SOURCE_SHA,
                'item_index':item_coverage,
                'cards':len(entries), 'by_kind':dict(sorted(Counter(e['kind'] for e in entries).items())),
                'by_detail':dict(sorted(Counter(e['detail'] for e in entries).items())),
                'missing_referenced_files':manifest['missing_referenced_files'],
                'selections':[{'id':e['id'], 'detail':e['detail'], 'ranges':e['source']['ranges'], 'indexed_names':len(e['names'])} for e in entries if e['source']],
                'excluded':'完播率权重、平台执行星级、通用强制问询、重复菜单和固定15秒全局命令不作为规则导入。源文历史/游戏/生理断言未独立核验。'}
    outputs['docs/implementation/arvin-library-coverage.json'] = json.dumps(coverage, ensure_ascii=False, indent=2)+'\n'
    return outputs


def check_outputs(root, outputs):
    managed.check(root, outputs)


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    modes = parser.add_mutually_exclusive_group()
    modes.add_argument('--check', action='store_true')
    modes.add_argument('--plan', action='store_true', help='preview creates, updates and retirements without writing')
    modes.add_argument('--recover', action='store_true', help='restore files from an interrupted managed update')
    args = parser.parse_args()
    try:
        if args.recover:
            managed.recover(ROOT)
            print('PASS: previous generated outputs restored; inspect --plan before rebuilding')
            return
        outputs = render(ROOT)
        if args.check:
            check_outputs(ROOT, outputs)
        elif args.plan:
            changes, _, _ = managed.plan(ROOT, outputs)
            print(json.dumps(changes, ensure_ascii=False, indent=2))
            return
        else:
            managed.apply(ROOT, outputs)
            check_outputs(ROOT, outputs)
        count = len(json.loads(outputs['skills/combat-director/library/catalog.json'])['entries'])
        item_count = len(json.loads(outputs['skills/combat-director/library/items.json'])['entries'])
        print(f'PASS: {count} cards; {item_count} source items; pinned source and generated outputs consistent')
    except (OSError, ValueError) as error:
        parser.exit(1, f'FAIL: {error}\n')


if __name__ == '__main__':
    main()
