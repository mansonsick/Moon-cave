"""Local synthetic frames and poses only; never opens the user's physical camera.
Real tablet / child movement accuracy is a separate acceptance test.
"""
import argparse
import json
from pathlib import Path
from playwright.sync_api import sync_playwright, expect
from story_test_support import serve
from camera_lanes_test import FAKE_CAMERA

FAKE=FAKE_CAMERA[:FAKE_CAMERA.index('window.Worker=class')].replace("ctx.fillStyle='#466d58';ctx.fillRect(0,0,640,480);", "ctx.fillStyle='#ddd';ctx.fillRect(0,0,640,480);ctx.fillStyle='#1767ee';ctx.beginPath();ctx.arc(160,240,50,0,Math.PI*2);ctx.fill();window.fakeCanvas=c;")+'''
window.style='stand';window.ballY=.5;window.hasBall=true;window.colourPicked=false;window.frames=0;window.inferenceDelay=5;window.jumpHeight=.09;
window.Worker=class{
 constructor(){this.dead=false;workers.push(this)}
 postMessage(data){
  if(data.type==='init'){setTimeout(()=>this.emit({type:window.modelFailure?'error':'ready'}),5);return;}
  if(data.type==='colour'){window.colourPicked=!!data.colour;window.selectedColour=data.colour;return;}
  window.frames++;
  data.bitmap.close();const p=window.fixtureBody();
  if(window.style==='balance'){p[28].y=.6;p[26].y=.56;}
  if(window.style==='jump')for(const v of p)v.y-=window.jumpHeight;
  const ball=window.hasBall&&window.colourPicked?{x:.5,y:window.ballY,r:.025}:null;
  setTimeout(()=>this.emit({type:'pose',poses:window.noPose?[]:window.twoPeople?[p,p]:[p],ball,colorReady:window.colourPicked,at:data.at}),window.inferenceDelay);
 }
 emit(data){if(!this.dead)this.onmessage?.({data})}
 terminate(){this.dead=true;terminates++}
};
'''
RESULTS=[]
def record(name):print('PASS',name,flush=True);RESULTS.append(name)
def click(page,name):page.locator(f'[data-action="{name}"]').click()
def mode(page,name):page.wait_for_selector(f'.camera-action[data-mode="{name}"]')
def stopped(page):return page.evaluate('streams.every(s=>s.getTracks().every(t=>t.readyState==="ended"))&&workers.every(w=>w.dead)')
def setup(page,url,kind):
    page.goto(url);page.wait_for_selector('body[data-ready=true]')
    page.evaluate("async()=>{window.fixtureBody=(await import('../../tests/camera_actions_rules.js')).body}")
    click(page,kind)

def main():
    parser=argparse.ArgumentParser();parser.add_argument('--output',type=Path,default=Path('../hub-review/camera-actions'));out=parser.parse_args().output;out.mkdir(parents=True,exist_ok=True)
    server,base=serve();url=base+'experiments/camera-actions/'
    try:
      with sync_playwright() as p:
        browser=p.chromium.launch();context=browser.new_context(viewport={'width':820,'height':1180});context.add_init_script(FAKE)
        page=context.new_page();errors=[];page.on('pageerror',lambda e:errors.append(str(e)))
        setup(page,url,'balance')
        assert page.evaluate("async()=>(await import('../../tests/camera_actions_rules.js')).runActionRuleTests()") == 16
        record('16 rule/pixel groups: balance, short/small/sparse jumps, missing frames, three ball checkpoints, one wrist, no-ascent/drop/held-ball negatives and timestamps')
        assert page.evaluate('cameraCalls')==0
        page.evaluate("permissionMode='denied'");click(page,'action-camera');mode(page,'manual');assert page.evaluate('constraints.audio===false');click(page,'action-manual-start');mode(page,'manual-run');click(page,'action-stop')
        setup(page,url,'jump');page.evaluate("Object.defineProperty(navigator,'mediaDevices',{value:undefined,configurable:true})");click(page,'action-camera');mode(page,'manual');click(page,'action-manual-start')
        for _ in range(5):click(page,'action-manual-rep')
        mode(page,'done');assert page.locator('.action-counter').inner_text()=='5 / 5';page.wait_for_timeout(300);expect(page.locator('[data-action=continue]')).to_be_visible()
        record('opt-in video only, denied/unsupported fallback, manual repetitions, reward waits for Continue')
        setup(page,url,'balance');click(page,'action-camera');mode(page,'camera');page.wait_for_timeout(2300)
        page.evaluate("style='balance'");page.wait_for_timeout(1200);assert page.locator('progress').evaluate('e=>e.value')>0
        page.evaluate('twoPeople=true');page.wait_for_timeout(350);assert page.locator('progress').evaluate('e=>e.value')==0
        page.evaluate('twoPeople=false');mode(page,'camera');page.wait_for_selector('.camera-action[data-mode=done]',timeout=12000);assert stopped(page)
        page.screenshot(path=str(out/'balance-success.png'),full_page=True)
        record('camera balance counts 8s from full body, resets for two people, completes and stops streams/worker')
        setup(page,url,'jump');click(page,'action-camera');mode(page,'prepare');assert page.locator('.action-counter').inner_text() in ['5','4'];assert page.locator('progress').evaluate('e=>e.value')==0
        mode(page,'camera');page.wait_for_timeout(2300);page.evaluate('jumpHeight=.04')
        for _ in range(5):
            page.evaluate("style='jump'");page.wait_for_timeout(120);page.evaluate("style='stand'");page.wait_for_timeout(650)
        mode(page,'done');assert stopped(page);assert page.locator('.action-counter').inner_text()=='5 / 5'
        record('5s step-back preparation, five short/small camera jumps require takeoff and landing, no duplicate counts')
        setup(page,url,'catch');click(page,'action-camera');mode(page,'setup');page.evaluate('noPose=true');page.wait_for_timeout(8500)
        mode(page,'setup');assert page.locator('progress').evaluate('e=>e.value')==0
        click(page,'camera-photo');mode(page,'photo')
        before=page.locator('.camera-photo').evaluate('c=>c.toDataURL()')
        page.evaluate("const ctx=fakeCanvas.getContext('2d');ctx.fillStyle='#ed2814';ctx.fillRect(0,0,640,480)");page.wait_for_timeout(300)
        assert page.locator('.camera-photo').evaluate('c=>c.toDataURL()')==before
        photo=page.locator('.camera-photo');box=photo.bounding_box()
        photo.click(position={'x':box['width']*.1,'y':box['height']*.1});mode(page,'photo');expect(page.locator('[data-action=camera-photo-ready]')).to_be_hidden()
        photo.click(position={'x':box['width']*.75,'y':box['height']*.5});mode(page,'selected')
        assert 200<page.evaluate('selectedColour.h')<240
        page.screenshot(path=str(out/'photo-selected.png'),full_page=True)
        page.evaluate('noPose=false');click(page,'camera-photo-ready');mode(page,'prepare');assert page.locator('.camera-photo').evaluate('c=>c.width')==0
        mode(page,'camera')
        for _ in range(3):
            page.evaluate('ballY=.5');page.wait_for_timeout(1000)
            page.evaluate('hasBall=false');page.wait_for_timeout(300);expect(page.locator('.action-status[data-status=camera-ball-wait]')).to_be_visible()
            page.evaluate('ballY=.12;hasBall=true');page.wait_for_timeout(150)
            page.evaluate('hasBall=false');page.wait_for_timeout(600)
            page.evaluate('ballY=.50;hasBall=true');page.wait_for_timeout(650)
            if _==0:
                assert page.locator('.action-counter').inner_text()=='1 / 3'
                click(page,'camera-repick');mode(page,'setup');click(page,'camera-photo');mode(page,'photo')
                box=photo.bounding_box();photo.click(position={'x':box['width']*.5,'y':box['height']*.5});mode(page,'selected')
                click(page,'camera-photo-ready');mode(page,'camera');assert page.locator('.action-counter').inner_text()=='1 / 3'
        mode(page,'done');assert stopped(page);assert page.locator('.action-counter').inner_text()=='3 / 3'
        record('frozen mirrored photo selection without body, invalid colour retry, 5s retreat, three coarse throws with invisible gaps, photo and streams discarded')
        setup(page,url,'catch');click(page,'action-camera');mode(page,'setup');click(page,'camera-photo');mode(page,'photo');click(page,'camera-retake');mode(page,'setup');assert page.locator('.camera-photo').evaluate('c=>c.width')==0
        click(page,'balance');assert stopped(page)
        page.evaluate("permissionMode='pending'");click(page,'action-camera');mode(page,'loading');click(page,'action-manual');page.evaluate('finishPermission()');page.wait_for_timeout(100);assert stopped(page);mode(page,'manual')
        record('switching challenges stops camera; cancellation also closes a later permission grant')
        for failure in ['model','missing','hidden','pagehide','timeout']:
            setup(page,url,'jump')
            if failure=='model':page.evaluate('modelFailure=true')
            if failure=='timeout':
                page.clock.install();page.evaluate("permissionMode='pending'");click(page,'action-camera');page.clock.run_for(16000);mode(page,'manual');page.evaluate('finishPermission()');page.clock.run_for(100);assert stopped(page);page.clock.resume();continue
            click(page,'action-camera')
            if failure=='model':mode(page,'manual')
            else:
                mode(page,'camera')
                if failure=='missing':page.evaluate('noPose=true');page.wait_for_selector('.camera-action[data-mode=manual]',timeout=11000)
                elif failure=='hidden':page.evaluate("Object.defineProperty(document,'hidden',{value:true,configurable:true});document.dispatchEvent(new Event('visibilitychange'))");mode(page,'idle')
                else:
                    page.evaluate("window.dispatchEvent(new Event('pagehide'))");assert stopped(page)
                    page.evaluate("window.dispatchEvent(new PageTransitionEvent('pageshow',{persisted:true}))");mode(page,'idle')
            assert stopped(page)
        record('model failure, 8s no body, ignored permission, background and pagehide cleanup/fallback; no automatic resume')
        setup(page,url,'jump');page.evaluate('inferenceDelay=720');click(page,'action-camera');mode(page,'camera');page.wait_for_selector('[data-status=camera-jump]',timeout=7000)
        assert page.evaluate('frames')>3
        # A slow worker result remains readable; it is not always expired at delivery.
        assert page.locator('.action-camera-view canvas:not(.camera-photo)').evaluate("c=>c.getContext('2d').getImageData(0,0,c.width,c.height).data.some(v=>v!==0)")
        click(page,'action-stop');assert stopped(page)
        for stage in ['photo','selected','prepare']:
            setup(page,url,'catch');click(page,'action-camera');mode(page,'setup');click(page,'camera-photo');mode(page,'photo')
            if stage!='photo':
                box=page.locator('.camera-photo').bounding_box();page.locator('.camera-photo').click(position={'x':box['width']*.75,'y':box['height']*.5});mode(page,'selected')
            if stage=='prepare':click(page,'camera-photo-ready');mode(page,'prepare')
            page.evaluate("window.dispatchEvent(new Event('pagehide'))");assert stopped(page);assert page.locator('.camera-photo').evaluate('c=>c.width')==0
        record('slow inference result is delivered; photo, selection and countdown clean up camera and in-memory photo on leave')
        for width,height in [(390,844),(820,1180),(1180,820)]:
            setup(page,url,'catch');page.set_viewport_size({'width':width,'height':height});page.evaluate("document.documentElement.style.setProperty('--text-scale',1.5)")
            assert page.evaluate('document.documentElement.scrollWidth<=innerWidth')
            page.screenshot(path=str(out/f'camera-ui-{width}.png'),full_page=True)
        assert not errors,errors
        story=context.new_page();story.goto(base+'stories/story-03/');story.wait_for_selector('body[data-ready=true]')
        migrations=story.evaluate('''async()=>{
          const s=await import('./state.js'),m=await import('../../engine/math-worksheet.js'),old=s.fresh('motionreview');old.schema=2;
          const w=m.createWorksheet(old.code);old.passwords=[0,1,2].map(g=>m.gatePasswords(w,g));old.seed=true;old.scene='ordinary';
          const migrated=s.validate(old);
          if(migrated.schema!==3||migrated.scene!=='ordinary'||!Object.values(migrated.actions).every(Boolean))throw Error('v2 ending lost');
          const fresh=s.validate({...migrated,scene:'chest',actions:{balance:true,jump:true,catch:false}});if(fresh.scene!=='catch')throw Error('pending catch skipped');
          return true;
        }''');assert migrations
        for kind in ['balance','jump','catch']:
            story.evaluate('''async kind=>{
              const s=await import('./state.js'),m=await import('../../engine/math-worksheet.js');const state=s.fresh('motionreview'),w=m.createWorksheet(state.code);
              state.passwords=[0,1,2].map(g=>m.gatePasswords(w,g));state.scene=kind;state.actions={balance:kind!=='balance',jump:kind==='catch',catch:false};
              localStorage.setItem(s.KEY,JSON.stringify(state));
            }''',kind);story.reload();story.wait_for_selector('body[data-ready=true]');story.evaluate('Promise.all([...document.images].map(i=>i.decode()))')
            assert story.locator('body').get_attribute('data-scene')==kind
            story.screenshot(path=str(out/f'story-{kind}.png'),full_page=True)
        click(story,'action-manual');click(story,'action-manual-start');click(story,'action-manual-rep');story.reload();story.wait_for_selector('.camera-action[data-mode=idle]');assert story.locator('.action-counter').inner_text()=='0 / 3'
        click(story,'action-manual');click(story,'action-manual-start')
        for _ in range(3):click(story,'action-manual-rep')
        mode(story,'done');story.reload();mode(story,'done');assert story.evaluate('cameraCalls')==0
        saved=story.evaluate("JSON.parse(localStorage.getItem('adventure.story-03.state'))")
        assert saved['actions']==dict(balance=True,jump=True,catch=True)
        assert not any(k in json.dumps(saved) for k in ['landmarks','colorReady','ballY','permission'])
        record('schema-2 ending preserved, pending actions guarded, story art inspected, completed action survives refresh, partial motion and camera data not saved')
        context.close()
        # Actual bundled inference on a generated blank frame; proves wiring/model loading,
        # NOT recognition accuracy on a real child. No getUserMedia call here.
        real=browser.new_page();real.goto(url);real.wait_for_selector('body[data-ready=true]')
        check=real.evaluate('''async()=>{
          const worker=new Worker(new URL('../../engine/camera-action-worker.js',location.href));let empty=null;
          try{return await new Promise((resolve,reject)=>{
            const timeout=setTimeout(()=>reject(Error('worker timed out')),40000);
            worker.onerror=e=>{clearTimeout(timeout);reject(Error(e.message))};
            worker.onmessage=async({data})=>{
              if(data.type==='error'){clearTimeout(timeout);reject(Error('model error'))}
              if(data.type==='ready'){const c=document.createElement('canvas');c.width=320;c.height=240;const ctx=c.getContext('2d');ctx.fillStyle='#eee';ctx.fillRect(0,0,320,240);const bitmap=await createImageBitmap(c);worker.postMessage({type:'frame',bitmap,at:10,catch:true},[bitmap])}
              if(data.type==='pose'){
                if(!empty){
                  empty={poses:data.poses.length,ball:data.ball,color:data.colorReady};
                  const c=document.createElement('canvas');c.width=320;c.height=240;const ctx=c.getContext('2d');ctx.fillStyle='#ddd';ctx.fillRect(0,0,320,240);
                  ctx.fillStyle='#1767ee';ctx.beginPath();ctx.arc(80,120,16,0,Math.PI*2);ctx.fill();
                  const {pickColour}=await import('../../engine/ball-vision.js');const colour=pickColour(ctx.getImageData(0,0,320,240),.25,.5);
                  worker.postMessage({type:'colour',colour});const bitmap=await createImageBitmap(c);worker.postMessage({type:'frame',bitmap,at:100,catch:true},[bitmap]);
                }else{clearTimeout(timeout);resolve({empty,colour:data.colorReady,found:!!data.ball&&Math.abs(data.ball.x-.25)<.02&&Math.abs(data.ball.y-.5)<.02})}
              }
            };worker.postMessage({type:'init'});
          })}finally{worker.terminate()}
        }''')
        assert check=={'empty':{'poses':0,'ball':None,'color':False},'colour':True,'found':True};record('actual vendored MediaPipe/WASM worker runs blank pixels then detects selected photo colour, without physical camera')
        browser.close()
      (out/'results.json').write_text(json.dumps({'passed':RESULTS},ensure_ascii=False,indent=2),encoding='utf-8')
    finally:server.shutdown()

if __name__=='__main__':main()
