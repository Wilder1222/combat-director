"""Authoritative synthetic scenarios; build requires pinned editorial receipts."""
import argparse
import copy
import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
SKILL = ROOT / 'skills/combat-director'
sys.path.insert(0, str(SKILL / 'scripts'))
import combat_tool as tool
from combat_action import describe_actor


def state(zone, item='', support='双脚落地'):
    return {'zone': zone, 'facing': '关注对方及退路', 'support': support,
            'held_items': {'left': '', 'right': item}, 'damage': [], 'constraints': []}


def weapon(wid, name, kind, traits, owner, mount='held'):
    return {'id': wid, 'name': name, 'type': kind, 'visible_traits': traits, 'owner_id': owner, 'mount': mount}


def event(eid, actor, target, start, end, action, origin, path, endpoint, contact, outcome,
          response='', item='', hands=(), transfers=(), ability=None):
    e = {'id': eid, 'actor_id': actor, 'target_id': target, 'start': start, 'end': end,
         'response_to': response, 'weapon_id': item, 'hands_used': list(hands), 'movement': 'walk',
         'action': action, 'trajectory': {'start': origin, 'path': path, 'end': endpoint,
         'screen_direction': '保持侧面可读，运动不靠跳切'}, 'contact': contact, 'outcome': outcome,
         'transfers': list(transfers)}
    if ability:
        e['ability_use'] = ability
    return e


def delta(actors=None, environment=None, causes=()):
    return {'actors': actors or {}, 'environment': environment or {}, 'caused_by': list(causes)}


def describe(s, names):
    return describe_actor(s,names)


def make(name, goal, cast, weapons, initial, steps, abilities=()):
    duration = steps[-1]['end']
    plan = {'schema_version': '1.2', 'id': name, 'provenance': '项目原创结构化教学案例；未生成视频，非媒体观察。',
            'template': 'grounded' if not abilities else 'epic', 'duration': duration, 'aspect_ratio': '16:9',
            'generation': 'single', 'camera_mode': 'one-take', 'rules': {'fantasy': bool(abilities), 'max_scale': 'person'},
            'timing': {'lead_in': .2, 'tail_out': .6, 'result_at': duration-.6},
            'anchors': list(initial['environment']), 'cast': cast, 'abilities': list(abilities), 'references': [],
            'weapon_profiles': weapons, 'action_initial_state': copy.deepcopy(initial),
            'headers': {'goal': goal+f'。{duration}秒，一镜到底；最后0.6秒保留呼吸和余动。',
                        'cast': '\n'.join(f'{a["id"]} {a["description"]}，目标{a["goal"]}，初始{a["hand"]}持{a["prop"]}。' for a in cast),
                        'scene': '；'.join(f'{k}：{v}' for k,v in initial['environment'].items())+'。写实布料与地面支撑；动作尺度以规则为限。',
                        'budget': f'0.2秒入点与0.6秒出点均包含在{duration}秒内。',
                        'continuity': '身份、持物、空间和代价继承上一拍；接触过程可见，不用烟雾或镜头遮挡掩盖交接。'},
            'beats': [], 'sections': [], 'editorial_reviews': {}}
    current = copy.deepcopy(initial)
    names={w['id']:w['name'] for w in weapons}
    def text_state(s):
        return {a: describe(v,names) for a,v in s['actors'].items()} | {'environment': '；'.join(f'{k}：{v}' for k,v in s['environment'].items()), 'camera_side': '南侧'}
    plan['initial_state'] = text_state(current)
    start = 0
    for i, step in enumerate(steps,1):
        before = text_state(current)
        for a, patch in step['delta']['actors'].items():
            current['actors'][a].update(copy.deepcopy(patch))
        current['environment'].update(step['delta']['environment'])
        actors = {}
        for a in cast:
            own = [e['action'] for e in step['events'] if e['actor_id']==a['id']]
            actors[a['id']] = {'action': '；'.join(own) or step.get('offscreen',{}).get(a['id'],'留在原区域，观察当前交手，不凭空离场'),
                                'performance': step['performance'][a['id']]}
        beat = {'id': f'B{i:02d}', 'start': start, 'end': step['end'], 'intent': step['intent'], 'actors': actors,
                'emotion': step['emotion'], 'camera': {'shot_id':'S01','transition':'start' if i==1 else 'continuous',
                'side':'南侧','path':step['camera'],'axis_bridge':''}, 'vfx':step.get('vfx','无超自然效果，保留真实动作模糊'),
                'environment':step['environment'], 'sound':step['sound'], 'ability_ids':list(dict.fromkeys(e['ability_use']['ability_id'] for e in step['events'] if 'ability_use' in e)),
                'before':before,'after':text_state(current),'action_events':step['events'],'state_delta':step['delta']}
        plan['beats'].append(beat)
        summary = {'action':'；'.join(f'{a}：{v["action"]}' for a,v in actors.items()),
                   'expression':'；'.join(f'{a}：{v["performance"]}' for a,v in actors.items()),
                   'emotion':beat['emotion'],'camera':step['camera'],'vfx':beat['vfx'],'environment':step['environment'],
                   'sound':step['sound'],'continuity':'；'.join(f'{a}：{describe(v,names)}' for a,v in current['actors'].items())}
        plan['sections'].append({'id':f'P{i:02d}','beat_ids':[beat['id']],'summary':summary})
        start=step['end']
    tool.validate(plan,require_review=False)
    return plan


def scenarios():
    staff=weapon('STAFF','硬木短杖','钝头木杖','深色木纹、无刃无金属护手','A')
    letter=weapon('LETTER','封口密函','纸质道具','米白封套、红色封口、仅一封','B')
    cast=[{'id':'A','description':'成年灰衣女行者','goal':'取回密函后停手','prop':'硬木短杖','hand':'右手'},
          {'id':'B','description':'成年褐衣护函者','goal':'保住密函并脱身','prop':'封口密函','hand':'右手'}]
    initial={'actors':{'A':state('巷南','STAFF'),'B':state('巷北','LETTER')},'environment':{'南口':'可退出','北口':'可退出','砖墙':'完整'}}
    steps=[
      {'end':4,'intent':'第一次索回被阻，双方保留退路','events':[
        event('E1','B','A',.2,2,'左掌推挡A肩前，右手护住密函','B左胸前','短直线前伸','A肩前','掌接衣袖，A后退卸力','密函仍在B右手',hands=['left']),
        event('E2','A','B',2,4,'右手横持木杖轻抵B左前臂，身体斜退半步','A身前','杖身短幅横移','B左前臂外侧','木杖贴住衣袖后即撤离','两人不再贴身推挤','E1','STAFF',['right'])],
       'delta':delta({'A':{'zone':'巷南外缘'}},causes=['E2']), 'performance':{'A':'盯密函，呼气后肩部稍沉','B':'皱眉看杖身，握函指节收紧'},
       'emotion':'急促而克制','camera':'南侧斜向中全景，连续后退半步，手和脚均可见，不切镜', 'environment':'墙面不破坏，鞋底擦出浅灰痕','sound':'掌接布料与木杖擦袖，无金属火花或碰撞长鸣'},
      {'end':10,'intent':'让出退路换回密函','events':[
        event('E3','A','B',4,7,'停住木杖并伸空着的左掌，让出通往北口的直路','巷南外缘','向墙边移半步','墙边','不再发生攻击接触','B看见畅通北口',item='STAFF',hands=['right','left']),
        event('E4','B','A',7,10,'看到退路后将密函递入A左掌并松手','B右胸前','纸封沿可见直线伸出','A左掌','纸封由两人短暂共触后完全交接','B右手空，A左手持函','E3',hands=['right'],transfers=[{'item_id':'LETTER','from_actor':'B','from_hand':'right','to_actor':'A','to_hand':'left','destination':'A左手'}])],
       'delta':delta({'A':{'held_items':{'left':'LETTER','right':'STAFF'}},'B':{'held_items':{'left':'','right':''}}},causes=['E3','E4']),
       'performance':{'A':'目光先看封口再回到B，握杖手放松','B':'看北口后吐气，右手手指逐一松开'},'emotion':'从争持转为止争',
       'camera':'同侧连续小幅跟进，保持两双手与纸封交接可见，不切镜','environment':'封口完整，纸函只有一封，地面擦痕保留','sound':'纸张轻响，脚步暂停，呼吸可闻'},
      {'end':15,'intent':'双方脱离','events':[
        event('E5','A','B',10,13,'左手持函贴胸，右手垂杖，向南口退开','墙边','沿巷南退两步','南口内侧','没有新接触','A取得密函且不追击',item='STAFF',hands=['right','left']),
        event('E6','B','A',13,14.4,'双手张开并向北口退开','巷中','北向两步','北口内侧','没有新接触','B可以离开，最后0.6秒只保留呼吸','E5')],
       'delta':delta({'A':{'zone':'南口内侧'},'B':{'zone':'北口内侧'}},causes=['E5','E6']),
       'performance':{'A':'肩部放松但仍看B双手','B':'确认A停手后缓缓吐气'},'emotion':'克制收束','camera':'同一机位侧连续拉开至全景，保留两端退路',
       'environment':'墙与纸封完整，擦痕不复位','sound':'相反方向的脚步和轻微巷风，无台词'}]
    yield make('alley-letter-15','窄巷取回密函，低能力尺度，双方均可退出',cast,[staff,letter],initial,steps)

    # Three actors: C remains represented while temporarily offscreen.
    c3=copy.deepcopy(cast)
    c3[0].update(goal='保护C穿过出口')
    c3[1].update(description='成年黑衣拦路者',goal='挡住出口',prop='短刀')
    c3.append({'id':'C','description':'成年蓝衣信使','goal':'带密函穿过出口','prop':'封口密函','hand':'右手'})
    knife=weapon('KNIFE','短刀','单刃短刀','暗色刀柄、短而宽的刀身','B')
    l3=copy.deepcopy(letter);l3['owner_id']='C'
    i3={'actors':{'A':state('通道南侧','STAFF'),'B':state('出口前','KNIFE'),'C':state('A后方','LETTER')},'environment':{'出口':'东侧畅通','墙角':'可提供遮挡但不是瞬移通道'}}
    s3=[
      {'end':6,'intent':'A吸引正面阻挡','events':[
        event('T1','B','A',.2,2,'以短刀横在通道前压迫A退后','出口前','步行向通道中央','A前方','未刺中身体','B注意转向A',item='KNIFE',hands=['right']),
        event('T2','A','B',2,5.5,'右手木杖侧拨短刀并侧移，左掌示意C沿后路走','通道南侧','向南侧半步','墙角外侧','刀碰木短促闷响，无火花','B跟随A偏离出口直线','T1','STAFF',['right','left'])],
       'delta':delta({'A':{'zone':'墙角外侧'},'B':{'zone':'通道中央'}},causes=['T1','T2']),
       'performance':{'A':'看刀后短看C，呼吸有节奏','B':'视线追随木杖','C':'盯出口，攥紧密函'},'emotion':'压迫中争取空间','camera':'南侧三人全景，横移保留出口与C的起点','environment':'墙角与出口关系清晰','sound':'刀碰木闷响与三组脚步'},
      {'end':12,'intent':'C从既有后路离开，A不追击','events':[
        event('T3','C','A',6,10,'持函沿A身后步行通过出口','A后方','沿墙边既有后路','出口外','不与兵器接触','C和密函到出口外',item='LETTER',hands=['right']),
        event('T4','A','B',10,12,'收杖到身前并后退，继续面对B','墙角外侧','沿南侧后退','出口近侧','与B刀路脱离','A留出跟随C撤离的间隙','T2','STAFF',['right'])],
       'delta':delta({'C':{'zone':'出口外'},'A':{'zone':'出口近侧'}},causes=['T3','T4']),
       'performance':{'A':'听到C脚步渐远后略松肩','B':'仍看A，短刀收回','C':'开始进入画外，脚步保持步行'},'emotion':'护送逐步成立','camera':'同侧连续跟随A，C从画面边缘经已交代出口离开，不能突然消失','environment':'出口没有新增障碍','sound':'C脚步沿出口方向渐远，前景呼吸与衣料声'},
      {'end':18,'intent':'A撤离，B停止追进','events':[
        event('T5','A','B',12,15,'面向B退到出口再转身离开','出口近侧','连续后退再转身','出口外','无新交接','A与C会合',item='STAFF',hands=['right']),
        event('T6','B','A',15,17.4,'停在通道中央放低短刀，不追入出口','通道中央','脚步停稳','通道中央','无接触','威胁留在原空间','T5','KNIFE',['right'])],
       'delta':delta({'A':{'zone':'出口外'}},causes=['T5']), 'offscreen':{'C':'保持出口外，不重新进入交手；密函仍在右手'},
       'performance':{'A':'确认C后吐气','B':'目光停在出口','C':'画外回应脚步停稳，不捏造面部特写'},'emotion':'有限胜利','camera':'连续拉开留下出口和B，C保持明确画外位置','environment':'墙角与出口不变','sound':'出口外脚步停下，无新增交锋'}]
    yield make('three-person-exit-18','三人护送，C在局部画外仍有连续状态',c3,[staff,knife,l3],i3,s3)

    # Synthetic failed counterplay: shelf stays jammed; ability cost persists.
    cf=copy.deepcopy(cast)
    cf[0].update(description='成年巡检剑士',goal='撤出机甲活动范围',prop='硬木短杖')
    cf[1].update(description='工业四足守卫机',goal='阻止A通过',prop='前置机械臂',hand='不持械')
    arm=weapon('ARM','机械臂','安装式机械结构','单一前置关节与钝面抓手','B','mounted')
    ability={'id':'GUARD','owner':'A','trigger':'站稳短暂撑起局部屏障','limit':'只挡一次正面接触','cost':'结束后右手失去握持能力','end_condition':'承受一次接触后消散','visual':'掌前一块半透明薄面','scale':'person','supernatural':True}
    initialf={'actors':{'A':state('控制柱旁','STAFF'),'B':state('货架另一侧')},'environment':{'货架':'导轨卡住，不能落下','闸门按钮':'控制柱左侧可触及','东侧闸门':'开启，A可以从侧面退出'}}
    sf=[
      {'end':6,'intent':'货架反制失败后抵住一次压迫','events':[
        event('F1','A','B',.2,2,'观察到货架导轨卡住，站稳撑起局部屏障','控制柱旁','左掌向前短推','身前薄面','尚未接触机械臂','屏障仅遮身体前方',hands=['left'],ability={'ability_id':'GUARD','phase':'activate','visible_cost':'呼吸变急','restrictions_added':[]}),
        event('F2','B','A',2,5.5,'机械臂前压接触薄面后减速','货架另一侧','沿直线压近','屏障表面','机械臂接触薄面，无穿透身体','屏障开始裂开','F1','ARM')],
       'delta':delta(environment={'货架':'导轨仍卡住，未落位'},causes=['F1','F2']), 'performance':{'A':'视线看导轨后转机械臂，咬牙呼气','B':'状态灯稳定，臂关节减速'},'emotion':'原反制失效，转为保命','camera':'南侧大全景同时交代卡住的货架和接触点','environment':'导轨保持卡住，不能偷偷完成落架','sound':'导轨空转与一次接触闷响','vfx':'掌前小范围薄面，接触后出现裂纹'},
      {'end':12,'intent':'支付代价并换用空闲左手','events':[
        event('F3','A','B',6,9,'屏障消散后右手松开，木杖沿身侧落地，身体退到按钮旁','控制柱旁','身体侧退半步，杖沿竖向下降','按钮旁与脚侧地面','木杖先离手再触地','右手不能继续动作，左手仍可用',hands=['right'],transfers=[{'item_id':'STAFF','from_actor':'A','from_hand':'right','to_actor':'','to_hand':'','destination':'控制柱脚侧地面'}],ability={'ability_id':'GUARD','phase':'consume','visible_cost':'右手指节松开、前臂垂下，无法再握杖','restrictions_added':['no_right_hand']})],
       'delta':delta({'A':{'zone':'按钮旁','held_items':{'left':'','right':''},'constraints':['no_right_hand']}},causes=['F3']),
       'performance':{'A':'看落杖后转按钮，右臂垂下','B':'臂关节回收后继续追踪'},'emotion':'承认代价并选择撤离','camera':'同侧连续跟进，把松手到落地完整留下','environment':'木杖留在柱脚，货架仍卡住','sound':'屏障散去后木杖落地，A短促呼吸','vfx':'薄面消散不再复制'},
      {'end':18,'intent':'左手关闭隔离闸后撤出','events':[
        event('F4','A','B',12,15,'用左手按下现有隔离按钮并跨到闸门外侧，右手始终垂下','按钮旁','左掌触钮后步行侧出','闸门外侧','左手触钮，门体随后沿轨道下降','隔离闸挡住机械臂',hands=['left']),
        event('F5','B','A',15,17.4,'机械臂接近闸门后停住，机体不能穿门','货架侧','短距离前移后制动','门内侧','机械臂轻触实体门后回收','A完成撤离，B仍可动','F4','ARM')],
       'delta':delta({'A':{'zone':'闸门外侧'},'B':{'zone':'门内侧'}},{'东侧闸门':'关闭，隔开A与机械臂'},['F4','F5']),
       'performance':{'A':'左手离钮后呼气，右臂持续垂下','B':'状态灯保留，关节慢慢回收'},'emotion':'带代价的有限脱离','camera':'同镜连续后退，清楚留下闸门内外关系','environment':'闸门关闭，货架仍卡住，木杖仍在柱脚','sound':'按钮声后门轨移动，末尾呼吸与低机械声'}]
    yield make('failed-counter-repair-18','环境反制失败后用左手隔离闸撤离，右手代价持续',cf,[staff,arm],initialf,sf,[ability])


def main():
    parser=argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--drafts', action='store_true')
    args=parser.parse_args()
    for plan in scenarios():
        if args.drafts:
            folder=ROOT/'outputs/action-drafts'
        else:
            receipt=tool.read_json(ROOT/'sources/editorial/0.4.0'/f'{plan["id"]}.review.json')
            plan=tool.apply_review(plan,receipt)
            tool.validate(plan)
            folder=SKILL/'examples'
        folder.mkdir(parents=True,exist_ok=True)
        (folder/f'{plan["id"]}.plan.json').write_text(json.dumps(plan,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
        if not args.drafts:
            (folder/f'{plan["id"]}.prompt.txt').write_text(tool.prompt(plan),encoding='utf-8')
        print(plan['id'])


if __name__=='__main__':
    main()
