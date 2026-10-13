# 当前架构

项目分为技能运行包、仓库维护工具、来源权威与证据四部分。发布包从`skills/combat-director/`及插件元数据构建；来源、测试、维护工具和本机输出留在仓库维护侧。

## 运行包

[SKILL.md](../skills/combat-director/SKILL.md)维护任务判断和共通状态链，直接路由到按需参考。人物、兵器、接点、在途攻击和未完事件由同一份动作事实承接，摄影、声音与效果解释这些事实。创作方法的具体规则保持在运行参考中，维护文档只描述职责。

`references/`维护专题方法，`library/`提供可追溯候选资料，`assets/`保存契约和模板，`scripts/`提供可选工程与抽帧工具。普通提示词任务直接从自然语言输入开始；JSON工程和媒体制作按对应任务启用。运行工具保留自含依赖，可以从发布包独立执行。

## 维护工具与生成权威

`scripts/combat_project/`承载发布资源校验、来源核对、ZIP构建和发布回归的实现。[project.py](../scripts/project.py)保留既有CLI和导入兼容，委托实现包；[validate_release.py](../scripts/validate_release.py)编排发布检查。[build_arvin_library.py](../scripts/build_arvin_library.py)和[validate_content.py](../scripts/validate_content.py)继续作为独立专项工具。公共命令不随内部模块分工变化。

实现包按职责划分：`runtime.py`验证可发布资源与自含入口，`sources.py`核对来源和生成一致性，`archive.py`负责确定性ZIP及受保护替换，`loading.py`按文件位置加载维护助手，`reporting.py`保存检查回执和输入指纹，`release_smoke.py`在独立解包目录检查运行行为。

| 输入与权威 | 处理 | 输出与归属 |
| --- | --- | --- |
| `sources/editorial/library-base.json`、`arvin-facets.json`与固定Arvin来源 | 资料库生成器 | 运行卡片、导航、catalog与items；归属指纹记录于`arvin-generated.json` |
| 插件元数据与`skills/combat-director/` | 内容检查、发布白名单和构建 | `dist/`中的自含ZIP及包内发布指纹清单 |
| 当前源码、测试及可选验证环境 | 发布回归 | `outputs/validation/release-validation.json` |
| 固定来源与历史审阅记录 | 按Git修订审计 | 历史完整性结果；不修改已审记录 |

资料库内容先改编辑权威；解析或生成行为先改维护实现，再执行生成器。生成器检查归属和当前字节，保护未知文件与人工改动。`arvin-generated.json`由工具维护，不把生成卡片当第二份编辑权威。[来源页](source-status.md)说明来源原件与改编的区别。

## 证据与临时产物

`tests/`维护可丢弃夹具和可重复回归。`outputs/`保存本机试用、媒体证据与当次报告，`dist/`保存可重建发布产物；它们不进入Git和默认技能读取。私人原片继续在忽略目录保留，公开文档不依赖这些原片才能使用技能。

`docs/implementation/`中的融合和验收JSON绑定当时的目标文件、原报告与指纹，保持原始字节。[历史索引](history/2026-10-09-integration.md)按固定Git提交复查；[当前验证](validation.md)检查工作树。改变实现后不重算旧审阅指纹来维持通过，也不将旧版验收当作当前改动的验证。

本次结构取舍、去重依据和官方资料见[架构重构记录](history/2026-10-10-architecture.md)。
