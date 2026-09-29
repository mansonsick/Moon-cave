import {CameraActionTracker} from '../engine/camera-actions.js';
import {findBall,pickColour} from '../engine/ball-vision.js';
export function body(){
  const p=Array.from({length:33},()=>({x:.5,y:.5,visibility:.99}));
  for(const [i,x,y]of [[0,.5,.12],[11,.42,.28],[12,.58,.28],[23,.46,.53],[24,.54,.53],[25,.46,.70],[26,.54,.70],[27,.46,.90],[28,.54,.90],[15,.46,.50],[16,.54,.50]])Object.assign(p[i],{x,y});
  return p;
}
export function runActionRuleTests(){
  const assert=(x,msg)=>{if(!x)throw Error(msg);};let checks=0;
  const sample=(p=body(),ball=null)=>({poses:[p],ball,colorReady:true});
  const calibrated=kind=>{const t=new CameraActionTracker(kind);for(let at=0;at<=2100;at+=100)t.update(sample(),at);return t;};
  const raised=()=>{const p=body();p[28].y=.60;p[26].y=.56;return p;};
  let t=calibrated('balance'),r;
  for(let at=2200;at<=10200;at+=100)r=t.update(sample(raised()),at);
  assert(r.done&&r.seconds===8,'single leg 8s');checks++;
  t=calibrated('balance');for(let at=2200;at<=5000;at+=100)t.update(sample(raised()),at);
  const held=t.held;t.update(sample(),5100);t.update(sample(),5200);assert(t.held===held,'brief loss pauses');
  for(let at=5300;at<=6000;at+=100)t.update(sample(),at);assert(t.held===0,'long loss resets');checks++;
  for(const invalid of [[],[body(),body()],[body().map((p,i)=>i===27?{...p,visibility:.1}:p)]]){
    t=calibrated('balance');t.update(sample(raised()),2200);t.update({poses:invalid},2300);assert(t.held===0,'uncertain/multiple/occluded body');
  }checks++;
  t=calibrated('balance');t.update(sample(raised()),2200);const before=t.held;t.update(sample(raised()),2200);assert(t.held===before,'duplicate time');t.update(sample(raised()),5000);assert(t.held===0&&!t.base,'stale frame recalibrates');checks++;
  t=calibrated('jump');let at=2200;
  for(let j=0;j<5;j++){
    const up=body().map(p=>({...p,y:p.y-.09}));t.update(sample(up),at);t.update(sample(up),at+100);r=t.update(sample(),at+200);
    for(let a=300;a<=700;a+=100)t.update(sample(),at+a);at+=800;
  }assert(r.done&&t.count===5,'5 full jump cycles');checks++;
  for(const style of ['wave','crouch','oneFoot','hipsOnly']){
    t=calibrated('jump');for(let a=2200;a<5200;a+=100){const p=body();if(style==='wave')p[15].y=.1;if(style==='crouch'){p[23].y+=.12;p[24].y+=.12;}if(style==='oneFoot')p[27].y-=.12;if(style==='hipsOnly'){p[23].y-=.12;p[24].y-=.12;}t.update(sample(p),a);}assert(t.count===0,style+' is not jump');
  }checks++;
  // Short hops only need one modest takeoff observation, then a real landing.
  for(const interval of [40,100,300,600,850]){
    t=calibrated('jump');const up=body().map(p=>({...p,y:p.y-.04}));
    t.update(sample(up),2200);t.update(sample(),2200+interval);
    assert(t.count===1,'small hop / sparse landing '+interval);
  }checks++;
  t=calibrated('jump');t.update(sample(body().map(p=>({...p,y:p.y-.04}))),2200);
  t.update({poses:[]},2300);t.missing(2500);t.update(sample(),2400);
  assert(t.count===1,'one missing pose and delayed result preserve takeoff; wall clock does not reject capture');checks++;
  for(const loss of ['long','multiple']){
    t=calibrated('jump');t.update(sample(body().map(p=>({...p,y:p.y-.04}))),2200);
    if(loss==='multiple')t.update({poses:[body(),body()]},2300);
    else t.missing(3200);
    t.update(sample(),3300);assert(t.count===0,'unsafe jump loss '+loss);
  }
  t=calibrated('jump');const tiny=body().map(p=>({...p,y:p.y-.012}));
  for(let a=2200;a<4000;a+=100)t.update(sample(a%200?body():tiny),a);
  assert(t.count===0,'standing jitter is not takeoff');checks++;
  t=new CameraActionTracker('catch');at=0;
  const feed=(y,duration=100)=>{for(let end=at+duration;at<end;at+=100)r=t.update(sample(body(),{x:.5,y,r:.025}),at);};
  for(let n=0;n<3;n++){feed(.5,1000);feed(.30);feed(.22);feed(.30);feed(.39,300);feed(.50,800);}
  assert(t.count===3&&r.done,'3 visible toss-return-hold cycles');checks++;
  t=new CameraActionTracker('catch');for(at=0;at<5000;at+=100)t.update(sample(body(),null),at);assert(t.count===0,'no ball never counts');
  for(at=5000;at<10000;at+=100)t.update(sample(body(),{x:.5,y:.5,r:.03}),at);assert(t.count===0,'static ball never counts');checks++;
  // A descending ball passing the hands without remaining held is not a catch.
  t=new CameraActionTracker('catch');at=0;feed(.5,800);feed(.3);feed(.2);feed(.3);feed(.5);feed(.8,500);assert(t.count===0,'dropped ball');checks++;
  const checkpoint=(y,at,p=body())=>t.update(sample(p,y===null?null:{x:.5,y,r:.025}),at);
  t=new CameraActionTracker('catch');checkpoint(.5,0);checkpoint(.5,200);checkpoint(null,600);
  assert(t.phase==='held'&&t.status==='camera-ball-wait','armed during invisible ascent');
  checkpoint(.12,900);t.update({poses:[],ball:null,colorReady:true},1000);checkpoint(null,1400);
  assert(t.phase==='flight'&&t.status==='camera-ball-wait','flight survives missing ball and body');
  const oneHand=body();oneHand[15].visibility=.1;
  checkpoint(.5,1700,oneHand);checkpoint(null,1800);checkpoint(.5,1900,oneHand);
  assert(t.count===1,'coarse hand/high/hand checkpoints, no intermediate trajectory, one visible wrist');
  checkpoint(.5,1900);checkpoint(.5,1890);assert(t.count===1,'duplicate/backwards catch timestamp');checks++;
  for(const invalid of ['noHigh','longGap','liftHeldBall','multiple']){
    t=new CameraActionTracker('catch');checkpoint(.5,0);checkpoint(.5,200);
    if(invalid==='liftHeldBall'){
      const handsUp=body();handsUp[15].y=.12;handsUp[16].y=.12;checkpoint(.12,400,handsUp);
    }else if(invalid!=='noHigh')checkpoint(.12,400);
    if(invalid==='multiple')t.update({poses:[body(),body()],colorReady:true},500);
    if(invalid==='longGap'){
      for(let a=500;a<=2100;a+=100)checkpoint(null,a);
      checkpoint(.5,2200);checkpoint(.5,2400);
    }else{checkpoint(null,600);checkpoint(.5,800);checkpoint(.5,1000);}
    assert(t.count===0,'incomplete or unsafe catch '+invalid);
  }checks++;
  t=new CameraActionTracker('catch');checkpoint(.5,0);checkpoint(.5,200);checkpoint(.12,400);checkpoint(.5,600);
  checkpoint(null,1100);checkpoint(.5,1400);assert(t.count===0,'long return gap needs fresh confirmation');
  checkpoint(.5,1600);assert(t.count===1,'fresh return confirmation can complete');checks++;
  const canvas=document.createElement('canvas');canvas.width=160;canvas.height=120;const c=canvas.getContext('2d');
  const clear=()=>{c.fillStyle='#ddd';c.fillRect(0,0,160,120);};const circle=(x,y)=>{c.fillStyle='#1767ee';c.beginPath();c.arc(x,y,8,0,Math.PI*2);c.fill();};
  clear();circle(80,50);let pixels=c.getImageData(0,0,160,120),colour=pickColour(pixels,.5,50/120),ball=findBall(pixels,colour);
  assert(colour&&Math.abs(ball.x-.5)<.01&&Math.abs(ball.y-50/120)<.01,'real pixels find selected blue ball');
  assert(!pickColour(pixels,.1,.1),'grey cannot calibrate');
  circle(120,80);assert(findBall(c.getImageData(0,0,160,120),colour)===null,'two same-colour balls ambiguous');
  clear();c.fillStyle='#1767ee';c.fillRect(15,10,5,70);assert(findBall(c.getImageData(0,0,160,120),colour)===null,'long colour stripe not ball');checks++;
  return checks;
}
