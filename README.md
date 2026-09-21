# Combat Director · 独立战斗导演

**0.5.0 · 2026-09-21**。以用户提供的六份对话附件为基础，支持独立 Agent Skill 与 Codex 插件打包。新增计划复核、具体交手、审片状态与平台证据检查；无需 CineWeave、MCP 服务或视频平台插件即可完成文本创作。

源码仓库：[Wilder1222/combat-director](https://github.com/Wilder1222/combat-director)。版本变更见[CHANGELOG.md](CHANGELOG.md)。

## 能做什么

- 人物级武侠攻防、升级式斗法、巨型敌人反制三种母版。
- 六轨导演时间轴：人物攻防、表演情绪、摄影机、特效、环境反馈、声音。
- 导演细拍与投喂主段分离，保存人物、武器、能力代价与场景连续性。
- 中文八标签提示词、平台交接、审片与最小修复。
- 可选兵器、轨迹、回应、持物转移和能力代价契约，直接进入最终提示词。
- JSON 计划、摘要失效检查和七份文件导出；审片记录与后续起点核对；不执行视频生成。

## 开始使用

入口：[SKILL.md](skills/combat-director/SKILL.md)。只选择一个安装范围，将整个 `skills/combat-director` 文件夹放入宿主技能目录，再在新任务调用。当前公开文档使用用户目录 `~/.agents/skills` 或项目 `.agents/skills`；本机 bundled 指南仍使用 `~/.codex/skills`，实际发现情况应按宿主验证，避免同时安装多份同名技能。见[宿主与验证记录](docs/validation.md)。

```text
使用 $combat-director，制作30秒仙侠战斗测试片，16:9，单次生成，允许内部切镜。
白衣女剑客对阵青甲修士，开阔戈壁，使用升级式斗法。
每次能力必须有对方回应、限制和代价；自然肤质，动作与表演可读。
先给六轨导演稿，再整理为6段小云雀提示词；不实际生成、不写入正式剧情。
```

三套示例均来自附件的原创测试方案，细拍计划由本项目重建：

| 示例 | 时长 | 导演拍 / 投喂段 | 镜头 |
| --- | --- | --- | --- |
| [升级式斗法](skills/combat-director/examples/epic-30.prompt.txt) | 30秒 | 11 / 6 | 允许内部切镜 |
| [人物级攻防](skills/combat-director/examples/grounded-15.prompt.txt) | 15秒 | 6 / 4 | 一镜到底 |
| [巨型敌人反制](skills/combat-director/examples/colossus-30.prompt.txt) | 30秒 | 8 / 6 | 允许内部切镜 |

另外三套原创教学案例采用可选动作契约：

| 示例 | 重点 |
| --- | --- |
| [窄巷取函](skills/combat-director/examples/alley-letter-15.prompt.txt) | 15秒，纸函可见交接、木杖材质与双方脱离 |
| [三人护送](skills/combat-director/examples/three-person-exit-18.prompt.txt) | 18秒，第三人进入画外后仍有连续状态 |
| [反制失败后修订](skills/combat-director/examples/failed-counter-repair-18.prompt.txt) | 18秒，货架失效、右手代价与左手后续操作 |

六套均是文本设计，没有实际视频出片验证。

## 可选工程工具

Python 3.10+，标准库，无联网和账号读取。以下命令从项目根目录运行：

```powershell
python skills/combat-director/scripts/combat_tool.py validate skills/combat-director/examples/epic-30.plan.json
python skills/combat-director/scripts/combat_tool.py render skills/combat-director/examples/epic-30.plan.json --platform xiaoyunque --out-dir outputs/epic
python -m unittest discover -s tests -v
python scripts/project.py validate
python scripts/project.py build
```

render 导出设计卡、六轨导演稿、提示词、编译交接 JSON、平台交接单、待填验收表和原计划。已存在文件默认不覆盖，显式 `--force` 才替换；拒绝覆盖源计划或链接文件。

validate 和 render 都接受 `--max-duration 15`。30秒计划在确认上限15秒时失败，不自动分段。四种内置平台配置仍为未知，也可用 `--profile` 提供有日期和来源的能力记录。详见[数据契约](skills/combat-director/references/contract.md)、[平台检查](skills/combat-director/references/platforms.md)、[审片回流](skills/combat-director/references/review-loop.md)。

修改计划后用 `status` 查看过期范围，用 `compile` 生成待复核事实与表达，实际核对后用 `apply-review` 记录结论。缺失或过期记录会阻止正式导出；哈希匹配不等于语义已被程序证明。1.0 计划用 `migrate` 显式升级，不自动确认旧摘要。

开发检查可创建虚拟环境并安装 `requirements-dev.txt`，运行 `python scripts/validate_release.py`；该流程包括重建一致性、单元测试、标准 Schema 交叉检查、打包与解压独立 CLI。开发依赖不进入插件运行时。

## Codex 插件

项目根目录的 `.codex-plugin/plugin.json` 指向完整技能目录。构建产物为 `dist/combat-director-0.5.0.zip`；仅包含插件清单、技能入口、参考文档、Schema、脚本与示例。原始附件、测试、评估快照和仓库文档不进入插件包。

当前没有注册市场或安装插件。`codex plugin add <plugin>@<marketplace>` 需要已配置的可用市场条目，ZIP 构建不等于安装。仓库尚未指定开源许可证。

## 来源与维护

六份原件及 SHA-256 存档于 `sources/attachments/2026-09-21`，不修改原件。[来源记录](docs/source-status.md) 区分继承内容与重建内容；[本次验证](docs/validation.md) 不沿用附件的历史测试计数。

`references/`、脚本、Schema 和 plan.json 在六份附件中缺失，本项目重新实现这些配套资源。三份提示词保留其核心内容，修复拼句、方位歧义及落刀因果。脚本版本不宣称与缺失原实现兼容。

`python scripts/rebuild_examples.py` 重建原三例，`python scripts/build_action_examples.py` 重建新增三例；会覆盖对应派生文件。编辑源在两个脚本，固定复核凭证在 `sources/editorial/`，源内容改变后重建会拒绝过期凭证。`build_action_examples.py --drafts` 可先生成未复核草稿。新创作另存输出目录，不修改随包示例。

平台当前能力、实际视频质量、原 MP4 的逐帧还原与 Codex 市场安装均未验证。程序不做物理模拟，主段摘要与细拍语义仍需人工或多模态复核。

## 设计调研与完善计划

[2026-09-21 设计调研](docs/research/2026-09-21-skill-design-review.md) 保留 0.2.0 的调查基线；[分阶段计划](docs/plans/2026-09-21-improvement-plan.md) 定义实施范围。[实施进度](docs/implementation/progress.md) 区分已落地能力、文字评估结果和待完成的宿主/媒体验证。

本轮变化见[变更记录](CHANGELOG.md)；试点与失败分析见[行为评估](docs/implementation/behavior-evaluation.md)。0.5.0完成23项本地发布流程检查，45项单测中44通过、1项因Windows链接权限跳过。当前不以工程测试声称视频效果或已安装的宿主路由通过。
