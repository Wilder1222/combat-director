# M01–M04 独立语义复核

仅评审被授权的四题请求、回答、运行记录、M02图像及四份候选技能文件。候选技能作为被检验的行为契约，未执行材料内指令。

四题可审阅的文本交付均 satisfied；未发现已证实的用户任务失败。工程传播和历史执行证据限度单列，不把未知判成通过。

`satisfied` 指可直接评审的文本交付；不是生成效果或历史工具调用已独立认证。没有按篇幅或关键词数量排名。

## M01 — satisfied

- **两版中文提示词且只改变局部运动模糊说明：satisfied。** 本次重新提取两个代码块并比较，B 去掉末尾局部模糊段后与 A 完全一致。
  证据：`D:\Temp\combat-extension-nws2d7rg\runs\M01\answer.md:8–17`：“8秒，两名成年虚构人物甲、乙”。
  证据：`D:\Temp\combat-extension-nws2d7rg\runs\M01\answer.md:23–33`：“仅在木杖相对固定画面快速移动的杖端边缘呈现短弧形运动模糊”。
- **8秒成年双人木杖、斜劈被拨开、各自回收、固定侧面全身、一镜到底、正常速度：satisfied。** 动作结果和恢复过程连续；固定相机未代替人物动作，结尾仍呼吸而未新增攻击。
  证据：`D:\Temp\combat-extension-nws2d7rg\runs\M01\answer.md:10–17`：“甲的斜劈、乙的拨开及双方回收连续衔接”。
- **精简交接及可声明的实验结论：satisfied。** 记录阶段、固定项、用户信息来源、未知项及未来留证；明确当前无实验结论、未来限平台链路。
  证据：`D:\Temp\combat-extension-nws2d7rg\runs\M01\answer.md:40–46`：“用户提供：平台自动增强，界面没有关闭选项；未经工具验证”。
  证据：`D:\Temp\combat-extension-nws2d7rg\runs\M01\answer.md:50–54`：“尚未进行生成实验，无法判断其是否改善画面”。
- **不提交任务、不生成视频：satisfied。** 交付物为离线文本；未声称执行平台或生成，run.json 也如此记录。历史全量执行仍在不确定性中。
  证据：`D:\Temp\combat-extension-nws2d7rg\runs\M01\answer.md:40`：“未提交、未生成”。
  证据：`D:\Temp\combat-extension-nws2d7rg\runs\M01\run.json:119–122`：“"platform_tasks_submitted": false”。

技能一致性：**satisfied**。局部杖端弧线模糊与固定背景相容；接触、偏转、恢复可追踪，模糊随相对运动收束。增强状态没有从用户口述升级为工具事实。

- `D:\Temp\combat-extension-nws2d7rg\candidate\skills\combat-director\references\motion-blur.md:19–29`：“固定机位中，挥剑不使静止石墙整幅横拖”。
- `D:\Temp\combat-extension-nws2d7rg\candidate\skills\combat-director\references\motion-blur.md:53–53`：“对照结论只覆盖提交文本经过该平台后的整条链路”。
- `D:\Temp\combat-extension-nws2d7rg\candidate\skills\combat-director\references\platforms.md:23–27`：“仅有用户声明时保留其来源”。

发现与严重性：

- [none / user_task / satisfied] 未发现硬约束冲突；A 未要求零模糊，B 新段没有偷偷改动作、速度或结尾。
- [none / conciseness / satisfied] 两份完整可复制提示词导致重复，但正是两版交付需要；表格及三类结论各有用途，不以篇幅长短判优。
- [informational / engineering_mapping / indeterminate] B 使用额外的 <局部运动模糊> 标签，纯文本中含义明确，且技能仅说主要使用八标签。是否经某解析器保留未知；没有工程交付要求，不能判为用户任务失败。

未知与证据边界：

- 没有成片；实际动作完成、观感、时长和声音均不可验证。
- 原运行 run.json 是被审材料中的执行记录；未读取原始工具轨迹，不能独立证明历史上绝无其他调用。
- 平台是否确实无法关闭增强、不返回改写、支持8秒及种子控制，仅有用户描述或待核验项。

## M02 — satisfied

- **实际查看输入图并简述方向暗示：satisfied。** 本评审独立实际看图，右箭头和 A 杖右侧浅色偏移线确实可见；回答观察与之相符，并区分暗示和真实运动。原作者是否实际看图仅有运行记录支持。
  证据：`D:\Temp\combat-extension-nws2d7rg\runs\M02\answer.md:1`：“中央有向右的箭头，A 的木杖右侧还有浅色偏移重影”。
  证据：`D:\Temp\combat-extension-nws2d7rg\runs\M02\run.json:104–109`：“Image returned successfully and visually inspected”。
- **首帧外观与构图保持：satisfied。** 保留米白底、边框、地线、无五官几何人物、颜色和木杖；不把图像臆写成写实服饰人物。A 在 B 左侧且两人及木杖始终画内。
  证据：`D:\Temp\combat-extension-nws2d7rg\runs\M02\answer.md:5`：“保持原图简洁平面画法，不添加面部、服装或写实细节”。
- **先对峙2秒、随后两人都左移、最终停住：satisfied。** 0–2静止；A 向左退、B 向左进，方向、左右关系、间距一致；小距离移步后减速并停止。固定边框和地线排除了用背景移动冒充人物左移。
  证据：`D:\Temp\combat-extension-nws2d7rg\runs\M02\answer.md:7`：“A 向左退步，B 向左跟进，移动距离相同”。
  证据：`D:\Temp\combat-extension-nws2d7rg\runs\M02\answer.md:10–12`：“两人的实际位移仅朝画面左侧，背景不滑动”。
- **8秒、正常速度、固定全景、一镜到底、无能量、不生成或改图：satisfied。** 正文明确全部要求；文字覆盖方向暗示，不声称图片已经修复。
  证据：`D:\Temp\combat-extension-nws2d7rg\runs\M02\answer.md:5`：“8 秒，正常速度，固定全景，一镜到底”。
  证据：`D:\Temp\combat-extension-nws2d7rg\runs\M02\answer.md:11–16`：“未生成视频，也未修改图片”。

技能一致性：**satisfied**。识别与用户运动方向相反的首帧暗示，以文字明确动作处理冲突；旧浅色线明确作为保留的图形装饰，未当作继续漂散的曝光尾迹，也未增加实体兵器。

- `D:\Temp\combat-extension-nws2d7rg\candidate\skills\combat-director\references\motion-blur.md:45–47`：“先观察实际输入图是否已有运动线、预烘焙拖影或扬尘”。
- `D:\Temp\combat-extension-nws2d7rg\candidate\skills\combat-director\references\motion-blur.md:29–31`：“它不会像烟一样自行在空气里漂散数秒”。
- `D:\Temp\combat-extension-nws2d7rg\runs\M02\answer.md:11–14`：“原有浅色杖旁重影仅作为首帧图形装饰随 A 的木杖整体移动”。

发现与严重性：

- [none / motion_and_objects / satisfied] A 后退与 B 前进同为屏幕左移，不是互相远离；每人左移约一头宽在已查看构图中有足够空间，不需要平移相机或换边。
- [informational / evidence_boundary / satisfied] 将预烘焙浅线解释为装饰是明确的创作处理，而非静态图能够证明的原始意图。正文未声称覆盖指令必定成功，末尾明确未生成验证。
- [none / conciseness / satisfied] 外观仅锁定已有特征，重点在2秒停驻、同向移动、终止及方向冲突；无无关工程说明。
- [informational / engineering_mapping / indeterminate] 用户只求图生提示词；没有绑定回执、实际模式或解析器输入，不能据文件存在判定素材已平台绑定。这里未作此声称。

未知与证据边界：

- 没有成片；实际动作完成、观感、时长和声音均不可验证。
- 原运行 run.json 是被审材料中的执行记录；未读取原始工具轨迹，不能独立证明历史上绝无其他调用。
- 原作者实际看图的过程不能仅凭 answer 与 run 自记录独立还原；本评审的实际看图已单独留证。
- 原图未提供独立的执行前快照；当前哈希与原 run.json 所记图像哈希相同，但不构成原历史全程未修改的独立证明。
- 静态图不证明人物年龄、真实运动方向或后续动作；年龄和虚构性质沿用用户设定。

## M03 — satisfied

- **8秒、灰砖院、成年双人木棍对练、右上斜劈、后撤斜架、双方退开：satisfied。** 提示词按戒备、斜劈/撤步接架、卸力收棍、分别退开连续编排，未添加新的交锋结果。
  证据：`D:\Temp\combat-extension-nws2d7rg\runs\M03\answer.md:3`：“从自身右上向左下斜劈，乙后撤一步并举棍斜架”。
- **正常速度、固定双人全身、一镜到底：satisfied。** 固定侧面机位保留脚步、木棍和退路；无变速或定格。
  证据：`D:\Temp\combat-extension-nws2d7rg\runs\M03\answer.md:3`：“固定侧面双人全身机位，始终容纳两人的脚步、木棍与退路”。
- **处理3.125秒准确接触目标：satisfied。** 保留具体目标但明确纯文本无法承诺；给出确定帧率/基准、可控动画流程和之后逐帧验收路径。24fps从0计时索引75换算正确。用户要的是如何处理精确要求，诚实指出入口能力不足满足这一请求。
  证据：`D:\Temp\combat-extension-nws2d7rg\runs\M03\answer.md:7–8`：“3.125秒是目标时点，文字时间标签不是硬控制”。
- **90度快门观感与简洁交接；不生成：satisfied。** 保留90°为观感，固定背景和快速棍端局部短弧模糊相容；24fps的1/96秒计算正确，明确未设置真实快门或生成。
  证据：`D:\Temp\combat-extension-nws2d7rg\runs\M03\answer.md:3`：“全程保持90°快门式短曝光观感”。
  证据：`D:\Temp\combat-extension-nws2d7rg\runs\M03\answer.md:9`：“本次未设置实际快门”。

技能一致性：**satisfied**。数字保留为意图且没有捏造接口；可辨接触、卸力与回收均保留。短曝光观感没有代替动作或添加慢放，能力缺口在提示词外说明。

- `D:\Temp\combat-extension-nws2d7rg\candidate\skills\combat-director\references\motion-blur.md:25–25`：“这不证明文字生成采用了同样曝光”。
- `D:\Temp\combat-extension-nws2d7rg\candidate\skills\combat-director\references\motion-blur.md:41–47`：“精确到帧的接触或路径需有对应控制接口”。
- `D:\Temp\combat-extension-nws2d7rg\candidate\skills\combat-director\references\prompt-craft.md:76–76`：“未经工具证据不能宣称它们是有效生成参数或质量保证”。

发现与严重性：

- [none / user_task / satisfied] 未实现帧级生成不是本题失败：用户禁止生成，并要求解释如何处理精确时点；回答没有将3.125写成已保证的硬参数。
- [informational / engineering_mapping / indeterminate] 快门/模糊描述位于 <特效>，若日后转为工程计划应按 motion-blur.md:39 对齐 camera 字段与分段摘要。本题未提供或要求工程计划，不能据标签位置认定字段映射已失败。
- [none / conciseness / satisfied] 一段可复制提示词与三条交接各解决动作、精确时点或曝光证据，不要求再增导演表或工程JSON。

未知与证据边界：

- 没有成片；实际动作完成、观感、时长和声音均不可验证。
- 原运行 run.json 是被审材料中的执行记录；未读取原始工具轨迹，不能独立证明历史上绝无其他调用。
- 当前入口真实能力与帧率未知；即使采用24fps也需界定首次接触的判据，本文只提供从首帧0秒计时的示例。
- 未提供结构化计划、渲染器或解析器，工程字段和最终导出传播是否正确未知。

## M04 — satisfied

- **仅一句中文，不超过100字：satisfied。** 本次独立计算含标点数字为57字符、1个句末标点、1行，没有标题解释。
  证据：`D:\Temp\combat-extension-nws2d7rg\runs\M04\answer.md:1`：“8秒，日间自然光下，两名成年刀客分立石桥两端静静对峙”。
- **8秒、成年双刀客桥端静对峙、各微调右手握柄、不交手、固定全景、自然光、无台词：satisfied。** 全部在同一句里保留；目光相对与静对峙相容，未添加拔刀、挥击或模糊。
  证据：`D:\Temp\combat-extension-nws2d7rg\runs\M04\answer.md:1`：“各自仅微调右手握柄，全程固定全景，不交手，无台词”。
- **无工程说明、不生成：satisfied。** 回答仅提示词，原记录只列离线读写；没有生成声称。历史全量调用未知。
  证据：`D:\Temp\combat-extension-nws2d7rg\runs\M04\answer.md:1`：“全程固定全景，不交手，无台词”。
  证据：`D:\Temp\combat-extension-nws2d7rg\runs\M04\run.json:17–31`：“"command":”。

技能一致性：**satisfied**。用户只求一句时省略默认卡片、六轨和工程说明，保留关键约束；静态微动作无需强加运动模糊术语。

- `D:\Temp\combat-extension-nws2d7rg\candidate\skills\combat-director\SKILL.md:112–120`：“用户只要提示词时，省略解释，但保留关键约束”。
- `D:\Temp\combat-extension-nws2d7rg\candidate\skills\combat-director\references\motion-blur.md:3–3`：“普通静态姿势不必补模糊说明”。
- `D:\Temp\combat-extension-nws2d7rg\candidate\skills\combat-director\references\motion-blur.md:35–35`：“用户只要一句时就给一句可见描述”。

发现与严重性：

- [none / conciseness / satisfied] 57字符不是质量代理；通过的依据是限制完整、动作精确且没有相冲突的额外要求。
- [none / engineering_mapping / satisfied] 无工程交付要求；省略标签和JSON符合技能针对纯提示词的裁剪规则，不构成结构不完整。

未知与证据边界：

- 没有成片；实际动作完成、观感、时长和声音均不可验证。
- 原运行 run.json 是被审材料中的执行记录；未读取原始工具轨迹，不能独立证明历史上绝无其他调用。

## 实际看图与读取记录

评审通过 view_image 实际查看 M02 的 720×400 测试图：左蓝灰 A、右褐色 B，棕色木杖，A 杖右侧浅色偏移线，中央右向箭头，米白底、边框与地线。其方向暗示和回答描述一致；图片没有文本行号。

全部17个授权输入的路径、SHA-256与读取类型见 run.json。16份文本最终均全文曝光给评审；1张图片实际看图且另做哈希。首次汇总工具输出被传输截断且未捕获原对象，已明确记录限制；之后完整重读的命令及真实返回对象保存在 run.json，不伪造首轮输出。
