import {loadText,symbolImage} from './text.js';
import {SymbolAudio} from './symbol-audio.js';
import {POOL} from './state.js';
const text=await loadText(),manifest=await(await fetch('./assets/audio/manifest.json')).json();
// This page never reads, saves or clears a story state and does not alter the sound preference.
const audio=new SymbolAudio(manifest.entries,new URL('./assets/audio/',import.meta.url),true);
const root=document.querySelector('#app');root.replaceChildren();root.className='shell';root.setAttribute('aria-busy','false');
const h=document.createElement('h1');h.append(text('audio-review'));root.append(h);
const note=document.createElement('p');note.className='story-copy';note.append(text('review-note'));root.append(note);
const home=document.createElement('a');home.href='./';home.append(text('menu'));root.append(home);
const status=document.createElement('p');status.className='story-copy';status.setAttribute('role','status');root.append(status);
const grid=document.createElement('div');grid.className='audio-grid';root.append(grid);let revision=0;
for(const c of POOL){const button=document.createElement('button');button.type='button';button.dataset.symbol=c;button.setAttribute('aria-label','試聽 '+c);button.append(symbolImage(c));grid.append(button);button.addEventListener('click',async()=>{const token=++revision;status.replaceChildren(text('sound-playing'));const unlocked=await audio.unlock();const ok=unlocked&&await audio.symbol(c);if(token!==revision)return;status.replaceChildren(symbolImage(c),text(ok?'sound-check':'sound-fail'));});}
const credits=document.createElement('section');credits.id='credits';credits.className='credits lesson-panel';
const title=document.createElement('h2');title.append(text('credits'));credits.append(title);
const details=document.createElement('p');details.append(text('audio-credit-note'));credits.append(details);
for(const [id,url] of [['audio-credit-title',manifest.source],['credits',manifest.license]]){const a=document.createElement('a');a.href=url;a.target='_blank';a.rel='noopener';a.append(text(id));if(id==='credits')a.append(document.createTextNode(' · CC BY 4.0'));const p=document.createElement('p');p.append(a);credits.append(p);}root.append(credits);
window.addEventListener('pagehide',()=>{revision++;audio.setHidden(true);});window.addEventListener('pageshow',()=>audio.setHidden(document.hidden));document.addEventListener('visibilitychange',()=>{if(document.hidden)revision++;audio.setHidden(document.hidden);});
