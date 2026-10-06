"""Decode every official clip and exercise real voice-ended / cancellation behavior."""
import hashlib,json,io,wave
from pathlib import Path
import numpy as np
from playwright.sync_api import sync_playwright
from story_test_support import serve,remember_family_entry,REPO
from story_06_test import click,state,initial,learn,scene,tap,OUT
def main():
 manifest=json.loads((REPO/'stories/story-06/assets/audio/manifest.json').read_text(encoding='utf-8'));records=[];pcm_hashes=set()
 for id,e in manifest['entries'].items():
  if e['category']!='symbol':continue
  path=REPO/'stories/story-06/assets/audio'/e['src'];b=path.read_bytes();assert hashlib.sha256(b).hexdigest()==e['sha256']
  assert e['sourceEntry']=='audio/F'+str(ord(e['symbol'])-0x3104)+'.WAV'
  with wave.open(io.BytesIO(b)) as w:
   pcm=w.readframes(w.getnframes());digest=hashlib.sha256(pcm).hexdigest();assert digest not in pcm_hashes;pcm_hashes.add(digest)
   signal=np.frombuffer(pcm,dtype='<i2').astype(float)/32768;assert np.max(np.abs(signal))>.03
   records.append({'symbol':e['symbol'],'file':e['src'],'duration':w.getnframes()/w.getframerate(),'peak':float(np.max(np.abs(signal))),'pcmSha256':digest})
 assert len(records)==37
 server,base=serve();errors=[]
 try:
  with sync_playwright() as p:
   browser=p.chromium.launch();ctx=browser.new_context(viewport={'width':768,'height':1024});remember_family_entry(ctx);page=ctx.new_page();page.on('pageerror',lambda e:errors.append(str(e)))
   page.goto(base+'stories/story-06/audio-review.html');page.wait_for_selector('.audio-grid button')
   # Browser decodes all original WAVs at the actual runtime URLs.
   decoded=page.evaluate('''async()=>{const m=await(await fetch('./assets/audio/manifest.json')).json();const context=new AudioContext();const out=[];for(const [id,e] of Object.entries(m.entries)){const r=await fetch('./assets/audio/'+e.src);if(!r.ok)throw Error(e.src);const b=await context.decodeAudioData(await r.arrayBuffer());out.push({id,duration:b.duration,channels:b.numberOfChannels,length:b.length});}await context.close();return out;}''')
   assert len(decoded)==46
   # Run all 37 actual ended events; this is playback/decoding QA, not a human listening claim.
   for r in records:
    page.locator(f'.audio-grid [data-symbol="{r["symbol"]}"]').click()
    page.wait_for_function("document.querySelector('[role=status] .bpmf')?.getAttribute('aria-label')==='聲音試聽完成。'",timeout=8000)
    assert page.locator('[role=status] .symbol').get_attribute('alt')==r['symbol']
   initial(page,base+'stories/story-06/');learn(page);scene(page,'S04');target=state(page)['roundSymbols'][0][0]
   click(page,'begin-question');assert not page.locator('.answer-field').is_visible()
   page.wait_for_selector('.answer-field:not([hidden])',timeout=8000);tap(page,f'.answer-card[data-symbol="{target}"]');assert state(page)['results'][0][0]['mode']=='independent'
   click(page,'next-question');assert not page.locator('.answer-field').is_visible();click(page,'settings');assert not page.locator('.answer-field').is_visible();page.wait_for_timeout(1800);assert not page.locator('.answer-field').is_visible();click(page,'close');click(page,'begin-question');page.wait_for_selector('.answer-field:not([hidden])',timeout=8000)
   click(page,'assist');click(page,'sound');click(page,'sound');click(page,'begin-question');page.wait_for_selector('.answer-field:not([hidden])',timeout=8000);target=state(page)['roundSymbols'][0][1];tap(page,f'.answer-card[data-symbol="{target}"]');assert state(page)['results'][0][1]['mode']=='assisted'
   click(page,'next-question')
   page.route('**/audio/symbols/**',lambda r:r.abort());page.reload();click(page,'resume');click(page,'begin-question');page.wait_for_function("document.querySelector('.quiz-message .bpmf')?.getAttribute('aria-label')?.startsWith('聲音暫時聽不到')",timeout=10000);assert not page.locator('.answer-field').is_visible();click(page,'assist');target=state(page)['roundSymbols'][0][2];tap(page,f'.answer-card[data-symbol="{target}"]');assert state(page)['progress'][0]==3
   assert not errors,errors
   (OUT/'audio-results.json').write_text(json.dumps({'sourceMapping':'37 official HTML table IDs and WAV entries matched','recordings':records,'webAudioDecoded':decoded,'browserPlayback':'37 actual ended events; no human listening claim','checks':['Cards hidden before voice ended','Actual heard question recorded independent','Settings cancels in-flight playback','Visual assistance remains assisted after sound toggles','Blocked download supports explicit visual fallback'],'pageErrors':errors},ensure_ascii=False,indent=2),encoding='utf-8')
   browser.close();print('PASS: 37 source mappings, unique nonempty PCM, 46 browser decodes, 37 playback completions and quiz audio lifecycle.')
 finally:server.shutdown()
if __name__=='__main__':main()
