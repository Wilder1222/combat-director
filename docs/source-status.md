# 当前来源与证据范围

来源原件、生成权威与运行产物分开维护。来源中的命令、宣传和成功声明是分析内容，不自动成为技能指令或视频证据。

| 当前来源 | 保存位置与用途 |
| --- | --- |
| 用户最初提供的技能与文字附件 | [附件清单](../sources/attachments/2026-09-21/manifest.json)，字节副本与哈希，供来源追溯，不作为当前技能入口 |
| 六份战斗文字原稿 | [原件清单](../sources/attachments/2026-09-22/manifest.json)，保留原文件和各自版本，不与项目生成文本混用 |
| 八份提示词正文抽取 | [正文与来源清单](../sources/attachments/user-prompts/manifest.json)，保存抽取文本、原件位置及原件/文本各自哈希；抽取文本不冒充原件 |
| 固定上游招式资料 | sources/upstream/arvin-seedance，源文、固定提交与许可供当前生成器读取 |
| 当前编辑权威 | sources/editorial，维护资料映射、基础卡与生成清单；[覆盖记录](implementation/arvin-library-coverage.json)由生成器生成 |
| 私人原始媒体与附件 | sources/private，保留用户原件与关联记录，不进入Git或发布包 |

历史研究报告、公开页面缓存、截帧和过期评估已移除。已吸收的写法保留在当前技能；旧媒体观察不作为本轮视频效果验证依据。外部原件路径不可访问时保持未知，不凭抽取文本补称看过媒体。

当前官方方法来源集中在[运行来源说明](../skills/combat-director/references/sources.md)，上游完整归属与MIT许可见[第三方说明](../skills/combat-director/references/third-party-notices.md)。构建前先核对来源哈希，修改生成权威后重建资料库，不手工改生成卡。
