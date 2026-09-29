# E09 / E12 独立评审

结论：两题均 **satisfied**，指本次所要求的文字/文件交付。媒体效果均 **indeterminate**。只评估允许范围内的请求和实际产物，没有改写答案。

## E09 — satisfied

### E09-F1 · text_delivery · satisfied

原计划与原提示词确有相应读取日志，当前原件 SHA-256 与执行记录匹配；本次独立读取并逐项比较。正式 revised.plan.json、prompt.txt、director.md 和复测点齐全，正文提示词与正式导出一致。

- `runs\E09\request.txt` L1：只修第3主段的握持和动作连接，保持其他主段、人物、镜头要求与结尾不变
- `runs\E09\original.plan.json` $.beats[3].actors.A.action; $.beats[4].actors.A.action：迈一步主动交锋，逼出对方后退的空隙，不加额外空翻 / 完成最后一次清楚交接，看见对方失位便停止继续攻击
- `reviews\E09-E12\independent-checks.json` $：prompt_outside_P03_unchanged=true; all_cameras_equal=true; P03_exit_unchanged=true; answer_prompt_equals_export=true
- `runs\E09\lookup-13.txt` L1：Exported 7 files: D:\Temp\combat-extension-nws2d7rg\runs\E09\export
- `runs\E09\answer.md` L92–98：关键连接被遮挡而无法判断时记为“未确认”，不能凭单帧判通过

### E09-F2 · change_scope · satisfied

独立递归差异仅见 B04/B05 的 A 动作、两拍内部 A 状态、P03 动作/连续性摘要，以及 P03/P04 的复核记录。B01–B03/B06、P01/P02/P04 内容、人物、镜头、表演、声音、特效与结尾保持不变；原提示词 P03 外逐字一致。P04 复核更新没有改写第4主段。

- `runs\E09\revised.plan.json` $.beats[3].actors.A.action; $.beats[3].after.A; $.beats[4].actors.A.action; $.beats[4].before.A; $.sections[2].summary.{action,continuity}：右手五指持续合拢握住剑柄
- `reviews\E09-E12\independent-checks.json` $：prompt_outside_P03_unchanged=true; all_cameras_equal=true; P03_exit_unchanged=true; answer_prompt_equals_export=true
- `runs\E09\receipt.json` $.reviews[0].checks; $.reviews[1].checks; L11–14; L24–27：此为文本语义复核，未验证视频

### E09-F3 · action_prop_space · satisfied

修订把持柄、手腕与剑的共同运动、接触后屈肘回收与落脚、第二次交接及停手串联，未加新的兵器或能力。A 从道路中部向北侧 B 前进一步；B 接剑后退入既有碎石带，再因失衡/持刀手被带偏而松刀。只有 B 短刀离手，A 的直剑持续右手持握。细拍与投喂摘要顺序一致。

- `runs\E09\revised.plan.json` L244; L271; L284; $.beats[4].actors.B.action：手、柄、护手和剑身沿同一连续短弧移动
- `runs\E09\revised.plan.json` $.beats[3].actors.A.action; $.beats[3].after.A; $.beats[4].actors.A.action; $.beats[4].before.A; $.sections[2].summary.{action,continuity}：右手五指持续合拢握住剑柄
- `runs\E09\export\prompt.txt` L47–56; comparison with original.prompt.txt：唯一离手兵器是B的短刀

### E09-F4 · state_inheritance · satisfied

独立检查全部相邻 after/before 相等。第3主段入口承接 B03；内部更新同时落在 B04.after.A/B05.before.A；B05 出口未变并传给 B06。最后仍是 A 通过后转身、右手剑略低，B 北侧一膝触地、右手空，落刀留存。

- `runs\E09\revised.plan.json` $.beats[2].after == $.beats[3].before; $.beats[3].after == $.beats[4].before; $.beats[4].after == $.beats[5].before：通路前停止攻击，右手剑保持警戒 / 北侧一膝触地，右手空，刀在身侧地面
- `reviews\E09-E12\independent-checks.json` $：prompt_outside_P03_unchanged=true; all_cameras_equal=true; P03_exit_unchanged=true; answer_prompt_equals_export=true

### E09-F5 · observation_boundary · satisfied

将离手漂移明确归于用户观看报告；未拿到视频，未把文本歧义推断当成帧级观察或已证实成因。复测要求连续帧、原条件可控项、遮挡时标未确认，并覆盖局部入口/出口及整片回归；没有执行生成。

- `runs\E09\answer.md` L1; L10; L16：潜在歧义，不作为已观察到的视频原因 / 不证明视频效果
- `runs\E09\answer.md` L92–98：关键连接被遮挡而无法判断时记为“未确认”，不能凭单帧判通过
- `runs\E09\export\review.md` L1–14：未生成、未观看视频；本表不是验收通过证明。

### E09-F6 · engineering · satisfied

本次以 Python -B 只读复跑 status/validate，退出码均为0；原计划全部 ready，草稿 P03/P04 stale，正式修订全部 ready。revised、verified 与 export/combat-plan.json 内容一致，正式计划与导出计划字节也一致。历史三次日志包装器异常已披露，后续成功凭证与本次独立校验足以确认当前工程状态。未重做导出操作。

- `reviews\E09-E12\validate-revised.plan.json.txt` L1：VALID: grounded-15; 6 beats, 4 sections; reviewed revision matches
- `reviews\E09-E12\status-revised.plan.json.txt` $[*].status：ready
- `reviews\E09-E12\status-revised.draft.plan.json.txt` $[3:5].status：stale
- `reviews\E09-E12\independent-checks.json` $：prompt_outside_P03_unchanged=true; all_cameras_equal=true; P03_exit_unchanged=true; answer_prompt_equals_export=true
- `runs\E09\run.json` $.commands; L190–253：底层技能调用结束后，自有日志编号逻辑报错
- `runs\E09\lookup-13.txt` L1：Exported 7 files: D:\Temp\combat-extension-nws2d7rg\runs\E09\export

### E09-F7 · receipt_scope · satisfied

P03 凭据覆盖握持/动作顺序、原镜头时段、人物级能力和起止状态；P04 凭据覆盖继承状态与未变结尾。代码把前序 after 累积进 inherited_states，因此 P04 input_digest 变化确有依据。ready 仅验证当前事实/表达与声明哈希匹配；凭据中的语义说明已另行对读，不能因此推得物理正确或视频成功。

- `runs\E09\receipt.json` $.reviews[0].checks; $.reviews[1].checks; L11–14; L24–27：此为文本语义复核，未验证视频
- `candidate\skills\combat-director\scripts\combat_handoff.py` L36–54; L57–70：inherited_states / input_digest / expression_digest
- `reviews\E09-E12\status-revised.draft.plan.json.txt` $[3:5].status：stale
- `reviews\E09-E12\status-revised.plan.json.txt` $[*].status：ready

### E09-F8 · media_effect · indeterminate

没有原视频、复测视频、连续帧或音频；实际握持漂移是否消除、动作是否自然、15秒输出是否满足机位和身份约束均未知。此项不是本次不生成视频的文本任务未完成。

- `runs\E09\answer.md` L1; L10; L16：潜在歧义，不作为已观察到的视频原因 / 不证明视频效果
- `runs\E09\export\review.md` L1–14：未生成、未观看视频；本表不是验收通过证明。
- `runs\E09\export\handoff.md` L3–13：状态：待核验。本工具没有查询平台或提交生成。

未知与边界：

- 用户报告所指的真实帧、遮挡及漂移原因未知。
- 实际复测效果与平台15秒单次生成能力未知。
- 原输入未修改的判断基于当前字节与执行记录哈希一致；没有任务开始前的独立文件系统快照。

## E12 — satisfied

### E12-F1 · text_delivery · satisfied

四段各3秒组成12秒六轨，另有中文可复制提示词；两名成年虚构角色、A 徒手退守、B 木棍压进、正常速度和一个连续镜头均明确。一个镜头满足最多两个镜头，不以相机停下替代人物定格。

- `runs\E12\request.txt` L1：12秒水墨外观的雨中退守 / 只有人物级身体能力 / 最多两个镜头
- `runs\E12\answer.md` L3–5; L21; L31–35：两名成年虚构人物 / A 徒手 / B 双手持一根木棍 / 正常速度，单个连续镜头
- `runs\E12\answer.md` L9–14：人物攻防 | 表演情绪 | 摄影机 | 特效 | 环境反馈 | 声音（设计）

### E12-F2 · appearance_ability · satisfied

水墨通过纸面、淡墨雨丝、衣缘洇染与轮廓表达，接触形状仍清晰。明确排除能量波、大招、分身与墨龙；无断棍、碎柱或爆裂，所有结果来自人物级动作和湿滑支撑变化。

- `runs\E12\answer.md` L11–14; L21; L32–33：水墨表现纸面、雨丝、衣褶与轮廓，不形成攻击实体
- `runs\E12\answer.md` L3–5; L21; L31–35：两名成年虚构人物 / A 徒手 / B 双手持一根木棍 / 正常速度，单个连续镜头

### E12-F3 · terrain_causality · satisfied

湿滑并非背景标签：A 为避扫退步后轻滑，屈膝并重新踩实才续退；B 趁机压进却也在檐口水膜上滑步，被迫缩步稳住。较干平台改变 A 的立足条件；水痕和袖口湿痕留存。

- `runs\E12\answer.md` L5; L12–13; L25–26; L33：后脚在湿阶向外滑半掌 / 屈膝降重心、前脚踩实下一阶止滑
- `runs\E12\answer.md` L11–14; L24–27：B 收肘回抽、试图补步；A 随回抽调整压手守住入口

### E12-F4 · reciprocal_action_prop · satisfied

B 送棍—A 侧避退阶—B 收棍跟进；横扫迫退后两人各有恢复；第二次送棍后 A 侧移并利用 B 缩步时接近。末段 B 仍双手握原木棍并回抽/补步，A 随之调整压手，不是 B 静止等待制伏。A 未夺棍或换为持械。

- `runs\E12\answer.md` L11–14; L24–27：B 收肘回抽、试图补步；A 随回抽调整压手守住入口
- `runs\E12\answer.md` L3–5; L21; L31–35：两名成年虚构人物 / A 徒手 / B 双手持一根木棍 / 正常速度，单个连续镜头

### E12-F5 · space_and_ending · satisfied

南低北高石阶、檐下平台、先行可见的入口右柱与东侧机位贯穿全片。A 沿阶北退，再最后侧移；B 留在南侧湿阶。末段把棍身推柱、压前手腕、前后脚撑稳作为短暂拦阻依据，结尾 A 在檐下、B 未跨入，未补造击倒或超能力胜负。文字层面因果可用，精确近身距离和肢体可达性仍需实际排演/媒体验证。

- `runs\E12\answer.md` L5; L13–16; L26–27; L35：A 在北、B 在南 / A 最后才向入口右柱侧移
- `runs\E12\answer.md` L11–14; L24–27：B 收肘回抽、试图补步；A 随回抽调整压手守住入口
- `runs\E12\answer.md` L14; L27; L35：最后一秒 B 重心退回湿阶，没有迈进檐下；A 不追击

### E12-F6 · observation_boundary · satisfied

声音明确标为设计，交付说明未绑定素材、未提交生成，12秒入口能力待确认。没有把创作指令当作已观察镜头或平台已支持事实。

- `runs\E12\answer.md` L9; L38：声音（设计） / 本稿未绑定素材、未提交生成
- `runs\E12\run.json` $.execution; $.validation：media_generation: false / 无媒体生成或成片验证

### E12-F7 · engineering · indeterminate

本题要求简明六轨与提示词，未要求结构化计划或正式导出。不存在可运行的计划/校验凭证；不把未运行 JSON 校验计为失败，也不声称已通过工程导出门禁。

- `runs\E12\answer.md` L9–14：人物攻防 | 表演情绪 | 摄影机 | 特效 | 环境反馈 | 声音（设计）
- `candidate\skills\combat-director\SKILL.md` L112; L120：无需工程文件的纯提示词任务直接完成创作，不引入 JSON 流程
- `runs\E12\run.json` $.execution; $.validation：media_generation: false / 无媒体生成或成片验证

### E12-F8 · media_effect · indeterminate

未提供成片或音频，水墨观感、正常速度下12秒动作密度、手腕/棍/柱接触清晰度及最终阻拦效果均未实证。

- `runs\E12\answer.md` L9; L38：声音（设计） / 本稿未绑定素材、未提交生成
- `runs\E12\run.json` $.execution; $.validation：media_generation: false / 无媒体生成或成片验证

未知与边界：

- 木棍长度、双方臂长、踏步尺寸与前手腕可达距离未量化；简明创作可用，不构成排演验证。
- 三层石阶的开场具体落脚级未编号，文本有可行连续路径，但实际镜头仍需核对落脚和台阶进度。
- 水墨外观、12秒动作执行与拦阻效果尚无媒体证据；平台入口时长支持未知。

## 执行记录

独立比较结果见 `independent-checks.json`，原始差异见 `diff-output.txt`，只读复跑命令/退出码/stdout/stderr 见 `validation-commands.json`；完整读取清单、SHA-256、范围与工具输出索引见 `run.json`。E09 历史日志包装器的三次失败不混同为当前校验失败；本次检查脚本也曾因 CRLF 匹配失败，修复后重跑，详见记录。
