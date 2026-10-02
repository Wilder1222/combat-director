# 平台交接与执行证据

仅在实际平台交接、绑定或生成时读取。通用写作不依赖平台；模型、版本、入口和账号能力分别核实。以当前界面或官方资料确认时长、参考模式、比例、声音和正文长度限制，记录日期与来源。用户口述标为用户提供，未知不补成支持。

## 准备正文与素材

先按实际输入模式组织已完成的六项设置与动作正文，不用平台链接代替写作：

| 输入模式 | 正文怎样写 | 需要核对 |
| --- | --- | --- |
| 纯文本 | 写清人物、武器、空间与光线的稳定设定，再按时间段展开动作 | 六项完整，不虚构存在参考图 |
| 人物/外观参考 | “{角色称呼}采用{用户指定素材}中的{可见外观}”，同时写出关键辨识与本场动作 | 映射到真实素材；图像未提供的武器/能力是创作设定，不说成图中事实 |
| 首帧输入 | “开场保持{图中位置、握持、支撑和正在发生的状态}，随即{从该状态能接出的动作}” | 不跳回通用站姿；身份图被入口当首帧时也要处理其实际姿态 |
| 动作/摄影参考 | 将选中的“{重心转换/攻击回应/相机覆盖关系}”改写成本场具体动作 | 不只写“照视频打”；新人物、兵器与场地仍需成立 |

正文沿用已定事件，只调整当前入口支持的表达。转换后对读角色、兵器、顺序、路径、结果及镜头要求；不能借“适配”擅改胜负或删关键桥接。不套统一字数上限、负向语法、@引用或某一代模型的建议。超限先删重复，冲突仍在则说明具体限制。

素材按[参考用途](review-loop.md#素材与观察)区分身份、首帧、动作、摄影和场景。参考状态planned、available、bound不同：文件存在不证明上传，引用不证明绑定。需要真实核对人物映射、拟提交引用和任务历史的对应；跨机器路径无法读取时不声称可以上传。

已有授权范围内完成提交，不因通用清单重复询问。单次目标30秒而入口仅支持15秒时，不能擅自拆段或把拼接称直出；先完成可交付文本，说明须调整的目标或路径。写提示词本身不授权消费和生成。

## 留下足以诊断的执行记录

使用[提交记录](../assets/submission-record.md)，只填实际可得内容，不存密钥、Cookie或私人签名链接。

- 作者拟提交正文、当前编辑器草稿、任务历史输入、返回扩写分开；后两者不可见就注明。当前节点或开关不能倒推旧任务。
- 素材身份与用途、实际绑定、模型入口、已知设置、提示增强/AutoLink状态及依据分别记录。重复引用先核对歧义，不据此直接断言坏片原因。
- 请求规格、任务回执和下载原片探测值分开记录时长、尺寸、FPS和音轨。出现差异先找版本/任务关系，不猜测降级机制。
- 提交成功只证明调用结果，不证明每个动作、身份和镜头执行。素材哈希、上传回执和生成绑定也不能互相替代。

设置或扩写不可见时，实验结论限于平台链路，不声称隐藏输入只变了一个词。整体方案比较与单因素复测的差别见[审片](review-loop.md)。

## 可选JSON证据与能力配置

以下仅用于已有工程计划，纯文本无需补这些字段。available/bound素材附asset（id、location、sha256、media_type），取不到哈希可留空；bound另附binding（asset_id、platform、model、entry、task_id、receipt、verification、checked_at）。verification区分user_reported与tool_reported；脚本不重新访问远端验证声明。

`--platform`只选择通用交接清单，不是经过实测的模型适配器。内置[能力配置](../assets/platform-profiles.json)仍为未知。`--profile`读取display_name、platform、model、entry、mode、account_scope、claims；已知claim必须有source、scope、checked_at、expires_at，max_duration支持时还需正数value。过期或未来日期降为待核验，有效期只是维护策略。

当前脚本只核对max_duration和计划需要的first_frame、last_frame、video_reference，其他项目另核实。compatible只表示已检查项相容，needs_verification允许离线交付并列未知，conflict阻止导出。`--max-duration`采用使用者已确认的上限，不探测平台；`--as-of`用于复现，实际交接默认当天。

```bash
python scripts/combat_tool.py assess-profile my.plan.json --profile verified-profile.json
python scripts/combat_tool.py render my.plan.json --profile verified-profile.json --out-dir output/check
```

这些命令在技能目录执行，都是离线检查/导出，不上传或生成。完整结构及版本复核见[工程契约](contract.md)。
