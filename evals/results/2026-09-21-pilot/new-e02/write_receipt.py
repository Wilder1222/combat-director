import json
from pathlib import Path

out = Path(r'D:\Temp\combat-director-evals-20260921\new-e02')
compiled = json.loads((out / 'review-input-final.json').read_text(encoding='utf-8'))
checks = {
    'headers': {
        'identity_action': '人物仍为成年青衣A与黑衣B，目标仍为突破与拦截。cast和headers.cast均将A设为约1.2米无金属包头的圆木杖、右手握后段且左手空；B仍右手短刀。scene补入initial_state的站位与开场完整状态。',
        'camera_timing': 'goal与budget对应15秒、16:9、single、one-take，0.2秒入点和0.6秒出点包含在总长内；14.4秒前A已通过并转身。南侧机位与初始camera_side一致。',
        'ability_cost': 'rules.fantasy为false且abilities为空；表达保留人物级、无仙术无能量效果，木杖接触仅有刮痕与闷响，无能力代价字段需要表达。',
        'continuity': 'headers.continuity与各段状态一致：A不换手不换武器、刮痕持续；B落刀后空手；结尾维持碎石带旁、刀在身侧与A安全距离警戒。'
    },
    'P01': {
        'identity_action': '摘要涵盖B01的斜接拨刀与轻退及B02的两次退步拨刀；A右手握杖后段，B右手短刀每次拨偏后收回。特效和声音同步为木痕、木质闷响与擦木声。',
        'camera_timing': 'B01 0至2秒、B02 2至4.5秒连续覆盖P01；0至0.2秒戒备写入双方动作。摄影机S01从南侧横移到连续跟随，没有切镜。',
        'ability_cost': '两拍ability_ids为空；拨挡依靠可见手臂与脚步，无能量或新增能力，木杖完整但留下刮痕。',
        'continuity': 'B01.before等于initial_state，B02.before继承B01.after。主段结束A退到中线偏西南站稳持杖，B在北侧靠近碎石带持刀，擦痕和木痕保留。'
    },
    'P02': {
        'identity_action': '摘要与B03同为A在中线偏西南站稳向南侧身，用斜杖拨刀并观察B重心；B前压被拨后回收。双方呼吸与目光表演保留。',
        'camera_timing': 'P02仅选B03，4.5至7秒；S01持续南侧小幅前跟，双脚仍在画内，未新增切镜。',
        'ability_cost': 'B03无技能调用；接触和停顿来自木杖与人体运动，未增加能力、火花或能量效果。',
        'continuity': 'B03从B02.after的双方位置与持物开始；结束A侧身站稳仍右手持杖，B在碎石前收回上身和刀，为B04主动迫退留出时机。'
    },
    'P03': {
        'identity_action': '摘要依次覆盖B04圆钝杖端逼近、B横刀后退，以及B05斜拨刀身、杖前段短促击压右前臂近腕处、松石滑动、手指松开落刀和一膝触地。未保留剑格缴械；A见落刀收杖停手。',
        'camera_timing': 'P03覆盖B04 7至10秒和B05 10至12.5秒。S01在南侧连续横移后少许后退，落刀完整入画，无切镜或遮挡替换。',
        'ability_cost': '没有能力引用；B退步由杖端逼近触发，失衡落刀由前臂受力和后脚松石共同引起；vfx无血液、火花和能量波，声音对应木杖、衣袖、碎石和土面。',
        'continuity': 'B04继承B03状态并可见退到碎石，B05继承后脚不稳和持刀状态；结束B左手撑地右手空、刀在身侧夯土，A仍右手持完整木杖停在南侧通路前。摘要终态与B05.after对应。'
    },
    'P04': {
        'identity_action': 'B06及摘要都写A右手持杖从南侧空隙通过、两步后转身且圆钝杖端略低；B留在碎石带旁一膝触地、左手撑地右手空，不捡刀。',
        'camera_timing': 'P04为12.5至15秒；14.4秒前完成安全距离转身，末0.6秒保留呼吸、衣摆与尘土。S01南侧连续后移拉成双人全景。',
        'ability_cost': '无能力与新增特效；离开阻挡通过可见两步和转身完成，不瞬移、不追加攻击。',
        'continuity': '起点继承B05的A持杖停手、B跪地空手及刀掉落点；终点保留木杖刮痕、擦痕、碎石和刀原位，保留输入计划的胜负与停手结尾。'
    }
}
reviews = []
for scope in compiled['scopes']:
    reviews.append({
        'scope': scope['scope'],
        'input_digest': scope['input_digest'],
        'expression_digest': scope['expression_digest'],
        'reviewer': '本次计划编辑执行代理',
        'method': 'agent',
        'checks': checks[scope['scope']]
    })
(out / 'receipt.json').write_text(json.dumps({'plan_id': compiled['plan_id'], 'reviews': reviews}, ensure_ascii=False, indent=2) + '\n', encoding='utf-8')
print('Wrote receipt.json for the inspected facts and expressions')
