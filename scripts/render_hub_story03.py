"""Render full-line Story 03 hub labels with the private font; never copy it."""
import argparse
import json
from pathlib import Path
from PIL import Image,ImageDraw,ImageFont

parser=argparse.ArgumentParser();parser.add_argument('--font',type=Path,required=True);args=parser.parse_args()
root=Path(__file__).resolve().parents[1]
labels=json.loads((root/'stories/story-03/story.json').read_text(encoding='utf-8'))['labels']
font=ImageFont.truetype(str(args.font),192)
assert font.getname()==('Bpmf GenRyu Min','H')
for key in ['title','hub-chapter','hub-description-first','hub-description-second']:
    value=labels[key];left,top,right,bottom=font.getbbox(value)
    image=Image.new('RGBA',(right-left+24,bottom-top+24),(0,0,0,0))
    ImageDraw.Draw(image).text((12-left,12-top),value,font=font,fill='#30283e')
    image.save(root/f'assets/hub-text/story-03-{key}.png',optimize=True)
    print(key,image.size)
