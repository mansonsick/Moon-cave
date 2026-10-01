"""Render local Story 04 zhuyin, including contextual glyph variants. Never publish fonts."""
import argparse,json,tempfile,math
from pathlib import Path
from fontTools.ttLib import TTFont
from PIL import Image,ImageDraw,ImageFont

def main():
    ap=argparse.ArgumentParser();ap.add_argument('--font',required=True,type=Path);ap.add_argument('--story',type=Path,default=Path(__file__).resolve().parents[1]/'stories/story-04');args=ap.parse_args()
    config=json.loads((args.story/'story.json').read_text(encoding='utf-8'))
    font=ImageFont.truetype(str(args.font),192)
    if font.getname()!=('Bpmf GenRyu Min','H'):raise ValueError('Use the supplied BpmfGenRyuMin-H.ttf')
    out=args.story/'assets/text';out.mkdir(parents=True,exist_ok=True)
    # The local H font has alternate readings in ss01. Pillow here has no RAQM,
    # so use private temporary cmap variants, never a public modified font.
    with tempfile.TemporaryDirectory(prefix='story04-private-font-') as temp:
        variants={}
        for char in '背還差種':
            f=TTFont(args.font);glyph=f.getBestCmap()[ord(char)]+'.ss01'
            if glyph not in f.getGlyphOrder():raise ValueError('Missing alternate reading '+char)
            for table in f['cmap'].tables:
                if table.format in (4,12):table.cmap[ord(char)]=glyph
            path=Path(temp)/(str(ord(char))+'.ttf');f.save(path);f.close()
            variants[char]=ImageFont.truetype(str(path),192)
        def selected(text,index):
            c=text[index]
            return variants[c] if c in '背還差' or (c=='種' and text[index:index+2]=='種子') else font
        all_bounds=[selected(text,i).getbbox(c) for text in config['labels'].values() for i,c in enumerate(text)]
        top=min(b[1] for b in all_bounds);bottom=max(b[3] for b in all_bounds);pad=12
        manifest={'font':'Bpmf GenRyu Min H (local rendered images only)','fontSize':192,'contextReadings':{'背':'ㄅㄟ','還':'ㄏㄞˊ','郵差':'ㄧㄡˊ ㄔㄞ','種子':'ㄓㄨㄥˇ ㄗˇ','種花':'ㄓㄨㄥˋ ㄏㄨㄚ'},'labels':{}}
        for key,text in config['labels'].items():
            chunks=[];start=0
            for i,c in enumerate(text):
                if i-start>=5 and c not in '，。！？：』」':chunks.append((start,text[start:i]));start=i
            if start<len(text):chunks.append((start,text[start:]))
            parts=[]
            for n,(start,chunk) in enumerate(chunks):
                items=[(selected(text,start+i),c) for i,c in enumerate(chunk)]
                widths=[f.getlength(c) for f,c in items];width=math.ceil(sum(widths))+pad*2
                image=Image.new('RGBA',(width,bottom-top+pad*2),(0,0,0,0));draw=ImageDraw.Draw(image);x=pad
                for (chosen,c),advance in zip(items,widths):draw.text((x,pad-top),c,font=chosen,fill='#30283e');x+=advance
                bounds=image.getbbox()
                if not bounds or not(bounds[0]>0 and bounds[1]>0 and bounds[2]<image.width and bounds[3]<image.height):raise ValueError('Empty or cropped label '+key)
                name=f'{key}-{n}.png';image.save(out/name,optimize=True)
                parts.append({'src':name,'text':chunk,'width':image.width,'height':image.height})
            manifest['labels'][key]={'text':text,'parts':parts}
        (out/'text.json').write_text(json.dumps(manifest,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
    print('Rendered',len(manifest['labels']),'labels with contextual zhuyin; private fonts removed.')

if __name__=='__main__':main()
