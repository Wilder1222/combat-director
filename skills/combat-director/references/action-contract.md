# 可选动作契约

只在需要细节编排、重复修订或工程交接时启用。自然语言创作直接使用这些判断方法即可，不要求用户填表。

## 最小可见交手

描述实际兵器的名称、类型与可见特征；说明谁对谁做什么、从哪里经什么路径到哪里、对方如何回应、接触或避让的结果。招式名可以省略，动作过程不能被“激烈交锋”替代。表演和机位服务于这个过程。

能力事件交代发动、维持、消耗或结束。代价要落实成可见反应和后续约束，例如右手失握后松杖，下一动作改由可用的左手完成。非人敌人以部件朝向、回收迟滞、支撑与状态灯表达行动。

## JSON 模式

[Schema](../assets/combat-plan.schema.json) 的可选字段必须成组使用：

- 根 `weapon_profiles`：兵器和关键道具 ID、名称、类型、可见形制、初始归属、held/mounted。密函也可作为需追踪的道具。
- 根 `action_initial_state`：每人 zone、facing、support、held_items.left/right、damage、constraints；另有 environment 锚点状态。
- 每拍 `action_events`：行动者、目标、时间、response_to、weapon_id、hands_used、movement、action、trajectory、contact、outcome、transfers。
- 每拍 `state_delta`：本拍修改的演员字段和环境字段，caused_by 引用本拍事件。

response_to 只能引用已出现且时间不晚于自身的事件。轨迹用起点、路径、终点、画面方向表达，不强制精确坐标。事件可以时间重叠，但必须按起始时间排序；不能用循环回应解释因果。

held_items 中空字符串表示空手；mounted 兵器不占手。临时共同触碰写在 contact，归属转移用 transfers 描述离手与接手。当前转移支持持有人到另一人/另一只手或掉到有名称的落点；尚未建模从地面重新拾取和多人长期共持。需要这些行为时先扩展契约并增加测试，不伪装成既有支持。

ability_use 包含 ability_id、phase、visible_cost、restrictions_added。程序检查归属、先激活后消耗/结束，以及 no_right_hand、no_left_hand、no_running 是否影响后续事件。任意复杂的能力文字、速度、力和距离合理性仍需导演复核。

## 状态只有一个来源

启用结构化动作时，initial_state、before、after 是结构化状态的文字投影，由 `combat_action.state_text` 生成；校验器拒绝不一致的手写副本。原三例仍使用自由文本状态，迁移不会猜测它们的空间结构。

每个状态变化需要本拍事件解释；持物变化还需要 transfers 与 held_items 一致。损伤和代价不能无声重置。当前不模拟恢复/治疗，不推断“轻伤会自动恢复”；需要解除约束时另行设计有证据的规则。

最终提示词的“具体交手”由事件直接编译，包含兵器特点、轨迹、回应、接触、结果和状态变化；事件 ID 和完整来源保留在 prompt-handoff.json，投喂文本以画面语言表达。

## 可运行案例

| 案例 | 要观察的机制 |
| --- | --- |
| [窄巷取函](../examples/alley-letter-15.plan.json) / [提示词](../examples/alley-letter-15.prompt.txt) | 木杖与衣袖接触、B右手到A左手的密函转移、双方退出 |
| [三人护送](../examples/three-person-exit-18.plan.json) / [提示词](../examples/three-person-exit-18.prompt.txt) | C从既有出口进入画外，状态仍存在，A/B交手不让C瞬移 |
| [反制失败后修订](../examples/failed-counter-repair-18.plan.json) / [提示词](../examples/failed-counter-repair-18.prompt.txt) | 货架卡住、屏障结束与右手失握、后续改用左手按钮 |

这些是原创教学设计，没有生成视频；不能用其通过结构校验来声称动作效果已验证。
