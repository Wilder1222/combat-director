# 来源与归属

当前跨模型方法和逐项官方来源见[通用视频生成写法](video-generation.md)。2026-10-04核对Runway、Google Veo、Kling、OpenAI Sora、Adobe Firefly的官方正文，读取Luma官网搜索收录内容，并结合此前同日读取的Seedance官方2.0/2.5正文。采用可迁移的写作决策，保留各家在负向表达、多镜模式、时间与声音上的差异；Seedance仅为按需专项，不是默认模型。未观看本轮指南内媒体、安装外部skill或发起生成。

创作方法已转写在prompt-construction.md、choreography.md与review-loop.md中；本页只供追溯，不是写作前置，不要求Agent打开外链才能应用方法。

| 依据 | 已内化的提示词写法 | 证据边界 |
| --- | --- | --- |
| 用户提供的八份原提示词（时序局、双人打斗第二弹、小师妹首登、最新打斗提示词、铜币转场、7.31、7.30、8.2） | 兵器差异与逐招任务、发射机制反制、旧痕回收、离手交接与伞结构转招、地形接力与尺度升级、法相揭示、附魔蓄爆、延迟结果与焦点交接、构图匹配、贴附式水墨及分层碰撞反馈 | 已将可迁移关系重写为变量句式与局部教学例句；不沿用重复段、时长冲突、无依据的精确参数和固定特效套餐。文字不证明原片执行或模型成功率 |
| 更早的双女、双男、双人打斗原稿 | 分波封路与逐层碰撞、主剑/飞剑/投影的去向、跨区锚点、透明气压波通过介质显形 | 同构稿不计为独立效果验证；能力归属、角色外观与原稿全局限制不混用，重复方法并入同节 |
| 用户30秒荒野双人斗法与17.83秒月下持伞视频 | 攻防接力、范围升级、环境支撑；重心/旋向/兵器余势连招、光弧与动作同向、构件反馈 | 覆盖全片的采样与局部连续帧；未实听音轨，不宣称全片速度/完整镜数已验收 |
| 动漫局部截图与用户失败成片 | 纵深、高差与法术层次；接点缺失、重复接架、持物和终局修复句式 | 截图只支持采样范围；失败用于界定问题，不作为成功案例 |
| Arvin固定版本招式资料 | 按名称/描述/路径等级检索，再转成当前交锋 | 原文、项目补写与用户设定分开；完整归属和MIT文本保留在third-party-notices.md |

当前来源原件、正文抽取及各自哈希保留在仓库来源目录，不进入创作必读路径；历史研究报告与截帧已清理，旧观察不作为本轮生成效果证据。模板为本项目的可替换编写方法，不是原作者逐字提示词。保留原始附件、来源摘录和许可，用于当前方法与资料库的来源追溯。

结构设计采用[Agent Skills作者最佳实践](https://agentskills.io/skill-creation/best-practices)的明确触发、渐进读取、可执行步骤和输出模板，以及[评估方法](https://agentskills.io/skill-creation/evaluating-skills)的真实任务检查。它们支持技能组织，不证明视频生成质量。

## 视频生成方法依据

2026-10-03核对下列官方资料，将共通原则转写成当前战斗流程；战斗片段边界、接触验收和密度取舍是项目设计推导，并非厂商验证过的战斗配方。版本建议只在对应模式适用，来源日期不代表用户账号已具备这些能力。

| 官方资料 | 本项目采用的原则与范围 |
| --- | --- |
| [Runway提示方法](https://help.runwayml.com/hc/en-us/articles/47313698911891-Introduction-to-Prompting)、[图生视频](https://help.runwayml.com/hc/en-us/articles/48324313115155-Image-to-Video-Prompting-Guide) | 细节用于消除歧义，按结果逐项迭代；图生以运动为主，起始图质量和隐含运动影响后续，不把所有写法列为必填 |
| [Google视频最佳实践](https://docs.cloud.google.com/gemini-enterprise-agent-platform/models/video/best-practice)、[提示指南](https://docs.cloud.google.com/gemini-enterprise-agent-platform/models/video/video-gen-prompt-guide) | 短片聚焦清楚的场景事件，图生避免重复静态画面；负向表达须按支持它的实际入口处理 |
| [Sora 2提示指南](https://developers.openai.com/cookbook/examples/sora/sora2_prompting_guide) | 动作按可观察节拍写清，简化单镜的主动作与相机任务；只作为该指南的写法依据，不推断当前服务可用性或跨模型限制 |
| [Seedance 2.0发布说明](https://seed.bytedance.com/zh/blog/official-launch-of-seedance-2-0)、[Seedance 2.5提示指南](https://docs.volcengine.com/docs/ark/seedance-2-5-prompt-guide?lang=zh) | 多模态与多镜控制需按版本/任务路由，素材用途和对应关系清楚；时间表达及参考能力不从某一代模型泛化到所有入口 |

2026-10-04针对用户提供的Seedance 2.0 mini全能参考失败样片，复核[Seedance 2.0系列提示词指南](https://docs.volcengine.com/docs/ark/seedance-2-0-prompt-guide?lang=zh&redirect=1)：按事件顺序写分镜、精确时间支持不稳定、单镜优先一项运镜、避免冗余剧本，并明确素材的参考用途。上述是系列指南；该单条样片不支持mini能力上限或成功率结论。把单次打击与持续推压分开、核对首次接触和分离，是本项目从可见失败中形成的创作修正，尚无修订后生成验证。

具体操作集中在生成模板的“整场编排与生成片段”和review-loop.md，不要求普通创作重新联网读取这些来源。

2026-10-04另核对[Seedance 2.0官方展示](https://seed.bytedance.com/en/seedance2_0)中的绿幕动作联合参考与雪地近战两例，取得展示文件并查看定点帧。前者在同一媒体中展示人物图、动作参考和结果；后者标记I2V但未取得独立首帧。它们支持素材分工与指定招式另行验收的设计，不证明独立复现、实时节奏或本项目成功率；未将原片或外部提示词复制进运行包。

## 公开skill方法比较

2026-10-04补充核对三个一手研究/开源项目，以下为独立转写的设计依据，未复制或运行外部代码：

| 项目 | 可采用的关系 | 不据此推断 |
| --- | --- | --- |
| [DanceTogether](https://dancetog.github.io/) | 参考图配合逐人姿态与遮罩，强调交互过程中身份和动作的持续绑定；据此增加换位/遮挡后的身份检查 | 作者展示与评测不是本项目复现；本轮只读项目说明，未审阅其演示视频，不宣称所有双人接点可靠 |
| [Wan2.2 / Wan-Animate](https://github.com/Wan-Video/Wan2.2) | 动画与角色替换是不同任务，输入视频和角色图承担不同信息；据此明确动作迁移的输入分工 | 单角色驱动说明不等于双人战斗能力保证，也不等于普通文字能锁定骨架或持械接点 |
| [Motion Prompting](https://motion-prompting.github.io/) | 轨迹可表达物体和相机运动；据此区分人物世界路径与摄影，并核对控制数据是否真实存在 | 页面说明大部分展示为四选一、非实时；不将轨迹条件能力转成通用文字承诺，不以精选片估算成功率 |

具体适配写法在prompt-construction.md的“参考动作适配”，接触相位与遮挡承接在choreography.md；研究项目提供问题和控制方式的依据，中文战斗句式是本项目设计推导。

2026-10-04复核公开源码：[ai-film-skills打戏专项](https://github.com/62656456/ai-film-skills/blob/main/skills/ai-storyboard-director/references/fight-design.md)将事件、摄影、播放与剪辑分开判断，对本项目的节奏诊断有参考价值；[higgsfield战斗模块](https://github.com/beshuaxian/higgsfield-seedance2-jineng/blob/main/skills/05-fight-scenes/SKILL.md)提供动作与摄影组织样本，不继承其固定节奏处方；[MapleShaw实验记录](https://github.com/MapleShaw/seedance2.0-prompt-skill/blob/main/experiments/summary.md)保留作者人工反馈，但所读总结标明视频目录为空，不能当成已独立复现的战斗生成案例。这里只比较方法并独立改写，未安装、执行或复制外部skill代码；没有据此认定某项目效果最佳。

2026-10-04补充比较[seedance-motion](https://github.com/Emily2040/seedance-2.0/blob/main/skills/seedance-motion/SKILL.md)及其[导演推导](https://github.com/Emily2040/seedance-2.0/blob/main/references/directing-engine.md)：借鉴目标转成可见行动、后果改变局势、摄影解释当下选择的方法；不采用固定三拍、每短片单动作、其他人物仅微动的通用限制，不将作者经验当作模型保证。未复制代码或整段模板，仍以本项目的双方回应与完整动作链组织复杂交锋。

来源库固定提交为`c526a49bb8695f5333af90b56365dc492e24b6ff`，原文与第三方许可见[third-party-notices.md](third-party-notices.md)。外链只作归属和方法追溯；实际平台能力以任务使用的入口核验，不继承网页中的未知参数。
