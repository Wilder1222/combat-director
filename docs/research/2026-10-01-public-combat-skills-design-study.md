# 公开战斗与视频创作 skill 设计调研

调研日期：2026-10-01。范围：6 个公开仓库的目录结构及相关源码，交叉核对模型官方资料、电影创作者访谈和 Agent Skills 文档。现有 combat skill 只作为问题背景，不作为有效性证据；未安装或执行外部 skill，未调用付费生成，也未复现外部战斗成片。

## 结论

本轮找到了有价值的设计部件，尚无依据推荐一个已经在本项目条件下验证优于其他方案的“最佳战斗 skill”。应分别评价方法可读性、实现完整性、作者反馈与真实媒体证据。星标、文件数量、术语丰富度和模型自评都不能替代出片结果。

最值得迁移的组合是：事件与摄影分别设计，参考素材明确分工，按实际模型入口组织执行提示词，最后用无 skill、旧版、新版三组结果检验收益。这比继续扩充招式词库更接近当前问题。

## 1. 仓库比较

### A. beshuaxian/higgsfield-seedance2-jineng：直接战斗提示词技能

主要文件是 `skills/05-fight-scenes/SKILL.md`。组织方式偏向百科：招式、机位、环境、冲击效果和示例。优点是帮助补充动作词汇；风险是固定开场钩子、慢镜和蓄势循环可能占掉交战时间，而且其中偏好长镜的建议不适合直接覆盖本项目的多机位要求。[战斗模块源码](https://github.com/beshuaxian/higgsfield-seedance2-jineng/blob/main/skills/05-fight-scenes/SKILL.md)

迁移判断：作为按需动作素材索引有价值，不采用其整套默认节奏，也不把“模型善于某动作”的陈述当作本项目已验证能力。本轮未核验其示例与对应原始生成视频的配对证据。

### B. ouyangevan/codex-short-drama-pipeline-skill：导演到执行提示词的分层

战斗部分将意图、动作、反馈、摄影、提示词组装和质检拆开。最有价值的是内部导演信息不全部进入执行正文，且不同执行条件有不同组织方式。[提示词组装源码](https://github.com/ouyangevan/codex-short-drama-pipeline-skill/blob/main/skills/short-drama-pipeline/core/combat/combat_prompt_assembler.md)

它也固定了普通镜长、动作事件数量和时间分布比例，并设置文本评分阈值。这些属于作者处方，不能直接迁移成自适应分镜规则。[导演层](https://github.com/ouyangevan/codex-short-drama-pipeline-skill/blob/main/skills/short-drama-pipeline/core/combat/fight_director_layer.md)、[质检模块](https://github.com/ouyangevan/codex-short-drama-pipeline-skill/blob/main/skills/short-drama-pipeline/core/combat/combat_qc.md)

迁移判断：借职责分离与按条件组装的思路，不引入大型必填表，也不以数字合规证明战斗节奏。

### C. 62656456/ai-film-skills：事件、摄影与实现分开

战斗专项分别处理交锋条件变化、身体后果、空间和时间；摄影模块要求确定观看对象、路径与终点，已定镜头转换成提示词时避免重新导演。[打戏专项](https://github.com/62656456/ai-film-skills/blob/main/skills/ai-storyboard-director/references/fight-design.md)、[摄影设计](https://github.com/62656456/ai-film-skills/blob/main/skills/ai-storyboard-director/references/cinematography-design-engine.md)

仓库有视频文件和实验性白模模块；白模声明只验证自身执行的空间与运动，不保证视频模型复现。本轮只核验文件存在与说明，没有播放并验证那些成片。[实验性预演入口](https://github.com/62656456/ai-film-skills/blob/main/experimental/whitebox-previs-executor/SKILL.md)

迁移判断：在本轮样本中，其动作/摄影分责较适合我们；不整体引入所有模块，不把预演变成用户获取提示词的必经步骤。

### D. MapleShaw/seedance2.0-prompt-skill：按输入类型分流、根据反馈修订

它为文字、图片、分镜板等输入安排不同路径，保留作者手动生成后的反馈。记录中有极简策略表现不佳的样本，并补充了适用边界。[入口源码](https://github.com/MapleShaw/seedance2.0-prompt-skill/blob/main/SKILL.md)、[实验反馈](https://github.com/MapleShaw/seedance2.0-prompt-skill/blob/main/experiments/summary.md)

迁移判断：学习承认失败、保留边界和区分输入条件的做法。作者评级不是独立盲评，题材与当前战斗也不同；不迁移其字符配额、短片必须只做一种内容的限定或与其他场景有关的审核推断。

### E. keizman/seedance-skill 与 songguoxs/seedance-prompt-skill：素材角色与调用语法

二者说明如何让图片分别承担人物、首尾帧或场景用途，让视频承担动作、镜头或节奏用途。[keizman 源码](https://github.com/keizman/seedance-skill/blob/main/zh/SKILL.md)、[songguoxs 源码](https://github.com/songguoxs/seedance-prompt-skill/blob/master/.claude/skills/seedance/SKILL.md)

迁移判断：适合作为素材绑定设计的参考，不能承担完整的战斗编排。版本参数需重新核验；示例时间段和收尾习惯也不能作为通用模板。书写 `@素材` 与平台实际完成绑定是两件事。

## 2. 官方指南指出：提示词组织依赖输入模式

Runway Gen-4 官方建议先确定主要运动，再逐项迭代，图生视频避免重复描绘图中已明确的信息。这适用于其指定模型与工作方式，不能推导出所有视频模型都只适合极短提示词。[Runway 官方指南](https://help.runwayml.com/hc/en-us/articles/39789879462419-Gen-4-Video-Prompting-Guide)

Google 的图生视频指南同样区分视觉起点与后续运动；其对文生视频的表达建议又包含主体、摄影、动作与环境。因此详细与简洁应由素材承担了多少信息决定。[Google 视频最佳实践](https://docs.cloud.google.com/vertex-ai/generative-ai/docs/video/best-practice)、[Veo 提示指南](https://cloud.google.com/blog/products/ai-machine-learning/ultimate-prompting-guide-for-veo-3-1/)

Seedance 2.5 官方资料将动作参考与白模参考列为控制手段，并承认复杂运动和多主体交互仍有改进空间。它说明存在文字之外的控制途径，不保证当前用户入口具备相同功能或能精确执行每次接触。[Seedance 2.5 官方介绍](https://seed.bytedance.com/en/blog/one-take-creation-flexible-referencing-introducing-seedance-2-5)

Wan2.2 官方代码有可选提示词扩写流程。因此必须区分原始正文与模型最终接收的正文；这不是对用户所称 Wan3.0 的实现推断。[Wan2.2 生成代码](https://github.com/Wan-Video/Wan2.2/blob/main/generate.py)

**对本项目的推论**：入口应区分三种条件，而不是交付同一种长文本。

| 实际输入 | 提示词设计重点 | 不能默认成立 |
| --- | --- | --- |
| 文字或仅有人物外观参考 | 自主设计完整攻防与摄影，外观映射明确 | 外观图能提供攻防速度、镜头路径或有效初始站位 |
| 已有明确的首帧/关键状态 | 从可见状态继续动作，检查该构图是否支持目标 | 静态关键帧能证明中间运动可达 |
| 已绑定动作/运镜视频或预演 | 提取并指定控制维度，文字补差异与结果 | 视频所有信息都应照搬；已引用即表示平台绑定正确 |

没有模型信息时仍可产出通用详细稿，不阻塞用户四项输入入口；不虚构引用标签、平台控制项或能力保证。发现执行条件不足时指出具体未受控项。

## 3. 专业动作创作对 skill 的启发

David Bordwell 对香港动作片的分析强调构图与剪辑如何让动作关系清楚；清楚的画面也可以非常短。因此不能将可读性等同于长镜或慢动作。[Bordwell 原文](https://www.davidbordwell.net/blog/2010/09/15/bond-vs-chan-jackie-shows-how-its-done/)

《John Wick 3》的摄影访谈呈现了动作、摄影和场景协同设计的方式；《Nobody》剪辑师 Evan Schiff 的访谈则说明场地与编排会影响可用切点，不能在完成动作之后随意套一种剪法。[ASC 访谈](https://theasc.com/article/john-wick-chapter-3-slayin-in-the-rain/)、[剪辑师访谈](https://blog.frame.io/2021/05/19/art-of-the-cut-evan-schiff-nobody/)

《The Continental》的创作者介绍了事先拍摄、剪辑动作预演来协调正式拍摄的流程。对 AI 创作可迁移的是先显式解决运动与观看关系；不意味着本项目必须制作昂贵预演。[ASC 动作预演访谈](https://theasc.com/article/three-nights-the-continental/)

据此提出三个本项目设计判断，均需新视频验证：

- **以完整交换组织观看。** 同一段可以包含连续数招，观众需要看出主动权或位置发生什么变化；动作细节服务这个变化。
- **摄影拥有自己的表达任务。** 镜头可以追上、落后、提前等待或转交主体，但每种选择都要明确观众获得的威胁、空间或结果信息。
- **强度来自可见压迫和回应。** 缩短镜长、加快摄影机、增加特效都不能单独证明角色出手快、对手来不及应对。

## 4. 真正有效的 skill 还需要“没有它会怎样”的比较

Agent Skills 文档强调优先写可执行流程、按需披露知识，并在独立上下文中比较有无 skill 或新旧版本；可观察断言与人工判断各有用途。[编写最佳实践](https://agentskills.io/skill-creation/best-practices)、[输出评估](https://agentskills.io/skill-creation/evaluating-skills)

对战斗视频需要两层实验，不能混成一次模型自评：

1. **创作层**：相同用户输入与素材，分别由无 skill、旧版、新版产出提示词。盲评用户约束、交锋变化、摄影可执行性和信息负载。不同运行不继承本次研究和已写好的答案。
2. **媒体层**：在固定模型、模式、素材绑定和已知设置下，用候选提示词实际生成；隐去版本身份后比较正常播放的紧迫感、接点、受力和空间。抽帧辅助定位，不能取代正常播放。

还应区分“整套 skill 带来多少收益”和“某项机制为何有效”：前者比较完整输出，后者固定主事件，只改动作表达、摄影表达或参考绑定其中一项。避免同一实验同时改动作、场景、模型，再给某条规则记功。

当前失败视频可作为失败证据。由于实际提交文本、最新模型/模式尚不明确，它不能直接成为同条件因果实验的旧版基线。没有真实生成结果的候选不保存为历史成功案例；工程测试仍与创作参考隔离。

## 5. 调研后对上轮方案的补充

上轮“主要结果→攻防变化→移动→摄影→正文→返修”可以保留，但还不足以解决执行偏差。建议补齐下列职责，优先改现有文件而非扩建复杂系统。

### 5.1 素材与控制方式进入入口

在 `SKILL.md` 和 `prompt-craft.md` 增加简短分流：素材控制外观、起始状态还是运动；模型/入口已知时按已核实能力组织。完整规格仍放按需平台资料，通用创作不强迫用户先选平台。

### 5.2 区分编排与提示词表达

内部先有一份稳定的动作与摄影事实；写正文时选择需要说明的内容，不能在改写、精简或平台转换中临时更改攻击对象、路线和结尾。借鉴分层思想，不照搬大型 Schema 或固定镜长。

### 5.3 四类速度分别设计

在现有切镜/摄影文件中明确：人物动作速度、摄影机速度、播放速度、切镜频率。四者可以协作，不能互相冒充，也无需逐段全部声明。优先修复实际出手、回应和接续；特写及微慢仅服务所选关键点。

### 5.4 攻防需要差异，摄影也需要选择

对主要转折比较两种真正不同的观看方式，例如同框展示即时反制与沿来刀转交防守者。只在关键位置比较，不输出每镜多方案，不将比较结果固定成某种通用镜头顺序。

### 5.5 故障定位先决定修改层

| 现象 | 先检查 | 不宜直接做 |
| --- | --- | --- |
| 开头等待 | 开画动作相位、首帧状态及绑定模式 | 把高速形容词再写一遍 |
| 同姿态反复 | 防守之后的结果、后续机会和招式轮廓 | 只增加镜头数 |
| 人物共同漂移 | 主动移动与被迫退让、相对距离变化 | 放大背景视差 |
| 接点不清 | 实际距离、取景与遮挡、生成偏离 | 堆火星或震屏 |
| 有破坏无力感 | 作用对象、传力方向、身体和支撑变化 | 再增加裂纹和云浪 |
| 镜头与文字不符 | 既定摄影、最终提交正文、入口支持及素材参考 | 立即新增更复杂摄影术语 |

### 5.6 外部规则明确取舍

采用：参考用途分工、导演信息与执行正文分离、攻防/摄影分责、真实失败反馈、独立基线对照。

不采用：固定两秒钩子、每镜固定姿势数量、固定动作时间比例、统一字数上限、每招一套完整特效、默认全片长镜、文本高分视为出片成功。

条件采用：关键帧、动作视频、白模、局部再生成与多段制作。由用户意图和当前能力决定；不能自动把单条 15 秒测试改成多段拼接。

## 6. 交付与证据索引

- 本报告是独立调研与设计建议，未执行运行技能修改。
- 6 个仓库共 17 个所读文件的 URL、字节数和 SHA-256 记录在 [来源清单](evidence/public-combat-skills-2026-10-01/source-manifest.json)。部分仓库已固定提交；其余提交查询受 GitHub API 速率限制，以分支 URL 与文件哈希记录，不伪称全部固定版本。
- 网页缓存和实时分支内容可能存在行数差异；具体源码判断优先采用本轮读取版本。目录中视频文件的存在不证明本轮观看、提示词对应关系或质量。
- 官方指南说明特定模型与模式的建议；专业摄影资料说明创作方法；作者实验说明作者报告。三者均不能直接充当本项目复现证据。
- 下一阶段应把上述候选方法落实到最小核心流程，再做独立创作对照与获授权的媒体复测。保留镜数自适应、详细可复制输出、开阔战场和四项输入入口，不恢复历史未验证案例，不做 LibTV 适配。
