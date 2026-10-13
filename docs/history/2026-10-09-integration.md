# 2026-10-09 融合与验收索引

此页索引当时的仙侠融合、视觉重音与连续性研究，供历史复查。固定Combat Director基线为`fdfdf3aaa4feee3e49df229fc1be9db063b03214`；上游仙侠来源固定到`f3721de6e21af8cd5186c88079bf92d252ec416e`。历史结果不自动覆盖后续工作树改动。

## 记录与展开节点

| 记录 | 用途 |
| --- | --- |
| [源清单](../../sources/upstream/xianxia-combat-skill/source-manifest.json) | 原始来源文件与完整指纹 |
| [迁移清单](../implementation/xianxia-integration-inventory.json) | 来源单元、能力、条件、原测试与最终处置 |
| [完成记录](../implementation/xianxia-integration-completion.json) | 完整受审快照、迁移关系、原报告与版本绑定 |
| [发布记录](../implementation/release-validation.json) | 冻结的当时检查结果与包指纹 |
| [视觉重音研究](../implementation/vibeshot-impact-optimization.md) | 方法分析、取舍与原创文字试用 |
| [连续性研究](../implementation/goodcase-continuity-optimization.md) | 参考适配、跨镜接续与文字试用 |
| [设计](../implementation/xianxia-design-research.md)、[专题](../implementation/xianxia-topic-research.md)、[工具](../implementation/xianxia-tool-research.md)、[契约](../implementation/xianxia-contract-research.md)调查 | 当时的读取范围与实现取舍 |

完成记录的JSON指针：

- `/proofs/semantic_current/snapshot`：当时运行正文的语义审阅。
- `/proofs/tool_design/snapshot`：工具、函数、负例及原案例映射的完整规范副本。
- `/proofs/contract_design/snapshot`：契约扩展、实现关系及测试映射的完整规范副本。
- `/proofs/blind_forward/snapshot`：独立完整创作审阅。
- `/proofs/release/snapshot`：发布结果与已审运行文件的绑定。
- `/proofs/host_discovery/snapshot`、`/proofs/host_installation/snapshot`：当时实际发现与安装回执。

原工具与契约映射JSON在上述快照中完整保留，重复文件已移除；原路径、原报告指纹与既有标记保持原始记录，原文件仍可从固定Git版本取回。来源、研究和历史记录不成为运行技能的读取依赖。

## 复查固定版本

~~~powershell
python -X utf8 scripts/validate_integration.py --revision fdfdf3aaa4feee3e49df229fc1be9db063b03214
git show fdfdf3aaa4feee3e49df229fc1be9db063b03214:docs/xianxia-integration-plan.md
~~~

修订审计读取该提交的原件、目标正文与证明文件，核对当时记录；它不为当前工作树补签语义审阅。原命令、长计划及同日各轮验收可直接从该Git版本读取，不额外复制正文。

历史验收分别包含文字、工程、合成抽帧工具、包和宿主入口结果。原记录明确没有生成或审看新的创作视频，文字盲审和合成测试不证明实际动作、连续接点或音轨质量。涉及私人原片的进一步复查需要原本机证据；公开历史审计只声明实际可验证的范围。
