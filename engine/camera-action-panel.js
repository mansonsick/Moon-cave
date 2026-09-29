import {CameraActionSource} from './camera-action-source.js';
import {CameraActionTracker,ACTION_TARGETS,actionBody} from './camera-actions.js';
import {pickColour} from './ball-vision.js';

// Reusable UI adapter: caller supplies rendered text and completion persistence.
export function mountCameraAction(host,{kind,text,button,completed=false,onComplete=()=>{},onContinue=()=>{}}){
  const make=(tag,cls='')=>{const n=document.createElement(tag);n.className=cls;return n;};
  const root=make('section','camera-action');root.dataset.kind=kind;host.append(root);
  const source=new CameraActionSource(kind);let tracker=new CameraActionTracker(kind),mode='idle',disposed=false,complete=completed,frame=0,token=0,lastSeen=0,manualCount=0,startAt=null,lastDrawn=undefined;
  const cameraModes=['loading','setup','photo','selected','prepare','camera'];
  const intro=make('p');intro.append(text(`action-${kind}-help`));
  const privacy=make('p','camera-note');privacy.append(text('camera-local'));
  const view=make('div','action-camera-view');view.hidden=true;
  const video=make('video');video.autoplay=true;video.muted=true;video.playsInline=true;video.setAttribute('aria-label','鏡頭預覽');
  const photo=make('canvas','camera-photo');photo.hidden=true;photo.setAttribute('aria-label','定格照片，請點球的中央');
  const overlay=make('canvas');overlay.width=480;overlay.height=360;overlay.setAttribute('aria-hidden','true');view.append(video,photo,overlay);
  const feedback=make('p','action-status');feedback.setAttribute('role','status');feedback.setAttribute('aria-live','polite');
  const counter=make('output','action-counter');counter.setAttribute('aria-label','挑戰進度');
  const progress=make('progress');progress.max=ACTION_TARGETS[kind];progress.value=0;
  const controls=make('div','actions'),secondary=make('div','actions');
  const act=(id,fn)=>button(text,id,fn,id);
  const camera=act('action-camera',startCamera),manual=act('action-manual',()=>manualMode('action-manual-help'));
  const stop=act('action-stop',()=>idle('camera-stopped'));
  const begin=act('action-manual-start',startManual),rep=act('action-manual-rep',()=>{if(mode!=='manual-run'||complete)return;manualCount++;paint(manualCount,'action-manual-help');if(manualCount>=ACTION_TARGETS[kind])finish();});
  const next=act('continue',onContinue),pick=act('camera-repick',setupPhoto);
  const snap=act('camera-photo',takePhoto),retake=act('camera-retake',setupPhoto),ready=act('camera-photo-ready',prepare);
  controls.append(camera,manual,begin,rep,snap,ready,next);secondary.append(stop,pick,retake);
  root.append(intro,privacy,view,feedback,counter,progress,controls,secondary);
  let lastStatus='';
  function status(id){if(id===lastStatus)return;lastStatus=id;feedback.replaceChildren(text(id));feedback.dataset.status=id;root.dataset.status=id;}
  function paint(value,id){progress.value=value;counter.textContent=`${kind==='balance'?Math.floor(value):value} / ${ACTION_TARGETS[kind]}`;status(id);}
  function buttons(){
    root.dataset.mode=mode;camera.hidden=complete||cameraModes.includes(mode)||mode==='manual-run';manual.hidden=complete||mode==='manual'||mode==='manual-run';
    begin.hidden=mode!=='manual'||complete;rep.hidden=mode!=='manual-run'||kind==='balance'||complete;next.hidden=!complete;
    stop.hidden=!cameraModes.includes(mode)&&mode!=='manual-run';pick.hidden=kind!=='catch'||mode!=='camera';view.hidden=!cameraModes.includes(mode);
    snap.hidden=mode!=='setup';retake.hidden=!['photo','selected'].includes(mode);ready.hidden=mode!=='selected';
    photo.hidden=!['photo','selected'].includes(mode);video.hidden=!photo.hidden;
    overlay.hidden=!['camera','selected'].includes(mode);counter.hidden=['setup','photo','selected','loading'].includes(mode);
  }
  function clearPhoto(){photo.width=0;photo.height=0;}
  function release(){token++;cancelAnimationFrame(frame);source.stop();startAt=null;clearPhoto();lastDrawn=undefined;overlay.getContext('2d').clearRect(0,0,overlay.width,overlay.height);}
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
    if(sample===lastDrawn)return;lastDrawn=sample;
    const ctx=overlay.getContext('2d'),width=video.videoWidth||480,height=video.videoHeight||360;
    if(overlay.width!==width||overlay.height!==height){overlay.width=width;overlay.height=height;}
    const w=overlay.width,h=overlay.height;ctx.clearRect(0,0,w,h);ctx.lineWidth=3;ctx.strokeStyle='#7df2d0';ctx.fillStyle='#7df2d0';
    if(sample?.poses?.length===1){const p=sample.poses[0];for(const [a,b]of [[11,12],[11,23],[12,24],[23,24],[11,13],[13,15],[12,14],[14,16],[23,25],[25,27],[24,26],[26,28]]){
      if(p[a]?.visibility<.65||p[b]?.visibility<.65)continue;ctx.beginPath();ctx.moveTo(p[a].x*w,p[a].y*h);ctx.lineTo(p[b].x*w,p[b].y*h);ctx.stroke();
    }}
    if(sample?.ball){ctx.strokeStyle='#ffdb65';ctx.lineWidth=4;ctx.beginPath();ctx.arc(sample.ball.x*w,sample.ball.y*h,Math.max(9,sample.ball.r*w+5),0,Math.PI*2);ctx.stroke();}
  }
  function setupPhoto(){
    if(disposed||complete)return;
    cancelAnimationFrame(frame);source.pause(true);source.setColour(null);tracker.lose();clearPhoto();
    mode='setup';paint(tracker.count,'camera-photo-help');buttons();
  }
  function takePhoto(){
    if(mode!=='setup')return;
    try{
      if(!source.capturePhoto(photo))throw Error('photo');
      mode='photo';status('camera-pick');buttons();
    }catch{manualMode('camera-fallback');}
  }
  function prepare(){
    if(disposed||complete)return;
    clearPhoto();source.pause(false);tracker.lose();lastDrawn=undefined;mode='prepare';startAt=performance.now();buttons();
    const tick=now=>{
      if(disposed||mode!=='prepare')return;
      const remaining=Math.max(0,Math.ceil((5000-(now-startAt))/1000));
      counter.textContent=String(remaining);status('camera-step-back');
      if(remaining){frame=requestAnimationFrame(tick);return;}
      mode='camera';lastSeen=now;const startedAt=now;buttons();
      const track=time=>{
        if(disposed||mode!=='camera')return;
        const candidate=source.read(time),sample=candidate?.at>=startedAt?candidate:null;draw(sample);
        const result=sample?tracker.update(sample,sample.at):tracker.missing(time);
        if(actionBody(sample?.poses,kind))lastSeen=time;
        if(time-lastSeen>8000){manualMode('camera-fallback');return;}
        paint(kind==='balance'?result.seconds:result.count,result.status);
        if(result.done)finish();else frame=requestAnimationFrame(track);
      };
      frame=requestAnimationFrame(track);
    };
    frame=requestAnimationFrame(tick);
  }
  async function startCamera(){
    if(disposed||complete)return;release();const ticket=token;mode='loading';tracker=new CameraActionTracker(kind);paint(0,'camera-loading');buttons();
    const ok=await source.start(video,()=>manualMode('camera-fallback'));
    if(disposed||ticket!==token)return;
    if(!ok){manualMode('camera-fallback');return;}
    if(kind==='catch')setupPhoto();else prepare();
  }
  photo.addEventListener('pointerdown',event=>{
    if(!['photo','selected'].includes(mode))return;
    const box=photo.getBoundingClientRect(),x=1-(event.clientX-box.left)/box.width,y=(event.clientY-box.top)/box.height;
    try{
      const pixels=photo.getContext('2d').getImageData(0,0,photo.width,photo.height),colour=pickColour(pixels,x,y);
      if(!colour){source.setColour(null);mode='photo';status('camera-photo-retry');buttons();return;}
      source.setColour(colour);mode='selected';status('camera-photo-selected');buttons();
      overlay.width=photo.width;overlay.height=photo.height;const ctx=overlay.getContext('2d');ctx.strokeStyle='#ffdb65';ctx.lineWidth=4;
      ctx.beginPath();ctx.arc(x*photo.width,y*photo.height,15,0,Math.PI*2);ctx.stroke();
    }catch{manualMode('camera-fallback');}
  });
  const hidden=()=>{if(document.hidden&&!complete)idle('camera-paused');};
  const pagehide=()=>{if(!complete)idle('camera-paused');};
  document.addEventListener('visibilitychange',hidden);window.addEventListener('pagehide',pagehide);
  if(complete){mode='done';paint(ACTION_TARGETS[kind],'action-success');}else paint(0,'camera-ready');buttons();
  return ()=>{disposed=true;release();document.removeEventListener('visibilitychange',hidden);window.removeEventListener('pagehide',pagehide);};
}
