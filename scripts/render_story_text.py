"""Render Story 02 labels in short wrapping chunks. Never copies or publishes the font.

python scripts/render_story_text.py --font /private/BpmfGenRyuMin-H.ttf
Requires Pillow; all Chinese visible labels originate in story.json.
"""
import argparse
import json
from pathlib import Path
from PIL import Image, ImageDraw, ImageFont

def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--font', required=True, type=Path)
    parser.add_argument('--story', type=Path, default=Path(__file__).resolve().parents[1]/'stories/story-02')
    args = parser.parse_args()
    config = json.loads((args.story/'story.json').read_text(encoding='utf-8'))
    font = ImageFont.truetype(str(args.font), 192)
    if font.getname() != ('Bpmf GenRyu Min', 'H'):
        raise ValueError('Use the project-standard BpmfGenRyuMin-H.ttf.')
    out = args.story/'assets/text'; out.mkdir(parents=True, exist_ok=True)
    groups = {}
    for key, value in config['labels'].items():
        chunks, chunk = [], ''
        for char in value:
            if len(chunk) >= 6 and char not in '，。！？：」…':
                chunks.append(chunk); chunk = ''
            chunk += char
            if char in '，。！？：' and len(chunk) >= 3:
                chunks.append(chunk); chunk = ''
        if chunk: chunks.append(chunk)
        groups[key] = chunks
    top = min(font.getbbox(chunk)[1] for chunks in groups.values() for chunk in chunks)
    bottom = max(font.getbbox(chunk)[3] for chunks in groups.values() for chunk in chunks)
    manifest = {'font':'Bpmf GenRyu Min H (local render only)', 'fontSize':192, 'labels':{}}
    for key, chunks in groups.items():
        rendered = []
        for index, chunk in enumerate(chunks):
            left, _, right, _ = font.getbbox(chunk); pad = 12
            image = Image.new('RGBA',(right-left+pad*2,bottom-top+pad*2),(0,0,0,0))
            ImageDraw.Draw(image).text((pad-left,pad-top),chunk,font=font,fill='#30283e')
            bounds = image.getbbox()
            assert bounds and bounds[0]>0 and bounds[1]>0 and bounds[2]<image.width and bounds[3]<image.height
            filename=f'{key}-{index}.png'; image.save(out/filename,optimize=True)
            rendered.append(dict(src=filename,text=chunk,width=image.width,height=image.height))
        manifest['labels'][key]=dict(text=config['labels'][key],parts=rendered)
    (out/'text.json').write_text(json.dumps(manifest,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
    print(f'Rendered {len(groups)} labels; font was not copied.')

if __name__ == '__main__': main()
