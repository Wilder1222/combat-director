# 0.10.0 验证报告

日期：2026-09-30。核心0.10.0、LibTV适配0.10.0-libtv.1；Combat Plan仍为1.2，新增可选combat-prompt/1表达文件。旧版记录保留于[0.9.2历史报告](history/validation-0.9.2.md)。

完整发布流程43项通过。单元测试105项，其中103通过、2因Windows符号链接条件跳过；不能将跳过计为通过。发布包195个文件，两次构建字节一致，完整导出七文件、精简导出八文件均在仓库外解压环境验证。原计划与完整提示词重建未产生漂移。

- [机器发布证据](implementation/validation-0.10.0.json)：来源、Schema、专项失效校验、构建和解压检查。
- [独立文字试写与复核](../evals/results/combat-0.10.0/review.md)：16题初测，发现2题距离问题，补规则后另行2题重测；保留原始不足与声音汇总修正，不声称全量重跑或媒体通过。
- [日常安装与新进程发现](implementation/host-installed-0.10.0.json)：personal插件installed/enabled为0.10.0，195文件与发布包一致，唯一启用路径为新版缓存。当前桌面任务的已加载上下文未热替换。
- [交付与边界](implementation/combat-0.10.0-delivery.md)：各工作包、旧版本备份、LibTV交接与未完成的媒体环节。

发布包：[combat-director-0.10.0.zip](../dist/combat-director-0.10.0.zip)。SHA-256：`3d3ce93304c6a7de5f92943fb59bf2354c7df4557fba2041735d5a5c7e9bad20`。

LibTV本地构建提供完整Markdown、可粘贴正文与候选ZIP；格式构建不证明站内导入。未执行收费生成、未重新核验平台实际输入，未验证新版视频效果或成功率。未运行新版Linux/Python3.10环境；本报告记录优化验收状态，后续Git发布状态以仓库历史为准。

复现工程检查：在仓库根运行 `.venv/Scripts/python.exe scripts/validate_release.py` 与 `python scripts/build_libtv.py`。安装验证脚本位于 `evals/host-0.10.0/verify_installed.py`，只查询新CLI进程发现并比对缓存，不执行模型任务。
