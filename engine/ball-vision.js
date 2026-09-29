// A selected saturated colour + compact connected component, not a general object model.
// Tracking pixels stay in the worker. The opt-in setup photo is read locally in
// the panel, then discarded; only its selected colour is sent to the worker.
export function hsv(r,g,b){
  r/=255;g/=255;b/=255;const max=Math.max(r,g,b),min=Math.min(r,g,b),d=max-min;
  let h=!d?0:max===r?((g-b)/d+6)%6:max===g?(b-r)/d+2:(r-g)/d+4;
  return {h:h*60,s:max?d/max:0,v:max};
}
export function pickColour(image,x,y){
  const px=Math.min(image.width-1,Math.max(0,Math.round(x*(image.width-1))));
  const py=Math.min(image.height-1,Math.max(0,Math.round(y*(image.height-1))));
  const values=[];
  for(let dy=-1;dy<=1;dy++)for(let dx=-1;dx<=1;dx++){
    const i=(Math.min(image.height-1,Math.max(0,py+dy))*image.width+Math.min(image.width-1,Math.max(0,px+dx)))*4;
    const c=hsv(...image.data.slice(i,i+3));if(c.s>.4&&c.v>.25)values.push(c);
  }
  return values.length>=5?values[Math.floor(values.length/2)]:null;
}
export function findBall(image,colour){
  if(!colour)return null;
  const {width:w,height:h,data}=image,n=w*h,mask=new Uint8Array(n),queue=new Int32Array(n),candidates=[];
  for(let i=0;i<n;i++){const c=hsv(data[i*4],data[i*4+1],data[i*4+2]),dh=Math.abs(c.h-colour.h);if(Math.min(dh,360-dh)<16&&c.s>.38&&c.v>.23)mask[i]=1;}
  for(let i=0;i<n;i++)if(mask[i]){
    let head=0,tail=1,sx=0,sy=0,minx=w,maxx=0,miny=h,maxy=0;queue[0]=i;mask[i]=0;
    while(head<tail){const a=queue[head++],x=a%w,y=Math.floor(a/w);sx+=x;sy+=y;minx=Math.min(minx,x);maxx=Math.max(maxx,x);miny=Math.min(miny,y);maxy=Math.max(maxy,y);
      for(const b of [x>0?a-1:-1,x<w-1?a+1:-1,y>0?a-w:-1,y<h-1?a+w:-1])if(b>=0&&mask[b]){mask[b]=0;queue[tail++]=b;}
    }
    const bw=maxx-minx+1,bh=maxy-miny+1,ratio=bw/bh,fill=tail/(bw*bh);
    if(tail>=10&&tail<n*.035&&ratio>.55&&ratio<1.8&&fill>.48&&minx>0&&miny>0&&maxx<w-1&&maxy<h-1)candidates.push({x:sx/tail/w,y:sy/tail/h,r:Math.sqrt(tail/Math.PI)/w});
  }
  // Ambiguous same-colour objects are a pause, never guess which one is the ball.
  return candidates.length===1?candidates[0]:null;
}
