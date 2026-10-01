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
        # Scene notices are complete, fixed-line images, not flow-layout chunks.
        # A shared canvas and font size keep ink consistent across all notices.
        notes=config.get('sceneText',{})
        note_width=math.ceil(max(sum(selected(config['labels'][key],sum(map(len,lines[:n]))+i).getlength(c)
          for i,c in enumerate(line)) for key,lines in notes.items() for n,line in enumerate(lines)))+pad*4
        line_height=bottom-top+pad*2;gap=36;note_height=line_height*3+gap*2+pad*2
        for key,lines in notes.items():
            original=config['labels'][key]
            if ''.join(lines)!=original:raise ValueError('Scene note changed approved text: '+key)
            image=Image.new('RGBA',(note_width,note_height),(0,0,0,0));draw=ImageDraw.Draw(image)
            y=(note_height-len(lines)*line_height-(len(lines)-1)*gap)/2;offset=0
            for line in lines:
                items=[(selected(original,offset+i),c) for i,c in enumerate(line)]
                advances=[f.getlength(c) for f,c in items];x=(note_width-sum(advances))/2
                for (chosen,c),advance in zip(items,advances):
                    draw.text((x,y+pad-top),c,font=chosen,fill='#211b12');x+=advance
                y+=line_height+gap;offset+=len(line)
            bounds=image.getbbox()
            if not bounds or not(0<bounds[0]<bounds[2]<image.width and 0<bounds[1]<bounds[3]<image.height):raise ValueError('Cropped scene notice '+key)
            name='scene-'+key+'.png';image.save(out/name,optimize=True)
            manifest['labels'][key]['scene']={'src':name,'width':image.width,'height':image.height,'lines':lines}
        (out/'text.json').write_text(json.dumps(manifest,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
    print('Rendered',len(manifest['labels']),'labels with contextual zhuyin; private fonts removed.')

if __name__=='__main__':main()
