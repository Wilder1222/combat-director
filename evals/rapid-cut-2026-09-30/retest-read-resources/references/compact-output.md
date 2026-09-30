# 精简正文与导演事实分开

默认创作交付采用“总设定 + 按时间段的可见事件 + 必要连续性约束”。六轨用于内部检查，只有用户要导演细稿时才完整呈现。不要固定字数、每秒动作数或三镜模板；一个长回合可能比三个孤立招式更清楚。

用户明确要求[短镜爆剪](rapid-cut-continuity.md)时执行其三镜链与约44镜目标，不被一般精简建议覆盖。总设定写清轴线、B左A右、镜长区间和两处微慢镜；主段保留镜号范围、各攻击的来路→命中点Hit Stop→反馈及受力方向、每3—5秒的复位时点、实际换边过程和遮挡前后运动接续。段数不是镜数，压缩不能把已分镜的动作重新描述成一镜到底。

强化节奏时，主段仍体现前段提密、中段成簇爆点和终局逐层兑现：写明上一击反馈怎样接下一击、各爆点改变什么、硬切落在哪个动作相位。复位保留“双方左右/间距/地标/下一击路线”的具体句子，不压成一句“切高位复位”；删重复蓄势，不删关键接触和受力结果。

将“可复制正文”单独拿出复核：不能依赖“按上表执行”“沿用上述设定”或只在导演表解释的攻击ID。正文必须自含人物/兵器、空间约束、关键动作与接触、复位和速度例外。若精确逐镜要求必须连同镜头表才能执行，就把表纳入同一可复制交付块，并明确复制范围；不要将依赖外部表格的摘要标为独立完整提示词。正文镜数、时间和节奏统计来自最终逐镜表，不另写一份猜测配额。

## 保留什么

每段仍需明确攻击者与兵器、起点与路径、对手回应、接触/避让结果、必要回握/落脚、环境变化如何影响下一步，以及拍到这些事的镜头。能力预算、持械手、尺度、光线和结束状态不能因压缩丢失。总设定只写一次稳定身份，段内优先事件，不逐次重复皮肤、衣料、眉眼与八轨标题。

投喂顺序为场景状态 → 动作因果 → 镜头覆盖 → 连贯正文。精简是表达投影，不是新增招式、改变胜负或伪造已绑定素材。先锁定事件再对照压缩前后：谁先动、对方为何动、位置和武器最后在哪里、大场面如何建立尺度。缺少关键事实时回到导演层修订。

## 可选工程路径

纯文本任务不强制 JSON。已有工程计划时，旧 `combat_tool.py render` 默认保留完整八标签格式，保证已有产物兼容；新 `--prompt-style compact --prompt-file ...` 使用单独的 `combat-prompt/1` 表达文件。平台选择只改变交接清单，不声称存在已实测的模型专属语法。

在技能目录执行：

```bash
python scripts/combat_prompt.py prepare examples/grounded-15.plan.json --out draft.json
# 作者填写 opening、sections[].text 和 closing；不要自动填复核通过。
python scripts/combat_prompt.py compile examples/grounded-15.plan.json draft.json --out inspection.json
# 逐段对读 inspection 中的 source 与 expression，另写 receipt.json。
python scripts/combat_prompt.py apply-review examples/grounded-15.plan.json draft.json --receipt receipt.json --out reviewed.json
python scripts/combat_tool.py render examples/grounded-15.plan.json --prompt-style compact --prompt-file reviewed.json --out-dir output/compact
```

receipt 必须含 plan_id、source_digest、expression_digest（从 inspection 取得）、reviewer、method（human/agent），以及 checks：event_coverage、scene_camera、identity_ability、rhythm、constraints。每项写实际对读依据，不是布尔值。脚本检查字段、段序、内容非空、来源及表达哈希；不会自动判断一句话是否真的覆盖事件。

表达文件不改变 Combat Plan 1.2。原计划仍须通过既有导演层复核；精简表达另外复核。计划的动作、环境、光线描述、镜头、能力、参考或摘要改变后，旧投影失效；正文改变后旧复核失效。重新对读再写新回执，不能机械更新哈希冒充复核。投喂段数跟随原计划，要重新分段先改计划并复核。

精简模式输出八份文件，新增 prompt-projection.json 留存表达与复核；完整模式仍输出原七份。没有视频时，只能报告文本与结构检查结果，不能报告生成效果提升。
