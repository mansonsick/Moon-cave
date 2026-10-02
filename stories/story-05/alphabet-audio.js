import {AudioManager} from '../../engine/audio-manager.js';

// Voice completion / cancellation controls the timer; existing books' manager stays unchanged.
export class AlphabetAudio extends AudioManager {
  constructor(...args) {super(...args);this.letterRevision=0;this.letterVoice=null;this.finishLetter=null;this.background=null;}
  sceneAmbience(id) {this.background=id;void this.setAmbience(id,this.letterVoice?.12:1);}
  cancelLetter() {
    this.letterRevision++;
    if(this.letterVoice){this.stopVoice(this.letterVoice);this.letterVoice=null;}
    this.finishLetter?.(false);this.finishLetter=null;
    if(this.background)void this.setAmbience(this.background,1);
  }
  async letter(letter) {
    this.cancelLetter();const revision=this.letterRevision;
    if(!this.enabled||!this.unlocked||this.hidden)return false;
    const buffer=await Promise.race([this.buffer('letter-'+letter),new Promise(r=>setTimeout(()=>r(null),6500))]);
    if(!buffer||revision!==this.letterRevision||!this.enabled||this.hidden||this.context?.state!=='running')return false;
    return new Promise(resolve=>{
      const source=this.context.createBufferSource(),gain=this.context.createGain();
      source.buffer=buffer;gain.gain.value=.9;source.connect(gain);gain.connect(this.context.destination);
      const voice={source,gain,id:'letter-'+letter};this.letterVoice=voice;this.voices.add(voice);
      void this.setAmbience(this.background,.12);
      let done=false;
      const finish=ok=>{if(done)return;done=true;clearTimeout(timeout);if(this.letterVoice===voice)this.letterVoice=null;this.finishLetter=null;
        this.stopVoice(voice);if(this.background)void this.setAmbience(this.background,1);resolve(ok);};
      const timeout=setTimeout(()=>finish(false),(buffer.duration+1.5)*1000);
      this.finishLetter=finish;source.onended=()=>finish(true);
      try{source.start();}catch{finish(false);}
    });
  }
  setEnabled(value){this.cancelLetter();super.setEnabled(value);}
  setHidden(value){if(value)this.cancelLetter();super.setHidden(value);}
  dispose(){this.cancelLetter();super.dispose();}
}
