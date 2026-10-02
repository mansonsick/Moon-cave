import {createStorage} from '../../engine/storage.js';
import {MovingTargets,bindStableTap,alphaTarget} from '../../engine/moving-targets.js';
import {AlphabetAudio} from './alphabet-audio.js';
import {freshState,validateState,GROUPS,QUIZ_SCENES,LEARN_SCENES,currentLetter,recordCorrect,loseHeart,resetCurrentStage,choicesFor} from './state.js';
import {loadText} from './text.js';

const root=document.querySelector('#app');
const asset=(name)=>new URL('./assets/images/'+name,import.meta.url).href;
const element=(tag,className='')=>{const node=document.createElement(tag);node.className=className;return node;};

class AlphabetStory {
  constructor(config,text,audioConfig) {
    this.config=config;this.text=text;this.storage=createStorage('story-05',freshState,validateState);this.state=this.storage.load();
    this.audio=new AlphabetAudio(audioConfig,new URL('./assets/audio/',import.meta.url),this.storage.sound());
    this.cleanups=[];this.generation=0;this.started=false;this.inMenu=true;this.modalOpen=false;this.quiz=null;this.gemSelected=false;
    this.visibility=()=>{
      this.audio.setHidden(document.hidden);
      if(document.hidden&&this.quiz)this.pauseQuiz();
      // Resume is an explicit user action: no automatic clock or animation catch-up.
    };
    document.addEventListener('visibilitychange',this.visibility);
    window.addEventListener('pagehide',()=>this.clearScene());
    document.addEventListener('fullscreenchange',()=>this.updateFullscreen());
    this.renderMenu();
  }
  save(){this.storage.save(this.state);}
  button(label,callback,action=label) {
    const b=element('button');b.type='button';b.dataset.action=action;b.append(this.text(label));
    b.addEventListener('click',callback);return b;
  }
  icon(symbol,label,callback,action=label) {
    const b=element('button');b.type='button';b.dataset.action=action;b.setAttribute('aria-label',this.config.labels[label]);
    b.textContent=symbol;b.addEventListener('click',callback);return b;
  }
  clearScene(){this.generation++;for(const cleanup of this.cleanups.splice(0))cleanup();this.audio.cancelLetter();this.quiz=null;this.gemSelected=false;}
  shell(title='title') {
    this.clearScene();root.replaceChildren();root.setAttribute('aria-busy','false');root.style.setProperty('--text-scale',this.state.size);
    const book=element('article','book');const header=element('header','book-header');
    const h=element('h1');h.append(this.text(title));const tools=element('nav','tools');tools.setAttribute('aria-label','故事操作');
    const home=element('a');home.href='../../#english';home.dataset.action='home';home.append(this.text('home'));tools.append(home);
    if(!this.inMenu)tools.append(this.button('menu',()=>this.renderMenu()));
    tools.append(this.icon('A−','title',()=>this.changeSize(-.1),'smaller'),this.icon('A+','title',()=>this.changeSize(.1),'larger'));
    tools.querySelector('[data-action="smaller"]').setAttribute('aria-label','縮小文字');tools.querySelector('[data-action="larger"]').setAttribute('aria-label','放大文字');
    tools.append(this.icon(this.audio.enabled?'🔊':'🔇','sound',()=>this.toggleSound()),this.icon('⛶','fullscreen',()=>this.fullscreen(),'fullscreen'),this.icon('⚙','settings',()=>this.settings()));
    header.append(h,tools);
    if(this.state.gem&&!['S10','H02'].includes(this.state.scene)&&!this.inMenu){const item=element('img','inventory');item.src=asset('props/moonstone.png');item.alt=this.config.labels.moonstone;header.append(item);}
    book.append(header);root.append(book);this.book=book;return book;
  }
  changeSize(delta){this.state.size=Math.round(Math.max(.85,Math.min(1.45,this.state.size+delta))*100)/100;root.style.setProperty('--text-scale',this.state.size);this.save();}
  async toggleSound(){
    this.audio.setEnabled(!this.audio.enabled);this.storage.setSound(this.audio.enabled);
    const b=root.querySelector('[data-action="sound"]');if(b)b.textContent=this.audio.enabled?'🔊':'🔇';
    if(this.audio.enabled){await this.audio.unlock();this.audio.sceneAmbience(this.ambienceFor(this.state.scene));}
    if(this.quiz&&this.quiz.phase==='answering')void this.quiz.listen();
  }
  async fullscreen(){
    try {if(document.fullscreenElement)await document.exitFullscreen();else if(root.requestFullscreen)await root.requestFullscreen();else throw new Error('Unsupported');}
    catch{this.notice('fullscreen-help');}
  }
  updateFullscreen(){const b=root.querySelector('[data-action="fullscreen"]');if(b)b.setAttribute('aria-label',this.config.labels[document.fullscreenElement?'exit-fullscreen':'fullscreen']);}
  ambienceFor(sid){return ['E01','E02','H03'].includes(sid)?'dawn':['S05','S06','S07','H01'].includes(sid)?'house':['S08','S09','S10','H02'].includes(sid)?'bridge':'fog';}
  art(scene,{quiz=false,learning=false,purify=false}={}) {
    const cfg=this.config.scenes[scene];const stage=element('div','scene'+(quiz?' quiz':'')+(learning?' learning':'')+(purify?' purification':''));
    stage.dataset.scene=scene;stage.setAttribute('aria-label',this.config.labels[cfg.title]);
    const art=element('div','art');const bg=element('img','scene-background');bg.src=asset('backgrounds/'+cfg.background+'.png');bg.alt='';bg.draggable=false;art.append(bg);
    const person=element('img','actor person');person.src=asset('characters/atong-'+cfg.person+'.png');person.alt='';person.draggable=false;
    const squirrel=element('img','actor squirrel');squirrel.src=asset('characters/squirrel-'+cfg.squirrel+'.png');squirrel.alt='';squirrel.draggable=false;
    art.append(person,squirrel);
    if(['S05','S06'].includes(scene)) {
      const door=element('img','prop door-cover');door.src=asset('props/watch-door.png');Object.assign(door.style,{left:'76%',top:'3%',width:'20%',height:'46%',objectFit:'fill'});door.alt='';art.append(door);
      if(scene==='S06'){const slit=element('div','door-eye');const glimpse=element('img');glimpse.src=asset('characters/nabieqi-stalking.png');glimpse.alt='';slit.append(glimpse);art.append(slit);}
    }
    if(['S03','S05','S08'].includes(scene)) {const paper=element('img','prop quiet-note');paper.src=asset('props/watch-note.png');paper.alt='';art.append(paper);}
    if(!quiz&&!purify&&['S02','S10'].includes(scene)) {const monster=element('img','actor monster-story flying');monster.src=asset('characters/nabieqi-reaching-v2.png');monster.alt='';art.append(monster);}
    if(scene==='S01'){const monster=element('img','actor');monster.src=asset('characters/nabieqi-stalking.png');Object.assign(monster.style,{left:'77%',top:'9%',width:'7%',height:'12%',opacity:'.35'});monster.alt='';art.append(monster);}
    if(scene==='H03') {const shadow=element('img','actor monster-story cleansing-ghost');shadow.src=asset('characters/nabieqi-cleansing.png');shadow.alt='';art.append(shadow);}
    if(['H03','E02'].includes(scene)) {const angel=element('img','actor angel-story gentle');angel.src=asset('characters/angel.png');angel.alt='';art.append(angel);}
    stage.append(art);const mist=element('div','mist');mist.style.opacity=['E01','E02','H03'].includes(scene)?0:quiz?.75:.2;stage.append(mist);
    this.book.append(stage);return stage;
  }
  copy(scene) {const area=element('section','copy');for(const id of this.config.scenes[scene].lines){const p=element('p');p.append(this.text(id));area.append(p);}this.book.append(area);}
  actions(items){const area=element('div','actions');for(const [label,fn,action] of items)area.append(this.button(label,fn,action));this.book.append(area);return area;}
  paragraph(label,className='hint'){const p=element('p',className);p.append(this.text(label));this.book.append(p);return p;}
  async start(resume=false) {
    await this.audio.unlock();this.started=true;this.inMenu=false;
    if(!resume){const settings={size:this.state.size,motion:this.state.motion,timer:this.state.timer};this.state={...this.storage.reset(),...settings};this.save();}
    this.render();
  }
  renderMenu() {
    this.inMenu=true;this.audio.sceneAmbience(null);this.audio.stopAmbience();const book=this.shell();const stage=this.art('S01');stage.querySelector('.mist').style.opacity=.2;
    this.paragraph('cover-first','copy');this.paragraph('cover-second','copy');this.paragraph('hearts-rule');this.paragraph('hearts-reset');
    const hasProgress=this.state.scene!=='S01'||this.state.learned.some(x=>x.length)||this.state.completed.some(x=>x.length);
    const items=hasProgress?[['resume',()=>this.start(true)],['replay',()=>this.confirmReplay()]]:[['start',()=>this.start(false)]];
    this.actions(items);this.paragraph('settings-help');
  }
  go(scene,{history=true}={}) {
    if(history&&this.state.scene!==scene&&this.state.scene!=='R01')this.state.history.push(this.state.scene);
    this.state.history=this.state.history.slice(-24);this.state.scene=scene;
    const q=QUIZ_SCENES.indexOf(scene);
    if(q>this.state.stage){this.state.stage=q;this.state.hearts=3;}
    if(scene==='E01')this.state.ending='ordinary';if(scene==='E02')this.state.ending='secret';
    this.save();this.render();
  }
  previous() {
    let prev=this.state.history.pop();if(!prev)return;
    if(prev==='H02'&&this.state.round===5)prev='S10';
    this.state.scene=prev;this.save();this.render();
  }
  render() {
    this.inMenu=false;const scene=this.state.scene;const cfg=this.config.scenes[scene];
    this.shell(cfg.title);this.audio.sceneAmbience(this.ambienceFor(scene));
    if(QUIZ_SCENES.includes(scene))return this.renderQuiz(QUIZ_SCENES.indexOf(scene));
    if(LEARN_SCENES.includes(scene))return this.renderLearning(LEARN_SCENES.indexOf(scene));
    if(scene==='H02')return this.renderPurification();
    const stage=this.art(scene);this.copy(scene);
    if(scene==='S07') {
      const mark=element('button','hidden-mark');mark.type='button';mark.setAttribute('aria-label','查看牆腳');mark.dataset.action='moon-mark';
      const img=element('img');img.src=asset('props/moon-mark.png');img.alt='';mark.append(img);mark.addEventListener('click',()=>{this.state.gem=true;this.save();this.go('H01');});stage.append(mark);
    }
    if(scene==='H01'){this.state.gem=true;this.save();this.paragraph('take-stone','complete');void this.audio.playSfx('moonlight');}
    if(scene==='S10'&&this.state.gem) {
      const target=stage.querySelector('.monster-story');target.dataset.action='purify-target';target.style.pointerEvents='auto';target.tabIndex=0;target.setAttribute('role','button');target.setAttribute('aria-label','納別奇');
      this.bindGem(stage,target,()=>this.go('H02'));
    }
    const links={S01:['walk-ahead','S02'],S02:['shelter','S03'],S07:['bridge','S08'],H01:['continue','S08'],S10:['village','E01'],H03:['continue','E02']};
    if(scene==='R01') {
      this.paragraph('lost-hearts');this.paragraph('save-help');this.actions([['retry-stage',()=>{resetCurrentStage(this.state);this.save();this.render();}],['back-learning',()=>this.go(LEARN_SCENES[this.state.stage],{history:false})]]);
    } else if(links[scene]) {const [label,next]=links[scene];this.actions([[label,()=>this.go(next)]]);}
    if(['E01','E02'].includes(scene)) {
      this.paragraph(scene==='E01'?'ordinary-success':'secret-success','complete');this.paragraph('ending-learned');
      this.actions([['menu',()=>this.renderMenu()],['replay',()=>this.confirmReplay()]]);void this.audio.playSfx('success');
    }
    if(scene==='H03'){this.paragraph('angel-success','complete');void this.audio.playSfx('moonlight');}
    if(this.state.history.length&&scene!=='R01')this.actions([['previous',()=>this.previous()]]);
  }
  renderLearning(index) {
    const stage=this.art(LEARN_SCENES[index],{learning:true});this.copy(LEARN_SCENES[index]);
    const card=element('div','learn-card');const pair=element('div','letter-pair');const counter=element('span','counter');
    const listen=this.button('listen',()=>play(),'letter-voice');card.append(pair,counter,listen,this.text('heard'));stage.append(card);
    let at=this.state.learnIndex[index],busy=false;
    const group=GROUPS[index];const update=()=>{
      const letter=group[at];pair.textContent=letter+letter.toLowerCase();pair.setAttribute('aria-label',letter+' '+letter.toLowerCase());
      counter.textContent=`${at+1} / ${group.length}`;this.state.learnIndex[index]=at;
      if(!this.state.learned[index].includes(letter))this.state.learned[index].push(letter);this.save();
      previous.disabled=at===0;next.disabled=false;next.replaceChildren(this.text(at===group.length-1?'learn-done':'next-card'));
    };
    const play=async()=>{if(busy)return;busy=true;listen.disabled=true;await this.audio.unlock();await this.audio.letter(group[at]);listen.disabled=false;busy=false;};
    const previous=this.button('previous-card',()=>{this.audio.cancelLetter();at=Math.max(0,at-1);update();},'previous-card');
    const next=this.button('next-card',()=>{
      this.audio.cancelLetter();if(at<group.length-1){at++;update();return;}
      if(this.state.learned[index].length<group.length){at=group.split('').findIndex(x=>!this.state.learned[index].includes(x));update();return;}
      if(this.state.hearts===0&&index===this.state.stage)resetCurrentStage(this.state);
      this.go(QUIZ_SCENES[index]);
    },'next-card');
    const actions=element('div','actions');actions.append(previous,next);this.book.append(actions);update();
    if(this.state.history.length)this.actions([['previous',()=>this.previous()]]);
  }
  overlay(stage,label,items=[],target=null) {
    stage.querySelector('.feedback')?.remove();const panel=element('div','feedback');panel.setAttribute('role','status');panel.append(this.text(label));
    if(target){const preview=element('span','target-preview');preview.textContent=target+target.toLowerCase();panel.append(preview);}
    for(const [id,fn,action] of items)panel.append(this.button(id,fn,action));stage.append(panel);return panel;
  }
  renderQuiz(index) {
    const cfg=this.config.stages[index],complete=this.state.completed[index].length===GROUPS[index].length;
    if(!complete){this.state.stage=index;this.save();}
    const toolbar=element('div','quiz-toolbar');const hearts=element('span','hearts');const time=element('span','remaining');
    const voice=this.button('listen-again',()=>this.quiz?.listen(),'replay-letter');const pause=this.button('pause',()=>this.pauseQuiz());
    const show=this.button('show-letter',()=>this.quiz?.hint());toolbar.append(hearts,time,voice,pause,show);this.book.append(toolbar);
    const stage=this.art(cfg.scene,{quiz:true});stage.dataset.count=cfg.count;stage.dataset.progress=this.state.completed[index].length;
    const progress=element('div','progress-lamps');
    for(let i=0;i<GROUPS[index].length;i++) {const lamp=element('img','progress-lamp'+(i<this.state.completed[index].length?' lit':''));lamp.src=asset('props/'+(index===1?'candle':'lantern')+'-'+(i<this.state.completed[index].length?'lit':'unlit')+'.png');lamp.alt='';lamp.draggable=false;progress.append(lamp);}
    stage.append(progress);stage.querySelector('.mist').style.opacity=complete?0:.75*(1-this.state.completed[index].length/GROUPS[index].length);
    if(complete&&index===1){stage.querySelector('.door-cover')?.remove();stage.querySelector('.door-eye')?.remove();}
    const refreshHearts=()=>{hearts.replaceChildren();for(let i=0;i<3;i++){const h=element('span','heart'+(i>=this.state.hearts?' empty':''));h.textContent=i<this.state.hearts?'♥':'♡';hearts.append(h);}hearts.setAttribute('aria-label',`剩下${this.state.hearts}顆心`);};refreshHearts();
    if(complete){voice.disabled=true;pause.disabled=true;show.disabled=true;time.textContent='';this.overlay(stage,`stage-${index+1}-done`,[['continue',()=>this.go(cfg.next)]]);void this.audio.playSfx('success');return;}
    const target=currentLetter(this.state),letters=choicesFor(this.state,cfg.count);const field=element('div','playfield');const lanes=element('div','letter-lanes');
    const targets=letters.map(letter=>{const lane=element('div','lane');const card=element('button','letter-card');card.type='button';card.textContent=letter;card.dataset.letter=letter;card.setAttribute('aria-label',letter);lane.append(card);lanes.append(lane);return card;});
    const monsterLane=element('div','monster-lane');const monster=element('canvas','monster-target');monster.tabIndex=0;monster.setAttribute('role','button');monster.setAttribute('aria-label','納別奇');monster.dataset.action='monster';monsterLane.append(monster);field.append(lanes,monsterLane);stage.append(field);
    let monsterHit=()=>false;
    alphaTarget(monster,asset('characters/nabieqi-reaching-v2.png')).then(hit=>monsterHit=hit).catch(()=>{monster.style.visibility='hidden';});
    const generation=this.generation;
    const quiz={phase:'idle',assisted:false,seconds:cfg.seconds,heard:false,speechRevision:0,stage,target,motion:null,
      freeze:()=>quiz.motion.setRunning(false),resume:()=>quiz.motion.setRunning(quiz.phase==='answering'&&!this.modalOpen&&!document.hidden),
      showCards:visible=>{for(const card of targets){card.style.visibility=visible?'visible':'hidden';card.disabled=!visible;card.setAttribute('aria-hidden',String(!visible));}},
      beginAnswer:()=>{stage.querySelector('.feedback')?.remove();quiz.showCards(true);quiz.phase='answering';quiz.resume();},
      listen:async()=>{
        if(['correct','failed','finished'].includes(quiz.phase))return;
        const speechRevision=++quiz.speechRevision;quiz.phase='speaking';quiz.freeze();quiz.showCards(false);voice.disabled=true;stage.querySelector('.feedback')?.remove();
        const ok=await this.audio.letter(target);
        if(generation!==this.generation||speechRevision!==quiz.speechRevision)return;
        voice.disabled=false;quiz.seconds=cfg.seconds;quiz.heard=ok;quiz.phase='ready';
        if(!ok){quiz.assisted=true;this.overlay(stage,'visual-help',[['ready',quiz.beginAnswer]],target);}
        else quiz.beginAnswer();
      },
      hint:()=>{
        if(['correct','failed'].includes(quiz.phase))return;
        quiz.speechRevision++;this.audio.cancelLetter();quiz.assisted=true;quiz.phase='paused';quiz.freeze();quiz.showCards(false);voice.disabled=false;
        this.overlay(stage,'listen-help',[['ready',quiz.beginAnswer]],target);
      },
      answer:(letter)=>{
        if(quiz.phase!=='answering')return;quiz.freeze();
        if(letter.toUpperCase()===target) {
          quiz.phase='correct';recordCorrect(this.state,target,quiz.assisted||!quiz.heard);this.save();stage.dataset.progress=this.state.completed[index].length;
          const lamp=progress.children[this.state.completed[index].length-1];lamp.classList.add('lit');lamp.src=asset('props/'+(index===1?'candle':'lantern')+'-lit.png');
          stage.querySelector('.mist').style.opacity=.75*(1-this.state.completed[index].length/GROUPS[index].length);
          voice.disabled=true;show.disabled=true;pause.disabled=true;void this.audio.playSfx('success');
          const all=this.state.completed[index].length===GROUPS[index].length;
          if(all&&index===1){stage.querySelector('.door-cover')?.remove();stage.querySelector('.door-eye')?.remove();}
          this.overlay(stage,all?`stage-${index+1}-done`:'correct',[[all?'continue':'next-lamp',()=>all?this.go(cfg.next):this.nextQuiz()]]);
        }else quiz.miss('wrong');
      },
      miss:(label)=>{
        if(quiz.phase!=='answering')return;quiz.phase='failed';quiz.freeze();void this.audio.playSfx('fail-soft');
        const exhausted=loseHeart(this.state);this.save();refreshHearts();voice.disabled=true;show.disabled=true;pause.disabled=true;
        if(exhausted){this.go('R01',{history:false});return;}
        this.overlay(stage,label,[['retry-question',()=>this.nextQuiz()]]);
      }
    };
    quiz.motion=new MovingTargets([...targets,monster],{mode:this.state.motion,speed:[.9,1.2,1.5][index],onTick:dt=>{
      if(quiz.phase!=='answering'||!this.state.timer||!cfg.seconds)return;
      quiz.seconds=Math.max(0,quiz.seconds-dt);time.textContent=Math.ceil(quiz.seconds)+'s';if(quiz.seconds===0)quiz.miss('timeout');
    }});
    quiz.showCards(false);this.quiz=quiz;this.cleanups.push(()=>quiz.motion.dispose());
    for(const card of targets)this.cleanups.push(bindStableTap(card,{freeze:quiz.freeze,resume:quiz.resume,allowed:()=>quiz.phase==='answering'&&!this.modalOpen,activate:()=>quiz.answer(card.dataset.letter)}));
    this.cleanups.push(bindStableTap(monster,{freeze:quiz.freeze,resume:quiz.resume,allowed:()=>quiz.phase==='answering'&&!this.modalOpen,hit:e=>monsterHit(e),activate:()=>quiz.miss('monster-wrong')}));
    time.textContent=this.state.timer&&cfg.seconds?cfg.seconds+'s':'∞';
    this.overlay(stage,'listen-first',[['listen',()=>quiz.listen(),'begin-question']]);
    this.actions([['review',()=>this.go(LEARN_SCENES[index])]]);
    this.paragraph('hearts-rule');
  }
  nextQuiz(){this.render();void this.quiz?.listen();}
  pauseQuiz(){
    const quiz=this.quiz;if(!quiz||['correct','failed'].includes(quiz.phase))return;
    quiz.speechRevision++;quiz.phase='paused';quiz.freeze();quiz.showCards(false);this.audio.cancelLetter();
    const replay=root.querySelector('[data-action="replay-letter"]');if(replay)replay.disabled=false;
    this.overlay(quiz.stage,'paused',[['unpause',()=>quiz.listen()]]);
  }
  bindGem(stage,target,hit) {
    const bag=element('div','bag');const gem=element('button','gem');gem.type='button';gem.setAttribute('aria-label',this.config.labels.moonstone);gem.dataset.action='gem';
    const image=element('img');image.src=asset('props/moonstone.png');image.alt='';gem.append(image);bag.append(gem);
    if(stage.classList.contains('purification'))stage.append(bag);else this.book.append(bag);
    const glow=element('div','gem-light');this.book.append(glow);let dragging=null,moved=false,used=false;
    const overlap=(x,y)=>{const b=target.getBoundingClientRect();return x>b.left+b.width*.18&&x<b.right-b.width*.18&&y>b.top+b.height*.14&&y<b.bottom-b.height*.14;};
    const choose=()=>{this.gemSelected=!this.gemSelected;gem.classList.toggle('selected',this.gemSelected);};
    const down=e=>{if(!e.isPrimary||e.button!==0||this.modalOpen)return;dragging={id:e.pointerId,x:e.clientX,y:e.clientY};moved=false;used=false;gem.setPointerCapture(e.pointerId);e.preventDefault();};
    const move=e=>{
      if(!dragging||e.pointerId!==dragging.id)return;
      moved||=Math.hypot(e.clientX-dragging.x,e.clientY-dragging.y)>12;
      if(moved){glow.style.display='block';glow.style.left=e.clientX+'px';glow.style.top=e.clientY+'px';if(!used&&overlap(e.clientX,e.clientY)){used=true;hit();}}
    };
    const up=e=>{if(!dragging||e.pointerId!==dragging.id)return;if(!moved)choose();else if(!used&&overlap(e.clientX,e.clientY))hit();dragging=null;glow.style.display='none';};
    const cancel=()=>{dragging=null;glow.style.display='none';};
    gem.addEventListener('pointerdown',down);gem.addEventListener('pointermove',move);gem.addEventListener('pointerup',up);gem.addEventListener('pointercancel',cancel);
    gem.addEventListener('keydown',e=>{if(e.key==='Enter'||e.key===' '){e.preventDefault();choose();}});
    const activate=()=>{if(this.gemSelected&&!this.modalOpen){this.gemSelected=false;gem.classList.remove('selected');hit();}};
    target.addEventListener('click',activate);target.addEventListener('keydown',e=>{if(e.key==='Enter'||e.key===' '){e.preventDefault();activate();}});
    this.cleanups.push(cancel);
  }
  renderPurification() {
    const stage=this.art('H02',{purify:true});this.copy('H02');this.paragraph('purify-help');this.paragraph('purify-touch');
    const monster=element('img','purify-monster');monster.draggable=false;monster.tabIndex=0;monster.setAttribute('role','button');monster.setAttribute('aria-label','納別奇');monster.dataset.action='purify-target';stage.append(monster);
    const spots=matchMedia('(max-width:680px)').matches?[[59,36],[34,49],[58,57],[28,39],[54,44]]:[[64,24],[43,9],[67,43],[39,33],[60,14]];
    const counter=element('p','hint');counter.dataset.action='light-count';this.book.append(counter);let busy=false;
    const update=()=>{const round=this.state.round;const [x,y]=spots[Math.min(round,4)];monster.style.left=x+'%';monster.style.top=y+'%';monster.src=asset('characters/nabieqi-'+(round<2?'reaching-v2':'cleansing')+'.png');counter.textContent=`${round} / 5`;};
    const hit=()=>{
      if(busy||this.modalOpen||this.state.round>=5)return;busy=true;this.state.round++;this.save();counter.textContent=`${this.state.round} / 5`;monster.classList.add('shining');void this.audio.playSfx('moonlight');
      this.overlay(stage,'light-hit',[['next-light',()=>{if(this.state.round===5){this.go('H03');return;}stage.querySelector('.feedback')?.remove();monster.classList.remove('shining');update();busy=false;this.gemSelected=false;}]]);
    };
    this.bindGem(stage,monster,hit);update();this.actions([['ordinary-route',()=>this.go('E01')]]);
    if(this.state.round>=5){this.go('H03',{history:false});}
  }
  modal(title,build) {
    if(this.modalOpen)return;this.modalOpen=true;this.pauseQuiz();this.audio.cancelLetter();
    const shade=element('div','modal-shade'),panel=element('section','modal');panel.setAttribute('role','dialog');panel.setAttribute('aria-modal','true');panel.setAttribute('aria-label',this.config.labels[title]);
    const h=element('h2');h.append(this.text(title));panel.append(h);shade.append(panel);root.append(shade);
    const previous=document.activeElement;
    const close=()=>{shade.remove();this.modalOpen=false;previous?.focus();};
    const onkey=e=>{if(e.key==='Escape'){e.preventDefault();close();}if(e.key==='Tab'){const buttons=[...panel.querySelectorAll('button,a')].filter(x=>!x.disabled);if(!buttons.length)return;const i=buttons.indexOf(document.activeElement);if(e.shiftKey&&i<=0){e.preventDefault();buttons.at(-1).focus();}else if(!e.shiftKey&&i===buttons.length-1){e.preventDefault();buttons[0].focus();}}};
    shade.addEventListener('keydown',onkey);build(panel,close);panel.querySelector('button')?.focus();
  }
  notice(label){this.modal(label,(panel,close)=>panel.append(this.button('close',close)));}
  confirmReplay(){this.modal('replay',(panel,close)=>{const p=element('p');p.append(this.text('confirm-replay'));panel.append(p,this.button('yes-replay',()=>{close();void this.start(false);}),this.button('cancel',close));});}
  settings(){
    this.modal('settings',(panel,close)=>{
      const p=element('p');p.append(this.text('settings-help'));panel.append(p);
      const row=(title,items)=>{const block=element('div','setting-row');block.append(this.text(title));const options=element('div','options');
        for(const [label,value,prop] of items){const b=this.button(label,()=>{this.state[prop]=value;this.save();this.quiz?.motion.setMode(this.state.motion);for(const n of options.children)n.setAttribute('aria-pressed',n===b?'true':'false');});b.setAttribute('aria-pressed',this.state[prop]===value?'true':'false');options.append(b);}block.append(options);panel.append(block);};
      row('timer',[['timer',true,'timer'],['no-timer',false,'timer']]);row('movement',[['normal-motion','normal','motion'],['slow-motion','slow','motion'],['static-motion','static','motion']]);
      const audioReview=element('a','audio-review');audioReview.href='./assets/audio/letters/review.html';audioReview.target='_blank';audioReview.rel='noopener';audioReview.textContent='🔤 A–Z';panel.append(audioReview);
      panel.append(this.button('close',close));
    });
  }
}

try {
  const [config,text,audioConfig]=await Promise.all([
    fetch(new URL('./story.json',import.meta.url)).then(r=>{if(!r.ok)throw new Error('Missing story');return r.json();}),
    loadText(),fetch(new URL('./assets/audio/manifest.json',import.meta.url)).then(r=>r.ok?r.json():{entries:{}}).catch(()=>({entries:{}}))
  ]);
  new AlphabetStory(config,text,audioConfig.entries);
} catch {
  root.setAttribute('aria-busy','false');root.replaceChildren();const p=element('p','loading');const img=element('img');img.src=new URL('./assets/text/load-error-0.png',import.meta.url);img.alt='故事暫時沒有載入，請重新整理。';p.append(img);root.append(p);
}
