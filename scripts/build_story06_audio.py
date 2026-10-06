"""Import the independently licensed MOE recordings without changing their bytes.

Pass --package and --official-index downloaded from the URLs recorded below.
Original, deterministic procedural ambience/SFX are generated separately.
"""
import argparse,hashlib,io,json,re,wave,zipfile
from pathlib import Path
import numpy as np
ROOT=Path(__file__).resolve().parents[1]
SOURCE='https://language.moe.gov.tw/001/Upload/files/site_content/M0001/juyin/'
def sha(b):return hashlib.sha256(b).hexdigest()
def wav(path,data,rate=22050):
 data=np.asarray(data);data=np.clip(data,-.95,.95)
 with wave.open(str(path),'wb') as w:w.setnchannels(1);w.setsampwidth(2);w.setframerate(rate);w.writeframes((data*32767).astype('<i2').tobytes())
def main():
 p=argparse.ArgumentParser(description=__doc__);p.add_argument('--package',type=Path,required=True);p.add_argument('--official-index',type=Path,required=True);a=p.parse_args()
 out=ROOT/'stories/story-06/assets/audio';(out/'symbols').mkdir(parents=True,exist_ok=True)
 html=a.official_index.read_text(encoding='utf-8-sig');mapping={}
 for row in re.findall(r'<tr>(.*?)</tr>',html,re.S):
  n=re.search(r"play\('a(\d+)'\)",row);s=re.search(r"zhStroker\('app', '([^']+)'\)",row)
  if n and s:mapping[s.group(1)]=int(n.group(1))
 pool=[chr(i) for i in range(0x3105,0x312a)];assert set(mapping)==set(pool)
 entries={};hashes=set()
 with zipfile.ZipFile(a.package) as z:
  for symbol in pool:
   number=mapping[symbol];entry=f'audio/F{number}.WAV'
   assert re.search(r'<audio id="a'+str(number)+r'">\s*<source src="'+re.escape(entry)+r'"',html)
   b=z.read(entry);digest=sha(b);assert digest not in hashes;hashes.add(digest)
   with wave.open(io.BytesIO(b)) as w:
    assert w.getsampwidth()==2 and w.getnchannels()==2
    pcm=np.frombuffer(w.readframes(w.getnframes()),dtype='<i2');assert np.max(np.abs(pcm.astype('int32')))>1000
    duration=w.getnframes()/w.getframerate();assert .2<duration<6
   code=f'{ord(symbol):04x}';path=out/'symbols'/f'{code}.wav';path.write_bytes(b)
   entries['symbol-'+code]={'category':'symbol','symbol':symbol,'available':True,'src':'symbols/'+code+'.wav','volume':.9,'sha256':digest,'duration':duration,'sourceEntry':entry,'changes':'None: original WAV bytes','author':'教育部終身教育司','license':'CC BY 4.0'}
 rate=22050
 def tone(data,time,freq,length,volume=.22):
  i=int(time*rate);n=min(int(length*rate),len(data)-i)
  if n<=0:return
  t=np.arange(n)/rate;env=np.minimum(t/.015,1)*np.exp(-t*5/max(length,.1));env[-min(250,n):]*=np.linspace(1,0,min(250,n))
  data[i:i+n]+=volume*env*(np.sin(2*np.pi*freq*t)+.2*np.sin(2*np.pi*freq*2.7*t))
 rng=np.random.default_rng(6)
 for name in ['quiet-forest','cricket-song','stream-song','bird-song','found-item','success','fail-soft','secret-bell','forest-celebration']:
  length=10.8 if name=='forest-celebration' else 12 if name.endswith(('forest','song')) else (2.8 if name=='secret-bell' else .9)
  data=np.zeros(int(length*rate))
  if name=='quiet-forest':
   for time,f in [(1,523.25),(4,659.25),(7,783.99),(10,587.33)]:tone(data,time,f,1.5,.13)
  elif name=='cricket-song':
   for time in np.arange(.3,11.5,.8):
    for j in range(3):tone(data,time+j*.085,3400,.065,.13)
   for time,f in [(1,523),(5,659),(9,784)]:tone(data,time,f,1,.08)
  elif name=='stream-song':
   noise=rng.normal(0,1,len(data));noise=np.convolve(noise,np.ones(12)/12,'same')
   data=noise*.11
   for time in np.arange(.6,11.7,.7):tone(data,time,float(rng.uniform(700,1400)),.22,.15)
  elif name=='bird-song':
   for time in np.arange(.8,11,2):
    for j,f in enumerate([1500,2100,1800]):tone(data,time+j*.16,f,.2,.17)
  elif name=='forest-celebration':
   # An original wordless choir-like melody with bell accents. No voice sample,
   # nursery-song recording or copyrighted tune is used.
   notes=[(0,523.25,.4),(.45,659.25,.4),(.9,783.99,.8),(1.8,659.25,.4),(2.25,698.46,.4),(2.7,783.99,.8),
          (3.6,880,.4),(4.05,783.99,.4),(4.5,659.25,.8),(5.4,587.33,.4),(5.85,659.25,.4),(6.3,783.99,.8),
          (7.2,1046.5,.55),(7.85,880,.4),(8.3,783.99,.4),(8.75,659.25,.4),(9.2,523.25,1.4)]
   for time,freq,duration in notes:
    n=int(duration*rate);t=np.arange(n)/rate;phase=2*np.pi*freq*t+.05*np.sin(2*np.pi*5*t)
    harmonics=range(1,9);weights=[.35/k+np.exp(-((k*freq-750)/350)**2)+.6*np.exp(-((k*freq-1200)/400)**2) for k in harmonics]
    voice=sum(w*np.sin(k*phase) for k,w in zip(harmonics,weights))/sum(weights)
    envelope=np.minimum(t/.05,1)*np.minimum((duration-t)/.12,1)
    i=int(time*rate);data[i:i+n]+=.29*envelope*voice
    tone(data,time,freq*2,min(duration,.6),.055)
   for time,freqs in [(0,[261.63,329.63,392]),(3.6,[220,349.23,440]),(7.2,[261.63,329.63,392])]:
    for f in freqs:tone(data,time,f,3.3,.045)
  elif name=='fail-soft':tone(data,0,330,.55,.16)
  else:
   for j,f in enumerate([523.25,659.25,783.99] if name=='success' else [784,1046,1568]):tone(data,j*.18,f,1.6 if name=='secret-bell' else .4,.25)
  data[:500]*=np.linspace(0,1,500);data[-500:]*=np.linspace(1,0,500)
  path=out/(name+'.wav');wav(path,data,rate)
  entries[name]={'category':'ambience' if length==12 else 'sfx','available':True,'src':path.name,'volume':.22 if length==12 else .48,'sha256':sha(path.read_bytes()),'duration':length,'author':'Moon-cave project','license':'Project original synthesis','changes':'Generated by scripts/build_story06_audio.py; no sampled music'}
 result={'source':SOURCE,'sourcePackage':SOURCE+'bopomofo_materials_20170213.zip','packageSha256':sha(a.package.read_bytes()),'mappingSource':SOURCE+'html_ch/index.html','mappingSha256':sha(a.official_index.read_bytes()),'license':'https://creativecommons.org/licenses/by/4.0/','entries':entries}
 (out/'manifest.json').write_text(json.dumps(result,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
 print('Imported 37 unchanged official recordings; generated 4 ambience and 5 SFX including an original completion melody.')
if __name__=='__main__':main()
