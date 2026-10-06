export const POOL = Array.from({length:37},(_,i)=>String.fromCodePoint(0x3105+i));
export const POOL_VERSION = 'moe-37-v1';
export const LEARN = ['S03','S05','S08'];
export const QUIZ = ['S04','S06','S09'];
const SCENES = ['S01','S02',...LEARN,...QUIZ,'S07','H01','S10','H02','E01','E02'];
export function seeded(seed) {
  let a=seed>>>0;
  return ()=>{a+=0x6D2B79F5;let t=a;t=Math.imul(t^(t>>>15),t|1);t^=t+Math.imul(t^(t>>>7),t|61);return((t^(t>>>14))>>>0)/4294967296;};
}
export function shuffle(items,random=Math.random) {
  const out=[...items];for(let i=out.length-1;i>0;i--){const j=Math.floor(random()*(i+1));[out[i],out[j]]=[out[j],out[i]];}return out;
}
export function freshState() {
  const seed=crypto.getRandomValues(new Uint32Array(1))[0];
  const symbols=shuffle(POOL,seeded(seed)).slice(0,18);
  return {schemaVersion:1,poolVersion:POOL_VERSION,seed,roundSymbols:[symbols.slice(0,6),symbols.slice(6,12),symbols.slice(12)],
    started:false,scene:'S01',history:[],learned:[[],[],[]],progress:[0,0,0],results:[[],[],[]],
    assistedPending:[false,false,false],lamp:false,bell:false,bellPlaced:false,endings:[],size:1,motion:'slow'};
}
export function canVisit(s,id) {
  const g=LEARN.indexOf(id),q=QUIZ.indexOf(id);
  if(id==='S01'||id==='S02')return true;
  if(g>=0)return s.lamp&&(g===0||s.progress[g-1]===6);
  if(q>=0)return s.lamp&&s.learned[q].length===6&&(q===0||s.progress[q-1]===6);
  if(id==='S07'||id==='H01')return s.progress[1]===6;
  if(id==='S10'||id==='E01')return s.progress.every(p=>p===6);
  if(id==='H02'||id==='E02')return s.progress.every(p=>p===6)&&s.bell&&s.bellPlaced;
  return false;
}
export function validateState(raw) {
  if(!raw||raw.schemaVersion!==1||raw.poolVersion!==POOL_VERSION||!Number.isInteger(raw.seed)||raw.seed<0||raw.seed>0xffffffff)return null;
  const groups=raw.roundSymbols;
  if(!Array.isArray(groups)||groups.length!==3||groups.some(g=>!Array.isArray(g)||g.length!==6||g.some(c=>!POOL.includes(c)))||new Set(groups.flat()).size!==18)return null;
  // Keep the saved draw; do not reconstruct it with a later shuffle implementation.
  const s={...raw,roundSymbols:groups.map(g=>[...g])};
  s.learned=Array.from({length:3},(_,g)=>Array.isArray(raw.learned?.[g])?[...new Set(raw.learned[g].filter(c=>groups[g].includes(c)))]:[]);
  s.results=Array.from({length:3},(_,g)=>{const list=[];for(let i=0;i<6;i++){const r=raw.results?.[g]?.[i];if(!r||r.symbol!==groups[g][i]||!['independent','assisted'].includes(r.mode))break;list.push({symbol:r.symbol,mode:r.mode});}return list;});
  s.progress=s.results.map(r=>r.length);
  for(let g=0;g<3;g++)if(s.learned[g].length!==6||(g>0&&s.progress[g-1]!==6)){s.results[g]=[];s.progress[g]=0;if(g>0&&s.progress[g-1]!==6)s.learned[g]=[];}
  s.started=raw.started===true;s.lamp=raw.lamp===true;
  if(!s.lamp){s.learned=[[],[],[]];s.results=[[],[],[]];s.progress=[0,0,0];}
  s.bell=raw.bell===true&&s.progress[1]===6;
  s.bellPlaced=raw.bellPlaced===true&&s.bell&&s.progress.every(p=>p===6);
  s.assistedPending=Array.from({length:3},(_,g)=>raw.assistedPending?.[g]===true&&s.progress[g]<6);
  s.endings=(Array.isArray(raw.endings)?[...new Set(raw.endings)]:[]).filter(e=>(e==='ordinary'&&s.progress.every(p=>p===6))||(e==='secret'&&s.bellPlaced));
  s.size=Number.isFinite(raw.size)?Math.max(.85,Math.min(1.45,raw.size)):1;
  s.motion=['slow','static'].includes(raw.motion)?raw.motion:'slow';
  s.scene=SCENES.includes(raw.scene)&&canVisit(s,raw.scene)?raw.scene:(s.lamp?'S03':'S01');
  s.history=(Array.isArray(raw.history)?raw.history:[]).filter(id=>SCENES.includes(id)&&canVisit(s,id)).slice(-40);
  return s;
}

// Review is optional and separate from the current adventure. A new draw must
// not erase sounds the family still wants to practise; old saves need no migration.
export function freshReview(){return {schemaVersion:1,symbols:{}};}
export function validateReview(raw){
  if(!raw||raw.schemaVersion!==1||!raw.symbols||typeof raw.symbols!=='object')return null;
  const review=freshReview();
  const count=n=>Number.isSafeInteger(n)&&n>0?Math.min(n,1000000):0;
  for(const symbol of POOL){
    const entry=raw.symbols[symbol],errors=count(entry?.errors);if(!errors)continue;
    const confusions={};for(const other of POOL)if(other!==symbol&&count(entry.confusions?.[other]))confusions[other]=count(entry.confusions[other]);
    review.symbols[symbol]={errors,confusions};
  }
  return review;
}
export function recordMistake(review,target,chosen){
  if(!POOL.includes(target)||!POOL.includes(chosen)||target===chosen)return;
  const e=review.symbols[target]||={errors:0,confusions:{}};
  e.errors=Math.min(e.errors+1,1000000);e.confusions[chosen]=Math.min((e.confusions[chosen]||0)+1,1000000);
}
export function commonMistakes(review){
  return Object.entries(review.symbols).filter(([,e])=>e.errors>0)
    .sort((a,b)=>b[1].errors-a[1].errors||a[0].codePointAt(0)-b[0].codePointAt(0));
}
