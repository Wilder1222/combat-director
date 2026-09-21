# Combat Plan 1.0

本项目新建的数据契约，非附件中未提供的原 Schema。与 CineWeave 等工具组合时只交换文件，接入方自行确认字段映射；不假定私有 API。

权威结构：[combat-plan.schema.json](../assets/combat-plan.schema.json)。三个完整计划位于 [母版索引](templates.md)。所有数字是有限 JSON number，布尔值不能充当时长。

| 字段 | 含义 |
| --- | --- |
| schema_version / id / provenance | 契约版本、唯一方案标识、原件与重建说明 |
| template / duration / aspect_ratio | 母版、包含入出点的总时长、画幅 |
| generation / camera_mode | 本版只接受 single；one-take 或 multi-shot |
| headers | 可复制提示词的目标、身份、场景、预算、全程连续性文字 |
| rules / abilities | 幻想许可、能力尺度；每项技能的归属、触发、限制、代价、结束条件 |
| timing | lead_in、tail_out、result_at；结果不得晚于 duration - tail_out |
| cast / anchors / references | 人物目的与持物、空间锚点、素材控制/排除范围与绑定证据 |
| initial_state | 各角色、environment、camera_side 的初始状态 |
| beats | 顺序细拍；起止时间、双方攻防表演、情绪、机位、效果、环境、声音、技能和前后状态 |
| sections | 按顺序无重无漏的 beat_ids，加人工维护的八标签投喂摘要 |

状态值是简洁中文文字：位置、朝向、支撑、持物和损伤要表达清楚。下一拍 before 必须与前拍 after 相等。新增状态时同时更新各拍与 initial_state；保持 actor id 一致。首镜 transition 为 start，后续为 continuous 或 cut；连续时 shot_id 不变，切镜时改变。一镜到底全程同一 shot_id；越轴填写 axis_bridge。

`headers` 和 `sections.summary` 是人工撰写的投喂文字，代码不从它们推理故事。修改 cast、timing、rules、beats 后需同步摘要与总设定并做语义复查；程序只检查结构、引用、声明与时间关系。能力声明的真假、实际消耗、物理成立均需导演复核。

## 命令

从技能目录运行：

```bash
python scripts/combat_tool.py validate examples/epic-30.plan.json
python scripts/combat_tool.py validate examples/epic-30.plan.json --max-duration 15
python scripts/combat_tool.py render examples/grounded-15.plan.json --platform generic --out-dir output/check
```

第二条预期失败，不会自动拆分。render 也支持 `--max-duration`；四种 `--platform` 值为 generic、libtv、xiaoyunque、flova，差别是交接单名称，均不注入未核验参数。

导出六份：design-card.md、director.md、prompt.txt、handoff.md、review.md、combat-plan.json。默认不覆盖，`--force` 才替换指定输出；拒绝符号链接、路径中的 junction，以及覆盖输入计划。导出不修改源计划，不访问网络，不生成视频。

校验器只实现随包 Schema 所使用的关键字和本契约的语义规则，不是任意 JSON Schema 引擎。可另用标准 Draft 2020-12 验证器交叉验证结构。
