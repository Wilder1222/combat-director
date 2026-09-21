# combat-director · 独立战斗导演

**版本：0.1.0；交付日期：2026-09-20。**

这是可独立使用的 Agent Skill 文件夹，不是 CineWeave 子模块，也不是只有一段提示词的笔记。它负责战斗设计、表演与镜头编排、中文视频提示词、审片修复与平台交接，不负责付费执行生成。

## 最快开始

解压后，把整个 `combat-director` 文件夹放进你的项目：

```text
你的项目/
└── .agents/
    └── skills/
        └── combat-director/
            ├── SKILL.md
            ├── references/
            ├── assets/
            ├── examples/
            └── scripts/
```

只选一个安装范围，避免同名技能同时存在。跨项目使用可放到 `~/.agents/skills/combat-director/`。这两个位置来自 OpenAI 官方技能文档，见 `references/sources.md`。无需安装 Python 才能使用文本技能；脚本是可选功能。

在支持技能发现的 Codex 任务中输入：

```text
$combat-director
做一段30秒仙侠战斗测试片，16:9，单次生成，允许内部切镜。
白衣女剑客对阵青色能量修士，场景是开阔荒原。
采用升级式斗法，但每次技能必须有对方回应、代价和可见结果。
人物自然肤质，表情与视线清楚，衣料与兵器有重量。
先输出六轨导演时间轴，再整理成6段中文小云雀提示词。
不实际提交生成，不把测试设定写入我的正式世界观。
```

宿主未发现技能时检查文件夹层级与 SKILL.md 名称，然后新开任务或重启宿主。本交付没有远程安装到你的设备，也没有发布到插件市场。其他支持 Agent Skills 的宿主使用其自身导入方式；不宣称所有产品安装路径相同。

## 包内能力

| 能力 | 内容 |
|---|---|
| 编排 | 战斗目的、攻防回应、转折、能力代价、结尾 |
| 六轨 | 人物攻防、表演情绪、摄影机、特效、环境反馈、声音 |
| 连续性 | 角色位置、姿态、武器、场景状态、镜头衔接 |
| 三种母版 | 人物级攻防；升级式斗法；巨型敌人反制 |
| 平台交接 | 通用、LibTV、小云雀；Flova 保留待核验通用入口 |
| 修复 | 找到失效节拍，只改必要动作、机位或负载 |
| 工程辅助 | JSON 方案格式、结构检查、文本导出、单元测试 |

渲染风格是独立变量：可写真人、CG、三维动画、漫画等，不必为了换风格另做一个战斗系统。

## 直接可看的三个例子

- `examples/epic-30.prompt.txt`：30秒升级式斗法，11个导演节拍整理为6个投喂段。
- `examples/grounded-15.prompt.txt`：15秒人物级武侠攻防，严格一镜到底，无仙术。
- `examples/colossus-30.prompt.txt`：30秒巨型机械威胁反制，以开路撤离为目标，不靠无限放大大招。

这三套均为本包原创测试方案，不是参考视频原始提示词，不是正式剧情定稿，也没有在 SaaS 平台完成出片验证。

## 可选脚本

需要 Python 3.10+，只用标准库，不访问网络、不读取账号密钥。

```bash
cd combat-director
python scripts/combat_tool.py validate examples/epic-30.plan.json
python scripts/combat_tool.py render examples/epic-30.plan.json --platform libtv --out-dir ./output/epic
python -m unittest discover -s tests -v
```

导出包含设计卡、六轨导演稿、可复制提示词、平台交接清单、验收表和原始方案。已存在的输出文件默认不覆盖，只有明确传入 `--force` 才覆盖。

当前界面确认只支持15秒时，可检查时长冲突：
```bash
python scripts/combat_tool.py validate examples/epic-30.plan.json --max-duration 15
```

校验失败是预期结果，不会自动把单次30秒改成两段15秒。`--max-duration` 是你确认的可选上限，不是本程序探测平台得到的结果。

## 独立性与组合

```text
你的创意 / 视频 / 人物场景资产
                 ↓
          combat-director
                 ↓
战斗计划 + 六轨导演稿 + 中文提示词 + 交接清单
                 ↓
独立交给视频平台，或交给 CineWeave / 其他 Agent 消费
```

组合只交换文件，不导入 CineWeave 私库，不改变其版本或接口。外部系统自己的字段映射需在接入时核实，见 `references/contract.md`。

## 验证范围

本地验证涵盖：示例格式、时间覆盖、状态继承、能力尺度、单镜冲突、主段覆盖、参考绑定记录、导出行为。报告见 `VALIDATION.md`。

未验证：视频平台实际生成结果、人物脸部稳定性、音画同步、特效质量、技能在你本机的加载与远程 CineWeave 对接。格式检查通过不等于视频必然成功。

## 来源与素材

结构格式、安装范围、平台能力均记录在 `references/sources.md`。能力记录是2026-09-20的公开资料快照，不能代替当前账户可用性。

包内不分发原抖音视频、截图或第三方人物素材。`references/source-case.md` 只保留抽象结构与证据边界。
