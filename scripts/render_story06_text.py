"""Render private project font to PNGs; never publish a font, even a modified one."""
import argparse,json,subprocess,sys,tempfile
from pathlib import Path
from fontTools.ttLib import TTFont
from PIL import Image,ImageDraw,ImageFont
ROOT=Path(__file__).resolve().parents[1];STORY=ROOT/'stories/story-06'
def main():
 p=argparse.ArgumentParser(description=__doc__);p.add_argument('--font',type=Path,required=True);a=p.parse_args()
 with tempfile.TemporaryDirectory(prefix='story06-private-font-') as folder:
  ft=TTFont(a.font);cmap=ft.getBestCmap();sub={}
  for feature in ft['GSUB'].table.FeatureList.FeatureRecord:
   if feature.FeatureTag=='ss01':
    for index in feature.Feature.LookupListIndex:
     for table in ft['GSUB'].table.LookupList.Lookup[index].SubTable:sub.update(getattr(table,'mapping',{}))
  # Here 還=hai2 (still / again), 重=chong2 (restart), 長=zhang3 (parent).
  # 藏 remains the default cang2 (hide), rather than zang4 (treasure).
  for char in '還重長':
   glyph=cmap[ord(char)];alternate=sub.get(glyph,glyph+'.ss01');assert alternate in ft.getGlyphOrder()
   for table in ft['cmap'].tables:
    if table.isUnicode() and ord(char) in table.cmap:table.cmap[ord(char)]=alternate
  private=Path(folder)/'context.ttf';ft.save(private);ft.close()
  subprocess.run([sys.executable,str(ROOT/'scripts/render_story_text.py'),'--font',str(private),'--story',str(STORY)],check=True)
 font=ImageFont.truetype(str(a.font),210);out=STORY/'assets/symbols';out.mkdir(parents=True,exist_ok=True);manifest={}
 for c in map(chr,range(0x3105,0x312a)):
  # The H font reserves annotation advance even for a symbol; center the ink,
  # not that wider advance box, so all 37 cards remain equally legible.
  probe=Image.new('RGBA',(512,512),(0,0,0,0));ImageDraw.Draw(probe).text((0,0),c,font=font,fill='#183b34');box=probe.getbbox()
  assert box and box[2]-box[0]<232 and box[3]-box[1]<232
  img=Image.new('RGBA',(256,256),(0,0,0,0));ImageDraw.Draw(img).text(((256-box[2]-box[0])/2,(256-box[3]-box[1])/2),c,font=font,fill='#183b34')
  bounds=img.getbbox();assert bounds[0]>0 and bounds[1]>0 and bounds[2]<256 and bounds[3]<256
  if c=='ㄧ':assert bounds[2]-bounds[0]>bounds[3]-bounds[1],'Use horizontal ㄧ'
  name=f'{ord(c):04x}.png';img.save(out/name,optimize=True);manifest[c]={'src':name,'width':256,'height':256}
 (out/'manifest.json').write_text(json.dumps({'font':'Bpmf GenRyu Min H (local render only)','symbols':manifest},ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
 print('Rendered 37 symbol PNGs; temporary context font removed.')
if __name__=='__main__':main()
