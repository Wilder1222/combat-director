# 多画风、画质与摄影输出优化

日期：2026-10-10。任务是在保留详细攻防与状态接续的前提下，让完整提示词实际交付所选视觉与摄影，而不是只写“CGI、电影感、动态镜头”。实施前已把工作树的现有Markdown字节保存到本机baseline，包含此前架构重构与模型方法改动；没有重置工作树、改来源原件或重算历史审阅指纹。

## 问题与实施

原入口把风格放在动作完成后的按需补充，正文模板只在场景栏末尾提“风格”；风格参考的入口分类主要是CGI/真人。即使资料库有多个风格，普通创作也容易省略材质、光色、效果形态和摄影基调。

现在完整创作先继承用户与素材职责，选择相容的视觉方向，正文开头实际展开媒介/画质、材质或笔触、光色、特效与摄影。短稿可合并栏目，局部改稿保留已有基调；既不增加用户必填表，也不照抄所有候选参数。

画风参考覆盖真人、写实国漫/游戏CG、风格化3D、赛璐璐、2.5D厚涂、水墨、纸偶定格、像素和版画等开放方向；画质沿所选媒介展开，通透、纪实、复古胶片、柔光或平面高对比也可分别选择。摄影分稳定观察、手持、动作牵引、稳定器/滑轨、御空追逐和主观等取向，单镜、多镜与动作速度分别决定。

动作/视觉增强前后核身份、兵器、能力、先后/并发、接点/结果、时长与结局。新增实攻剑雨或涡流必须补机制，视觉尾迹不增加攻击。单镜相机用动作触发、当前位置、开放路线和结束覆盖接续；焦段、微抖、延迟、快门和焦点均按本场意图与入口控制分层。

## 用户参考的采用范围

| 已归档文件 | 实际读取位置及采用 |
| --- | --- |
| [双人第二弹](../../sources/attachments/user-prompts/2-双人打斗第二弹.extracted.txt) | 第1—9行的写实3D/材质/光照/荒野介质、效果与单镜规格；原件与抽取收据分别保持。第9与34行的禁止冻结/末尾定格冲突不整体继承 |
| [时序局](../../sources/attachments/user-prompts/1-时序局_打斗分镜提示词分享.extracted.txt) | 第5—6及107—109行的离线CG、广角和多镜覆盖；不继承源角色与整套剧情 |
| [铜币](../../sources/attachments/user-prompts/5-8.5-铜币转场.extracted.txt)、[7.31](../../sources/attachments/user-prompts/6-7.31.extracted.txt)、[7.30](../../sources/attachments/user-prompts/7-7.30.extracted.txt)、[8.2](../../sources/attachments/user-prompts/8-8.2.extracted.txt) | 开头的CG叠水墨、动作带动相机与连续追踪取向；固定效果套餐和精确时码不升级为通用模型能力 |
| [真人武侠](../../sources/attachments/2026-09-21/grounded-15.prompt.txt) | 第2—3、7、11行的真人媒介、衣料重量和自然光；只取视觉与摄影决策 |
| [Arvin固定来源](../../sources/upstream/arvin-seedance/SKILL.md) | 第2960—2993行的五风格/自定义及选择后展开；生成卡仍从原编辑权威生成，本轮不手改 |

本对话新增的增强包与第二弹前置设定对应；用户现在要求多种风格，因此它作为一类可选写实方案，其他媒介仍保留自身质感。

## 公开项目与提示词方法

以下为2026-10-10读取范围。star取GitHub页面当时显示的约数，仅说明关注度；精选示例和提示文本不能代替本项目视频测试。

| 来源与读取 | 可迁移方法及不采用项 |
| --- | --- |
| [Wan2.2](https://github.com/Wan-Video/Wan2.2)，约17.8k stars；README、扩写代码与[系统提示](https://github.com/Wan-Video/Wan2.2/blob/main/wan/utils/system_prompt.py) | 选择适合的光、色、景别和构图子集，保留主体/动作。默认白天、自动加舞蹈、固定字数和二维取消摄影不作本项目规则 |
| [HunyuanVideo](https://github.com/Tencent-Hunyuan/HunyuanVideo)，约12.6k stars；README的Normal/Master与[扩写代码](https://github.com/Tencent-Hunyuan/HunyuanVideo/blob/main/hyvideo/prompt_rewrite.py) | 原要求保留与视觉丰富度分别核；摄影强化可能损失语义的作者提醒转为增强前后对读。强制英语或以美感改语义不采用 |
| [LTX-2](https://github.com/Lightricks/LTX-2)，约9.6k stars；README与[官方真实提示词指南](https://ltx.io/blog/prompting-guide-for-ltx-2) | 先事件、再时间中的相机/光色变化；车辆擦镜、追随和终点案例启发连续相机起终关系。该入口单段/长度建议不推广 |
| [Runway图生](https://help.runwayml.com/hc/en-us/articles/48324313115155-Image-to-Video-Prompting-Guide)、[摄影提示实例](https://help.runwayml.com/hc/en-us/articles/46749315925395-Camera-Terms-Prompts-Examples) | 尊重首图外观与来势，文本集中变化；环境尘土、逆光与跟拍共同服务运动，不把摄影词表作为必填包 |
| [Veo官方提示指南](https://docs.cloud.google.com/gemini-enterprise-agent-platform/models/video/video-gen-prompt-guide) | 分清主体、动作、媒介、光照、光学和相机；具体表面或线条比风格标签可读，高级摄影词不保证接口控制 |
| [Rylaispirit原skill](https://github.com/Rylaispirit/cinematic-video-prompt-skill/blob/main/SKILL.md)，147 stars；README、SKILL和MIT许可 | 独立选择视觉维度，检查光与天气相容；不整体复制术语库、固定秒数或英语要求 |
| [CyberJ0605原skill](https://github.com/CyberJ0605/cinematic-video-prompt-engineer-skill/blob/main/cinematic-video-prompt-engineer/SKILL.md)，126 stars；README、SKILL、风格模式相关段和MIT许可 | 用观看目的选择镜头与落点；不继承分析式交付、固定运镜配额和默认慢动作 |
| [WanPE论文正文](https://arxiv.org/html/2609.30221v1) | 阅读问题定义、语义一致性及逐阶段规划方法。采用请求在整场传播的思想，不移植模型或自报偏好指标，不据论文给本项目质量打分 |
| [Epic Path Tracer 5.4](https://dev.epicgames.com/documentation/en-us/unreal-engine/path-tracer-in-unreal-engine?application_version=5.4)、[Filmic Tonemapper](https://dev.epicgames.com/documentation/en-us/unreal-engine/color-grading-and-the-filmic-tonemapper-in-unreal-engine?application_version=5.4) | 与本对话前轮技术包核查衔接：真实渲染/色调映射与提示词中的目标观感分别处理，不声称生成入口已经使用这些管线 |

高关注度模型项目与小型公开skill分开称呼，不制作“热门/优秀排行榜”。原仓库许可身份各自保留，社区许可项目不当MIT；本轮只原创转述决策，不复制完整系统提示、词库、角色世界或外部代码到运行包。

## 验证方法与证据边界

[九项完整创作请求](../../tests/fixtures/visual-style-regression.md)覆盖未指定风格、写实荒野一镜到底、二维快切、水墨单镜、复古固定机位、同动作低多边形/木刻双版本、剪纸定格、像素固定机位，以及厚涂柔光/平滑摄影。独立作者从当前skill冷启动写完整复制块，另一审读核原请求与实际正文、视觉区分、动作保留和摄影连续性；不是关键词计分，也不是生成视频质量验收。

本机baseline、完整文字产物、读取记录与受审文件指纹保存在忽略的`outputs/current/2026-10-10-multi-style/`；当前工程和发布报告位于`outputs/validation/`。旧融合证明保持原字节、按固定Git版本审计，新的运行正文不据旧报告补签。真实模型生成、运动兑现、画质/HDR、原速与声音尚需各自的实际媒体证据。

### 本轮实际结果

九项原请求产出十版完整提示词，独立通读原请求与全部最终正文。写实长镜初稿中第三术剑向北上偏转却直接撞地，发现一处路径缺口；局部改成向北下导偏后重新实读，接点、出线和撞地耗尽闭环，原稿与修订稿分别保留。最终没有未关闭的文字发现，不能把初稿记成全通过。

技能前置校验、166运行资源预检与本地内容检查通过；220项工程回归中208项通过、12项因本机条件跳过，另外22项媒体工具测试通过。完整发布记录41条中40条通过，plugin-creator未安装记为可选未执行；候选ZIP为167文件，重复构建字节一致。独立审读记录实际读取的入口/专题和产物指纹，不据全局指纹清单宣称所有旧专题重新实读；最终恢复摄影/审阅两文件原有LF换行，分别记录字节迁移与正文等价，发布检查按最终字节重跑。来源与生成资料没有改写。这里的媒体测试使用合成工具夹具，没有生成或观看本项目创作视频。
