"""Seeded free-flight bounds/turns and actual foreground/background pointer precedence."""
import json
from pathlib import Path
from playwright.sync_api import sync_playwright
from story_test_support import serve,remember_family_entry

server,base=serve()
try:
 with sync_playwright() as p:
  browser=p.chromium.launch();context=browser.new_context(viewport={'width':820,'height':1180});remember_family_entry(context)
  page=context.new_page();errors=[];page.on('pageerror',lambda e:errors.append(str(e)))
  page.goto(base+'stories/story-05/');page.wait_for_selector('.site-links')
  audit=page.evaluate('''async()=>{
    const {MovingTargets}=await import('../../engine/moving-targets.js');let seed=17993;
    const random=()=>((seed=(seed*1664525+1013904223)>>>0)/4294967296);
    const field=document.createElement('div');Object.assign(field.style,{position:'relative',width:'760px',height:'400px'});document.body.append(field);
    const nodes=Array.from({length:6},()=>{const n=document.createElement('div');Object.assign(n.style,{position:'absolute',width:'68px',height:'68px'});field.append(n);return n;});
    const depths=new Set();let elapsed=0;
    const motion=new MovingTargets(nodes,{random,onTurn:n=>{if(n===nodes[5]){n.style.zIndex=random()<.6?'3':'0';depths.add(n.style.zIndex);}},onTick:dt=>elapsed+=dt});
    motion.dispose();motion.setRunning(true);
    const extents=motion.entries.map(e=>({minX:e.x,maxX:e.x,minY:e.y,maxY:e.y}));let inBounds=true;
    for(let i=1;i<=1001;i++){motion.tick(i*60);cancelAnimationFrame(motion.frame);motion.entries.forEach((e,j)=>{
      const s=extents[j];s.minX=Math.min(s.minX,e.x);s.maxX=Math.max(s.maxX,e.x);s.minY=Math.min(s.minY,e.y);s.maxY=Math.max(s.maxY,e.y);
      inBounds&&=e.x>=7.99&&e.y>=7.99&&e.x+e.w<=motion.width-7.99&&e.y+e.h<=motion.height-7.99;
    });}
    motion.setMode('static');const fixed=nodes.map(n=>n.style.transform),before=elapsed;
    for(let i=1002;i<=1012;i++){motion.tick(i*60);cancelAnimationFrame(motion.frame);}
    const still=nodes.every((n,i)=>n.style.transform===fixed[i])&&elapsed>before;
    motion.setRunning(false);const clock=elapsed;motion.tick(1013*60);cancelAnimationFrame(motion.frame);const paused=elapsed===clock;
    field.style.width='340px';field.style.height='355px';motion.layout();const resized=motion.entries.every(e=>e.x>=8&&e.y>=8&&e.x+e.w<=332&&e.y+e.h<=347);
    // Force a lingering overlap in slow mode: the grace period uses wall time.
    const first=motion.entries[0],second=motion.entries[1];first.x=second.x=100;first.y=second.y=100;first.vx=first.vy=first.dx=first.dy=0;first.turn=10;first.overlap=.64;
    motion.move(first,.01,.06);const separates=Math.hypot(first.vx,first.vy)>200;
    motion.dispose();field.remove();return {inBounds,depths:[...depths].sort(),still,paused,resized,separates,extents};
  }''')
  assert all(audit[k] for k in ['inBounds','still','paused','resized','separates']),audit
  assert audit['depths']==['0','3']
  assert all(e['maxX']-e['minX']>150 and e['maxY']-e['minY']>100 for e in audit['extents']),audit
  page.evaluate('localStorage.setItem("adventure.settings.sound","false")')
  def setup(kind):
   page.evaluate('''async()=>{const {freshState}=await import('./state.js');const s=freshState();s.scene='S04';s.timer=false;s.motion='static';s.learned[0]=[...'ABCDEFGHI'];localStorage.setItem('adventure.story-05.state',JSON.stringify(s));}''')
   page.reload();page.locator('[data-action="resume"]').click();page.locator('[data-action="begin-question"]').click();page.locator('[data-action="ready"]').click()
   page.wait_for_function('!document.querySelector(".feedback")&&document.querySelector("canvas").width===300')
   return page.evaluate('''kind=>{
     const s=JSON.parse(localStorage.getItem('adventure.story-05.state')),target=s.orders[0][0];const card=[...document.querySelectorAll('.letter-card')].find(n=>n.dataset.letter.toUpperCase()===target);
     const c=document.querySelector('canvas'),field=c.parentElement,fb=field.getBoundingClientRect();
     const data=c.getContext('2d').getImageData(0,0,c.width,c.height).data;let point;
     for(let y=25;y<c.height-25&&!point;y++)for(let x=25;x<c.width-25;x++){const a=data[(y*c.width+x)*4+3];if(kind==='transparent'?a===0:a>240){point={x,y};break;}}
     c.style.transform='translate(110px,110px)';c.style.zIndex=kind==='behind'?'0':'3';const b=c.getBoundingClientRect();
     const x=b.left+(point.x+.5)/c.width*b.width,y=b.top+(point.y+.5)/c.height*b.height;
     card.style.transform=`translate(${x-fb.left-card.offsetWidth/2}px,${y-fb.top-card.offsetHeight/2}px)`;
     return {x,y,target};
   }''',kind)
  results=[]
  for kind in ['front','behind','transparent']:
   point=setup(kind);page.mouse.click(point['x'],point['y']);page.wait_for_selector('.feedback')
   s=page.evaluate('JSON.parse(localStorage.getItem("adventure.story-05.state"))')
   if kind=='front':assert s['hearts']==2 and not s['completed'][0]
   else:assert s['hearts']==3 and s['completed'][0]==[point['target']]
   results.append(kind)
  assert not errors,errors
  out=Path('../hub-review/story05/flight');out.mkdir(parents=True,exist_ok=True)
  (out/'results.json').write_text(json.dumps({'motion':audit,'overlapClicks':results,'errors':errors},indent=2),encoding='utf-8')
  browser.close();print('PASS seeded random full-field X/Y flight, bounds, depth turns, resize, slow-mode separation, freeze and three overlap click cases')
finally:server.shutdown()
