# Combat Director · 战斗导演

一个入口编写和改写详细中文战斗视频提示词，覆盖武侠、仙侠及其他战斗；支持素材适配、成片诊断和可选工程导出。当前软件0.11.0，工程契约Combat Plan 1.3。

从[唯一技能入口](skills/combat-director/SKILL.md)开始。输入场景、人物、招式和约束即可；主流程组织目标、动作、摄影及连续状态，御剑、法阵、分身、真人质感和声音按本次任务读取专题。

默认详细正文集中稳定设定，逐镜常用【画面与动作】【摄影】【衔接】。时长按用户要求或内容拟定；同一次交换不因栏目/切镜再次发动。整场一个完整复制块，独立提交的分段各自自含。一镜到底使用镜内节拍。

需要视觉重音时，按局势选择出招、接触或结果相位，写清冲击帧/闪帧的保留信息与恢复动作。方法、项目取舍与原创示例见[关键一击优化报告](docs/implementation/vibeshot-impact-optimization.md)。

参考适配明确保留与替换的关系，多镜正文逐切口对读事件相位、方向/地标、持物接点与动势。方法与工程边界见[GoodCase连续性融合分析](docs/implementation/goodcase-continuity-optimization.md)。

~~~text
使用 $combat-director，写12秒单剑御空追逐转近战，保留双方持剑与回应，末尾脱离剑程但追击继续。
~~~

## 当前结构

| 位置 | 用途 |
| --- | --- |
| skills/combat-director | 唯一Skill、按需参考、资料库和自含工程工具 |
| scripts、tests | 来源/内容/构建校验及原工程、仙侠机制和媒体工具回归 |
| sources/editorial | 资料库生成权威；修改后重建，勿手改生成卡 |
| sources/upstream | 固定上游及完整仙侠来源快照，不是运行入口 |
| docs | [设计](docs/design.md)、[验证](docs/validation.md)、[来源](docs/source-status.md)及[融合计划](docs/xianxia-integration-plan.md) |
| outputs/current、dist | 本机试用/证据和当前候选包，均不进入Git或默认加载 |

## 工程工具

核心工具使用Python 3.10+与标准库。普通创作不需要JSON；本地抽帧另检查Pillow、ffmpeg、ffprobe。

~~~powershell
python -X utf8 skills/combat-director/scripts/combat_tool.py validate tests/fixtures/three-actors.plan.json
python -X utf8 scripts/validate_content.py
python -X utf8 scripts/project.py build
.venv/Scripts/python.exe scripts/validate_release.py
~~~

工程计划、已审正文与实际观察分别保存，修改事实/正文使对应复核失效。[契约](skills/combat-director/references/contract.md)说明1.1/1.2兼容及1.3可选扩展；[抽帧说明](skills/combat-director/references/video-evidence-tool.md)说明PTS、像素与审阅边界。

发布包只提供combat-director。仙侠插件入口由本项目吸收后退役；切换安装必须核对当前版本与宿主实际发现，源码变化不会热替换既有对话缓存。文字、结构、打包和工具测试各有验证范围，真实视频和声音另按实际观察记录。
