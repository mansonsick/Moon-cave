import {AudioManager} from '../../engine/audio-manager.js';

export class SymbolAudio extends AudioManager {
  constructor(manifest,baseURL,enabled=true) {
    super(Object.fromEntries(Object.entries(manifest).map(([id,e])=>[id,e.category==='symbol'?{...e,src:e.src+'?v='+e.sha256.slice(0,12)}:e])),baseURL,enabled);
    this.symbolRevision=0;this.activeSymbol=null;this.background=null;this.sceneScale=1;
  }
  sceneAmbience(id,scale=1) {
    this.background=id||null;this.sceneScale=scale;
    if(!id){this.desired=null;this.stopAmbience();return;}
    void this.setAmbience(id,this.sceneScale*(this.activeSymbol?.08:1));
  }
  cancelSymbol() {
    this.symbolRevision++;this.activeSymbol?.finish(false);
  }
  async symbol(symbol) {
    this.cancelSymbol();const revision=this.symbolRevision;
    if(!this.enabled||!this.unlocked||this.hidden)return false;
    const id='symbol-'+symbol.codePointAt(0).toString(16);
    // An explicit retry also retries a previously failed download.
    if(this.cache.has(id)&&!await this.cache.get(id))this.cache.delete(id);
    const buffer=await this.buffer(id);
    if(!buffer||revision!==this.symbolRevision||!this.enabled||this.hidden||this.context?.state!=='running')return false;
    return new Promise(resolve=>{
      const source=this.context.createBufferSource(),gain=this.context.createGain();source.buffer=buffer;
      gain.gain.value=this.level(id,.9);source.connect(gain);gain.connect(this.context.destination);
      const voice={source,gain,id};let done=false,timer;
      const job={voice,finish:ok=>{
        if(done)return;done=true;clearTimeout(timer);source.onended=null;this.stopVoice(voice);
        if(this.activeSymbol===job)this.activeSymbol=null;
        if(this.background)void this.setAmbience(this.background,this.sceneScale);resolve(ok);
      }};
      this.activeSymbol=job;this.voices.add(voice);
      if(this.background)void this.setAmbience(this.background,this.sceneScale*.08);
      timer=setTimeout(()=>job.finish(false),(buffer.duration+1.5)*1000);
      source.onended=()=>job.finish(true);
      try{source.start();}catch{job.finish(false);}
    });
  }
  setEnabled(value){this.cancelSymbol();super.setEnabled(value);if(value&&this.background)void this.setAmbience(this.background,this.sceneScale);}
  setHidden(value){if(value)this.cancelSymbol();super.setHidden(value);}
  dispose(){this.cancelSymbol();this.background=null;super.dispose();}
}
