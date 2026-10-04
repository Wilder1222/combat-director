# Combat Plan 1.2：事实、表达与复核

权威结构：[当前 Schema](../assets/combat-plan.schema.json)。[1.0 Schema](../assets/combat-plan-v1.schema.json) 只供迁移与结构检查。软件版本和数据契约版本分别维护；文本创作不强制填写 JSON。

当前兼容读取 1.1，1.2 增加可选动作结构与素材证据。旧计划不被强制补写未知动作事实；1.0 必须显式迁移并重新复核。已标 available/bound 的旧素材声明需补证据，不能仅迁移版本号后当作已验证。

软件0.10.0新增可选 `combat-prompt/1` 表达文件，独立于本契约，不给 Combat Plan 添加字段。原完整导出保持不变；精简导出将已审导演事实映射为另外复核的连贯正文，事实/正文变更都会使相应复核失效。字段与命令见[逐镜表达](contract.md#逐镜详细表达与兼容投影)。下表的 prompt 硬约束/具体交手栏目指完整模式；精简模式需逐项保留其含义，由复核者对读，脚本不自动证明语义完整。

## 字段职责与交接

| 字段 | 权威角色 | 交付位置 |
| --- | --- | --- |
| duration / aspect_ratio / generation / camera_mode / timing / rules | 时间、镜头和能力的硬约束 | prompt 硬约束、设计卡、交接单 |
| cast / abilities / anchors / initial_state | 人物、持物、能力和开场事实 | prompt 硬约束、导演稿、编译交接 |
| beats | 动作、表演、机位、声音与状态事实 | director.md、prompt-handoff.json |
| weapon_profiles / action_initial_state / action_events / state_delta | 可选具体交手；启用时为动作状态的唯一权威 | prompt 具体交手、投影状态、编译交接；见[动作契约](contract.md#可选动作结构) |
| sections.beat_ids | 投喂段选取的连续细拍 | 导出时间范围与交接记录 |
| headers / sections.summary | 人工或 Agent 编写的表达 | prompt.txt；需要语义复核 |
| editorial_reviews | 对特定输入和表达版本的复核声明 | 计划与状态检查；不是视频验收 |
| id / provenance | 文件身份与来源说明 | 计划和设计卡；不参与语义摘要哈希 |

新编写的完整提示词按[生成模板](prompt-construction.md)在每段分镜内部按需求选择中文类型标签并详细描述。使用详细工程导出时，逐镜正文写入既有表达文件sections[].text；opening承载独立公共模块，集中写全场稳定设定；各镜直接继承，只补当前状态、事件与变化，不重复公共内容。人物、兵器、能力和事件仍以事实计划为准，先核对各段beat_ids对应的来路、回应、结果再选择相关项展开；创作新增事实时先同步计划再复核，不只往文字里补写。按需选项不增加Combat Plan字段，不让旧计划补造未知事实；detailed检查标签结构与已有复核绑定，语义完整性仍由作者及审阅者逐镜核对。

每拍记录全部角色的动作与表演。before 继承上一拍 after，包括角色、environment、camera_side。第一拍 transition=start；之后 continuous 保持 shot_id，cut 改变 shot_id。一镜到底全程一个 shot_id，越轴需要可见过渡。状态文字相等不证明物理成立。

## 修订流程

改动事实或表达后，先检查状态，再编译供复核的内容：

```bash
python scripts/combat_tool.py status my.plan.json
python scripts/combat_tool.py compile my.plan.json --out review-input.json
```

review-input.json 按 headers 和各主段提供 facts、expression、input_digest、expression_digest。独立比较两者，修正遗漏或矛盾，再编译。重点是身份/动作、镜头/时间、能力/代价、连续性；不能只看标签齐全。

将实际复核结论保存为 receipt JSON。每条必须复制所检查版本的两个 digest，并用具体证据填写四项 checks：

```json
{
  "plan_id": "your-plan-id",
  "reviews": [{
    "scope": "P01",
    "input_digest": "从review-input中复制的64位哈希",
    "expression_digest": "从review-input中复制的64位哈希",
    "reviewer": "实际复核者名称",
    "method": "agent",
    "checks": {
      "identity_action": "说明该段兵器、动作和回应与细拍如何一致",
      "camera_timing": "说明该段时间与镜头规则如何对应",
      "ability_cost": "说明能力限制/代价的表达；无能力时说明不适用",
      "continuity": "说明起止状态与相邻段的关系"
    }
  }]
}
```

示意哈希不可直接执行。method 可选 human 或 agent。receipt 可只包含重新检查的 scope；其余旧记录保持，但不能绕过已失效的检查。

```bash
python scripts/combat_tool.py apply-review my.plan.json --receipt receipt.json --out reviewed.plan.json
python scripts/combat_tool.py validate reviewed.plan.json
python scripts/combat_tool.py render reviewed.plan.json --platform generic --out-dir output/check
```

ready 仅表示复核声明对应当前事实和表达。stale 表示内容已变化；needs_semantic_review 表示没有复核声明。后两者阻止正式导出。不要为通过导出而只刷新哈希：程序无法判断复核者是否认真读过内容。

全局人物/能力/时间变更影响所有段；某段动作或摘要变化影响本段；前序结束状态和能力变化也影响后续段；最终状态变化会使总设定复核失效。哈希对 JSON 对象键顺序、数字 1/1.0、文本首尾空白和行尾差异归一化，保留正文内部语义差异。

## 旧计划与文件保护

```bash
python scripts/combat_tool.py migrate old-1.0.plan.json --out migrated.plan.json
```

迁移保留事实和表达，新增空的复核记录；不自动确认旧摘要正确。compile、migrate、apply-review 默认拒绝已有输出、链接路径及源文件覆盖。render 导出 7 份：design-card.md、director.md、prompt.txt、prompt-handoff.json、handoff.md、review.md、combat-plan.json。只有 render 提供显式 --force。

validate 和 render 接受 --max-duration 15；确认平台上限为15秒时，30秒单次计划失败，不自动拆分。可选 --profile 文件用于离线工程能力检查，不作为提示词写作的前置条件。审片记录与下一段起点见[审片回流](review-loop.md)。

校验器审计随包 Schema 的关键字；未知断言明确失败，不静默忽略。它是标准库实现的有限子集，并额外拒绝要求非空的纯空白字符串，不是通用 JSON Schema 引擎。结构、引用与复核版本可由代码检查，表达忠实性仍由复核者负责。

## 可选动作结构

启用时，以根层`weapon_profiles`和`action_initial_state`定义兵器及初始状态，并在每个beat中同时填写`action_events`与`state_delta`。仅写文本的旧计划不必补造未知事实。

- 兵器档案记录ID、名称、形制与持用方式。角色初始状态记录zone、facing、support、左右手持物、damage和constraints，另记录environment。空字符串表示空手；mounted物品不占手。
- 事件记录actor_id、target_id、start/end、response_to、weapon_id、hands_used、movement、action、trajectory、contact、outcome和必要transfers。事件按开始时间排序，可重叠；response_to引用更早事件且不能成环。
- 临时接触不等于持物转移。transfers支持现持有人向另一角色/另一只手转移或丢到命名位置；当前结构不支持从地上捡回、多人长期共持，不自行发明字段来绕过。
- 能力使用按owner及activate/consume/end核对；代码支持no_right_hand、no_left_hand、no_running等明确约束，不是任意物理模拟。损伤、限制和兵器去向不能无因恢复。

启用动作结构后，状态投影由`combat_action.state_text`生成，手写状态与投影漂移会失败；它不是第二套可独立修改的事实。编译交接保留事件ID与具体动作，Schema通过仍不证明距离、接触或生物力学正确。

## 逐镜详细表达与兼容投影

需要机器导出逐镜分类正文时，使用既有`combat-prompt/1`表达文件和`--prompt-style detailed`；普通自然语言创作无需此流程。作者在每个sections[].text中按生成模板填写该镜所需标签及详细内容，标签数量与顺序不固定，opening中的公共设定无需逐镜复写，但镜内必要事件和变化不能省略。每个section对应一个实际分镜或一镜到底的时间节拍；需细分镜头时先同步计划段落。Combat Plan 1.2不增加字段。原full/compact仅保留旧工程兼容，不作为当前逐镜分类写作格式。

```bash
python scripts/combat_prompt.py prepare your-plan.json --out draft.json
python scripts/combat_prompt.py compile your-plan.json draft.json --out inspection.json
python scripts/combat_prompt.py apply-review your-plan.json draft.json --receipt receipt.json --out reviewed.json
python scripts/combat_tool.py render your-plan.json --prompt-style detailed --prompt-file reviewed.json --out-dir output/detailed
```

作者将独立公共模块写入opening，逐镜内容写入sections[].text，收尾写入closing；detailed保持公共模块在全部分镜之前，只输出一次，不向各镜自动复制；detailed导出逐段检查是否有中文类型标签、重复标签与空内容，不要求25项齐全或固定顺序，生成段内标签及镜长，只输出正文、表达文件和事实计划三份文件，不产生平台交接单。格式检查不判定内容质量；作者仍须逐镜对读。编译后对读正文与事实，再写复核凭据。凭据包括plan_id、source_digest、expression_digest、reviewer、method（human或agent），以及event_coverage、scene_camera、identity_ability、rhythm、constraints五项checks的具体依据。脚本检查表达文件结构、标签非重复、非空与摘要匹配，不自动证明语义完整。

事实变更使投影失效，正文变更使其复核失效；重分段应先改计划，再重新检查。旧compact导出8份文件，比旧full导出增加prompt-projection.json；不得用压缩省略关键交手、空间桥接与结尾兑现。

## 结构化审片与续作

仅在已有计划且需要可追溯审片记录时使用。如何观察媒体与区分失败原因见[审片](review-loop.md)。

```bash
python scripts/combat_tool.py review-template my.plan.json --take-id take-001 --out take-001.review.json
python scripts/combat_tool.py review-take take-001.review.json --plan my.plan.json
python scripts/combat_tool.py continuation-seed take-001.review.json --plan my.plan.json --out next-start.json
python scripts/combat_tool.py check-continuation take-001.review.json --plan my.plan.json --next-plan next.plan.json
```

模板初始为未观察、pending及未知状态。记录绑定计划哈希，填写真实媒体位置/身份/哈希与证据类型actual_media、user_report或synthetic。脚本不会播放视频；实际完整播放才可声明full_video，抽帧只支持采样点，audio_observed要求实际聆听，不能由截图、用户转述或工程夹具推出。

completed_events/incomplete_events必须引用现有beat/event且互斥；意外事件另记，偏差包括时间、观察、影响和修复建议。验收决定由用户或已授权的自动选择作出，校验器不能代替验收：

| 决定 | 含义 |
| --- | --- |
| pending | 尚未选择，不建立续作 |
| accept | 无已知偏差或未完成事件 |
| accept_with_deviation | 明确接受并解释偏差 |
| repair / reject | 修复或弃用，不作为已接受续作起点 |

只有接受的take可输出续作起点；以observed_end_state继承实际持物、位置、损伤和环境，与下一计划initial_state一致。未知状态保留未知或声明假设，不用原计划终态冒充观察。结构化动作投影也须一致；字段细节以随包Schema和CLI帮助为准，不新增工具不支持的元数据。
