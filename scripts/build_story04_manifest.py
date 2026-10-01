"""Inventory Story 04 assets without modifying the generated images or local font."""
import json
from pathlib import Path
from PIL import Image

STORY=Path(__file__).resolve().parents[1]/'stories/story-04'
assets=[]
for path in sorted((STORY/'assets').rglob('*')):
    if path.suffix not in ('.png','.svg'):continue
    relative=path.relative_to(STORY).as_posix()
    entry={'path':relative}
    if path.suffix=='.png':
        with Image.open(path) as image:
            entry.update(width=image.width,height=image.height,transparent='A' in image.getbands() and image.getchannel('A').getextrema()[0]<255)
        entry['kind']='local rendered zhuyin text' if '/text/' in relative else 'generated illustration'
    else:entry['kind']='original code-native teaching picture or prop'
    assets.append(entry)
text=json.loads((STORY/'assets/text/text.json').read_text(encoding='utf-8'))
config=json.loads((STORY/'story.json').read_text(encoding='utf-8'))
for card in [c for group in config['learning'] for c in group]+config['questions']:
    if card.get('illustration'):
        assert (STORY/'assets/images/cards'/card['illustration']).is_file(),card['illustration']
for prop in config['props'].values():assert (STORY/'assets/images/props'/prop['src']).is_file(),prop['src']
assert all((STORY/'assets/text'/part['src']).is_file() for entry in text['labels'].values() for part in entry['parts'])
data={'created':'2026-10-01','generatedImages':sum('/images/' in a['path'] for a in assets),
 'practiceSVGs':sum(a['path'].endswith('.svg') for a in assets),'textLabels':len(text['labels']),
 'fixedSceneNotices':len(config['sceneText']),'fontFilesPublished':False,'generatedOriginalsPreserved':True,
 'promptSets':['assets/images/PROMPTS.json','assets/images/VISUAL_FIX_PROMPTS.json'],'assets':assets}
(STORY/'assets/ASSET_MANIFEST.json').write_text(json.dumps(data,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
print(f"Inventoried {len(assets)} assets: {data['generatedImages']} painted images, {data['textLabels']} labels and {data['fixedSceneNotices']} fixed notices.")
