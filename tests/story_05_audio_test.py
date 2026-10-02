"""Human audio credits/review, cache versioning and distinct A/I decoded content."""
from playwright.sync_api import sync_playwright
from story_test_support import serve, remember_family_entry

server,base=serve()
try:
    with sync_playwright() as p:
        browser=p.chromium.launch();context=browser.new_context();remember_family_entry(context);page=context.new_page();errors=[];bad=[]
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
        music=page.evaluate('''async()=>{
          const {AlphabetAudio}=await import('./alphabet-audio.js');const manifest=await fetch('./assets/audio/manifest.json').then(r=>r.json());
          const a=new AlphabetAudio(manifest.entries,new URL('./assets/audio/',location.href),true);await a.unlock();
          const b=await a.buffer('come-play-with-me');a.sceneAmbience('come-play-with-me');
          await new Promise(r=>setTimeout(r,150));const source=a.current.source;a.sceneAmbience('come-play-with-me');
          const single=a.current.source===source;const normal=a.ambienceLevel();
          const voice=a.letter('A');await new Promise(r=>setTimeout(r,300));const duck=a.ambienceLevel();await voice;
          const restored=Math.abs(a.ambienceLevel()-normal)<.001;
          a.sceneAmbience(null);a.cancelLetter();a.setEnabled(false);a.setEnabled(true);await a.unlock();a.setHidden(true);a.setHidden(false);
          await new Promise(r=>setTimeout(r,600));const stopped=!a.current&&!a.desired&&!a.background;a.dispose();
          return {seconds:b.duration,single,normal,duck,restored,stopped};
        }''')
        assert 131<music['seconds']<133 and music['single'] and music['restored'] and music['stopped'],music
        assert abs(music['normal']-.12)<.001 and abs(music['duck']-.0144)<.001,music
        # Safe scenes remain quiet even when the user turns sound back on.
        for scene in ['H03','E01','E02']:
          page.evaluate('''async scene=>{const {freshState}=await import('./state.js');const s=freshState();s.scene=scene;s.stage=2;s.gem=true;s.round=5;s.completed=s.orders.map(x=>x.slice());localStorage.setItem('adventure.story-05.state',JSON.stringify(s));localStorage.setItem('adventure.settings.sound','true');}''',scene)
          loops=[];page.add_init_script('''const original=AudioBufferSourceNode.prototype.start;AudioBufferSourceNode.prototype.start=function(...args){if(this.loop)window.__startedLoops=(window.__startedLoops||0)+1;return original.apply(this,args)};window.__startedLoops=0;''')
          page.reload();page.locator('[data-action="resume"]').click();page.wait_for_timeout(650)
          page.locator('[data-action="sound"]').click();page.locator('[data-action="sound"]').click();page.wait_for_timeout(650)
          assert page.evaluate('window.__startedLoops')==0,scene
        browser.close();print('PASS 26 letter players/credits/mapping, A/I distinct PCM; supplied 132s MP3 decodes, one loop, low volume/voice ducking, safe endings stop and stay quiet')
finally:server.shutdown()
