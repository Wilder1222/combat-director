# Combat Director · 战斗导演

输入**场景、战斗类型、人物、招式**，输出一份可直接复制的详细中文战斗视频提示词。当前工作区按AIGC战斗设置、拆解模板与提示词生成逻辑维护；源码基版为0.10.0，本机插件安装与发现结果见[当前验证](docs/validation.md)。

入口：[SKILL.md](skills/combat-director/SKILL.md)判断任务；完整创作读取[战斗设置与生成模板](skills/combat-director/references/prompt-construction.md)，其余专项按需读取。当前8份reference内含可执行步骤、可替换句式和使用条件，外链仅作来源追溯。具体分工见[设计说明](docs/design.md)。文本创作无需平台插件、查库或JSON。

## 创作流程

四项自然语言描述 → 六项战斗设置 → 动作单元 → 状态衔接 → 时间与镜头覆盖 → 命中及光影 → 自含提示词与对读。

默认路径区分内部事件事实与模型投喂表达；素材区分身份参考、首帧和动作/摄影参考。人物动作、相机运动、播放倍率和剪辑密度分开安排。用户只改摄影时保持事件与胜负，平台未知仍能完成文本创作。

- 仙侠支持花海、林冠、山体、崖壁与云海的纵深和高差；人物实际跨区，近身、御器与场域压制有转换原因。狭窄场地仍遵守用户设定。
- 高能通过快速发力、接点反馈、回收接反击、移动追压和战术升级实现；镜头剪得快不等于动作快。
- 轴线保证可读性，换边与跨区展示真实路径，不将整场锁死在小石台。镜数按动作、时长与可读性自适应，先编排再统计；改为自适应后不再沿用旧镜数。
- 默认总设定明确写出**整体风格、战斗人物、武器、技能招式、命中效果、特效光影**；时间段正文展开攻防，并把实际命中与光效反馈落到对应动作。徒手、无命中、无超自然特效可直接说明；精简、导演表、JSON均为按需交付。
- 对抗型连招以回应和结果推动下一招，演武型连招以重心、旋向和兵器余势接续；不为展示强补敌人或伤害。教学骨架不作为已验证的成片案例。

使用时直接描述四项信息即可，时长、镜头形式、结尾与参考图可补充在同一句话。只写提示词不会启动视频生成。

## 设计依据与边界

[八份原提示词审阅](docs/research/2026-10-01-eight-prompts-design-review.md)、[公开技能设计调研](docs/research/2026-10-01-public-combat-skills-design-study.md)、[当前设计](docs/design.md)、[验证](docs/validation.md)。原片、《诛仙》及失败成片研究保留在docs/research，其观察范围分别声明。没有新版生成视频，不声称动作速度或生成成功率已提高。

本轮维护独立skill，已移除停用的LibTV独立适配与构建链。平台导入、模型能力与媒体生成需实际入口核验。

## 可选工程工具

Python 3.10+，运行时仅标准库。以用户自己的计划替换your-plan.json：

```powershell
python skills/combat-director/scripts/combat_tool.py validate your-plan.json
python skills/combat-director/scripts/combat_tool.py render your-plan.json --out-dir outputs/render
python skills/combat-director/scripts/library_tool.py items --query "乌龙摆尾" --school "八卦掌"
python skills/combat-director/scripts/library_tool.py validate
python scripts/project.py validate-release
python scripts/project.py build
.venv/Scripts/python.exe scripts/validate_release.py
```

JSON与精简投影保留复核失效检查、来源保护和完整导出；哈希通过不证明语义正确。工程说明见[数据契约](skills/combat-director/references/contract.md)。开发依赖见requirements-dev.txt。

招式资料卡来源在sources/upstream，修改生成权威后运行scripts/build_arvin_library.py，勿直接改生成卡。它们用于检索候选与来源追溯，不作为视频成功案例。许可见[第三方说明](skills/combat-director/references/third-party-notices.md)。

构建只包含插件清单与技能资源，拒绝examples、tests、fixtures或evals进入技能包。原始附件、工程夹具、历史评估和私人资料不进入发布包。安装/更新后是否被宿主发现须另验；当前任务已加载的缓存不会因源码修改热替换。
