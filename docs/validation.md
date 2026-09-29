# 0.9.2 验证报告

日期：2026-09-29。软件0.9.2、卡索引2、条目索引1、Combat Plan1.2；Windows x64、Python3.13.3。本轮只增加技能入口的乱码读取恢复指引，插件清单与入口版本同步；运动成像规则、库、案例与脚本未改变。上一版记录见[0.9.1历史报告](history/validation-0.9.1.md)。

完整发布流程实际重跑，**41项通过**；单元测试**95项，93通过、2跳过**。命令输出、来源及187个运行文件哈希见[机器证据](implementation/validation-0.9.2.json)。跳过项为Windows符号链接条件，不能计为通过。

| 检查 | 证据与结论 |
| --- | --- |
| 变更范围 | 与0.9.1 ZIP比较，仅插件清单及SKILL入口变化，其余185个运行文件相同；[精确比较](../evals/results/host-encoding-0.9.2/comparison.json) |
| 来源与构建 | 固定附件、1466条目证据、来源/派生一致性及正式构建预检通过；116张卡、卡索引2与条目索引1保留 |
| 计划与导出 | 六套原计划、两套motion计划、Schema、复核失效和七文件导出检查通过；不证明自由文字物理正确 |
| 独立包 | 仓库外解压后检索、条目详情、原文展开、计划校验、导出和审片/迁移边界检查通过 |
| 可复现构建 | 187文件，CRC与固定元数据检查通过，两次构建字节一致 |
| 实际读取恢复 | 两份原失败请求在0.9.2复测均取得可读SKILL及motion正文，解码后与候选全文匹配；初次乱码仍存在，见[恢复报告](implementation/encoding-recovery-0.9.2.md) |
| 本轮文字行为 | 上述两题及一题静态短稿共三次新调用，独立复核均满足；静态题未读motion或新增特效，不沿用旧版成绩 |
| 原0.9.1矩阵 | 八格实际执行与独立复核保留原结果；其中两次未恢复读取仍记为历史失败，见[原矩阵](implementation/host-motion-matrix-0.9.1.md) |
| 既有文字证据 | [0.9.1四题motion增量](implementation/motion-blur-behavior-0.9.1.md)、[六题原扩展](implementation/extension-behavior-0.9.1.md)、[0.9.0资料库比较](implementation/library-behavior-0.9.0.md)各保留冻结版本，不改记为0.9.2全量行为验证 |
| 最低Python版本 | 0.9.0曾在Python3.10.21跑95项单测，93通过、2跳过；[历史证据](implementation/compatibility-python310-0.9.0.json)。0.9.2未改Python运行脚本，本轮未重新执行该环境 |
| Linux | WSL Ubuntu因虚拟磁盘缺失未能启动，未运行Linux测试；[环境记录](implementation/compatibility-linux-2026-09-24.json)仍属当时探测 |
| 生命周期 | 安装/升级/回滚/卸载及目录发现的[既有宿主证据](implementation/host-verification-0.9.1.md)属于0.9.1；本轮只做独立临时项目实际读取，日常插件未升级 |
| 媒体 | 无视频生成或审片结果；[18条D/B草案](../evals/media-motion-draft-2026-09-29/README.md)仍待入口核验与执行条件 |

本轮运行恢复依赖可用的读取方式，Python不可用情形未实测。Shell底层编码损坏仍存在；不能宣称Windows通用兼容已修好。宿主使用已有CLI0.154.0-alpha.6.2、继承模型配置、只读unelevated沙箱及单次插件隔离，范围限定在报告中的条件。

## 构建产物

[combat-director-0.9.2.zip](../dist/combat-director-0.9.2.zip)

SHA-256：`aefa93903bdf83806d25459b0249e43f486fe5ca2feab63125bc9490978d03aa`

从项目根目录复现：

```powershell
.\.venv\Scripts\python.exe scripts/build_arvin_library.py --check
.\.venv\Scripts\python.exe scripts/validate_release.py
```

当前结果位于工作区，未提交推送或升级日常插件。多配置重复比较、条件化媒体里程碑与环境限制仍分别列在[完成核对](implementation/completion-audit-2026-09-24.md)，不以本轮三题复测宣称完整当前版行为集或媒体效果通过。
