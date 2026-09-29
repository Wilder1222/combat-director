# 0.9.0 验证报告

日期：2026-09-24。软件0.9.0、卡索引2、条目索引1、Combat Plan1.2；Windows x64、Python3.13.3。WP04逐招来源与WP05紧凑读取已实现，WP06独立创作评估进行中。历史见[0.8.3报告](validation-0.8.3.md)。

完整发布流程 **41项通过**；单元测试 **95项，93通过、2跳过**。命令输出、来源及187个运行文件哈希见[机器证据](../implementation/validation-0.9.0.json)，实现及来源分级见[交付说明](../implementation/library-items-0.9.0.md)。

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
| WP06文字行为 | 已冻结0.8.0/0.9.0并开始独立任务；尚未完成，工程成绩不替代语义结果 |
| 最低 Python 版本 | 2026-09-24 补跑 Python 3.10.21 的当前 95 项单测，93 通过、2 项 Windows 链接条件跳过；[独立记录](../implementation/compatibility-python310-0.9.0.json) |
| Linux 环境 | WSL 注册了 Ubuntu，但启动因虚拟磁盘缺失失败，未运行 Linux 测试；[探测记录](../implementation/compatibility-linux-2026-09-24.json) |
| 宿主与视频 | 未升级安装插件、未测自动发现、未运行视频生成或媒体对照 |

两项跳过为Windows符号链接条件，不计为通过。第一次使用系统Python运行时缺少jsonschema；单测通过后在Schema检查停止，[失败记录](../implementation/validation-0.9.0-attempt1.json)保留。改用项目已有虚拟环境后41项检查通过，运行脚本仍仅依赖Python标准库。最低声明版本3.10随后完成单测验证；它不替代3.13环境中的开发依赖Schema检查，Linux仍未执行。

逐招等级是编辑政策和源文供给标记，不是动作完整性或事实鉴定。测量证明给调用者展示的字符减少，新增索引会增加本地读取与解析数据量；没有token、延迟、费用或视频质量成绩。历史motion blur行为报告仍属于该专项，不沿用为全库行为比较。

## 构建产物

[combat-director-0.9.0.zip](../../dist/combat-director-0.9.0.zip)

SHA-256：`a018117b6442727ba6d0b53471c1f6be4e981afe58029423314c60c54b30a689`

从项目根目录复现：

```powershell
.\.venv\Scripts\python.exe scripts/build_arvin_library.py --check
.\.venv\Scripts\python.exe scripts/validate_release.py
```

当前结果位于工作区，尚未提交推送。WP06仍需完成九类任务、对照及独立语义评价，整体目标保持进行中。
