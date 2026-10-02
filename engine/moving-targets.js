// Shared full-field flight. Random turns, edge bounces and lightweight avoidance;
// Brief crossings are allowed; lingering overlaps trigger separation.
export class MovingTargets {
  constructor(nodes, {mode='normal',speed=1,onTick=()=>{},onTurn=()=>{},random=Math.random}={}) {
    this.nodes=nodes;this.mode=mode;this.speed=speed;this.onTick=onTick;this.running=false;this.last=0;this.elapsed=0;
    this.random=random;this.onTurn=onTurn;this.container=nodes[0]?.parentElement;this.gap=8;this.signature='';
    this.entries=nodes.map(node=>({node,x:0,y:0,w:0,h:0,vx:0,vy:0,dx:0,dy:0,turn:0,overlap:0}));
    this.layout();this.observer=new ResizeObserver(()=>this.layout());
    if(this.container)this.observer.observe(this.container);
    for(const node of nodes)this.observer.observe(node);
    this.frame=requestAnimationFrame(time=>this.tick(time));
  }
  setRunning(value) {this.running=Boolean(value);this.last=0;}
  setMode(mode) {this.mode=mode;}
  direction(entry) {
    const angle=this.random()*Math.PI*2;
    const pace=Math.max(35,Math.min(90,(this.width+this.height)*.065))*(.8+this.random()*.35);
    entry.dx=Math.cos(angle)*pace;entry.dy=Math.sin(angle)*pace;entry.turn=.8+this.random()*2;
    this.onTurn(entry.node);
  }
  layout() {
    if(!this.container)return;
    const width=this.container.clientWidth,height=this.container.clientHeight;
    const sizes=this.entries.map(e=>[e.node.offsetWidth,e.node.offsetHeight]);
    const signature=[width,height,...sizes.flat()].join(',');
    if(signature===this.signature||!width||!height)return;
    this.signature=signature;this.width=width;this.height=height;
    // Randomize spacious initial cells, then discard the cells for free flight.
    const pad=8,w=width-pad*2,h=height-pad*2;
    const maxW=Math.max(...sizes.map(s=>s[0])),maxH=Math.max(...sizes.map(s=>s[1]));
    const maxCols=Math.max(1,Math.floor(w/(maxW+this.gap)));
    let cols=Math.min(maxCols,Math.max(1,Math.ceil(Math.sqrt(this.entries.length*w/h))));
    while(Math.ceil(this.entries.length/cols)*(maxH+this.gap)>h&&cols<maxCols)cols++;
    const rows=Math.ceil(this.entries.length/cols),cw=w/cols,ch=h/rows;
    const slots=Array.from({length:cols*rows},(_,i)=>i);
    for(let i=slots.length-1;i>0;i--){const j=Math.floor(this.random()*(i+1));[slots[i],slots[j]]=[slots[j],slots[i]];}
    this.entries.forEach((e,i)=>{
      [e.w,e.h]=sizes[i];const slot=slots[i];
      e.x=pad+slot%cols*cw+this.gap/2+this.random()*Math.max(0,cw-e.w-this.gap);
      e.y=pad+Math.floor(slot/cols)*ch+this.gap/2+this.random()*Math.max(0,ch-e.h-this.gap);
      e.x=Math.min(e.x,width-e.w-pad);e.y=Math.min(e.y,height-e.h-pad);
      this.direction(e);e.vx=e.dx;e.vy=e.dy;e.overlap=0;this.place(e);
    });
  }
  place(e) {e.node.style.transform=`translate(${e.x}px,${e.y}px)`;}
  move(e,dt,wallTime=dt) {
    e.turn-=dt;if(e.turn<=0)this.direction(e);
    const blend=Math.min(1,dt*2.8);e.vx+=(e.dx-e.vx)*blend;e.vy+=(e.dy-e.vy)*blend;
    const maxX=this.width-e.w-8,maxY=this.height-e.h-8;
    let x=e.x+e.vx*dt,y=e.y+e.vy*dt;
    if(x<8||x>maxX){e.vx*=-1;e.dx*=-1;x=Math.max(8,Math.min(maxX,x));}
    if(y<8||y>maxY){e.vy*=-1;e.dy*=-1;y=Math.max(8,Math.min(maxY,y));}
    const other=this.entries.find(o=>o!==e&&x<o.x+o.w&&x+e.w>o.x&&y<o.y+o.h&&y+e.h>o.y);
    e.overlap=other?e.overlap+wallTime:0;
    if(other&&e.overlap>.65){
      // Let targets fly through; move away promptly if they linger together.
      let ax=e.x+e.w/2-other.x-other.w/2,ay=e.y+e.h/2-other.y-other.h/2;
      if(Math.hypot(ax,ay)<1){const angle=this.random()*Math.PI*2;ax=Math.cos(angle);ay=Math.sin(angle);}
      const length=Math.hypot(ax,ay),escape=220;
      e.vx=e.dx=ax/length*escape;e.vy=e.dy=ay/length*escape;e.turn=.45;
      x=Math.max(8,Math.min(maxX,e.x+e.vx*dt));y=Math.max(8,Math.min(maxY,e.y+e.vy*dt));
    }
    e.x=x;e.y=y;this.place(e);
  }
  tick(time) {
    const dt=this.last?Math.min((time-this.last)/1000,.06):0;this.last=time;
    if(this.running&&!document.hidden) {
      const multiplier=this.mode==='slow'?.48:this.mode==='static'?0:1;
      const step=dt*this.speed*multiplier;this.elapsed+=step;
      if(step&&this.width)for(const entry of this.entries)this.move(entry,step,dt);
      this.onTick(dt);
    }
    this.frame=requestAnimationFrame(t=>this.tick(t));
  }
  dispose() {cancelAnimationFrame(this.frame);this.observer.disconnect();this.running=false;}
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
