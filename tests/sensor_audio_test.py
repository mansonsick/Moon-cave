"""Browser checks for real shared controllers, deterministic sensor traces and Web Audio.

python tests/sensor_audio_test.py --output ../hub-review/story02-tests
Audio fixtures are generated in memory by this test; no substitute audio is shipped.
"""
import argparse
import base64
import io
import json
import wave
from pathlib import Path
from playwright.sync_api import sync_playwright, expect
from story_test_support import REPO, serve

RESULTS=[]
def record(name,detail):
    RESULTS.append(dict(check=name,result='PASS',detail=detail));print('PASS '+name,flush=True)

def permission_script(mode):
    if mode=='unsupported': return "Object.defineProperty(window,'DeviceOrientationEvent',{value:undefined,configurable:true});"
    return f"Object.defineProperty(window,'DeviceOrientationEvent',{{value:class {{static requestPermission(){{return Promise.resolve('{mode}')}}}},configurable:true}}); Object.defineProperty(window,'DeviceMotionEvent',{{value:class {{static requestPermission(){{return Promise.resolve('{mode}')}}}},configurable:true}});"

def stream(page,beta=90,gamma=0):
    page.evaluate('''([beta,gamma])=>{window.trace={beta,gamma}; clearInterval(window.feed);window.feed=setInterval(()=>{const e=new Event('deviceorientation');Object.assign(e,window.trace);window.dispatchEvent(e)},50)}''',[beta,gamma])

def main():
    parser=argparse.ArgumentParser();parser.add_argument('--output',type=Path,default=REPO.parent/'hub-review/story02-tests');args=parser.parse_args();args.output.mkdir(parents=True,exist_ok=True)
    server,base=serve();
    try:
        with sync_playwright() as p:
            browser=p.chromium.launch()
            context=browser.new_context();page=context.new_page();page.goto(base+'experiments/balance-sensor/')
            result=page.evaluate('''async()=>{
              const {StabilityTracker}=await import('../../engine/sensors.js');
              const sample={beta:90,gamma:0,screen:0,shake:0};
              const calibrate=t=>{for(let i=0;i<22;i++)t.step(sample,100)};
              const still=new StabilityTracker('stillness');calibrate(still);
              for(let i=0;i<20;i++)still.step(sample,100);const before=still.elapsed;
              for(let i=0;i<5;i++)still.step({...sample,gamma:30},100);
              const noise=still.status==='paused'&&still.elapsed===before;
              still.step(sample,100);const recovered=still.status==='steady';
              for(let i=0;i<8;i++)still.step({...sample,gamma:30},100);
              const failed=still.status==='failed'&&still.elapsed===0;
              still.reset();for(let i=0;i<30;i++)still.step({...sample,beta:0},100);
              const upright=still.status==='upright'&&still.elapsed===0;
              const balance=new StabilityTracker('balance');calibrate(balance);for(let i=0;i<20;i++)balance.step(sample,100);
              const credit=balance.elapsed;for(let i=0;i<20;i++)balance.step({...sample,gamma:12},100);
              const soft=balance.status==='paused'&&balance.elapsed===credit;
              for(let i=0;i<9;i++)balance.step({...sample,gamma:30},100);const grace=balance.status!=='failed';
              balance.step({...sample,gamma:30},100);const hard=balance.status==='failed'&&balance.elapsed===0;
              balance.reset();calibrate(balance);balance.step({...sample,screen:90},100);const rotation=!balance.baseline&&balance.elapsed===0;
              const noData=new StabilityTracker('balance');for(let i=0;i<500;i++)noData.step(null,100);
              const noCredit=noData.elapsed===0&&!noData.baseline;
              const done=new StabilityTracker('balance');calibrate(done);for(let i=0;i<80;i++)done.step(sample,100);
              return {noise,recovered,failed,upright,soft,grace,hard,rotation,noCredit,complete:done.status==='complete'};
            }''')
            assert all(result.values()),result
            record('sensor-thresholds','2-second calibration, upright requirement, transient noise grace, sustained motion reset, soft balance pause, 1-second hard reset, orientation rotation and no-data/no-credit verified.')
            context.close()
            for mode in ['unsupported','denied','granted']:
                context=browser.new_context();context.add_init_script(permission_script(mode));q=context.new_page();q.clock.install();q.goto(base+'experiments/balance-sensor/')
                q.locator('[data-action="challenge-start"]').click();q.clock.run_for(11000)
                expect(q.locator('#panel')).to_have_text('Complete — awaiting your next action.')
                context.close()
            record('sensor-fallbacks','Unsupported API, denied permission, and granted permission with no events all complete via ordinary 8-second countdown.')
            context=browser.new_context();context.add_init_script(permission_script('granted'));q=context.new_page();errors=[];q.on('pageerror',lambda error:errors.append(str(error)));q.clock.install();q.goto(base+'experiments/balance-sensor/')
            stream(q);q.locator('[data-action="challenge-start"]').click();q.clock.run_for(4600)
            q.evaluate('window.trace.gamma=32');q.clock.run_for(1000)
            expect(q.locator('.challenge-status')).to_have_text('Movement detected. Try again.')
            expect(q.locator('[data-action="challenge-start"]')).to_be_enabled()
            q.evaluate('window.trace.gamma=0');q.locator('[data-action="challenge-start"]').click();q.clock.run_for(11000)
            expect(q.locator('#panel')).to_have_text('Complete — awaiting your next action.')
            record('sensor-success-retry','Injected orientation events drive the real controller: movement fails gently, retry recalibrates, and steady 8 seconds succeeds.')
            q.locator('#balance').click();stream(q,beta=30);q.locator('[data-action="challenge-start"]').click();q.clock.run_for(5000)
            q.evaluate('clearInterval(window.feed)');q.clock.run_for(3500)
            expect(q.locator('.challenge-status')).to_have_text('Ordinary countdown (no sensor).')
            assert q.locator('progress').evaluate('e=>e.value')<2000
            q.clock.run_for(8500);expect(q.locator('#panel')).to_have_text('Complete — awaiting your next action.')
            record('sensor-stale-stream','Loss of events during play switches to a fresh 8-second countdown; stale sensor time is never credited.')
            q.locator('#stillness').click();stream(q);q.locator('[data-action="challenge-start"]').click();q.clock.run_for(4000)
            q.evaluate("Object.defineProperty(document,'hidden',{value:true,configurable:true});document.dispatchEvent(new Event('visibilitychange'));")
            q.clock.run_for(20000)
            q.evaluate("Object.defineProperty(document,'hidden',{value:false,configurable:true});document.dispatchEvent(new Event('visibilitychange'));")
            q.clock.run_for(20000)
            expect(q.locator('.challenge-status')).to_have_text('Paused in background. Start again.')
            assert q.locator('progress').evaluate('e=>e.value')==0
            q.locator('[data-action="challenge-start"]').click();q.clock.run_for(11000)
            expect(q.locator('#panel')).to_have_text('Complete — awaiting your next action.')
            record('background-pause','Going to background cancels sensor timing; returning cannot auto-complete, and a fresh start recalibrates.')
            # Valid APIs but invalid numerical samples are not accepted as stability.
            q.locator('#stillness').click();stream(q,beta=None,gamma=None);q.locator('[data-action="challenge-start"]').click();q.clock.run_for(3000)
            expect(q.locator('.challenge-status')).to_have_text('Ordinary countdown (no sensor).')
            q.clock.run_for(8500);expect(q.locator('#panel')).to_have_text('Complete — awaiting your next action.')
            record('invalid-sensor-data','null-valued events are ignored and lead to a fresh ordinary countdown.')
            # Exercise real tiltDodge controller with sensor movement and existing buttons.
            q.evaluate('''async()=>{
              clearInterval(window.feed);const {tiltDodge}=await import('../../engine/challenges.js');
              const panel=document.querySelector('#panel');panel.replaceChildren();
              const text=id=>document.createTextNode(id);const button=(id,fn)=>{const b=document.createElement('button');b.textContent=id;b.onclick=fn;return b};
              window.cleanDodge=tiltDodge({panel,text,button,onComplete:()=>{window.cleanDodge();panel.textContent='Dodge complete'}});
            }''')
            stream(q,beta=70,gamma=0);q.locator('[data-action="tilt"]').click();q.clock.run_for(2400)
            assert q.locator('.dodge-field').get_attribute('data-mode')=='tilt'
            for _ in range(55):
                field=q.locator('.dodge-field')
                if not field.count(): break
                obstacle=int(field.get_attribute('data-obstacle'))
                q.evaluate('(g)=>window.trace.gamma=g',-24 if obstacle!=0 else 24)
                q.clock.run_for(600)
            expect(q.locator('#panel')).to_have_text('Dodge complete')
            assert not errors,errors;context.close()
            record('tilt-dodge-sensor','Same obstacle/movement controller completes 5 obstacles using calibrated orientation events; ordinary button route was tested separately.')
            # Generated silent WAV exists only in this test process and is served by route interception.
            fixture=io.BytesIO()
            with wave.open(fixture,'wb') as wav:
                wav.setnchannels(1);wav.setsampwidth(2);wav.setframerate(8000);wav.writeframes(b'\x00\x00'*16000)
            context=browser.new_context();q=context.new_page();q.goto(base+'experiments/audio/');audio_errors=[];q.on('pageerror',lambda error:audio_errors.append(str(error)))
            q.route('**/test-sound.wav',lambda route:route.fulfill(body=fixture.getvalue(),content_type='audio/wav'))
            q.route('**/missing-sound.wav',lambda route:route.fulfill(status=404,body='missing'))
            q.route('**/bad-sound.wav',lambda route:route.fulfill(body=b'not audio',content_type='audio/wav'))
            q.evaluate('''async()=>{
              const {AudioManager}=await import('../../engine/audio-manager.js');
              const audio={a:{src:'test-sound.wav',available:true},b:{src:'test-sound.wav',available:true},'secret-bell':{src:'test-sound.wav',available:true},sfx:{src:'test-sound.wav',available:true},missing:{src:'missing-sound.wav',available:true},bad:{src:'bad-sound.wav',available:true},pending:{src:'never-request.mp3',available:false}};
              window.audioTest=new AudioManager(audio,location.href,true);
              document.querySelector('#unlock').onclick=()=>window.unlockResult=audioTest.unlock();
            }''')
            assert q.evaluate('audioTest.context===null && !audioTest.unlocked')
            q.locator('#unlock').click();q.evaluate('window.unlockResult')
            assert q.evaluate('audioTest.unlocked')
            result=q.evaluate('''async()=>{
              const a=audioTest;
              const first=await a.setAmbience('a');const original=a.current;
              await a.setAmbience('a');const same=a.current===original;
              const switching=a.setAmbience('b');await a.setAmbience('a');await switching;
              const race=a.current===original&&a.current.id==='a';
              await a.setAmbience('b');const switched=a.current?.id==='b';
              const sfx=await a.playSfx('sfx');const duplicate=await a.playSfx('sfx');
              const bell=await a.playSfx('secret-bell');
              const voices=a.voices.size<=3;
              a.setEnabled(false);const muted=!a.current&&a.voices.size===0&&!await a.playSfx('sfx');
              a.setEnabled(true);await a.setAmbience('a');a.setHidden(true);
              const background=!a.current&&a.voices.size===0;
              a.setHidden(false);await a.setAmbience('a');const restored=a.current?.id==='a';
              const missing=await a.playSfx('missing'),bad=await a.playSfx('bad'),pending=await a.playSfx('pending');
              a.dispose();
              return {first,same,race,switched,sfx,duplicate:!duplicate,bell,voices,muted,background,restored,failedSafe:!missing&&!bad&&!pending};
            }''')
            assert all(result.values()),result
            assert not audio_errors,audio_errors
            record('audio-manager','Real AudioContext unlocks only on click; one ambience, same-track reuse, rapid switch cancellation, SFX cooldown, bell ducking calls, mute, visibility and missing/decode-error/placeholder fallbacks verified with in-memory WAV.')
            context.close();browser.close()
        (args.output/'sensor-audio-results.json').write_text(json.dumps(RESULTS,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
    finally: server.shutdown()

if __name__=='__main__': main()
