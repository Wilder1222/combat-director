from pathlib import Path
import contextlib
import hashlib
import io
import json
import runpy
import sys

ROOT = Path(r'D:\study\projects\combat-director\evals\candidates\0.5.0\skills\combat-director')
OUT = Path(r'D:\Temp\combat-director-evals-20260921\final-e04')
PLAN = ROOT / 'examples/epic-30.plan.json'
PROFILE = Path(r'D:\study\projects\combat-director\evals\fixtures\synthetic-limit-15.json')
TOOL = ROOT / 'scripts/combat_tool.py'
reads = set()

def audit(event, args):
    if event == 'open' and isinstance(args[0], (str, bytes)):
        path = Path(args[0]).resolve()
        mode = args[1]
        if isinstance(mode, str) and ('r' in mode or '+' in mode):
            reads.add(str(path))

sys.addaudithook(audit)
sys.dont_write_bytecode = True

def write(name, body):
    path = OUT / name
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(body, encoding='utf-8')

def write_json(name, value):
    write(name, json.dumps(value, ensure_ascii=False, indent=2) + '\n')

def invoke(name, args):
    old = sys.argv[:]
    sys.argv = [str(TOOL)] + args
    stdout, stderr = io.StringIO(), io.StringIO()
    exit_code = 0
    try:
        with contextlib.redirect_stdout(stdout), contextlib.redirect_stderr(stderr):
            runpy.run_path(str(TOOL), run_name='__main__')
    except SystemExit as error:
        exit_code = error.code if isinstance(error.code, int) else 1
    finally:
        sys.argv = old
    result = {'name': name, 'argv': [str(TOOL)] + args, 'exit_code': exit_code, 'stdout': stdout.getvalue(), 'stderr': stderr.getvalue()}
    write_json('checks/' + name + '.json', result)
    return result

plan_bytes = PLAN.read_bytes()
profile_bytes = PROFILE.read_bytes()
plan = json.loads(plan_bytes.decode('utf-8-sig'))
profile = json.loads(profile_bytes.decode('utf-8-sig'))
checks = [
    invoke('plan-validation', ['validate', str(PLAN)]),
    invoke('duration-validation', ['validate', str(PLAN), '--max-duration', '15']),
    invoke('profile-assessment', ['assess-profile', str(PLAN), '--profile', str(PROFILE), '--as-of', '2026-09-21']),
    invoke('blocked-render', ['render', str(PLAN), '--profile', str(PROFILE), '--as-of', '2026-09-21', '--out-dir', str(OUT / 'platform-export')]),
]
write_json('checks/results.json', checks)
assessment = json.loads(checks[2]['stdout'])
write_json('capability-assessment.json', assessment)
(OUT / 'source-plan.json').write_bytes(plan_bytes)
(OUT / 'synthetic-profile.json').write_bytes(profile_bytes)

def cell(text):
    return str(text).replace('|', '\\|').replace('\n', '<br>')

def t(value):
    return f'{value:g}'

design = '''# 战斗设计卡：epic-30

交付性质：离线创作资料。合成入口时长冲突，平台正式导出被阻止；本文件不表示可以向该入口提交。

来源为指定快照 examples/epic-30.plan.json，原文件按字节保存在 source-plan.json；没有修改时长、生成次数、人物能力或结尾。原计划自述为独立测试片，不写入已有剧情正史；细节拍与能力结束条件是原项目编辑补充。没有参考媒体输入，也未观看或实听生成素材。

| 约束 | 内容 |
| --- | --- |
| 战斗目标 | A 打破封锁并压制风暴形态，不追求杀伤；B 阻止 A 前进 |
| 优势与转折 | B 最初阻路追压；A 以交手留下三印记并形成剑阵；B 屏障破裂后由同一身体转成风柱；A 利用核心转向迟缓回收阵列落下巨剑 |
| 时长与模式 | 总长 30 秒，单次生成，16:9，允许内部切镜；不是一镜到底 |
| 余量 | 开头 0.3 秒、结尾 0.8 秒都包含在 30 秒内；29.2 秒前完成压制 |
| 场景 | 开阔戈壁，远方孤岩、灰蓝云层、中性日光；三处金白印记逐步形成 |
| 空间 | A 初始西侧，B 初始东侧，彼此面向；机位保持南侧；移动必须可见 |
| 结尾 | B 在原地缩回人形核心、暂时受压；A 放低右手剑保持警戒；尘土沉降 |
| 表现边界 | 场地级仙侠能力；两名成年虚构角色；无台词、无背景音乐，不增加旁观者或无依据死亡特写 |

## 人物与能力

'''
design += plan['headers']['cast'] + '\n\n'
design += '| 能力 / 归属 | 触发 | 可见表现 | 限制 | 代价 | 结束条件 |\n| --- | --- | --- | --- | --- | --- |\n'
for a in plan['abilities']:
    design += '| ' + ' | '.join(cell(a[k]) for k in ['id', 'trigger', 'visual', 'limit', 'cost', 'end_condition']).replace(cell(a['id']), cell(a['id'] + ' / ' + a['owner']), 1) + ' |\n'
design += '\n假设继承原计划：独立测试片、真人仙侠影视外观、自然肤质与真实衣料。没有新增平台能力假设。能力允许幻想，但规模不超出既有场地。\n'
write('creative-draft/design-card.md', design)

director = '# 六轨导演时间轴：30 秒创作稿\n\n离线草稿；15 秒合成入口不可提交。时间点是导演意图，不是平台逐秒硬参数。六轨为人物攻防、表演情绪、摄影机、特效、环境反馈、声音；时间列独立于六轨。\n\n'
director += '| 时间 / 节拍 | 人物攻防 | 表演情绪 | 摄影机 | 特效 | 环境反馈 | 声音 |\n| --- | --- | --- | --- | --- | --- | --- |\n'
for b in plan['beats']:
    actions = '；'.join(f'{actor}：{info["action"]}' for actor, info in b['actors'].items())
    performances = '；'.join(f'{actor}：{info["performance"]}' for actor, info in b['actors'].items()) + '；情绪：' + b['emotion']
    camera = f'{b["camera"]["shot_id"]} / {b["camera"]["transition"]} / {b["camera"]["side"]}：{b["camera"]["path"]}'
    row = [f'{t(b["start"])}–{t(b["end"])} 秒 / {b["id"]}', actions, performances, camera, b['vfx'], b['environment'], b['sound']]
    director += '| ' + ' | '.join(cell(x) for x in row) + ' |\n'
director += '\n## 连续性状态\n\n开场：A 在西侧、面向 B，右手银色直剑；B 在东侧阻路、面向 A，右手青色能量短刃；南侧机位。孤岩是固定锚点，三处印记尚待逐步形成。\n\n'
director += '| 拍末 | A | B | 本拍环境变化 | 下一拍起点 |\n| --- | --- | --- | --- | --- |\n'
for i, b in enumerate(plan['beats']):
    next_id = plan['beats'][i+1]['id'] if i + 1 < len(plan['beats']) else '成片结束'
    director += '| ' + ' | '.join(cell(x) for x in [b['id'], b['after']['A'], b['after']['B'], b['environment'], next_id + ' 继承本拍状态']) + ' |\n'
director += '\n所有机位保持南侧；实体兵器及右手不变。B 屏障碎裂、原身体显露、青光沿身体上旋、沙尘包围成柱按序可见。已有剑影命中消散或回收，不能重新无代价复制。衣着没有新增损伤设定，不擅自添加破衣、断刃或环境复位。原计划 environment 长字符串保存累计事件；其中早期“尚无印记”等句是历史，不能解释为后续状态回退。\n\n开头 0.3 秒与末尾 0.8 秒属于上述总时长；29.2 秒前到达结尾结果，29.2–30 秒继续自然沉降与呼吸。声音均为设计建议，未实听。\n'
write('creative-draft/director.md', director)

prompt = '离线创作草稿：保留单次 30 秒；当前 15 秒合成入口存在冲突，禁止作为该入口可执行交接。\n\n'
for key in ['goal', 'cast', 'scene', 'budget', 'continuity']:
    prompt += plan['headers'][key] + '\n\n'
prompt += '<连续性>能力结束条件：' + '；'.join(a['id'] + '：' + a['end_condition'] for a in plan['abilities']) + '。\n\n'
beat_map = {b['id']: b for b in plan['beats']}
tags = [('action', '动作'), ('expression', '表情'), ('emotion', '情绪'), ('camera', '运镜'), ('vfx', '特效'), ('environment', '环境反馈'), ('sound', '声音'), ('continuity', '连续性')]
for s in plan['sections']:
    start = beat_map[s['beat_ids'][0]]['start']
    end = beat_map[s['beat_ids'][-1]]['end']
    prompt += f'{s["id"]}｜{t(start)}–{t(end)} 秒\n'
    for key, tag in tags:
        prompt += f'<{tag}>{s["summary"][key]}\n'
    prompt += '\n'
write('creative-draft/prompt-draft.txt', prompt)

handoff = '''# 平台交接：因时长冲突暂停

截至 2026-09-21，指定的合成入口只记录单次上限 15 秒，原计划要求单次 30 秒。两者冲突，正式平台导出被阻止。原计划保留 30 秒 / single，没有缩短、拆成两次、拼接、换平台或执行生成。独立于平台的创作稿已放入 creative-draft/，不构成该入口的可执行方案。

## 入口身份和证据

| 字段 | 记录 |
| --- | --- |
| display_name | 仅用于离线评估的合成入口 |
| platform | synthetic-test |
| model | fixture-only |
| entry | offline-test |
| mode / account_scope | single / synthetic-only |
| max_duration | supported，15 秒 |
| 来源 | synthetic fixture, not real provider evidence |
| 适用范围 | offline-evaluation-only |
| checked_at / expires_at | 2026-09-21 / 2026-10-21 |
| 本次检查日期 | 2026-09-21，使用 --as-of 固定 |

这份证据只支持离线合成测试结论；不是 LibTV、小云雀、Seedance 或任何真实服务商的能力证据。当前日处于配置有效期内，所以不是“未知上限”或“证据过期”，而是明确时长冲突。

## 设置与素材清单

| 项目 | 计划要求 | 交接状态 |
| --- | --- | --- |
| 生成次数、时长 | 单次 30 秒 | blocked：比所给上限多 15 秒 |
| 画幅 | 16:9 | 配置未声明支持，待真实入口证据 |
| 镜头 | 单次任务内允许切镜 | 配置未声明支持，待核验 |
| 声音 | 事件音效，无台词与背景音乐 | 能力未知；当前声音只是设计建议 |
| 参考图、参考视频 | 原计划 references 为空 | 无素材可用性或绑定声明，没有上传 |
| 首帧、尾帧、视频参考 | 当前计划均未要求 | 不启用；配置没有相应能力证据 |
| 局部重拍 | 当前未请求 | 不启用；能力未知 |
| 模型 ID、接口参数、账号限制 | 只有合成标识 | 未据此臆造生产 ID、按钮或调用参数 |
| 提交、积分、生成、发布 | 用户要求离线且不实际生成 | 均未执行；没有任务 ID 或生成回执 |

## 后续决策

用户已明确保留单次 30 秒，本次不会请求将计划缩到 15 秒或改为两段拼接。当前入口交接维持阻止；要恢复正式交接，需要用户指定一个有当前证据证明支持单次至少 30 秒的入口，再核验其画幅、镜头、声音和账号能力。这是后续入口选择与证据条件，不是本次已完成的操作；本次不选择或接触真实平台。

若未来用户主动改变目标或生成路径，应另行改写并复核对应方案；不能将拼接成片称为 30 秒单次直出。

## 交付清单

- source-plan.json：输入计划原字节副本，保留现有复核声明。
- synthetic-profile.json：本次合成能力配置原字节副本。
- capability-assessment.json：指定日期的脚本能力检查结果。
- checks/：计划结构校验、15 秒上限校验、能力检查与受阻导出的原始 stdout、stderr、退出码。
- creative-draft/design-card.md：目标、人物与能力边界。
- creative-draft/director.md：11 拍六轨时间轴及逐拍连续性。
- creative-draft/prompt-draft.txt：6 个主段的中文创作提示词，明确标为当前入口不可执行。
- review.md：后续成片验收要点和本次检查范围。
- run.json：实际读取文件及工具记录。

没有平台可执行导出包，也没有生成视频。原计划的复核声明、哈希和校验结果都不能替代平台能力证据或成片验收。
'''
write('handoff.md', handoff)
review = '''# 检查记录与验收要点

本次仅进行离线文本与能力配置检查。计划原文与配置已保留；机器检查结果见 checks/。结构校验不证明动作物理效果、人物稳定或生成成功。原计划携带的 editorial_reviews 是输入记录，没有冒充本次新签发复核；没有改动事实、表达或刷新其哈希。

本次入口冲突是 30 秒单次要求超出 15 秒上限。即使计划结构通过，平台交接仍为 blocked。所给配置只是合成样本，不能推断真实平台能力。

未来在已解决入口冲突且实际取得成片后，逐项验收：

- 成片总长 30 秒，开头 0.3 秒及结尾 0.8 秒包含在总长内。单个成片文件不能证明单次生成，需实际任务回执支持生成次数。
- A、B 两名成年角色身份、服装、实体武器形状与右手持械连续，人物移动可见；摄影机维持南侧空间关系。
- 剑刃交接先发生，随后身体受力；三印记由剑尖先后留下，阵列在第三印记成立后出现。
- 两波剑影冲击使 B 后退、屏障出现裂纹；命中剑影消散，能力存在动作幅度与呼吸代价。
- 屏障破裂后 B 原身体仍可见，青光沿同一身体上旋形成风柱；不存在爆闪换角色。
- 核心转向迟缓，A 沿印记外缘可见移动、拨开飞石；三印记与孤岩未被全部遮蔽。
- A 站稳触印后回收余下阵列；巨剑只在圈定范围落下一次。29.2 秒前完成压制，B 原地缩回人形核心，A 仅警戒，末尾尘土自然沉降。
- 无新增角色、死亡特写、无代价复制剑阵、瞬移、换武器或环境复位。
- 声音逐事件对应碰撞、脚步、擦地、屏障、风、拨石、巨剑与呼吸；无台词、无背景音乐。当前只是声音设计，尚未实听。

验收状态：未取得成片，以上项目均未进行媒体验收。
'''
write('review.md', review)

consulted = [ROOT / 'SKILL.md', ROOT / 'references/platforms.md', ROOT / 'references/contract.md', ROOT / 'assets/platform-profiles.json', PLAN, PROFILE, TOOL]
run = {
    'task': '为原计划准备离线平台交接，保留单次 30 秒，不实际生成',
    'as_of': '2026-09-21',
    'skill_snapshot': str(ROOT),
    'output_directory': str(OUT),
    'status': 'blocked_duration_conflict',
    'requested_duration': 30,
    'requested_generation': 'single',
    'profile_max_duration': 15,
    'input_sha256': {'plan': hashlib.sha256(plan_bytes).hexdigest(), 'profile': hashlib.sha256(profile_bytes).hexdigest()},
    'files_read_directly_for_task': [str(x) for x in consulted],
    'files_read_by_python_execution': sorted(reads),
    'tools_used': [
        {'name': 'functions.exec', 'purpose': '调用本地读文件、帮助查询、校验、写入和核对工具'},
        {'name': 'exec_command', 'purpose': 'PowerShell Get-Content、ConvertFrom-Json、rg、Python 帮助与离线脚本'},
        {'name': 'apply_patch', 'purpose': '写入 prepare_delivery.py 以生成交付文档和保留原始检查输出'}
    ],
    'help_commands': ['combat_tool.py --help', 'combat_tool.py assess-profile --help', 'combat_tool.py validate --help', 'combat_tool.py render --help'],
    'checks': checks,
    'input_unchanged': True,
    'network_used': False,
    'platform_called': False,
    'generation_performed': False,
    'delegation_used': False,
    'memory_read': False,
    'other_versions_or_evaluation_results_read': False,
    'notes': ['files_read_by_python_execution 来自本次 Python open 审计事件；Python 标准库与已缓存模块的导入也可能在该列表中。', '直接阅读清单记录模型实际咨询的输入和说明；没有自评分数，也没有猜测模型或 token。', 'creative-draft 为保留原计划的离线创作资料，不是绕过冲突后提供的正式平台导出。']
}
write_json('run.json', run)
print(json.dumps({'status': run['status'], 'checks': [{'name': x['name'], 'exit_code': x['exit_code'], 'stdout': x['stdout'], 'stderr': x['stderr']} for x in checks], 'output': str(OUT)}, ensure_ascii=False, indent=2))
