"""Subject anchors work with touch and without JavaScript; story saves stay intact."""
import json
from pathlib import Path
from playwright.sync_api import sync_playwright
from story_test_support import serve, remember_family_entry

out=Path('../hub-review/subject-hub');out.mkdir(parents=True,exist_ok=True)
server,base=serve()
try:
 with sync_playwright() as p:
  browser=p.chromium.launch()
  for width,height in [(390,844),(820,1180),(1180,820)]:
   context=browser.new_context(viewport={'width':width,'height':height},has_touch=True)
   remember_family_entry(context)
   page=context.new_page();errors=[];bad=[];fonts=[]
   page.on('pageerror',lambda e:errors.append(str(e)))
   page.on('response',lambda r:bad.append(r.url) if r.status>=400 else None)
   page.on('request',lambda r:fonts.append(r.url) if r.url.split('?')[0].endswith(('.ttf','.otf','.woff','.woff2')) else None)
   page.goto(base)
   saved={'moonCaveState':'legacy-save','moonCaveTextScale':'1.3','adventure.story-02.state':'story-two-save','adventure.story-03.state':'story-three-save','adventure.settings.sound':'off'}
   page.evaluate('(values)=>Object.entries(values).forEach(([k,v])=>localStorage.setItem(k,v))',saved);page.reload()
   assert page.locator('.subject-entry').count()==3
   assert page.locator('#chinese .story-card').evaluate_all('cards=>cards.map(c=>c.dataset.story)')==['moon-cave','story-02','story-04']
   assert page.locator('#math .story-card').evaluate_all('cards=>cards.map(c=>c.dataset.story)')==['story-03']
   assert page.locator('#english .story-card').evaluate_all('cards=>cards.map(c=>c.dataset.story)')==['story-05']
   assert page.locator('#english .start').count()==1
   assert '虎姑婆' not in page.content()
   for subject in ['chinese','math','english']:
    entry=page.locator(f'[data-subject="{subject}"]');assert entry.bounding_box()['height']>=64;entry.tap()
    page.wait_for_url(base+'#'+subject)
    assert page.locator('#'+subject).bounding_box()['y']>=0
    assert page.locator('#'+subject).bounding_box()['y']<height
    assert page.evaluate('document.documentElement.scrollWidth<=innerWidth')
    page.locator('#'+subject+' .subject-return').tap();page.wait_for_url(base+'#subjects')
   assert page.evaluate('Object.fromEntries(Object.entries(localStorage))')==saved
   page.screenshot(path=str(out/f'subjects-{width}.png'),full_page=False)
   # Opaque/damaged saves prove the hub never parses them. Entry checks below use
   # a clean isolated test session so legacy stories do not parse those fixtures.
   page.evaluate('localStorage.clear()')
   for subject,story in [('chinese','moon-cave'),('chinese','story-02'),('chinese','story-04'),('math','story-03'),('english','story-05')]:
    page.goto(base+'#'+subject);page.locator(f'[data-story="{story}"] .start').tap();page.wait_for_url(base+'stories/'+story+'/')
   assert not errors,errors;assert not bad,bad;assert not fonts,fonts
   context.close()
  context=browser.new_context(java_script_enabled=False,has_touch=True)
  page=context.new_page();page.goto(base);assert page.locator('.access-nojs').is_visible()
  assert page.locator('.subject-entry').first.evaluate('n=>getComputedStyle(n).visibility')=='hidden'
  page.locator('.access-nojs a').click();page.wait_for_url(base+'legal/');assert page.locator('h1').is_visible()
  browser.close()
 print('PASS subject anchors, five stories, English entry, all story links, 390/820/1180 touch layouts, no-JS access notice, no font dependency, saved data preserved')
 (out/'results.json').write_text(json.dumps({'passed':True,'sizes':[390,820,1180],'physical_tablet':False}),encoding='utf-8')
finally:server.shutdown()
