import {createWorksheet,normalizeCode,newCode,checkAnswers,DEFAULT_CONFIG,OPERATORS,operatorSign,answerCapacity,checkPasswords} from '../../engine/math-worksheet.js';
import {createStorage} from '../../engine/storage.js';
import {AudioManager} from '../../engine/audio-manager.js';
import {bindDrag,place} from '../../engine/interactions.js';
import {sceneLayers} from '../../engine/scene-layers.js';
import {mountCameraAction} from '../../engine/camera-action-panel.js';
import {fresh,validate,KEY} from './state.js';
import {loadText,button} from './text.js';
import {labelledSymbolMarkup,symbolName,codeLegend} from '../../engine/symbol-code.js';

const app=document.querySelector('#app');
const star=`<svg viewBox="0 0 100 100" aria-hidden="true"><path d="M50 5 62 35 95 38 70 60 78 94 50 76 22 94 30 60 5 38 38 35Z" fill="#a77a40" stroke="#594326" stroke-width="5"/><path d="m47 25 7 42m-21-17 34 9" stroke="#79562e" stroke-width="3"/></svg>`;
const seed=`<svg viewBox="0 0 100 100" aria-hidden="true"><ellipse cx="50" cy="57" rx="25" ry="34" fill="#ffda69" stroke="#97702d" stroke-width="4"/><path d="M49 55Q35 20 66 10Q76 35 49 55" fill="#89b879" stroke="#416d43" stroke-width="4"/></svg>`;
try {
  const text=await loadText();
  const store=createStorage('story-03',()=>fresh(newCode()),validate);
  let state=store.load(), worksheet=createWorksheet(state.code), selected=0, cleanup=()=>{}, stale=false;
  let expectedCode=state.code, blocked=false;
  const manifest=Object.fromEntries(['found-item','success','fail-soft','drag-lock'].map(id=>[id,{category:'sfx',available:true,src:`../story-02/assets/audio/sfx/${id}.wav`,volume:.48}]));
  let audio=new AudioManager(manifest,import.meta.url,store.sound());
  const el=(tag,cls='')=>{const node=document.createElement(tag);node.className=cls;return node;};
  const action=(id,handler,name=id)=>button(text,id,handler,name);
  const line=(id,tag='p')=>{const n=el(tag);n.append(text(id));return n;};
  const link=(id,url,blank=false)=>{const n=el('a');n.href=url;n.append(text(id));if(blank){n.target='_blank';n.rel='noopener';}return n;};
  function persist(){const ok=store.save(state);if(!ok){blocked=true;document.querySelector('#storage-note')?.replaceChildren(text('storage-warning'));}return ok;}
  function go(scene){if(scene!=='cover')state.resumeScene=null;state.scene=scene;selected=0;persist();render();window.scrollTo({top:0,behavior:'instant'});}
  function closeDialog(){document.querySelector('dialog')?.close();document.querySelector('dialog')?.remove();}
  function modal(label,buttons){
    closeDialog();const d=el('dialog');d.append(line(label));const bar=el('div','actions');
    for(const [id,fn] of buttons)bar.append(action(id,()=>{closeDialog();fn();}));d.append(bar);document.body.append(d);d.showModal();return d;
  }
  function reward(label,next,sfx='found-item'){void audio.playSfx(sfx);modal(label,[['continue',next]]);}
  function reset(code){state=fresh(code);selected=0;expectedCode=code;worksheet=createWorksheet(code);persist();stale=false;history.replaceState(null,'',`?code=${code}`);render();}
  function changeCode(code){
    if(code===state.code)return;
    const progressed=state.scene!=='cover'||state.entries.some(row=>row.some(v=>v!==''))||state.passwords.some(row=>row.some(v=>v!==''));
    if(progressed)modal('confirm-change',[['yes-change',()=>reset(code)],['cancel',()=>{}]]);else reset(code);
  }
  function staleWarning(){if(stale)return;stale=true;cleanup();modal('stale',[['reload',()=>location.replace('./')]]);}
  document.addEventListener('click',event=>{
    if(event.target.closest('dialog'))return;
    try {const saved=JSON.parse(localStorage.getItem(KEY));if(saved&&saved.code!==expectedCode){event.preventDefault();event.stopImmediatePropagation();staleWarning();}}
    catch{/* Storage denial falls back to this tab's memory. */}
  },true);
  window.addEventListener('storage',event=>{if(event.key===KEY&&event.newValue){try{if(JSON.parse(event.newValue).code!==expectedCode)staleWarning();}catch{}}});
  document.addEventListener('visibilitychange',()=>audio.setHidden(document.hidden));
  document.addEventListener('pointerdown',()=>{if(state.scene!=='cover'&&!audio.unlocked)void audio.unlock();});
  window.addEventListener('pagehide',()=>{cleanup();audio.dispose();});
  window.addEventListener('pageshow',event=>{if(event.persisted){audio=new AudioManager(manifest,import.meta.url,store.sound());render();}});
  const imageURL=new URL('./assets/images/',import.meta.url);
  function stageFor(scene){
    const forest=['cover','intro','ordinary','secret-home'].includes(scene);
    const roof=['catch','chest','roof','secret'].includes(scene);
    const courtyard=['balance','jump'].includes(scene);
    const layers=[{id:'atong',src:'atong.png',box:[12,35,20,49],z:3},{id:'squirrel',src:'squirrel.png',box:[30,61,11,23],z:4}];
    if(roof){layers[0].box=[8,37,19,49];layers[1].box=[26,63,10,23];}
    if(courtyard){layers[0].src=`atong-${scene}.png`;layers[0].box=scene==='balance'?[33,28,27,59]:[49,18,25,57];layers[1].box=scene==='balance'?[65,60,13,27]:[21,56,14,28];}
    if(scene==='catch'){layers[0].src='atong-catch.png';layers[0].box=[25,26,27,61];layers[1].box=[57,60,13,27];}
    if(scene==='passage'){layers[0].box=[32,37,18,45];layers[1].box=[51,63,10,22];}
    if(scene==='window'){layers[0].box=[59,35,20,49];layers[1].box=[42,60,11,23];}
    if(scene==='gate2'){layers[0].box=[65,36,20,49];layers[1].box=[18,58,12,26];}
    if(scene==='gate3'){layers[0].box=[18,29,24,59];layers[1].box=[61,60,13,26];}
    if(scene.startsWith('gate')&&!state.solved[Number(scene.at(-1))-1])layers.unshift({id:'door',src:scene==='gate1'?'door-stone.png':'door.png',box:[38.6,17.5,22.3,55.2],z:1});
    if(scene==='chest')layers.unshift({id:'chest',src:state.seed?'chest-open.png':'chest.png',box:state.seed?[30,37,27,42]:[31,45,24,33],z:2});
    const stage=sceneLayers({background:forest?'forest-bg.png':roof?'roof-bg.png':courtyard?'courtyard-bg.png':'tower-bg.png',layers,baseURL:imageURL});
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
    const h=el('header','toolbar'),nav=el('nav','story-navigation');nav.append(link('home','../../'));
    if(state.scene!=='cover')nav.append(action('story-menu',()=>{state.resumeScene=state.scene;go('cover');}));h.append(nav);
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
    const input=el('input');input.value=state.code;input.maxLength=40;input.autocomplete='off';input.autocapitalize='none';input.spellcheck=false;input.name='code';input.setAttribute('aria-label','題卷碼');label.append(input);
    const submit=el('button');submit.type='submit';submit.append(text('use-code'));submit.dataset.action='use-code';
    const error=el('p','feedback');error.setAttribute('role','alert');form.append(label,submit,error);
    form.onsubmit=event=>{event.preventDefault();const code=normalizeCode(input.value);if(!code){error.replaceChildren(text('invalid-code'));return;}closeDialog();changeCode(code);};
    const settings=el('div','difficulty-settings');settings.append(line('difficulty-help'));
    const config=structuredClone(worksheet.config||DEFAULT_CONFIG);
    config.forEach((c,g)=>{
      const field=el('fieldset','gate-settings');field.dataset.gate=g;const legend=el('legend');legend.append(text(`gate${g+1}-label`));field.append(legend);
      const limits=el('div','operand-settings');
      const within=el('input');within.type='checkbox';within.checked=c.within10;within.name=`within-${g}`;
      const withinLabel=el('label','within-setting');withinLabel.append(within,text('within-ten'));
      for(const [key,labelId]of[['leftDigits','first-number'],['rightDigits','second-number']]){
        const label=el('label');label.append(text(labelId));const select=el('select');select.name=`${key}-${g}`;
        select.setAttribute('aria-label',`${g+1}：${key==='leftDigits'?'前':'後'}一個數的位數`);
        for(const value of[1,2]){const option=el('option');option.value=value;option.textContent=value;select.append(option);}select.value=c[key];
        select.onchange=()=>{c[key]=Number(select.value);const available=c.leftDigits===1&&c.rightDigits===1;within.disabled=!available;if(!available){c.within10=false;within.checked=false;}};
        label.append(select,text('digits'));limits.append(label);
      }
      within.disabled=c.leftDigits!==1||c.rightDigits!==1;within.onchange=()=>{c.within10=within.checked;};
      const operations=el('div','operation-settings');
      for(const op of OPERATORS){const label=el('label'),check=el('input');check.type='checkbox';check.value=op;check.name=`ops-${g}`;check.checked=c.ops.includes(op);check.setAttribute('aria-label',`第 ${g+1} 關 ${operatorSign(op)}`);check.onchange=()=>{c.ops=OPERATORS.filter(v=>[...operations.querySelectorAll('input:checked')].some(n=>n.value===v));};const sign=el('span');sign.textContent=operatorSign(op);label.append(check,sign);operations.append(label);}
      field.append(limits,operations,withinLabel);settings.append(field);
    });
    const settingsError=el('p','feedback');settingsError.setAttribute('role','alert');
    area.append(form,settings,settingsError,action('new-code',()=>{
      let code;try{code=newCode(config);}catch{settingsError.replaceChildren(text('settings-error'));return;}
      closeDialog();changeCode(code);
    }),link('print',`print.html?code=${state.code}`,true));return area;
  }
  function setupDialog(){const d=modal('setup',[['cancel',()=>{}]]);d.insertBefore(setupForm(),d.lastChild);}
  function inventory(){
    const bag=el('div','inventory');
    if(state.wood){const wood=el('button','inventory-item');wood.dataset.item='wood';wood.innerHTML=star;wood.append(text('wood'));wood.disabled=state.placed;bag.append(wood);}
    if(state.seed&&!['ordinary','secret-home'].includes(state.scene)){const item=el('div','inventory-item');item.innerHTML=seed;item.append(text('seed'));bag.append(item);}
    return bag;
  }
  function nextScene(){return {gate1:'passage',gate2:'window',gate3:'catch'}[state.scene];}
  function paintNumber(node,value){
    node.replaceChildren();node.dataset.value=value;
    if(value==='')node.append(text('tap-symbols'));
    else node.innerHTML=[...value].map(labelledSymbolMarkup).join('');
  }
  function symbolKeypad(enter){
    const keypad=el('div','keypad');
    for(let digit=0;digit<=9;digit++){
      const key=el('button','symbol-key');key.innerHTML=labelledSymbolMarkup(digit);
      key.setAttribute('aria-label',`${digit}，${symbolName(digit)}`);key.dataset.digit=digit;key.onclick=()=>enter(String(digit));keypad.append(key);
    }
    return keypad;
  }
  function appendDigit(value,digit,capacity){
    const next=(value==='0'?'':value)+digit;
    return next.length<=capacity?next:null;
  }
  function reviewQuestion(g,i=0){
    const gate=worksheet.gates[g],q=gate.questions[i],d=modal('review-title',[['close',()=>{}]]);
    const body=el('div','question-review');d.insertBefore(body,d.lastChild);
    const label=el('label','review-picker');label.append(text('question-number'));
    const picker=el('select');picker.setAttribute('aria-label','要檢查的題號');picker.name='review-question';
    gate.questions.forEach((question,index)=>{const option=el('option');option.value=index;option.textContent=question.id;picker.append(option);});
    picker.value=i;picker.onchange=()=>reviewQuestion(g,Number(picker.value));label.append(picker);
    const math=el('p','hint-math');math.textContent=`${q.a} ${operatorSign(q.op)} ${q.b} = ?`;
    const input=el('div','number-entry review-entry');input.setAttribute('role','group');input.setAttribute('aria-label','這題的答案');
    const feedback=el('p','review-feedback');feedback.setAttribute('role','status');
    const paint=()=>{
      paintNumber(input,state.entries[g][i]);feedback.replaceChildren();
      if(state.checked[g][i]){
        const correct=checkAnswers(worksheet,g,state.entries[g])[i];feedback.className=`review-feedback ${correct?'correct':'wrong'}`;
        feedback.append(correct?'✓ ':'× ',text(correct?'review-correct':'review-incorrect'));
      }
    };
    const edit=value=>{state.entries[g][i]=value;state.checked[g][i]=false;persist();paint();};
    const keypad=symbolKeypad(digit=>{
      const value=appendDigit(state.entries[g][i],digit,answerCapacity(gate));
      if(value===null){feedback.replaceChildren(text('entry-limit'));return;}edit(value);
    });
    const controls=el('div','actions');controls.append(action('erase',()=>edit(state.entries[g][i].slice(0,-1))),action('clear-answer',()=>edit('')),
      action('check-question',()=>{state.checked[g][i]=true;persist();paint();}),action('next-answer',()=>reviewQuestion(g,(i+1)%gate.questions.length)));
    const help={'+':'hint-place-add','-':'hint-place-subtract','*':'hint-multiply','/':'hint-divide'}[q.op];
    body.append(line('review-help'),label,math,input,keypad,controls,feedback,line(help));paint();
  }
  function gatePanel(g,panel,stage){
    const capacity=answerCapacity(worksheet.gates[g]),fields=el('div','password-fields'),cards=[],inputs=[];
    const labels=['maximum-answer','minimum-answer'];selected=Math.min(selected,1);
    const select=i=>{selected=i;inputs.forEach((node,j)=>{node.classList.toggle('selected',j===i);node.setAttribute('aria-pressed',String(j===i));});};
    const paint=i=>{
      const value=state.passwords[g][i],checked=state.passwordChecked[g][i],correct=checkPasswords(worksheet,g,state.passwords[g])[i];
      paintNumber(inputs[i],value);inputs[i].setAttribute('aria-label',`${i===0?'最大':'最小'}答案：${value||'尚未輸入'}${checked?(correct?'，正確':'，再看看'):''}`);
      cards[i].classList.toggle('correct',checked&&correct);cards[i].classList.toggle('wrong',checked&&!correct);
      cards[i].querySelector('.answer-mark').textContent=checked?(correct?'✓':'×'):'';
    };
    labels.forEach((label,i)=>{
      const card=el('div','password-card'),heading=el('div','answer-heading');heading.append(text(label));
      const mark=el('span','answer-mark');mark.setAttribute('aria-hidden','true');heading.append(mark);
      const input=el('button','number-entry');input.type='button';input.dataset.answer=i;input.disabled=state.solved[g];input.onclick=()=>select(i);
      card.append(heading,input);cards.push(card);inputs.push(input);fields.append(card);paint(i);
    });
    panel.append(line('password-help'),fields);
    if(state.solved[g]){panel.append(line('success'),action('continue',()=>go(nextScene())));stage.classList.add('unlocked');return;}
    const legend=el('details','on-screen-legend'),summary=el('summary');summary.append(text('code-table'));legend.append(summary,codeLegend());
    const feedback=el('p','feedback');feedback.setAttribute('role','status');
    const message=()=>state.passwords[g].some(v=>v==='')?'password-empty':'password-incorrect';
    if(state.passwordChecked[g].some(Boolean))feedback.append(text(message()));
    const edit=value=>{state.passwords[g][selected]=value;state.passwordChecked[g][selected]=false;paint(selected);feedback.replaceChildren();persist();};
    const keypad=symbolKeypad(digit=>{
      const value=appendDigit(state.passwords[g][selected],digit,capacity);
      if(value===null){feedback.replaceChildren(text('entry-limit'));return;}edit(value);
    });
    const controls=el('div','actions');controls.append(action('erase',()=>edit(state.passwords[g][selected].slice(0,-1))),action('clear-answer',()=>edit('')),
      action('check',()=>{
        const results=checkPasswords(worksheet,g,state.passwords[g]);state.passwordChecked[g].fill(true);
        if(results.every(Boolean)){state.solved[g]=true;persist();void audio.playSfx('success');render();return;}
        persist();cards.forEach((_,i)=>paint(i));feedback.replaceChildren(text(message()));void audio.playSfx('fail-soft');
      }));
    const dock=el('div','symbol-dock');dock.append(keypad,controls);
    panel.append(legend,dock,feedback,action('review-questions',()=>reviewQuestion(g)));select(selected);
  }
  function render(){
    cleanup();cleanup=()=>{};closeDialog();app.replaceChildren(header());
    document.documentElement.style.setProperty('--text-scale',state.scale);
    document.body.dataset.scene=state.scene;
    const main=el('main','book'),stage=stageFor(state.scene),panel=el('section','story-panel'),bar=el('div','actions');
    main.append(packetTools(),stage,panel);app.append(main);
    const scene=state.scene;
    const names={cover:'title',intro:'intro-title',passage:'passage-title',window:'window-title',chest:'chest-title',roof:'roof-title',ordinary:'ordinary-title',secret:'secret-title','secret-home':'ordinary-title'};
    const physical=['balance','jump','catch'].includes(scene);
    panel.append(line(physical?`${scene}-title`:scene.startsWith('gate')?`${scene}-name`:names[scene],'h1'));
    const lines={cover:'cover-line',intro:'intro-line',passage:'passage-line',window:'window-line',chest:'chest-line',roof:'roof-line',ordinary:'ordinary-line',secret:'secret-line','secret-home':'secret-home-line'};
    panel.append(line(physical?`${scene}-line`:scene.startsWith('gate')?`${scene}-line`:lines[scene]));
    if(scene==='cover'){
      const start=action(state.resumeScene?'resume':'start',()=>{void audio.unlock();go(state.resumeScene||'intro');});start.className='primary';bar.append(start);panel.append(bar);
      const prep=el('details','prepare');const summary=el('summary');summary.append(text('setup'));prep.append(summary,setupForm());panel.append(prep);
    } else if(scene==='intro')bar.append(action('continue',()=>go('gate1')));
    else if(scene.startsWith('gate'))gatePanel(Number(scene.at(-1))-1,panel,stage);
    else if(physical){
      cleanup=mountCameraAction(panel,{kind:scene,text,button,completed:state.actions[scene],
        onComplete:()=>{state.actions[scene]=true;persist();void audio.playSfx('success');},
        onContinue:()=>go({balance:'gate2',jump:'gate3',catch:'chest'}[scene])});
    }
    else if(scene==='passage')bar.append(action('continue',()=>go('balance')));
    else if(scene==='window'){
      bar.append(action('upstairs',()=>go('jump')));
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
