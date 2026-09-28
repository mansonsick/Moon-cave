"""Verify delivered audio, audible Web Audio graph, and actual story sound events."""
import argparse
import hashlib
import json
import wave
from pathlib import Path
import numpy as np
from playwright.sync_api import sync_playwright, expect
from story_test_support import REPO, serve

RESULTS=[]
def record(name,detail):
    RESULTS.append(dict(check=name,result='PASS',detail=detail));print('PASS '+name,flush=True)

def observe_audio(page):
    page.evaluate('''async()=>{
      const {AudioManager}=await import('/Moon-cave/engine/audio-manager.js?v=story02-audio-1');
      window.audioLog=[];const unlock=AudioManager.prototype.unlock,play=AudioManager.prototype.playSfx;
      AudioManager.prototype.unlock=function(...args){window.activeAudio=this;return unlock.apply(this,args)};
      AudioManager.prototype.playSfx=function(id){return play.call(this,id).then(result=>{audioLog.push({id,result});return result})};
    }''')

def main():
    parser=argparse.ArgumentParser();parser.add_argument('--output',type=Path,default=REPO.parent/'hub-review/story02-audio-tests');args=parser.parse_args();args.output.mkdir(parents=True,exist_ok=True)
    story=REPO/'stories/story-02';manifest=json.loads((story/'assets/audio/manifest.json').read_text(encoding='utf-8'))
    config=json.loads((story/'story.json').read_text(encoding='utf-8'))
    assert len(manifest['assets'])==9 and sum(e['category']=='ambience' for e in manifest['assets'])==4
    for entry in manifest['assets']:
        path=story/'assets/audio'/entry['file'];settings=config['audio'][entry['id']]
        assert settings['available'] and settings['src']=='assets/audio/'+entry['file']
        assert hashlib.sha256(path.read_bytes()).hexdigest()==entry['sha256']
        with wave.open(str(path),'rb') as wav:
            assert wav.getnchannels()==1 and wav.getsampwidth()==2 and wav.getframerate()==22050
            samples=np.frombuffer(wav.readframes(wav.getnframes()),dtype='<i2').astype(float)/32768
        assert .001<float(np.sqrt(np.mean(samples*samples)))<.3
        assert float(np.max(np.abs(samples)))<=.551
        assert samples[0]==0 and samples[-1]==0
        assert entry['seconds']>=20 if entry['category']=='ambience' else .2<=entry['seconds']<=4
    assert sum(e['bytes'] for e in manifest['assets'])<5_000_000
    record('delivered-wavs','All 9 WAV paths/hashes match; PCM16 mono 22.05kHz; non-silent, bounded peaks, zero-ended envelopes; 20s ambience loops; 3.80 MB total.')
    server,base=serve()
    try:
        with sync_playwright() as p:
            browser=p.chromium.launch();context=browser.new_context();q=context.new_page();errors=[];bad=[];requests=[]
            q.on('pageerror',lambda error:errors.append(str(error)))
            q.on('response',lambda response:bad.append(response.url) if response.status>=400 else None)
            q.on('request',lambda request:requests.append(request.url) if '.wav' in request.url else None)
            q.goto(base+'experiments/audio/');q.wait_for_selector('#controls button')
            q.evaluate('''async()=>{
              const {AudioManager}=await import('../../engine/audio-manager.js');const config=await(await fetch('../../stories/story-02/story.json')).json();
              window.a=new AudioManager(config.audio,new URL('../../stories/story-02/',location.href));a.setAmbience('forest-evening');
              document.querySelector('#unlock').onclick=()=>window.started=a.unlock();
            }''')
            assert q.evaluate('a.context===null && !a.unlocked') and not requests
            q.locator('#unlock').click();q.evaluate('window.started')
            assert q.evaluate('a.unlocked')
            decoded=q.evaluate('''async()=>{const result=[];for(const id of Object.keys(a.manifest)){const b=await a.buffer(id);result.push({id,duration:b?.duration||0})}return result}''')
            assert len(decoded)==9 and all(r['duration']>0 for r in decoded)
            q.evaluate("a.setAmbience('forest-evening')")
            q.evaluate('''()=>{window.meter=a.context.createAnalyser();meter.fftSize=2048;a.current.gain.connect(meter)}''')
            q.wait_for_function('''()=>{const samples=new Float32Array(meter.fftSize);meter.getFloatTimeDomainData(samples);return samples.some(v=>Math.abs(v)>.0001)}''')
            record('real-audio-output','No context/request before Start; gesture unlocks; all 9 delivered files decode; analyser confirms a non-zero output waveform.')
            q.evaluate("a.setAmbience('creepy-house',.5)");q.wait_for_timeout(700)
            level=q.evaluate('a.current.gain.gain.value');assert .10<level<.15,level
            q.evaluate('a.setHidden(true)');assert q.evaluate('a.current===null && a.voices.size===0')
            q.evaluate('a.setHidden(false)');q.wait_for_function("a.current?.id==='creepy-house'");q.wait_for_timeout(700)
            assert abs(q.evaluate('a.current.gain.gain.value')-.12)<.02
            q.evaluate('a.setEnabled(false)');assert q.evaluate('a.current===null && a.voices.size===0')
            record('levels-mute-and-resume','Hiding scene uses half ambience gain; foreground resume preserves level; mute and background stop sound.')
            # Delayed SFX must be cancelled by scene exit, while an explicitly carried bell survives.
            result=q.evaluate('''async()=>{
              a.setEnabled(true);await a.setAmbience('temple-night');
              const original=a.buffer.bind(a),buffer=await original('secret-bell');let release;
              a.buffer=id=>id==='secret-bell'?new Promise(resolve=>release=()=>resolve(buffer)):original(id);
              const pending=a.playSfx('secret-bell');a.stopSfx();release();const cancelled=!await pending;
              a.lastSfx.clear();const carried=a.playSfx('secret-bell');a.stopSfx(['secret-bell']);await a.setAmbience('temple-night');release();const kept=await carried;
              const voice=[...a.voices].find(v=>v.id==='secret-bell');a.stopSfx(['secret-bell']);await a.setAmbience('temple-night');
              const same=a.voices.has(voice);a.stopSfx();a.buffer=original;return {cancelled,kept,same};
            }''')
            assert all(result.values()),result
            record('pending-and-carried-sfx','Leaving cancels delayed cues; the bell may survive an immediate transition without duplicate playback; ambient switching does not invalidate it.')
            q.evaluate('a.dispose()');context.close()

            context=browser.new_context(viewport={'width':820,'height':1180},has_touch=True)
            context.add_init_script("window.audioContexts=0;const Native=window.AudioContext;window.AudioContext=class extends Native{constructor(...args){super(...args);window.audioContexts++}};")
            page=context.new_page();page.on('pageerror',lambda error:errors.append(str(error)))
            page.on('response',lambda response:bad.append(response.url) if response.status>=400 else None)
            url=base+'stories/story-02/';page.goto(url);page.wait_for_selector('[data-action="start-adventure"]')
            assert page.evaluate('window.audioContexts')==0
            checkpoint=dict(version=1,scene='clues',clues=['prints','fur'],inventory=[],completed=[],placed=[],ending=None,textScale=1)
            page.evaluate('(s)=>localStorage.setItem("adventure.story-02.state",JSON.stringify(s))',checkpoint)
            page.reload();page.wait_for_selector('[data-action="start-adventure"]');observe_audio(page)
            page.locator('[data-action="start-adventure"]').click();page.wait_for_function('activeAudio?.unlocked')
            page.locator('[data-target="tail"]').click();page.wait_for_function("audioLog.some(e=>e.id==='success'&&e.result)")
            page.locator('[data-action="continue"]').click();page.locator('[data-target="key"]').click()
            page.wait_for_function("audioLog.some(e=>e.id==='found-item'&&e.result)")
            record('actual-discovery-cues','The third clue plays success; picking up the key plays found-item using the real game callbacks and real audio files.')

            checkpoint.update(scene='temple',clues=['prints','fur','tail'],inventory=['key','bell'],completed=['hide','bamboo','bridge'])
            page.evaluate('(s)=>localStorage.setItem("adventure.story-02.state",JSON.stringify(s))',checkpoint)
            page.reload();page.wait_for_selector('[data-action="start-adventure"]');observe_audio(page);page.locator('[data-action="start-adventure"]').click()
            page.wait_for_function('activeAudio?.unlocked');page.evaluate("activeAudio.buffer('secret-bell')")
            assert page.evaluate("audioLog.every(e=>e.id!=='secret-bell')")
            source=page.locator('[data-item="bell"]');source.scroll_into_view_if_needed();a=source.bounding_box();b=page.locator('.bell-hook').bounding_box()
            page.mouse.move(a['x']+a['width']/2,a['y']+a['height']/2);page.mouse.down();page.mouse.move(b['x']+b['width']/2,b['y']+b['height']/2,steps=8);page.mouse.up()
            page.wait_for_function("audioLog.some(e=>e.id==='secret-bell'&&e.result)&&audioLog.some(e=>e.id==='drag-lock'&&e.result)")
            page.evaluate("window.bellVoice=[...activeAudio.voices].find(v=>v.id==='secret-bell')")
            page.locator('[data-action="continue"]').click();expect(page.locator('#story')).to_have_attribute('data-scene','secret')
            assert page.evaluate("activeAudio.voices.has(bellVoice) && audioLog.filter(e=>e.id==='secret-bell'&&e.result).length===1")
            page.wait_for_function("activeAudio.current?.id==='temple-night'");page.wait_for_timeout(350)
            assert page.evaluate('activeAudio.current.gain.gain.value')<.11
            page.locator('[data-action="sound"]').click();assert page.evaluate('activeAudio.current===null && activeAudio.voices.size===0')
            page.reload();page.wait_for_selector('[data-action="start-adventure"]');page.locator('[data-action="start-adventure"]').click()
            assert page.evaluate('window.audioContexts')==0
            record('secret-bell-and-saved-mute','No bell before dragging; drag-lock and secret-bell fire once; Continue preserves ringing/ducking into divine ending; mute stops it and reload respects saved silence.')
            checkpoint.update(scene='temple',placed=[])
            page.evaluate('(s)=>{localStorage.setItem("adventure.story-02.state",JSON.stringify(s));localStorage.setItem("adventure.settings.sound","true")}',checkpoint)
            page.reload();page.wait_for_selector('[data-action="start-adventure"]');observe_audio(page);page.locator('[data-action="start-adventure"]').click();page.wait_for_function('activeAudio?.unlocked')
            page.locator('[data-action="wait"]').click();expect(page.locator('#story')).to_have_attribute('data-scene','ordinary')
            page.wait_for_function("audioLog.some(e=>e.id==='success'&&e.result)");page.wait_for_timeout(650)
            assert page.evaluate('activeAudio.current===null')
            record('ordinary-ending','Normal ending has a success cue and fades out ambience; carrying an unused bell triggers no secret sound.')
            assert not errors,errors;assert not bad,bad
            browser.close()
        (args.output/'results.json').write_text(json.dumps(RESULTS,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
    finally:server.shutdown()

if __name__=='__main__':main()
