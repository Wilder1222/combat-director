# Combat Director · 独立战斗导演

**0.10.0 · 2026-09-30**。支持独立 Agent Skill 与 Codex 插件打包。116张资料卡与1,466个逐招来源条目覆盖技法、九角色战斗体系、连招、镜头、特效与场景，接入六轨编排；支持Niagara式粒子行为与按镜头选择的运动成像描述。无需 CineWeave、MCP 服务或视频平台插件即可完成文本创作。

源码仓库：[Wilder1222/combat-director](https://github.com/Wilder1222/combat-director)。版本变更见[CHANGELOG.md](CHANGELOG.md)。

LibTV 站内适配提供与核心0.10.0同步的自包含规则，入口与交付方式见 [LibTV 适配](adapters/libtv/README.md)。该版提供自包含 Markdown 和候选导入包，平台导入与生成尚未实测；原 Codex 发行方式不变。

## 能做什么

- 人物级武侠攻防、升级式斗法、巨型敌人反制三种母版。
- 六轨导演时间轴：人物攻防、表演情绪、摄影机、特效、环境反馈、声音。
- 粒子效果按触发、来源、路径、交互、消散与环境留存组织，区分附刃光效和离体攻击。
- 运动模糊结合主体与相机相对运动编排，区分曝光、粒子尾迹和艺术残影，保留用户的速度与风格选择。
- 导演细拍与投喂主段分离，保存人物、武器、能力代价与场景连续性。
- 可选[约44镜短镜爆剪](skills/combat-director/references/rapid-cut-continuity.md)：三镜攻击链、同侧轴线、每3—5秒空间复位、Hit Stop与力感反馈，附30秒镜长配额；仅文字设计，未验证成片效果。
- 默认精简事件正文，可选八标签导演细稿；场地状态、环境因果与镜头覆盖联动。
- 现成提示词分版本拆解、武器召回与回握、动作接力、旧伤铺垫、台词预算和镜头/定格例外复核。
- 可选兵器、轨迹、回应、持物转移和能力代价契约，直接进入最终提示词。
- 动作签名、破防恢复、多人与远近调度；七张原创机制卡按普通设计/幻想能力分开检索。
- 38类技法、9个角色预设、18张编排卡、15张镜头卡、4张特效卡、5种风格与20个场景；支持招式名、武学、角色版本、内容层级过滤和分页。
- 固定源文逐段摘录与原创改编说明分开，17张仅有名称/定位的卡显式标为轮廓。
- 逐招区分仅名称、文字描述与动作路径，保留同名流派、别名歧义和源行；紧凑检索后只读选中条目，原文按需展开。
- JSON 计划、摘要失效检查和完整七文件/精简八文件导出；审片记录与后续起点核对；不执行视频生成。

爆剪规则的[场景文本测试与优化记录](evals/rapid-cut-2026-09-30/analysis.md)包含两轮独立生成、逐镜时间核算、独立审阅和保留的失败样本；算术通过与空间语义结论分别报告。

[国漫仙侠战斗参考研究](docs/research/2026-09-30-donghua-combat-study.md)持续积累实际画面观察；当前为首批局部样本，保留来源版本、抽样时间及证据缺口，不将抽帧当作完整逐镜或音轨验证。

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

另有两套运动成像案例：[固定机位木杖12秒](skills/combat-director/examples/motion-staff-12.md)、[侧移跟拍附刃交手12秒](skills/combat-director/examples/motion-blade-12.md)。各含六轨、结构化计划与可复制提示词，从作者计划与显式复核凭证确定性生成；没有视频观测证据。

0.7.0新增[18秒演武与恢复](skills/combat-director/examples/sword-recovery-18.md)和[24秒回廊护送](skills/combat-director/examples/corridor-escape-24.md)，含六轨与可复制提示词。太极剑、龙爪手、袈裟、独孤九剑、六脉神剑通过[动作转译](skills/combat-director/references/action-design.md)和[机制库](skills/combat-director/references/library-workflow.md)使用；它们是创作解释，不是历史招谱、原著还原或已验证生成参数。

另有两套直接阅读的文字案例：[18秒飞剑回握与旧裂口](skills/combat-director/examples/return-and-payoff-18.md)、[15秒登场与首斩前收黑](skills/combat-director/examples/entrance-cliffhanger-15.md)。它们展示新增编排方法，没有配套JSON，也不冒充CLI已校验的动作事实。

## 可选工程工具

0.10.0 新增[15秒双女兵器大场面与换场地案例](skills/combat-director/examples/xianxia-weapons-15.md)，以及与既有事件一致的[人物级精简正文](skills/combat-director/examples/grounded-15.compact.txt)。它们是文字设计，没有媒体效果证明。场景分区、环境后果和镜头覆盖先于正文，详见[精简输出](skills/combat-director/references/compact-output.md)。

已有计划可通过 `render ... --prompt-style compact --prompt-file reviewed.json` 导出独立复核后的精简表达；默认命令保持原详细输出。精简模式另存表达与复核文件，修改事实或正文会使旧复核失效。

Python 3.10+，标准库，无联网和账号读取。以下命令从项目根目录运行：

```powershell
python skills/combat-director/scripts/combat_tool.py validate skills/combat-director/examples/epic-30.plan.json
python skills/combat-director/scripts/combat_tool.py render skills/combat-director/examples/epic-30.plan.json --platform xiaoyunque --out-dir outputs/epic
python skills/combat-director/scripts/library_tool.py search design --query "回廊 撤离" --scope group
python skills/combat-director/scripts/library_tool.py search abilities --query "六脉神剑"
python skills/combat-director/scripts/library_tool.py search techniques --query "乌龙摆尾" --school "八卦掌"
python skills/combat-director/scripts/library_tool.py items --query "乌龙摆尾" --kind techniques --school "八卦掌"
python skills/combat-director/scripts/library_tool.py items --query "小内返" --min-detail description
python skills/combat-director/scripts/library_tool.py item arvin-tech-judo-item-655720874f5d --source
python skills/combat-director/scripts/library_tool.py search characters --character "白鸽"
python skills/combat-director/scripts/library_tool.py stats
python skills/combat-director/scripts/library_tool.py validate
python scripts/build_arvin_library.py --check
python -m unittest discover -s tests -v
python scripts/project.py validate
python scripts/project.py validate-release
python scripts/project.py build
```

render 导出设计卡、六轨导演稿、提示词、编译交接 JSON、平台交接单、待填验收表和原计划。已存在文件默认不覆盖，显式 `--force` 才替换；拒绝覆盖源计划或链接文件。

validate 和 render 都接受 `--max-duration 15`。30秒计划在确认上限15秒时失败，不自动分段。四种内置平台配置仍为未知，也可用 `--profile` 提供有日期和来源的能力记录。详见[数据契约](skills/combat-director/references/contract.md)、[平台检查](skills/combat-director/references/platforms.md)、[审片回流](skills/combat-director/references/review-loop.md)。

修改计划后用 `status` 查看过期范围，用 `compile` 生成待复核事实与表达，实际核对后用 `apply-review` 记录结论。缺失或过期记录会阻止正式导出；哈希匹配不等于语义已被程序证明。1.0 计划用 `migrate` 显式升级，不自动确认旧摘要。

开发检查可创建虚拟环境并安装 `requirements-dev.txt`，运行 `python scripts/validate_release.py`；该流程包括重建一致性、单元测试、标准 Schema 交叉检查、打包与解压独立 CLI。开发依赖不进入插件运行时。

## Codex 插件

项目根目录的 `.codex-plugin/plugin.json` 指向完整技能目录。构建产物为 `dist/combat-director-0.10.0.zip`；仅包含插件清单、技能入口、参考文档、机制库、Schema、脚本与示例。原始附件、测试、评估快照和仓库文档不进入插件包。

`codex plugin add <plugin>@<marketplace>` 需要可用的市场条目，ZIP构建不等于安装。本机使用个人市场的本地来源；安装/升级状态与代码验证分别记录于[验证报告](docs/validation.md)。其他机器仍需配置自己的安装来源。仓库尚未指定开源许可证。

## 来源与维护

六份原件及 SHA-256 存档于 `sources/attachments/2026-09-21`，不修改原件。[来源记录](docs/source-status.md) 区分继承内容与重建内容；[本次验证](docs/validation.md) 不沿用附件的历史测试计数。

新增六份原件存于 `sources/attachments/2026-09-22`，保留哈希和八个版本的范围。[逐份拆解](docs/research/2026-09-22-combat-prompt-breakdown.md)包含时间结构、优势、冲突和修订理由；运行包只收录提炼的方法及两套文字例，未读取的参考图和视频不会被写成已观察证据。

`references/`、脚本、Schema 和 plan.json 在六份附件中缺失，本项目重新实现这些配套资源。三份提示词保留其核心内容，修复拼句、方位歧义及落刀因果。脚本版本不宣称与缺失原实现兼容。

`python scripts/rebuild_examples.py` 重建原三例，`python scripts/build_action_examples.py` 重建新增三例；会覆盖对应派生文件。编辑源在两个脚本，固定复核凭证在 `sources/editorial/`，源内容改变后重建会拒绝过期凭证。`build_action_examples.py --drafts` 可先生成未复核草稿。新创作另存输出目录，不修改随包示例。

平台当前能力、实际视频质量与原MP4的逐帧还原均未验证。程序不做物理模拟，主段摘要与细拍语义仍需人工或多模态复核；新提示词方法中的语义对读也没有伪装为确定性程序检查。

## 设计调研与完善计划

[2026-09-21 设计调研](docs/research/2026-09-21-skill-design-review.md) 保留 0.2.0 的调查基线；[分阶段计划](docs/plans/2026-09-21-improvement-plan.md) 定义实施范围。[实施进度](docs/implementation/progress.md) 区分已落地能力、文字评估结果和待完成的宿主/媒体验证。

本轮变化见[变更记录](CHANGELOG.md)。早期试点与失败分析保留在[原行为评估](docs/implementation/behavior-evaluation.md)，新增素材的两题旧版/新版比较见[0.6.0文字评估](docs/implementation/prompt-evaluation-0.6.0.md)。本地发布流程、运行包与安装证据见[当前验证](docs/validation.md)，不以这些检查声称视频效果通过。

0.7.0的[融合决策](docs/research/2026-09-22-skill-library-integration.md)记录实际读取范围、采用/舍弃的规则与新实现边界。原数据契约仍为1.2，六套结构化示例无需迁移。当前LibTV适配是独立维护的0.6.0基础版本，新机制库未自动同步到其单文件入口。

0.8.0的[招式融合方法](skills/combat-director/references/technique-adaptation.md)将主攻、破招与收势落实为可见动作，并区分同名角色/招式版本。[白鸽对红茶18秒演武](skills/combat-director/examples/arvin-baige-hongcha-18.md)与[剑神对火焰绯雪24秒交锋](skills/combat-director/examples/arvin-sword-fire-24.md)提供完整六轨和可复制提示词，没有配套JSON或视频实测。

Arvin原件与MIT许可固定在 `sources/upstream/arvin-seedance`；[本次吸收记录](docs/research/2026-09-23-arvin-combat-integration.md)记录范围和限制，[覆盖清单](docs/implementation/arvin-library-coverage.json)逐卡列出源文行号。编辑 `scripts/build_arvin_library.py` 内的选段/改编说明或 `sources/editorial/library-base.json` 后执行 `python scripts/build_arvin_library.py`，再运行发布验证；生成卡与catalog不直接手改。上游六份兵器/轻功专项缺失，不宣称复原完整武学。运行包包含归属清楚的摘录卡及MIT通知，不依赖原始快照或网络；LibTV单文件仍独立维护。


0.8.1修复[审阅中的三项实现问题](docs/reviews/2026-09-23-0.8.0-review.md)：正式打包检查生成一致性，补齐跨分类筛选，并让已登记旧卡可退役、写入失败可恢复。维护前可用 `python scripts/build_arvin_library.py --plan`只读查看变化；`--recover`用于确认原进程结束后的中断恢复。关联依据在 `sources/editorial/arvin-facets.json`，受管理产物在 `sources/editorial/arvin-generated.json`，不得用刷新哈希绕过人工改动冲突。进度见[优化计划](docs/plans/2026-09-23-0.8.0-optimization-plan.md)。

0.8.2的[Niagara调研](docs/research/2026-09-23-niagara-prompt-research.md)核对用户分享、Epic官方资料、示例项目和视频模型指南；[实施与对照计划](docs/plans/2026-09-23-niagara-integration-plan.md)明确已落地内容和未运行试验。使用时按需读[粒子行为](skills/combat-director/references/particle-vfx.md)，参考[12秒附刃光迹](skills/combat-director/examples/particle-blade-12.md)或[12秒木杖薄尘](skills/combat-director/examples/particle-staff-12.md)。这些是画面设计，不代表实际执行Niagara或已验证视频效果；保留六轨、八标签和计划1.2，库数据不变。

0.8.3按[motion blur融入计划](docs/plans/2026-09-23-motion-blur-integration-plan.md)接入[运动成像参考](skills/combat-director/references/motion-blur.md)、两套结构化案例及双层表达回归。示例权威在sources/editorial/0.8.3，执行 `python scripts/build_motion_examples.py` 重建，正式构建自动检查漂移；复核凭证必须来自实际文本审阅。工程与行为证据分开记录于[历史验证](docs/history/validation-0.8.3.md)，视频实验仍未运行。

2026-09-24补充[motion blur控制边界与验证设计](docs/research/2026-09-24-motion-blur-control-and-evaluation.md)及[后续文件级计划](docs/plans/2026-09-24-motion-blur-review-and-next-steps.md)：区分模型版本、提示增强、可见运动与真实参数；媒体探索先比较18条D/B样本，尚未执行。

0.9.0的[逐招来源与读取说明](docs/implementation/library-items-0.9.0.md)记录items索引1、CLI兼容和实测字符数；可从[分类导航](skills/combat-director/library/index.md)开始。WP04与WP05工程已完成，WP06全库独立创作比较进行中，不以检索测试代替。
