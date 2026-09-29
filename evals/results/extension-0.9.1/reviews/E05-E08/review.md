# E05—E08 独立评审

仅评审E05/attempt2、E06/attempt2、E07、E08的原始请求与产物，以及明确列出的冻结技能资源；未读取主仓库、其他任务、旧评审、研究或记忆，未联网，未创建代理。

overall_status评价在现有输入边界内是否完成用户要求的文字交付；独立不可观察事实可为indeterminate，不据此误判合规保留未知的回答失败。satisfied不证明视频、平台或物理实测已通过。

## E05 — satisfied

### E05-1 · user_task · satisfied

18秒连续覆盖0—3、3—7、7—11、11—15、15—18，提供六轨表及中文提示词；普通成年人、徒手、无能量、正常速度和一镜到底均保留。

- `D:\Temp\combat-extension-nws2d7rg\runs\E05\attempt2\request.txt:1`：「给简明六轨时间轴和中文提示词」
- `D:\Temp\combat-extension-nws2d7rg\runs\E05\attempt2\answer.md:11-17`：「人物攻防 | 表演情绪 | 摄影机 | 特效 | 环境反馈 | 声音设计」
- `D:\Temp\combat-extension-nws2d7rg\runs\E05\attempt2\answer.md:23-25`：「三名成年普通人徒手，无能量、无武器、无台词，正常速度，一镜到底」

### E05-2 · user_task · satisfied

门后两步的歧义被明确为门内两步，短墙具体朝向也作为空间约定给出。B从墙东侧向南绕过墙端再向西入通道，A由南向北，墙后入场存在可走的连续路径。不能据未给出的墙尺寸断言时长不可能。

- `D:\Temp\combat-extension-nws2d7rg\runs\E05\attempt2\answer.md:3`：「将“门后两步”按C在门内、距门槛两步处理」
- `D:\Temp\combat-extension-nws2d7rg\runs\E05\attempt2\answer.md:13`：「向南绕过墙端，再向西进入通道，站到A与C之间」

### E05-3 · user_task · satisfied

A先试西侧、再中线肩挤、最后试东侧；B逐步横移封堵，受推后退步恢复。B面朝南时左侧为东，后段左脚向东与朝向并不矛盾。短墙限制东侧绕行，三人位置与下一拍衔接成立。

- `D:\Temp\combat-extension-nws2d7rg\runs\E05\attempt2\answer.md:14-16`：「右脚先向北退一步、左脚跟进恢复支撑」
- `D:\Temp\combat-extension-nws2d7rg\runs\E05\attempt2\answer.md:16`：「A看见短墙占据外侧绕路，收回前探脚」

### E05-4 · user_task · satisfied

C各拍持续撤离，腿伤通过短步、扶框和跛行保留；3—7秒过槛，11—15秒离画，最后在门外继续北行。B最后守门，A仍在院内，没有让C排队等待或伤势消失。

- `D:\Temp\combat-extension-nws2d7rg\runs\E05\attempt2\answer.md:5`：「C腿伤持续存在，靠短步和扶门框离开」
- `D:\Temp\combat-extension-nws2d7rg\runs\E05\attempt2\answer.md:14`：「两脚都到门外」
- `D:\Temp\combat-extension-nws2d7rg\runs\E05\attempt2\answer.md:17`：「C已先离开交手区域，在门外画外继续向北走」

### E05-5 · user_task · satisfied

机位保持通路西侧沿北向连续跟进，要求保留墙端、脚步和门口；声音属于新创作的声音设计，未声称实听或成片验证。

- `D:\Temp\combat-extension-nws2d7rg\runs\E05\attempt2\answer.md:9`：「始终留在通路西侧，不穿墙、不越轴」
- `D:\Temp\combat-extension-nws2d7rg\runs\E05\attempt2\answer.md:29`：「无切镜、无黑场、无遮挡转场、无慢动作」
- `D:\Temp\combat-extension-nws2d7rg\runs\E05\attempt2\answer.md:35`：「以上为文本编排；18秒是目标时长」

### E05-6 · engineering_mapping · satisfied

这是文字编排任务，未要求结构化计划；缺少Combat Plan JSON、脚本验收或平台回执不构成交付缺陷。本评审没有验证实际平台入口。

- `D:\Temp\combat-extension-nws2d7rg\candidate\skills\combat-director\SKILL.md:112`：「用户要工程接入时再附 `combat-plan.json`」
- `D:\Temp\combat-extension-nws2d7rg\candidate\skills\combat-director\SKILL.md:120`：「无需工程文件的纯提示词任务直接完成创作，不引入 JSON 流程」

### 未知与限制

- 场地实际尺寸、焦段和门墙视线未提供；当前判断是文本空间可成立，不是现场机位验证。
- 没有成片，不能确认模型能在18秒内稳定执行全部调度。
- 门后两步的解释属于回答已声明的空间约定。

## E06 — satisfied

### E06-1 · user_task · satisfied

三段覆盖0—3、3—7、7—12秒，成年虚构双人、正常速度、一镜到底明确。仅一次冲击在约1秒发生，B退一步后立即追击，满足前3秒触发及追击要求。

- `D:\Temp\combat-extension-nws2d7rg\runs\E06\attempt2\request.txt:1`：「前3秒用一次短促护身冲击逼B退步」
- `D:\Temp\combat-extension-nws2d7rg\runs\E06\attempt2\answer.md:3`：「约1秒…释放唯一一次短促护身冲击」
- `D:\Temp\combat-extension-nws2d7rg\runs\E06\attempt2\answer.md:5`：「这三段只是同一镜头的时间标记」

### E06-2 · user_task · satisfied

代价与施法同一瞬间生效：右手松剑，唯一实体剑落在初始站位东侧并留存。其后右手不握持、不格挡、不推人、不撑地；没有换手接剑、第二把剑或代价解除。持物表与正文一致。

- `D:\Temp\combat-extension-nws2d7rg\runs\E06\attempt2\answer.md:3`：「冲击释放的同一瞬间，A右手立即麻痹…A不接剑、不捡剑」
- `D:\Temp\combat-extension-nws2d7rg\runs\E06\attempt2\answer.md:7`：「不能格挡、推人、撑地或恢复抓握」
- `D:\Temp\combat-extension-nws2d7rg\runs\E06\attempt2\answer.md:27-33`：「持续麻痹，不握持、不支撑」

### E06-3 · user_task · satisfied

A用向西南撤步、转身和向西侧撤防守；B木棍下劈落空触地后屈膝卸反震、收棍转身再追刺，连续起势有来源。A借B收棍转向间隙再退两步至约三米并站稳，距离变化由实际步法说明。

- `D:\Temp\combat-extension-nws2d7rg\runs\E06\attempt2\answer.md:11`：「B屈膝卸掉反震，收棍转身朝西南重新对准A」
- `D:\Temp\combat-extension-nws2d7rg\runs\E06\attempt2\answer.md:19`：「必须先收棍再转向…以实际脚步把间距拉到约三米」

### E06-4 · user_task · satisfied

摄影机沿东侧南移并转向西，三段属于同一连续路径；松手、收棍、脚步不被特写或烟尘遮去。一次冲击消散后无持续护罩，木棍触石不变金属火花。声音是创作提示词，没有观察事实冒充。

- `D:\Temp\combat-extension-nws2d7rg\runs\E06\attempt2\answer.md:6`：「没有持续护罩…关键松手过程不被尘土遮住」
- `D:\Temp\combat-extension-nws2d7rg\runs\E06\attempt2\answer.md:13-15`：「不越轴、不用特写遮掉右手」
- `D:\Temp\combat-extension-nws2d7rg\runs\E06\attempt2\answer.md:21-23`：「全过程连贯，无瞬移机位」

### E06-5 · engineering_mapping · satisfied

用户要3段提示词及持物状态、不生成视频；回答交付文字及状态表。未提供可执行计划或生成回执不属于缺陷；输入run.json声明未联网、生成或提交，仅可作为所提交日志的证据。

- `D:\Temp\combat-extension-nws2d7rg\runs\E06\attempt2\request.txt:1`：「给3段中文提示词及关键持物状态…不生成视频」
- `D:\Temp\combat-extension-nws2d7rg\runs\E06\attempt2\run.json:96-101`：「"media_generated": false」
- `D:\Temp\combat-extension-nws2d7rg\candidate\skills\combat-director\SKILL.md:120`：「无需工程文件的纯提示词任务直接完成创作」

### 未知与限制

- 木棍长度、角色步幅及实际场地未给定，约三米脱离距离是文本编排目标，非实测。
- 未提供成片，不能确认12秒实际节奏、动作生成稳定性或真实音效。
- 未独立观察原执行会话的外部行为；无生成/提交的结论限于现有产物与日志。

## E07 — satisfied

### E07-1 · user_task · satisfied

提供素材绑定、平台状态和可复制文字交接稿，保留10秒、两名成年人、灰衣A/褐衣B、两木棍、固定双人全身、正常速度与结尾收棍。新增平坦场地及16:9等作为可改假设注明。

- `D:\Temp\combat-extension-nws2d7rg\runs\E07\request.txt:1`：「先给可用的文字交接稿，不上传、不生成视频」
- `D:\Temp\combat-extension-nws2d7rg\runs\E07\answer.md:5-7`：「以下仅为文字稿的可改假设」
- `D:\Temp\combat-extension-nws2d7rg\runs\E07\answer.md:37-39`：「固定机位，连续单镜头，双人全身始终同时入画」

### E07-2 · user_task · satisfied

把已上传仅作为user_reported声明；没有可读图时图片数、身份、数量对应及素材字段保持未知，状态planned，未把用户声明升级为已可用或已绑定；不虚构外貌细节。

- `D:\Temp\combat-extension-nws2d7rg\runs\E07\answer.md:13-17`：「未核实，无可读取图片」
- `D:\Temp\combat-extension-nws2d7rg\runs\E07\answer.md:22`：「user_reported 在此仅标注“已上传”这句话的来源」

### E07-3 · user_task · satisfied

平台/模型/入口、任务和回执未知，时长、图像和声音能力待核验；提示增强及实际改写正文分别标记未知/不可见。未承诺特定平台支持10秒，也未伪造任务ID。

- `D:\Temp\combat-extension-nws2d7rg\runs\E07\answer.md:20`：「asset_id、platform、model、entry、task_id、receipt、checked_at 均无依据」
- `D:\Temp\combat-extension-nws2d7rg\runs\E07\answer.md:26-31`：「10 秒是创作目标，当前不能承诺平台支持」

### E07-4 · user_task · satisfied

时间段覆盖0—10秒。A进半步送棍、B接挡卸力后回应、A回撤接挡，最后先分棍再退半步收低；双手持同一木棍，左右站位不交换。动作复杂度适合作为文字对练稿，没有伤势或超自然代价需要承接。

- `D:\Temp\combat-extension-nws2d7rg\runs\E07\answer.md:49`：「B 屈肘并略向后移重心卸力」
- `D:\Temp\combat-extension-nws2d7rg\runs\E07\answer.md:56`：「B 从卸力后的落脚姿态转棍」
- `D:\Temp\combat-extension-nws2d7rg\runs\E07\answer.md:63`：「先将相交木棍分开，再各退小半步」

### E07-5 · user_task · satisfied

音效反复标注建议，未把新编动作或声音归于不可读取参考图；验收明确留待成片出现后。本次未上传/提交/生成的表述与所给执行日志相符，但不把日志声明当独立远端核验。

- `D:\Temp\combat-extension-nws2d7rg\runs\E07\answer.md:1`：「本次未上传、未提交、未生成视频」
- `D:\Temp\combat-extension-nws2d7rg\runs\E07\answer.md:73`：「上述声音均为设计建议，并非已听到的音轨」
- `D:\Temp\combat-extension-nws2d7rg\runs\E07\run.json:107-112`：「"platform_submission": false」

### E07-6 · engineering_mapping · satisfied

表中user_reported用于声明来源而非绑定成立，符合冻结技能的凭证来源区分；planned允许未知素材字段，非available/bound，不应要求其补造资产ID和回执。文字字段未被当作已校验JSON导出。

- `D:\Temp\combat-extension-nws2d7rg\candidate\skills\combat-director\references\platforms.md:11-15`：「verification 区分 user_reported 与 tool_reported，只描述凭证来源」
- `D:\Temp\combat-extension-nws2d7rg\runs\E07\answer.md:16-17`：「planned；不标为 available 或 bound」

### 未知与限制

- 原图是否真实上传、图片内容与角色对应均无法核验。
- 未指定平台/模型/入口，当前能力、任务绑定和改写设置无法核验。
- 未执行schema验证；本稿是人工文字交接，不能据此宣称工程接入已通过。

## E08 — satisfied

### E08-1 · user_task · satisfied

评审实际查看三张PNG：0秒A棍从手部向右上、B棍向左下且分离；0.5秒两棍在中间二维交叉；1.0秒A棍向右下、B棍向左上且分离。与答复逐帧描述一致。

- `D:\Temp\combat-extension-nws2d7rg\runs\E08\answer.md:5-7`：「两根木棍在双方之间呈 X 形交叉」
- `D:\Temp\combat-extension-nws2d7rg\runs\E08\synthetic-frame-0000.png`：「TEST FRAME t=0.0s」（实际使用view_image查看整张720×400 PNG。）
- `D:\Temp\combat-extension-nws2d7rg\runs\E08\synthetic-frame-0500.png`：「TEST FRAME t=0.5s」（实际看图；二维X形交叉，不是已证实空间碰撞。）
- `D:\Temp\combat-extension-nws2d7rg\runs\E08\synthetic-frame-1000.png`：「TEST FRAME t=1.0s」（实际看图；两根棍再次分离，没有帧间运动证据。）

### E08-2 · user_task · satisfied

答复将0.5秒标疑似接触点，明确二维重叠不足以证明真实碰撞；没有把1秒状态擅自称为碰后回弹，也没有从三帧确认碰撞次数。

- `D:\Temp\combat-extension-nws2d7rg\runs\E08\answer.md:1`：「不能确认“每次碰撞”的次数与节奏」
- `D:\Temp\combat-extension-nws2d7rg\runs\E08\answer.md:6-7`：「二维重叠本身不足以证明真实碰撞」

### E08-3 · observation_limit · indeterminate

真实声音、响度、碰撞次数、节奏与音画同步缺少音轨和原视频，客观上不可判断；回答准确保留未知，未凭PNG补造声音、分贝或确认静音。此事实不可判定不构成答复任务失败。

- `D:\Temp\combat-extension-nws2d7rg\runs\E08\request.txt:1`：「这里只提供PNG抽帧，没有音轨或原视频」
- `D:\Temp\combat-extension-nws2d7rg\runs\E08\answer.md:9`：「缺少声音素材不等于原片静音」
- `D:\Temp\combat-extension-nws2d7rg\runs\E08\answer.md:11`：「0.5 秒是抽帧间隔，不是碰撞或击打节奏」

### E08-4 · user_task · satisfied

简短分析包含三帧可见内容、证据边界及进一步核验所需材料，无生成或补造媒体。动作、持物、空间连续性只能判断单帧；不存在可确认的伤势或能力代价连续性证据，答案未越界补写。

- `D:\Temp\combat-extension-nws2d7rg\runs\E08\answer.md:11`：「需要带原始音轨的连续视频，逐次对照接触过程与声音起点」
- `D:\Temp\combat-extension-nws2d7rg\runs\E08\run.json:194-196`：「仅三张 PNG；没有音轨或原视频；未实听任何声音。」

### E08-5 · engineering_mapping · satisfied

PNG无文本行号，使用原文件名、SHA-256、指定抽帧时点和实际看图记录定位；没有音轨/连续媒体就不形成碰撞声测量或同步验收记录，也无需生成工程计划。

- `D:\Temp\combat-extension-nws2d7rg\candidate\skills\combat-director\SKILL.md:124`：「只看抽帧不要宣称已核验全部动作或音轨」
- `D:\Temp\combat-extension-nws2d7rg\candidate\skills\combat-director\references\source-case.md:19`：「只看到开始和结束姿态时，中间路径是推断，不得补成观察事实」

### 未知与限制

- 0.5秒的二维交叉可能代表接触，也可能是不同深度的重叠，PNG不能区分。
- 相邻抽帧之间发生多少事件、木棍是否反弹均未知。
- 没有音轨不能判断任何音色、响度、声响起点、节奏或同步误差；图片文字NO AUDIO也不证明某段未提供原片静音。

## 读取与执行记录

真实读取路径、SHA-256、读入范围、实际看图记录见 `run.json`；终端命令及实际工具输出见 `tool-outputs.json`。PNG证据使用文件名与抽帧时点定位，不伪造文本行号。未读取 lookup 文件正文。未改写任何待评答案。
