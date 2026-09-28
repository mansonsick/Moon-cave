"""Render supplied BpmfGenRyuMin-H text as transparent PNGs, without copying the font.

python scripts/render_zhuyin.py --font /private/path/BpmfGenRyuMin-H.ttf \
    --manifest assets/hub-text/text.json

Requires Pillow. Review contextual pronunciation and small-screen legibility.
"""

import argparse
import json
import re
from pathlib import Path

from PIL import Image, ImageDraw, ImageFont


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--font', type=Path, required=True)
    parser.add_argument('--manifest', type=Path, required=True)
    args = parser.parse_args()
    manifest = json.loads(args.manifest.read_text(encoding='utf-8'))
    font = ImageFont.truetype(str(args.font), manifest.get('font_size', 192))
    if font.getname() != ('Bpmf GenRyu Min', 'H'):
        raise ValueError('Use the project-standard BpmfGenRyuMin-H.ttf font.')
    labels = manifest['labels']
    if not labels or len({label['id'] for label in labels}) != len(labels):
        raise ValueError('Labels must have unique IDs.')
    pad = max(4, manifest.get('padding', 12))
    bounds = [font.getbbox(label['text']) for label in labels]
    top = min(b[1] for b in bounds)
    bottom = max(b[3] for b in bounds)
    output = args.manifest.parent
    for label, (left, _, right, _) in zip(labels, bounds):
        if not re.fullmatch(r'[a-z0-9]+(?:-[a-z0-9]+)*', label['id']):
            raise ValueError('Label IDs must be lowercase filename-safe names.')
        image = Image.new('RGBA', (right-left+2*pad, bottom-top+2*pad), (0, 0, 0, 0))
        ImageDraw.Draw(image).text((pad-left, pad-top), label['text'], font=font, fill=label['color'])
        box = image.getbbox()
        if not box or not (box[0] > 0 and box[1] > 0 and box[2] < image.width and box[3] < image.height):
            raise ValueError(f'Clipped or empty text: {label["id"]}')
        image.save(output / f'{label["id"]}.png', optimize=True)
        print(f'{label["id"]}.png: {image.width} x {image.height}')


if __name__ == '__main__':
    main()
