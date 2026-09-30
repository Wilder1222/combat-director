# Combat Plan 1.2：事实、表达与复核

权威结构：[当前 Schema](../assets/combat-plan.schema.json)。[1.0 Schema](../assets/combat-plan-v1.schema.json) 只供迁移与结构检查。软件版本和数据契约版本分别维护；文本创作不强制填写 JSON。

当前兼容读取 1.1，1.2 增加可选动作结构与素材证据。旧案例不被强制补写未知动作事实；1.0 必须显式迁移并重新复核。已标 available/bound 的旧素材声明需补证据，不能仅迁移版本号后当作已验证。

软件0.10.0新增可选 `combat-prompt/1` 表达文件，独立于本契约，不给 Combat Plan 添加字段。原完整导出保持不变；精简导出将已审导演事实映射为另外复核的连贯正文，事实/正文变更都会使相应复核失效。字段与命令见[精简输出](compact-output.md)。下表的 prompt 硬约束/具体交手栏目指完整模式；精简模式需逐项保留其含义，由复核者对读，脚本不自动证明语义完整。

## 字段职责与交接

| 字段 | 权威角色 | 交付位置 |
| --- | --- | --- |
| duration / aspect_ratio / generation / camera_mode / timing / rules | 时间、镜头和能力的硬约束 | prompt 硬约束、设计卡、交接单 |
| cast / abilities / anchors / initial_state | 人物、持物、能力和开场事实 | prompt 硬约束、导演稿、编译交接 |
| beats | 动作、表演、机位、声音与状态事实 | director.md、prompt-handoff.json |
| weapon_profiles / action_initial_state / action_events / state_delta | 可选具体交手；启用时为动作状态的唯一权威 | prompt 具体交手、投影状态、编译交接；见[动作契约](action-contract.md) |
| sections.beat_ids | 投喂段选取的连续细拍 | 导出时间范围与交接记录 |
| headers / sections.summary | 人工或 Agent 编写的表达 | prompt.txt；需要语义复核 |
| editorial_reviews | 对特定输入和表达版本的复核声明 | 计划与状态检查；不是视频验收 |
| id / provenance | 文件身份与来源说明 | 计划和设计卡；不参与语义摘要哈希 |

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

validate 和 render 接受 --max-duration 15；确认平台上限为15秒时，30秒单次计划失败，不自动拆分。内置平台模式保持未知；可使用带证据的 --profile 文件进行能力冲突检查，见[平台交接](platforms.md)。审片记录与下一段起点见[审片回流](review-loop.md)。

校验器审计随包 Schema 的关键字；未知断言明确失败，不静默忽略。它是标准库实现的有限子集，并额外拒绝要求非空的纯空白字符串，不是通用 JSON Schema 引擎。结构、引用与复核版本可由代码检查，表达忠实性仍由复核者负责。
