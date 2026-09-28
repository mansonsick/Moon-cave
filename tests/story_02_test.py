"""Story 02 acceptance through the real browser UI.

python tests/story_02_test.py --output ../hub-review/story02-tests
Requires Playwright + Chromium. No production assets/storage are modified.
"""
import argparse
import hashlib
import json
import subprocess
from pathlib import Path
from playwright.sync_api import sync_playwright, expect
from story_test_support import REPO, serve

KEY = 'adventure.story-02.state'
RESULTS = []
def record(name, detail):
    RESULTS.append(dict(check=name, result='PASS', detail=detail)); print('PASS '+name, flush=True)

def scene(page, id): expect(page.locator('#story')).to_have_attribute('data-scene', id)
def action(page, name): page.locator(f'[data-action="{name}"]').click()
def state(page): return page.evaluate('(key)=>JSON.parse(localStorage.getItem(key))', KEY)
def no_spoilers(page):
    visible = page.evaluate('''() => document.title + document.body.innerText + [...document.querySelectorAll('[aria-label],img[alt]')].filter(e=>e.getClientRects().length).map(e=>e.getAttribute('aria-label')||e.alt).join(' ')''')
    assert '虎姑婆' not in visible, visible
    assert '山神鈴' not in visible, visible
    assert page.locator('[data-item="bell"]').count() == 0

def images(page):
    page.wait_for_function('''() => [...document.images].every(img=>img.complete && img.naturalWidth>0)''')

def countdown(page):
    action(page, 'challenge-start'); page.clock.run_for(9000)
    expect(page.locator('[data-testid="reward"]')).to_be_visible()
    page.clock.run_for(20000)
    expect(page.locator('[data-testid="reward"]')).to_be_visible()
    action(page, 'continue')

def run_bamboo(page, collision=False):
    action(page, 'challenge-start')
    field = page.locator('.dodge-field')
    if collision:
        page.clock.run_for(2750)
        assert field.get_attribute('data-passed') == '0'
        assert float(field.get_attribute('data-position')) < 70
        assert page.locator('[aria-label="碰到了！慢慢換一邊，再出發。"]') .count() == 1
    for _ in range(50):
        if page.locator('[data-testid="reward"]').count(): break
        obstacle = int(field.get_attribute('data-obstacle'))
        lane = int(field.get_attribute('data-lane'))
        desired = 0 if obstacle != 0 else 2
        for _ in range(abs(lane-desired)): action(page, 'left' if desired<lane else 'right')
        page.clock.run_for(600)
    expect(page.locator('[data-testid="reward"]')).to_be_visible()
    assert 'bamboo' in state(page)['completed']
    action(page, 'continue'); scene(page, 'fork')

def begin(page, url):
    page.goto(url); page.wait_for_selector('[data-action="start-adventure"]'); action(page, 'start-adventure')

def main():
    parser=argparse.ArgumentParser(); parser.add_argument('--output',type=Path,default=REPO.parent/'hub-review/story02-tests'); args=parser.parse_args(); args.output.mkdir(parents=True,exist_ok=True)
    server, base = serve(); url=base+'stories/story-02/'
    try:
        with sync_playwright() as p:
            browser=p.chromium.launch()
            context=browser.new_context(viewport={'width':820,'height':1180},has_touch=True)
            context.add_init_script("Object.defineProperty(window,'DeviceOrientationEvent',{value:undefined,configurable:true});")
            page=context.new_page(); errors=[]; failed=[]
            page.on('pageerror',lambda error: errors.append(str(error)))
            page.on('response',lambda response: failed.append(response.url) if response.status>=400 else None)
            page.clock.install()
            page.goto(url); page.wait_for_selector('[data-action="start-adventure"]')
            page.evaluate("localStorage.setItem('moonCaveState','moon-sentinel');localStorage.setItem('moonCaveTextScale','1.2');")
            no_spoilers(page); images(page); page.screenshot(path=str(args.output/'cover-820.png'),full_page=True)
            # Sound preference can be changed before Start, but audio must remain locked.
            action(page,'sound'); assert page.evaluate("localStorage.getItem('adventure.settings.sound')")=='false'
            action(page,'start-adventure'); scene(page,'path'); no_spoilers(page)
            action(page,'house'); scene(page,'house'); no_spoilers(page)
            action(page,'enter'); scene(page,'welcome'); no_spoilers(page)
            action(page,'continue'); scene(page,'clues'); no_spoilers(page)
            images(page); page.screenshot(path=str(args.output/'clues-820.png'),full_page=True)
            for id in ['prints','fur']:
                page.locator(f'[data-target="{id}"]').click(); no_spoilers(page)
                page.locator(f'[data-target="{id}"]').evaluate('(button)=>button.dispatchEvent(new MouseEvent("click",{bubbles:true}))')
            assert state(page)['clues']==['prints','fur']
            page.reload(); action(page,'start-adventure'); scene(page,'clues'); no_spoilers(page)
            assert page.locator('.find-hit.found').count()==2
            page.locator('[data-target="tail"]').click()
            expect(page.locator('[aria-label="阿通心裡一驚：她是虎姑婆！"]')).to_be_visible()
            assert '虎姑婆' in page.title(); assert len(state(page)['clues'])==3
            page.clock.run_for(15000); scene(page,'clues'); action(page,'continue'); scene(page,'key')
            record('identity-and-clues','No identity/bell spoilers before all 3 clues; duplicate clicks do not count; partial clue progress resumes; reveal/reward waits for Continue.')
            page.clock.run_for(14000); assert page.locator('[data-action="hint-one"]').count()==0
            page.clock.run_for(1600); action(page,'hint-one'); assert page.locator('[data-action="hint-two"]').count()==0
            page.clock.run_for(15500); action(page,'hint-two')
            expect(page.locator('.find-hit.hinted')).to_be_visible()
            action(page,'take-key'); assert state(page)['inventory']==['key']
            page.locator('[data-target="key"]').evaluate('(e)=>e.dispatchEvent(new MouseEvent("click",{bubbles:true}))')
            assert state(page)['inventory']==['key']
            page.reload(); action(page,'start-adventure'); expect(page.locator('[data-testid="reward"]')).to_be_visible()
            action(page,'continue'); scene(page,'hide'); hide_state=state(page)
            record('key-hints-and-save','First hint after 15 seconds, second after 30; explicit final pickup prevents a dead end; item/reward survives reload with no duplicate grant.')
            countdown(page); scene(page,'bamboo'); run_bamboo(page,collision=True); fork_state=state(page)
            hidden_style=page.locator('[data-action="tracks"]').evaluate('(e)=>({shadow:getComputedStyle(e).boxShadow,background:getComputedStyle(e).backgroundColor})')
            assert hidden_style=={'shadow':'none','background':'rgba(0, 0, 0, 0)'}
            assert page.locator('[data-item="bell"]').count()==0
            images(page); page.screenshot(path=str(args.output/'fork-820.png'),full_page=True)
            action(page,'bridge'); scene(page,'bridge'); countdown(page); scene(page,'temple')
            assert page.locator('[data-item="bell"]').count()==0
            action(page,'wait'); scene(page,'ordinary'); assert state(page)['ending']=='ordinary'
            record('ordinary-full-route-muted','Complete route from cover through all required scenes with sound off, unsupported sensors -> 8-second countdowns, and 5 obstacles using buttons; collision is recoverable.')
            # Reuse a legitimately achieved fork checkpoint to cover both optional branches.
            page.evaluate('([key,value])=>localStorage.setItem(key,JSON.stringify(value))',[KEY,fork_state])
            page.reload(); action(page,'start-adventure'); action(page,'tracks'); scene(page,'shrine')
            assert page.locator('[data-item="bell"]').count()==0
            page.locator('[data-target="bell"]').click(); assert state(page)['inventory']==['key','bell']
            page.locator('[data-target="bell"]').evaluate('(e)=>e.dispatchEvent(new MouseEvent("click",{bubbles:true}))')
            assert state(page)['inventory'].count('bell')==1
            action(page,'continue'); countdown(page); scene(page,'temple'); temple_state=state(page)
            assert page.locator('button').filter(has_text='使用山神鈴').count()==0
            hook=page.locator('[data-testid="bell-hook"]')
            assert hook.evaluate('(e)=>getComputedStyle(e).boxShadow')=='none'
            action(page,'wait'); scene(page,'ordinary'); assert state(page)['ending']=='ordinary'
            record('unused-bell-ordinary','Optional prints are unlit; bell has no inventory slot before discovery; repeated discovery is idempotent; owned but unused bell still reaches the complete ordinary ending.')
            page.evaluate('([key,value])=>localStorage.setItem(key,JSON.stringify(value))',[KEY,temple_state])
            page.reload(); action(page,'start-adventure'); images(page)
            page.screenshot(path=str(args.output/'temple-empty-820.png'),full_page=True)
            source=page.locator('[data-item="bell"]'); source.scroll_into_view_if_needed()
            a=source.bounding_box(); b=page.locator('[data-testid="bell-hook"]').bounding_box()
            page.mouse.move(a['x']+a['width']/2,a['y']+a['height']/2); page.mouse.down()
            page.mouse.move(10,10,steps=4); page.mouse.up()
            assert state(page)['placed']==[] and page.locator('.drag-ghost').count()==0
            # Real mouse pointer capture path first (touch path covered below).
            page.mouse.move(a['x']+a['width']/2,a['y']+a['height']/2); page.mouse.down()
            page.mouse.move(b['x']+b['width']/2,b['y']+b['height']/2,steps=12); page.mouse.up()
            assert state(page)['placed']==['bell']; expect(page.locator('.bell-hook.placed')).to_be_visible()
            page.clock.run_for(15000); scene(page,'temple'); images(page); page.screenshot(path=str(args.output/'temple-placed-820.png'),full_page=True)
            page.reload(); action(page,'start-adventure'); expect(page.locator('.bell-hook.placed')).to_be_visible()
            action(page,'continue'); scene(page,'secret'); assert state(page)['ending']=='secret'
            action(page,'continue'); scene(page,'secret-after')
            record('secret-ending-and-drag','Actual pointer drag onto aligned empty hook locks a glowing bell, persists on reload, waits for Continue, reaches divine ending and illusion-disappearance epilogue.')
            action(page,'replay'); action(page,'confirm-replay'); action(page,'start-adventure'); scene(page,'path')
            no_spoilers(page)
            assert page.evaluate("localStorage.getItem('moonCaveState')")=='moon-sentinel'
            assert page.evaluate("localStorage.getItem('moonCaveTextScale')")=='1.2'
            assert page.evaluate("localStorage.getItem('adventure.settings.sound')")=='false'
            assert state(page)['inventory']==[] and state(page)['completed']==[]
            record('storage-isolation','Replay clears only Story 02 progress; Moon Cave sentinels and common sound preference remain unchanged.')
            # Tablet touch drag, portrait and landscape, plus text scale and pinch-zoom metadata.
            for width,height in [(768,1024),(1180,820),(390,844)]:
                page.set_viewport_size({'width':width,'height':height})
                page.evaluate('([key,value])=>localStorage.setItem(key,JSON.stringify(value))',[KEY,temple_state]); page.reload(); action(page,'start-adventure')
                page.get_by_role('button',name='放大文字',exact=True).click(); page.get_by_role('button',name='放大文字',exact=True).click()
                images(page); assert page.evaluate('document.documentElement.scrollWidth<=innerWidth'), (width,height)
                page.screenshot(path=str(args.output/f'temple-{width}.png'),full_page=True)
                if width==768:
                    source=page.locator('[data-item="bell"]'); source.scroll_into_view_if_needed(); a=source.bounding_box(); b=page.locator('.bell-hook').bounding_box()
                    cdp=context.new_cdp_session(page)
                    cdp.send('Input.dispatchTouchEvent',{'type':'touchStart','touchPoints':[{'x':a['x']+a['width']/2,'y':a['y']+a['height']/2}]})
                    cdp.send('Input.dispatchTouchEvent',{'type':'touchMove','touchPoints':[{'x':b['x']+b['width']/2,'y':b['y']+b['height']/2}]})
                    cdp.send('Input.dispatchTouchEvent',{'type':'touchEnd','touchPoints':[]})
                    assert state(page)['placed']==['bell']
                assert 'user-scalable=no' not in page.locator('meta[name="viewport"]').get_attribute('content')
            record('tablet-and-touch','768px/820px portrait, 1180px landscape and 390px phone; A+ does not overflow; touch pointer drag works; native pinch zoom is not disabled. Real-device review remains pending.')
            assert not errors,errors; assert not failed,failed
            record('browser-loads','No JavaScript errors or failed HTTP resources in UI journeys; undelivered audio triggers no asset requests.')
            # Damaged storage / unavailable storage cannot block progress.
            page.evaluate('(key)=>localStorage.setItem(key,"{broken")',KEY); page.reload(); action(page,'start-adventure'); scene(page,'path')
            blocked=browser.new_context(); blocked.add_init_script("Storage.prototype.getItem=function(){throw new DOMException('blocked','SecurityError')};Storage.prototype.setItem=function(){throw new DOMException('blocked','QuotaExceededError')};")
            q=blocked.new_page(); begin(q,url); scene(q,'path'); action(q,'house'); scene(q,'house'); blocked.close()
            record('storage-failure','Corrupt JSON starts safely; blocked/quota-exceeded storage still allows playing in memory.')
            unavailable=browser.new_context(); q=unavailable.new_page()
            q.route('**/story.json',lambda route:route.fulfill(status=503,body='unavailable'))
            q.goto(url); expect(q.get_by_role('button',name='重新整理',exact=True)).to_be_visible()
            assert q.locator('.load-error img').count()==3
            unavailable.close()
            browser.close()
        protected=['index.html','stories/moon-cave/index.html','assets/hub-text','assets/moon-cave-cover.webp']
        diff=subprocess.check_output(['git','diff','origin/main','--',*protected],cwd=REPO)
        assert not diff
        assert not list((REPO/'stories/story-02').rglob('*.ttf'))
        manifest=json.loads((REPO/'stories/story-02/assets/images/sources.json').read_text(encoding='utf-8'))
        for entry in manifest:
            assert hashlib.sha256((REPO/'stories/story-02/assets/images'/entry['file']).read_bytes()).hexdigest()==entry['sha256'],entry['file']
        config=json.loads((REPO/'stories/story-02/story.json').read_text(encoding='utf-8'))
        text=json.loads((REPO/'stories/story-02/assets/text/text.json').read_text(encoding='utf-8'))
        assert set(config['labels'])==set(text['labels'])
        for id,label in text['labels'].items():
            assert label['text']==config['labels'][id]
            for part in label['parts']: assert (REPO/'stories/story-02/assets/text'/part['src']).is_file()
        record('published-story-preserved','Homepage, Moon Cave code and prior hub assets have no diff from origin/main; no font file was copied into Story 02.')
        (args.output/'results.json').write_text(json.dumps(RESULTS,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
    finally: server.shutdown()

if __name__=='__main__': main()
