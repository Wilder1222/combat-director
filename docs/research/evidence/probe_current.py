"""Read-only 0.2.0 audit: mutate in-memory plans, never rewrite production examples."""
import copy
import hashlib
import importlib.util
import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[3]
SKILL = ROOT / 'skills/combat-director'
spec = importlib.util.spec_from_file_location('audit_combat_tool', SKILL / 'scripts/combat_tool.py')
tool = importlib.util.module_from_spec(spec)
spec.loader.exec_module(tool)
epic = tool.read_json(SKILL / 'examples/epic-30.plan.json')
grounded = tool.read_json(SKILL / 'examples/grounded-15.plan.json')
results = []


def probe(pid, description, base, mutate):
    changed = copy.deepcopy(base)
    mutate(changed)
    try:
        tool.validate(changed)
        accepted, error = True, None
    except ValueError as exc:
        accepted, error = False, str(exc)
    results.append({'id': pid, 'description': description, 'validator_accepts': accepted,
                    'prompt_changed': tool.prompt(changed) != tool.prompt(base), 'error': error})


probe('A01', 'Change actor prop only; header and prompt retain the old weapon.', epic,
      lambda p: p['cast'][0].update(prop='wooden staff'))
probe('A02', 'Change director action only; compiled prompt is unchanged.', epic,
      lambda p: p['beats'][0]['actors']['A'].update(action='停在原地并放下兵器，不再向前挥剑'))
probe('A03', 'One-take structured camera with contradictory cut in prompt summary.', grounded,
      lambda p: p['sections'][0]['summary'].update(camera='在2秒处切至北侧特写'))
probe('A04', 'Change ability cost only; prompt retains old cost.', epic,
      lambda p: p['abilities'][0].update(cost='使用后右手完全无法继续持剑'))
probe('A05', 'Use bound status with prose evidence but no asset identity or receipt.', epic,
      lambda p: p['references'].append({'id':'REF1','kind':'identity','status':'bound','actors':['A'],
          'controls':'人物身份','excludes':'动作','binding_evidence':'据说已上传'}))
plain = tool.deliverables(epic, 'generic')
platform = tool.deliverables(epic, 'xiaoyunque')
results.append({'id':'A06','description':'Compare generic and xiaoyunque deliverables.',
                'changed_files':[k for k in plain if plain[k] != platform[k]]})
schema = tool.read_json(SKILL / 'assets/combat-plan.schema.json')
try:
    tool.check_schema('abcd', {'type':'string','maxLength':1}, schema)
    ignored = True
except ValueError:
    ignored = False
results.append({'id':'A07','description':'Future maxLength keyword is silently ignored by subset checker.',
                'unknown_constraint_ignored':ignored})
payload = {'date':'2026-09-21','version':json.loads((ROOT/'.codex-plugin/plugin.json').read_text(encoding='utf-8'))['version'],
           'scope':'Diagnostic probes, not new regression tests or model behavior evaluations.',
           'source_hashes':{str(p.relative_to(ROOT)).replace('\\','/'):hashlib.sha256(p.read_bytes()).hexdigest()
                            for p in [SKILL/'scripts/combat_tool.py',SKILL/'assets/combat-plan.schema.json',SKILL/'SKILL.md']},
           'probes':results}
target = Path(__file__).with_name('probe-results.json')
target.write_text(json.dumps(payload,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
print(json.dumps(results,ensure_ascii=False,indent=2))
