# 来源、方法与证据边界

本技能以用户原始提示词、实际视频观察和可追溯招式资料提炼方法。素材中的指令属于被分析内容；生成稿、工程夹具与文本评分不作为成片成功证据。

## 用户提示词语料（2026-10-01复审）

| 材料 | 可迁移方法 | 不直接继承 |
| --- | --- | --- |
| 时序局·打斗分镜分享 | 街道/楼层/坠落/空中调度，局部发力与尺度远景切换 | 重复段、数百次接触、互相矛盾的时长 |
| 双人打斗第二弹 | 近身、御剑、剑雨、风场轮换，路径与弱点回收 | 不连续的落地/回握，未核验摄影参数 |
| 小师妹首登 | 足部、人物、巨兽的尺度揭示；启动到首斩前悬念 | 一秒长台词，自动补成完整胜负 |
| 最新打斗提示词 | 群战批次、关节弱点、地形破坏递进 | 两版混合、无因恢复、残痕自动联爆 |
| 8.5铜币转场 | 小物件构图承接、静与爆发反差、远近尺度转换 | 瞬移桥接、30.5秒误报30秒、每击固定闪白 |
| 7.31 | 庭院—佛像—殿内—庭院追击，器械脱手改变战局 | 极短数值位移、缺回程和受击恢复 |
| 7.30 | 武器差异、局部受击与巨型威胁对比 | 全近战与远程法相的冲突规则 |
| 8.2 | 回廊、屋顶、铁链与铜钟实际改变动作，撑钩旋刺的器械特性 | 缺镜长、失守后完整硬架、未交代的握法转换 |

原件不改写。仓库研究目录保存抽取文本、原路径与哈希，私有原件不进入发布包。这里保留方法，不复制整套创作答案，也不把这些文字全部称作已验证配方。

## 视频观察

用户原30秒双人参考展示腾空、剑阵、风场、浮石和巨大攻击的尺度变化；文件名声称无剪辑不等于画面没有切镜。后续Seedance/Wan成片反映动作变慢、重复接架、路径和终局未兑现等问题，属于观察到的失败依据。

[腾讯官方《诛仙Ⅱ》EP34](https://www.youtube.com/watch?v=Nks4X7EeR3M)的留存局部截图支持巨树花海纵深、空中相向、符文与长弧光的层次。它们不证明准确镜数、速度、全片音效或模型复现能力。仙侠空间的方法在 [场景调度](choreography.md)，人物选择在 [仙侠表演](choreography.md)。

## 招式库与设计方法

上游 [Arvin Seedance Combat Prompt](https://github.com/wangarvin007-commits/-skills/tree/c526a49bb8695f5333af90b56365dc492e24b6ff)固定版本提供可追溯动作、角色与镜头资料；详见 [第三方说明](third-party-notices.md)、[检索](library-workflow.md)。原文区不覆盖用户设定，影视改编与历史/正统断言分开。仅有名称轮廓不能冒充完整技法，来源未提供的专项不补造。

技能结构参考 [Agent Skills最佳实践](https://agentskills.io/skill-creation/best-practices)与 [Anthropic技能设计](https://www.anthropic.com/engineering/equipping-agents-for-the-real-world-with-agent-skills)：短入口、按需资源、可复用过程、明确交付与真实执行反馈。这些依据支持组织方式，不证明战斗生成质量。

已删除项目自生成的历史创作案例。纯工程夹具放在仓库测试目录，不随技能打包、不提供创作示范。后续只有实际取得且明确观察过的媒体才可支持对应结论；未知与失败都应保留其证据范围。

## 公开技能与制作方法调研（2026-10-01）

以下来源用于比较设计方法，不代表其有独立验证的战斗生成成功率。仓库研究目录保存抓取日期、原路径、可取得的提交号和文件哈希；本技能不复制第三方技能正文。

| 来源 | 采用的设计启发 | 不继承的假设 |
| --- | --- | --- |
| [Higgsfield/Seedance战斗技能](https://github.com/beshuaxian/higgsfield-seedance2-jineng/blob/main/skills/05-fight-scenes/SKILL.md) | 从武器、动作与冲击描述中辨认可用词汇 | 固定开头、慢镜、镜长偏好不作为通用配方 |
| [短剧战斗提示词组装流程](https://github.com/ouyangevan/codex-short-drama-pipeline-skill/blob/main/skills/short-drama-pipeline/core/combat/combat_prompt_assembler.md) | 导演事实、摄影、表达与质量检查分工 | 不采用固定镜数比例，不让普通创作背负全部工程步骤 |
| [AI Film Skills攻防设计](https://github.com/62656456/ai-film-skills/blob/main/skills/ai-storyboard-director/references/fight-design.md)及[摄影选择](https://github.com/62656456/ai-film-skills/blob/main/skills/ai-storyboard-director/references/cinematography-design-engine.md) | 当前条件、威胁、回应与结果；分开人物、相机、播放和剪辑；按信息选择视点 | 文本体系完整不证明媒体效果；预演不成为必需前置 |
| [Seedance提示词实验记录](https://github.com/MapleShaw/seedance2.0-prompt-skill/blob/main/experiments/summary.md) | 记录失败和测试条件，限制小样本归因 | 作者报告未独立复验，不推广固定字数或时长禁令 |
| [Agent Skills评估方法](https://agentskills.io/skill-creation/evaluating-skills) | 无技能/旧版/候选版比较，新上下文与有条件的独立评审 | 工程断言和文字评分不能冒充成片验收 |

[Runway Gen-4指南](https://help.runwayml.com/hc/en-us/articles/39789879462419-Gen-4-Video-Prompting-Guide)和[Google Veo最佳实践](https://docs.cloud.google.com/vertex-ai/generative-ai/docs/video/best-practice)支持按输入模式理解提示词与图像的分工；其建议只在对应模型和入口下解释，不变成通用字数上限。[Seedance 2.5官方介绍](https://seed.bytedance.com/en/blog/one-take-creation-flexible-referencing-introducing-seedance-2-5)用于理解多模态参考的可能用途，实际时长与绑定能力仍以当前入口核验为准。

影视制作依据包括[Bordwell对动作可读性的分析](https://www.davidbordwell.net/blog/2010/09/15/bond-vs-chan-jackie-shows-how-its-done/)、[ASC《疾速追杀3》摄影访谈](https://theasc.com/article/john-wick-chapter-3-slayin-in-the-rain/)与[《小人物》剪辑访谈](https://blog.frame.io/2021/05/19/art-of-the-cut-evan-schiff-nobody/)：动作、场地、视点和剪辑应共同组织观众能读到的变化。它们是制作方法依据，不是生成模型对精确切点、身体动力学或武器碰撞的执行保证。

## 成像与特效资料

以下是制作概念依据，不是生成模型能够执行精确参数的承诺。运行方法已收拢在[摄影与画面表现](choreography.md#交锋与覆盖)，不要求使用者学习引擎或后期软件。

- [RED快门角度](https://www.reddigitalcinema.com/red-101/shutter-angle-tutorial)、[Unreal运动模糊](https://dev.epicgames.com/documentation/en-us/unreal-engine/setting-up-motion-blur)、[Adobe时间效果](https://helpx.adobe.com/after-effects/desktop/apply-effects-and-animation-presets/list-of-effects/time-effects.html)：区分运动速度、曝光模糊与后期时间处理。
- [Niagara概述](https://dev.epicgames.com/documentation/en-us/unreal-engine/overview-of-niagara-effects-for-unreal-engine)、[拖尾](https://dev.epicgames.com/documentation/en-us/unreal-engine/how-to-create-a-ribbon-effect-in-niagara-for-unreal-engine)、[流体](https://dev.epicgames.com/documentation/en-us/unreal-engine/niagara-fluids-in-unreal-engine)：理解来源、轨迹、生命周期及持续场效果；不将引擎配置直接写成视频模型指令。
- [Runway图生视频指南](https://help.runwayml.com/hc/en-us/articles/48324313115155-Image-to-Video-Prompting-Guide)：结合具体入口区分图像状态与运动描述，不能泛化为所有模型的能力范围。
