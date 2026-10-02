"""Original quiet music-box / wordless vowel / wing-rustle audio. No sampled music."""
import hashlib, json, wave
from pathlib import Path
import numpy as np

ROOT=Path(__file__).resolve().parents[1]/'stories/story-05/assets/audio'
RATE=22050
rng=np.random.default_rng(20261002)

def note(freq, seconds=1.7):
    t=np.arange(int(seconds*RATE))/RATE
    return (np.sin(2*np.pi*freq*t)+.22*np.sin(2*np.pi*freq*2.76*t)+.1*np.sin(2*np.pi*freq*5.4*t))*np.exp(-t*3)*np.minimum(t/.012,1)

def ambience(kind):
    seconds=12;n=int(RATE*seconds);t=np.arange(n)/RATE
    # Six notes in an original minor motif, distinct rhythms for the three gates.
    freqs={'fog':[261.63,311.13,293.66,220,329.63,246.94],'house':[220,261.63,246.94,196,233.08,293.66],
           'bridge':[293.66,349.23,329.63,246.94,392,311.13],'dawn':[261.63,329.63,392,440,392,329.63]}[kind]
    x=np.zeros(n)
    for i,f in enumerate(freqs):
        start=int((.4+i*1.85)*RATE);sample=note(f);length=min(len(sample),n-start);x[start:start+length]+=.14*sample[:length]
    hum=np.sin(2*np.pi*(110*t+.13*np.sin(2*np.pi*.45*t)))+.3*np.sin(2*np.pi*220*t)
    x+=hum*.022*(.5-.5*np.cos(2*np.pi*t/seconds))
    if kind!='dawn':
        rustle=rng.normal(size=n);rustle=np.convolve(rustle,np.ones(24)/24,mode='same')
        x+=rustle*.04*(np.maximum(0,np.sin(2*np.pi*t*(.45 if kind=='bridge' else .23)))**8)
        x+=.028*np.sin(2*np.pi*55*t)*np.maximum(0,np.cos(2*np.pi*t*(1 if kind=='bridge' else .5)))**18
    fade=np.minimum(t/.3,1)*np.minimum((seconds-t)/.4,1);return x*fade

def cue(kind):
    if kind=='fail-soft':return note(196,.7)*.18+note(185,.7)*.08
    if kind=='wing':
        t=np.arange(RATE)/RATE;noise=np.convolve(rng.normal(size=RATE),np.ones(12)/12,mode='same')
        return noise*.2*np.sin(np.pi*t)**2*(.2+.8*np.maximum(0,np.sin(t*27)))
    if kind=='moonlight':
        x=np.zeros(int(RATE*1.5))
        for i,f in enumerate([523.25,659.25,783.99]):
            s=note(f,1.5-i*.15)*.15;j=int(i*.15*RATE);x[j:j+len(s)]+=s
        return x
    return note(659.25,.9)*.16+note(783.99,.9)*.12

def write_audio(name,x):
    path=ROOT/(name+'.wav');pcm=np.int16(np.clip(x,-.9,.9)*32767)
    with wave.open(str(path),'wb') as f:f.setnchannels(1);f.setsampwidth(2);f.setframerate(RATE);f.writeframes(pcm.tobytes())
    return dict(src=path.name,available=True,seconds=round(len(x)/RATE,3),sha256=hashlib.sha256(path.read_bytes()).hexdigest())

def main():
    ROOT.mkdir(parents=True,exist_ok=True);manifest={}
    for name in ['fog','house','bridge','dawn']:
        manifest[name]={**write_audio(name,ambience(name)), 'category':'ambience','volume':.18}
    for name in ['success','fail-soft','wing','moonlight']:
        manifest[name]={**write_audio(name,cue(name)),'category':'sfx','volume':.52}
    letters=json.loads((ROOT/'letters/manifest.json').read_text(encoding='utf-8-sig'))
    for item in letters:
        with wave.open(str(ROOT/item['src']),'rb') as f:seconds=f.getnframes()/f.getframerate()
        manifest['letter-'+item['letter']]={**item,'available':True,'category':'letter','volume':.9,'seconds':seconds}
    (ROOT/'manifest.json').write_text(json.dumps({'source':'Original procedural ambience/SFX; local installed en-US TTS for letter names, no third-party samples','entries':manifest},ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
    print('Built 4 original ambience loops, 4 cues and indexed 26 letter-name recordings.')

if __name__=='__main__':main()
