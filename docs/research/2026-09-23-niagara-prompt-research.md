# Niagara 粒子行为与战斗视频提示词调研

调研日期：2026-09-23。起点为用户提供的[《解释Niagara粒子提示词》分享](https://chatgpt.com/share/6ab3da1e-8c44-83ec-aa33-76eee857dd9a)。网页检索器只取得标题；通过浏览器读取了完整的一问一答。本文区分官方技术事实、分享中的建议和本项目的创作转译。没有运行 Unreal Engine、下载示例资产或生成视频。

## 结论

“niraga”在该分享中指 **Niagara**。它是 Unreal Engine 的 VFX 系统；在普通视频生成提示词中写 Niagara，通常只是风格/技术意图描述。现有材料不能证明任意视频模型会因此执行 Niagara 模拟，更不能证明准确粒子数、碰撞或寿命得到执行。

对本项目最有用的转译是：**谁在何时何处产生什么 → 沿什么路径运动 → 与何物发生什么交互 → 如何结束 → 留下什么结果**。将它放进已有六轨，比新增一个必填的“引擎标签”更符合项目结构。以下提示词框架和案例是本项目原创设计判断，尚无出片效果证据。

## 对分享内容的核对

| 分享中的观点 | 核对结论 | 项目处理 |
| --- | --- | --- |
| Niagara 不是固定 AIGC 提示语法 | 可采用；官方文档描述的是引擎资产、模块与参数 | 明确区分视频画面描述和实际引擎制作任务 |
| 用生成、运动、生命周期描述粒子 | 有对应的引擎概念；不等于模型支持同名参数 | 将术语翻译成可见动作与时间关系 |
| 比单写“电影级VFX”强很多 | 分享未提供同模型对照、原始输出或重复试验 | 记为待检验假设，不写成已测增益 |
| 数千粒子、精确消散秒数 | 引擎可配置参数；普通视频文本中的精确执行未证实 | 密度优先写疏密与轮廓，秒数标为导演时段意图 |
| 拖尾进一步压成离体月牙剑气 | 这是新增能力和攻击事件，不是拖尾的必然结果 | 只有用户许可离体攻击时才设计该转化 |
| 把十二维固定加入每次输出 | 可作内部检查菜单，全部外显容易挤占动作篇幅 | 简单效果只写关键句，复杂效果按需展开 |
| “不像一团贴图”的效果更好 | 外观可读性与底层渲染技术不能混同 | Sprite、Ribbon、Mesh 和流体各有用途；不用“非贴图”当质量保证 |

分享中的旋转、剑弧、前冲等文字仍需重新核对空间：身体转半周并不自动证明剑尖走了完整圆周。特效沿已写明的兵器路径继承，不替动作补造更大的攻击范围。

## 一手资料与可迁移方法

以下均于调研当日读取。Epic 页面当时显示 UE 5.8 文档；NDC 专项链接固定为 5.6。概念借鉴不承诺跨版本引擎接口兼容。

| 来源与读取范围 | 已核实信息 | 本项目采用 / 不采用 |
| --- | --- | --- |
| [Epic Niagara Overview](https://dev.epicgames.com/documentation/en-us/unreal-engine/overview-of-niagara-effects-for-unreal-engine)，核心组件与生成/更新章节 | System 组织效果，Emitter 生成粒子，模块改变状态，参数提供数据 | 采用“出生—变化—结束”的描述；不虚构引擎调用 |
| [Epic Ribbon Effect](https://dev.epicgames.com/documentation/en-us/unreal-engine/how-to-create-a-ribbon-effect-in-niagara-for-unreal-engine)，教程正文 | 连续条带有专门 Renderer；教程分别配置发射、寿命、宽度和运动 | 将尾迹连续形状与散落颗粒分开；不照搬教程数值 |
| [Epic Niagara Fluids](https://dev.epicgames.com/documentation/en-us/unreal-engine/niagara-fluids-in-unreal-engine)，概览 | 流体模板覆盖火烟等效果，也可烘焙为 flipbook | 烟火强调体积、翻卷与稀释；不用发光点阵代表所有介质 |
| [Epic Collisions](https://dev.epicgames.com/documentation/unreal-engine/collisions-in-niagara-for-unreal-engine)，概览 | 存在多种碰撞实现；GPU 光追碰撞标为实验功能 | 文本只指定接触结果；不声称真实碰撞已经求解 |
| [Epic NDC collision effects](https://dev.epicgames.com/documentation/unreal-engine/combining-collision-effects-in-niagara-data-channels?application_version=5.6)，概览、变量及触发流程 | 示例传递撞击位置、表面法线、表面类型，并在事件位置产生效果 | 对应“接触在哪里、向何方散开、撞到什么材质”；不把性能经验当提示词参数 |
| [Runway Gen-4 guide](https://help.runwayml.com/hc/en-us/articles/39789879462419-Gen-4-Video-Prompting-Guide)，迭代与最佳实践 | 建议从简单运动描述开始，逐项增加细节；该模型推荐正向表述 | 内部详细设计，外部压缩成关键行为；其负向限制规则不推广到所有平台 |
| [Google Veo guide](https://docs.cloud.google.com/vertex-ai/generative-ai/docs/video/video-gen-prompt-guide)，Action 与摄影相关段落；当日重定向到 Google 新文档地址 | 主体动作、环境和相机是可分别描述的维度 | 保持人物运动、特效运动、相机运动的职责；不由本文推断平台时长和接口 |

这些文档支持术语含义与方法来源，不支持本项目的提示词成功率。最终用户输入应遵守所选平台的当前能力，不能把某个模型指南变成通用协议。

## 示例项目比较

| 项目 | 实际读取的依据 | 值得借鉴之处 | 本轮未验证的部分 |
| --- | --- | --- | --- |
| [Epic Niagara Examples Pack](https://www.fab.com/listings/0e188eca-4e54-4fb2-a9ed-d8b8a565e600) | Epic Games 发布的商品说明；[Epic 学习索引](https://www.unrealengine.com/learning/februarys-epic-learning-content-vfx-2d-animation-and-digital-twins)列出配套教学 | 将撞击、尾迹、脚步、附魔分为有触发条件的用途，而非把全部特效叠在一次交手上 | 未下载、未打开 Gallery、未检查蓝图与帧率；不复制其资产或将其作为生成参考素材 |
| [seiko-dev/LeafVFX](https://github.com/seiko-dev/LeafVFX) | 作者 README 的 NS_Leaf 与状态转换说明 | 落叶有积聚、受力、吹散等不同状态，转换保留位置；可启发“已有落叶受扰”的连续性描述 | 未运行项目、未验证引擎版本或性能；不引入代码依赖 |
| [ParticleGen，arXiv:2608.00629v1](https://arxiv.org/abs/2608.00629v1) | 2026-08-01 预印本摘要及提交信息 | 作者研究的是把自然语言转为可编辑模拟配置，再依据渲染反馈迭代；这说明“文本生成引擎效果”是单独的工程链路 | 本轮仅读摘要，没有审阅全文、代码或复现实验；不采信其成绩为本项目效果证据，也不称成熟生产方案 |

选择依据是可定位的一手说明与本项目的关联，不是热度排名。前两项属于可分析的样例项目；ParticleGen 单列为研究线索。没有任何一个项目证明在通用视频模型里堆叠 Niagara/GPU/实时等字样就更有效。

## 从引擎维度转成画面语言

下表是本项目的创作映射，不是 API 字段规范。

| 设计问题 | 可见描述示例 | 常见缺口 |
| --- | --- | --- |
| 来源和触发 | 双刃接触处短促散出火星；剑开始挥动时刃后出现细带 | 挥空也凭空爆出命中火花 |
| 分布和形状 | 刃旁是窄带，外侧只有稀疏细点；脚边是低矮尘片 | 所有效果都变成包住全身的大球 |
| 路径和参照 | 新光带沿当前剑路生长，旧尾迹留在刚经过的空气位置 | 剑已反向，整条旧尾迹也粘着翻转 |
| 分层运动 | 重砂先落，轻尘慢慢向廊外漂；火舌靠热源翻卷 | 尘、石、火、冰共用相同漂浮动作 |
| 接触与回应 | 冰片撞到石阶后弹开，另一人跨向仍未结冰的干燥侧 | 雾的视觉遮挡被擅自写成实体束缚 |
| 衰减与残留 | 停止挥剑后停止生光，旧尾端先暗；地面擦痕留存 | 关停发射就让场内一切和破坏一起消失 |
| 可读性 | 接触瞬间能看清两只持械手；亮部只占交刃附近 | 借白闪跳过交锋因果或重置位置 |

短稿先保留来源、路径、事件、结束。密度、粒径、紊动等只在影响画面或诊断失败时补充。数字是设计目标；模型是否准确执行要由输出验收。普通木杖对练可只有木屑、足尘和衣摆，完全不需要能量、发光或湍流。

## 项目落地与验收

当前项目已有 `beats[].vfx`、`beats[].environment` 与 `sections[].summary.vfx` 等文本位置，适合承载粒子行为，不需要新增第七轨或迁移 Combat Plan 1.2。这里的自由文本仍须语义复核，CLI 不检查粒子物理。

当前运行方法见[粒子行为参考](../../skills/combat-director/references/choreography.md#特效与成像)，媒体检验按[修复循环](../../skills/combat-director/references/review-loop.md)。本报告保留来源与机制分析，不保留历史自生成例稿和实施快照。
