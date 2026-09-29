# 0.9.1 验证报告

日期：2026-09-24。软件0.9.1、卡索引2、条目索引1、Combat Plan1.2；Windows x64、Python3.13.3。落实motion深化计划P1的规则与交接增量，原0.9.0资料库WP06独立创作评估继续在冻结条件上进行。历史见[0.9.0报告](validation-0.9.0.md)。

本次重新运行完整发布流程，**41项通过**；单元测试 **95项，93通过、2跳过**。命令输出、来源及187个运行文件哈希见[机器证据](../implementation/validation-0.9.1.json)。本次增量见[成像交接说明](../implementation/motion-blur-integration-0.9.1.md)，资料库实现及来源分级见[0.9.0交付说明](../implementation/library-items-0.9.0.md)。

| 检查 | 证据与结论 |
| --- | --- |
| 条目来源 | 1,466项、59张卡；全部证据行与表头对应固定源文，名称/描述/路径分别标记 |
| 缺项与版本 | 小内返保持名称资料；乌龙摆尾可定位动作行；同名白蛇吐信及别名冲突分别返回 |
| 读取范围 | items/item只读索引，选中条目与整卡改编分区；默认show保留归属和许可，原文可展开 |
| 兼容 | 116张卡与全部旧ID保留，catalog2逐字段不变；Python完整搜索/读卡API保持原默认语义 |
| 紧凑输出 | 卡搜索默认第一页3,377字符；逐招第一页4,519字符；原始输出和数据读取记录见[测量](../implementation/library-retrieval-0.9.0.json) |
| 生成管理 | items与十份导航均纳入来源、漂移、暂存和回滚；未重建或手改产物不能绕过正式构建 |
| 既有内容 | 六套原计划与两套motion计划、来源附件、MIT许可、六轨与复核导出继续通过 |
| 独立包 | 解压包在仓库外运行检索、条目读取、原文展开、计划校验、七文件导出和审片/迁移边界 |
| 可复现构建 | 187文件，CRC及固定元数据通过，两次构建相同 |
| motion P1 | 按模式组织输入，交接记录提交/改写与来源；原片/后期版分开。未增加Schema字段或轨道 |
| 0.9.1扩展行为 | 四题motion增量和六题原缺项全部完成独立语义复核，均满足；[motion报告](../implementation/motion-blur-behavior-0.9.1.md)、[原缺项报告](../implementation/extension-behavior-0.9.1.md)保留中断、工程范围和未知媒体效果 |
| WP06文字行为 | 18次执行与三组匿名评审已完成；候选9满足，基线8满足1部分，8持平1候选优先；[报告](../implementation/library-behavior-0.9.0.md)保留轻微问题与证据边界 |
| 最低 Python 版本 | 0.9.0曾在Python3.10.21运行95项单测，93通过、2跳过；[独立记录](../implementation/compatibility-python310-0.9.0.json)。0.9.1只改运行参考、模板和版本，未将该历史记录改标为本次执行 |
| Linux 环境 | WSL 注册了 Ubuntu，但启动因虚拟磁盘缺失失败，未运行 Linux 测试；[探测记录](../implementation/compatibility-linux-2026-09-24.json) |
| 宿主 | [生命周期与目录发现](../implementation/host-verification-0.9.1.md)及[三题实际模型调用](../implementation/host-routing-0.9.1.md)有独立证据；模型调用经CLI/目录权限/同名隔离修正后通过，前6次尝试保留，日常插件未升级 |
| 视频 | 未运行视频生成或媒体对照 |

两项跳过为Windows符号链接条件，不计为通过。0.9.1本次使用项目已有虚拟环境执行，41项检查通过。0.9.0先前系统Python缺少jsonschema的[失败记录](../implementation/validation-0.9.0-attempt1.json)保持历史归属。运行脚本仍仅依赖Python标准库；Linux仍未执行。

逐招等级是编辑政策和源文供给标记，不是动作完整性或事实鉴定。测量证明给调用者展示的字符减少，新增索引会增加本地读取与解析数据量；没有token、延迟、费用或视频质量成绩。历史motion blur行为报告仍属于该专项，不沿用为全库行为比较。

## 构建产物

[combat-director-0.9.1.zip](../../dist/combat-director-0.9.1.zip)

SHA-256：`150ad6f4ba5e9c7ce82f3cd5248facc442f0a0e58cd5767ac878e77a66f50354`

从项目根目录复现：

```powershell
.\.venv\Scripts\python.exe scripts/build_arvin_library.py --check
.\.venv\Scripts\python.exe scripts/validate_release.py
```

当前结果位于工作区，尚未提交推送。WP06、原评估集十二题的分版本覆盖、四题motion增量及三题实际宿主调用已有独立结果；未做每配置三次重复，不把分版本覆盖写成当前版十二题全测。条件化媒体工作仍未执行，整体目标状态见[完成核对](../implementation/completion-audit-2026-09-24.md)。
