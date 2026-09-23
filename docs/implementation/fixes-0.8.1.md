# 0.8.1 审阅问题修复记录

日期：2026-09-23。落实[审阅](../reviews/2026-09-23-0.8.0-review.md)中R01、R02、R03，对应[计划](../plans/2026-09-23-0.8.0-optimization-plan.md)的WP01—WP03。库索引仍为2，Combat Plan仍为1.2；116张卡和六套结构化案例保持原有范围。

## R01：正式构建遗漏生成一致性检查

`scripts/project.py build`和`validate-release`现在共同检查固定来源哈希、生成卡、catalog、覆盖清单及生成文件登记。完整发布流程调用同一入口。只改生成正文、索引、配方、来源或关联权威而未正确重建，均拒绝正式打包。

构建先在dist目录写临时ZIP，完成CRC和文件清单检查后替换版本包。预检、写入或CRC失败都保留原ZIP。`project.py validate`继续只检查运行资源；解压包无需携带上游完整快照或开发脚本。

回归证据：`tests/test_release_build.py`覆盖五类漂移、旧ZIP保护、重复构建、故障注入及无来源的运行资源验证。

## R02：跨分类筛选漏掉已有内容

新增编辑权威`sources/editorial/arvin-facets.json`，逐卡登记18张编排、15张镜头、4张特效卡的武学、角色和场面关联，并说明来源行段或改编依据。生成器校验卡ID和关联值后写入catalog；不通过任意全文关键词推断关联。

`顶心肘 + 八极拳`可找到八极连段，`白鸽 + 白鸽角色`可找到角色特效表；火焰绯雪与冰霜兵器仍独立。镜头的群战、追逐等范围按具体方法复核。`library_tool.py stats`新增`facets_by_kind`，显示每类实际登记的筛选值。

关联仍是卡片级。共享卡被角色/流派筛选命中不代表其中每一行都适用；空关联表示未登记，场面标签表示候选改编范围，均不代表视频验证或能力授权。逐招详情和精确行定位属于WP04。

回归证据：`tests/test_arvin_library.py`覆盖技法、角色、编排、特效四类组合查询，错误流派/角色排除，版本区别与镜头范围；发布流程另在解压包中执行两组问题查询和分类统计。

## R03：生成器不能安全退役旧卡

新增`scripts/generated_files.py`及`sources/editorial/arvin-generated.json`。登记覆盖109张来源卡、catalog、覆盖清单，共111个输出；初次登记前已核对原生成结果，随后由生成器维护内容哈希。

重建先计算新增、更新、退役清单，再暂存新内容、备份和恢复日志。只有已登记且字节未被修改的旧文件可以退役；未登记同名文件、人工修改和越界/链接路径在写入前阻止操作。应用失败尝试恢复原字节；恢复也失败或发生中断时保留日志与锁，阻止继续生成和正式发布。

维护命令（仓库根目录）：

```powershell
python scripts/build_arvin_library.py --plan
python scripts/build_arvin_library.py
python scripts/build_arvin_library.py --check
python scripts/project.py validate-release
python scripts/validate_release.py
```

发生中断后，应先确认原生成进程已结束，再执行`python scripts/build_arvin_library.py --recover`恢复前一状态，然后重新生成。恢复时若发现后续人工编辑，保留现场并报错；不要直接删除锁或修改登记哈希来绕过保护。此机制覆盖进程中断和可注入的文件I/O失败，不承诺操作系统掉电后的磁盘持久性。

回归证据：`tests/test_generated_files.py`覆盖只读预览、重命名、用户文件保护、暂存失败、安装失败回滚、显式恢复和恢复冲突；`tests/test_release_build.py`还在完整临时仓库中重命名真实配方并验证旧卡不再入包。

## 验证与范围

完整命令输出、测试结果、ZIP文件哈希及重建结果见[当前验证报告](../validation.md)和[0.8.1机器证据](validation-0.8.1.json)。审阅阶段的[0.8.0复现证据](../reviews/2026-09-23-0.8.0-evidence.json)原样保留。

WP04逐招详情、WP05紧凑读取、WP06独立创作行为比较尚未实施。此次没有视频生成或安装升级；LibTV单文件保持原样。修复完成后，按用户“提交推送”将本批修复与此前未提交的0.8.0资料吸收一起交付当前分支。
