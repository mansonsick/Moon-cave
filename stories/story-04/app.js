import {createStorage} from '../../engine/storage.js';
import {AudioManager} from '../../engine/audio-manager.js';
import {bindDrag,place} from '../../engine/interactions.js';
import {sceneLayers} from '../../engine/scene-layers.js';
import {newReadingCode,normalizeReadingCode,readingWorksheet} from '../../engine/reading-worksheet.js';
import {fresh,validate,passed} from './state.js';
import {loadText,button} from './text.js';

const root=document.querySelector('#app'),baseURL=new URL('./',import.meta.url);
const el=(tag,cls='')=>{const n=document.createElement(tag);n.className=cls;return n;};
async function boot() {
  const response=await fetch(new URL('./story.json',import.meta.url));if(!response.ok)throw new Error('Missing story');
  const config=await response.json(),text=await loadText();
  const initialCode=newReadingCode(),storage=createStorage('story-04',()=>fresh(initialCode),value=>validate(config,value));
  let state=storage.load(),sheet=readingWorksheet(config,state.code),view='menu',phase='learn',cleanups=[],selectedItem=false;
  const incoming=new URL(location.href).searchParams.get('code');let requested=incoming||state.code,invalidIncoming=Boolean(incoming&&!normalizeReadingCode(incoming));
  if(incoming&&normalizeReadingCode(incoming)&&incoming!==state.code&&state.scene==='S01') {state=fresh(normalizeReadingCode(incoming));sheet=readingWorksheet(config,state.code);storage.save(state);}
  const audio=new AudioManager(config.audio,baseURL,storage.sound());let started=false;
  const save=()=>storage.save(state),isPassed=i=>passed(config,state,i);
  function clear(){cleanups.splice(0).forEach(fn=>fn());audio.stopSfx();selectedItem=false;root.replaceChildren();}
  const btn=(label,click,action=label)=>button(text,label,click,action);
  const paragraph=(parent,key,cls='')=>{const p=el('p',cls);p.append(text(key));parent.append(p);return p;};
  function href(label,url){const a=el('a','link-button');a.href=url;a.append(text(label));return a;}
  function updateURL(){const url=new URL(location.href);url.searchParams.set('code',state.code);history.replaceState({},'',url);}
  function controls() {
    const nav=el('nav','toolbar');nav.setAttribute('aria-label','閱讀工具');nav.append(href('home','../../'));
    if(view!=='menu')nav.append(btn('menu',()=>{view='menu';render();}));
    for(const [symbol,delta,label] of [['A−',-.1,'縮小文字'],['A+',.1,'放大文字']]) {
      const b=el('button','font-control');b.type='button';b.textContent=symbol;b.setAttribute('aria-label',label);
      b.addEventListener('click',()=>{state.scale=Math.max(.85,Math.min(1.5,+(state.scale+delta).toFixed(2)));save();root.style.setProperty('--scale',state.scale);});nav.append(b);
    }
    const sound=el('button','font-control');sound.type='button';sound.dataset.action='sound';
    const soundState=()=>{sound.textContent=audio.enabled?'🔊':'🔇';sound.setAttribute('aria-label',audio.enabled?'關閉音效':'開啟音效');sound.setAttribute('aria-pressed',String(audio.enabled));};
    soundState();sound.addEventListener('click',()=>{audio.setEnabled(!audio.enabled);storage.setSound(audio.enabled);soundState();if(started&&audio.enabled)void audio.unlock();});nav.append(sound);root.append(nav);
  }
  function dialog(label,confirm,confirmLabel='yes-replay') {
    const wrap=el('div','dialog-wrap'),box=el('section','dialog');box.setAttribute('role','dialog');box.setAttribute('aria-modal','true');box.setAttribute('aria-label',config.labels[label]);
    paragraph(box,label);const actions=el('div','actions');const cancel=btn('cancel',()=>{wrap.remove();trigger?.focus();});
    const trigger=document.activeElement,yes=btn(confirmLabel,()=>{wrap.remove();confirm();});actions.append(cancel,yes);box.append(actions);wrap.append(box);root.append(wrap);cancel.focus();
    wrap.addEventListener('keydown',event=>{if(event.key==='Escape'){wrap.remove();trigger?.focus();}if(event.key==='Tab'){event.preventDefault();(document.activeElement===cancel?yes:cancel).focus();}});
  }
  function changeCode(code) {
    if(!normalizeReadingCode(code))return false;
    invalidIncoming=false;
    const apply=()=>{state=fresh(code);sheet=readingWorksheet(config,code);save();requested=code;updateURL();view='menu';render();};
    if(code===state.code){requested=code;return true;}
    if(state.scene==='S01'&&!state.learned.some(Boolean))apply();else dialog('change-help',apply,'apply-code');
    return true;
  }
  function menu(main) {
    main.append(stageFor(config.scenes.S01,'S01'));
    const panel=el('section','cover-tools');paragraph(panel,'learn-stages');paragraph(panel,'paper-help');paragraph(panel,'no-printer','small-help');
    const row=el('div','code-row'),label=el('label');label.htmlFor='code-input';label.append(text('code'));const input=el('input');input.id='code-input';input.value=requested;
    input.autocomplete='off';input.autocapitalize='none';input.spellcheck=false;input.setAttribute('aria-label','題卷碼');input.maxLength=32;
    const warn=el('div');warn.setAttribute('role','status');const apply=btn('apply-code',()=>{if(!changeCode(normalizeReadingCode(input.value))){warn.replaceChildren(text('bad-code'));}else warn.replaceChildren();});
    input.addEventListener('keydown',e=>{if(e.key==='Enter'){e.preventDefault();apply.click();}});row.append(label,input,apply);
    panel.append(row);paragraph(panel,'code-help','small-help');panel.append(warn);
    if(invalidIncoming)warn.append(text('bad-code'));
    const actions=el('div','actions');actions.append(btn('new-paper',()=>changeCode(newReadingCode())),href('paper','./print.html?code='+state.code),href('answers','./print.html?answers=1&code='+state.code));
    actions.append(btn(state.scene==='S01'?'start':'resume',()=>{started=true;if(audio.enabled)void audio.unlock();view='story';phase='learn';render();},'start-adventure'));
    if(state.scene!=='S01')actions.append(btn('replay',()=>dialog('reset-help',()=>{state=fresh(state.code);save();render();})));
    panel.append(actions);main.append(panel);
  }
  function go(scene) {state.scene=scene;if(['E01','E03'].includes(scene)){state.badge=true;state.ending=scene==='E01'?'ordinary':'secret';}save();phase='learn';view='story';render();}
  function prop(stage,name,box,cls='') {
    const art=config.props?.[name],n=el('div','scene-prop '+cls+(art?' painted-prop':''));n.dataset.prop=name;
    place(n,box);const img=el('img');img.src=art?'./assets/images/props/'+art.src:'./assets/practice/'+name+'.svg';img.alt='';
    // Position the painted silhouette, including its alpha margin, on the surface.
    if(art){const [x,y,w,h]=art.crop;Object.assign(img.style,{left:(-x/w*100)+'%',top:(-y/h*100)+'%',width:(100/w)+'%',height:(100/h)+'%'});}
    n.append(img);stage.append(n);return n;
  }
  function stageText(stage,label,box,cls=''){const n=el('div','scene-label '+cls);n.dataset.label=label;place(n,box);n.append(text.scene(label));stage.append(n);return n;}
  function notice(stage,label,box){
    prop(stage,'note-paper',box,'notice-paper');
    const [x,y,w,h]=box;stageText(stage,label,[x+w*.1,y+h*.14,w*.8,h*.74],'scene-note');
  }
  function stageFor(scene,id) {
    let pose=scene.pose,box=[...scene.actorBox];
    if(id==='S05'&&state.delivered[0]){pose='atong-walking.png';box=[32,23,26,72];}
    if(id==='S07'&&state.delivered[1]){pose='atong-walking.png';box=[15,23,25,73];}
    if(id==='S10'&&state.delivered[2]){pose='atong-walking.png';box=[25,20,25,73];}
    const layers=[{id:'atong',src:'assets/images/'+pose,box,z:3},{id:'squirrel',src:'assets/images/squirrel-pointing.png',box:[Math.max(2,box[0]-15),62,18,30],z:4}];
    if(id==='S05')layers.push({id:'rabbit',src:'assets/images/rabbit.png',box:[58,34,17,53],z:3});
    if(id==='S07')layers.push({id:'bear',src:'assets/images/bear.png',box:[38,17,20,67],z:3});
    if(['S09','S10'].includes(id))layers.push({id:'bird',src:'assets/images/bird.png',box:state.delivered[2]?[63,49,12,18]:[70,17,13,20],z:3});
    if(['E01','E03'].includes(id))layers.push({id:'rabbit',src:'assets/images/rabbit.png',box:[62,45,13,44],z:3},{id:'bear',src:'assets/images/bear.png',box:[77,27,18,62],z:3},{id:'bird',src:'assets/images/bird.png',box:[69,62,12,18],z:4});
    if(id==='E03')layers.push({id:'mouse',src:'assets/images/mouse-postman.png',box:[5,36,23,53],z:4});
    const stage=sceneLayers({background:'assets/images/'+scene.background,layers,baseURL,label:config.labels[scene.title]});
    if(['S01','S02'].includes(id))for(let i=0;i<3;i++)prop(stage,'envelope',id==='S01'?[60+i*6.3,50.1+i*.4,5.1,2.1]:[57+i*10,52-i*.1,7,2.7]);
    if(['S01','S02','S03'].includes(id)){
      const photo=el('img','scene-layer photo');photo.src='./assets/images/anchor.png';photo.alt='';place(photo,id==='S01'?[77,23,11,12]:[76,21,10,16]);stage.append(photo);
    }
    if(id==='S03'&&isPassed(0))for(const [i,qid] of ['Q01','Q02','Q05'].entries()){
      const card=[54+i*13,41,11,13];prop(stage,'wood-card',card);stageText(stage,config.questions.find(q=>q.id===qid).answer,card,'sign-card');
    }
    if(id==='S04'){stageText(stage,config.questions[0].answer,[46,27,5,7.5]);stageText(stage,config.questions[4].answer,[64,27,5,7.5]);}
    if(id==='S05'){notice(stage,'sign-note',[71.5,30,18,24]);if(state.delivered[0])prop(stage,'envelope',[74,68.5,6.5,2.5]);}
    if(id==='S07'){notice(stage,'bear-note',[81,21,18,24]);if(state.delivered[1])prop(stage,'envelope',[70,54,8.5,4]);}
    if(id==='H01')prop(stage,'leaf-marked',[76,13,15,25]);
    if(id==='S08'&&!state.leaf)prop(stage,'leaf',[15,80,4,5]);
    if(['S09','S10'].includes(id))notice(stage,'bird-note',[72,32,18,24]);
    if(id==='S10'&&state.delivered[2])prop(stage,'envelope',[75,69.2,8,3]);
    if(['S11','E02'].includes(id)&&state.placed)prop(stage,'leaf',id==='S11'?[75,39,6,11]:[68,39,6,11],'placed-leaf');
    if(id==='E02')notice(stage,'secret-note',[4,8,18,24]);
    if(['E01','E03'].includes(id)){
      // Each pose has its own chest anchor, away from straps, arms and the bag.
      const [cx,cy]=id==='E03'?[.56,.49]:[.632,.467],width=box[2]*.065,height=width*1672/941;
      prop(stage,'badge',[box[0]+box[2]*cx-width/2,box[1]+box[3]*cy-height/2,width,height],'shirt-badge');
    }
    return stage;
  }
  function hotspot(stage,label,box,action,id=label,hidden=false){const b=hidden?el('button','hotspot hidden-hotspot'):btn(label,action,id);b.type='button';b.dataset.action=id;b.classList.add('hotspot');if(hidden){b.setAttribute('aria-label',label);b.addEventListener('click',action);}place(b,box);stage.append(b);return b;}
  function reward(panel,label,next) {const n=el('section','reward');paragraph(n,label);n.append(btn('continue',()=>go(next)));panel.append(n);}
  function inventory(main) {
    if(state.scene==='S01')return null;const n=el('aside','inventory');n.setAttribute('aria-label','郵差包');
    const bagIcon=el('img');bagIcon.src='./assets/practice/mailbag.svg';bagIcon.alt='';bagIcon.className='bag-icon';n.append(bagIcon);
    const info=el('div');info.append(text('letters'));const count=el('strong','plain-symbol');count.textContent=' '+state.delivered.filter(Boolean).length+' / 3';info.append(count);n.append(info);
    if(state.leaf){const leaf=btn('leaf-name',()=>{selectedItem=true;},'select-leaf');leaf.className='item draggable';const img=el('img');img.src='./assets/practice/leaf.svg';img.alt='';leaf.prepend(img);leaf.dataset.item='leaf';n.append(leaf);}
    if(state.badge){const badge=el('div','item');const img=el('img');img.src='./assets/images/props/badge-painted.png';img.alt='';badge.append(img,text('badge'));n.append(badge);}
    main.append(n);return n;
  }
  function teach(panel,stage) {
    const entries=config.learning[stage],index=state.learning[stage],card=entries[index];paragraph(panel,'learn');paragraph(panel,'learn-help','small-help');
    const counter=el('div','counter');counter.textContent=`${index+1} / ${entries.length}`;panel.append(counter);
    const frame=el('section','learning-card'),visual=el('div','learning-visual'+(card.shape?'':' contextual-learning'));
    if(card.shape){
      for(const [picture,caption] of [[card.picture,'card-picture'],[card.shape,'card-shape']]){
        const part=el('div');const img=el('img','picture');img.src='./assets/practice/'+picture+'.svg';img.alt=config.labels[card.word];part.append(img,text(caption,'caption'));visual.append(part);
      }
    }else{
      const part=el('div','context-picture');const img=el('img','picture'+(card.illustration?' illustration':''));
      img.src=card.illustration?'./assets/images/cards/'+card.illustration:'./assets/practice/'+card.picture+'.svg';img.alt=config.labels[card.help];part.append(img);visual.append(part);
    }
    const word=el('div');word.append(text(card.word,'word'),text('card-read','caption'));visual.append(word);frame.append(visual);paragraph(frame,card.help,'card-help');panel.append(frame);
    const actions=el('div','actions');if(index>0)actions.append(btn('previous-card',()=>{state.learning[stage]--;save();render();}));
    if(index<entries.length-1)actions.append(btn('next-card',()=>{state.learning[stage]++;save();render();}));
    else actions.append(btn('learn-done',()=>{state.learned[stage]=true;save();phase='practice';render();}));
    if(state.learned[stage])actions.append(btn('practice',()=>{phase='practice';render();},'back-practice'));
    panel.append(actions);
  }
  function practice(panel,stage) {
    paragraph(panel,state.full[stage]?'practice':'representative');if(!state.full[stage])paragraph(panel,'not-all','small-help');
    const mode=el('div','actions');mode.append(btn('review',()=>{phase='learn';state.learning[stage]=0;save();render();}));
    if(!isPassed(stage))mode.append(btn(state.full[stage]?'two-mode':'all-mode',()=>{state.full[stage]=!state.full[stage];save();render();}));panel.append(mode);
    const questions=sheet.stages[stage].filter(q=>state.full[stage]||config.representatives[stage].includes(q.id));
    for(const q of questions) {
      const field=el('fieldset','question');field.dataset.question=q.id;const legend=el('legend');legend.textContent=q.id;field.append(legend);
      if(q.passage)paragraph(field,q.passage,'passage');if(q.illustration||q.picture){const image=el('img','question-picture'+(q.illustration?' illustration':''));image.src=q.illustration?'./assets/images/cards/'+q.illustration:'./assets/practice/'+q.picture+'.svg';image.alt=config.labels[q.passage||q.prompt];field.append(image);}
      paragraph(field,q.prompt);const choices=el('div','choices');
      q.choices.forEach((choice,i)=>{const label=el('label','choice'),input=el('input');input.type='radio';input.name=q.id;input.value=choice;input.checked=state.answers[q.id]===choice;input.disabled=isPassed(stage);
        input.addEventListener('change',()=>{state.answers[q.id]=choice;state.checked=state.checked.filter(id=>id!==q.id);save();render();});
        const code=el('span','choice-code');code.textContent='ABC'[i];label.append(input,code,text(choice));choices.append(label);});field.append(choices);
      if(state.checked.includes(q.id)){const answered=Boolean(state.answers[q.id]),correct=state.answers[q.id]===q.answer;field.classList.add(correct?'correct':answered?'incorrect':'incomplete');const feedback=el('div','feedback');const mark=el('strong');mark.textContent=correct?'✓':answered?'↻':'○';feedback.append(mark,text(correct?'correct':answered?'try':'empty-answer'));field.append(feedback);
        if(!correct){paragraph(field,q.hint,'small-help');field.append(btn('review',()=>{const cards=[0,1,2,3,4,5,0,1,2,3,4,5,0,0,1,2,3,4,4,4];state.learning[stage]=cards[Number(q.id.slice(1))-1];phase='learn';save();render();},'review-'+q.id));}}
      const hint=btn('hint',()=>{if(!field.querySelector('.question-hint'))paragraph(field,q.hint,'question-hint');});field.append(hint);panel.append(field);
    }
    if(isPassed(stage)){reward(panel,stage===0?'stage-ready':'station-done',['S04','S07','S10'][stage]);return;}
    const actions=el('div','actions');actions.append(btn('check',()=>{for(const q of questions)if(!state.checked.includes(q.id))state.checked.push(q.id);save();const complete=isPassed(stage);render();audio.playSfx(complete?'success':'fail-soft');}));
    actions.append(btn('together',()=>dialog('adult-help',()=>{state.learned[stage]=true;state.assisted[stage]=true;save();render();audio.playSfx('success');},'adult-confirm'),'parent-confirm'));
    // An adult confirmation is stored as assistance, not fabricated correct answers.
    panel.append(actions);
  }
  function story(main) {
    const id=state.scene,scene=config.scenes[id];root.dataset.scene=id;
    const heading=el('h2');heading.append(text(scene.title));main.append(heading);const stage=stageFor(scene,id);main.append(stage);
    const body=el('section','reading');(id==='S10'&&!state.delivered[2]?['bird-note']:scene.lines).forEach(key=>paragraph(body,key));main.append(body);const bag=inventory(main),panel=el('section','panel');main.append(panel);
    const actions=el('div','actions');panel.append(actions);
    if(id==='S01')hotspot(stage,'into-office',[60,76,30,17],()=>go('S02'));
    else if(id==='S02'){actions.append(href('paper','./print.html?code='+state.code),btn('prepared',()=>go('S03')));}
    else if(['S03','S06','S09'].includes(id)){
      const which={S03:0,S06:1,S09:2}[id];if(isPassed(which)){const review=btn('word-cards',()=>{phase='review';state.learning[which]=0;save();render();});actions.append(review);
        if(phase==='review')teach(panel,which);else reward(panel,which===0?'stage-ready':'station-done',['S04','S07','S10'][which]);
      }else if(phase==='learn'||!state.learned[which])teach(panel,which);else practice(panel,which);
      if(isPassed(which)&&which>0)paragraph(panel,which===1?'bear-note':'bird-note');
      if(id==='S06')paragraph(panel,'clap-break','small-help');
    }
    else if(id==='S04'){
      hotspot(stage,'mountain-road',[38,76,23,14],()=>{paragraph(panel,'wrong-road');audio.playSfx('fail-soft');});
      hotspot(stage,'bridge-road',[71,77,26,14],()=>go('S05'));paragraph(panel,'bird-break','small-help');
    }
    else if(['S05','S07','S10'].includes(id)){
      const index={S05:0,S07:1,S10:2}[id],next=['S06','S08','S11'][index];
      if(state.delivered[index])reward(panel,'delivered',next);
      else {const good=id==='S05'?['door-tray',[75,78,24,14]]:id==='S07'?['table-top',[68,60,27,13]]:['root-tray',[70,81,28,14]];
        const bad=id==='S05'?['tree-basket',[1,76,23,14]]:id==='S07'?['under-table',[68,79,27,14]]:['nest',[81,6,18,13]];
        hotspot(stage,...good,()=>{state.delivered[index]=true;save();render();audio.playSfx('success');});
        hotspot(stage,...bad,()=>{paragraph(panel,'wrong-place');audio.playSfx('fail-soft');});}
    }
    else if(id==='S08'){
      hotspot(stage,'walk-tree',[66,69,30,17],()=>go('S09'));
      if(!state.leaf)hotspot(stage,'草邊的葉子',[12,73,10,17],()=>{state.leaf=true;save();go('H01');audio.playSfx('found-item');},'hidden-leaf',true);
    }
    else if(id==='H01')reward(panel,'got-leaf','S08');
    else if(id==='S11'){
      if(state.placed){reward(panel,'station-done','E02');}
      else {
        hotspot(stage,'back-office',[3,3,28,17],()=>go('E01'));
        const slot=hotspot(stage,'老信箱',[73,37,10,16],()=>{if(selectedItem&&state.leaf)lock();else paragraph(panel,'observe-box');},'mailbox',true);
        const lock=()=>{if(!state.leaf||state.placed)return;state.placed=true;save();render();audio.playSfx('drag-lock');};
        if(state.leaf)cleanups.push(bindDrag(bag.querySelector('[data-item="leaf"]'),slot,lock));
      }
    }
    else if(id==='E02')actions.append(btn('visit-tree',()=>go('E03')));
    else if(['E01','E03'].includes(id)){paragraph(panel,'ending');actions.append(btn('menu',()=>{view='menu';render();}),btn('replay',()=>dialog('reset-help',()=>{state=fresh(state.code);save();go('S01');})));}
  }
  function render(){clear();root.style.setProperty('--scale',state.scale);controls();const main=el('main');const title=el('h1');title.append(text('title'));main.append(title);root.append(main);if(view==='menu'){root.dataset.scene='menu';menu(main);}else story(main);document.title=config.labels.title;}
  const visibility=()=>audio.setHidden(document.hidden);document.addEventListener('visibilitychange',visibility);
  window.addEventListener('pagehide',()=>{cleanups.splice(0).forEach(fn=>fn());audio.setHidden(true);});window.addEventListener('pageshow',()=>audio.setHidden(document.hidden));
  updateURL();render();
}
boot().catch(async()=>{root.replaceChildren();try{const text=await loadText();root.append(text('load-error'));}catch{root.textContent='故事暫時沒有載入。請重新整理。';}});
