"""Build the two motion examples from authored plans and explicit review receipts."""
from __future__ import annotations

import argparse
import importlib.util
import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
NAMES = ('motion-staff-12', 'motion-blade-12')


def render(root: Path) -> dict[str, bytes]:
    skill = root / 'skills/combat-director'
    spec = importlib.util.spec_from_file_location('motion_example_tool', skill / 'scripts/combat_tool.py')
    tool = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(tool)
    outputs = {}
    for name in NAMES:
        source = root / 'sources/editorial/0.8.3'
        plan = tool.read_json(source / f'{name}.plan.json')
        if plan['id'] != name or plan['editorial_reviews']:
            raise ValueError('Expected an unreviewed source plan with its declared ID: ' + name)
        receipt = tool.read_json(source / f'{name}.review.json')
        plan = tool.apply_review(plan, receipt)
        tool.validate(plan)
        payloads = tool.deliverables(plan, 'generic', as_of='2026-09-23')
        prefix = f'skills/combat-director/examples/{name}'
        outputs[prefix + '.plan.json'] = payloads['combat-plan.json'].encode('utf-8')
        outputs[prefix + '.prompt.txt'] = payloads['prompt.txt'].encode('utf-8')
        notes = ['# 运动成像教学例 · ' + name, '',
                 '由源计划与作者复核凭证生成，修改权威后重建。正常速度、单次12秒为设计意图；未生成视频、未验证平台时长或真实曝光设置。', '',
                 f'[结构化计划]({name}.plan.json) · [可复制提示词]({name}.prompt.txt) · [方法](../references/motion-blur.md)', '',
                 payloads['design-card.md'], '', payloads['director.md'], '',
                 '## 可复制提示词', '', '```text', payloads['prompt.txt'].rstrip(), '```', '',
                 '## 作者文本复核', '', '以下是作者语义对读，不是独立评价、物理模拟或视频验收。', '']
        for review in receipt['reviews']:
            notes.append(f'- {review["scope"]}：' + ' '.join(review['checks'].values()))
        outputs[prefix + '.md'] = ('\n'.join(notes) + '\n').encode('utf-8')
    return outputs


def check_outputs(root: Path, outputs: dict[str, bytes]) -> None:
    for name, expected in outputs.items():
        target = root / name
        if not target.is_file() or target.read_bytes() != expected:
            raise ValueError('Motion example is stale or missing: ' + name)


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--check', action='store_true')
    args = parser.parse_args()
    outputs = render(ROOT)
    if args.check:
        check_outputs(ROOT, outputs)
    else:
        for name, content in outputs.items():
            (ROOT / name).write_bytes(content)
    print(f'PASS: {len(NAMES)} reviewed motion plans; {len(outputs)} derived files' + (' unchanged' if args.check else ' rebuilt'))


if __name__ == '__main__':
    main()
