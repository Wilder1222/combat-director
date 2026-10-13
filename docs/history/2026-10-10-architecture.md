# 2026-10-10 架构重构记录

基线：`fdfdf3aaa4feee3e49df229fc1be9db063b03214`。目标是减少维护实现和当前文档的重复，让运行包、编辑权威、历史证据与当次产物各有明确归属。运行技能内容保持原样。

## 结构取舍

维护实现集中到`scripts/combat_project/`，根层脚本保留既有CLI及导入兼容。运行技能内部的工具继续自含；测试检查实际行为与发布包，不靠根仓库的隐式导入完成运行。编辑权威经生成器生成资料卡、导航和索引，归属清单保护未知文件与人工修改。

README与当前架构、来源、验证页各自说明用法和边界。完成后的长融合计划缩为摘要，历史调查和验收由[固定版本索引](2026-10-09-integration.md)追溯，不复制长计划、能力矩阵和同日多轮统计。

新的发布报告写入`outputs/validation/release-validation.json`。`docs/implementation/release-validation.json`保留冻结历史字节；迁移证明按固定Git提交审计，避免新的回归覆写旧报告或使旧验收冒充当前验证。

独立复审补回构建时全部Python文件的语法检查和核心CLI的独立导入检查，损坏资源在写包前被拒绝，已有ZIP继续保留。当前验证绑定检查前后的源码、夹具、编辑权威及来源指纹；输入变化就要求重跑。历史审计直接读取Git原始对象并禁用替换对象，导出属性和本机Git设置不能改写受审字节。

## 可证明的去重

删除`docs/implementation/xianxia-tool-mapping.json`与`xianxia-contract-mapping.json`前，分别解析并确认其完整JSON对象等于完成记录的`/proofs/tool_design/snapshot`与`/proofs/contract_design/snapshot`；同时核对工作树原字节与上述Git基线、原报告SHA-256一致。

两份原文件指纹分别为`5a43ff5da71ee12294ec48f24c5de5f1851ceb2b3479c5a768c3139e41bd07ab`与`95ed15ea06469e6f9d57f2ac0991cbba279afdc2a4cdc6642573609b9bd5bb39`。无运行调用依赖这两个文件；研究导航改为完成记录及具体展开节点。证据本体不改原路径、标记或指纹，历史修订审计仍从Git取得原文件。

固定上游、用户来源收据、原片和原创规则各有证据或运行价值，继续保留；不同表示或收到时间的相似附件不按文本相似度删除。

## 官方依据

2026-10-10读取[Agent Skills规范](https://agentskills.io/specification)：技能以`SKILL.md`为入口，支持脚本、参考及资源，并按任务渐进读取。这里保留运行包的直接专题导航，仓库维护与历史资料留在其边界外。

同日读取[PyPA：src布局与flat布局](https://packaging.python.org/en/latest/discussions/src-layout-vs-flat-layout/)对可导入代码、工具文件及安装验证的区别。本项目的维护工具从源码执行，使用`scripts/combat_project/`明确内部包边界，保留原CLI；自含发布验证检查运行工具不依赖维护包。这是结合当前交付方式的取舍，官方材料没有要求所有项目统一采用某种目录。

当前重构的检查结果读取[验证用法](../validation.md)所列命令与当次报告。此记录描述改动与去重依据，不替代实际测试、语义审阅或媒体观察。
