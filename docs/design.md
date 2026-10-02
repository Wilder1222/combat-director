# 当前设计与维护边界

Combat Director以场景、战斗类型、人物与招式为输入，生成详细中文战斗视频提示词。2026-10-02重构围绕AIGC设置拆解与提示词生成；源码基版保持0.10.0，本机安装由缓存刷新后缀区分，并在验证记录中单独核验。

## 从设置到正文

[入口](../skills/combat-director/SKILL.md)判断生成、局部改稿、参考分析或工程任务。完整生成实际读取[生成模板](../skills/combat-director/references/prompt-construction.md)，按以下过程完成：

**六项设置 → 动作单元 → 状态链 → 时间与镜头覆盖 → 命中及光影 → 正文与对读。**

六项为整体风格、战斗人物、武器、技能招式、命中效果、特效光影。模板将内容展开为25项写法（含法阵、法术效果与手印变化），每项包含组织顺序、可替换句式、具体教学例句及易错边界，另示范把多个要素融合成连续攻防；对抗单元以对手回应与结果衔接，演武单元以重心、旋向和兵器余势衔接。完整提示词在同一复制块中包含总设定与逐镜时间/镜长，按动作和信息量安排长短变化；一镜到底则划分镜内动作节拍。局部改稿仍遵守用户范围。

## 运行资源与读取条件

当前8份reference中，生成模板是完整创作的直接依赖；其余按任务选读。每个创作模块给出可替换句式和成立条件，链接仅用于加载，不代替方法。

| 资源 | 触发与用途 |
| --- | --- |
| [prompt-construction.md](../skills/combat-director/references/prompt-construction.md) | 完整生成/重编；逐项组织顺序/句式/例句、融合成段、动作单元、生成顺序、自含正文模板及修正 |
| [choreography.md](../skills/combat-director/references/choreography.md) | 特殊兵器、复杂攻防/演武、空间与群战、摄影或特效；选择相关局部句式融入本场 |
| [review-loop.md](../skills/combat-director/references/review-loop.md) | 参考拆解/成片诊断；把时间码证据转成提示词句，或给出可替换的修复正文 |
| [library-workflow.md](../skills/combat-director/references/library-workflow.md) | 查库/核实名称；命令、详情等级和来源动作到本场交锋的转换 |
| [platforms.md](../skills/combat-director/references/platforms.md) | 实际交接/绑定/生成；按文生、外观图、首帧、动作参考组织正文并核验入口 |
| [contract.md](../skills/combat-director/references/contract.md) | JSON/编译/审片；沿现有事实和表达字段工作，不为写作模板新增Schema |
| [sources.md](../skills/combat-director/references/sources.md) | 最小来源与证据范围；只追溯，不作为应用前置 |
| [third-party-notices.md](../skills/combat-director/references/third-party-notices.md) | 保留完整归属及MIT许可，来源卡仍依赖此路径 |

## 本轮删改

- 入口原有大段输出细则移入单一生成模板，入口只保留路由、继承、核心关系与工作顺序；消除“有链接就算已应用”的歧义。
- 将战斗、摄影和成像的抽象讲解改为适用条件、局部句式与成立边界；八份原提示词和两段实片中的可用关系已内化，创作不依赖研究目录或外链。
- 参考拆解从只交“观察与解释”改为同时提供证据到句子的转写方法；诊断从泛化建议改为替换句和复测目标。
- 来源页删除长篇外链书目、重复的方法介绍与历史版本叙述，仅保留来源类别、已提炼内容和证据范围。研究报告仍保留原始依据，不重复复制到运行包。
- 教学骨架使用变量并配局部写法示例，不恢复历史整场创作答案；只选择本场需要的关系，不把两片的身份、场景、镜数和结尾固化成默认模板。

## 不变的工程边界

数据契约、运行代码、生成资料卡和原始来源保持原样。工程接口、来源等级、素材绑定与复核失效规则是必要操作信息，不改写为视频画面指令。许可完整保留。

资料权威在sources/editorial与固定sources/upstream中，变更生成资料时先改权威再生成和校验，不手改卡片。工程夹具在tests/fixtures，研究图片与分析在docs/research，文字试用输出在outputs；均不混入运行技能包。构建继续拒绝examples、tests、fixtures或evals进入技能资源。

正式构建使用`python scripts/project.py build`；完整工程验证使用`.venv/Scripts/python.exe scripts/validate_release.py`，统一更新docs/implementation/release-validation.json。验证结果与文字试用边界见[当前验证](validation.md)。

## 依据

使用本机skill-creator指导，并于2026-10-02核对[Agent Skills最佳实践](https://agentskills.io/skill-creation/best-practices)与[评估方法](https://agentskills.io/skill-creation/evaluating-skills)：清晰触发、渐进读取、可执行过程、适度细节与真实任务检查。来源只支撑设计方法，不证明视频质量。

创作依据保留在[八份提示词审阅](research/2026-10-01-eight-prompts-design-review.md)与[两段战斗视频拆解](research/2026-10-02-two-combat-videos-analysis.md)。文字试用、结构校验和可复现打包分别留证，不声称本轮已完成新视频验收或成功率比较。
