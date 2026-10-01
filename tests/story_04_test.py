"""Story 04 browser acceptance: teach before practice, endings, paper and isolated saves."""
import json
from pathlib import Path
from playwright.sync_api import sync_playwright
from story_test_support import serve,REPO

OUT=REPO.parent/'hub-review/story-04-qa';OUT.mkdir(parents=True,exist_ok=True)
DATA=json.loads((REPO/'stories/story-04/story.json').read_text(encoding='utf-8'))
ANSWERS=['山','水','日','月','木','口','上','下','拿','放','隻','朵','上','門口','樹下','阿通','讀小紙','花','小兔','種花']
server,base=serve();url=base+'stories/story-04/'
def click(page,action):
    scope=page.locator('.dialog') if page.locator('.dialog').count() else page
    scope.locator(f'[data-action="{action}"]').first.click()
def scene(page,id):page.wait_for_selector(f'#app[data-scene="{id}"]')
def ready(page):page.wait_for_selector('#app[data-scene="menu"]')
def images(page):page.evaluate('async()=>{await Promise.all([...document.images].map(i=>i.decode()));}')
def snapshot(page,name):
    images(page);page.screenshot(path=str(OUT/(name+'.png')),full_page=True)
def learn(page,stage):
    assert page.locator('.question').count()==0,'Questions appeared before teaching'
    assert page.locator('.learning-card').count()==1
    for _ in range(len(DATA['learning'][stage])-1):click(page,'next-card')
    click(page,'learn-done');assert page.locator('.question').count()==2
def solve(page,full=False):
    if full:click(page,'all-mode')
    for id in page.locator('.question').evaluate_all('items=>items.map(i=>i.dataset.question)'):
        expected=ANSWERS[int(id[1:])-1]
        option=next(c for c in DATA['questions'][int(id[1:])-1]['choices'] if DATA['labels'][c]==expected)
        page.locator(f'input[name="{id}"][value="{option}"]').check()
    click(page,'check');assert page.locator('.reward').count()==1
    assert page.locator('.incorrect').count()==0
def begin(page):
    page.goto(url);ready(page);click(page,'start-adventure');scene(page,'S01');click(page,'into-office');scene(page,'S02');click(page,'prepared');scene(page,'S03')
def route(page,leaf=False,full=False):
    begin(page);learn(page,0)
    # Wrong answer is recoverable and offers a hint without advancing.
    q='Q02';wrong=next(c for c in DATA['questions'][1]['choices'] if DATA['labels'][c]!='水')
    page.locator(f'input[name="{q}"][value="{wrong}"]').check();click(page,'check')
    assert page.locator(f'[data-question="{q}"].incorrect').count()==1;scene(page,'S03')
    click(page,'review-Q02');assert page.locator('.learning-card .word').get_attribute('aria-label')=='水';click(page,'back-practice')
    solve(page,full);click(page,'word-cards');assert page.locator('.learning-card').count()==1
    # Revisiting learning does not erase successfully completed practice.
    for _ in range(5):click(page,'next-card')
    click(page,'learn-done');assert page.locator('.reward').count()==1
    click(page,'continue');scene(page,'S04');click(page,'mountain-road');scene(page,'S04');click(page,'bridge-road');scene(page,'S05');snapshot(page,'rabbit-before')
    click(page,'tree-basket');assert page.locator('.reward').count()==0
    click(page,'door-tray');assert page.locator('.reward').count()==1;click(page,'continue');scene(page,'S06')
    learn(page,1);solve(page,full);click(page,'continue');scene(page,'S07')
    snapshot(page,'bear-before');click(page,'under-table');assert page.locator('.reward').count()==0;click(page,'table-top');click(page,'continue');scene(page,'S08')
    assert page.locator('[data-item="leaf"]').count()==0
    hidden=page.locator('[data-action="hidden-leaf"]');assert hidden.evaluate('e=>getComputedStyle(e).boxShadow')=='none'
    assert '金色葉片' not in page.inner_text('.inventory')
    if leaf:
        hidden.click();scene(page,'H01');assert page.locator('[data-item="leaf"]').count()==1;click(page,'continue');scene(page,'S08');assert page.locator('[data-action="hidden-leaf"]').count()==0
    click(page,'walk-tree');scene(page,'S09');learn(page,2);solve(page,full);click(page,'continue');scene(page,'S10')
    assert page.get_by_role('img',name='三封信都送到了。',exact=True).count()==0
    snapshot(page,'bird-before');click(page,'nest');assert page.locator('.reward').count()==0;click(page,'root-tray');assert page.get_by_role('img',name='三封信都送到了。',exact=True).count()==1;click(page,'continue');scene(page,'S11')
    images(page);page.screenshot(path=str(OUT/('mailbox-leaf.png' if leaf else 'mailbox-normal.png')),full_page=True)
try:
 with sync_playwright() as p:
    browser=p.chromium.launch()
    context=browser.new_context(viewport={'width':820,'height':1180},has_touch=True)
    page=context.new_page();errors=[];bad=[];fonts=[]
    page.on('pageerror',lambda e:errors.append(str(e)))
    page.on('response',lambda r:bad.append((r.status,r.url)) if r.status>=400 else None)
    page.on('request',lambda r:fonts.append(r.url) if r.url.split('?')[0].endswith(('.ttf','.otf','.woff','.woff2')) else None)
    page.goto(url);ready(page)
    preserved={'moonCaveState':'legacy','adventure.story-02.state':'two','adventure.story-03.state':'three','unrelated':'other'}
    page.evaluate('(v)=>Object.entries(v).forEach(([k,s])=>localStorage.setItem(k,s))',preserved)
    # Complete ordinary ending with representative paper checks.
    route(page);click(page,'back-office');scene(page,'E01');click(page,'menu');ready(page)
    saved=json.loads(page.evaluate('localStorage.getItem("adventure.story-04.state")'));code=saved['code']
    assert saved['ending']=='ordinary' and saved['delivered']==[True]*3 and len(saved['checked'])==6
    page.reload();ready(page);click(page,'start-adventure');scene(page,'E01')
    click(page,'replay');click(page,'cancel');scene(page,'E01');click(page,'replay');click(page,'yes-replay');scene(page,'S01')
    for k,v in preserved.items():assert page.evaluate('(k)=>localStorage.getItem(k)',k)==v
    # Full tablet mode: all twenty checks, leaf drag, secret route.
    page.evaluate('localStorage.removeItem("adventure.story-04.state")')
    route(page,leaf=True,full=True)
    source=page.locator('[data-item="leaf"]');target=page.locator('[data-action="mailbox"]')
    source.scroll_into_view_if_needed();a=source.bounding_box();b=target.bounding_box()
    cdp=context.new_cdp_session(page);sx,sy=a['x']+a['width']/2,a['y']+a['height']/2;tx,ty=b['x']+b['width']/2,b['y']+b['height']/2
    assert 0<=sy<1180 and 0<=ty<1180
    cdp.send('Input.dispatchTouchEvent',{'type':'touchStart','touchPoints':[{'x':sx,'y':sy,'id':1}]})
    for step in range(1,9):cdp.send('Input.dispatchTouchEvent',{'type':'touchMove','touchPoints':[{'x':sx+(tx-sx)*step/8,'y':sy+(ty-sy)*step/8,'id':1}]})
    cdp.send('Input.dispatchTouchEvent',{'type':'touchEnd','touchPoints':[]})
    assert page.locator('.placed-leaf').count()==1 and page.locator('.reward').count()==1
    assert page.locator('.placed-leaf').evaluate('e=>getComputedStyle(e).filter')!='none'
    page.reload();ready(page);click(page,'start-adventure');scene(page,'S11');assert page.locator('.placed-leaf').count()==1
    click(page,'continue');scene(page,'E02');click(page,'visit-tree');scene(page,'E03');images(page);page.screenshot(path=str(OUT/'secret-ending.png'),full_page=True)
    saved=json.loads(page.evaluate('localStorage.getItem("adventure.story-04.state")'));assert len(saved['checked'])==20 and saved['ending']=='secret'
    # Leaf is optional even when found.
    page.evaluate('localStorage.removeItem("adventure.story-04.state")');route(page,leaf=True);click(page,'back-office');scene(page,'E01')
    # Changing codes is explicit; invalid input cannot destroy an existing save.
    click(page,'menu');before=page.evaluate('localStorage.getItem("adventure.story-04.state")');page.locator('#code-input').fill('not-a-code');click(page,'apply-code');assert page.evaluate('localStorage.getItem("adventure.story-04.state")')==before
    click(page,'new-paper');click(page,'cancel');assert page.evaluate('localStorage.getItem("adventure.story-04.state")')==before
    click(page,'new-paper');click(page,'apply-code');ready(page);newcode=page.locator('#code-input').input_value();assert newcode!=code
    # Paper code is reproducible; paper answers are separate.
    actual=page.evaluate('async c=>{const m=await import("../../engine/reading-worksheet.js");const d=await(await fetch("story.json")).json();return [m.readingWorksheet(d,c),m.readingWorksheet(d,c)];}',newcode);assert actual[0]==actual[1]
    for parent in [False,True]:
        page.goto(url+'print.html?code='+newcode+('&answers=1' if parent else ''));page.wait_for_selector('.paper-page');images(page)
        assert page.locator('.paper-page').count()==(1 if parent else 3);assert page.locator('[data-question]').count()==20
        assert page.locator('.solution').count()==(20 if parent else 0)
        page.pdf(path=str(OUT/('answers.pdf' if parent else 'practice.pdf')),prefer_css_page_size=True,print_background=True)
        page.screenshot(path=str(OUT/('answers-screen.png' if parent else 'practice-screen.png')),full_page=True)
    page.goto(url+'print.html?code=bad');page.wait_for_selector('[aria-label="題卷碼不正確，請再看一次。"]');assert page.locator('.paper-page').count()==0
    # Malformed and internally inconsistent saves recover; denied storage still works.
    page.goto(url);ready(page);page.evaluate('localStorage.setItem("adventure.story-04.state","{bad")');page.reload();ready(page);click(page,'start-adventure');scene(page,'S01')
    repaired=page.evaluate('async c=>{const m=await import("./state.js");const d=await(await fetch("story.json")).json();return m.validate(d,{...m.fresh(c),scene:"E03",leaf:true,placed:true,delivered:[true,true,true]});}',newcode)
    assert repaired['scene']=='S03' and repaired['delivered']==[False]*3 and not repaired['leaf'] and not repaired['placed']
    assert not errors,errors;assert not bad,bad;assert not fonts,fonts
    context.close()
    for width,height in [(390,844),(820,1180),(1180,820)]:
        context=browser.new_context(viewport={'width':width,'height':height},has_touch=True);page=context.new_page();begin(page);images(page)
        assert page.evaluate('document.documentElement.scrollWidth<=innerWidth')
        for _ in range(5):page.get_by_role('button',name='放大文字',exact=True).click()
        images(page);assert page.evaluate('document.documentElement.scrollWidth<=innerWidth')
        assert page.locator('.bpmf img').evaluate_all('items=>items.every(i=>Math.abs((i.getBoundingClientRect().width/i.getBoundingClientRect().height)/(i.naturalWidth/i.naturalHeight)-1)<.02)'),'Zhuyin image was stretched'
        page.screenshot(path=str(OUT/f'learning-{width}.png'),full_page=True)
        click(page,'menu');ready(page);page.get_by_role('link',name='回首頁',exact=True).click();page.wait_for_url(base);context.close()
    context=browser.new_context();context.add_init_script("Storage.prototype.getItem=()=>{throw new Error('Denied')};Storage.prototype.setItem=()=>{throw new Error('Denied')};")
    page=context.new_page();begin(page);learn(page,0);click(page,'parent-confirm');click(page,'adult-confirm');assert page.locator('.reward').count()==1;click(page,'continue');scene(page,'S04');context.close()
    for mode in ['muted','failed-audio']:
        context=browser.new_context();page=context.new_page();requests=[];page.on('request',lambda r:requests.append(r.url) if '.wav' in r.url else None)
        if mode=='failed-audio':page.route('**/*.wav',lambda route:route.abort())
        else:
            page.goto(url);ready(page);page.evaluate('localStorage.setItem("adventure.settings.sound","false")')
        begin(page);learn(page,0);solve(page);click(page,'continue');scene(page,'S04')
        if mode=='muted':assert requests==[]
        context.close()
    browser.close()
 print('PASS teach-first/review; ordinary and secret routes; 20/6 checks; recoverable errors; persistent leaf drag; optional leaf; code changes; three print pages; separate answers; saves and storage denial; 390/820/1180; no font requests')
 (OUT/'results.json').write_text(json.dumps({'passed':True,'physicalTablet':False,'paperQuestions':20,'teachingCards':sum(map(len,DATA['learning']))}),encoding='utf-8')
finally:server.shutdown()
