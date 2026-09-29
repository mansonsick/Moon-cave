// Deterministic action rules, independent of camera/DOM. All coordinates are transient.
export const ACTION_TARGETS = Object.freeze({balance:8, jump:5, catch:3});
const good = p => p && Number.isFinite(p.x) && Number.isFinite(p.y) && p.x>.015 && p.x<.985 && p.y>.015 && p.y<.985 && p.visibility>=.65 && (p.presence===undefined||p.presence>=.65);
const mean=(a,b)=>({x:(a.x+b.x)/2,y:(a.y+b.y)/2});
const distance=(a,b)=>Math.hypot(a.x-b.x,a.y-b.y);
export function actionBody(poses,kind){
  if(poses?.length!==1)return null;
  const p=poses[0],ids=kind==='catch'?[11,12,23,24]:[0,11,12,23,24,25,26,27,28];
  if(!ids.every(i=>good(p[i])))return null;
  const shoulders=mean(p[11],p[12]),hips=mean(p[23],p[24]);
  const scale=kind==='catch'?(hips.y-shoulders.y)*2.6:Math.max(p[27].y,p[28].y)-p[0].y;
  if(scale<.25||hips.y-shoulders.y<.08||Math.abs(p[11].x-p[12].x)<.045)return null;
  const handPoints=[p[15],p[16]].filter(good);
  return {p,hips,shoulders,scale,handPoints,ankles:kind==='catch'?null:mean(p[27],p[28]),hands:handPoints.length===2?mean(...handPoints):handPoints[0]};
}

export class CameraActionTracker {
  constructor(kind){if(!(kind in ACTION_TARGETS))throw Error('action');this.kind=kind;this.reset();}
  reset(){this.count=0;this.held=0;this.last=null;this.lastBodyAt=null;this.base=null;this.calibration=null;this.calibratedAt=null;this.badSince=null;this.support=null;this.phase='ready';this.phaseAt=0;this.cooldown=0;this.lastBallAt=null;this.nearSince=null;this.status='camera-calibrate';}
  result(status=this.status){this.status=status;return {status,count:this.count,seconds:Math.min(8,this.held/1000),done:this.kind==='balance'?this.held>=8000:this.count>=ACTION_TARGETS[this.kind]};}
  lose(){this.phase='ready';this.nearSince=null;this.lastBallAt=null;this.calibration=null;}
  missing(at,ambiguous=false){
    // A missing observation is not a new camera timestamp. Slow results can still arrive.
    if(!ambiguous&&this.kind==='jump'&&this.base&&this.lastBodyAt!==null&&at-this.lastBodyAt<=900)
      return this.result(this.phase==='air'?'camera-land':'camera-jump');
    if(!ambiguous&&this.kind==='catch')return this.missingBall(at);
    this.lose();this.held=0;this.support=null;
    if(this.lastBodyAt!==null&&at-this.lastBodyAt>600)this.base=null;
    return this.result('camera-body');
  }
  missingBall(at){
    if(this.lastBallAt!==null&&at-this.lastBallAt<=1500&&this.phase!=='ready'&&
      at-this.phaseAt<=(this.phase==='held'?5000:3500))return this.result('camera-ball-wait');
    this.lose();return this.result('camera-ball');
  }
  update(sample,at){
    if(!sample)return this.missing(at);
    // Duplicate/backwards timestamps cannot accumulate time or repetitions.
    if(this.last!==null&&at<=this.last)return this.result();
    const gap=this.last===null?0:at-this.last,dt=gap>350?0:gap;this.last=at;
    if(gap>(this.kind==='catch'?1500:this.kind==='jump'?900:600)){this.lose();this.held=0;this.base=null;this.support=null;}
    const b=actionBody(sample?.poses,this.kind);
    if(!b)return this.missing(at,sample.poses?.length>1);
    this.lastBodyAt=at;
    if(this.kind==='catch')return this.catchBall(b,sample.ball,at,!!sample.colorReady);
    if(!this.base){
      const standing=Math.abs(b.p[27].y-b.p[28].y)<b.scale*.045;
      if(!standing||this.calibration&&distance(b.hips,this.calibration.body.hips)>b.scale*.035){this.calibration=null;return this.result('camera-calibrate');}
      this.calibration ||= {at,body:b};
      if(at-this.calibration.at>=2000){this.base=this.calibration.body;this.calibratedAt=at;}
      return this.result('camera-calibrate');
    }
    return this.kind==='balance'?this.balance(b,at,dt):this.jump(b,at);
  }
  balance(b,at,dt){
    const lifted=b.p[27].y<b.p[28].y?27:28,support=lifted===27?28:27;
    const liftedKnee=lifted===27?25:26;
    const valid=b.p[support].y-b.p[lifted].y>b.scale*.14 && b.p[liftedKnee].y<b.p[support].y-b.scale*.2 &&
      Math.abs(b.p[support].y-this.base.p[support].y)<b.scale*.055 &&
      Math.abs(b.hips.x-this.base.hips.x)<b.scale*.12 && Math.abs(b.shoulders.y-this.base.shoulders.y)<b.scale*.1 &&
      (!this.support||support===this.support);
    if(valid){this.support=support;this.badSince=null;this.held+=dt;return this.result('camera-hold');}
    this.badSince??=at;
    if(at-this.badSince>=750){this.held=0;this.support=null;return this.result('camera-reset');}
    return this.result('camera-pause');
  }
  jump(b,at){
    const s=this.base.scale,up=this.base.hips.y-b.hips.y;
    const bothUp=[27,28].every(i=>this.base.p[i].y-b.p[i].y>s*.03);
    const landed=[27,28].every(i=>Math.abs(this.base.p[i].y-b.p[i].y)<s*.055)&&Math.abs(up)<s*.065;
    if(Math.abs(b.hips.x-this.base.hips.x)>s*.18||Math.abs(b.scale-this.base.scale)>s*.2){this.phase='ready';return this.result('camera-center');}
    // One credible takeoff frame is enough; no minimum time suspended in the air.
    if(this.phase==='ready'&&at>=this.cooldown&&bothUp&&up>s*.045){this.phase='air';this.phaseAt=at;this.peakUp=up;}
    else if(this.phase==='air'){
      if(at-this.phaseAt>1600)this.phase='ready';
      else if(landed&&this.peakUp-up>s*.025){this.count++;this.phase='ready';this.cooldown=at+350;}
      else this.peakUp=Math.max(this.peakUp,up);
    }
    return this.result(this.phase==='air'?'camera-land':'camera-jump');
  }
  catchBall(b,ball,at,colorReady){
    if(!colorReady){this.lose();return this.result('camera-pick');}
    if(!ball||!Number.isFinite(ball.x)||!Number.isFinite(ball.y)||!b.hands)return this.missingBall(at);
    if(this.lastBallAt!==null&&at-this.lastBallAt>1500)this.lose();
    const s=b.scale,near=Math.min(...b.handPoints.map(p=>distance(p,ball)))<s*.25&&
      Math.abs(ball.y-b.hands.y)<s*.20&&Math.abs(ball.x-b.hands.x)<s*.32;
    this.lastBallAt=at;
    if(this.phase!=='ready'&&at-this.phaseAt>(this.phase==='held'?5000:3500))this.lose();
    if(this.phase==='ready'){
      if(near){this.nearSince??=at;if(at-this.nearSince>=200&&at>=this.cooldown){this.phase='held';this.origin={...ball};this.peak=ball.y;this.phaseAt=at;}}
      else this.nearSince=null;
    }else if(this.phase==='held'){
      // Three checkpoints, not a continuous trajectory. Still require a visible ball
      // higher than its starting point and separated from the visible hand(s).
      if(!near&&this.origin.y-ball.y>s*.12&&b.handPoints.every(p=>distance(p,ball)>s*.25)){
        this.phase='flight';this.phaseAt=at;this.peak=ball.y;
      }
    }else if(this.phase==='flight'){
      this.peak=Math.min(this.peak,ball.y);
      if(ball.y>b.hips.y+s*.2){this.lose();}
      else if(near&&ball.y-this.peak>s*.08){this.phase='caught';this.nearSince=at;this.returnAt=at;}
    }else if(this.phase==='caught'){
      // Two real hand-height sightings, 150–650 ms apart. Missing frames do not
      // earn time/counts; a passing or dropped ball must not count as a catch.
      if(!near){this.lose();}
      else if(at-this.returnAt>650){this.nearSince=at;this.returnAt=at;}
      else if(at-this.nearSince>=150){this.count++;this.lose();this.cooldown=at+500;}
    }
    return this.result(this.phase==='flight'?'camera-catch':this.phase==='caught'?'camera-hold-ball':'camera-toss');
  }
}
