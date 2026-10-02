"""Scene composition, reduced motion, navigation and viewport geometry checks."""
import json
from pathlib import Path
from playwright.sync_api import sync_playwright
from story_test_support import serve, remember_family_entry

OUT=Path(__file__).resolve().parents[2]/'hub-review/story05/visual'
OUT.mkdir(parents=True,exist_ok=True)
server,base=serve();errors=[];bad=[]
try:
 with sync_playwright() as p:
  browser=p.chromium.launch();context=browser.new_context(viewport={'width':820,'height':1180},has_touch=True,reduced_motion='reduce')
  remember_family_entry(context)
  page=context.new_page();page.on('pageerror',lambda e:errors.append(str(e)));page.on('response',lambda r:bad.append(r.url) if r.status>=400 else None)
  page.goto(base+'stories/story-05/');page.wait_for_selector('[data-action="start"]');page.locator('[data-action="start"]').click()
  assert page.evaluate('JSON.parse(localStorage.getItem("adventure.story-05.state")).motion')=='static'
  for scene,stage,gem in [('S01',0,False),('S02',0,False),('S03',0,False),('S04',0,False),('S05',1,False),('S06',1,False),('S07',1,False),('H01',1,True),('S08',2,True),('S09',2,True),('R01',2,True),('S10',2,True),('H02',2,True),('H03',2,True),('E01',2,True),('E02',2,True)]:
   page.evaluate('''async ([scene,stage,gem])=>{
     const {freshState}=await import('./state.js');const s=freshState();s.scene=scene;s.stage=stage;s.gem=gem;
     s.learned=['ABCDEFGHI','JKLMNOPQR','STUVWXYZ'].map(x=>x.split(''));s.timer=false;
     for(let i=0;i<stage;i++)s.completed[i]=s.learned[i].slice();
     if(['S10','H02','H03','E01','E02'].includes(scene))s.completed=s.learned.map(x=>x.slice());
     if(scene==='R01')s.hearts=0;if(['H03','E02'].includes(scene))s.round=5;
     localStorage.setItem('adventure.story-05.state',JSON.stringify(s));localStorage.setItem('adventure.settings.sound','false');
   }''',[scene,stage,gem]);page.reload();page.locator('[data-action="resume"]').click()
   page.wait_for_function('Array.from(document.images).every(i=>i.complete&&i.naturalWidth>0)')
   page.wait_for_timeout(80)
   assert page.locator('.scene').get_attribute('data-scene')==scene
   assert page.evaluate('document.documentElement.scrollWidth<=innerWidth')
   bg=page.locator('.scene-background');assert bg.evaluate('i=>getComputedStyle(i).objectFit')=='contain'
   if scene=='S06':assert page.locator('.door-cover').count()==1 and page.locator('.door-eye').count()==1
   if scene=='H03':assert page.locator('.angel-story').evaluate('n=>getComputedStyle(n).opacity')=='1'
   if scene=='S07':assert page.locator('.inventory, [data-action="gem"]').count()==0
   page.screenshot(path=str(OUT/(scene+'.png')),full_page=True)
  # Browser fullscreen API works when offered; leave fullscreen explicitly.
  page.locator('[data-action="fullscreen"]').click();page.wait_for_timeout(100)
  assert page.evaluate('document.fullscreenElement!==null');page.locator('[data-action="fullscreen"]').click();page.wait_for_function('document.fullscreenElement===null')
  page.locator('[data-action="home"]').click();page.wait_for_url(base+'#english');page.wait_for_function('Array.from(document.images).every(i=>i.complete&&i.naturalWidth>0)')
  assert page.locator('#english [data-story="story-05"]').count()==1
  page.screenshot(path=str(OUT/'hub-english.png'),full_page=False)
  assert not errors and not bad,(errors,bad)
  (OUT/'results.json').write_text(json.dumps({'passed':True,'scenes':16,'reducedMotion':True,'fullscreen':True,'errors':errors,'badResponses':bad}),encoding='utf-8')
  browser.close()
 print('PASS 16 scene compositions, reduced motion, uncropped backgrounds, fullscreen enter/exit and English hub')
finally:server.shutdown()
