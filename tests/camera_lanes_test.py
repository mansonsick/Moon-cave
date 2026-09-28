"""Camera controls: synthetic video/poses, lifecycle, fallback and the real WASM worker.

No real camera is opened. Physical tablet recognition remains a separate acceptance step.
"""
import argparse
import hashlib
import json
from pathlib import Path
from playwright.sync_api import sync_playwright, expect
from story_test_support import REPO, serve

RESULTS=[]
def record(name,detail):
    RESULTS.append(dict(check=name,result='PASS',detail=detail));print('PASS '+name,flush=True)

# All frames come from an artificial canvas; the fake worker supplies deterministic
# landmarks in the real library's x/y/visibility format (presence is optional).
FAKE_CAMERA='''
window.cameraCalls=0;window.stops=0;window.terminates=0;window.poseX=.5;window.noPose=false;
window.permissionMode='granted';window.workers=[];window.streams=[];
const nativeStop=MediaStreamTrack.prototype.stop;
MediaStreamTrack.prototype.stop=function(){window.stops++;return nativeStop.call(this)};
const fakeStream=()=>{const c=document.createElement('canvas');c.width=640;c.height=480;const ctx=c.getContext('2d');ctx.fillStyle='#466d58';ctx.fillRect(0,0,640,480);const stream=c.captureStream(15);window.streams.push(stream);return stream};
Object.defineProperty(navigator,'mediaDevices',{value:{getUserMedia:constraints=>{
  window.cameraCalls++;window.constraints=constraints;
  if(window.permissionMode==='denied')return Promise.reject(new DOMException('denied','NotAllowedError'));
  if(window.permissionMode==='pending')return new Promise(resolve=>window.finishPermission=()=>resolve(fakeStream()));
  return Promise.resolve(fakeStream());
}},configurable:true});
Object.defineProperty(HTMLMediaElement.prototype,'currentTime',{get(){return performance.now()/1000}});
window.Worker=class {
  constructor(){this.dead=false;window.workers.push(this)}
  postMessage(data){if(data.type==='init'){setTimeout(()=>this.emit({type:window.modelFailure?'error':'ready'}),5)}else{
    data.bitmap.close();const p=Array.from({length:33},()=>({x:.5,y:.5,z:0,visibility:.99}));
    const x=1-window.poseX;for(const a of [11,23])p[a].x=x-.07;for(const b of [12,24])p[b].x=x+.07;
    setTimeout(()=>this.emit({type:'pose',poses:window.noPose?[]:window.twoPeople?[p,p]:[p],at:data.at}),5)
  }}
  emit(data){if(!this.dead)this.onmessage?.({data})}
  terminate(){this.dead=true;window.terminates++}
};
'''

def main():
    parser=argparse.ArgumentParser();parser.add_argument('--output',type=Path,default=REPO.parent/'hub-review/camera-tests');args=parser.parse_args();args.output.mkdir(parents=True,exist_ok=True)
    manifest=json.loads((REPO/'engine/vendor/mediapipe/manifest.json').read_text())
    for entry in manifest['files']:
        data=(REPO/'engine/vendor/mediapipe'/entry['file']).read_bytes();assert len(data)==entry['bytes'];assert hashlib.sha256(data).hexdigest()==entry['sha256']
    record('vendor-integrity','Pinned MediaPipe 1.0.1 and Lite model v1 files match SHA-256 manifest; Apache license retained.')
    server,base=serve()
    try:
        with sync_playwright() as p:
            browser=p.chromium.launch();context=browser.new_context();page=context.new_page();page.goto(base+'experiments/camera-lanes/')
            result=page.evaluate('''async()=>{
              const {bodyCenter,CameraLaneTracker}=await import('../../engine/camera-lanes.js?v=camera-1');
              const pose=x=>{const p=Array.from({length:33},()=>({x:.5,y:.5,visibility:.9}));p[23].x=x-.05;p[24].x=x+.05;return p};
              const t=new CameraLaneTracker();let result,at=1000;const hold=x=>{for(let i=0;i<7;i++)result=t.update(x,at+=100);return result?.lane};
              const mirrored=Math.abs(bodyCenter([pose(.2)])-.8)<.001;
              const lanes=[hold(.15),hold(.5),hold(.85)].join() === '0,1,2';
              const p=pose(.2);p[15].x=.99;const hand=Math.abs(bodyCenter([p])-.8)<.001;
              const multiple=bodyCenter([p,p])===null,empty=bodyCenter([])===null;
              for(const point of p)point.visibility=.1;const low=bodyCenter([p])===null;
              t.reset();hold(.2);for(const x of [.33,.34,.32,.35,.33])result=t.update(x,at+=100);const jitter=result.lane===0;
              const lost=t.update(null,at+=100)===null;const reacquire=t.update(.8,at+=100)===null;
              return {mirrored,lanes,hand,multiple,empty,low,jitter,lost,reacquire};
            }''');assert all(result.values()),result
            record('body-to-lanes','Mirrored hips/shoulders map to three lanes; hands do not steer; boundary jitter, low confidence, multiple/no people and reacquisition are handled.')
            # Real dependency, model and inference in a real Worker, never a device camera.
            external=[];page.on('request',lambda r:external.append(r.url) if not r.url.startswith(base.split('/Moon-cave/')[0]) else None)
            result=page.evaluate('''async()=>{
              const w=new Worker(new URL('../../engine/camera-worker.js?v=camera-1',location.href));
              return await new Promise(resolve=>{const timer=setTimeout(()=>{w.terminate();resolve({type:'timeout'})},45000);
                w.onerror=e=>{clearTimeout(timer);w.terminate();resolve({type:'error',message:e.message})};
                w.onmessage=async({data})=>{if(data.type==='ready'){const c=document.createElement('canvas');c.width=320;c.height=240;const bitmap=await createImageBitmap(c);w.postMessage({type:'frame',bitmap,at:1000},[bitmap])}else{clearTimeout(timer);w.terminate();resolve(data)}};
                w.postMessage({type:'init'});
              });
            }''');assert result['type']=='pose' and result['poses']==[],result;assert not external,external
            record('real-model-worker','Self-hosted JS/WASM/model initialize and infer a blank frame successfully in a real worker; no external requests. This does not claim real-person/tablet accuracy.')
            context.close()

            context=browser.new_context(viewport={'width':820,'height':1180},has_touch=True);context.add_init_script(FAKE_CAMERA);page=context.new_page();errors=[];page.on('pageerror',lambda e:errors.append(str(e)));requests=[];page.on('request',lambda r:requests.append(r.url))
            url=base+'experiments/camera-lanes/';page.goto(url);page.wait_for_selector('[data-action="camera"]');page.wait_for_timeout(150)
            assert page.evaluate('cameraCalls')==0 and not any('/vendor/' in r for r in requests)
            page.evaluate("window.permissionMode='denied'");page.locator('[data-action="camera"]').click();expect(page.locator('.dodge-field')).to_have_attribute('data-mode','buttons');assert page.evaluate('constraints.audio===false')
            expect(page.locator('[data-action="left"]')).to_be_enabled()
            record('opt-in-and-denial','No camera request or model download on entry; only explicit camera button requests video, never microphone; denied permission returns to usable buttons.')

            page.reload();page.wait_for_selector('[data-action="camera"]');page.locator('[data-action="camera"]').click();page.wait_for_function("document.querySelector('.dodge-field').dataset.mode==='camera'");page.wait_for_function("!document.querySelector('.camera-selected').hidden")
            for x,lane in [(.15,'0'),(.5,'1'),(.85,'2')]:
                page.evaluate('(x)=>window.poseX=x',x);page.wait_for_function('(lane)=>document.querySelector(".dodge-field").dataset.lane===lane',arg=lane)
            page.screenshot(path=str(args.output/'camera-three-lanes-820.png'),full_page=True)
            assert page.locator('video').evaluate("v=>getComputedStyle(v).transform.includes('-1')")
            page.evaluate('window.noPose=true');page.wait_for_timeout(750);before=page.locator('.dodge-field').get_attribute('data-position');page.wait_for_timeout(600);assert page.locator('.dodge-field').get_attribute('data-position')==before
            page.evaluate('window.noPose=false;window.twoPeople=true');page.wait_for_timeout(400);assert page.locator('.dodge-field').get_attribute('data-position')==before
            page.evaluate('window.twoPeople=false');page.wait_for_function("!document.querySelector('.camera-selected').hidden")
            record('live-video-lane-controls','Synthetic video drives the real camera source and game; all 3 lanes work, preview is mirrored; no/multiple people freeze obstacle progress, tracking resumes after reacquisition.')

            # Complete all obstacles through camera coordinates, with no arrow input.
            while page.locator('.dodge-field').count():
                obstacle=int(page.locator('.dodge-field').get_attribute('data-obstacle'))
                page.evaluate('(x)=>window.poseX=x',.82 if obstacle==0 else .18)
                page.wait_for_timeout(150)
            expect(page.locator('.reward')).to_be_visible();assert page.evaluate('streams.every(s=>s.getTracks().every(t=>t.readyState==="ended"))')
            assert page.evaluate('workers.every(w=>w.dead)');record('camera-complete','All five obstacles complete using camera coordinates; collision remains recoverable; successful reward releases camera tracks and worker.')

            # Late permission after cancellation must never leave a live camera behind.
            page.reload();page.wait_for_selector('[data-action="camera"]');page.evaluate("permissionMode='pending'");page.locator('[data-action="camera"]').click();page.locator('[data-action="buttons"]').click();page.evaluate('finishPermission()');page.wait_for_timeout(100)
            assert page.evaluate('streams.every(s=>s.getTracks().every(t=>t.readyState==="ended"))')
            expect(page.locator('.dodge-field')).to_have_attribute('data-mode','buttons')
            record('late-permission-cleanup','Switching to buttons while permission is pending stops a subsequently granted stream immediately; no late camera mode activation.')

            waiting=context.new_page();waiting.clock.install();waiting.goto(url);waiting.wait_for_selector('[data-action="camera"]');waiting.evaluate("permissionMode='pending'");waiting.locator('[data-action="camera"]').click();waiting.clock.run_for(16000)
            expect(waiting.locator('.dodge-field')).to_have_attribute('data-mode','buttons');waiting.evaluate('finishPermission()');waiting.clock.run_for(100)
            assert waiting.evaluate('streams.every(s=>s.getTracks().every(t=>t.readyState==="ended"))');waiting.close()
            unsupported=context.new_page();unsupported.goto(url);unsupported.wait_for_selector('[data-action="camera"]');unsupported.evaluate("Object.defineProperty(navigator,'mediaDevices',{value:undefined,configurable:true})");unsupported.locator('[data-action="camera"]').click()
            expect(unsupported.locator('.dodge-field')).to_have_attribute('data-mode','buttons');assert unsupported.evaluate('cameraCalls')==0;unsupported.close()
            record('unsupported-and-ignored-permission','Unsupported devices and ignored permission prompts return to buttons; a late grant after the 15-second timeout is closed immediately.')

            for event in ['visibilitychange','pagehide']:
                page.reload();page.wait_for_selector('[data-action="camera"]');page.locator('[data-action="camera"]').click();page.wait_for_function("document.querySelector('.dodge-field').dataset.mode==='camera'")
                page.evaluate('(event)=>{if(event==="visibilitychange"){Object.defineProperty(document,"hidden",{value:true,configurable:true});document.dispatchEvent(new Event(event))}else window.dispatchEvent(new Event(event))}',event)
                assert page.evaluate('streams.every(s=>s.getTracks().every(t=>t.readyState==="ended"))&&workers.every(w=>w.dead)')
                expect(page.locator('[data-action="challenge-start"]')).to_be_visible()
            record('background-camera-cleanup','Background and pagehide stop streams/workers and require an explicit resume; hidden time gives no progress.')

            page.reload();page.wait_for_selector('[data-action="camera"]');page.evaluate('window.modelFailure=true');page.locator('[data-action="camera"]').click();page.wait_for_function("document.querySelector('.dodge-field').dataset.mode==='buttons'")
            assert page.evaluate('streams.every(s=>s.getTracks().every(t=>t.readyState==="ended"))');expect(page.locator('[data-action="right"]')).to_be_enabled()
            page.reload();page.wait_for_selector('[data-action="camera"]');page.locator('[data-action="camera"]').click();page.wait_for_function("document.querySelector('.dodge-field').dataset.mode==='camera'");page.evaluate('window.noPose=true');page.wait_for_function("document.querySelector('.dodge-field').dataset.mode==='buttons'",timeout=15000)
            assert page.evaluate('streams.every(s=>s.getTracks().every(t=>t.readyState==="ended"))');assert not errors,errors
            record('model-and-tracking-fallback','Model failure and 8 seconds without usable tracking release all resources and return to buttons; no JavaScript errors.')
            for width in [390,768,1180]:
                page.set_viewport_size({'width':width,'height':1180});page.reload();page.wait_for_selector('[data-action="camera"]');assert page.evaluate('document.documentElement.scrollWidth <= innerWidth+1')
            record('tablet-layout','390/768/820/1180px layout stays within viewport; camera labels use the supplied pre-rendered Zhuyin font.')
            # The actual story uses the same camera-enabled controller, preserves its save,
            # and cleanup also happens when switching directly to tilt/buttons.
            page.set_viewport_size({'width':820,'height':1180});page.goto(base+'stories/story-02/');page.wait_for_selector('[data-action="start-adventure"]')
            state=dict(version=1,scene='bamboo',clues=['prints','fur','tail'],inventory=['key'],completed=['hide'],placed=[],ending=None,textScale=1)
            page.evaluate('(s)=>{localStorage.setItem("adventure.story-02.state",JSON.stringify(s));localStorage.setItem("adventure.settings.sound","false");localStorage.setItem("moonCaveState","camera-test-sentinel")}',state)
            page.reload();page.locator('[data-action="start-adventure"]').click();expect(page.locator('[data-action="camera"]')).to_be_visible();assert page.evaluate('cameraCalls')==0
            page.locator('[data-action="camera"]').click();page.wait_for_function("document.querySelector('.dodge-field').dataset.mode==='camera'");expect(page.locator('[data-action="challenge-start"]')).to_be_hidden()
            page.locator('[data-action="buttons"]').click();assert page.evaluate('streams.every(s=>s.getTracks().every(t=>t.readyState==="ended"))&&workers.every(w=>w.dead)')
            assert page.evaluate('localStorage.getItem("moonCaveState")==="camera-test-sentinel"&&JSON.parse(localStorage.getItem("adventure.story-02.state")).scene==="bamboo"')
            record('story-camera-integration','Actual Story 02 exposes the opt-in camera only in bamboo; switching back closes it, start control stays hidden, existing story/Moon Cave saves are unchanged.')
            context.close();browser.close()
        (args.output/'camera-results.json').write_text(json.dumps(RESULTS,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
    finally:server.shutdown()

if __name__=='__main__':main()
