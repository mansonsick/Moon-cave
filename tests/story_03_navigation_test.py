"""Three-story hub and return-to-book menu preserve the active worksheet/save."""
from pathlib import Path
import json
from playwright.sync_api import sync_playwright
from story_test_support import serve
from camera_actions_test import FAKE,stopped

out=Path('../hub-review/story03-navigation');out.mkdir(parents=True,exist_ok=True)
server,base=serve()
try:
  with sync_playwright() as p:
    browser=p.chromium.launch();context=browser.new_context(viewport={'width':820,'height':1180});context.add_init_script(FAKE)
    page=context.new_page();errors=[];bad=[];requests=[]
    page.on('pageerror',lambda e:errors.append(str(e)));page.on('response',lambda r:bad.append(r.url) if r.status>=400 else None);page.on('request',lambda r:requests.append(r.url))
    page.goto(base);assert page.locator('.story-card').count()==3
    assert page.locator('.story-card').evaluate_all('cards=>cards.map(c=>c.dataset.story)')==['moon-cave','story-02','story-03']
    card=page.locator('[data-story="story-03"]');card.scroll_into_view_if_needed();page.evaluate('Promise.all([...document.images].map(i=>i.decode()))');card.screenshot(path=str(out/'hub-third-story.png'))
    card.locator('.start').click();page.wait_for_selector('body[data-ready=true]');assert page.evaluate('cameraCalls')==0
    assert not any('/vendor/' in u for u in requests)
    page.locator('[data-action=start]').click();page.locator('[data-action=continue]').click()
    page.locator('[data-digit="7"]').click()
    old=page.evaluate("JSON.parse(localStorage.getItem('adventure.story-03.state'))")
    page.locator('[data-action=story-menu]').click();assert page.locator('body').get_attribute('data-scene')=='cover'
    assert page.locator('[data-action=resume]').is_visible();page.reload();page.wait_for_selector('body[data-ready=true]');page.locator('[data-action=resume]').click()
    new=page.evaluate("JSON.parse(localStorage.getItem('adventure.story-03.state'))")
    assert new['scene']=='gate1' and new['passwords']==old['passwords'] and new['code']==old['code']
    assert new['resumeScene'] is None
    for width,height in [(390,844),(820,1180),(1180,820)]:
        page.set_viewport_size({'width':width,'height':height});page.evaluate("document.documentElement.style.setProperty('--text-scale',1.5)")
        assert page.locator('[data-action=story-menu]').is_visible();assert page.evaluate('document.documentElement.scrollWidth<=innerWidth')
    page.evaluate('''async()=>{const s=await import('./state.js'),m=await import('../../engine/math-worksheet.js');const v=s.fresh('menucamera'),w=m.createWorksheet(v.code);v.passwords[0]=m.gatePasswords(w,0);v.scene='balance';localStorage.setItem(s.KEY,JSON.stringify(v))}''')
    page.reload();page.wait_for_selector('body[data-ready=true]');page.evaluate("async()=>{window.fixtureBody=(await import('../../tests/camera_actions_rules.js')).body}")
    page.locator('[data-action=action-camera]').click();page.wait_for_selector('.camera-action[data-mode=camera]')
    page.locator('[data-action=story-menu]').click();assert stopped(page);assert page.locator('[data-action=resume]').is_visible()
    page.locator('[data-action=resume]').click();page.wait_for_selector('.camera-action[data-mode=idle]');assert page.evaluate('cameraCalls')==1
    assert not errors,errors;assert not bad,bad
    browser.close()
  print('PASS third hub card, fixed links/art, resume after refresh preserves code/answers, responsive header, menu closes camera and requires explicit restart')
  (out/'results.json').write_text(json.dumps({'passed':True,'real_camera':False}),encoding='utf-8')
finally:server.shutdown()
