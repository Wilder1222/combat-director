# 资料库、专题路由与提示词兑现审阅

日期：2026-10-12。回应用户“library和references是否都有用，很多内容输出时无法体现”的问题。全量盘点116张卡的索引、来源元数据、分类与检索，盘点21份专题的职责与入口；抽查各类改编正文、原始来源及近期15秒稿。不是116张卡全部源文的逐句质量认证，也没有全部卡的独立生成或媒体试验。

## 判断

库与专题各有用途，当前主要问题是路由过窄、部分候选说明被泛化，以及选材到成稿之间缺少按类别的兑现检查。没有据此删除资料卡或条件性专题，也不以每份资料都出现在每个提示词里作为成功标准。

资料检索是宿主写作时的只读选材步骤，提示词导出脚本没有自动挑卡并注入正文的过程。文档、卡数和引用链接存在，只能证明资源可用，不能证明每次写作调用或兑现。

## library九类用途

当前七张原创机制卡、109张固定来源卡，共116张；命名记录1466条，其中710条有部分运动路径、166条为描述、590条仅名称。这些是按卡保留的记录，不是1466套独立完整招式。

| 分类 | 卡数 | 能改变提示词什么 | 不该照搬什么 |
| --- | --- | --- | --- |
| design | 5 | 观察截线、接引、抓控、遮线或护送的前提与结果 | 原示例人物、固定成功及原题材能力 |
| abilities | 2 | 已获准的布场、指向能力之来源/路线/预算/结束 | 仅凭招名授予新能力 |
| techniques | 38 | 当前兵器/肢体路径、支撑与作用 | 名称当完整路径或正统考证 |
| characters | 9 | 距离偏好、攻防选择与动作签名 | 用户未选的姓名、外貌、全套能力 |
| choreography | 18 | 前招改变条件、后招接续与节拍 | 固定全部二十手、必胜终结或统一恢复秒数 |
| camera | 15 | 事件触发的取景、机位路线、焦点与接点覆盖 | 固定镜数、角度、拖尾比例及新增命中 |
| effects | 4 | 已设作用的主形、路径、接触变化、照明与退出 | 用色光、面积或爆炸证明伤害与胜负 |
| styles | 5 | 媒介、材料/线面、光色和动态成像 | 引擎词证明执行，画风授权能力 |
| scenes | 20 | 地物对通路、支撑、遮挡、层次的作用 | 为适配卡片替换用户固定场地 |

五张风格卡没有独立水墨卡，二十张场景卡没有宫阙湖面卡；这是资料覆盖范围，并非项目不能创作水墨或湖面。相应写法在[风格专题](../../skills/combat-director/references/style-and-materials.md)及用户参考中支持，零命中时按用户条件原创，不硬换成竹林或木船。

## references逐份职责

“可进入正文”指适用内容转成画面或动作，而非输出文档名；“按需”不表示无用。

| 文件 | 适用任务 | 输出中的作用 |
| --- | --- | --- |
| [prompt-construction](../../skills/combat-director/references/prompt-construction.md) | 普通成稿 | 全局栏目、事件句、时间与逐镜分类 |
| [genre-routing](../../skills/combat-director/references/genre-routing.md) | 识别/改变题材与媒介 | 决定允许动作，约束转换范围 |
| [choreography](../../skills/combat-director/references/choreography.md) | 交锋与目标编排 | 动力、回应、窗口、受力、回收及下一状态 |
| [camera-and-rhythm](../../skills/combat-director/references/camera-and-rhythm.md) | 取景、单镜/多镜与节奏 | 实际观看路线、范围与切点 |
| [style-and-materials](../../skills/combat-director/references/style-and-materials.md) | 选风格与视觉兑现 | 具体表面/线面、光场、作用变化 |
| [sound-and-performance](../../skills/combat-director/references/sound-and-performance.md) | 表演与声音 | 判断、握持/身体响应与声源阶段；静音任务约束不必复述技术规则 |
| [movement-and-projectiles](../../skills/combat-director/references/movement-and-projectiles.md) | 追逐、御空、离手、投射、换区 | 可达路线、在途顺序与结束 |
| [powers-and-formations](../../skills/combat-director/references/powers-and-formations.md) | 屏障、阵法、巨敌、能力对抗 | 功能、尺度、接点、局部失效与代价 |
| [clones-and-multi-combat](../../skills/combat-director/references/clones-and-multi-combat.md) | 分身、围攻、协同 | 人数、职责、并发与友军通路；双人任务通常不用 |
| [reference-and-iteration](../../skills/combat-director/references/reference-and-iteration.md) | 有素材、复刻、转换、续接 | 绑定与适配范围，素材对应结果 |
| [xianxia-vocabulary](../../skills/combat-director/references/xianxia-vocabulary.md) | 仙侠表达缺具体形态 | 补当前机制的可见词句；不必用满术语 |
| [library-workflow](../../skills/combat-director/references/library-workflow.md) | 候选选材与点名来源 | 将各类候选转为相应事件/摄影/视觉句 |
| [video-generation](../../skills/combat-director/references/video-generation.md) | 入模写法、绑定与改写 | 投喂正文及参数分层；不要求提示词复制接口知识 |
| [seedance](../../skills/combat-director/references/seedance.md) | 指定Seedance模式 | 对应入口的素材和正文适配 |
| [generation-execution](../../skills/combat-director/references/generation-execution.md) | 实际生成 | 授权、任务、预算和回执；不塞进创作正文 |
| [rendering-and-quality](../../skills/combat-director/references/rendering-and-quality.md) | 实际渲染/规格或复杂画质诊断 | 制作方案与成片诊断；普通画质词由风格页承担 |
| [review-loop](../../skills/combat-director/references/review-loop.md) | 素材审阅、失败修复、续作 | 诊断与修订正文，证据分层 |
| [video-evidence-tool](../../skills/combat-director/references/video-evidence-tool.md) | 本地视频抽帧 | 观察工具及范围记录，不是模型提示词 |
| [contract](../../skills/combat-director/references/contract.md) | 可选结构化工程导出 | 状态/字段与审片绑定；纯文本写作不用读全部契约 |
| [sources](../../skills/combat-director/references/sources.md) | 方法核查与维护 | 来源与适用范围，不重复进每个复制块 |
| [third-party-notices](../../skills/combat-director/references/third-party-notices.md) | 溯源、许可与再分发 | 归属边界，不作为画面内容 |

没有发现需要因“未写进普通提示词”而删除的无主文件。专题有路由或工具/维护职责；内容是否能改善每次输出，需对具体任务继续验证。

## 明确问题及本轮修复

1. 主入口只把资料检索挂在仙侠措辞/指定招式，检索页又明确写“普通创作无需查库”。现在完整新创作需要自定打法、摄影、场景或视觉方案时主动查看对应候选；完整用户参考与局部改稿按范围处理。
2. 11张摄影模式卡共用同一改编摘要，5张风格卡也共用同一摘要。其原文不同，但默认检索无法提供足够选择信息。现在由[生成器](../../scripts/build_arvin_library.py)为16张卡分别维护具体可用方案，不直接改生成卡。
3. 原分类导航只有标题、层级与命名数，缺少选卡用途；卡的公共转写句还把风格/摄影都称为“所选动作”。现在[导航生成器](../../scripts/arvin_items.py)输出各类正文职责和卡片用途，公共转写按动作、摄影、视觉分别处理，删去同卡重复的检索规则链接。
4. 检索结果只是关键词候选，既没有语义搜索，也不等于适用性批准。当前查询仍保持只读和候选边界；新增用途摘要后，“缺口、承重、腰侧、汗珠、赛璐璐、霓虹”六组真实查询从零命中变为各一张对应候选。来源身份、行段、命名记录与详情等级未改变，1466条目文件字节一致。
5. 成稿缺少按资料类别的兑现检查。现在正文与审阅明确检查选定内容实际改变哪条事件/摄影/视觉句；边界专题可只约束状态，创作方案不能只落为卡名、泛句或禁令。零命中不强塞不相容预设，不要求每片用齐九类。

## 真实文字试用与验证

本机证据保存在 `outputs/library-reference-audit-2026-10-12/`：全量卡/专题清单、前后检索、备份、两份完整文字试用、所选资料与正文对应、工程回归及当前指纹。试用由本轮主代理完成，未冒充独立代理评测。

- 原15秒湖面稿保持八镜与全部动作/时间/终态，仅在既有导偏中兑现3D材料转面，在原抵盾处兑现接点双色、金纹断开与局部照明退出。摄影全景收尾的方法原稿已体现，不再为证明引用重复增招或运镜；不采用木船场景和观察后二次截线卡。
- 新12秒真人木船争路稿采用船卡的横摇/栏杆支撑、真人格斗的体重/衣料响应、兵器取景和连续跟随，所有支撑与地物进入具体事件。船卡的油画媒介未迁移，攻防为本场原创，不宣称出自源文正统套路。

纯结构/检索测试不证明模型会稳定调用这些卡，文字试用不证明视频质量。后续应按实际任务复看输入、资料选择、完整发送与新媒体结果。

当前验证：148份技能Markdown均从入口可达，无失联卡或专题；来源摘录块保持，条目文件字节不变。14项资料库回归通过，其中新增两项覆盖摄影决策和媒介特征检索。完整工程报告40项检查通过，1项可选plugin-creator工具不可用；222项项目单测完成、12项跳过，另22项媒体工具测试通过。内容检查通过793个本地引用、28个原时间轴案例和30个片段，技能格式有效，169文件包独立解包与重复构建通过。受检运行输入与当前指纹一致；这些结果不证明本轮生成媒体效果。
