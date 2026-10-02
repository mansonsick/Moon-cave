"""Human audio credits/review, cache versioning and distinct A/I decoded content."""
from playwright.sync_api import sync_playwright
from story_test_support import serve

server,base=serve()
try:
    with sync_playwright() as p:
        browser=p.chromium.launch();page=browser.new_page();errors=[];bad=[]
        page.on('pageerror',lambda e:errors.append(str(e)))
        page.on('response',lambda r:bad.append(r.url) if r.status>=400 else None)
        page.goto(base+'stories/story-05/assets/audio/letters/review.html');page.wait_for_selector('article:nth-child(26)')
        assert page.locator('article h2').all_text_contents()==[c+' '+c.lower() for c in 'ABCDEFGHIJKLMNOPQRSTUVWXYZ']
        assert page.locator('article small a').count()==52
        page.locator('h1').click();page.locator('audio').nth(0).evaluate('a=>a.play()')
        page.wait_for_function('!document.querySelectorAll("audio")[0].paused')
        page.locator('audio').nth(8).evaluate('a=>a.play()')
        page.wait_for_function('document.querySelectorAll("audio")[0].paused&&!document.querySelectorAll("audio")[8].paused')
        page.locator('audio').nth(8).evaluate('a=>a.pause()')
        page.locator('.back').click();page.wait_for_selector('[data-action="start"]')
        audit=page.evaluate('''async()=>{
          const {AlphabetAudio}=await import('./alphabet-audio.js');const manifest=await fetch('./assets/audio/manifest.json').then(r=>r.json());
          const a=new AlphabetAudio(manifest.entries,new URL('./assets/audio/',location.href),true);await a.unlock();
          const A=await a.buffer('letter-A'),I=await a.buffer('letter-I');const av=A.getChannelData(0),iv=I.getChannelData(0);
          const distinct=av.length!==iv.length||av.some((v,i)=>v!==iv[i]);
          const mapped=[...'ABCDEFGHIJKLMNOPQRSTUVWXYZ'].every(c=>a.manifest['letter-'+c].letter===c&&
            a.manifest['letter-'+c].src==='letters/'+c.toLowerCase()+'.wav?v='+manifest.entries['letter-'+c].sha256.slice(0,12));
          a.dispose();return {distinct,mapped};
        }''')
        assert audit=={'distinct':True,'mapped':True} and not errors and not bad,(audit,errors,bad)
        browser.close();print('PASS 26 credited letter-name players, one active voice, A/I distinct decoded PCM, all runtime IDs/cache versions matched')
finally:server.shutdown()
