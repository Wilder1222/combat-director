import json
from pathlib import Path

root = Path(r'D:\Temp\combat-director-evals-20260921\final-e02')
compiled = json.loads((root/'work/review-input-final.json').read_text(encoding='utf-8'))
checks = {
 'headers': {
  'identity_action':'对照cast、initial_state及ending_state：A身份服装不变，右手中后段握1.4米实心无金属木杖，左手空；B仍右手短刀。总设定记录斜挡、木痕、近腕接触与失足脱刀，未保留金属碰撞火花。',
  'camera_timing':'duration=15，16:9，single和one-take不变；入点0.2秒、结尾0.6秒均计入15秒，14.4秒完成通过转身；所有拍S01、南侧连续移动。',
  'ability_cost':'rules.fantasy=false、max_scale=person、abilities为空；总设定限于可见身体动作、木材接触与碎石受力，无新增超自然能力，不适用能力消耗。',
  'continuity':'起点A在B正西、B在北缘以南；西北退追、A南移、东北逼退形成完整路线；终点A经南侧通过后东南约2.2米转身，B留北缘跪地、刀在身侧，保持用户结尾。木痕、脚印和衣膝尘土均延续。'
 },
 'P01': {
  'identity_action':'摘要逐项对应B01和B02：A右手木杖斜挡第一次探刀后西退，接着两次短幅斜挡；B右手短刀跟进，木材接触为短响和刮擦，无金属长鸣和火花。',
  'camera_timing':'B01为0至2秒、B02为2至4.5秒，主段覆盖0至4.5秒。0至0.2秒站姿余量保留；S01从南侧向西连续跟移，脚和杖端在画内。',
  'ability_cost':'双方均为人物级正常步法，未加入能力；A以退步恢复重心，接触后回收木杖，木材留下浅痕不被重置。',
  'continuity':'A试探小步后退略大半步解释首拍终点西移；下一拍A西北退、B西北追，两者均有北向位移，故B到北缘南0.8米有动作依据。P01终态等于B03起态。'
 },
 'P02': {
  'identity_action':'摘要对应B03：A向南半步并右手斜立木杖引刀；B向西探半步后回收，转向西南面对A。双方面貌、服装、持物与持械手保持一致。',
  'camera_timing':'对应B03的4.5至7秒；S01连续小幅跟进，机位仍南侧，双脚侧移和转向可见。',
  'ability_cost':'无能力调用；双脚重新落稳和B探步后收回身体构成自然恢复，不添加瞬移或效果替身。',
  'continuity':'从A在B正西1.2米出发，仅A向南侧移到B西南约1.3米；B退回本拍起点，距碎石带仍0.8米；因此下一段东北方向进逼会将B带向北缘。'
 },
 'P03': {
  'identity_action':'摘要覆盖B04与B05：木杖前端短直线进逼被B刀背侧格开；B后退踏碎石后再次探刀，木杖前段接触右前臂近腕衣袖，持刀臂偏开，碎石失足、手指展开、落刀、左膝左掌着地依次可见，无剑格夺刀。',
  'camera_timing':'7至10秒逼退，10至12.5秒失位脱刀；同一S01从南侧向东小移再向南退，镜头保留手、杖、脚与刀的连续轨迹。',
  'ability_cost':'无幻想能力；短刀和木杖、衣袖接触及碎石滑动解释结果，B膝上尘土成为持续状态，无无接触缴械或额外伤害。',
  'continuity':'A在B西南向东北进、B沿东北实际退，后脚进入北缘碎石带；B05向北滑出小步使静止A与B间距由约1.1米增到1.3米。B右手从持刀变为空，刀留右侧半米内；A收杖停手，下一拍继承。'
 },
 'P04': {
  'identity_action':'B06及摘要一致：A右手木杖不换手、杖前端略放低；B右手空，不重新捡刀。A克制停手与B较快呼吸保留原结尾表演。',
  'camera_timing':'主段12.5至15秒；12.5至14.4秒两大步通过并转身，最后0.6秒呼吸与沉尘；南侧S01连续向东南后退平移，双方和落刀同框。',
  'ability_cost':'无新增能力、飞跃或慢动作；通过只使用两大步和连续转身，最后保留自然呼吸。',
  'continuity':'A从B西南出发，经B南側空隙向东南移动到约2.2米再朝西北转身；B保持北缘原落点、左膝与左掌支撑，只转头朝东南看A，短刀和既有痕迹不复位。'
 }
}
reviews = [{
 'scope': scope['scope'], 'input_digest': scope['input_digest'],
 'expression_digest': scope['expression_digest'],
 'reviewer': '本次计划编辑代理', 'method': 'agent', 'checks': checks[scope['scope']]
} for scope in compiled['scopes']]
(root/'work/receipt.json').write_text(json.dumps({'plan_id':compiled['plan_id'], 'reviews':reviews}, ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
print('Wrote semantic comparison receipt for headers and P01-P04.')
