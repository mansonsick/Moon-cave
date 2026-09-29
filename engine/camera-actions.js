// Deterministic action rules, independent of camera/DOM. All coordinates are transient.
export const ACTION_TARGETS = Object.freeze({balance:8, jump:5, catch:3});
const good = p => p && Number.isFinite(p.x) && Number.isFinite(p.y) && p.x>.015 && p.x<.985 && p.y>.015 && p.y<.985 && p.visibility>=.65 && (p.presence===undefined||p.presence>=.65);
const mean=(a,b)=>({x:(a.x+b.x)/2,y:(a.y+b.y)/2});
const distance=(a,b)=>Math.hypot(a.x-b.x,a.y-b.y);
export function actionBody(poses,kind){
  if(poses?.length!==1)return null;
  const p=poses[0],ids=kind==='catch'?[11,12,15,16,23,24]:[0,11,12,23,24,25,26,27,28];
  if(!ids.every(i=>good(p[i])))return null;
  const shoulders=mean(p[11],p[12]),hips=mean(p[23],p[24]);
  const scale=kind==='catch'?(hips.y-shoulders.y)*2.6:Math.max(p[27].y,p[28].y)-p[0].y;
  if(scale<.25||hips.y-shoulders.y<.08||Math.abs(p[11].x-p[12].x)<.045)return null;
  return {p,hips,shoulders,scale,ankles:kind==='catch'?null:mean(p[27],p[28]),hands:mean(p[15],p[16])};
}

export class CameraActionTracker {
  constructor(kind){if(!(kind in ACTION_TARGETS))throw Error('action');this.kind=kind;this.reset();}
  reset(){this.count=0;this.held=0;this.last=null;this.base=null;this.calibration=null;this.calibratedAt=null;this.badSince=null;this.support=null;this.phase='ready';this.phaseAt=0;this.cooldown=0;this.lastBall=null;this.lastHands=null;this.nearSince=null;this.status='camera-calibrate';}
  result(status=this.status){this.status=status;return {status,count:this.count,seconds:Math.min(8,this.held/1000),done:this.kind==='balance'?this.held>=8000:this.count>=ACTION_TARGETS[this.kind]};}
  lose(){this.phase='ready';this.nearSince=null;this.lastBall=null;this.lastHands=null;this.calibration=null;}
  update(sample,at){
    // Duplicate/backwards timestamps cannot accumulate time or repetitions.
    if(this.last!==null&&at<=this.last)return this.result();
    const gap=this.last===null?0:at-this.last,dt=gap>350?0:gap;this.last=at;
    if(gap>600){this.lose();this.held=0;this.base=null;this.support=null;}
    const b=actionBody(sample?.poses,this.kind);
    if(!b){this.lose();this.held=0;this.support=null;return this.result('camera-body');}
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
    const bothUp=[27,28].every(i=>this.base.p[i].y-b.p[i].y>s*.055);
    const landed=[27,28].every(i=>Math.abs(this.base.p[i].y-b.p[i].y)<s*.04)&&Math.abs(up)<s*.065;
    if(Math.abs(b.hips.x-this.base.hips.x)>s*.18||Math.abs(b.scale-this.base.scale)>s*.2){this.phase='ready';return this.result('camera-center');}
    if(this.phase==='ready'&&at>=this.cooldown&&bothUp&&up>s*.075){this.phase='air';this.phaseAt=at;}
    else if(this.phase==='air'){
      if(at-this.phaseAt>1600)this.phase='ready';
      else if(landed&&at-this.phaseAt>=100){this.count++;this.phase='ready';this.cooldown=at+450;}
    }
    return this.result(this.phase==='air'?'camera-land':'camera-jump');
  }
  catchBall(b,ball,at,colorReady){
    if(!colorReady){this.lose();return this.result('camera-pick');}
    if(!ball||!Number.isFinite(ball.x)||!Number.isFinite(ball.y)){this.lose();return this.result('camera-ball');}
    const s=b.scale,near=[15,16].every(i=>distance(b.p[i],ball)<s*.23);
    const previous=this.lastBall;this.lastBall={...ball,at};
    if(previous&&distance(previous,ball)>s*.35){this.phase='ready';this.nearSince=null;}
    if(this.phase==='ready'){
      if(near){this.nearSince??=at;if(at-this.nearSince>=350&&at>=this.cooldown){this.phase='held';this.origin={...ball};this.peak=ball.y;this.phaseAt=at;}}
      else this.nearSince=null;
    }else if(this.phase==='held'){
      // A visible ball must leave BOTH hands and rise. Hand gestures alone never count.
      if(!near&&this.origin.y-ball.y>s*.09&&Math.min(...[15,16].map(i=>distance(b.p[i],ball)))>s*.24){this.phase='flight';this.phaseAt=at;this.peak=ball.y;this.descended=false;}
      else if(at-this.phaseAt>5000){this.phase='ready';this.nearSince=null;}
    }else if(this.phase==='flight'){
      this.peak=Math.min(this.peak,ball.y);
      if(ball.y-this.peak>s*.07)this.descended=true;
      if(at-this.phaseAt>3500||ball.y>b.hips.y+s*.2){this.phase='ready';this.nearSince=null;}
      else if(near&&distance(ball,b.hands)<=s*.16&&this.descended&&at-this.phaseAt>=250){this.phase='caught';this.phaseAt=at;this.lastHands=b.hands;this.nearSince=at;}
    }else if(this.phase==='caught'){
      const relative=distance(ball,b.hands);
      if(!near||relative>s*.16){this.phase='ready';this.nearSince=null;}
      else if(at-this.phaseAt>=400){this.count++;this.phase='ready';this.cooldown=at+500;this.nearSince=null;}
    }
    return this.result(this.phase==='flight'?'camera-catch':this.phase==='caught'?'camera-hold-ball':'camera-toss');
  }
}
