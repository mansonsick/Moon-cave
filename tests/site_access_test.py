"""Visitor reminder behavior, public notice, eight page hooks and no private-font delivery.

This tests a browser reminder, never claims server-side authentication.
"""
import hashlib,json
from pathlib import Path
from playwright.sync_api import sync_playwright
from story_test_support import serve,REPO

private=REPO.parent/'hub-review/site-access-password.txt'
pin=private.read_text(encoding='utf-8').strip() if private.exists() else '184629'
expected=hashlib.sha256(pin.encode()).hexdigest()
config=json.loads((REPO/'site-access.json').read_text(encoding='utf-8'))
if private.exists():assert config['sha256']==expected
assert pin not in (REPO/'site-access.js').read_text(encoding='utf-8')
server,base=serve()
try:
 with sync_playwright() as p:
  browser=p.chromium.launch();reports=[]
  for size in [(390,844),(820,1180),(1180,820)]:
   context=browser.new_context(viewport={'width':size[0],'height':size[1]},has_touch=True)
   if not private.exists():context.route('**/site-access.json',lambda r:r.fulfill(json={'sha256':expected}))
   page=context.new_page();errors=[];bad=[];fonts=[]
   page.on('pageerror',lambda e:errors.append(str(e)));page.on('response',lambda r:bad.append(r.url) if r.status>=400 else None)
   page.on('request',lambda r:fonts.append(r.url) if r.url.split('?')[0].endswith(('.ttf','.otf','.woff','.woff2')) else None)
   for route in ['',*[f'stories/{s}/' for s in ['moon-cave','story-02','story-03','story-04','story-05','story-06']],'stories/story-06/audio-review.html']:
    page.goto(base+route);page.wait_for_selector('.site-access');assert page.evaluate('document.documentElement.scrollWidth<=innerWidth')
    assert page.locator('body>:not(.site-access):not(script):not(style):not(noscript)').evaluate_all('ns=>ns.every(n=>getComputedStyle(n).visibility==="hidden"&&n.inert)')
    page.locator('#family-password').fill('000000');page.locator('.site-access button').click();page.wait_for_selector('.access-error img')
    assert page.locator('.site-access').is_visible()
    page.locator('#family-password').fill(pin);page.locator('.site-access button').click();page.wait_for_selector('.site-links');assert page.locator('.site-access').count()==0
    assert page.evaluate('document.documentElement.dataset.siteAccess')=='granted'
    # Same tab navigation/reload remembers it, but never alters gameplay saves.
    page.reload();page.wait_for_selector('.site-links');assert page.locator('.site-access').count()==0
    page.locator('.site-links button').click();page.wait_for_selector('.site-access')
   page.locator('.site-access a').click();page.wait_for_url(base+'legal/');page.wait_for_function('Array.from(document.images).every(i=>i.complete&&i.naturalWidth)')
   assert page.locator('.site-access').count()==0 and page.locator('h1').is_visible()
   assert 'CC' not in page.locator('h1').inner_text() # Title is the requested Chinese Zhuyin image.
   assert page.locator('a[href="https://creativecommons.org/licenses/by/4.0/"]').count()==1
   assert page.locator('a[href="https://www.tipo.gov.tw/tw/copyright/767-4893.html"]').count()==1
   assert '不能保證只有站主使用' in page.content() and page.evaluate('document.documentElement.scrollWidth<=innerWidth')
   out=REPO.parent/'hub-review/story05/access';out.mkdir(parents=True,exist_ok=True)
   page.screenshot(path=str(out/f'notice-{size[0]}.png'),full_page=True)
   assert not errors and not bad and not fonts,(errors,bad,fonts)
   reports.append({'width':size[0],'routes':8,'errors':errors});context.close()
  # Denied browser storage still permits this page, requiring re-entry after navigation.
  denied=browser.new_context();denied.add_init_script('Storage.prototype.getItem=()=>{throw Error("denied")};Storage.prototype.setItem=()=>{throw Error("denied")}')
  if not private.exists():denied.route('**/site-access.json',lambda r:r.fulfill(json={'sha256':expected}))
  page=denied.new_page();page.goto(base);page.locator('#family-password').fill(pin);page.locator('.site-access button').click();page.wait_for_selector('.site-links');page.reload();page.wait_for_selector('.site-access');denied.close()
  nojs=browser.new_context(java_script_enabled=False);page=nojs.new_page();page.goto(base);assert page.locator('.access-nojs').is_visible();page.locator('.access-nojs a').click();page.wait_for_url(base+'legal/');assert page.locator('h1').is_visible();nojs.close()
  # A new browser session is not remembered. This does not test resistance to bypass.
  fresh=browser.new_context();page=fresh.new_page();page.goto(base+'stories/story-05/');page.wait_for_selector('.site-access');fresh.close()
  (out/'results.json').write_text(json.dumps(reports,indent=2),encoding='utf-8')
  browser.close();print('PASS eight gated entry pages at 390/820/1180, wrong/right PIN, tab-session resume/logout, denied storage, no-JS notice, public legal page/credits and no font requests')
finally:server.shutdown()
