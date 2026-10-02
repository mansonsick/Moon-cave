"""Rebuild pinned, credited human letter names, using local originals and Chromium."""
import base64, hashlib, json, wave
from pathlib import Path
import numpy as np
from playwright.sync_api import sync_playwright

ROOT=Path(__file__).resolve().parents[1]/'stories/story-05/assets/audio/letters'
RATE=22050

def main():
    sources=json.loads((ROOT/'sources.json').read_text(encoding='utf-8'))
    assert [s['letter'] for s in sources]==list('ABCDEFGHIJKLMNOPQRSTUVWXYZ')
    records=[];hashes=set()
    with sync_playwright() as p:
        browser=p.chromium.launch();page=browser.new_page()
        for source in sources:
            data=(ROOT/source['original']).read_bytes()
            assert hashlib.sha1(data).hexdigest()==source['sourceSha1'],source['letter']
            decoded=page.evaluate('''async b64=>{
              const c=new AudioContext({sampleRate:22050});
              try{const bytes=Uint8Array.from(atob(b64),x=>x.charCodeAt(0));const b=await c.decodeAudioData(bytes.buffer);
                const a=new Float32Array(b.length);for(let ch=0;ch<b.numberOfChannels;ch++){const d=b.getChannelData(ch);for(let i=0;i<a.length;i++)a[i]+=d[i]/b.numberOfChannels;}
                const u=new Uint8Array(a.buffer);let s='';for(let i=0;i<u.length;i+=8192)s+=String.fromCharCode(...u.subarray(i,i+8192));
                return {rate:b.sampleRate,pcm:btoa(s)};
              }finally{await c.close();}
            }''',base64.b64encode(data).decode())
            assert decoded['rate']==RATE
            x=np.frombuffer(base64.b64decode(decoded['pcm']),dtype='<f4').astype(np.float64)
            assert np.isfinite(x).all() and np.max(np.abs(x))>.02
            # Remove outside silence only, preserving a generous consonant margin.
            rms=np.sqrt(np.convolve(x*x,np.ones(220)/220,mode='same'))
            active=np.flatnonzero(rms>max(.0015,rms.max()*.035));assert len(active)
            start=max(0,int(active[0])-int(.10*RATE));end=min(len(x),int(active[-1])+int(.14*RATE))
            x=x[start:end];x-=x.mean()
            gain=min(.85/np.max(np.abs(x)),.18/np.sqrt(np.mean(x*x)))
            x=np.concatenate([np.zeros(int(.12*RATE)),x*gain,np.zeros(int(.18*RATE))])
            pcm=np.int16(np.clip(x,-1,1)*32767);path=ROOT/(source['letter'].lower()+'.wav')
            with wave.open(str(path),'wb') as f:f.setnchannels(1);f.setsampwidth(2);f.setframerate(RATE);f.writeframes(pcm.tobytes())
            digest=hashlib.sha256(path.read_bytes()).hexdigest();assert digest not in hashes,source['letter'];hashes.add(digest)
            records.append({**source,'src':'letters/'+path.name,'voice':'Human recording: '+source['author'],'sha256':digest,
                            'changes':'Converted to mono 22050 Hz PCM WAV; outside silence trimmed with consonant margins; volume normalized; short silence padding added.'})
        browser.close()
    (ROOT/'manifest.json').write_text(json.dumps(records,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
    print('Rebuilt 26 unique, source-pinned human letter names, with distinct A and I.')

if __name__=='__main__':main()
