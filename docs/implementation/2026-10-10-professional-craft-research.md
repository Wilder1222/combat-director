# 专业电影、摄影、表演与渲染方法增量

日期：2026-10-10。任务是在现有多画风、详细战斗和连续状态规则上，补专业制作的决策与AIGC适配。实施前原工作树Markdown已逐字保留在本机baseline；旧重构和前轮规则不重置，来源原件、生成资料权威和冻结验收记录不改写。

## 实际缺口与落点

原项目已经有战术目标、感知来源、动作接点、轴线、取景任务、声音范围和多画风，因此本轮不再复制同义清单。新增内容如下：

| 问题 | 实施位置与行为 |
| --- | --- |
| 观众何时知道威胁 | 摄影专题区分共同发现、观众先知、客观观察；机位揭示不改变角色的实际感知或攻击进度 |
| 焦距、机距与透视 | 先选观看关系再定覆盖；校准取景视角、观察位置、画幅与景深关系，不把85mm本身当人物接近或透视压缩原因 |
| 光场与材质塑形 | 风格专题补软硬与反差独立、主补/环境回光、负补光、移动光区和反射；发光主体、环境受照与Bloom分开 |
| 真人/动画表演 | 声音表演专题把情绪词转成对手行动、刺激与选择；眼线/呼吸/重心并行，反射受击不强制先变脸 |
| 表演参考与驱动 | 参考职责新增表演；身份、脸、身体、摄影和双人接点独立，不能把换脸或半身驱动当完整打斗控制 |
| 引擎与交付方案 | 新增按需的渲染画质参考，区分观感、资产/渲染路线、编码显示；Lumen预览、Path Tracer最终动画分别核支持，4K/8K不代替时域或颜色验收 |
| 过期模型能力 | 当前官方页确认Sora 2/Videos API已下线，运行参考改为历史方法，禁止用旧示例承诺当前可执行入口 |

完整提示词只交付所选方法的可见结果，专业制作方案才展开技术条件。基础媒介、人物、兵器、允许能力、事件/结果和用户镜头形式仍优先，新增的光、表演、声音和运镜不偷加招式、伤势、破坏或结局。

## 一手研究与社区材料

本轮来源只作文字/代码研究；没有观看访谈内示例片、下载演示媒体、运行外部项目、安装引擎或付费生成。技术定义、主创个案、教学经验、社区草稿与本项目推导分别看待。以下说明实际读取范围，文字方法不升级为成片成功率。

| 来源与读取范围 | 采用与不采用 |
| --- | --- |
| [ARRI Lighting Handbook第四版](https://www.arri.com/resource/blob/83996/409091c612f371b0c68b41d9dcb636db/arri-lighting-handbook-english-data.pdf)，印刷页5—10、12—17 | 光质、主补、反射和阴影/高光边缘；不固定三点布光、色温与光比 |
| [ARRI ALEXA LF FAQ](https://www.arri.com/en/learn/camera-systems/frequently-asked-questions/alexa-lf-faq)、[Enola Holmes主创访谈](https://www.arri.com/news-en/-enola-holmes-on-arri-large-format/221720-221720) | 读取画幅/视角解释与亲近角色/环境的镜头选择；不复制主创焦段组合 |
| [ARRI Blade Runner 2049照明访谈](https://www.arri.com/news-en/lighting-blade-runner-2049-)、[ASC Ahsoka](https://theasc.com/article/ahsoka-framing-a-rebel-saga/) | 动机光、柔光、移动主光及地表/巨物改变回光；幻想光源也可有明确动机 |
| [ASC Normal摄影师实作](https://theasc.com/article/normal-cinematography-salas/)、[Splitsville摄影](https://theasc.com/article/shooting-splitsvilles-brutally-funny-fight-scene/) | 阅读场景/光 cue、操作员预判、后果覆盖与补充coverage；只吸收观看和阶段印记，不复制频闪、喷淋、破坏或切镜到单镜任务 |
| [Frame.io采访Road House剪辑师](https://blog.frame.io/2024/04/04/bands-and-bar-brawls-editing-action-packed-road-house/) | 原作者谈动作编排、观众知情和声音注意力；声层选择与静音看画面可用于复核，不能以声响补签看不见的接触 |
| [StudioBinder调度](https://www.studiobinder.com/blog/blocking-and-staging-scenes/)、[180度规则课程](https://www.studiobinder.com/blog/what-is-the-180-degree-rule-film/) | 课程分析的人物调度与观看关系；不把任意插入特写当重新授权无依据过轴 |
| [Atlantic官方课程目录](https://atlanticactingschool.org/wp-content/uploads/2026/02/Atlantic-Acting-School-Course-Catalog.pdf)，页12—15、21—22 | 可执行行动、搭档刺激、呼吸/身体与镜头表演；不是固定微表情配方 |
| [Disney动画制作](https://www.disneyanimation.com/process/animation/)、[Animation Mentor面部动画原作者教学](https://www.animationmentor.com/blog/facial-animation-101/) | 读取清楚调度、重量、时序、跟随动作和眼线；眼眉先动属可破的经验法，不硬套突发受力 |
| [Disney视觉开发](https://www.disneyanimation.com/process/visual-development/)、[Look Development](https://www.disneyanimation.com/process/look-development/) | 读取视觉设计目标、形体/颜色/材质分层、毛发/衣料与最终光场迭代说明；转为统一本场视觉语法与逐层校准，不观看或复制示例美术资产 |
| [SAFD舞台打斗词表](https://s3-eu-west-1.amazonaws.com/s3-euw1-ap-pe-ws4-cws-documents.ri-prod/9781032540276/documenting-movement/DM-17-SAFD-Stage-Combat-Glossary.pdf)，第1页 | 配合提示、实际距离、模拟接点与错位；该词表标2022-04-14，不称2026新标准。只作影视模拟与叙事受力区别的背景，不添加通用真人排练流程 |
| [Epic MetaHuman脸/身体解算](https://dev.epicgames.com/documentation/metahuman/metahuman-animator-02-process-and-export-your-animation-in-unreal-engine) | Face Only、Body Only、联合解算与导出分支；控制范围不由身份相似推断 |
| [Epic PBR](https://dev.epicgames.com/documentation/en-us/unreal-engine/physically-based-materials-in-unreal-engine)、[风格化MetaHuman](https://dev.epicgames.com/documentation/metahuman/metahuman-stylized-character-texture-and-material-editing)、[材质贴图](https://dev.epicgames.com/documentation/metahuman/metahuman-materials-and-textures)、[Groom](https://dev.epicgames.com/documentation/unreal-engine/hair-rendering-and-simulation-in-unreal-engine) | 实读物理材质与风格化、微细节、资产贴图/LOD、发丝与发卡；不把8K贴图、SSS或独立发丝词当视频输出保障 |
| [Epic Lumen](https://dev.epicgames.com/documentation/en-us/unreal-engine/lumen-global-illumination-and-reflections-in-unreal-engine)、[Path Tracer](https://dev.epicgames.com/documentation/en-us/unreal-engine/path-tracer-in-unreal-engine)、[CineCamera](https://dev.epicgames.com/documentation/en-us/unreal-engine/cinematic-cameras-in-unreal-engine) | 动态GI/发光噪声、视口累积与最终MRQ、特性支持、朝向和焦点追踪；各渲染分支分别检查 |
| [MRQ设置](https://dev.epicgames.com/documentation/en-us/unreal-engine/cinematic-rendering-image-quality-settings-in-unreal-engine)、[输出格式](https://dev.epicgames.com/documentation/en-us/unreal-engine/cinematic-render-settings-and-formats-in-unreal-engine)、[HDR显示](https://dev.epicgames.com/documentation/en-us/unreal-engine/high-dynamic-range-display-output-in-unreal-engine) | 实读采样、预热、OCIO、EXR/色调曲线与显示输出；不规定全项目统一样本数或将ACES等同HDR文件 |
| [Unity HDRP17.3路径追踪](https://docs.unity3d.com/Packages/com.unity.render-pipelines.high-definition@17.3/manual/path-tracing-understand.html)、[SSS](https://docs.unity3d.com/Packages/com.unity.render-pipelines.high-definition@17.3/manual/skin-and-diffusive-surfaces-subsurface-scattering.html)、[动态模糊](https://docs.unity3d.com/Packages/com.unity.render-pipelines.high-definition@17.3/manual/Post-Processing-Motion-Blur.html)、[HDR](https://docs.unity3d.com/Packages/com.unity.render-pipelines.high-definition@17.3/manual/HDR-Output.html) | 相同观感在另一引擎中的条件对照；不互套UE实现。本轮Epic默认页标UE5.8、Unity比较页17.3/6.3LTS，均非用户已安装版本 |
| [Veo官方提示](https://deepmind.google/models/veo/prompt-guide/)、[Runway Act-Two](https://help.runwayml.com/hc/en-us/articles/42311337895827-Performance-Capture-with-Act-Two) | 读取主体/摄影/风格组织及角色图/视频、gesture、长度差的模式条件；单人半身不签双人全身接点，角色视频循环补时与保留动作冲突需处理 |
| [LTX扩写代码](https://github.com/Lightricks/LTX-Video/blob/main/ltx_video/utils/prompt_enhance_utils.py) | 阅读T2V/I2V系统提示及输入分支；采用时间顺序，不继承150词硬限、图像caption无条件盖过用户请求；未执行代码 |
| [社区摄影草稿](https://github.com/quanluo/ltx-video-prompts/blob/main/prompts/camera-movements.md)、[表演草稿](https://github.com/quanluo/ltx-video-prompts/blob/main/prompts/character-dialogue.md) | 读取5+5个文字草稿，作者自标未独立生成；明确位移/视差/反射和声音层的表达可借鉴，不视为实测最佳方案。仓库仅2 stars，不称热门标杆 |

OpenAI部分优先用官方文档MCP搜索并获取实际正文：[视频页](https://developers.openai.com/api/docs/guides/video-generation)顶端与[下线通知](https://developers.openai.com/api/docs/deprecations#2026-03-24-sora-2-video-generation-models-and-videos-api)明确Sora 2/Videos API于2026-09-24下线，无一对一替代API。[归档提示指南](https://developers.openai.com/cookbook/examples/sora/sora2_prompting_guide)的摄影简报、光色/场景与动作节拍仍可作历史写作方法，旧端点和参数不作当前执行能力。

## 验证与交付范围

[专业方法回归请求](../../tests/fixtures/professional-craft-regression.md)分别试用演员行动、两种观众知情摄影、移动软光/反差、两种焦段/机距、风格化材质、真实渲染/颜色方案、Act-Two输入冲突以及停用服务。独立作者只读当前skill及命中参考完成实际成品，另一审读核原请求、正文与制作边界；不据字段齐全或术语命中计分。

本机原工作树baseline、完整产物、读取记录、修订与指纹保留在忽略的`outputs/current/2026-10-10-professional-craft/`。运行包自含，测试与研究不进入技能；工程与候选包检查仍按[验证用法](../validation.md)。本轮没有生成创作视频、运行引擎、原速看片或实际听辨，文字和工具通过不签摄影、演员表演、时域画质或HDR已经兑现。

本轮实际完成八项请求，产出七版完整提示词及三份非执行制作/输入方案。独立通读发现一处初稿范围归因：Sora回答把测试作者未联网的限制归给原用户请求；中性说明实际读取范围后重新实读，发现关闭，其余文字没有已确认的硬约束违约或概念冲突。原稿、修订和最终产物分别保留指纹，初稿不记成全通过。

最终技能前置、167运行资源预检及内容检查通过；220项工程回归中208项通过、12项因环境条件跳过，另22项媒体工具测试通过。41条发布记录中40条通过，plugin-creator未安装为可选未执行项；168文件候选包重复构建一致。运行Markdown在审读与最终检查期间指纹稳定，实际读取范围按独立报告列示，不由全局哈希推断所有旧专题重新阅读。
