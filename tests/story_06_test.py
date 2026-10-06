"""Story 06 browser acceptance: actual UI routes, pointer input and saved-state isolation."""
import json,sys,time
from pathlib import Path
from playwright.sync_api import sync_playwright
from story_test_support import serve,remember_family_entry,REPO
KEY='adventure.story-06.state'
OUT=REPO.parent/'hub-review/story06/runtime-qa';OUT.mkdir(parents=True,exist_ok=True)
def state(page):return page.evaluate('(key)=>JSON.parse(localStorage.getItem(key))',KEY)
def action(page,id):return page.locator(f'[data-action="{id}"]').first
def click(page,id):action(page,id).click(timeout=15000)
def scene(page,id):page.wait_for_selector(f'.book[data-scene="{id}"]',timeout=15000)
def tap(page,selector):
 node=page.locator(selector).first;node.evaluate("n=>n.scrollIntoView({block:'center',behavior:'instant'})");r=node.bounding_box();page.mouse.click(r['x']+r['width']/2,r['y']+r['height']/2)
def images(page):
 page.locator('img[loading="lazy"]').evaluate_all('ns=>ns.forEach(n=>n.loading="eager")')
 page.wait_for_function('Array.from(document.images).every(i=>i.complete&&i.naturalWidth>0)',timeout=20000)
def learn(page):
 for _ in range(5):click(page,'next-card')
 assert not action(page,'enter-quiz').is_disabled();click(page,'enter-quiz')
def solve(page,g,wrong=False):
 for i in range(6):
  assert state(page)['progress'][g]==i
  click(page,'assist');s=state(page);target=s['roundSymbols'][g][i]
  choices=page.locator('.answer-card').evaluate_all('(nodes)=>nodes.map(n=>n.dataset.symbol)')
  assert len(choices)==g+3 and len(set(choices))==len(choices)
  assert set(choices)<=set(s['roundSymbols'][g]) and target in choices
  if wrong and i==0:
   bad=next(c for c in choices if c!=target);tap(page,f'.answer-card[data-symbol="{bad}"]');assert state(page)['progress'][g]==i
  tap(page,f'.answer-card[data-symbol="{target}"]')
  assert state(page)['progress'][g]==i+1
  if i<5:click(page,'next-question')
 assert page.locator('[role="dialog"]').is_visible()
 page.wait_for_timeout(1100);assert page.locator('[role="dialog"]').is_visible()
 click(page,'continue')
def initial(page,url):
 page.goto(url);click(page,'start');scene(page,'S01');click(page,'next');scene(page,'S02');click(page,'next');scene(page,'S03')
def main():
 server,base=serve();errors=[];bad=[];summary=[]
 try:
  with sync_playwright() as p:
   browser=p.chromium.launch();ctx=browser.new_context(viewport={'width':768,'height':1024},has_touch=True);remember_family_entry(ctx)
   ctx.add_init_script("if(!localStorage.getItem('acceptance-set')){localStorage.setItem('adventure.settings.sound','false');localStorage.setItem('moonCaveSave','legacy-sentinel');localStorage.setItem('adventure.story-02.state','story02-sentinel');localStorage.setItem('adventure.story-05.state','story05-sentinel');localStorage.setItem('acceptance-set','yes');}")
   page=ctx.new_page();page.on('pageerror',lambda e:errors.append(str(e)));page.on('response',lambda r:bad.append(r.url) if r.status>=400 else None)
   initial(page,base+'stories/story-06/');draw=state(page)['roundSymbols'];assert len(set(sum(draw,[])))==18
   assert page.locator('[data-action="bell-item"]').count()==0
   assert action(page,'enter-quiz').is_disabled();learn(page);scene(page,'S04')
   assert not page.locator('.answer-field').is_visible();click(page,'begin-question');page.wait_for_timeout(200);assert not page.locator('.answer-field').is_visible()
   click(page,'assist');target=state(page)['roundSymbols'][0][0]
   page.reload();click(page,'resume');assert state(page)['roundSymbols']==draw and state(page)['assistedPending'][0]
   solve(page,0,wrong=True);scene(page,'S05');learn(page);scene(page,'S06');solve(page,1);scene(page,'S07')
   hidden=page.locator('[data-action="explore"]');assert hidden.evaluate("n=>getComputedStyle(n).boxShadow")=='none'
   click(page,'next');scene(page,'S08');learn(page);scene(page,'S09');solve(page,2);scene(page,'S10');click(page,'next');scene(page,'E01');assert state(page)['endings']==['ordinary']
   images(page);page.screenshot(path=str(OUT/'ordinary-tablet.png'),full_page=True);summary.append('18 questions, wrong retry, muted fallback, ordinary route and persistent rewards')
   # Backtracking to root fork permits optional exploration without undoing work.
   for _ in range(6):
    if state(page)['scene']=='S07':break
    click(page,'previous')
   scene(page,'S07');assert state(page)['progress']==[6,6,6]
   click(page,'explore');scene(page,'H01');click(page,'pickup');assert state(page)['bell'];assert page.locator('[role="dialog"]').is_visible();click(page,'continue');scene(page,'S07')
   click(page,'next');scene(page,'S08');click(page,'enter-quiz');scene(page,'S09');click(page,'continue');scene(page,'S10')
   # Bell owned and unused still gives full ordinary success.
   click(page,'next');scene(page,'E01');click(page,'previous');scene(page,'S10')
   source=action(page,'bell-item');target=page.locator('[data-role="bell-hollow"]');source.scroll_into_view_if_needed();a=source.bounding_box();b=target.bounding_box()
   # The original hollow is well above the bag; drag while the document scrolls.
   source.focus();a=source.bounding_box();page.mouse.move(a['x']+a['width']/2,a['y']+a['height']/2);page.mouse.down()
   target.scroll_into_view_if_needed();b=target.bounding_box();page.mouse.move(b['x']+b['width']/2,b['y']+b['height']/2,steps=18);page.mouse.up()
   scene(page,'H02');assert state(page)['bellPlaced'];assert page.locator('[data-role="mounted-bell"].glow').count()==1
   page.wait_for_timeout(1000);scene(page,'H02');click(page,'next');scene(page,'E02');assert state(page)['endings']==['ordinary','secret']
   images(page);page.screenshot(path=str(OUT/'secret-tablet.png'),full_page=True);summary.append('Hidden pickup, unused bell ordinary ending, actual drag into original hollow and secret ending')
   # Replay cancellation / acceptance isolates the Story 06 key.
   click(page,'replay');click(page,'cancel');assert state(page)['roundSymbols']==draw
   click(page,'menu');click(page,'resume');scene(page,'E02');assert state(page)['progress']==[6,6,6]
   click(page,'replay');click(page,'new-adventure');scene(page,'S01');assert state(page)['roundSymbols']!=draw and state(page)['progress']==[0,0,0]
   for key,val in [('moonCaveSave','legacy-sentinel'),('adventure.story-02.state','story02-sentinel'),('adventure.story-05.state','story05-sentinel')]:assert page.evaluate('(k)=>localStorage.getItem(k)',key)==val
   click(page,'larger');assert state(page)['size']>1;click(page,'smaller');click(page,'next');click(page,'next');scene(page,'S03');images(page)
   assert page.evaluate('document.documentElement.scrollWidth<=innerWidth')
   page.screenshot(path=str(OUT/'learning-tablet.png'),full_page=True)
   # Phone sizing / key target sizes, no horizontal overflow.
   page.set_viewport_size({'width':390,'height':844});images(page);assert page.evaluate('document.documentElement.scrollWidth<=innerWidth');page.screenshot(path=str(OUT/'learning-phone.png'),full_page=True)
   assert page.locator('.learn-card').evaluate_all('ns=>ns.every(n=>n.getBoundingClientRect().width>=48&&n.getBoundingClientRect().height>=48)')
   summary.append('Replay isolation, same draw after refresh/back/menu, A−/A+, tablet/phone layout')
   page.goto(base);page.wait_for_selector('[data-story="story-06"]');images(page);assert page.locator('[data-story="story-06"] .start').get_attribute('href')=='./stories/story-06/'
   assert page.locator('[data-story="story-06"]').evaluate("n=>n.closest('.subject-section').id")=='chinese'
   assert not errors,errors;assert not bad,bad
   (OUT/'browser-results.json').write_text(json.dumps({'passed':summary,'pageErrors':errors,'httpErrors':bad},ensure_ascii=False,indent=2),encoding='utf-8')
   browser.close();print('PASS:', '; '.join(summary))
 finally:server.shutdown()
if __name__=='__main__':main()
