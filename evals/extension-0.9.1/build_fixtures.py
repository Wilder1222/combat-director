"""Make deterministic synthetic stills for evidence-boundary behavior tasks.

Pillow is evaluation-only. These diagrams are not generated video evidence.
"""
from pathlib import Path
import hashlib
import json
from PIL import Image, ImageDraw


ROOT = Path(__file__).resolve().parent


def frame(label, staff_a, staff_b, ghosts=False):
    image = Image.new('RGB', (720, 400), '#f3f1ec')
    d = ImageDraw.Draw(image)
    d.rectangle((18, 50, 702, 362), outline='#8d8e8e', width=2)
    d.line((20, 335, 700, 335), fill='#858585', width=2)
    d.text((24, 16), 'SYNTHETIC GEOMETRIC TEST - NO AUDIO', fill='#202020')
    d.text((24, 375), label, fill='#202020')
    for x, color, letter in ((255, '#596778', 'A'), (470, '#89734f', 'B')):
        d.ellipse((x-15, 103, x+15, 133), fill=color)
        d.line((x, 135, x, 240), fill=color, width=10)
        d.line((x, 240, x-28, 331), fill=color, width=8)
        d.line((x, 240, x+27, 331), fill=color, width=8)
        d.text((x-4, 83), letter, fill='#202020')
    if ghosts:
        for shift, color in ((60, '#e6e0d5'), (34, '#d8cbbb')):
            d.line((285+shift, 169, 391+shift, 151), fill=color, width=8)
        d.line((322, 194, 427, 194), fill='#b3b9bd', width=2)
        d.polygon(((427,194),(415,189),(415,199)), fill='#b3b9bd')
    for x, staff, color in ((255, staff_a, '#596778'), (470, staff_b, '#89734f')):
        start, end = staff
        d.line((x, 151, start[0], start[1]), fill=color, width=7)
        d.line((*start, *end), fill='#8a5632', width=7)
    return image


def main():
    out = ROOT / 'fixtures'
    out.mkdir(exist_ok=True)
    specs = [
        ('synthetic-i2v-start.png', 'START IMAGE - DIRECTION CUES ARE DRAWN', ((285,169),(391,151)), ((440,179),(410,270)), True),
        ('synthetic-frame-0000.png', 'TEST FRAME t=0.0s', ((285,164),(337,92)), ((440,170),(377,245)), False),
        ('synthetic-frame-0500.png', 'TEST FRAME t=0.5s', ((285,164),(428,234)), ((440,165),(331,240)), False),
        ('synthetic-frame-1000.png', 'TEST FRAME t=1.0s', ((285,201),(327,285)), ((440,165),(403,91)), False),
    ]
    records = []
    for name, label, a, b, ghosts in specs:
        path = out / name
        frame(label, a, b, ghosts).save(path, optimize=False)
        records.append({'path': name, 'sha256': hashlib.sha256(path.read_bytes()).hexdigest(), 'width': 720, 'height': 400})
    (out / 'manifest.json').write_text(json.dumps({
        'format': 'synthetic-still-fixtures/1',
        'provenance': 'Locally drawn geometric diagrams; not extracted from video.',
        'audio': 'No audio asset exists.',
        'timing': 'Labels are synthetic test coordinates, not observed real footage timestamps.',
        'files': records,
    }, ensure_ascii=False, indent=2) + '\n', encoding='utf-8')
    print(json.dumps({'images': len(records), 'directory': str(out)}))


if __name__ == '__main__':
    main()
