"""Story 03 deterministic paper, layered art and both story routes.

python tests/story_03_test.py --output ../hub-review/story03-web
Uses the local Pages-prefix server; no camera/model claims.
"""
import argparse
import json
from pathlib import Path
from playwright.sync_api import sync_playwright
from story_test_support import serve

CODE = '5a2vgas12'
KEY = 'adventure.story-03.state'
EXPECTED = ['9-9','2+2','7-6','9-3','3+5','5+1','5-1','6-3','4+2','6+2','4-3','3+4','8+1','10-6','10-10','6+1','3+2','6-6','1+7','10-3']
ANSWERS = ['041686', '4368179', '4075087']
PASSWORDS = [('8','0'),('9','1'),('8','0')]
RESULTS=[]
def record(name):
    print('PASS',name,flush=True); RESULTS.append(name)
def complete_action(page):
    kind=page.locator('body').get_attribute('data-scene')
    if kind not in ['balance','jump','catch']:return
    page.locator('[data-action="action-manual"]').click()
    page.locator('[data-action="action-manual-start"]').click()
    if kind!='balance':
        for _ in range(5 if kind=='jump' else 3):page.locator('[data-action="action-manual-rep"]').click()
    page.wait_for_selector('.camera-action[data-mode="done"]',timeout=12000)
    assert state(page)['actions'][kind]
    page.locator('.camera-action [data-action="continue"]').click()

def act(page,name):
    root=page.locator('dialog[open]') if page.locator('dialog[open]').count() else page
    root.locator(f'[data-action="{name}"]').click()
    if name in ['continue','upstairs']:complete_action(page)
def scene(page,name): page.wait_for_selector(f'body[data-scene="{name}"]')
def ready(page):
    page.wait_for_selector('body[data-ready="true"]')
    page.evaluate('Promise.all([...document.images].map(i=>i.decode()))')
def state(page): return page.evaluate('(key)=>JSON.parse(localStorage.getItem(key))',KEY)
def enter(page,i,value):
    page.locator(f'[data-answer="{i}"]').click();act(page,'clear-answer')
    for digit in value:page.locator(f'[data-digit="{digit}"]').click()
def solve(page,g):
    for i,value in enumerate(PASSWORDS[g]): enter(page,i,value)
    act(page,'check')
    assert state(page)['solved'][g]
    assert page.locator('.password-card.correct').count()==2
    assert page.locator('.answer-mark').all_text_contents()==['✓']*2
    assert page.locator('[data-layer="door"]').count()==0
def to_roof(page,wood=False):
    act(page,'start'); act(page,'continue'); solve(page,0);act(page,'continue')
    scene(page,'passage');act(page,'continue');solve(page,1);act(page,'continue');scene(page,'window')
    if wood:
        act(page,'find-wood');assert page.locator('dialog[open]').count()==1
        act(page,'continue'); assert page.locator('[data-item="wood"]').count()==1
        assert page.locator('[data-action="find-wood"]').count()==0
    act(page,'upstairs');solve(page,2);act(page,'continue');scene(page,'chest')
    act(page,'open-chest');assert state(page)['seed'];act(page,'continue');scene(page,'roof')

def main():
    parser=argparse.ArgumentParser();parser.add_argument('--output',type=Path,default=Path('../hub-review/story03-web'));args=parser.parse_args();args.output.mkdir(parents=True,exist_ok=True)
    server,root=serve();url=root+'stories/story-03/'
    with sync_playwright() as p:
        browser=p.chromium.launch()
        context=browser.new_context(viewport={'width':820,'height':1180},has_touch=True)
        page=context.new_page();errors=[];missing=[]
        page.on('pageerror',lambda e:errors.append(str(e)))
        page.on('response',lambda r:missing.append(r.url) if r.status>=400 else None)
        page.goto(url+'?code='+CODE);ready(page)
        props=page.evaluate('''async () => {
          const m=await import('../../engine/math-worksheet.js');
          const w=m.createWorksheet('  5A2VGAS12  ');
          for(let n=0;n<500;n++){
            const x=m.createWorksheet('sample'+n),qs=x.gates.flatMap(g=>g.questions);
            if(x.gates.map(g=>g.questions.length).join()!=[6,7,7].join())throw Error('size');
            if(qs.filter(q=>q.op==='+').length!==10||new Set(qs.map(q=>`${q.a}${q.op}${q.b}`)).size!==20)throw Error('distribution');
            if(qs.some(q=>m.resultOf(q)<0||m.resultOf(q)>9||q.a>10||q.b>10))throw Error('range');
            if(JSON.stringify(x)!==JSON.stringify(m.createWorksheet('sample'+n)))throw Error('determinism');
          }
          for(const code of ['', 'a-b','<img>', 'a'.repeat(25)])if(m.normalizeCode(code)!==null)throw Error('validation');
          const {validate,fresh}=await import('./state.js');
          const bad={...fresh('x'),scene:'secret',seed:true,wood:true,placed:true,entries:[['x',''],[],[]]};
          if(validate(bad).scene!=='gate1'||validate({...bad,version:'future'})!==null)throw Error('save validation');
          return {equations:w.gates.flatMap(g=>g.questions).map(q=>`${q.a}${q.op}${q.b}`),code:w.code};
        }''')
        assert props=={'equations':EXPECTED,'code':CODE};record('500 deterministic codes, frozen example, 6/7/7, arithmetic ranges and damaged-save guards')
        assert page.locator('.scene-layer').count()==3
        assert page.locator('.inventory').count()==0
        page.screenshot(path=str(args.output/'cover.png'),full_page=True)
        page.evaluate("localStorage.setItem('moonCaveV3Save','keep');localStorage.setItem('adventure.story-02.state','keep02')")
        act(page,'sound');assert page.evaluate("localStorage.getItem('adventure.settings.sound')")=='false'
        act(page,'start');act(page,'continue');scene(page,'gate1')
        act(page,'check');assert state(page)['solved']==[False]*3
        enter(page,0,'1');enter(page,1,'0');act(page,'check')
        assert page.locator('[data-answer="1"]').get_attribute('data-value')=='0'
        assert page.locator('.password-card').nth(1).locator('.answer-mark').inner_text()=='✓'
        assert page.locator('.password-card').nth(0).locator('.answer-mark').inner_text()=='×'
        assert page.locator('.symbol-key .code-symbol').count()==10
        assert page.locator('.symbol-key .symbol-digit').all_text_contents()==list('0123456789')
        page.reload();ready(page);scene(page,'gate1');assert page.locator('[data-answer="0"]').get_attribute('data-value')=='1'
        assert page.locator('.password-card.correct').count()==1
        assert page.locator('.feedback img').count()>0
        page.screenshot(path=str(args.output/'symbol-feedback.png'),full_page=True)
        before_passwords=state(page)['passwords']
        act(page,'review-questions');page.locator('dialog [data-digit="1"]').click();act(page,'check-question')
        assert page.locator('.review-feedback.wrong').count()==1
        act(page,'clear-answer');page.locator('dialog [data-digit="0"]').click();act(page,'check-question')
        assert page.locator('.review-feedback.correct').count()==1
        assert state(page)['passwords']==before_passwords
        assert state(page)['solved']==[False]*3
        act(page,'close')
        solve(page,0);page.reload();ready(page);scene(page,'gate1');assert page.locator('[data-action="continue"]').count()==1
        act(page,'continue');act(page,'continue');solve(page,1);act(page,'continue');act(page,'upstairs');solve(page,2);act(page,'continue');act(page,'open-chest');act(page,'continue');act(page,'go-home');scene(page,'ordinary')
        page.screenshot(path=str(args.output/'ordinary.png'),full_page=True)
        record('two extrema passwords, numeric badges, green/red feedback, optional single-question review, muted ordinary route, valid zero and refresh')
        act(page,'replay');act(page,'yes-replay');scene(page,'cover');assert state(page)['code']==CODE
        assert page.evaluate("localStorage.getItem('moonCaveV3Save')")=='keep'
        assert page.evaluate("localStorage.getItem('adventure.story-02.state')")=='keep02'
        to_roof(page,wood=True)
        source=page.locator('[data-item="wood"]');target=page.locator('.wood-slot')
        source.scroll_into_view_if_needed();a=source.bounding_box();b=target.bounding_box()
        # The paper can extend beyond the viewport; bring both into view for a touch drag.
        page.set_viewport_size({'width':820,'height':1500});source.scroll_into_view_if_needed();target.scroll_into_view_if_needed();a=source.bounding_box();b=target.bounding_box()
        page.mouse.move(a['x']+a['width']/2,a['y']+a['height']/2);page.mouse.down();page.mouse.move(b['x']+b['width']/2,b['y']+b['height']/2,steps=12);page.mouse.up()
        assert state(page)['placed'];assert page.locator('.wood-slot.placed svg').count()==1
        page.screenshot(path=str(args.output/'roof-placed.png'),full_page=True)
        page.reload();ready(page);assert page.locator('.wood-slot.placed svg').count()==1
        act(page,'continue');scene(page,'secret');page.screenshot(path=str(args.output/'secret.png'),full_page=True)
        act(page,'continue');scene(page,'secret-home')
        record('optional wood, pointer drag alignment, retained glowing piece after reload, secret ending and forest return')
        act(page,'replay');act(page,'yes-replay');to_roof(page,wood=True);act(page,'go-home');scene(page,'ordinary');record('wood acquired but unused still reaches full ordinary success')
        before=state(page);printing=context.new_page();printing.goto(url+'print.html?code='+CODE);ready(printing)
        assert printing.locator('.paper').count()==3
        assert printing.locator('.answer-box').all_text_contents()==['']*20
        assert printing.locator('.packet-code').all_text_contents()==[CODE]*3
        assert printing.locator('.code-legend').count()==0
        assert printing.locator('[aria-label*="不用補零"]').count()==0
        dims=printing.locator('.answer-box').first.evaluate('(e)=>[e.offsetWidth,e.offsetHeight]');assert all(abs(v-mm*96/25.4)<1 for v,mm in zip(dims,[86,23]))
        assert printing.locator('.paper-password-answer').all_text_contents()==['']*6
        assert state(page)==before
        printing.pdf(path=str(args.output/'generated-print.pdf'),prefer_css_page_size=True,print_background=True)
        for i in range(3):printing.locator('.paper').nth(i).screenshot(path=str(args.output/f'paper-{i+1}.png'))
        printing.goto(url+'print.html?code='+CODE+'&mode=answers');ready(printing)
        assert printing.locator('.answer-box').all_text_contents()==list(''.join(ANSWERS))
        assert printing.locator('.code-legend,[aria-label*="不用補零"]').count()==0
        assert printing.locator('.paper-password-answer').all_text_contents()==[v for row in PASSWORDS for v in row]
        assert state(page)==before
        record('three A4 sheets, unsegmented wide answer areas, max/min summary, separate answer page, printing does not alter saved play')
        page.locator('.packet-tools summary').click();act(page,'change');page.locator('dialog input[name=code]').fill('another123');act(page,'use-code')
        assert state(page)['code']==CODE;act(page,'cancel');assert state(page)['code']==CODE
        act(page,'change');page.locator('dialog input[name=code]').fill('another123');act(page,'use-code');act(page,'yes-change');assert state(page)['code']=='another123'
        second=context.new_page();second.goto(url);ready(second)
        page.locator('.prepare summary').click();act(page,'new-code');second.wait_for_selector('dialog[open]');assert second.locator('[data-action="reload"]').count()==1
        record('explicit packet replacement confirmation and other-tab stale-code guard')
        for width,height in [(390,844),(820,1180),(1180,820)]:
            mobile=browser.new_page(viewport={'width':width,'height':height});mobile.goto(url+'?code='+CODE);ready(mobile)
            for _ in range(6):act(mobile,'larger')
            assert mobile.evaluate('document.documentElement.scrollWidth<=innerWidth')
            act(mobile,'start');act(mobile,'continue');ready(mobile)
            assert mobile.evaluate('document.documentElement.scrollWidth<=innerWidth')
            mobile.screenshot(path=str(args.output/f'gate-{width}.png'),full_page=True);mobile.close()
        record('portrait phone/tablet and landscape layouts with maximum A+; zoom viewport remains unrestricted')
        no_store=browser.new_context();no_store.add_init_script("Object.defineProperty(window,'localStorage',{get(){throw new Error('blocked')}})")
        fallback=no_store.new_page();fallback.goto(url+'?code='+CODE);ready(fallback);assert fallback.locator('#storage-note img').count()>0
        act(fallback,'start');act(fallback,'continue')
        for i,d in enumerate(PASSWORDS[0]):enter(fallback,i,d)
        act(fallback,'check');assert fallback.locator('[data-action="continue"]').count()==1
        no_store.close();record('blocked storage retains a playable in-memory session and visible reminder')
        assert not errors,errors;assert not missing,missing
        context.close();browser.close()
    server.shutdown();(args.output/'results.json').write_text(json.dumps({'passed':RESULTS},ensure_ascii=False,indent=2),encoding='utf-8')
    print(f'{len(RESULTS)} groups passed')

if __name__=='__main__':main()
