# 事件与读位窗口文本检查

入口 `check_sequence.py` 复用 `check_timing.py`，只检查显式声明的数据。正文与标记在同一稿内；输出回执绑定整个源稿SHA-256。不是Combat Plan字段扩展，也不是自然语言或视频动作识别器。

```powershell
python -X utf8 evals/rapid-cut-2026-09-30/check_sequence.py skills/combat-director/examples/flower-path-44.md --expected-duration 30 --expected-shots 44 --out evals/rapid-cut-2026-09-30/jade-full/sequence-validation.json
python -X utf8 evals/rapid-cut-2026-09-30/sequence_self_test.py
```

逐镜Markdown沿用镜号、入出点、可选镜长。职责单元格写 `E01/来路`、`E01/命中点`（或`避让点`）、`E01/反馈`，每事件连续三镜。时间标记单元格支持 `首触 3.30；Hit Stop 3.30—3.34`、`读位 4.80—6.00`。无接触的避让不写首触和短停；持续接触只引用原事件，不追加第二个首触。

单独一行写 `微慢 开场 0.20—0.70` 与 `微慢 终局 27.90—28.45`；跨镜微慢可跨镜界，但不得超总长。分段记录如 `节奏段 拉升 0.00—8.00`，必须从0连续覆盖到总长并落在镜界。空窗口、缺失事件或不支持的职责不会当通过。

检查结果包括镜长分布、三镜映射、接触间隔、分段切镜密度、读位窗口及开头/结尾的最大空间空窗。它不能证明声明的画面真的同框，不能发现未标注攻击，也不会自动判断刀剑可达、反向启动、靴底承重或情绪表演。正文中的统计摘要需与回执人工对读；旧稿没有这些标记时仍用原计时器，不批量改写历史证据。

高风险几何继续使用 `recheck_epic_footprints.py` 与 `verify_near_miss.py` 中的明确包络；时间检查通过不替代这些局部核算。源稿修改后重新生成回执，审阅记录分别标明主任务编辑复核、独立生成/审稿及实际媒体观察。
