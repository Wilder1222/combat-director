import hashlib
import json
from pathlib import Path

out = Path(r'D:\Temp\combat-director-evals-20260921\new-e02')
skill = Path(r'D:\study\projects\combat-director\evals\candidates\0.3.0\skills\combat-director')
source = Path(r'D:\study\projects\combat-director\evals\baselines\0.2.0\skills\combat-director\examples\grounded-15.plan.json')
before = json.loads((out / 'source-integrity.json').read_text(encoding='utf-8'))
after_hash = hashlib.sha256(source.read_bytes()).hexdigest()
assert before['sha256_before'] == after_hash
revised = json.loads((out / 'revised.plan.json').read_text(encoding='utf-8'))
exported = json.loads((out / 'combat-plan.json').read_text(encoding='utf-8'))
assert revised == exported
prompt = (out / 'prompt.txt').read_text(encoding='utf-8')
assert all(word not in prompt for word in ('剑格', '剑尖', '来剑', '直剑', '长剑', '收剑'))
assert '木杖' in prompt and '14.4秒前' in prompt and '最后0.6秒' in prompt
assert revised['duration'] == 15 and revised['camera_mode'] == 'one-take'
assert revised['timing'] == {'lead_in': 0.2, 'tail_out': 0.6, 'result_at': 14.4}

task_files = [
    ('SKILL.md', '直接读取技能入口'),
    ('references/choreography.md', '直接读取动作、状态与六轨编排规则'),
    ('references/contract.md', '直接读取修订、语义复核、导出契约'),
    ('assets/combat-plan.schema.json', '直接读取并由候选校验器读取结构定义'),
    ('scripts/combat_tool.py', '直接读取并执行候选编译、复核、校验、导出工具'),
    ('scripts/combat_handoff.py', '直接读取，并作为候选工具模块导入'),
    ('scripts/combat_schema.py', '候选工具运行时导入；未额外展开源码'),
    ('assets/platform-profiles.json', '候选render运行时读取，仅选择generic配置')
]
generated_reads = [
    ('edit_plan.py', 'Python执行本次创建的编辑脚本'),
    ('revised-unreviewed.plan.json', 'compile与apply-review读取本次修订稿'),
    ('review-input.json', '直接读取首次编译资料并据此修正文字和摘要标点'),
    ('review-input-final.json', '直接读取最终编译事实及表达，写复核凭据时读取摘要哈希'),
    ('write_receipt.py', 'Python执行本次创建的复核凭据写入脚本'),
    ('receipt.json', 'apply-review读取本次实际语义复核记录'),
    ('revised.plan.json', 'validate、render及导出一致性检查读取'),
    ('prompt.txt', '直接读取最终导出提示词并检查旧剑术词汇'),
    ('handoff.md', '直接读取通用平台交接清单'),
    ('combat-plan.json', '读取并与最终修订稿比较内容'),
    ('source-integrity.json', '读取修改前源文件哈希'),
    ('verify_and_record.py', 'Python执行本次创建的校验与记录脚本')
]
run = {
    'task': '把指定战斗计划中A的长剑改成木杖，保留结尾，交付修订计划与可复制提示词；不实际生成',
    'skill_path': str(skill / 'SKILL.md'),
    'input_plan': str(source),
    'output_directory': str(out),
    'read_files': [{'path': str(source), 'use': '用户指定唯一输入计划；编辑与源文件哈希检查'}]
                  + [{'path': str(skill / name), 'use': use} for name, use in task_files]
                  + [{'path': str(out / name), 'use': use} for name, use in generated_reads],
    'read_files_scope': '列出本任务实际读取的技能、输入及本次产物；不列Python与PowerShell标准运行时文件。',
    'tools_used': [
        {'name': 'functions.exec', 'use': '组织本地读写和Python工具执行'},
        {'name': 'exec_command', 'use': 'PowerShell Get-Content、Python -B运行本地脚本；没有联网命令'},
        {'name': 'apply_patch', 'use': '只在指定输出目录创建和修改本次脚本'},
        {'name': 'collaboration.send_message', 'use': '向父任务报告本次执行状态；没有委派工作'}
    ],
    'execution': [
        '读取指定候选技能、输入计划及按需编排与契约资源。',
        '在独立输出文件中将契约版本置为1.1并建立空复核记录；同步人物、武器、动作、声音、效果、状态和主段摘要。',
        '首次compile后读取事实与表达，修正B03位置描述及主段连续性标签和声音标点，再次compile。',
        '逐段比较最终事实与表达，写出具体四项语义复核记录及所审版本哈希。',
        'apply-review返回headers及P01至P04为ready。',
        'validate输出：VALID: grounded-15-wooden-staff; 6 beats, 4 sections; reviewed revision matches。',
        'render --platform generic导出7份文本或JSON文件。',
        '读取最终prompt与handoff，比较导出计划与修订计划，检查原输入哈希未变。'
    ],
    'observed_checks': {
        'source_sha256_before': before['sha256_before'],
        'source_sha256_after': after_hash,
        'source_bytes_unchanged': True,
        'rendered_plan_equals_revised_plan': True,
        'prompt_has_no_old_sword_terms': True,
        'duration_camera_and_timing_preserved': True,
        'candidate_validate_exit_code': 0,
        'candidate_render_exit_code': 0
    },
    'deliverables': ['revised.plan.json', 'combat-plan.json', 'prompt.txt', 'director.md', 'design-card.md', 'handoff.md', 'review.md', 'prompt-handoff.json', 'receipt.json'],
    'delivery_state': '已交付修订计划与可复制中文提示词',
    'restrictions_observed': [
        '未读取记忆。',
        '未读取其他版本内容，唯一例外是明确指定的0.2.0输入计划。',
        '未读取研究报告或其他评估结果。',
        '未联网、未调用生成平台、未上传或绑定素材。',
        '未委派任务；父任务状态通信不包含委派。',
        '未修改原计划或候选技能；本次写入均位于指定输出目录。',
        'Python使用-B，未要求在技能目录生成字节码缓存。',
        '未进行评分、自评或模型与token猜测。'
    ],
    'limitations': [
        '本次仅完成计划及提示词文本修订，没有生成、观看或听取视频；声音是设计建议。',
        'generic导出未核验实际平台、模型、账号入口、15秒可选时长或声音支持。',
        '木杖约1.2米、实心圆木、右手握后段为明确标注的创作假设。',
        '语义复核由本次编辑代理执行，哈希与结构检查不代表实际生成效果验证。'
    ],
    'errors': []
}
(out / 'run.json').write_text(json.dumps(run, ensure_ascii=False, indent=2) + '\n', encoding='utf-8')
print(json.dumps({'run_json': str(out / 'run.json'), 'source_unchanged': True, 'exported_plan_matches': True, 'prompt_old_sword_terms': []}, ensure_ascii=False))
