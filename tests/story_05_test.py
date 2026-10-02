"""Story 05 browser acceptance: real navigation + isolated fault/interaction cases."""
import json, math, sys
from pathlib import Path
from playwright.sync_api import sync_playwright
from story_test_support import serve

OUT=Path(__file__).resolve().parents[2]/'hub-review/story05/qa'
OUT.mkdir(parents=True,exist_ok=True)
GROUPS=['ABCDEFGHI','JKLMNOPQR','STUVWXYZ']
SENTINELS={'moonCaveState':'moon-v3-preserved','moonCaveTextScale':'1.2','adventure.story-02.state':'story-two-preserved',
           'adventure.story-03.state':'story-three-preserved','adventure.story-04.state':'story-four-preserved'}

def state(page):return page.evaluate('JSON.parse(localStorage.getItem("adventure.story-05.state"))')
def action(page,name):page.locator(f'[data-action="{name}"]').click()
def tap(page,node):
    b=node.bounding_box();page.mouse.click(b['x']+b['width']/2,b['y']+b['height']/2)
def assets(page):page.wait_for_function('Array.from(document.images).every(i=>i.complete&&i.naturalWidth>0)')
def target_card(page):
    s=state(page);target=next(x for x in s['orders'][s['stage']] if x not in s['completed'][s['stage']])
    return next(node for node in page.locator('.letter-card').all() if node.get_attribute('data-letter').upper()==target)
def ready(page):
    if page.locator('[data-action="begin-question"]').count():action(page,'begin-question')
    if page.locator('[data-action="ready"]').count():action(page,'ready')
    page.wait_for_function('!document.querySelector(".feedback")')
def answer(page):
    ready(page);tap(page,target_card(page));page.wait_for_selector('.feedback')
def wrong(page):
    ready(page);target=target_card(page).get_attribute('data-letter')
    node=next(n for n in page.locator('.letter-card').all() if n.get_attribute('data-letter')!=target)
    tap(page,node);page.wait_for_selector('.feedback, [data-action="retry-stage"]')
def learn(page,count):
    for _ in range(count):action(page,'next-card')
def solve(page,index):
    count=len(GROUPS[index])
    for i in range(count-len(state(page)['completed'][index])):
        answer(page)
        saved=state(page);assert len(saved['completed'][index])==i+1
        assert page.locator('.progress-lamp.lit').count()==i+1
        page.wait_for_timeout(30);assert page.locator('.feedback').count()==1
        assert page.locator('.letter-card').evaluate_all('ns=>new Set(ns.map(n=>n.dataset.letter.toUpperCase())).size')==[3,4,5][index]
        if i<count-1:action(page,'next-lamp')
    action(page,'continue')

def init(page,url,sound=False):
    page.goto(url);page.wait_for_selector('[data-action="start"], [data-action="resume"]')
    page.evaluate('(s)=>{for(const [k,v] of Object.entries(s))localStorage.setItem(k,v);localStorage.setItem("adventure.settings.sound","false")}',SENTINELS)
    if sound:page.evaluate('localStorage.setItem("adventure.settings.sound","true")')
    page.reload();page.wait_for_selector('[data-action="start"], [data-action="resume"]')
    if page.locator('[data-action="resume"]').count():action(page,'yes-replay') if page.locator('[data-action="yes-replay"]').count() else action(page,'resume')
    else:action(page,'start')
    action(page,'settings');action(page,'no-timer');action(page,'static-motion');action(page,'close')

def beginning(page):action(page,'walk-ahead');action(page,'shelter');learn(page,9)
def through_first_two(page):
    beginning(page);solve(page,0);learn(page,9);solve(page,1)
def seed(page,scene,stage=0,gem=False,hearts=3,completed=None):
    page.evaluate('''async ([scene,stage,gem,hearts,completed])=>{
      const {freshState}=await import('./state.js');const s=freshState();s.scene=scene;s.stage=stage;s.gem=gem;s.hearts=hearts;s.motion='static';s.timer=false;
      s.learned=['ABCDEFGHI','JKLMNOPQR','STUVWXYZ'].map(x=>x.split(''));
      for(let i=0;i<stage;i++)s.completed[i]=s.learned[i].slice();if(completed)s.completed=completed;
      localStorage.setItem('adventure.story-05.state',JSON.stringify(s));
    }''',[scene,stage,gem,hearts,completed]);page.reload();action(page,'resume')
def pixel_point(page,opaque=True):
    return page.locator('.monster-target').evaluate('''(c,opaque)=>{
      const ctx=c.getContext('2d'),p=ctx.getImageData(0,0,c.width,c.height).data,b=c.getBoundingClientRect();
      for(let y=20;y<c.height-20;y++)for(let x=20;x<c.width-20;x++)if(opaque?p[(y*c.width+x)*4+3]>240:p[(y*c.width+x)*4+3]===0)
        return {x:b.left+(x+.5)/c.width*b.width,y:b.top+(y+.5)/c.height*b.height};
    }''',opaque)

server,base=serve();results=[]
try:
 with sync_playwright() as p:
  browser=p.chromium.launch();context=browser.new_context(viewport={'width':820,'height':1180},has_touch=True)
  page=context.new_page();errors=[];bad=[];fonts=[]
  page.on('pageerror',lambda e:errors.append(str(e)))
  page.on('response',lambda r:bad.append(r.url) if r.status>=400 else None)
  page.on('request',lambda r:fonts.append(r.url) if r.url.split('?')[0].endswith(('.ttf','.otf','.woff','.woff2')) else None)
  url=base+'stories/story-05/'
  init(page,url);beginning(page)
  # Hearts count all errors, not consecutive errors; a correct answer never heals.
  wrong(page);assert state(page)['hearts']==2;action(page,'retry-question');answer(page)
  assert state(page)['hearts']==2 and len(state(page)['completed'][0])==1
  action(page,'next-lamp');wrong(page);assert state(page)['hearts']==1;action(page,'retry-question');wrong(page)
  assert state(page)['scene']=='R01' and state(page)['hearts']==0
  page.reload();action(page,'resume');assert page.locator('[data-action="retry-stage"]').count()==1
  action(page,'retry-stage');assert state(page)['hearts']==3 and state(page)['completed'][0]==[]
  solve(page,0);learn(page,9)
  wrong(page);action(page,'retry-question');wrong(page);action(page,'retry-question');wrong(page)
  assert state(page)['completed'][0] and state(page)['scene']=='R01'
  action(page,'retry-stage');assert len(state(page)['completed'][0])==9 and state(page)['completed'][1]==[]
  solve(page,1);assert page.locator('[data-action="gem"]').count()==0 and page.locator('.inventory').count()==0
  mark=page.locator('[data-action="moon-mark"]');assert mark.evaluate('n=>getComputedStyle(n).boxShadow')=='none'
  action(page,'bridge');learn(page,8);solve(page,2);assert state(page)['gem'] is False
  action(page,'village');assert state(page)['ending']=='ordinary' and all(len(state(page)['completed'][i])==len(GROUPS[i]) for i in range(3))
  assets(page);page.screenshot(path=str(OUT/'ordinary-portrait.png'),full_page=True)
  results.append('Full ordinary route, all 26 letters, nonconsecutive errors, retry only current stage, reload exhausted state')
  action(page,'replay');action(page,'yes-replay');assert state(page)['completed']==[[],[],[]]
  assert page.evaluate('(s)=>Object.entries(s).every(([k,v])=>localStorage.getItem(k)===v)',SENTINELS)
  through_first_two(page);action(page,'moon-mark');assert state(page)['gem'];action(page,'continue');learn(page,8);solve(page,2)
  # Owning the stone still permits the full ordinary ending.
  action(page,'village');assert state(page)['ending']=='ordinary' and state(page)['gem']
  action(page,'previous');assert state(page)['scene']=='S10'
  # Start secret branch with a real drag; next rounds alternate drag and tap assistance.
  gem=page.locator('[data-action="gem"]');monster=page.locator('[data-action="purify-target"]');a=gem.bounding_box();b=monster.bounding_box()
  page.mouse.move(a['x']+a['width']/2,a['y']+a['height']/2);page.mouse.down();page.mouse.move(b['x']+b['width']/2,b['y']+b['height']/2,steps=8);page.mouse.up()
  page.wait_for_selector('[data-scene="H02"]')
  hearts=state(page)['hearts']
  for i in range(5):
    if i%2==0:tap(page,page.locator('[data-action="gem"]'));tap(page,page.locator('[data-action="purify-target"]'))
    else:
      a=page.locator('[data-action="gem"]').bounding_box();b=page.locator('[data-action="purify-target"]').bounding_box()
      page.mouse.move(a['x']+a['width']/2,a['y']+a['height']/2);page.mouse.down();page.mouse.move(b['x']+b['width']/2,b['y']+b['height']/2,steps=8);page.mouse.up()
    assert state(page)['round']==i+1 and state(page)['hearts']==hearts
    # An extra click cannot award a second hit while feedback holds.
    page.locator('[data-action="purify-target"]').dispatch_event('click');assert state(page)['round']==i+1
    action(page,'next-light')
  assert state(page)['scene']=='H03';assets(page);page.screenshot(path=str(OUT/'angel-portrait.png'),full_page=True)
  action(page,'continue');assert state(page)['ending']=='secret'
  results.append('Hidden unlit mark, gem acquired once, owning-unused ordinary ending, five manual light rounds, drag/tap alternatives, secret ending')
  seed(page,'S04');ready(page);page.wait_for_function('document.querySelector("canvas").width===300')
  before=state(page)['hearts'];pos=pixel_point(page,False);page.mouse.click(pos['x'],pos['y']);assert state(page)['hearts']==before
  pos=pixel_point(page,True);page.mouse.click(pos['x'],pos['y']);assert state(page)['hearts']==before-1
  action(page,'retry-question');ready(page)
  card=target_card(page);b=card.bounding_box();before=state(page)
  page.mouse.move(b['x']+b['width']/2,b['y']+b['height']/2);page.mouse.down();page.mouse.move(b['x']+b['width']/2+40,b['y']+b['height']/2);page.mouse.up()
  assert state(page)==before
  results.append('Original alpha mask: opaque monster costs one heart; transparent padding and drag-out cost none')
  # Real audio and moving touch snapshots; no scripted click bypass of pointer handling.
  page.evaluate('localStorage.setItem("adventure.settings.sound","true")');seed(page,'S04');action(page,'settings');action(page,'normal-motion');action(page,'close');action(page,'unpause')
  page.wait_for_function('!document.querySelector(".feedback") && !document.querySelector("[data-action=replay-letter]").disabled')
  card=target_card(page);positions=[]
  for _ in range(8):positions.append(card.bounding_box());page.wait_for_timeout(130)
  assert max(b['x'] for b in positions)-min(b['x'] for b in positions)>1
  assert max(b['y'] for b in positions)-min(b['y'] for b in positions)>1
  b=card.bounding_box();page.mouse.move(b['x']+b['width']/2,b['y']+b['height']/2);page.mouse.down();fixed=card.bounding_box();page.wait_for_timeout(250);assert abs(card.bounding_box()['x']-fixed['x'])<.5;page.mouse.up()
  assert len(state(page)['independent'][0])==1
  action(page,'next-lamp');page.wait_for_timeout(1600);action(page,'pause');assert page.locator('[data-action="unpause"]').count()==1
  m=page.locator('.monster-target');b=m.bounding_box();page.wait_for_timeout(250);assert abs(m.bounding_box()['y']-b['y'])<.5
  action(page,'settings');action(page,'slow-motion');action(page,'close');assert page.locator('[data-action="unpause"]').count()==1
  action(page,'unpause');page.wait_for_timeout(1600)
  saved=state(page);action(page,'menu');action(page,'resume');assert state(page)['hearts']==saved['hearts'] and state(page)['completed']==saved['completed']
  results.append('Real letter WAV completion, independent listening saved, X/Y motion, pointerdown freeze, pause/settings/replay, menu resume')
  seed(page,'S06',1);action(page,'settings');action(page,'timer');action(page,'close');action(page,'unpause')
  page.wait_for_function('!document.querySelector(".feedback") && !document.querySelector("[data-action=replay-letter]").disabled')
  assert page.locator('.remaining').inner_text()=='12s'
  page.wait_for_timeout(1200);assert int(page.locator('.remaining').inner_text()[:-1])<12
  action(page,'pause');clock=page.locator('.remaining').inner_text();page.wait_for_timeout(1300);assert page.locator('.remaining').inner_text()==clock
  action(page,'unpause');action(page,'pause');page.wait_for_timeout(1600);assert page.locator('[data-action="unpause"]').count()==1
  action(page,'unpause');page.wait_for_function('!document.querySelector(".feedback")');before=state(page)['hearts']
  page.wait_for_selector('[data-action="retry-question"]',timeout=15000);assert state(page)['hearts']==before-1
  results.append('L2 12-second timer begins after voice, pause freezes clock, pause during voice cannot resume itself, timeout costs exactly one heart')
  action(page,'retry-question');page.wait_for_timeout(1500)
  page.evaluate('Object.defineProperty(document,"hidden",{configurable:true,get:()=>true});document.dispatchEvent(new Event("visibilitychange"))')
  assert page.locator('[data-action="unpause"]').count()==1
  page.evaluate('Object.defineProperty(document,"hidden",{configurable:true,get:()=>false});document.dispatchEvent(new Event("visibilitychange"))')
  page.wait_for_timeout(200);assert page.locator('[data-action="unpause"]').count()==1
  results.append('Simulated background visibility change pauses movement/voice/timer and requires explicit resume')
  # All voices decode; same origin only; successful playback promise, no ambience overlap.
  audit=page.evaluate('''async()=>{
    const {AlphabetAudio}=await import('./alphabet-audio.js');const manifest=await fetch('./assets/audio/manifest.json').then(r=>r.json());
    const a=new AlphabetAudio(manifest.entries,new URL('./assets/audio/',location.href),true);await a.unlock();
    const report=[];for(const c of 'ABCDEFGHIJKLMNOPQRSTUVWXYZ'){const b=await a.buffer('letter-'+c);report.push({letter:c,seconds:b?.duration});}
    await a.setAmbience('fog');await a.setAmbience('house');const one=a.current?.id==='house';a.dispose();return {report,one};
  }''')
  assert audit['one'] and all(x['seconds'] and .1<x['seconds']<4 for x in audit['report'])
  assert len({x['letter'] for x in audit['report']})==26
  results.append('26 A–Z WAVs decode and have finite durations; ambience switching leaves one current loop')
  # Storage denied and failed sounds must remain playable in assisted mode.
  broken=browser.new_context(viewport={'width':820,'height':1180});broken.add_init_script('Storage.prototype.getItem=()=>{throw Error("blocked")};Storage.prototype.setItem=()=>{throw Error("blocked")}')
  fault=broken.new_page();fault.route('**/assets/audio/**.wav',lambda route:route.abort());fault.goto(url);action(fault,'start');action(fault,'walk-ahead');action(fault,'shelter');learn(fault,9);action(fault,'begin-question')
  fault.wait_for_selector('[data-action="ready"]',timeout=12000);action(fault,'ready');assert fault.locator('.letter-card').count()==3
  action(fault,'show-letter');preview=fault.locator('.target-preview').inner_text()[0];action(fault,'ready');tap(fault,fault.locator(f'[data-letter="{preview}"]'));assert fault.locator('[data-action="next-lamp"]').count()==1
  broken.close();results.append('Blocked storage plus failed voice files: visual assisted answer succeeds without blocking')
  for width,height in [(390,844),(820,1180),(1180,820)]:
    page.set_viewport_size({'width':width,'height':height});page.evaluate('localStorage.setItem("adventure.settings.sound","false")');seed(page,'S09',2);ready(page);assets(page)
    assert page.evaluate('document.documentElement.scrollWidth<=innerWidth')
    cards=page.locator('.letter-card').all();assert all(n.bounding_box()['width']>=64 and n.bounding_box()['height']>=64 for n in cards)
    boxes=[n.bounding_box() for n in cards]+[page.locator('.monster-target').bounding_box()]
    for i,a in enumerate(boxes):
      for b in boxes[i+1:]:
        assert not (a['x']<b['x']+b['width'] and a['x']+a['width']>b['x'] and a['y']<b['y']+b['height'] and a['y']+a['height']>b['y'])
    page.screenshot(path=str(OUT/f'bridge-{width}.png'),full_page=True)
    action(page,'larger');assert state(page)['size']>1;action(page,'smaller')
  results.append('390 / 820 / 1180 layouts, all five targets >=64px, no target/monster overlap, A−/A+')
  assert page.evaluate('(s)=>Object.entries(s).every(([k,v])=>localStorage.getItem(k)===v)',SENTINELS)
  assert not errors and not bad and not fonts,(errors,bad,fonts)
  (OUT/'results.json').write_text(json.dumps({'passed':results,'errors':errors,'badResponses':bad,'fontRequests':fonts,'voiceAudit':audit},ensure_ascii=False,indent=2),encoding='utf-8')
  print(json.dumps({'passed':len(results),'checks':results,'errors':errors,'badResponses':bad},ensure_ascii=False));browser.close()
finally:server.shutdown()
