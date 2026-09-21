import hashlib
import json
from pathlib import Path

root = Path(r'D:\Temp\combat-director-evals-20260921\final-e02')
skill = Path(r'D:\study\projects\combat-director\evals\candidates\0.5.0\skills\combat-director')
source = Path(r'D:\study\projects\combat-director\evals\baselines\0.2.0\skills\combat-director\examples\grounded-15.plan.json')
logs = [json.loads(line) for line in (root/'work/tool-reads.jsonl').read_text(encoding='utf-8').splitlines()]
read_paths = {f for entry in logs for f in entry['read_files']}
read_paths.update(str(skill/x) for x in [
 'SKILL.md', 'references/contract.md', 'references/action-contract.md',
 'references/choreography.md', 'references/templates.md',
 'assets/combat-plan.schema.json', 'scripts/combat_tool.py'
])
read_paths.update(str(root/x) for x in [
 'work/run_tool.py', 'work/revise.py', 'work/receipt.py', 'work/finalize.py',
 'work/tool-reads.jsonl', 'work/migrated.plan.json', 'work/review-input.json',
 'work/review-input-final.json', 'work/source-sha256.txt',
 'combat-plan.json', 'prompt.txt', 'director.md'
])
plan = json.loads((root/'combat-plan.json').read_text(encoding='utf-8'))
prompt = (root/'prompt.txt').read_text(encoding='utf-8')
director = (root/'director.md').read_text(encoding='utf-8')
initial_hash = (root/'work/source-sha256.txt').read_text(encoding='utf-8').strip()
final_hash = hashlib.sha256(source.read_bytes()).hexdigest()
assert initial_hash == final_hash
assert plan['duration'] == 15 and plan['timing']['result_at'] == 14.4
assert len(plan['beats']) == 6 and len(plan['sections']) == 4
assert '木杖' in plan['cast'][0]['prop'] and '左手空手' in plan['cast'][0]['hand']
assert all(tag in prompt for tag in ['<动作>', '<表情>', '<情绪>', '<运镜>', '<特效>', '<环境反馈>', '<声音>', '<连续性>'])
assert all(track in director for track in ['1. 人物攻防', '2. 表演情绪', '3. 摄影机', '4. 特效', '5. 环境反馈', '6. 声音'])
run = {
 'task':'把指定15秒战斗计划中A的长剑改成木杖，保留结尾，交付修订计划及可复制提示词；不实际生成。',
 'skill': str(skill/'SKILL.md'),
 'input': str(source),
 'output_directory': str(root),
 'actual_read_files': sorted(read_paths),
 'read_file_scope':'列出作为任务上下文读取或由本次本地处理读取的技能、输入和产物文件；脚本运行读到的既有pyc也列入；不枚举Python标准库和操作系统运行时。',
 'tools_used': [
  {'name':'functions.exec', 'purpose':'编排已授权本地工具调用'},
  {'name':'tools.exec_command', 'purpose':'PowerShell读取指定文件、创建输出目录，Python 3.13.3执行迁移、编辑、编译、比对凭据应用、结构校验与文本导出'},
  {'name':'tools.apply_patch', 'purpose':'在指定输出目录写入本次辅助脚本与交付说明'}
 ],
 'skill_commands': [{'arguments':x['command'], 'exit_code':x['exit_code']} for x in logs],
 'source_sha256_before':initial_hash,
 'source_sha256_after':final_hash,
 'source_unchanged':initial_hash==final_hash,
 'limits_observed': [
  '未读取记忆。',
  '未读取其他技能版本；唯一跨版本输入为明确指定的0.2.0 grounded-15.plan.json。',
  '未读取研究报告或评估结果。',
  '未联网、未调用生成平台、未上传素材、未消费积分。',
  '未委派；本次编辑和语义比对由当前执行代理完成。',
  '未改动源计划；所有主动写入均位于指定输出目录，Python禁用字节码写入。',
  '未对任务效果评分，未猜测模型名称或token使用量。'
 ],
 'delivery_limits': [
  '离线编排与结构校验不构成视频效果验证。',
  '平台模型未指定、能力未实查；generic交接保持待核验状态。',
  '木杖尺寸与世界方位细化为编排假设；声音为创作建议。'
 ],
 'deliverables':[str(root/x) for x in ['README.md','combat-plan.json','prompt.txt','director.md','design-card.md','handoff.md','review.md','prompt-handoff.json','run.json']]
}
(root/'run.json').write_text(json.dumps(run,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
print('run.json written; source SHA-256 unchanged; deliverables present.')
