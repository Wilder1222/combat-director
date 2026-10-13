# Combat Director · 战斗导演

编写和改写详细中文战斗视频提示词，覆盖武侠、仙侠及其他战斗；支持素材适配、成片诊断和可选工程导出。软件版本0.11.0，工程契约Combat Plan 1.3。

从[技能入口](skills/combat-director/SKILL.md)开始，给出场景、人物、动作与约束即可。主流程组织目标、动作、摄影和连续状态，按任务读取机制专题；整场交付完整复制块，独立分段各自自含。

[成稿模板](skills/combat-director/references/prompt-construction.md)默认保留独立全局画面、画质、风格和逐镜动作/摄影标签；角色打法、材质光色、术法造型与声画主次在本场事件中兑现，既有环境按实际作用反馈。用户指定的其他格式、固定机位、静音和局部改稿范围优先。完善范围与验收方法见[表现力执行方案](docs/implementation/2026-10-12-creative-expression-optimization.md)。

[题材路由](skills/combat-director/references/genre-routing.md)让内容随仙侠、武侠、写实格斗等题材变化，再搭配真人、CG、二维等呈现方式；支持真人仙侠、动画武侠、二维写实格斗等组合。所选能力影响攻防，画风与运镜不自行增减能力，未使用的术法或兵器栏目省略。

完整提示词同时展开本场的画风/画质、材质或笔触、光色、特效形态与摄影。真人、写实国漫/游戏CG、赛璐璐、水墨、厚涂、纸偶、像素和版画等可按需求选用或明确组合；手持、稳定器、固定观察、一镜到底或快速多镜分别按动作安排。方法与来源见[多风格优化记录](docs/implementation/2026-10-10-visual-style-research.md)。

专业制作方法进一步覆盖观众知情/镜头揭示、机距与透视、移动光场、真人与动画表演，以及观感—资产渲染—编码显示的分层方案。实际方法与官方/主创/社区来源见[专业制作调研](docs/implementation/2026-10-10-professional-craft-research.md)；引擎方案按任务读取，不成为普通创作的必填流程。

~~~text
使用 $combat-director，写12秒单剑御空追逐转近战，保留双方持剑与回应，末尾脱离剑程但追击继续。
使用 $combat-director，写10秒真人徒手格斗，包含处理来拳、近身控制与脱离，动作和受力写实。
使用 $combat-director，把已有武侠交锋改为二维赛璐璐，保留人物、轻功、动作和结局，只调整呈现。
~~~

每个战斗节点在最终提示词中明确起止秒数和占时，战斗中的每个动作与对手回应直接标耗时，用具体秒数锚定速度；慢镜只写持续时长，预算内部核对，复制块不附计时归属注释。full/compact/detailed同步显示既有节点时间，已有具体交手事件按实际有效耗时投影。接触型静电、身体先反应而意识后确认、追赶型摄影按场景选用，示范见[觉醒型近战机制卡](skills/combat-director/library/abilities/static-contact-awakening.md)。

## 仓库结构

| 位置 | 职责 |
| --- | --- |
| `skills/combat-director/` | 发布的技能入口、按需参考、资料库、契约与自含工具 |
| `scripts/combat_project/`、`scripts/*.py` | 发布校验与构建实现包，以及保留既有CLI的专项生成、检查工具 |
| `tests/` | 工程、来源、构建和媒体工具回归；夹具不进入运行包 |
| `sources/editorial/` | 资料库编辑权威与生成归属记录 |
| `sources/upstream/`、`sources/attachments/` | 固定上游、许可与用户来源证据 |
| `docs/` | [当前架构](docs/design.md)、[验证用法](docs/validation.md)、[来源边界](docs/source-status.md) |
| `docs/history/`、`docs/implementation/` | 历史决策导航与冻结的融合、研究和验收记录 |
| `outputs/`、`dist/` | 忽略的本机证据、当次报告和构建产物 |

## 维护命令

Python 3.10+可运行标准库工具；完整发布校验使用项目虚拟环境。本地抽帧按需检查Pillow、ffmpeg与ffprobe。

~~~powershell
python -X utf8 skills/combat-director/scripts/combat_tool.py validate tests/fixtures/three-actors.plan.json
python -X utf8 scripts/build_arvin_library.py --check
python -X utf8 scripts/validate_content.py
python -X utf8 scripts/project.py build
.venv/Scripts/python.exe -X utf8 scripts/validate_release.py
~~~

资料库修改先进入编辑权威，再由生成器重建；具体依赖和生成归属见[架构](docs/design.md)。当前发布检查写入`outputs/validation/release-validation.json`，历史验收按[固定Git版本](docs/history/2026-10-09-integration.md)复查。源码重构后的当前检查与旧版审阅分别报告，文字、结构和工具测试不证明实际视频或声音质量。
