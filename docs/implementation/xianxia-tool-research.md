# 仙侠工具迁移：时间证据、兼容性与内容范围

2026-10-09（Asia/Shanghai）。源提交 `f3721de6e21af8cd5186c88079bf92d252ec416e`。本记录覆盖计划 X49、X53 与原案例保全；构建保护 X54 另由统一构建实现。精确函数、测试及案例对应见 [工具迁移映射](xianxia-tool-mapping.json)。

## 一手调研与采用决定

| 官方材料 | 可核对事实 | 当前采用 |
| --- | --- | --- |
| [FFmpeg 时间戳与帧模式](https://ffmpeg.org/ffmpeg.html#Advanced-options) | `passthrough` 传递帧时间戳；CFR 可增删帧；`copyts` 保留输入起点，但不能保证所有后续处理都保持时间戳 | 不用名义 FPS 计算选帧。探测整数 PTS 与有理时间基，按首视频帧为零点的左闭右开区间选取真实帧序号，再独立核对解码滤镜的 PTS |
| [FFprobe 的帧信息](https://ffmpeg.org/ffprobe.html#Main-options) | `show_frames` 输出逐帧信息，`show_entries` 可限制字段 | 保存选中视频轨元数据和完整时间字段；首帧非零、可变帧率、未知末帧时长分别处理，不从平均帧率补造持续时间 |
| [FFmpeg 的 select 与 showinfo](https://www.ffmpeg.org/ffmpeg-filters.html#showinfo) | `select` 的 `n` 为实际输入帧计数；`showinfo` 提供滤镜输入 PTS、时间基相关信息、尺寸和像素比例 | `select=eq(n,...)` 后接 `showinfo`。抽取日志须与独立探测清单逐项相等；不同时间基或不同 PTS 使清单标为失败 |
| [FFmpeg 自动旋转与缩放](https://ffmpeg.org/ffmpeg.html#Video-Options) | 自动旋转和按首帧分辨率自动缩放默认开启 | 保留源像素网格时同时显式禁用 `autorotate` 和 `autoscale`。这是本次对源实现的补全：原代码已禁旋转，但未显式禁默认缩放。保留旋转、SAR、色彩和位深元数据供播放器核查 |
| [Python 3.10 hashlib](https://docs.python.org/3.10/library/hashlib.html) 与 [file_digest 的引入版本](https://docs.python.org/3/library/hashlib.html#hashlib.file_digest) | SHA-256 的重复 `update` 等价于拼接输入；`file_digest` 从 Python 3.11 提供 | 使用 1 MiB 分块读取和标准库 `sha256().update()`，不增加依赖、不改哈希含义。多块内容和禁用 `file_digest` 的测试证明覆盖完整字节 |
| [Pillow Python 支持表](https://pillow.readthedocs.io/en/stable/installation/python-support.html) 与 [9.1.0 Resampling API](https://pillow.readthedocs.io/en/stable/releasenotes/9.1.0.html) | 支持表包含 Python 3.10；9.1.0 已提供 `Image.Resampling.LANCZOS` | Pillow 只在真正抽帧时导入并核验 Resampling API。缺 Pillow、缺 FFmpeg 或旧 API 时明确失败且不建输出；普通导入/写作不受影响。未自动安装任何软件 |
| [Pillow 图像模式](https://pillow.readthedocs.io/en/stable/handbook/concepts.html#modes) 与 [thumbnail](https://pillow.readthedocs.io/en/stable/reference/Image.html#PIL.Image.Image.thumbnail) | `RGB` 是每通道 8 位；thumbnail 会修改加载的图像并保留宽高比 | 原 PNG 不经 Pillow 重写；仅联系表缩略图采用 Lanczos。FFmpeg `rgb24` 转换会丢失原高位深，也未显式做 HDR 色调映射或显示色彩管理；静帧颜色不能替代原媒体审阅 |

## 统一接口与范围

抽帧脚本位于 [sample_video.py](../../skills/combat-director/scripts/sample_video.py)，保留本地单文件输入、已有输出保护、120 秒子进程上限、1–120 帧显式上限、拒绝隐式截断、源变更检测、逐 PNG 与联系表 SHA-256、`incomplete → artifacts_created / failed` 状态。所有人工审阅位默认 false；抽帧成功不表示接触、原速、连续性、音轨或视觉质量通过。

[validate_content.py](../../scripts/validate_content.py) 提供：

- `validate_links(root, *, scan_paths=None, exclude=DEFAULT_EXCLUDES)` 返回 `(errors, checked)`。
- `validate_content(root, *, scan_paths=None, exclude=DEFAULT_EXCLUDES, timeline_paths=DEFAULT_TIMELINES)` 返回错误、范围与各机械检查计数。
- CLI 可重复指定 `--scan`、`--exclude`、`--timeline`；`--skip-timelines` 用于不含维护案例的独立包。未指定时间轴时检查迁入的 `behavior-regression.md`。

默认扫描排除来源快照、私有来源、虚拟环境、输出、构建及缓存目录。排除只影响被扫描文档，公开文档的目标仍须存在、位于检查根目录内，且不得位于 `.local-evidence`、`sources/private`、`outputs`、`dist` 等本机目录。绝对本机文件、UNC 与 file URI 不会冒充外部 URL 通过。来源快照保留原仓库引用，不用这些历史内部链接误判当前运行内容；显式取消排除仍可审查快照。

Markdown 检查支持当前文档实际使用的 ATX 标题和行内链接：同文/跨文锚点、URL 编码路径与锚点、重复标题后缀、常用行内格式、闭合井号、反引号/波浪围栏、角括号路径及链接标题。它没有声称实现所有 Markdown 扩展，也不验证外部 URL。时间检查只针对案例的串行成片预算窗口，不禁止一个窗口内多人的并发攻防。

## 运行证据

本机 Python 3.13.3、Pillow 12.1.1、FFmpeg/FFprobe 8.1.1。已执行全部 17 项源抽帧测试和新增依赖/兼容测试，无跳过。真实工具测试生成临时无损片核对非零 PTS 的 VFR 帧、真实帧步长、像素、旋转与 SAR、10 位 BT.2020/PQ 标签；同时检查损坏片、播放列表、源变化和验证失败状态。临时片由测试自行生成并清理，未触动来源原媒体，未生成收费视频。

Python 3.10 使用的语法由 AST 的 3.10 模式核对，兼容哈希和缺依赖行为已实测；当前没有 Python 3.10 解释器运行证据，不能把语法检查写成该版本完整运行通过。

源结构测试 24 项已原名迁入，另增加扫描范围、来源排除、私有路径、包接口与案例忠实性测试。迁入案例保留全部正文，只调整当前规则、校验脚本及固定来源研究的相对引用。结构计数为 28 个目标时长案例、30 个片段；26 个素材条件案例及其他条件/执行边界记录保留，不用数量宣称创作质量。历史文中旧数量保留原义。

初次全仓检查发现既有 `docs/combat-research-plan.md` 和 `docs/validation.md` 共 54 条 `outputs/current` 依赖，交由主融合更新公开文档；未通过删媒体、扫描豁免或弱化目标检查绕开。集成后的最终结果与受测内容指纹见映射记录，不把此阶段结果当作最终发布验收。
