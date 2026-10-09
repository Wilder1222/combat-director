# Combat Plan 1.3：事实、表达与复核

权威结构：[当前 Schema](../assets/combat-plan.schema.json)。[1.0 Schema](../assets/combat-plan-v1.schema.json) 只供迁移与结构检查。软件版本和数据契约版本分别维护；文本创作不强制填写 JSON。

当前兼容读取 1.1/1.2；1.2 的动作与素材结构继续按原语义检查。1.3 新增可选 combat-action-state/2，只在工程需要追踪物件、身体实例、接点、效应或跨段事件时启用。旧计划不被强制补写未知动作事实；1.0 必须显式迁移并重新复核。已标 available/bound 的旧素材声明需补证据，不能仅迁移版本号后当作已验证。

软件0.10.0新增可选 `combat-prompt/1` 表达文件，独立于本契约，不给 Combat Plan 添加字段。原完整导出保持不变；精简导出将已审导演事实映射为另外复核的连贯正文，事实/正文变更都会使相应复核失效。字段与命令见[逐镜表达](contract.md#逐镜详细表达与兼容投影)。下表的 prompt 硬约束/具体交手栏目指完整模式；精简模式需逐项保留其含义，由复核者对读，脚本不自动证明语义完整。

## 字段职责与交接

| 字段 | 权威角色 | 交付位置 |
| --- | --- | --- |
| duration / aspect_ratio / generation / camera_mode / timing / rules | 时间、镜头和能力的硬约束 | prompt 硬约束、设计卡、交接单 |
| cast / abilities / anchors / initial_state | 人物、持物、能力和开场事实 | prompt 硬约束、导演稿、编译交接 |
| beats | 动作、表演、机位、声音与状态事实 | director.md、prompt-handoff.json |
| weapon_profiles / action_initial_state / action_events / state_delta | 可选具体交手；启用时为动作状态的唯一权威 | prompt 具体交手、投影状态、编译交接；见[动作契约](contract.md#可选动作结构) |
| body_profiles / action_initial_state 内扩展状态 / action_events.state_ops | 1.3 可选身体实例、持握与遥控、成对接点、在途攻击、阵法及未完事件 | 同一状态的投影、事件交接和复核摘要；见[扩展状态](contract.md#仙侠与多人扩展状态) |
| sections.beat_ids | 投喂段选取的连续细拍 | 导出时间范围与交接记录 |
| headers / sections.summary | 人工或 Agent 编写的表达 | prompt.txt；需要语义复核 |
| editorial_reviews | 对特定输入和表达版本的复核声明 | 计划与状态检查；不是视频验收 |
| id / provenance | 文件身份与来源说明 | 计划和设计卡；不参与语义摘要哈希 |

新编写的完整提示词按[生成模板](prompt-construction.md)在每段分镜内部按需求选择中文类型标签并详细描述。使用详细工程导出时，逐镜正文写入既有表达文件sections[].text；opening承载独立公共模块，集中写全场稳定设定；各镜直接继承，只补当前状态、事件与变化，不重复公共内容。人物、兵器、能力和事件仍以事实计划为准，先核对各段beat_ids对应的来路、回应、结果再选择相关项展开；创作新增事实时先同步计划再复核，不只往文字里补写。按需选项不增加Combat Plan字段，不让旧计划补造未知事实；detailed检查标签结构与已有复核绑定，语义完整性仍由作者及审阅者逐镜核对。

每拍记录全部角色的动作与表演。before 继承上一拍 after，包括角色、environment、camera_side。第一拍 transition=start；之后 continuous 保持 shot_id，cut 改变 shot_id。一镜到底全程一个 shot_id，越轴需要可见过渡。状态文字相等不证明物理成立。

逐切口正文对读按[相邻镜接续](camera-and-rhythm.md#相邻镜接续)，复用这些事实以及已有轨迹、接点、未完事件，不新增必填字段。`axis_bridge`非空只证明提供了越轴说明，`trajectory`中的方向/路径是文字声明；程序不计算世界方位、投影方向、射程或惯性。作者/审阅者要将切前末相位与切后起相位、地标、持物和动势对应到实际表达，工程通过不能替代动作匹配或媒体观察。

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
python scripts/combat_tool.py migrate old.plan.json --target-version 1.3 --out migrated.plan.json
```

迁移接受 1.0/1.1/1.2，保留事实和表达、清空复核记录；不自动确认旧摘要正确，不把旧动作状态转换成未知扩展事实，也不从计划制造实际观察。1.0/1.1 可显式选择 1.2 兼容目标；当前版本不重复迁移。compile、migrate、apply-review 默认拒绝已有输出、链接路径及源文件覆盖。render 导出 7 份：design-card.md、director.md、prompt.txt、prompt-handoff.json、handoff.md、review.md、combat-plan.json。只有 render 提供显式 --force。

validate 和 render 接受 --max-duration 15；确认平台上限为15秒时，30秒单次计划失败，不自动拆分。可选 --profile 文件用于离线工程能力检查，不作为提示词写作的前置条件。审片记录与下一段起点见[审片回流](review-loop.md)。

校验器审计随包 Schema 的关键字；未知断言明确失败，不静默忽略。它是标准库实现的有限子集，并额外拒绝要求非空的纯空白字符串，不是通用 JSON Schema 引擎。结构、引用与复核版本可由代码检查，表达忠实性仍由复核者负责。

## 可选动作结构

启用时，以根层`weapon_profiles`和`action_initial_state`定义兵器及初始状态，并在每个beat中同时填写`action_events`与`state_delta`。仅写文本的旧计划不必补造未知事实。

- 兵器档案记录ID、名称、形制与持用方式。角色初始状态记录zone、facing、support、左右手持物、damage和constraints，另记录environment。空字符串表示空手；mounted物品不占手。
- 事件记录actor_id、target_id、start/end、response_to、weapon_id、hands_used、movement、action、trajectory、contact、outcome和必要transfers。事件按开始时间排序，可重叠；response_to引用更早事件且不能成环。
- 临时接触不等于持物转移。旧动作结构的 transfers 支持现持有人向另一角色/另一只手转移或丢到命名位置；地面拾取、共持与遥控分离需要显式启用下方扩展状态，不往旧结构添加未实现字段。
- 能力使用按owner及activate/consume/end核对；代码支持no_right_hand、no_left_hand、no_running等明确约束，不是任意物理模拟。损伤、限制和兵器去向不能无因恢复。

启用动作结构后，状态投影由`combat_action.state_text`生成，手写状态与投影漂移会失败；它不是第二套可独立修改的事实。编译交接保留事件ID与具体动作，Schema通过仍不证明距离、接触或生物力学正确。

## 仙侠与多人扩展状态

仅在 Combat Plan 1.3 的 `action_initial_state.format="combat-action-state/2"` 下使用；可选 `body_profiles` 定义每具身体的稳定 ID、所属 cast 身份、original/clone/illusion/trail、能否实体交互及生成来源。不填 body_profiles 时，每个 cast ID 就是一具原始身体。出现同貌分身时明确各具 ID，不用屏幕左右当身份；全部身体在 actors 中以 active/inactive/exited 保留生命周期，未生成实例可以 inactive，退场实例不能用原 ID 无因复活。

| 状态 | 唯一事实与约束 |
| --- | --- |
| actors | 每具身体的位置、朝向、支撑、损伤、限制和生命周期；不存 held_items，cast 文本由身体聚合投影 |
| items | 每件 weapon_profiles 物件的 holders、自由位置、controller_id、control_mode、控制能力与依据、实体状态；同一物件可有多只持握手；默认每手一物，已设兼持由 hand_exceptions 明确限定身体、手、物件与来源 |
| contacts | 每条连接恰有两个身体/部位/物件端点、受限手、维持机制和释放条件；多接点逐条释放，结束一条不清空另一条 |
| effects | 投射、持续、遥控或自主效果的来源、实际控制者、依赖、位置/路径、在途阶段、下一威胁和中断处置；occupied_hands 可记录连续维持所占的手 |
| formations | 来源、附着 world/body/item/anchor、位置或相对偏移、朝向、形状、范围、功能、维持、阶段和局部节点；partial 保留完好与破坏节点 |
| pending_events | 未完事件的稳定 ID、原事件、参与者、既有路径/接点和下一威胁；下一段通过 continues 引用，完成时显式更新为 completed |
| hand_exceptions | 同一状态内的兼持/分指许可：body_id、hand、item_ids、grip/ability、能力、allows_casting、phase、basis；不全局解除占用 |
| active_abilities | ability_id + body_id 的发动实例；同身份的两个身体可以分别维持同一能力，结束本体不自动清除分身的发动 |

items.holders 为持握唯一权威，不再另写身体 held_items。持握不自动取得遥控：remote 的控制者、能力归属、该身体当前 active 发动和控制依据必须有效；autonomous 另声明能力和依据，不占施术手。无持握时保留实际位置，拾取操作的 from_location 必须等于原位置；退场先处理真实物件及连接，不让它们随身体自动消失。实体飞剑 effects.item_id 与同件 items 的自由位置一致，剑气不占原实体。

每个事件保留原有来路、回应、接触、结果，扩展操作写进 `state_ops`，字段为 domain、id、operation（create/update/end）、value 和可见 reason；具体 value 按随包 Schema 的 body_state/item_state/contact_state/effect_state/formation_state/pending_state 填写。拾取另填 from_location。body 操作只改生命周期，位移、损伤与持久代价仍写 state_delta；items/contact/effect/formation/pending 不在 state_delta 再存一份。扩展事件的 transfers 必须为空。每个操作必须引用已声明实体或明确新建连接/效果/未完事件；终止实例保留终态，不能复用 ID 偷换实体。

操作在 event.end 原子生效；按成片时间回放，同刻先处理结束再处理新事件开始。不同手、不同身体可并发；相同手或兵器的重叠使用需共享 concurrency.group 和同一 basis，说明既定的兼持、分指或同次复合动作机制。相同时间对同一实体的两个操作失败，合并为一次权威变更。contact_ids 可以明确持续使用的接点；受控手不能忽略仍有效接点直接独立挥动。维持 effects.occupied_hands 的手需明确续用、改维持或解除；自主效果可以不占手。程序核对声明关系，不能确认这些机制在画面或物理上成立。

effects/formations 的 dependencies 使用 `ability:ID@BODY`、`body:ID`、`effect:ID`、`formation:ID`、`contact:ID`。供能、控制或接点失效时，由同次操作给出依赖对象的实际去处：end/fall/freeze 分别落为 ended/falling/frozen；persist 可保留已脱离发射源的在途对象。停止发射不清除无依赖的余箭。依赖中断后仍保持旧依赖会失败，不以自动补写消散代替作者指定的机制。阵法随动由 attachment 关系表示，位置相对附着对象；orientation、范围和局部失效仍分别记录，校验器不计算空间变换或传播物理。

兼持用 hand_exceptions 明确列出同一身体/手允许的 item_ids；不填例外仍拒绝一手两件。kind=grip 记录已设机械握持，ability_id 为空；kind=ability 必须引用所属身份的能力及该身体当前 active 发动。allows_casting 仅允许指定手在指定持物范围内分指维持/施术；当手已持物时，新 activate/sustain 等 ability_use 也要检查该许可，不只检查已有 effect 的维持。机械兼持且 allows_casting=false 不能因此施术；空手按正常施术条件处理，其他手或物件的限制仍保留；纯施术例外可用空 item_ids，但必须明确 allows_casting。例外通过 hand_exception 的 state_ops 建立、修改或结束，结束能力时同步处理依赖该能力的许可与持物；不是另写手部持物状态。

每个状态转换后重新核对仍在运行的事件，而非只验起点。途中新束缚、兵器易手、控制结束或身体退场，必须保留已有允许的维持关系，或由造成中断的事件以 interrupts（event_id、reason）显式停止原事件，再从新状态安排下一事件。中断只取消该事件尚未执行的预定结束操作，不清除已发出的自持效果；中文动作投影直接读取同一回放的生效 interrupted_events，标出实际中断时间及未完成的原拟结果；中断者自身提前被打断时，其原拟中断不生效。不会从全部计划 interrupts 另猜结果，也不把未来回收、代价或转移当作已发生。不同身体/手的重叠及已声明兼容的共同动作继续允许。

同一接点 ID 固定身体和物件身份；同对象部位滑动可 update，换参与者或物件先结束旧 pair 再 create 新 ID。pending 的 source_event_id、actor_id、target_id 不变，completed 不可复活；完成无论用 update/end 都须 continues 指向该 ID。continues + ongoing 保留原始来源，可连续跨过多个片段，不改写为当前镜头的事件 ID。

能力触发与事件的兵器操作分开判断。1.3 扩展状态可在 abilities[] 填 trigger_spec：kind=held-item、source_item_id 指定“用当前持握手操作源器物本身”；kind=independent、source_item_id 为空表示独立施术。held-item 要求事件选择同一 weapon_id、held 方式，能力归属与执行身体一致，hands_used 中每只手当前实际持有该源物件；它不借 supernatural=false 豁免任何其他物件、其他手或接点限制。独立施术仍按有无持物及 allows_casting 核对，即使能力非超自然也不能越过许可。明确的器物引法可以是超自然能力，决定条件是结构化触发来源和实际持握关系。

旧未填写 trigger_spec 的记录继续读取：只有“非超自然 + 选中当前同源 held 实体 + 声明手各只持这一件物品”采用普通器物操作的兼容解释；其余走独立施术检查，不解析 trigger/action 自由文本关键词。新计划应显式写 trigger_spec；机械兼持多件本身不授权施术，也不自动判定哪一件提供能力。trigger_spec 仅在 1.3 combat-action-state/2 使用，旧结构不强补该字段。实际生效的触发类型与兼容依据记录在同一回放的 effective_ability_triggers，并进入可读动作投影；声明改变会使原事实复核失效。

全计划先检查每个 state_ops.value 的域 Schema 及人物、物件、能力、依赖和事件 ID 的声明引用，包括后来被取消的回调；未知字段和 NOT_DECLARED 等引用不能借取消绕过。再按实际回放核对持有、active、接点当前阶段与生命周期；取消回调不执行这些动态前置，不能因其原拟 end 能力尚未 active 就制造一次实际失败。

新状态、操作、身体档案全部进入事实复核摘要；前序 state_ops/state_delta 进入后续段依赖，变化使相关复核失效。state_text 从同一状态生成 initial_state/before/after；工程编译与结构投影不成为第二事实源，不证明原速、碰撞、数量可读性或画面质量。完整模式可导出操作的中文说明；逐镜表达仍由作者对读已编译事实后独立复核。

## 逐镜详细表达与兼容投影

需要机器导出逐镜分类正文时，使用既有`combat-prompt/1`表达文件和`--prompt-style detailed`；普通自然语言创作无需此流程。作者在每个sections[].text中按生成模板填写该镜所需标签及详细内容，标签数量与顺序不固定，opening中的公共设定无需逐镜复写，但镜内必要事件和变化不能省略。每个section对应一个实际分镜或一镜到底的时间节拍；需细分镜头时先同步计划段落。逐镜正文使用既有表达文件，1.3 的扩展状态也不另造正文事实字段。原full/compact仅保留旧工程兼容，不作为当前逐镜分类写作格式。

```bash
python scripts/combat_prompt.py prepare your-plan.json --out draft.json
python scripts/combat_prompt.py compile your-plan.json draft.json --out inspection.json
python scripts/combat_prompt.py apply-review your-plan.json draft.json --receipt receipt.json --out reviewed.json
python scripts/combat_tool.py render your-plan.json --prompt-style detailed --prompt-file reviewed.json --out-dir output/detailed
```

作者将独立全局设定写入opening，逐镜内容写入sections[].text，收尾写入closing；detailed保持全局设定在全部分镜之前，只输出一次。逐镜支持合并栏目【画面与动作】【摄影】【衔接】【声音】，也兼容原25项细项；两者按需取用，不要求固定数量或顺序，程序不自动改写已审正文。多镜导出标各镜镜长；one-take先标全镜时长，sections仅标镜内节拍，不能把每段显示成一次切镜。输出仍是正文、表达文件和事实计划三份文件，不产生平台交接单。

格式检查只核对逐段标签合法、非重复、内容非空和复核绑定，不判定创作质量或自动拆分独立生成请求；分段方案依生成模板编写，不改变section的镜头/节拍含义。编译后对读正文与事实，再写复核凭据。凭据包括plan_id、source_digest、expression_digest、reviewer、method（human或agent），以及event_coverage、scene_camera、identity_ability、rhythm、constraints五项checks的具体依据。事实与正文摘要匹配仍不等于语义完整或媒体通过。

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


扩展状态计划使用 combat-take-review/2 模板，observed_action_state 初始为 null（未知），action_state_evidence 为空。只有实际观察或保持来源标签的用户/合成报告才填写结构状态；observed_end_state 必须由该观察状态投影，不能分别手改两份起态。只有已经接受的记录输出 combat-continuation/2，携带实际身体身份、物件、未释放接点、仍在途效果、阵法及 pending_events。下一结构计划的 action_initial_state 和身体绑定必须与观察相同；null 不会由原计划终态补全。未知状态可以作为普通文字接续继续记录；要进入完整结构检查，先取得缺失观察，而不是用旧计划伪造已知。
