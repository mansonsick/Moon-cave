"""Reproduce Story 02's original synthesized sounds; no samples or network input.

Run: python scripts/build_story02_audio.py
Requires NumPy and SciPy. Output: mono 22,050 Hz PCM16 WAV, supported by Web Audio.
"""
import hashlib
import json
import wave
from pathlib import Path
import numpy as np
from scipy.signal import butter, sosfilt

RATE = 22050
ROOT = Path(__file__).resolve().parents[1] / 'stories/story-02/assets/audio'
RNG = np.random.default_rng(20260928)

def timeline(seconds): return np.arange(round(seconds*RATE),dtype=np.float64)/RATE

def noise(seconds,low=150,high=3500):
    raw=RNG.standard_normal(round(seconds*RATE))
    signal=sosfilt(butter(2,[low,high],btype='bandpass',fs=RATE,output='sos'),raw)
    return signal/max(np.max(np.abs(signal)),.001)

def fade(signal,attack=.012,release=.04):
    signal=signal.copy();a=min(round(attack*RATE),len(signal));r=min(round(release*RATE),len(signal))
    if a:signal[:a]*=np.sin(np.linspace(0,np.pi/2,a))**2
    if r:signal[-r:]*=np.sin(np.linspace(np.pi/2,0,r))**2
    return signal

def tone(seconds,hz,partials=(1,.18,.05),decay=5):
    t=timeline(seconds);out=np.zeros(len(t))
    for harmonic,amplitude in enumerate(partials,1):
        out+=amplitude*np.sin(2*np.pi*hz*harmonic*t)*np.exp(-decay*t/seconds*harmonic**.4)
    return fade(out,.012,.06)

def add(bed,sound,at,gain=1):
    start=round(at*RATE);end=min(len(bed),start+len(sound))
    if end>start:bed[start:end]+=sound[:end-start]*gain

def forest():
    t=timeline(20);x=noise(20,180,2700)*(.16+.04*np.sin(2*np.pi*t/10))
    for at,hz in [(2.2,1450),(6.9,1700),(12.3,1550),(16.6,1800)]:
        s=timeline(.36);bird=np.sin(2*np.pi*(hz*s+420*s*s))*np.sin(np.pi*s/.36)**2
        add(x,bird,at,.075);add(x,bird*.6,at+.48,.075)
    for at in [4.2,9.8,14.7,18.1]:
        s=timeline(.72);cricket=np.sin(2*np.pi*3300*s)*(np.sin(2*np.pi*12*s)**6)*np.sin(np.pi*s/.72)**2
        add(x,cricket,at,.021)
    return fade(x,.8,.8)

def house():
    t=timeline(20);x=noise(20,220,1800)*(.12+.025*np.sin(2*np.pi*t/8))
    for at in [1.5,5.4,11.2,16.8]:
        s=timeline(.75);phase=2*np.pi*(210*s+18*np.sin(2*np.pi*1.5*s)/(2*np.pi*1.5))
        creak=(np.sin(phase)+.12*np.sin(2.2*phase))*np.sin(np.pi*s/.75)**2
        add(x,creak,at,.045)
    for at in [3.2,4.8,7.9,9.4,13.2,18.1]:add(x,fade(noise(.075,900,4000),.006,.06),at,.02)
    return fade(x,.8,.8)

def bamboo():
    t=timeline(20);x=noise(20,400,4200)*(.18+.055*np.sin(2*np.pi*t/4))
    for index,at in enumerate(np.arange(.5,19.5,.5)):
        step=tone(.15,145 if index%2 else 165,partials=(1,.08),decay=6)
        add(x,step,at,.048);add(x,fade(noise(.19,900,4000),.02,.13),at+.045,.03)
    return fade(x,.7,.7)

def temple():
    t=timeline(20);x=noise(20,140,1900)*(.14+.025*np.sin(2*np.pi*t/10))
    # A soft, continuous air tone, never a bell/chime before the child discovers the hook.
    x+=(np.sin(2*np.pi*174.6*t)+.45*np.sin(2*np.pi*261.6*t))*.009*(.7+.3*np.sin(2*np.pi*t/20))
    return fade(x,1,1)

def found():
    x=np.zeros(round(.46*RATE));add(x,tone(.32,660,decay=6),.01,.6);add(x,tone(.25,880,decay=6),.16,.32)
    return fade(x)

def success():
    x=np.zeros(round(.96*RATE))
    for at,hz in [(0,440),(.18,554.37),(.36,659.25)]:add(x,tone(.57,hz,decay=5),at,.42)
    return fade(x)

def fail_soft():
    t=timeline(.42);phase=2*np.pi*(200*t-65*t*t/.42)
    return fade(np.sin(phase)*np.exp(-9*t),.02,.08)

def drag_lock():
    x=np.zeros(round(.46*RATE));add(x,fade(noise(.055,400,2300),.005,.04),.012,.18)
    add(x,tone(.3,780,partials=(1,.09),decay=8),.08,.28)
    return fade(x)

def secret_bell():
    t=timeline(3.3);bell=np.zeros(len(t))
    for ratio,amplitude,decay in [(1,1,1.25),(2.71,.32,2),(5.17,.12,3.5),(7.32,.045,5)]:
        bell+=amplitude*np.sin(2*np.pi*523.25*ratio*t)*np.exp(-decay*t)
    bell=fade(bell,.006,.4);x=np.zeros(round(3.9*RATE))
    add(x,bell,.015);add(x,bell,.255,.16);add(x,bell,.525,.07)
    return fade(x,.006,.35)

def main():
    records=[]
    entries=[('forest-evening','ambience',forest,.30),('creepy-house','ambience',house,.27),('bamboo-chase','ambience',bamboo,.32),('temple-night','ambience',temple,.27),('found-item','sfx',found,.46),('success','sfx',success,.50),('fail-soft','sfx',fail_soft,.36),('drag-lock','sfx',drag_lock,.40),('secret-bell','sfx',secret_bell,.55)]
    for id,category,build,peak in entries:
        x=build();x*=peak/max(np.max(np.abs(x)),.001)
        pcm=np.round(np.clip(x,-1,1)*32767).astype('<i2')
        path=ROOT/category/(id+'.wav');path.parent.mkdir(parents=True,exist_ok=True)
        with wave.open(str(path),'wb') as wav:
            wav.setnchannels(1);wav.setsampwidth(2);wav.setframerate(RATE);wav.writeframes(pcm.tobytes())
        records.append({'id':id,'file':str(path.relative_to(ROOT)).replace('\\','/'),'category':category,'seconds':len(x)/RATE,'bytes':path.stat().st_size,'sha256':hashlib.sha256(path.read_bytes()).hexdigest(),'sampleRate':RATE,'peak':round(float(np.max(np.abs(x))),4),'rms':round(float(np.sqrt(np.mean(x*x))),4),'source':'Original procedural synthesis; no third-party samples','loop':category=='ambience'})
    (ROOT/'manifest.json').write_text(json.dumps({'generator':'scripts/build_story02_audio.py','seed':20260928,'assets':records},ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
    print(f'Built {len(records)} original WAV files, {sum(r["bytes"] for r in records)/1e6:.2f} MB total.')

if __name__=='__main__':main()
