# 验证用法

当前工作树的内容、工程和发布检查分别执行。每次结果以实际命令回执及`outputs/validation/release-validation.json`为准；本页不维护容易过期的通过计数或ZIP指纹。

## 当前命令

~~~powershell
python -X utf8 scripts/build_arvin_library.py --check
python -X utf8 scripts/validate_content.py
.venv/Scripts/python.exe -X utf8 -m unittest discover -s tests -v
.venv/Scripts/python.exe -X utf8 scripts/validate_release.py
~~~

发布检查会汇总内容、契约、生成资料一致性、回归、自含解包与可复现构建。可选工具和依赖是否实际执行、哪些检查跳过，读取当次报告，不从旧记录推断。测试使用本地夹具，不自动生成收费媒体。

## 验证职责

| 检查 | 能证明的范围 |
| --- | --- |
| 来源与生成指纹 | 固定来源、编辑权威和生成归属的一致性 |
| 内容与案例结构 | 本地引用、章节、时间表达和公开/私有边界 |
| 工程回归 | 契约、事实回放、并发、占用、复核失效与导出兼容 |
| 抽帧工具测试 | PTS、像素及元数据、文件指纹和异常保护 |
| 独立语义审阅 | 实际所读条件、例外、目标正文与受审版本的对应 |
| 独立创作试用 | 真实请求下的读取路径、完整提示词及需求满足情况 |
| 包与安装 | 可复现ZIP、自含运行及实际宿主发现；安装另需相应回执 |

结构检查、合成媒体测试和提示词试用不证明生成视频的动作、接点、连续性或声音质量；静帧、原速观看和实际听辨分别保存观察证据。

分类结构回归见[交付结构请求](../tests/fixtures/prompt-layout-regression.md)，内容兑现与范围保持见[表现力请求](../tests/fixtures/creative-expression-regression.md)。独立试用保存原请求、完整产物、实际读取范围及受审指纹；语义审阅分别核动作/持物/时间、适用的视觉与摄影选择、媒介/静音/局部改稿边界。某稿出错先记录具体关系和修订版本，不能重写原输出或据一轮结果宣布稳定出片。

接触静电、觉醒表演与逐节点秒数的试用请求见[节点时间回归](../tests/fixtures/static-contact-timing-regression.md)。工程测试检查full/compact/detailed实际prompt.txt逐一显示被合并节点的起止与占时、单镜不增切点，逐动作耗时与简洁慢镜正文保留，以及修改节点时间后原复核失效。具体交手投影另核中断后的实际耗时与取消中断的接续；文字案例对读和媒体验证各自记录，不能据导出测试认定实际视频速度。

时间依赖、实际镜头登记和接点覆盖的自然语言回归输入见[预算与覆盖请求](../tests/fixtures/budget-camera-contact-regression.md)。核验每名行动者的关键路线和触发偏移、在途跨镜余时、实际切点与可读接点；这些行为结果由完整产物及版本指纹记录，不从文档关键词或标题测试推断。

冻结的五轮评估账本统一由[评估审计器](../scripts/audit_prompt_evaluations.py)复算，原目录入口保留为兼容包装。默认只读，使用`--out`将当次回执写到项目`outputs/`内且冻结目录之外；旧来源用`--source-revision`核对相应Git字节，不重写历史manifest、分数或validation。工具只验证已支持格式的指纹、结构与人工账本，不替代独立攻防评审。复测目录可直接运行；基线目录指定`--source-revision f2463f7542895b4ee366dac688087e6ea0d4a2d5`。

护送、多人同步与御空的新首稿由隔离代理独立评审，结果为97、79（硬失败封顶）、94，具体触发与取景问题见[泛化结果](evaluations/2026-10-13-generalization/report.md)。此格式不由五轮共享审计器推断语义。重复审计合并、旧包与缓存清理以及本轮完整工程验证见[清理记录](history/2026-10-14-generalization-cleanup.md)。

## 历史验收

2026-10-09的仙侠融合、视觉重音和连续性验收属于固定版本。原发布报告留在[历史JSON](implementation/release-validation.json)，融合证明及复查命令见[历史索引](history/2026-10-09-integration.md)。旧报告不会被新的发布检查覆盖；工作树重构后，历史审计通过只说明所选Git版本的记录完整。
