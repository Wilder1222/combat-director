# 研究证据索引

采集日期：2026-09-21；本地产品基线 0.2.0。这里是开发研究资料，不是 Skill 的运行时资源，不进入插件包。

| 文件 | 内容与边界 |
| --- | --- |
| [repository-snapshots.json](repository-snapshots.json) | 7 个远端仓库固定提交及 1 个 CineWeave 本地干净快照；candidate_files 是候选，不代表全部审阅 |
| [reviewed-sources.json](reviewed-sources.json) | 16 份实际取得的源文件路径、提交、SHA-256、行数；个别字段注明局部阅读范围 |
| [host-guidance.json](host-guidance.json) | 本机 skill-creator/plugin-creator 说明文件的快照身份，不证明插件实际调用成功 |
| [probe_current.py](probe_current.py) | 对内存中的计划副本做 7 项诊断；不修改产品代码或示例，会写入同目录的结果 JSON |
| [probe-results.json](probe-results.json) | 实际诊断结果与代码/Schema/Skill 的基线哈希 |
| [baseline-tests.txt](baseline-tests.txt) | 当前单元测试原始记录：26 项，25 通过，1 项因环境跳过 |

从项目根目录复现诊断：

```powershell
python docs/research/evidence/probe_current.py
python -m unittest discover -s tests -v
```

诊断脚本用于当前基线；后续实现修复后结果应变化。结果 JSON 内的基线哈希是判断是否同一实验对象的依据；重新运行会替换结果文件，正式保留历史证据时请先另存快照。该脚本不是生产回归测试，也没有运行宿主模型或视频生成。

外部源码仅用于阅读，没有执行其脚本；本目录不分发源码副本。GitHub API 的 license 空值不能解释为已确认无授权条款。

## 官方文档与获取范围

| 来源 | 阅读状态 | 用途 |
| --- | --- | --- |
| [Agent Skills specification](https://agentskills.io/specification) | 已读取正文 | 格式、元数据与渐进加载 |
| [Agent Skills evaluating skills](https://agentskills.io/skill-creation/evaluating-skills) | 已读取正文 | 真实任务、独立上下文和基线对照 |
| [OpenAI Build skills](https://learn.chatgpt.com/docs/build-skills) | 已读取正文；从 Codex skills 地址跳转 | 当前发现目录、入口与调用设计 |
| [Seedance 2.0 指南](https://docs.volcengine.com/docs/ark/seedance-2-0-prompt-guide?lang=en) | 检索可见，页面正文未完整取得 | 后续能力核验入口，不用于声明参数上限 |
| [Seedance 2.5 指南](https://docs.volcengine.com/docs/ark/seedance-2-5-prompt-guide?lang=zh) | 检索可见，页面正文未完整取得 | 后续能力核验入口，不用于声明参数上限 |
| [Liblib 官方首页](https://www.liblib.tv/) | 已读取公开页面 | 平台/模型关系，不证明账号能力 |

可变网页只代表访问时状态；研究报告中的开源实现链接均固定 commit。此处没有平台账号级验证、原 MP4 证据或已执行的 Skill 行为评估结果。
