import {createStorage} from '../../engine/storage.js';
import {MovingTargets,bindStableTap} from '../../engine/moving-targets.js';
import {bindDrag,place} from '../../engine/interactions.js';
import {freshState,validateState,canVisit,shuffle,POOL,LEARN,QUIZ} from './state.js';
import {SymbolAudio} from './symbol-audio.js';
import {loadText,symbolImage} from './text.js';

const el=(tag,cls='')=>{const n=document.createElement(tag);n.className=cls;return n;};
const fetchJSON=async path=>{const r=await fetch(new URL(path,import.meta.url));if(!r.ok)throw new Error('Missing asset: '+path);return r.json();};
class ForestStory {
  constructor(root,config,layout,manifest,text) {
    this.root=root;this.config=config;this.layout=layout;this.text=text;
    this.storage=createStorage('story-06',freshState,validateState);this.state=this.storage.load();
    this.audio=new SymbolAudio(manifest.entries,new URL('./assets/audio/',import.meta.url),this.storage.sound());
    this.cleanups=[];this.generation=0;this.playRevision=0;this.modal=null;this.quiz=null;this.inMenu=true;
    this.visibility=()=>{this.audio.setHidden(document.hidden);if(document.hidden&&this.quiz){this.pauseQuiz();}else if(this.quiz)this.message('paused');};
    document.addEventListener('visibilitychange',this.visibility);
    window.addEventListener('pagehide',()=>{this.audio.sceneAmbience(null);this.audio.setHidden(true);});
    window.addEventListener('pageshow',()=>{if(!document.hidden)this.audio.setHidden(false);});
    this.renderMenu();
  }
  save(){this.storage.save(this.state);}
  button(id,action,fn,icon='') {
    const b=el('button');b.type='button';b.dataset.action=action;
    if(icon){b.className='icon';b.textContent=icon;b.setAttribute('aria-label',this.config.labels[id]);b.title=this.config.labels[id];}
    else b.append(this.text(id));
    b.addEventListener('click',fn);return b;
  }
  link(id,href){const a=el('a');a.href=href;a.append(this.text(id));return a;}
  clear() {
    this.generation++;this.playRevision++;this.audio.cancelSymbol();this.audio.sceneAmbience(null);this.audio.stopSfx();
    this.cleanups.splice(0).forEach(fn=>fn());this.quiz=null;this.selected=false;
    if(this.modal){this.modal.remove();this.modal=null;}
  }
  shell(title) {
    this.clear();this.root.replaceChildren();this.root.setAttribute('aria-busy','false');
    this.root.style.setProperty('--text-scale',this.state.size);
    const shell=el('div','shell');this.root.append(shell);
    const h=el('h1');h.append(this.text('title'));shell.append(h);
    const nav=el('nav','toolbar');nav.setAttribute('aria-label','故事工具');shell.append(nav);
    nav.append(this.link('home','../../#chinese'),this.button('menu','menu',()=>this.renderMenu()),this.button('previous','previous',()=>this.back()));
    nav.lastChild.disabled=this.inMenu||!this.state.history.length;
    nav.append(this.button('font-smaller','smaller',()=>this.resize(-.1),'A−'),this.button('font-larger','larger',()=>this.resize(.1),'A+'));
    this.soundButton=this.button(this.audio.enabled?'sound-on':'sound-off','sound',()=>this.toggleSound(),this.audio.enabled?'🔊':'🔇');nav.append(this.soundButton);
    nav.append(this.button('fullscreen','fullscreen',async()=>{try{if(document.fullscreenElement)await document.exitFullscreen();else if(this.root.requestFullscreen)await this.root.requestFullscreen();else this.notice('fullscreen-fail');}catch{this.notice('fullscreen-fail');}},'⛶'),this.button('settings','settings',()=>this.settings(),'⚙'));
    this.book=el('section','book');shell.append(this.book);
    if(title){const heading=el('h2','story-heading');heading.append(this.text(title));this.book.append(heading);}
    const legal=this.link('website','../../legal/');legal.className='legal-link';shell.append(legal);
  }
  resize(delta){this.state.size=Math.round(Math.max(.85,Math.min(1.45,this.state.size+delta))*100)/100;this.save();this.root.style.setProperty('--text-scale',this.state.size);}
  toggleSound(){const next=!this.audio.enabled;this.audio.setEnabled(next);this.storage.setSound(next);this.soundButton.textContent=next?'🔊':'🔇';this.soundButton.setAttribute('aria-label',this.config.labels[next?'sound-on':'sound-off']);this.soundButton.title=this.soundButton.getAttribute('aria-label');if(next)void this.audio.unlock();if(this.quiz){this.pauseQuiz();this.message(next?'paused':'audio-unavailable');}}
  notice(label){this.showDialog(label,[{label:'close',action:'close',fn:()=>this.closeDialog()}]);}
  showDialog(label,actions,extra) {
    this.modal?.remove();const before=document.activeElement;
    const scrim=el('div','modal-scrim'),dialog=el('section','dialog');dialog.tabIndex=-1;dialog.setAttribute('role','dialog');dialog.setAttribute('aria-modal','true');dialog.setAttribute('aria-label',this.config.labels[label]);
    const heading=el('h2');heading.append(this.text(label));dialog.append(heading);extra?.(dialog);
    const controls=el('div','controls');for(const a of actions)controls.append(this.button(a.label,a.action,a.fn));dialog.append(controls);scrim.append(dialog);this.root.append(scrim);this.modal=scrim;this.modalBefore=before;dialog.focus();
    dialog.addEventListener('keydown',e=>{if(e.key==='Tab'){const items=[...dialog.querySelectorAll('button,a[href]')].filter(n=>!n.disabled);if(!items.length)return;e.preventDefault();let i=items.indexOf(document.activeElement);i=(i+(e.shiftKey?-1:1)+items.length)%items.length;items[i].focus();}});
    return dialog;
  }
  closeDialog(){this.modal?.remove();this.modal=null;this.modalBefore?.isConnected&&this.modalBefore.focus();}
  confirmReplay(){this.showDialog('new-confirm',[{label:'confirm',action:'new-adventure',fn:()=>{void this.audio.unlock();this.state=this.storage.reset();this.state.started=true;this.save();this.inMenu=false;this.renderScene();}},{label:'cancel',action:'cancel',fn:()=>this.closeDialog()}],d=>{const p=el('p');p.append(this.text('new-note'));d.append(p);});}
  renderMenu() {
    this.inMenu=true;this.shell();const stage=this.stage('S01');this.book.append(stage);
    const copy=el('div','story-copy');for(const id of ['cover-first','cover-second','cover-third']){const p=el('p');p.append(this.text(id));copy.append(p);}this.book.append(copy);
    const actions=el('div','scene-actions');stage.append(actions);
    actions.append(this.button(this.state.started?'resume':'start',this.state.started?'resume':'start',()=>{void this.audio.unlock();this.state.started=true;this.save();this.inMenu=false;this.renderScene();}));
    if(this.state.started)actions.append(this.button('replay','replay',()=>this.confirmReplay()));
  }
  go(id,remember=true) {
    if(!canVisit(this.state,id))return;
    if(remember&&id!==this.state.scene)this.state.history=[...this.state.history,this.state.scene].slice(-40);
    this.state.scene=id;this.inMenu=false;this.save();this.renderScene();
  }
  back(){if(this.inMenu)return;let id;while(this.state.history.length){const candidate=this.state.history.pop();if(canVisit(this.state,candidate)){id=candidate;break;}}if(id)this.go(id,false);}
  layer(l) {const n=el('img','layer'+(l.glow?' glow':''));n.src='./assets/images/'+l.file;n.alt='';n.draggable=false;n.dataset.asset=l.file;if(l.role)n.dataset.role=l.role;if(l.index!==undefined)n.dataset.index=l.index;place(n,[l.x,l.y,l.width,l.height]);n.style.zIndex=l.z;return n;}
  stage(id) {
    const scene=this.layout.scenes.find(s=>s.id===id),stage=el('div','stage');stage.dataset.scene=id;
    const bg=el('img','bg');bg.src='./assets/images/backgrounds/'+scene.background+'.png';bg.alt='';bg.draggable=false;stage.append(bg);
    let progress=QUIZ.includes(id)?this.state.progress[QUIZ.indexOf(id)]:id==='S08'?this.state.progress[2]:0;
    let lamps=0;
    for(const source of scene.layers){
      if(['learning-card','answer-card'].includes(source.role))continue;
      if(source.role==='hidden-pickup'&&this.state.bell)continue;
      let l=source;
      if(source.role==='progress-lamp'){if(lamps++<progress)l=scene.completedLayers[lamps-1];}
      if(source.role==='progress-bird'&&source.index<progress)l=(scene.completedLayers||this.layout.scenes.find(s=>s.id==='S09').completedLayers).find(o=>o.role==='progress-bird'&&o.index===source.index)||source;
      stage.append(this.layer(l));
    }
    if(scene.foregroundOccluder){const fg=bg.cloneNode();fg.style.zIndex=scene.foregroundOccluder.z;fg.style.clipPath='polygon('+scene.foregroundOccluder.polygon.map(([x,y])=>x+'% '+y+'%').join(',')+')';stage.append(fg);}
    if(scene.fog){const fog=el('div','fog');fog.style.opacity=scene.fog*(1-progress/6);stage.append(fog);}
    for(const r of (scene.restoredWater||[]).slice(0,progress)){const w=el('div','water');place(w,[r.x,r.y,r.width,r.height]);stage.append(w);}
    if(scene.dew)for(const [x,y] of [[12,8],[44,12],[78,9],[90,20],[8,29],[56,23],[69,31],[30,18]]){const dot=el('span','dew');dot.style.left=x+'%';dot.style.top=y+'%';stage.append(dot);}
    return stage;
  }
  renderScene() {
    const id=this.state.scene,scene=this.config.scenes.find(s=>s.id===id);this.inMenu=false;this.shell(scene.title);this.book.dataset.scene=id;
    this.currentStage=this.stage(id);this.book.append(this.currentStage);
    const copy=el('div','story-copy');for(const line of scene.lines){const p=el('p');p.append(this.text(line));copy.append(p);}this.book.append(copy);
    this.bag();
    this.updateAmbience();
    const g=LEARN.indexOf(id),q=QUIZ.indexOf(id);
    if(g>=0){this.lesson(g);return;}
    if(q>=0){this.startQuiz(q);return;}
    const actions=el('div','scene-actions');this.currentStage.append(actions);
    if(id==='S01')actions.append(this.button('enter-forest','next',()=>this.go('S02')));
    if(id==='S02')actions.append(this.button('take-lamp','next',()=>{this.state.lamp=true;this.save();this.go('S03');void this.audio.playSfx('found-item');}));
    if(id==='S07'){
      actions.append(this.button('go-tree','next',()=>this.go('S08')));
      this.hotspot(this.layout.scenes.find(s=>s.id===id).hiddenHotspot,'explore',()=>this.go('H01'),'探索樹根旁的畫面');
    }
    if(id==='H01'){
      if(this.state.bell)actions.append(this.button('bell-back','next',()=>this.go('S07')));
      else this.hotspot(this.layout.scenes.find(s=>s.id===id).pickupHotspot,'pickup',()=>{
        if(this.state.bell)return;this.state.bell=true;this.save();
        this.renderScene();void this.audio.playSfx('found-item');this.showDialog('bell-found',[{label:'continue',action:'continue',fn:()=>this.go('S07')}],d=>{const img=el('img','reward');img.src='./assets/images/props/dew-bell.png';img.alt='';d.append(img);});
      },'拿起水窪裡的小鈴');
    }
    if(id==='S10'){
      actions.append(this.button('go-home','next',()=>{if(!this.state.endings.includes('ordinary'))this.state.endings.push('ordinary');this.go('E01');}));
      if(this.state.bell&&!this.state.bellPlaced)this.mountBell();
      else if(this.state.bellPlaced){this.currentStage.append(this.layer(this.layout.scenes.find(s=>s.id==='H02').layers.find(l=>l.role==='mounted-bell')));actions.append(this.button('together','secret-again',()=>this.go('H02')));}
    }
    if(id==='H02')actions.append(this.button('together','next',()=>{if(!this.state.endings.includes('secret'))this.state.endings.push('secret');this.go('E02');}));
    if(id.startsWith('E')){actions.append(this.button('menu','book-menu',()=>this.renderMenu()),this.button('replay','replay',()=>this.confirmReplay()));this.summary();}
  }
  hotspot(box,action,fn,aria) {const b=el('button','hidden-target');b.type='button';b.dataset.action=action;b.setAttribute('aria-label',aria);place(b,[box.x,box.y,box.width,box.height]);b.addEventListener('click',fn);this.currentStage.append(b);return b;}
  bag() {
    if(!this.state.lamp&&!this.state.bell)return;
    const bag=el('aside','bag');bag.setAttribute('aria-label',this.config.labels.bag);bag.append(this.text('bag'));
    if(this.state.lamp){const item=el('span','item'),img=el('img');img.src='./assets/images/props/listening-lamp.png';img.alt='';item.append(img,this.text('lamp'));bag.append(item);}
    this.bellButton=null;
    if(this.state.bell&&!this.state.bellPlaced){const b=this.button('bell','bell-item',()=>{});const img=el('img');img.src='./assets/images/props/dew-bell.png';img.alt='';b.prepend(img);bag.append(b);this.bellButton=b;}
    this.book.append(bag);
  }
  mountBell() {
    const dz=el('div','dropzone');dz.dataset.role='bell-hollow';const b=this.layout.scenes.find(s=>s.id==='S10').dropzone;place(dz,[b.x,b.y,b.width,b.height]);this.currentStage.append(dz);
    const generation=this.generation,placed=()=>{
      if(generation!==this.generation||!this.state.bell||this.state.bellPlaced||!this.state.progress.every(n=>n===6))return;
      this.state.bellPlaced=true;this.save();this.go('H02');void this.audio.playSfx('secret-bell');
    };
    this.cleanups.push(bindDrag(this.bellButton,dz,placed));
    // Keyboard / tap-select fallback does not reveal the destination in visible UI.
    this.bellButton.addEventListener('click',()=>{this.selected=!this.selected;this.bellButton.classList.toggle('selected',this.selected);this.bellButton.setAttribute('aria-pressed',String(this.selected));dz.classList.toggle('selected',this.selected);});
    dz.addEventListener('click',()=>{if(this.selected)placed();});
    dz.setAttribute('role','button');dz.setAttribute('aria-label','探索樹洞');dz.tabIndex=0;dz.addEventListener('keydown',e=>{if(this.selected&&(e.key==='Enter'||e.key===' ')){e.preventDefault();placed();}});
  }
  lesson(g) {
    const group=this.state.roundSymbols[g],config=this.config.stages[g],nodes=this.layout.scenes.find(s=>s.id===LEARN[g]).layers.filter(l=>l.role==='learning-card');
    const cards=[];
    for(let i=0;i<6;i++){const b=el('button','learn-card');b.type='button';b.dataset.symbol=group[i];b.setAttribute('aria-label','聽 '+group[i]);place(b,[nodes[i].x,nodes[i].y,nodes[i].width,nodes[i].height]);const art=el('img','card-art');art.src='./assets/images/props/'+config.card;art.alt='';art.draggable=false;b.append(art,symbolImage(group[i]));this.currentStage.append(b);cards.push(b);}
    const panel=el('div','lesson-panel');panel.append(this.text('learning'));const p=el('p');p.append(this.text('learn-touch'));panel.append(p);
    const sample=el('div','sample'),info=el('span');sample.append(info);panel.append(sample);
    const status=el('p');status.setAttribute('role','status');panel.append(status);
    const controls=el('div','controls'),next=this.button('learn-next','next-card',()=>select((index+1)%6)),again=this.button('learn-again','learn-again',()=>select(index));controls.append(again,next);panel.append(controls);this.book.insertBefore(panel,this.currentStage.nextSibling);
    const actions=el('div','scene-actions'),enter=this.button(['go-grass','go-stream','go-birds'][g],'enter-quiz',()=>this.go(config.quiz));actions.append(enter);this.currentStage.append(actions);
    let index=Math.max(0,group.findIndex(c=>!this.state.learned[g].includes(c))),voiceRevision=0;
    const select=i=>{
      index=i;if(!this.state.learned[g].includes(group[i]))this.state.learned[g].push(group[i]);this.save();
      cards.forEach((c,j)=>{c.classList.toggle('active',j===i);c.classList.toggle('seen',this.state.learned[g].includes(group[j]));c.setAttribute('aria-pressed',String(j===i));});
      sample.querySelector('.symbol')?.remove();sample.prepend(symbolImage(group[i]));info.replaceChildren(this.text('learn-count'),document.createTextNode(' '+this.state.learned[g].length+' / 6'));
      enter.disabled=this.state.learned[g].length<6;
      status.replaceChildren(this.text(this.audio.enabled?'sound-playing':'assist-note'));
      const token=++voiceRevision,generation=this.generation;
      void this.audio.symbol(group[i]).then(ok=>{if(token===voiceRevision&&generation===this.generation)status.replaceChildren(this.text(ok?'sound-check':this.audio.enabled?'sound-fail':'assist-note'));});
    };
    cards.forEach((b,i)=>b.addEventListener('click',()=>{void this.audio.unlock();select(i);}));select(index);
  }
  startQuiz(g) {
    const config=this.config.stages[g],progress=this.state.progress[g];
    const panel=el('div','quiz-panel'),row=el('div','progress-row');row.append(this.text('progress'),document.createTextNode(' '+progress+' / 6'));const dots=el('span','progress-dots');for(let i=0;i<6;i++)dots.append(el('i',i<progress?'on':''));row.append(dots);panel.append(row,this.button('learn-return','review-learning',()=>this.go(config.learn)));this.book.insertBefore(panel,this.currentStage.nextSibling);
    if(progress===6){const actions=el('div','scene-actions');actions.append(this.text('completed'),this.button('continue','continue',()=>this.go(config.next)));this.currentStage.append(actions);return;}
    const group=this.state.roundSymbols[g],target=group[progress];
    const choices=shuffle([target,...shuffle(group.filter(c=>c!==target)).slice(0,config.choices-1)]);
    const field=el('div','answer-field');field.hidden=true;const box=this.layout.scenes.find(s=>s.id===config.quiz).answerSafe;place(field,[box.x,box.y,box.width,box.height]);this.currentStage.append(field);
    const cards=choices.map(symbol=>{const b=el('button','answer-card'+(g===0?' leaf':''));b.type='button';b.dataset.symbol=symbol;b.setAttribute('aria-label',symbol);const art=el('img','card-art');art.src='./assets/images/props/'+config.card;art.alt='';art.draggable=false;b.append(art,symbolImage(symbol));field.append(b);return b;});
    const badge=el('div','quiz-badge'),message=el('div','quiz-message');message.setAttribute('role','status');badge.append(message);
    const controls=el('div','controls');badge.append(controls);this.currentStage.append(badge);
    const q={g,target,progress,field,cards,badge,message,controls,ready:false,locked:false,mover:null,assisted:this.state.assistedPending[g]};this.quiz=q;
    const begin=this.button('begin-question','begin-question',()=>this.playQuestion());const assist=this.button('assist','assist',()=>this.assistQuestion());controls.append(begin,assist);this.message(this.audio.enabled?'paused':'audio-unavailable');
    for(const b of cards)this.cleanups.push(bindStableTap(b,{freeze:()=>q.mover?.setRunning(false),resume:()=>q.mover?.setRunning(q.ready&&!q.locked),allowed:()=>this.quiz===q&&q.ready&&!q.locked&&!this.modal,activate:()=>this.answer(b.dataset.symbol,b)}));
  }
  message(label){this.quiz?.message.replaceChildren(this.text(label));}
  pauseQuiz(){this.playRevision++;this.audio.cancelSymbol();if(!this.quiz)return;this.quiz.ready=false;this.quiz.field.hidden=true;this.quiz.mover?.setRunning(false);this.quiz.badge.querySelector('.symbol')?.remove();const b=this.quiz.controls.querySelector('[data-action="begin-question"]');if(b)b.disabled=false;}
  async playQuestion() {
    const q=this.quiz;if(!q||q.locked||this.modal)return;
    this.pauseQuiz();const token=++this.playRevision,generation=this.generation;this.message('listen-wait');q.controls.querySelector('[data-action="begin-question"]').disabled=true;
    const unlocked=await this.audio.unlock();const ok=unlocked&&await this.audio.symbol(q.target);
    if(token!==this.playRevision||generation!==this.generation||this.quiz!==q)return;
    q.controls.querySelector('[data-action="begin-question"]').disabled=false;
    if(!ok){this.message('audio-unavailable');return;}
    this.revealQuestion(q,false);
  }
  assistQuestion(){const q=this.quiz;if(!q||q.locked||this.modal)return;this.pauseQuiz();q.assisted=true;this.state.assistedPending[q.g]=true;this.save();this.revealQuestion(q,true);}
  revealQuestion(q,visual) {
    if(this.quiz!==q||document.hidden)return;
    q.ready=true;q.field.hidden=false;
    q.controls.querySelector('[data-action="begin-question"]').disabled=false;
    q.controls.querySelector('[data-action="begin-question"]').replaceChildren(this.text('listen-again'));
    this.message(visual?'assist-note':'choose');if(visual)q.badge.prepend(symbolImage(q.target));
    if(!q.mover){q.mover=new MovingTargets(q.cards,{mode:q.g===0?'static':this.state.motion,speed:q.g===1?.35:.7});this.cleanups.push(()=>q.mover.dispose());}
    q.mover.setRunning(q.g>0&&this.state.motion!=='static'&&!this.modal);
  }
  answer(symbol,button) {
    const q=this.quiz;if(!q||!q.ready||q.locked||this.modal)return;
    if(symbol!==q.target){button.classList.add('wrong');button.animate?.([{opacity:1},{opacity:.6},{opacity:1}],{duration:300});this.message('wrong');void this.audio.playSfx('fail-soft');q.mover?.setRunning(q.g>0&&this.state.motion!=='static');return;}
    q.locked=true;q.ready=false;q.mover?.setRunning(false);this.audio.cancelSymbol();button.classList.remove('wrong');button.classList.add('right');
    for(const b of q.cards)b.disabled=true;
    if(this.state.progress[q.g]!==q.progress)return;
    this.state.results[q.g].push({symbol:q.target,mode:q.assisted?'assisted':'independent'});this.state.progress[q.g]++;this.state.assistedPending[q.g]=false;this.save();
    this.restoreProgress(q.g);this.message('right');q.controls.replaceChildren();void this.audio.playSfx('success');
    if(this.state.progress[q.g]===6){q.field.hidden=true;this.showDialog(this.config.stages[q.g].success,[{label:'continue',action:'continue',fn:()=>this.go(this.config.stages[q.g].next)}]);}
    else q.controls.append(this.button('next-question','next-question',()=>this.renderScene()));
  }
  restoreProgress(g) {
    const stage=this.currentStage,scene=this.layout.scenes.find(s=>s.id===QUIZ[g]),count=this.state.progress[g];
    if(g===0){stage.querySelectorAll('[data-role="progress-lamp"]').forEach(n=>n.remove());scene.layers.filter(l=>l.role==='progress-lamp').forEach((l,i)=>stage.append(this.layer(i<count?scene.completedLayers[i]:l)));}
    if(g===1){stage.querySelectorAll('.water').forEach(n=>n.remove());for(const r of scene.restoredWater.slice(0,count)){const w=el('div','water');place(w,[r.x,r.y,r.width,r.height]);stage.append(w);}}
    if(g===2){stage.querySelectorAll('[data-role="progress-bird"]').forEach(n=>n.remove());scene.layers.filter(l=>l.role==='progress-bird').forEach(l=>stage.append(this.layer(l.index<count?scene.completedLayers.find(o=>o.role==='progress-bird'&&o.index===l.index):l)));}
    if(stage.querySelector('.fog'))stage.querySelector('.fog').style.opacity=scene.fog*(1-count/6);
    this.updateAmbience();
    const row=this.book.querySelector('.progress-row');row.replaceChildren(this.text('progress'),document.createTextNode(' '+count+' / 6'));const dots=el('span','progress-dots');for(let i=0;i<6;i++)dots.append(el('i',i<count?'on':''));row.append(dots);
  }
  updateAmbience(){const id=this.state.scene,p=this.state.progress;if(id.startsWith('E')||this.inMenu){this.audio.sceneAmbience(null);return;}const g=p[2]>0?2:p[1]>0?1:p[0]>0?0:-1;this.audio.sceneAmbience(g<0?'quiet-forest':['cricket-song','stream-song','bird-song'][g],g<0?1:.25+.75*p[g]/6);}
  summary(){const box=el('div','lesson-panel summary');box.append(this.text('summary'));for(const mode of ['independent','assisted']){const p=el('p');p.append(this.text(mode));box.append(p);const list=el('div','symbols');for(const r of this.state.results.flat().filter(r=>r.mode===mode))list.append(symbolImage(r.symbol));if(!list.childNodes.length)list.textContent='0';box.append(list);}this.book.append(box);}
  settings() {
    this.pauseQuiz();this.audio.cancelSymbol();
    this.showDialog('settings',[{label:'close',action:'close',fn:()=>{this.closeDialog();if(this.quiz)this.message('paused');}}],d=>{
      const p=el('p');p.append(this.text('motion'));d.append(p);
      const controls=el('div','controls');for(const mode of ['slow','static']){const b=this.button(mode,'motion-'+mode,()=>{this.state.motion=mode;this.save();for(const n of controls.children)n.setAttribute('aria-pressed',String(n===b));if(this.quiz)this.quiz.mover?.setMode(this.quiz.g===0?'static':mode);});b.setAttribute('aria-pressed',String(this.state.motion===mode));controls.append(b);}d.append(controls);
      const a=this.link('audio-review','./audio-review.html');a.target='_blank';a.rel='noopener';d.append(a);
      const note=el('p','credits');note.append(this.text('audio-credit-note'));d.append(note);
      const credits=this.link('credits','./audio-review.html#credits');credits.target='_blank';credits.rel='noopener';d.append(credits);
    });
  }
}
try {
  const [config,layout,manifest,text]=await Promise.all([fetchJSON('./story.json'),fetchJSON('./SCENE_LAYERS.json'),fetchJSON('./assets/audio/manifest.json'),loadText()]);
  new ForestStory(document.querySelector('#app'),config,layout,manifest,text);
} catch(error) {console.error(error);const root=document.querySelector('#app');root.setAttribute('aria-busy','false');const a=document.createElement('a');a.href=location.href;const img=document.createElement('img');img.src='./assets/text/loading-0.png';img.alt='重新開啟故事';a.append(img);root.replaceChildren(a);}
