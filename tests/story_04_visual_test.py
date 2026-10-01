"""Regression for scene ink containment, seated props and contextual reading cards.

Seeded saves below are layout fixtures, not evidence of successful gameplay.
The separate story_04_test runs actual complete routes.
"""
import json
from pathlib import Path
from PIL import Image
from playwright.sync_api import sync_playwright
from story_test_support import serve,REPO

OUT=REPO.parent/'hub-review/story-04-visual-qa';OUT.mkdir(parents=True,exist_ok=True)
DATA=json.loads((REPO/'stories/story-04/story.json').read_text(encoding='utf-8'))
TEXT=json.loads((REPO/'stories/story-04/assets/text/text.json').read_text(encoding='utf-8'))
assert len({(TEXT['labels'][key]['scene']['width'],TEXT['labels'][key]['scene']['height']) for key in DATA['sceneText']})==1
for key,lines in DATA['sceneText'].items():
    assert ''.join(lines)==DATA['labels'][key]
    with Image.open(REPO/'stories/story-04/assets/text'/TEXT['labels'][key]['scene']['src']) as ink:
        assert (33,27,18) in [pixel[:3] for pixel in ink.getdata() if pixel[3]>240],key

server,base=serve();url=base+'stories/story-04/'
def loaded(page):page.wait_for_selector('#app[data-scene="menu"]')
def images(page):
    try:page.evaluate('async()=>{await Promise.all([...document.images].map(i=>i.decode()));}')
    except Exception:
        print('Image failure:',page.locator('#app').get_attribute('data-scene'),page.locator('img').evaluate_all('items=>items.filter(i=>!i.complete||!i.naturalWidth).map(i=>({src:i.src,complete:i.complete,width:i.naturalWidth}))'))
        raise
def click(page,action):page.locator(f'[data-action="{action}"]').first.click()
def fixture(page,id,delivered=None,learning=None):
    page.evaluate('''async({id,delivered,learning})=>{
      const m=await import('./state.js'),w=await import('../../engine/reading-worksheet.js');
      const s=m.fresh(w.newReadingCode());s.scene=id;s.scale=1.5;s.learned=[true,true,true];s.assisted=[true,true,true];
      s.delivered=delivered||[true,true,true];s.leaf=['E02','E03'].includes(id);s.placed=s.leaf;s.badge=['E01','E03'].includes(id);
      if(learning!==null){s.learned[learning]=false;s.assisted[learning]=false;}
      localStorage.setItem('adventure.story-04.state',JSON.stringify(s));
    }''',{'id':id,'delivered':delivered,'learning':learning})
    # Fixtures replace the entire document. Settle its menu image requests before
    # immediately replacing the DOM again for a screenshot of the seeded scene.
    page.reload();loaded(page);images(page);click(page,'start-adventure');page.wait_for_selector(f'#app[data-scene="{id}"]');images(page)
def contained(inner,outer,margin=0):
    return inner['x']>=outer['x']+margin-.5 and inner['y']>=outer['y']+margin-.5 and inner['x']+inner['width']<=outer['x']+outer['width']-margin+.5 and inner['y']+inner['height']<=outer['y']+outer['height']-margin+.5

try:
 with sync_playwright() as p:
    browser=p.chromium.launch()
    for width,height in [(390,844),(820,1180),(1180,820)]:
        context=browser.new_context(viewport={'width':width,'height':height},has_touch=True);page=context.new_page();errors=[]
        page.on('pageerror',lambda e:errors.append(str(e)));page.goto(url);loaded(page)
        for id in ['S01','S02','S03','S04','S05','S07','S10','E01','E02','E03']:
            fixture(page,id)
            stage=page.locator('.scene-stage').bounding_box()
            assert page.evaluate('document.documentElement.scrollWidth<=innerWidth'),(width,id)
            assert page.locator('.scene-writing img').evaluate_all('items=>items.every(i=>Math.abs((i.getBoundingClientRect().width/i.getBoundingClientRect().height)/(i.naturalWidth/i.naturalHeight)-1)<.02)'),(width,id,'stretched ink')
            for note in page.locator('.scene-note').all():
                paper=page.locator('[data-prop="note-paper"]').bounding_box();rect=note.bounding_box();image=note.locator('img').bounding_box()
                assert contained(rect,paper) and contained(image,rect),(width,id,'ink outside paper')
                assert note.locator('[role="img"]').get_attribute('aria-label')==DATA['labels'][note.get_attribute('data-label')]
            # These independently measured background regions are physical surfaces,
            # not a copy of the prop coordinates in app.js.
            surfaces={'S01':[59,49,20,5],'S02':[55,50.5,36,5],'S05':[72,67,11,5],
              'S07':[57,53,40,6],'S10':[71,68,16,5]}
            if id in surfaces:
                x,y,w,h=surfaces[id];surface={'x':stage['x']+x/100*stage['width'],'y':stage['y']+y/100*stage['height'],'width':w/100*stage['width'],'height':h/100*stage['height']}
                props=page.locator('[data-prop="envelope"]');assert props.count()==(3 if id in ['S01','S02'] else 1)
                for prop in props.all():assert contained(prop.bounding_box(),surface),(width,id,'letter outside surface')
            if id=='S04':
                for index,box in enumerate([[41,26,14,10],[60,26,14,10]]):
                    x,y,w,h=box;board={'x':stage['x']+x/100*stage['width'],'y':stage['y']+y/100*stage['height'],'width':w/100*stage['width'],'height':h/100*stage['height']}
                    assert contained(page.locator('.scene-label').nth(index).bounding_box(),board)
            if id=='S10':
                bird=page.locator('[data-layer="bird"]').bounding_box();letter=page.locator('[data-prop="envelope"]').bounding_box()
                assert bird['y']+bird['height']<=letter['y'], 'Delivered letter covers the bird'
            if width==820:page.locator('.scene-stage').screenshot(path=str(OUT/(id+'.png')))
        for station,id in [(1,'S06'),(2,'S09')]:
            fixture(page,id,learning=station)
            for index,card in enumerate(DATA['learning'][station]):
                frame=page.locator('.learning-card');assert frame.locator('img.picture').count()==1
                assert frame.get_by_role('img',name='記住形狀',exact=True).count()==0
                if card['illustration']:
                    picture=frame.locator('img.illustration');assert picture.get_attribute('src').endswith(card['illustration'])
                    assert picture.bounding_box()['width']>frame.bounding_box()['width']*.85
                for _ in range(5):page.get_by_role('button',name='放大文字',exact=True).click()
                images(page);assert page.evaluate('document.documentElement.scrollWidth<=innerWidth'),(width,station,index)
                if width==820:frame.screenshot(path=str(OUT/f'learning-{station}-{index}.png'))
                if index<len(DATA['learning'][station])-1:click(page,'next-card');images(page)
            if station==2:
                click(page,'learn-done');click(page,'all-mode');images(page)
                for q in DATA['questions'][13:]:
                    field=page.locator(f'[data-question="{q["id"]}"]');picture=field.locator('img.illustration')
                    assert picture.count()==1 and picture.get_attribute('src').endswith(q['illustration'])
                    if width==820 and q['id'] in ['Q16','Q17']:field.screenshot(path=str(OUT/(q['id']+'.png')))
        assert not errors,errors;context.close()
    browser.close()
 print('PASS contained fixed ink; three seated letters; delivered surface positions; route signs; single contextual cards; Q14-Q20 illustrated; 390/820/1180 and A+')
 (OUT/'results.json').write_text(json.dumps({'passed':True,'viewports':[390,820,1180],'physicalTablet':False,'manualIllustrationReviewRequired':True}),encoding='utf-8')
finally:server.shutdown()
