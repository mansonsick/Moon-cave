"""Regression checks for automatic audio, clear cards, celebrations and optional review."""
import json
from playwright.sync_api import sync_playwright
from story_test_support import serve, remember_family_entry, REPO
from story_06_test import KEY, OUT, click, state, scene, tap, images

REVIEW = 'adventure.story-06.review.state'

def seed(page, g=0, progress=0, size=1, scene_id=None):
    page.evaluate('''async ({g,progress,size,sceneId,key})=>{
      const {freshState,QUIZ}=await import('./state.js');const s=freshState();
      s.started=true;s.lamp=true;s.size=size;s.scene=sceneId||QUIZ[g];
      for(let j=0;j<=g;j++){
        s.learned[j]=[...s.roundSymbols[j]];s.progress[j]=j<g?6:progress;
        s.results[j]=s.roundSymbols[j].slice(0,s.progress[j]).map(symbol=>({symbol,mode:'independent'}));
      }
      localStorage.setItem(key,JSON.stringify(s));
    }''', dict(g=g,progress=progress,size=size,sceneId=scene_id,key=KEY))
    page.reload();click(page,'resume')
    scene(page,scene_id or ['S04','S06','S09'][g])

def read_review(page):
    return page.evaluate('(k)=>JSON.parse(localStorage.getItem(k))',REVIEW)

def main():
    server,base=serve();errors=[];failures=[];geometry=[];checks=[]
    try:
        with sync_playwright() as p:
            browser=p.chromium.launch()
            ctx=browser.new_context(viewport={'width':768,'height':1024},has_touch=True)
            remember_family_entry(ctx)
            # Test-only reference to the actual runtime; production exposes no global story.
            source=(REPO/'stories/story-06/app.js').read_text(encoding='utf-8')
            ctx.route('**/story-06/app.js',lambda r:r.fulfill(body=source.replace('new ForestStory(document.querySelector', 'window.__forest=new ForestStory(document.querySelector'),content_type='text/javascript'))
            page=ctx.new_page();page.on('pageerror',lambda e:errors.append(str(e)))
            page.on('response',lambda r:failures.append(r.url) if r.status>=400 else None)
            page.goto(base+'stories/story-06/');page.wait_for_selector('[data-action="start"]')
            # Stage zero-progress must select its own loop even after completed earlier stages.
            for g,id in enumerate(['cricket-song','stream-song','bird-song']):
                seed(page,g)
                page.wait_for_function('(id)=>window.__forest.audio.current?.id===id',arg=id,timeout=8000)
                assert page.locator('.stage').get_attribute('data-ambience')==id
                assert not page.locator('.answer-field').is_visible()
                assert state(page)['progress'][g]==0
            checks.append('Three first-question scenes play their own ambience before any answer')

            seed(page);draw=state(page)['roundSymbols'];click(page,'begin-question')
            assert not page.locator('.answer-field').is_visible()
            page.wait_for_selector('.answer-field:not([hidden])',timeout=8000)
            tap(page,f'.answer-card[data-symbol="{draw[0][0]}"]');click(page,'next-question')
            assert not page.locator('.answer-field').is_visible()
            page.wait_for_selector('.answer-field:not([hidden])',timeout=8000)
            assert state(page)['progress']==[1,0,0] and state(page)['roundSymbols']==draw
            tap(page,f'.answer-card[data-symbol="{draw[0][1]}"]')
            assert state(page)['results'][0][1]['mode']=='independent'
            checks.append('Next sound automatically plays; choices stay hidden until real voice ended')

            # Completion is a one-shot actual decoded audio source, with no ambience loop.
            seed(page,0,5);click(page,'assist');target=state(page)['roundSymbols'][0][5]
            tap(page,f'.answer-card[data-symbol="{target}"]')
            page.wait_for_function("Array.from(window.__forest.audio.voices).some(v=>v.id==='forest-celebration')",timeout=8000)
            assert page.locator('[role="dialog"]').is_visible()
            assert page.evaluate('window.__forest.audio.current===null&&window.__forest.audio.desired===null')
            page.wait_for_timeout(400);assert page.locator('[role="dialog"]').is_visible()
            click(page,'continue');scene(page,'S05')
            page.wait_for_function("window.__forest.audio.current?.id==='stream-song'",timeout=8000)
            assert page.evaluate("!Array.from(window.__forest.audio.voices).some(v=>v.id==='forest-celebration')")
            seed(page,2,6,scene_id='S10');click(page,'next');scene(page,'E01')
            page.wait_for_function("Array.from(window.__forest.audio.voices).some(v=>v.id==='forest-celebration')",timeout=8000)
            assert page.evaluate('window.__forest.audio.current===null&&window.__forest.audio.background===null')
            click(page,'sound');assert page.evaluate('window.__forest.audio.voices.size===0')
            click(page,'replay-song');page.wait_for_timeout(200)
            assert page.evaluate('window.__forest.audio.voices.size===0')
            checks.append('Stage and ending completion melody, explicit continue, leave/mute cancellation')

            # Wrong targets persist separately; chosen distractors are recorded as confusion only.
            seed(page);click(page,'assist');target=state(page)['roundSymbols'][0][0]
            bad=next(s for s in page.locator('.answer-card').evaluate_all('ns=>ns.map(n=>n.dataset.symbol)') if s!=target)
            for _ in range(2):tap(page,f'.answer-card[data-symbol="{bad}"]')
            review=read_review(page);assert review['symbols'][target]=={'errors':2,'confusions':{bad:2}}
            assert bad not in review['symbols'] and state(page)['progress'][0]==0
            tap(page,f'.answer-card[data-symbol="{target}"]');page.reload();click(page,'resume')
            assert read_review(page)==review and state(page)['progress'][0]==1
            click(page,'menu');click(page,'replay');click(page,'new-adventure')
            assert read_review(page)==review and state(page)['progress']==[0,0,0]
            click(page,'menu');click(page,'mistakes')
            assert page.locator(f'[data-review-target="{target}"]').count()==1
            assert page.locator(f'[data-review-symbol="{bad}"]').count()==1
            # Sound was muted above; turn it on after closing, then hear actual target recording.
            click(page,'close');click(page,'sound');click(page,'mistakes')
            page.locator(f'[data-review-symbol="{target}"]').click()
            page.wait_for_function("document.querySelector('.review-status .bpmf')?.getAttribute('aria-label')==='聲音試聽完成。'",timeout=8000)
            before=page.evaluate('(k)=>localStorage.getItem(k)',KEY)
            click(page,'clear-review');click(page,'cancel');assert read_review(page)==review
            page.evaluate("localStorage.setItem('moonCaveSave','old-save');localStorage.setItem('adventure.story-02.state','story02-save')")
            click(page,'clear-review');click(page,'clear-review-yes')
            assert read_review(page)=={'schemaVersion':1,'symbols':{}}
            assert page.evaluate('(k)=>localStorage.getItem(k)',KEY)==before
            assert page.evaluate("localStorage.getItem('moonCaveSave')==='old-save'&&localStorage.getItem('adventure.story-02.state')==='story02-save'")
            checks.append('Wrong target/confusion counts, review replay, persistence across refresh/new draw, clear isolation')

            # Corrupted optional review cannot destroy a valid current adventure.
            click(page,'close');seed(page,1,2);draw=state(page)['roundSymbols']
            page.evaluate('(k)=>localStorage.setItem(k,"broken")',REVIEW);page.reload();click(page,'resume')
            assert state(page)['roundSymbols']==draw and state(page)['progress']==[6,2,0]
            click(page,'settings');click(page,'mistakes');assert page.locator('.review-entry').count()==0;click(page,'close')
            checks.append('Damaged optional review leaves saved adventure intact')

            # Sample moving cards in the lower safe area, including maximum text scale.
            for width in [320,390,768,1180]:
                page.set_viewport_size({'width':width,'height':1024})
                for size in [1,1.45]:
                    for g in range(3):
                        seed(page,g,size=size);click(page,'assist');images(page)
                        page.locator('.answer-field').evaluate("n=>n.scrollIntoView({block:'center',behavior:'instant'})")
                        for _ in range(4):
                            result=page.evaluate('''()=>{
                              const rect=n=>{const r=n.getBoundingClientRect();return {left:r.left,right:r.right,top:r.top,bottom:r.bottom,width:r.width,height:r.height}};
                              const field=rect(document.querySelector('.answer-field')),badge=rect(document.querySelector('.quiz-badge')),stage=rect(document.querySelector('.stage'));
                              const cards=Array.from(document.querySelectorAll('.answer-card'),n=>{const r=rect(n);return {...r,uncovered:document.elementFromPoint((r.left+r.right)/2,(r.top+r.bottom)/2)?.closest('.answer-card')===n}});
                              return {field,badge,stage,cards,docked:document.querySelector('.quiz-badge').classList.contains('docked'),overflow:document.documentElement.scrollWidth>innerWidth};
                            }''')
                            f=result['field'];b=result['badge'];s=result['stage']
                            assert b['bottom']+10<=f['top'],(width,size,g,result)
                            assert f['top']>=s['top']+s['height']*.37 and f['bottom']<=s['bottom'],(width,size,g,result)
                            for c in result['cards']:
                                assert c['width']>=47.9 and c['height']>=47.9 and c['uncovered'],(width,size,g,result)
                                assert c['left']>=f['left']-1 and c['right']<=f['right']+1 and c['top']>=f['top']-1 and c['bottom']<=f['bottom']+1,(width,size,g,result)
                            assert not result['overflow'];page.wait_for_timeout(70)
                        geometry.append(dict(width=width,size=size,group=g,docked=result['docked']))
                        if (width,size,g) in [(390,1,1),(768,1,2),(320,1.45,2)]:
                            page.screenshot(path=str(OUT/f'clear-cards-{width}-{size}-{g}.png'),full_page=True)
            checks.append('24 viewport/font/stage combinations: moving cards below prompt, within field, uncovered and at least 48px')
            assert not errors,errors;assert not failures,failures
            (OUT/'feedback-results.json').write_text(json.dumps(dict(checks=checks,geometry=geometry,pageErrors=errors,httpErrors=failures),ensure_ascii=False,indent=2),encoding='utf-8')
            browser.close();print('PASS:', '; '.join(checks))
    finally:server.shutdown()

if __name__=='__main__':main()
