# 主流视频模型文档与案例方法优化

核对日期：2026-10-10。目标是改进Combat Director的分镜决策、战术依赖与参考解析；不做模型排行榜，不把官方精选当本项目出片测试。保留此前架构工作区，修改技能运行正文与本记录，原件、历史验收和资料库生成权威不重写。

## 研究与证据范围

按官方文档优先选取与当前问题相关的教学案例。能力说明决定某输入是否有官方支持，案例提示词展示作者意图，实际取得的媒体才支持所见过程。官方示例未公开总尝试数、完整请求或后期时，不推出成功率和全流程可靠性。

Seedance 2.5双人武打编辑案例取得输入、输出MP4，做全片概览与局部连续帧核查；Kling 3.0单人武术案例取得两种输出，各查看41个概览帧。Sora官方怪物图生与改色案例取得两份GIF，各查看14个采样帧。其他案例本轮读取官方文字和工作流，没有播放嵌入视频。没有发起视频生成，没有原速连续播放或实际听辨；本轮不签速度、声音同步与本技能生成质量。

本机媒体与帧清单位于忽略目录 `outputs/research/2026-10-10-models/`，公开记录不依赖本机素材才能理解方法，也不再分发示例媒体。读者复核时从下列官方来源重新取得文件，核对指纹与区间。

## 官方文档与条件分支

| 官方页面与读取范围 | 版本/入口 | 采用的决策与边界 |
| --- | --- | --- |
| [Seedance 2.0提示指南](https://docs.volcengine.com/docs/ark/seedance-2-0-prompt-guide) | 方舟2.0系列；正文 | 参考、编辑、延长分开；旧代时间和素材经验不作永久通则。 |
| [Seedance 2.5提示指南](https://docs.volcengine.com/docs/ark/seedance-2-5-prompt-guide) | 方舟2.5；页面显示2026-10-09更新；正文与指定案例媒体 | 白模保留的身体结构决定须补的动作；复杂参考和编辑可分阶段，只有制作方式允许才采用。 |
| [Kling VIDEO 3.0](https://kling.ai/quickstart/klingai-video-3-model-user-guide) | Kling Web；正文 | 默认多镜与自定义分镜分别核设置，自然时码不视为真实切点。 |
| [Kling Motion Control](https://kling.ai/quickstart/motion-control-user-guide) | Kling VIDEO 3.0动作控制；2026-03-05文档；正文与指定媒体 | 面部element与主体element控制范围不同；单主体迁移不能证明双人接点与武器保持。 |
| [Runway图生指南](https://help.runwayml.com/hc/en-us/articles/48324313115155-Image-to-Video-Prompting-Guide)、[创建Gen-4.5](https://help.runwayml.com/hc/en-us/articles/46974685288467-Creating-with-Gen-4-5) | Gen-4.5 Web；正文 | 首图暗示来势；多项顺序动作按时长安排，末帧再图生属于续作与剪辑方案。 |
| [Runway Gen-4指南](https://help.runwayml.com/hc/en-us/articles/39789879462419-Gen-4-Video-Prompting-Guide) | Gen-4；正文 | 该代正向与负向限制不推广到所有Runway模式。 |
| [Aleph 2.0提示指南](https://help.runwayml.com/hc/en-us/articles/52150503729171-Aleph-2-0-Prompting-Guide) | Runway Edit Studio；正文 | 编辑目标状态与新增运动分别表达，不能照搬文生/图生提示约束。 |
| [Google视频最佳实践](https://docs.cloud.google.com/gemini-enterprise-agent-platform/models/video/best-practice)、[提示指南](https://docs.cloud.google.com/gemini-enterprise-agent-platform/models/video/video-gen-prompt-guide) | Google视频；页面2026-10-07更新；正文 | 主体、环境与相机分开；一个场景可有连续攻防与多个镜头。 |
| [Veo 3.1导演指南](https://cloud.google.com/blog/products/ai-machine-learning/ultimate-prompting-guide-for-veo-3-1/) | Veo 3.1 / Vertex AI；2025-10-16发布；正文与教学工作流 | 首尾帧、ingredients与时码多镜分别解决不同问题；教学时码不是精确兑现证据。 |
| [Veo延长](https://docs.cloud.google.com/gemini-enterprise-agent-platform/models/video/extend-videos)、[Google编辑](https://docs.cloud.google.com/gemini-enterprise-agent-platform/models/video/edit-videos) | 当前模型分支；正文 | Veo延长与Gemini Omni预览编辑分开；同目录不等于Veo拥有编辑页能力。 |
| [Firefly提示指南](https://helpx.adobe.com/uk/firefly/web/work-with-audio-and-video/work-with-video/writing-effective-text-prompts-for-video-generation.html)、[图生](https://helpx.adobe.com/africa/firefly/web/work-with-audio-and-video/work-with-video/generate-videos-using-images.html) | Firefly Video Web；2026-06-09更新；正文 | 具体动词与摄影；首帧/尾帧使部分控件禁用，不能同时要求互斥设置。 |
| [Firefly摄影参考](https://helpx.adobe.com/nz/firefly/web/work-with-audio-and-video/work-with-video/match-camera-motion-to-reference-video.html) | Firefly Video Web；正文 | 输入用途是摄影，实际采用范围与参考总长分开，不当双人身体控制。 |
| [Luma Ray3 Modify](https://lumalabs.ai/learning-hub/ray3-modify-user-guide) | Dream Machine；2025-12-12；正文 | 身份、关键帧与修改强度分别影响保留范围；旧版尾帧语义不套新版API。 |
| [Luma Ray3.2生成](https://docs.agents.lumalabs.ai/guides/videos/generation/)、[编辑](https://docs.agents.lumalabs.ai/guides/videos/editing/) | Agents API；正文，未见更新时间 | 按姿态/几何/轨迹/面部拆控制；`auto_controls: true`与`video.edit.controls`互斥，其他参数不一概归为互斥。官网与API不同上限不写入通用稿。 |
| [Sora 2提示指南](https://developers.openai.com/cookbook/examples/sora/sora2_prompting_guide)、[正式视频文档](https://developers.openai.com/api/docs/guides/video-generation) | Sora API；正文、两个官方GIF | 提示指南已标归档，写作方法仍可分析；当前参数和输入角色用正式文档核对。 |

Luma当前[官网](https://lumalabs.ai/ray)的搜索收录与[Agents模型页](https://docs.agents.lumalabs.ai/guides/model/)及[API schema](https://docs.agents.lumalabs.ai/api/cli/resources/generations/)在关键帧数量、V2V时长上不一致；官网直抓未完整成功，未判定它们是同入口。正式提交核具体模式schema，不以较大数值宣布能力。本轮未固定这些上限到运行规则。

## 案例解析与选择性迁移

### Seedance：双人素版武打转石堡

来源为[2.5指南的参考图辅助编辑](https://docs.volcengine.com/docs/ark/seedance-2-5-prompt-guide?lang=zh#video-refimage-edit)。输入[武打MP4](https://arkdocs.tos-cn-beijing.volces.com/videos/video-generation/sd25-pe/vid_011_reference1.mp4)，输出[石堡MP4](https://arkdocs.tos-cn-beijing.volces.com/videos/video-generation/sd25-pe/vid_012_output.mp4)。作者意图是换环境与服装、保持原动作节奏。

两片各193个视频帧/24fps。每6源帧概览33帧，局部4.00—6.84秒逐帧69帧；重叠12帧，去重后每片覆盖90个不同源帧。核对相位时用源帧与首帧零点，不把重复采样当新增覆盖。

- frame 99—100 / 4.125—4.167秒：双方前伸手臂与抬掌在上路交汇；这是可见接架关系，不计为身体受击。
- frame 101—104：可见退至下路、再次上路交汇；frame 106—108 / 4.417—4.500秒可见手间间隙与回架。该区间支持短交汇后分离，不能从一次模糊交汇算精确命中次数。
- frame 127 / 5.292秒两片同处切近，frame 150 / 6.250秒同处切宽，主要姿态阶段能对应。frame 144—157近身时手臂重叠与遮挡较多，部分接点未知。
- 约前4秒概览主要是对峙及小幅架势变化。它适合研究局部编辑保留，不据此当高密度战斗节奏标杆；未原速播放，不能精确评价空等与速度曲线。

迁移方法：参考精确可读时优先写事件阶段、保留项和修改差异；编辑后逐阶段对照，而非重写每招后声称原节奏保持。换成兵器战斗仍须核持物、刃线、握点与双方射程，徒手参考不能锁剑。

输入SHA-256 `fb10b0c3a4ebb6892e80207ec42c67568837f92046ff3ce38c323329eefdc576`；输出SHA-256 `835efa1526cdb208affdf9f5e013c423a64ebf3dce5d92a02ef3499609c2310f`。连续帧支持所列相位，未验证全片每一击、原速节奏或声音。

### Kling：单人武术与面部element

[Motion Control指南](https://kling.ai/quickstart/motion-control-user-guide)的Martial Arts Girl案例比较带/不带面部element的输出。两片各245帧/30fps，每6源帧查看41帧全片概览；没有取得原动作输入，两输出分辨率不同，不作为严格对照试验。

采样可见举拳、收架、向画面右侧伸臂，约3.0—3.8秒俯身时头部贴近或出下边界，约4.2—5.2秒起身展掌，之后回撤收手。这里没有对手、兵器或可核查实体接点；只能讨论单人阶段与出画后的重新识别，不能据此证明双人刀剑交互稳定。只看概览也不签速度曲线。

3.0该面部绑定只提供面部身份，不含衣装、发型、妆容或道具；其orientation条件、单element及主体选择方式属于该模式。迁移为实际控制范围审查，而非让所有战斗只留一人或降速。绑定输出SHA-256 `54e03a2e771a8b54ed63c88ed6923ff8e5ae84735e9fa6421ab88fed8baa7699`；未绑定输出 `2f33e116953605258b6aa2d5ca86efea8a2b6e2ec9b19576a67e359b741c5759`。媒体地址另保存在本机来源清单，公开入口可回到官方案例。

### Runway：首图扬尘与静止意图冲突

[Gen-4.5图生指南](https://help.runwayml.com/hc/en-us/articles/48324313115155-Image-to-Video-Prompting-Guide)对比带运动暗示和减弱暗示的汽车首图，说明输入图会影响停住汽车、相机环绕的结果。本轮读取官方说明，未看片。

迁移为开场动势审查：半空伸腿、飞散碎屑与前倾身体不能被无条件接成站稳反刺；调整允许修改的首图或补真实制动，不堆“保持不动”。这是输入与动作相容性的方法，不是禁止高速动作。

### Veo：探险者多镜时码与歌手首尾弧线

[Veo 3.1导演指南](https://cloud.google.com/blog/products/ai-machine-learning/ultimate-prompting-guide-for-veo-3-1/)分别给出探险者拨藤、表情反打、触壁跟随与高位揭示，以及歌手正面到背后视点的连续弧线工作流。均只读教学文字，未观察成片。

迁移为按观看任务选取景：发现来势、理解回应、进入作用范围、读出新局势；每次切镜有信息职责，同一击仍是一个事件。首尾构图作为两端设计，战斗中还须检查环绕通道、对手遮挡、持手和轴线，不能用两个正确姿态签中间运动通过。

### Seedance：白模结构与两阶段道具轨迹

2.5指南区分粗、细白模，说明白模内保留四肢/翅膀却缺动作会产生僵化风险；细白模的坐标、轨迹线和相机标记需清理。复杂帽子轨迹教学先完成轨迹，再编辑匹配角色与场景。本轮只读说明。

迁移为检查控制素材表示了什么、缺了什么。不能一面要求完整肢体逐帧保持，一面只用文字纠正错误姿态。两阶段可以降低同时改变轨迹、身份与环境的负担，但只能在用户允许多次生成/编辑时采用；单次直出保留其约束。

### Runway / Luma：目标外观不等于新增运动

[Aleph 2.0背景火焰案例](https://help.runwayml.com/hc/en-us/articles/52150503729171-Aleph-2-0-Prompting-Guide)区分编辑帧变化与新增的火焰传播；[Ray3 Modify角色驱动](https://lumalabs.ai/learning-hub/ray3-modify-user-guide)结合源表演、角色参考和修改强度。本轮只读工作流，未看片。

迁移为把阵面外观、传播路径和实际作用分开。变化强度不是忠实度保证；人形换兽形或短刀换长枪须重新核身体结构、回收空间、对方处理，摄影保持也不能替代接点保持。

### Sora：改色案例暴露保留项偏差

[正式文档](https://developers.openai.com/api/docs/guides/video-generation)展示冰箱开门、紫色怪物走出，以及仅改橙色的编辑案例。取得[原GIF](https://cdn.openai.com/API/docs/images/sora/sora_monster_original.gif)和[编辑GIF](https://cdn.openai.com/API/docs/images/sora/sora_monster_orange.gif)，各8秒、查看14帧，采样约0.6秒间隔；没有原速播放或音轨。

采样可见：原怪物较大，约4.17秒已在门外；橙色版本形体/毛发比例不同，约4.17秒仍在门口，后续前移位置也不同；原片上门已打开，编辑版所见上门仍闭合。不能把“仅改颜色”的指令当成其他属性全部保持的实证，也不能归因某一词或模型普遍失败。

迁移为局部编辑的双重验收：既核想改的颜色/效果，也核声称保留的身份形体、道具状态、事件阶段和轨迹。通用稿不因这个案例禁止编辑，而是把实际保留范围记录清楚。

原GIF SHA-256 `42adff75dd2746eeb78cfb770d91dfdc76a88735c76d02b21aebc30dca41b5bc`；编辑GIF SHA-256 `97b1545722711353594d040e924e659bff502afccc4d72768ccf2453ddad118e`。GIF只是公开预览，本轮没有取得对应完整请求与原MP4。

## 落实位置

| 能力 | 修改的维护权威 |
| --- | --- |
| 事件先解析、再解释镜头、选择性迁移 | `SKILL.md`、`references/review-loop.md` |
| 战术依赖、失败诱挡、窗口关闭后的后招检查 | `references/choreography.md` |
| 按观看关系选机位、从运动选择必要证据姿态 | `references/camera-and-rhythm.md` |
| 保留完整依赖组后收束负荷，指定同步不串行化 | `references/prompt-construction.md` |
| 按模型/入口拆控制层与证据，编辑核目标及保留项 | `references/video-generation.md` |
| 白模与复杂编辑的条件适配 | `references/seedance.md` |
| 当前来源与媒体观察边界 | `references/sources.md` |

没有更改工程Schema、示例媒体或资料库生成权威。正文内部检查不增加用户表格，也不把所有反事实分支塞进交付提示词。

## 验证记录

编辑完成后执行独立文字前向试用，并对实际产物做语义审阅：

| 真实请求 | 产物与审阅结论 |
| --- | --- |
| 12秒剑对枪过门，佯攻失败，守卫存活 | 六镜合计12秒；先承认封线未开，再实扎/拨杆/短压进身，处理枪尾并跨槛；前提与后招对应。 |
| 10秒9:16单次一镜，三人同步双挡 | 左盾挡枪、右剑拨短剑在同窗；纵深与高度分开来路/接点，分别解除后继续追防，未串行化夹击或编造Seedance参数。 |
| 只有文案和两端静帧描述，适配狭廊长枪/短刃 | 明确没有检查像素与中间媒体；分作者意图、未知过程和设计推导，重算杆路、射程与回应，没有用甩摇代替通过路径。 |

完整文本和根评估记录保存在本机 `outputs/research/2026-10-10-models/forward-test.md`、`forward-review.md`；普通写作不依赖它们。三项在所查文本范围满足请求，投喂长度与模型兑现仍须按真实入口检查。

最终运行 `.venv/Scripts/python.exe -X utf8 scripts/validate_release.py --report outputs/validation/2026-10-10-video-model-release.json` 成功。记录41项：40项执行通过，`plugin-creator`验证器未安装、标为不可用，不记成通过；skill-creator检查实际通过。

- 主测试运行220项：208通过、12跳过。跳过包括2项Windows符号链接条件和10项当前虚拟环境缺Pillow的真实抽帧测试。
- 验证器随后用有媒体依赖的系统Python运行22项媒体工具测试，全部通过，覆盖上述抽帧依赖跳过范围；不把两套运行相加为不重复的测试总数。
- 内容检查通过723个本地引用、28个时间轴案例、30个片段；资料库116卡、1466来源项及生成归属一致。
- 167文件运行包通过解包自含检查和重复构建字节一致性；验证输入指纹与最终源码一致，来源原件指纹不变。
- `git diff --check`通过；本轮修改8份技能权威和本研究记录。工程与文字结果不证明本技能已生成视频，也不代替原速观看与实听。
