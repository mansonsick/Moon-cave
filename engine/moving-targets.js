// Bounded, separate lanes keep visible targets apart; no physics engine or frame-state saves.
export class MovingTargets {
  constructor(nodes, {mode='normal',speed=1,onTick=()=>{}}={}) {
    this.nodes=nodes;this.mode=mode;this.speed=speed;this.onTick=onTick;this.running=false;this.last=0;this.elapsed=0;
    this.entries=nodes.map((node,i)=>({node,phase:i*1.7,x:0,y:0}));
    this.frame=requestAnimationFrame(time=>this.tick(time));
  }
  setRunning(value) {this.running=Boolean(value);this.last=0;}
  setMode(mode) {this.mode=mode;}
  tick(time) {
    const dt=this.last?Math.min((time-this.last)/1000,.06):0;this.last=time;
    if(this.running&&!document.hidden) {
      const multiplier=this.mode==='slow'?.48:this.mode==='static'?0:1;
      this.elapsed+=dt*this.speed*multiplier;
      for(const entry of this.entries) {
        const lane=entry.node.parentElement;
        const ax=Math.max(0,(lane.clientWidth-entry.node.offsetWidth)/2-8);
        const ay=Math.max(0,(lane.clientHeight-entry.node.offsetHeight)/2-8);
        entry.x=Math.sin(this.elapsed*.6+entry.phase)*ax;
        entry.y=Math.sin(this.elapsed*.83+entry.phase+.7)*ay;
        entry.node.style.transform=`translate(${entry.x}px,${entry.y}px)`;
      }
      this.onTick(dt);
    }
    this.frame=requestAnimationFrame(t=>this.tick(t));
  }
  dispose() {cancelAnimationFrame(this.frame);this.running=false;}
}

// Snapshot a pressed target and freeze motion before pointerup; a drag/cancel is not a tap.
export function bindStableTap(node, {freeze,resume,activate,hit=()=>true,allowed=()=>true}) {
  let press=null;
  const down=e=>{
    if(!e.isPrimary||e.button!==0||!allowed()||!hit(e))return;
    press={id:e.pointerId,x:e.clientX,y:e.clientY};freeze();node.setPointerCapture?.(e.pointerId);e.preventDefault();
  };
  const up=e=>{
    if(!press||e.pointerId!==press.id)return;
    const p=press;press=null;
    if(Math.hypot(e.clientX-p.x,e.clientY-p.y)<18&&allowed())activate();else resume();
  };
  const cancel=()=>{if(press){press=null;resume();}};
  const key=e=>{if((e.key==='Enter'||e.key===' ')&&allowed()){e.preventDefault();freeze();activate();}};
  node.addEventListener('pointerdown',down);node.addEventListener('pointerup',up);node.addEventListener('pointercancel',cancel);
  node.addEventListener('lostpointercapture',cancel);node.addEventListener('keydown',key);
  return ()=>{node.removeEventListener('pointerdown',down);node.removeEventListener('pointerup',up);node.removeEventListener('pointercancel',cancel);node.removeEventListener('lostpointercapture',cancel);node.removeEventListener('keydown',key);};
}

// Read the original alpha channel, excluding transparent padding and faint halo pixels.
export async function alphaTarget(canvas, src) {
  const image=new Image();image.src=src;await image.decode();
  canvas.width=300;canvas.height=Math.round(300*image.height/image.width);
  const ctx=canvas.getContext('2d',{willReadFrequently:true});ctx.drawImage(image,0,0,canvas.width,canvas.height);
  const pixels=ctx.getImageData(0,0,canvas.width,canvas.height).data;
  return e=>{
    const rect=canvas.getBoundingClientRect();
    const x=Math.floor((e.clientX-rect.left)/rect.width*canvas.width),y=Math.floor((e.clientY-rect.top)/rect.height*canvas.height);
    return x>=0&&x<canvas.width&&y>=0&&y<canvas.height&&pixels[(y*canvas.width+x)*4+3]>=100;
  };
}
