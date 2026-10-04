# Combat Director · 战斗导演

输入场景、战斗类型、人物与招式，输出可独立复制的详细中文战斗视频提示词。源码基版0.10.0，项目仅维护当前实现、必要来源与最新验证。

从[技能入口](skills/combat-director/SKILL.md)开始；完整创作按[生成模板](skills/combat-director/references/prompt-construction.md)组织，专项按需读取。文本创作无需平台插件、查库或JSON。

视频时长按用户需求确定；未指定时按动作内容、叙事目标与节奏拟定合理时长，不设固定秒数。其他未指定项默认16:9、允许切镜、快速实速为主。公共模块独立于分镜，集中写共用风格、人物外观、场景、兵器和规则；每段分镜内部按需求选择不编号的【中文标签】，详细写本镜人物、空间、动作、能力、镜头、时间与表演；25项是写作参考，不存在或未涉及的模块直接省略，不写“无”或“未使用”占位，不要求每镜写齐。攻防保留来路、回应、接触或让空与下一状态，镜数按动作与可读性确定。

指定模型或分段投喂时，区分整场编排、镜头与一次生成片段；图生正文以运动为主，分段各自带齐必要身份与接续状态。只改摄影时保持事件和胜负。写提示词不会自动启动视频生成。

## 当前项目结构

| 位置 | 内容 |
| --- | --- |
| skills/combat-director | 当前技能、7份专项reference、工程脚本、契约与资料库 |
| scripts、tests | 构建与验证工具、回归测试及必要兼容夹具 |
| sources | 当前生成权威、固定上游及用户来源原件；见[来源说明](docs/source-status.md) |
| docs | [当前设计](docs/design.md)、[当前验证](docs/validation.md)、来源说明与当前工程记录 |
| outputs/current、dist | 最新文字试用与检查结果、当前候选ZIP；均不纳入Git |

## 工程命令

Python 3.10+，运行时仅标准库，开发依赖见requirements-dev.txt。自然语言创作不需要JSON。工程导出时，以用户计划替换your-plan.json，并按工程契约填写及复核reviewed-prompt.json中的逐镜按需分类内容：

```powershell
python skills/combat-director/scripts/combat_tool.py validate your-plan.json
python skills/combat-director/scripts/combat_tool.py render your-plan.json --prompt-style detailed --prompt-file reviewed-prompt.json --out-dir outputs/current/render
python skills/combat-director/scripts/library_tool.py items --query "乌龙摆尾" --school "八卦掌"
python scripts/project.py build
.venv/Scripts/python.exe scripts/validate_release.py
```

修改资料权威后运行scripts/build_arvin_library.py，勿手改生成卡。工程接口见[数据契约](skills/combat-director/references/contract.md)，归属见[第三方许可](skills/combat-director/references/third-party-notices.md)。

发布包仅包含插件清单与技能资源。文字、测试和打包通过不证明视频效果；安装发现需另验，源码修改不会热替换已加载的插件缓存。
