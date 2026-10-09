# 单入口与整体设计调研

日期：2026-10-09。范围：当前本地skill-creator、固定仙侠来源、实施前当前项目与四份一手技能设计/评估材料。研究用于确定设计，完成度另以实际迁移和验证记录证明。

| 一手资料与实际读取范围 | 采用与本项目落点 | 保留的边界 |
| --- | --- | --- |
| [OpenAI：重审Skills与提示](https://developers.openai.com/blog/rethinking-skills-and-prompts-for-gpt-6-astra)，Better skills、Decision boundaries、Persistence正文 | 精确简洁描述；主入口保留共通关系和按问题直达参考；删除无关固定程序和重复写法 | 文章针对其模型经验，不变成本项目模型绑定，也不按缩短字数判断能力完整 |
| [OpenAI：Skills系统评估](https://developers.openai.com/blog/eval-skills)，成功定义、显式/隐式/负控制、执行记录、确定性与定性检查 | 检查完整产物、真实读/用路径、结构负例和独立创作；静态语义对读与冷启动任务分开 | 不凭测试数/最终文字自评分证明媒体，也不复制其示范任务与全套工具链 |
| [Agent Skills规范](https://agentskills.io/specification)，frontmatter、scripts、references、渐进读取与相对引用 | 一个name、description、SKILL；脚本声明条件依赖，入口直接链接维护权威 | 行数/token建议仅用于组织取舍，不作生成质量或机械配额 |
| [Anthropic技能作者实践](https://platform.claude.com/docs/en/agents-and-tools/agent-skills/best-practices)，简洁、自由度、专题组织、少层引用与实际使用迭代 | 开放创作保留选择空间；易错的状态/预算/文件行为用具体约束与工具；按症状分配专题 | 未将其客户端字段、模型族或工具语法迁为Codex硬配置 |

## 对当前仓库的实际取舍

- 两个入口拥有相似攻防/状态流程，题材机制适合组合到同一状态链，保留一个combat-director入口；仙侠原身份转为固定来源。
- 原prompt-construction的25类重复完整教学段改为按信息功能的表、必要机制和三个完整正文模板；专业术语的非显然区别仍保留，摄影词义集中到摄影专题。
- 原choreography的空间、摄影、成像移至对应专题；共通战术、双方接点、受力/恢复、物件、情绪选择保持权威。手印联动在独立审阅指出遗漏后补入力量专题。
- 核心知识保持自含。词库、上游资料、平台执行、抽帧及JSON工程按实际任务读取，写提示词不触发制作。
- 既有长研究流水及指向本机outputs的链接整理为当前设计/来源/验证记录。实施前原字节保存在本机baseline，原方法和当前仙侠来源继续可追溯。
- 完整来源盘点、每组条件对照、自动工具负例、独立语义审阅、冷启动完整提示词及发布发现分别记录。发现遗漏以实际正文修正后有界复核，不仅改清单状态。

## 尚需完成的验收

本记录证明读取与设计取舍，不单独证明融合完成。需以最新目标文件、源范围、条件/例外审阅、完整案例输出及实际命令结果关闭迁移清单；媒体质量只在有对应观察时声明。

## P5：本机安装与真实发现

2026-10-09补读[官方插件打包说明](https://developers.openai.com/plugins/build/plugins)的兼容布局、本地市场与安装缓存章节，以及[App Server说明](https://learn.chatgpt.com/docs/app-server)的初始化和Skills章节。现有`.codex-plugin/plugin.json`仍受支持；本次沿用已有personal市场和插件身份，避免增加第二份配置权威。修改市场源文件不代表安装缓存已经更新。

本机以已安装Codex 0.147.0的CLI帮助、生成的RPC schema与实际回执确定可用命令和字段。元数据验收只发送`initialize → initialized → skills/list(cwds, forceReload=true)`，检查启用入口及缓存正文指纹；不启动会话、模型或视频任务。官方页面提到的额外根字段未在当前本机schema中使用。

先核验发布记录、ZIP和暂存文件的全部指纹，再保留旧源目录并切换已验证目录；刷新combat-director后才移除旧仙侠入口。前后插件清单另行比较，其他插件不参与迁移。当前会话所带旧技能目录是既有上下文，不能由一次磁盘写入证明即时替换；新元数据连接的实际发现单独记录。
