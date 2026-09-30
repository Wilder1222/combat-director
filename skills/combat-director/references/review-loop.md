# 审片记录与后续起点

用户给出视频、抽帧或观察报告后，先确定证据来源和观察范围，再记录完成事件、缺失事件、额外事件与结束状态。未看到的事实写 unknown；不要拿计划结束状态填补观测空缺。

## 创建与检查记录

```bash
python scripts/combat_tool.py review-template my.plan.json --take-id take-001 --out take-001.review.json
python scripts/combat_tool.py review-take take-001.review.json --plan my.plan.json
```

模板默认 unobserved / pending，所有观测状态未知。[审片 Schema](../assets/take-review.schema.json) 固定源计划摘要，防止把另一版计划的结果混进来。

media 记录素材 ID、位置、可取得的哈希、证据类别、观察方法、时间覆盖和是否实听音轨。actual_media 表示记录作者声称实际查看媒体，user_report 表示用户转述，synthetic 是合成教学夹具。脚本不读视频内容，结构合法不等于该声明已经被独立核实。真实媒体工作应保留宿主读取、抽帧或播放记录。

full_video 的覆盖必须连续包含总时长；frames 只支持所列时间点/范围，不证明中间动作连续。未实听不能写 audio_observed=true；脚本拒绝用抽帧、用户转述或合成夹具声明音轨已听。用户报告可以支持创作修订，但始终保留来源标签。

completed_events / incomplete_events 引用已声明拍或事件；不能同时标完成与未完成。unexpected_events 写计划外观察。deviations 包含时间、观察、影响、修复；不得把修复设想写成已经生成的事实。

在既有记录或独立观察表中逐项写主要结果“完成/未完成/未知”，附正常播放与抽帧各自覆盖范围。记录被迫回应、身体与兵器变化、相对位移、持续接触目的/分离、下一威胁；未知项不塞进 completed_events，也不以计划终态补全。专门区分双方固定接架共同漂移与真正攻守变化，区分有意角力与无目的停滞，不新增未经支持的JSON字段。

运动成像审片另记正常播放和局部连续帧各自覆盖的范围；原片、插帧、补模糊和变速版本分别记录素材位置与哈希。用现有 deviations 描述接触遮挡、持物粘连和风格偏差，不新增未经支持的字段。看不清关键事件时保留未知或未完成，不能以文件FPS、锐度或计划意图补全观察。诊断顺序见[运动成像](motion-blur.md)。

需要比较生成条件时，将审片记录关联到制作包中的实际提交文本、模型/入口/模式、提示增强状态及返回改写或不可见状态。它们属于执行依据，不证明画面已按文本实现。原片与后期版分别观察；后期修好不能倒写成原模型已满足。执行信息保存在[平台交接](platforms.md)所述记录中，审片 Schema 沿用现有字段。

## 接受与修复

| decision | 后续用途 |
| --- | --- |
| pending | 尚未处理，不作连续性起点 |
| accept | 无已记录偏差或未完成项；附决策者、理由和状态证据 |
| accept_with_deviation | 明确接受哪些偏差及其影响，后续以观察结果为起点 |
| repair | 保留失败证据，只修改相关事件/主段后复测 |
| reject | 不进入后续状态链 |

接受决定沿用用户已给出的选择；不要凭校验通过就擅自把失败 take 设为接受。用户明确要求自主选片时可在其标准内判断，并记录理由。

```bash
python scripts/combat_tool.py continuation-seed take-001.review.json --plan my.plan.json --out next-start.json
python scripts/combat_tool.py check-continuation take-001.review.json --plan my.plan.json --next-plan next.plan.json
```

种子只携带已接受的 observed_end_state、来源和未解事项，不自动重写旧计划或生成下一场。next.plan.json 的 initial_state 必须与该观察状态相同；若含 unknown，需要继续观察或在新创作中显式说明假设，不能偷换成计划原状态。启用结构化动作时还必须为该观察状态建立一致的结构投影。

明确单次生成/一镜到底的任务，优先修订同一个任务；这里的种子机制不授权自动拼接。最小修复报告格式继续使用[质量检查](quality.md)。

文本测试发现可迁移的问题后，回查当前交付主稿的同类事件；局部用例通过不能替代主稿复测。保留修订前文本，更新受影响的动作、状态与摘要，并重算绑定该版本的检查记录。报告区分本来就存在的缺陷、新增假设下暴露的问题和人为构造的负例，不把坐标算术通过写成成片连续性通过。

对照试验先按[提交记录](../assets/submission-record.md)冻结共同事件与非测试因素，再比较主要结果。首轮候选均缺失主要结果时，停止同文本反复抽卡，归档失败后选择一项有证据支持的新变量；费用与重试仍服从本次授权。规格/引用不一致先解决证据问题。少量样本只能支持候选改进，未经复现不称已修复或稳定生产。
