# LibTV Skill 格式与 Combat Director 迁移调研

调研日期：2026-09-22。项目基线：Combat Director 0.6.0。

## 结论与证据范围

迁移应以 LibTV 站内自定义创作 Skill 为目标。官方 `libtv-labs/libtv-skills` 仓库提供的是外部 Agent 连接 LibTV 的工具技能；其 OpenClaw 元数据、Python 依赖和鉴权变量不能直接当作站内上传规范。

当前项目的文本方法论适合迁移。建议先准备不依赖本地脚本的创作版本，再通过登录后的创建页面验证导入格式。现阶段不能声称现有 Codex 插件 ZIP 可以直接上传，也不能声称 LibTV 会执行随包 Python。

证据分级：

| 事项 | 本次证据 | 判断 |
| --- | --- | --- |
| 站内 Skill 市场、分类、收藏、我的入口 | 官方站点实时浏览 | 已确认 |
| 站内详情展示名称、介绍、使用场景、如何使用、输出内容 | 官方站点实时浏览“影视打斗特效skill”详情 | 已确认展示字段；不等于全部创建必填字段 |
| 创建页面填写名称、一句话介绍、Markdown 规则及使用说明 | 创作者甲木的亲身使用记录 | 实操证据，尚未由当前登录后的表单复核 |
| 外部连接技能的 SKILL.md、scripts 和 YAML 元数据 | 官方 GitHub main | 已确认；只适用于该连接技能 |
| 原生 Skill ZIP 层级、上传大小、扩展名白名单、引用加载机制、Python 运行时 | 未取得登录后的创建表单或正式规范 | 未确认 |

本次在未登录浏览器点击“我的”后出现登录窗口，未创建账号、上传技能或执行生成。官方站点“帮助信息 → 使用教程”指向官方飞书指南；本次未从所查看的指南内容取得站内 Skill 导入规范。

## 两种 Skill 的区别

### 站内创作 Skill：本项目的迁移目标

运行在 LibTV Agent 创作环境，内容应表达专业方法、工作流程、输入输出与质量检查。当前可确认的展示层字段可映射为：

| 字段 | Combat Director 建议内容 |
| --- | --- |
| 名称 | 战斗导演 |
| 一句话介绍 | 编排有攻防因果、角色表演和连续性的武侠与仙侠战斗短片。 |
| Skill 内容 | 任务路由、约束卡、攻防节拍、六轨时间轴、提示词编译、参考绑定、生成与审片规则 |
| 使用场景 | 武侠交手、仙侠斗法、巨型敌人反制、角色登场、失败片段修复 |
| 如何使用 | 提供人物、目标、场景、时长与参考素材，说明只要方案还是需要生成。 |
| 输出内容 | 战斗设计卡、六轨稿、中文提示词；执行模式再输出实际生成结果及修复记录。 |

以上是迁移建议，不是官方字段 Schema。中文展示名与内部技能标识应分开；是否可设置内部标识、哪些字段必填，以当前创建页为准。

### 外部连接 Skill：可选的另一条接入路径

官方仓库结构为 `skills/libtv-skill/SKILL.md` 加 `scripts/`。脚本负责会话、查询、切换项目、素材上传与结果下载。`SKILL.md` 使用 YAML frontmatter 加 Markdown 正文，实际包含：

```yaml
name: libtv-skill
description: <用途和触发场景>
user-invocable: true
metadata:
  openclaw:
    emoji: "💬"
    requires:
      bins: [python3]
      env: [LIBTV_ACCESS_KEY]
    primaryEnv: LIBTV_ACCESS_KEY
```

这是已发布实例，不代表上述每个字段都是所有宿主的必填项。`LIBTV_ACCESS_KEY` 用于外部调用；不能据此要求站内自定义 Skill 再配置同一密钥。

该连接技能还要求用户侧 Agent 转发需求，由后端承担创作编排。这与 Combat Director 在本地承担战斗编排的职责不同，直接合并两份入口会产生职责冲突。站内迁移应将战斗方法提供给站内 Agent；若另做外部调用版，则需要明确编排与执行的交接边界。

## 建议的迁移源结构

以下是待适配源结构，尚不是通过 LibTV 导入验证的 ZIP 结构：

```text
combat-director-libtv/
├── SKILL.md
├── references/
│   ├── choreography.md
│   ├── prompt-craft.md
│   ├── templates.md
│   ├── quality.md
│   └── libtv-workflow.md
└── examples/
    ├── grounded-15.md
    └── entrance-cliffhanger-15.md
```

`SKILL.md` 建议保留名称和描述的 frontmatter，正文包括适用场景、输入与默认值、流程、输出、自检、何时询问用户。这是沿用当前项目的可维护源格式；站内表单若只收 Markdown 内容，应提供展开依赖的单文件版本，不能留下无法读取的相对链接。

在未确认多文件读取前，应准备单文件导入作为兼容方案；确认支持相对引用后再输出多文件包。关键约束始终放入口正文，细节与长案例再拆到参考文件。

## 与当前项目的具体差异

| 当前内容 | 建议处理 |
| --- | --- |
| `skills/combat-director/SKILL.md` | 保留编排核心，增加 LibTV 执行分支，减少本地 CLI 使用说明 |
| `references/choreography.md`、`prompt-craft.md`、`templates.md` | 保留攻防因果、飞剑回握、旧伤回收、能力边界等规则 |
| 六轨时间轴与八标签投喂结构 | 保留；说明其为创作表达，不是平台 API 参数 |
| `references/platforms.md` | 派生站内流程文档，以实际工具绑定参考和回收结果，不虚构工具名 |
| `.codex-plugin/plugin.json`、`agents/openai.yaml` | 不作为 LibTV 导入依赖，继续服务原 Codex 发行版 |
| `scripts/combat_*.py` | 保留在本地工程；站内 Python 能力未确认，不作为站内必经步骤 |
| Schema、计划 JSON、哈希复核 | 继续用于本地工程校验；站内文字自检不等于脚本校验通过 |
| 默认只输出提示词 | 保留“方案模式”；用户要求生成时进入已授权的“执行模式” |
| 默认 30 秒 | 作为创作目标，不当作所有模型与入口的固定支持上限 |

建议的站内流程：继承输入与授权 → 锁定人物目标和能力 → 编排连续攻防 → 绑定参考用途 → 编译提示词并自检 → 按用户要求交付方案或调用实际可用生成工具 → 查看真实结果后修复。

必须继续区分单次生成、一镜到底与单个成片文件。平台不能满足目标时长时应说明冲突，不能擅自拼接后宣称直出。没有真实绑定或生成结果时不能报告已绑定、已出片或效果通过。

## 完成迁移前的最小验证

1. 登录后读取创建页面：确认 Markdown 粘贴、单文件、文件夹或 ZIP 的实际支持方式。
2. 若支持 ZIP，确认 `SKILL.md` 所在层级、压缩大小、文件数量与类型限制。
3. 用一个小型参考文件验证相对引用能否实际读取；不要仅凭上传成功判断支持。
4. 确认是否有脚本运行环境、支持语言和依赖安装；没有证据时走纯文本路线。
5. 用人物级 15 秒案例检查攻防因果、武器持手、双方动作回应和连续性，再测试登场悬念案例。
6. 分开记录导入成功、规则生效、生成执行成功和成片质量；这四项互不替代。

本轮仅完成调研，没有更改技能入口、平台能力配置、构建脚本或发行产物。

## 来源

- [LibTV 站内 Skill](https://www.liblib.tv/skill)：2026-09-22 实时浏览，核验市场、详情展示字段及“我的”登录门槛。
- [官方使用指南](https://resonate.feishu.cn/wiki/Loxfw6XHziYRk0kKzdjcFfp9nhb)：由站点帮助入口打开，用于追溯官方文档入口。
- [官方连接技能仓库](https://github.com/libtv-labs/libtv-skills)：连接技能的用途与目录布局。
- [官方连接技能 SKILL.md](https://github.com/libtv-labs/libtv-skills/blob/main/skills/libtv-skill/SKILL.md)：frontmatter、运行依赖和用户侧转发职责。
- [甲木的自建 Skill 实操记录](https://watcha.cn/discuss/10220)：作者亲身操作说明，第四部分描述创建字段与 Markdown 内容；并非官方完整规范。
- 本地基线：`skills/combat-director/SKILL.md`、`references/platforms.md`、`assets/platform-profiles.json`、`.codex-plugin/plugin.json`、`README.md`。本轮直接读取，没有依赖历史记忆。
