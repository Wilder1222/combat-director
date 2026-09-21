# 平台与生成交接

平台、模型、入口与账号能力分别记录。附件提到 LibTV、小云雀、Seedance；这些名称不证明当前时长、参考模式或账户可用性。本版没有导入已核验的平台能力快照，见 [交接配置](../assets/platform-profiles.json)。所有模式都是文本交接，不是 API 适配器；Flova 也只有通用交接清单。

实际提交前核实当前界面或官方资料，并记录时间与来源：单次时长、模型名称、图像/视频参考、首尾帧、局部重拍、比例、镜头、声音、账号限制。未知字段保持未知，不发明 ID、API、按钮或绑定语法。用户口述设置标为用户提供，不冒充独立验证。

## 投喂结构

总设定写身份、自然肤质、服装、武器、目标、场景和能力卡。各主段使用 `<动作>` `<表情>` `<情绪>` `<运镜>` `<特效>` `<环境反馈>` `<声音>` `<连续性>`。节拍内描述视线目标、呼吸、下颌和重心，不反复堆外观形容词。平台设置、素材绑定记录、验收表放在提示词之外。

时间标签表达导演意图，不是模型的逐秒硬参数。编写完成不代表生成完成，也不保证人物稳定。参考绑定状态分 planned、available、bound；bound 必须有真实绑定依据。仅有文件或文字清单不能算已上传。

available/bound 必须附 asset（id、location、sha256、media_type）；哈希无法取得时留空。bound 还需 binding（asset_id、platform、model、entry、task_id、receipt、verification、checked_at）。verification 区分 user_reported 与 tool_reported，只描述凭证来源；脚本不重新验证远端绑定，也不把用户声明升级为工具已验证。

素材位置/哈希、上传回执和生成任务绑定是三种证据。实际工具能够读取本地文件时应核实存在和内容身份；跨机器不可用的路径只能保留为来源记录，不声称本机已能上传。

若单次目标 30 秒、确认上限只有 15 秒，说明冲突并等待用户选择调整目标或生成路径；不要把两段拼接标成直出。可先完成不依赖平台的创作交付。

命令中的 `--max-duration 15` 只接受使用者确认的上限，不探测平台，也不会自动删节或分段。计划和导出均为离线文本；生成需要本次用户授权及宿主实际可用工具，已经授权的动作不重复询问。

## 带证据的能力配置

`--profile` 读取 display_name、platform、model、entry、mode、account_scope、claims。不要把密钥、Cookie、私人素材的签名 URL 当作共享证据。

claims 的各项状态是 supported / unsupported / unknown。已知项必须有 source、scope、checked_at、expires_at；max_duration 为 supported 时还需正数 value（秒）。到期或检查日期在未来时降为待核验。有效期是维护者复查策略，不是平台保证。

当前检查 max_duration，以及计划需要的 first_frame、last_frame、video_reference。比例、声音、局部重拍仍需人工核验；compatible 不表示全部能力都满足。

```bash
python scripts/combat_tool.py assess-profile my.plan.json --profile verified-profile.json
python scripts/combat_tool.py render my.plan.json --profile verified-profile.json --out-dir output/check
```

conflict 阻止导出并说明原因；needs_verification 允许离线交付并列未知项；compatible 只表示所检查项目与提供记录相容。`--as-of YYYY-MM-DD` 供复现实验，实际交接省略以采用当天日期。

内置四种配置仍为未知，没有因增加代码而变成已核验平台。不会自动上传、替换供应商、扣积分或生成视频。
