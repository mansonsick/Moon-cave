import {CameraActionSource} from './camera-action-source.js';
import {CameraActionTracker,ACTION_TARGETS,actionBody} from './camera-actions.js';

// Reusable UI adapter: caller supplies rendered text and completion persistence.
export function mountCameraAction(host,{kind,text,button,completed=false,onComplete=()=>{},onContinue=()=>{}}){
  const make=(tag,cls='')=>{const n=document.createElement(tag);n.className=cls;return n;};
  const root=make('section','camera-action');root.dataset.kind=kind;host.append(root);
  const source=new CameraActionSource(kind);let tracker=new CameraActionTracker(kind),mode='idle',disposed=false,complete=completed,frame=0,token=0,lastSeen=0,manualCount=0,startAt=null;
  const intro=make('p');intro.append(text(`action-${kind}-help`));
  const privacy=make('p','camera-note');privacy.append(text('camera-local'));
  const view=make('div','action-camera-view');view.hidden=true;
  const video=make('video');video.autoplay=true;video.muted=true;video.playsInline=true;video.setAttribute('aria-label','鏡頭預覽');
  const overlay=make('canvas');overlay.width=480;overlay.height=360;overlay.setAttribute('aria-hidden','true');view.append(video,overlay);
  const feedback=make('p','action-status');feedback.setAttribute('role','status');feedback.setAttribute('aria-live','polite');
  const counter=make('output','action-counter');counter.setAttribute('aria-label','挑戰進度');
  const progress=make('progress');progress.max=ACTION_TARGETS[kind];progress.value=0;
  const controls=make('div','actions'),secondary=make('div','actions');
  const act=(id,fn)=>button(text,id,fn,id);
  const camera=act('action-camera',startCamera),manual=act('action-manual',()=>manualMode('action-manual-help'));
  const stop=act('action-stop',()=>idle('camera-stopped'));
  const begin=act('action-manual-start',startManual),rep=act('action-manual-rep',()=>{if(mode!=='manual-run'||complete)return;manualCount++;paint(manualCount,'action-manual-help');if(manualCount>=ACTION_TARGETS[kind])finish();});
  const next=act('continue',onContinue),pick=act('camera-repick',()=>{source.pickColour(null);tracker.lose();status('camera-pick');});
  controls.append(camera,manual,begin,rep,next);secondary.append(stop,pick);
  root.append(intro,privacy,view,feedback,counter,progress,controls,secondary);
  let lastStatus='';
  function status(id){if(id===lastStatus)return;lastStatus=id;feedback.replaceChildren(text(id));feedback.dataset.status=id;root.dataset.status=id;}
  function paint(value,id){progress.value=value;counter.textContent=`${kind==='balance'?Math.floor(value):value} / ${ACTION_TARGETS[kind]}`;status(id);}
  function buttons(){
    root.dataset.mode=mode;camera.hidden=complete||['loading','camera','manual-run'].includes(mode);manual.hidden=complete||mode==='manual'||mode==='manual-run';
    begin.hidden=mode!=='manual'||complete;rep.hidden=mode!=='manual-run'||kind==='balance'||complete;next.hidden=!complete;
    stop.hidden=!['loading','camera','manual-run'].includes(mode);pick.hidden=kind!=='catch'||mode!=='camera';view.hidden=!['loading','camera'].includes(mode);
  }
  function release(){token++;cancelAnimationFrame(frame);source.stop();startAt=null;overlay.getContext('2d').clearRect(0,0,overlay.width,overlay.height);}
  function idle(message){release();if(disposed||complete)return;mode='idle';paint(0,message);buttons();}
  function manualMode(message){release();if(disposed||complete)return;mode='manual';manualCount=0;paint(0,message);buttons();}
  function finish(){if(complete||disposed)return;complete=true;release();mode='done';paint(ACTION_TARGETS[kind],'action-success');buttons();onComplete();}
  function startManual(){
    if(disposed||complete)return;release();mode='manual-run';manualCount=0;startAt=performance.now();paint(0,'action-manual-help');buttons();
    if(kind==='balance'){
      const tick=now=>{if(disposed||mode!=='manual-run')return;const value=Math.min(8,(now-startAt)/1000);paint(value,'action-manual-help');if(value>=8)finish();else frame=requestAnimationFrame(tick);};
      frame=requestAnimationFrame(tick);
    }
  }
  function draw(sample){
    const ctx=overlay.getContext('2d');overlay.width=video.videoWidth||480;overlay.height=video.videoHeight||360;
    const w=overlay.width,h=overlay.height;ctx.clearRect(0,0,w,h);ctx.lineWidth=3;ctx.strokeStyle='#7df2d0';ctx.fillStyle='#7df2d0';
    if(sample?.poses?.length===1){const p=sample.poses[0];for(const [a,b]of [[11,12],[11,23],[12,24],[23,24],[11,13],[13,15],[12,14],[14,16],[23,25],[25,27],[24,26],[26,28]]){
      if(p[a]?.visibility<.65||p[b]?.visibility<.65)continue;ctx.beginPath();ctx.moveTo(p[a].x*w,p[a].y*h);ctx.lineTo(p[b].x*w,p[b].y*h);ctx.stroke();
    }}
    if(sample?.ball){ctx.strokeStyle='#ffdb65';ctx.lineWidth=4;ctx.beginPath();ctx.arc(sample.ball.x*w,sample.ball.y*h,Math.max(9,sample.ball.r*w+5),0,Math.PI*2);ctx.stroke();}
  }
  async function startCamera(){
    if(disposed||complete)return;release();const ticket=token;mode='loading';tracker=new CameraActionTracker(kind);paint(0,'camera-loading');buttons();
    const ok=await source.start(video,()=>manualMode('camera-fallback'));
    if(disposed||ticket!==token)return;
    if(!ok){manualMode('camera-fallback');return;}
    mode='camera';lastSeen=performance.now();buttons();
    const tick=now=>{
      if(disposed||mode!=='camera')return;
      const sample=source.read(now);draw(sample);
      const result=tracker.update(sample,sample?.at??now);
      if(actionBody(sample?.poses,kind))lastSeen=now;
      if(now-lastSeen>8000){manualMode('camera-fallback');return;}
      paint(kind==='balance'?result.seconds:result.count,result.status);
      if(result.done)finish();else frame=requestAnimationFrame(tick);
    };
    frame=requestAnimationFrame(tick);
  }
  view.addEventListener('pointerdown',event=>{
    if(kind!=='catch'||mode!=='camera')return;
    const box=video.getBoundingClientRect();source.pickColour({x:1-(event.clientX-box.left)/box.width,y:(event.clientY-box.top)/box.height});tracker.lose();status('camera-pick-wait');
  });
  const hidden=()=>{if(document.hidden&&!complete)idle('camera-paused');};
  const pagehide=()=>{if(!complete)idle('camera-paused');};
  document.addEventListener('visibilitychange',hidden);window.addEventListener('pagehide',pagehide);
  if(complete){mode='done';paint(ACTION_TARGETS[kind],'action-success');}else paint(0,'camera-ready');buttons();
  return ()=>{disposed=true;release();document.removeEventListener('visibilitychange',hidden);window.removeEventListener('pagehide',pagehide);};
}
