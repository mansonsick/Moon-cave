import {createWorksheet,normalizeCode,newCode,checkAnswers} from '../../engine/math-worksheet.js';
import {createStorage} from '../../engine/storage.js';
import {AudioManager} from '../../engine/audio-manager.js';
import {bindDrag,place} from '../../engine/interactions.js';
import {sceneLayers} from '../../engine/scene-layers.js';
import {fresh,validate,KEY} from './state.js';
import {loadText,button} from './text.js';

const app=document.querySelector('#app');
const star=`<svg viewBox="0 0 100 100" aria-hidden="true"><path d="M50 5 62 35 95 38 70 60 78 94 50 76 22 94 30 60 5 38 38 35Z" fill="#a77a40" stroke="#594326" stroke-width="5"/><path d="m47 25 7 42m-21-17 34 9" stroke="#79562e" stroke-width="3"/></svg>`;
const seed=`<svg viewBox="0 0 100 100" aria-hidden="true"><ellipse cx="50" cy="57" rx="25" ry="34" fill="#ffda69" stroke="#97702d" stroke-width="4"/><path d="M49 55Q35 20 66 10Q76 35 49 55" fill="#89b879" stroke="#416d43" stroke-width="4"/></svg>`;
try {
  const text=await loadText();
  const store=createStorage('story-03',()=>fresh(newCode()),validate);
  let state=store.load(), worksheet=createWorksheet(state.code), selected=0, cleanup=()=>{}, stale=false;
  let expectedCode=state.code, blocked=false;
  const manifest=Object.fromEntries(['found-item','success','fail-soft','drag-lock'].map(id=>[id,{category:'sfx',available:true,src:`../story-02/assets/audio/sfx/${id}.wav`,volume:.48}]));
  const audio=new AudioManager(manifest,import.meta.url,store.sound());
  const el=(tag,cls='')=>{const node=document.createElement(tag);node.className=cls;return node;};
  const action=(id,handler,name=id)=>button(text,id,handler,name);
  const line=(id,tag='p')=>{const n=el(tag);n.append(text(id));return n;};
  const link=(id,url,blank=false)=>{const n=el('a');n.href=url;n.append(text(id));if(blank){n.target='_blank';n.rel='noopener';}return n;};
  function persist(){const ok=store.save(state);if(!ok){blocked=true;document.querySelector('#storage-note')?.replaceChildren(text('storage-warning'));}return ok;}
  function go(scene){state.scene=scene;selected=0;persist();render();window.scrollTo({top:0,behavior:'instant'});}
  function closeDialog(){document.querySelector('dialog')?.close();document.querySelector('dialog')?.remove();}
  function modal(label,buttons){
    closeDialog();const d=el('dialog');d.append(line(label));const bar=el('div','actions');
    for(const [id,fn] of buttons)bar.append(action(id,()=>{closeDialog();fn();}));d.append(bar);document.body.append(d);d.showModal();return d;
  }
  function reward(label,next,sfx='found-item'){void audio.playSfx(sfx);modal(label,[['continue',next]]);}
  function reset(code){state=fresh(code);expectedCode=code;worksheet=createWorksheet(code);persist();stale=false;history.replaceState(null,'',`?code=${code}`);render();}
  function changeCode(code){
    if(code===state.code)return;
    const progressed=state.scene!=='cover'||state.entries.some(row=>row.some(v=>v!==''));
    if(progressed)modal('confirm-change',[['yes-change',()=>reset(code)],['cancel',()=>{}]]);else reset(code);
  }
  function staleWarning(){if(stale)return;stale=true;modal('stale',[['reload',()=>location.replace('./')]]);}
  document.addEventListener('click',event=>{
    if(event.target.closest('dialog'))return;
    try {const saved=JSON.parse(localStorage.getItem(KEY));if(saved&&saved.code!==expectedCode){event.preventDefault();event.stopImmediatePropagation();staleWarning();}}
    catch{/* Storage denial falls back to this tab's memory. */}
  },true);
  window.addEventListener('storage',event=>{if(event.key===KEY&&event.newValue){try{if(JSON.parse(event.newValue).code!==expectedCode)staleWarning();}catch{}}});
  document.addEventListener('visibilitychange',()=>audio.setHidden(document.hidden));
  document.addEventListener('pointerdown',()=>{if(state.scene!=='cover'&&!audio.unlocked)void audio.unlock();});
  window.addEventListener('pagehide',()=>{cleanup();audio.dispose();});
  const imageURL=new URL('./assets/images/',import.meta.url);
  function stageFor(scene){
    const forest=['cover','intro','ordinary','secret-home'].includes(scene);
    const roof=['chest','roof','secret'].includes(scene);
    const layers=[{id:'atong',src:'atong.png',box:[12,35,20,49],z:3},{id:'squirrel',src:'squirrel.png',box:[30,61,11,23],z:4}];
    if(roof){layers[0].box=[8,37,19,49];layers[1].box=[26,63,10,23];}
    if(scene.startsWith('gate')&&!state.solved[Number(scene.at(-1))-1])layers.unshift({id:'door',src:scene==='gate1'?'door-stone.png':'door.png',box:[38.6,17.5,22.3,55.2],z:1});
    if(scene==='chest')layers.unshift({id:'chest',src:state.seed?'chest-open.png':'chest.png',box:state.seed?[30,37,27,42]:[31,45,24,33],z:2});
    const stage=sceneLayers({background:forest?'forest-bg.png':roof?'roof-bg.png':'tower-bg.png',layers,baseURL:imageURL});
    if(['ordinary','secret-home'].includes(scene)){
      const glow=el('div','lantern-light');glow.setAttribute('aria-hidden','true');stage.append(glow);
    }
    if(scene==='secret'){
      const stars=el('div','constellation');stars.setAttribute('aria-hidden','true');
      stars.innerHTML='<svg viewBox="0 0 500 150"><g fill="none" stroke="#fff2a9" stroke-width="3"><path d="M130 120 165 65 180 30 197 66 240 80 280 115 310 70 305 28 340 15 363 38 350 90 280 115 200 128 130 120"/></g><g fill="#fff4bc">'+[[130,120],[165,65],[180,30],[197,66],[240,80],[280,115],[310,70],[305,28],[340,15],[363,38],[350,90],[200,128]].map(([x,y])=>`<circle cx="${x}" cy="${y}" r="5"/>`).join('')+'</g></svg>';stage.append(stars);
    }
    return stage;
  }
  function header(){
    const h=el('header','toolbar');h.append(link('home','../../'));
    const controls=el('div','controls');
    for(const [label,delta]of[['A−',-.1],['A+',.1]]){const b=el('button');b.textContent=label;b.dataset.action=delta<0?'smaller':'larger';b.onclick=()=>{state.scale=Math.min(1.5,Math.max(.85,state.scale+delta));persist();document.documentElement.style.setProperty('--text-scale',state.scale);};controls.append(b);}
    const sound=el('button');sound.textContent=audio.enabled?'🔊':'🔇';sound.setAttribute('aria-label',audio.enabled?'關閉音效':'開啟音效');sound.dataset.action='sound';
    sound.onclick=()=>{audio.setEnabled(!audio.enabled);store.setSound(audio.enabled);sound.textContent=audio.enabled?'🔊':'🔇';sound.setAttribute('aria-label',audio.enabled?'關閉音效':'開啟音效');};controls.append(sound);h.append(controls);return h;
  }
  function packetTools(){
    const tools=el('details','packet-tools');const summary=el('summary');summary.append(text('current-code'));
    const code=el('code');code.textContent=state.code;summary.append(code);tools.append(summary);
    const bar=el('div','actions');bar.append(link('print',`print.html?code=${state.code}`,true),action('copy',async()=>{
      try{await navigator.clipboard.writeText(new URL(`?code=${state.code}`,location.href).href);modal('copied',[['close',()=>{}]]);}catch{modal('copy-failed',[['close',()=>{}]]);}
    }),action('change',()=>setupDialog()));tools.append(bar);return tools;
  }
  function setupForm(){
    const area=el('div','setup');area.append(line('code-help'));
    const form=el('form','code-form'),label=el('label');label.append(text('code'));
    const input=el('input');input.value=state.code;input.maxLength=24;input.autocomplete='off';input.autocapitalize='none';input.spellcheck=false;input.name='code';input.setAttribute('aria-label','題卷碼');label.append(input);
    const submit=el('button');submit.type='submit';submit.append(text('use-code'));submit.dataset.action='use-code';
    const error=el('p','feedback');error.setAttribute('role','alert');form.append(label,submit,error);
    form.onsubmit=event=>{event.preventDefault();const code=normalizeCode(input.value);if(!code){error.replaceChildren(text('invalid-code'));return;}closeDialog();changeCode(code);};
    area.append(form,action('new-code',()=>{closeDialog();changeCode(newCode());}),link('print',`print.html?code=${state.code}`,true));return area;
  }
  function setupDialog(){const d=modal('setup',[['cancel',()=>{}]]);d.insertBefore(setupForm(),d.lastChild);}
  function inventory(){
    const bag=el('div','inventory');
    if(state.wood){const wood=el('button','inventory-item');wood.dataset.item='wood';wood.innerHTML=star;wood.append(text('wood'));wood.disabled=state.placed;bag.append(wood);}
    if(state.seed&&!['ordinary','secret-home'].includes(state.scene)){const item=el('div','inventory-item');item.innerHTML=seed;item.append(text('seed'));bag.append(item);}
    return bag;
  }
  function nextScene(){return {gate1:'passage',gate2:'window',gate3:'chest'}[state.scene];}
  function hint(g,i){
    const q=worksheet.gates[g].questions[i],d=modal(q.op==='+'?'hint-add':'hint-subtract',[['close',()=>{}]]);
    const math=el('p','hint-math');math.textContent=`${q.id}.  ${q.a} ${q.op==='-'?'−':'+'} ${q.b} = ?`;d.prepend(math);
    const dots=el('div','hint-dots');
    const group=(n)=>{const tray=el('div','hint-group');for(let j=0;j<n;j++){const dot=el('button','count-dot');dot.textContent='●';dot.setAttribute('aria-label',String(j+1));dot.onclick=()=>{if(q.op==='-')dot.classList.toggle('crossed');};tray.append(dot);}return tray;};
    dots.append(group(q.a));if(q.op==='+'){const plus=el('b');plus.textContent='+';dots.append(plus,group(q.b));}d.insertBefore(dots,d.lastChild);
  }
  function gatePanel(g,panel,stage){
    if(state.solved[g]){panel.append(line('success'),action('continue',()=>go(nextScene())));stage.classList.add('unlocked');return;}
    const fields=el('div','answer-fields');fields.style.setProperty('--count',worksheet.gates[g].questions.length);
    const inputs=[];
    worksheet.gates[g].questions.forEach((q,i)=>{
      const column=el('div','answer-column'),label=el('label');label.textContent=String(q.id).padStart(2,'0');
      const input=el('input');input.inputMode='numeric';input.autocomplete='off';input.maxLength=1;input.pattern='[0-9]';input.value=state.entries[g][i];input.dataset.answer=i;input.setAttribute('aria-label',`第 ${q.id} 題`);
      input.onfocus=()=>{selected=i;inputs.forEach((n,j)=>n.classList.toggle('selected',j===i));};
      input.oninput=()=>{if(stale){input.value=state.entries[g][i];return;}input.value=input.value.replace(/[^0-9]/g,'').slice(-1);state.entries[g][i]=input.value;input.classList.remove('wrong');persist();};
      inputs.push(input);label.append(input);const help=el('button','hint-button');help.textContent='?';help.setAttribute('aria-label',`看看第 ${q.id} 題`);help.onclick=()=>hint(g,i);column.append(label,help);fields.append(column);
    });
    const keypad=el('div','keypad');
    for(let digit=0;digit<=9;digit++){const key=el('button');key.textContent=digit;key.dataset.digit=digit;key.onclick=()=>{const input=inputs[selected];input.value=String(digit);state.entries[g][selected]=String(digit);input.classList.remove('wrong');persist();selected=Math.min(inputs.length-1,selected+1);inputs.forEach((n,i)=>n.classList.toggle('selected',i===selected));};keypad.append(key);}
    keypad.append(action('erase',()=>{state.entries[g][selected]='';inputs[selected].value='';persist();}));
    const feedback=el('p','feedback');feedback.setAttribute('role','status');
    const check=action('check',()=>{
      const results=checkAnswers(worksheet,g,state.entries[g]);
      if(results.every(Boolean)){state.solved[g]=true;persist();void audio.playSfx('success');render();return;}
      inputs.forEach((input,i)=>input.classList.toggle('wrong',!results[i]));feedback.replaceChildren(text(state.entries[g].some(v=>v==='')?'empty':'incorrect'));void audio.playSfx('fail-soft');
    });
    inputs[selected].classList.add('selected');panel.append(line('answer-help'),fields,keypad,feedback,check);
  }
  function render(){
    cleanup();cleanup=()=>{};closeDialog();app.replaceChildren(header());
    document.documentElement.style.setProperty('--text-scale',state.scale);
    document.body.dataset.scene=state.scene;
    const main=el('main','book'),stage=stageFor(state.scene),panel=el('section','story-panel'),bar=el('div','actions');
    main.append(packetTools(),stage,panel);app.append(main);
    const scene=state.scene;
    const names={cover:'title',intro:'intro-title',passage:'passage-title',window:'window-title',chest:'chest-title',roof:'roof-title',ordinary:'ordinary-title',secret:'secret-title','secret-home':'ordinary-title'};
    panel.append(line(scene.startsWith('gate')?`${scene}-name`:names[scene],'h1'));
    const lines={cover:'cover-line',intro:'intro-line',passage:'passage-line',window:'window-line',chest:'chest-line',roof:'roof-line',ordinary:'ordinary-line',secret:'secret-line','secret-home':'secret-home-line'};
    panel.append(line(scene.startsWith('gate')?`${scene}-line`:lines[scene]));
    if(scene==='cover'){
      const start=action('start',()=>{void audio.unlock();go('intro');});start.className='primary';bar.append(start);panel.append(bar);
      const prep=el('details','prepare');const summary=el('summary');summary.append(text('setup'));prep.append(summary,setupForm());panel.append(prep);
    } else if(scene==='intro')bar.append(action('continue',()=>go('gate1')));
    else if(scene.startsWith('gate'))gatePanel(Number(scene.at(-1))-1,panel,stage);
    else if(scene==='passage')bar.append(action('continue',()=>go('gate2')));
    else if(scene==='window'){
      bar.append(action('upstairs',()=>go('gate3')));
      if(!state.wood){const wood=el('button','hidden-object');wood.dataset.action='find-wood';wood.setAttribute('aria-label','看看這裡');wood.innerHTML=star;place(wood,[79.5,71,5.3,7]);wood.onclick=()=>{state.wood=true;persist();render();reward('wood-found',()=>{});};stage.append(wood);}
    } else if(scene==='chest'){
      if(state.seed){panel.append(line('seed-found'));bar.append(action('continue',()=>go('roof')));}
      else {const open=action('open-chest',()=>{state.seed=true;persist();render();void audio.playSfx('found-item');});bar.append(open);}
    } else if(scene==='roof'){
      bar.append(action('go-home',()=>go('ordinary')));
      const target=el('div','wood-slot');place(target,[68.6,56.2,13.5,8.5]);stage.append(target);
      if(state.placed){target.innerHTML=star.replace('<svg','<svg preserveAspectRatio="none"');target.classList.add('placed');panel.append(line('placed'));bar.prepend(action('continue',()=>go('secret')));}
    } else if(scene==='secret')bar.append(action('continue',()=>go('secret-home')));
    else if(['ordinary','secret-home'].includes(scene))bar.append(action('replay',()=>modal('replay-confirm',[['yes-replay',()=>reset(state.code)],['cancel',()=>{}]])),link('home','../../'));
    if(scene!=='cover')panel.append(bar);
    const bag=inventory();if(bag.children.length)main.append(bag);
    if(scene==='roof'&&state.wood&&!state.placed){
      const source=bag.querySelector('[data-item="wood"]'),target=stage.querySelector('.wood-slot');
      const lock=()=>{if(state.placed)return;state.placed=true;persist();render();void audio.playSfx('drag-lock');};
      cleanup=bindDrag(source,target,lock);
      // Keyboard users discover the same recess after selecting the acquired item.
      source.addEventListener('keydown',event=>{if(event.key==='Enter'||event.key===' '){event.preventDefault();target.tabIndex=0;target.setAttribute('role','button');target.setAttribute('aria-label','星形凹槽');target.focus();}});
      target.addEventListener('keydown',event=>{if(event.key==='Enter'||event.key===' '){event.preventDefault();lock();}});
    }
    const note=el('p','storage-note');note.id='storage-note';if(blocked)note.append(text('storage-warning'));main.append(note);
  }
  render();
  const query=new URLSearchParams(location.search).get('code');
  if(query!==null){const code=normalizeCode(query);if(code)changeCode(code);else modal('invalid-code',[['close',()=>{}]]);}
  persist();document.body.dataset.ready='true';
} catch(error){app.textContent='暫時無法開啟故事，請重新整理。';console.error(error);}
