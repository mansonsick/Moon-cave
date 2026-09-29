// V2 codes carry all settings. Freeze this algorithm once shared/printed.
export const VERSION_V2 = 'story03-math-v2';
export const OPERATORS = ['+', '-', '*', '/'];
export const DEFAULT_CONFIG = [
  {leftDigits:1,rightDigits:1,ops:['+','-'],within10:true},
  {leftDigits:2,rightDigits:1,ops:['+','-'],within10:false},
  {leftDigits:2,rightDigits:2,ops:['+','-'],within10:false},
];
export function normalizeConfig(config) {
  if (!Array.isArray(config) || config.length !== 3) throw Error('Invalid settings');
  return config.map(c => {
    if (!c || ![1,2].includes(c.leftDigits) || ![1,2].includes(c.rightDigits) || !Array.isArray(c.ops)
      || !c.ops.length || c.ops.some(op=>!OPERATORS.includes(op))) throw Error('Invalid settings');
    const ops=OPERATORS.filter(op=>c.ops.includes(op)), within10=c.within10===true;
    if (within10 && (c.leftDigits!==1 || c.rightDigits!==1)) throw Error('Invalid range');
    // Do not silently reverse the operands when a requested operation is impossible.
    if (c.leftDigits<c.rightDigits && ops.some(op=>op==='-'||op==='/')) throw Error('No nonnegative integer questions');
    return {leftDigits:c.leftDigits,rightDigits:c.rightDigits,ops,within10};
  });
}
function hash(s) {
  let h=2166136261;
  for(const c of s) h=Math.imul(h^c.charCodeAt(0),16777619)>>>0;
  return h;
}
const checksum=s=>(hash(s)%1296).toString(36).padStart(2,'0');
export function encodeCode(config,seed) {
  if(!/^[a-z0-9]{8}$/.test(seed)) throw Error('Invalid seed');
  const packed=normalizeConfig(config).map(c=>{
    const mask=c.ops.reduce((n,op)=>n|(1<<OPERATORS.indexOf(op)),0);
    return ((c.leftDigits-1)|((c.rightDigits-1)<<1)|(mask<<2)|(c.within10?64:0)).toString(36).padStart(2,'0');
  }).join('');
  const prefix=`m2-${packed}-${seed}`;
  return `${prefix}-${checksum(prefix)}`;
}
export function decodeCode(code) {
  const match=/^m2-([a-z0-9]{6})-([a-z0-9]{8})-([a-z0-9]{2})$/.exec(code);
  if(!match || checksum(code.slice(0,-3))!==match[3]) return null;
  try {
    const config=Array.from({length:3},(_,g)=>{
      const n=parseInt(match[1].slice(g*2,g*2+2),36);
      if(n>127)throw Error('Unknown flags');
      return {leftDigits:1+(n&1),rightDigits:1+((n>>1)&1),ops:OPERATORS.filter((_,i)=>n&(1<<(i+2))),within10:!!(n&64)};
    });
    return normalizeConfig(config);
  } catch {return null;}
}
export function randomCode(config=DEFAULT_CONFIG) {
  const alphabet='23456789abcdefghjkmnpqrstuvwxyz',values=new Uint32Array(8);
  globalThis.crypto.getRandomValues(values);
  return encodeCode(config,[...values].map(v=>alphabet[v%alphabet.length]).join(''));
}
export function calculate({a,b,op}) {
  switch(op){case '+':return a+b;case '-':return a-b;case '*':return a*b;case '/':return a/b;default:throw Error('Unknown operator');}
}
export const operatorSign=op=>({'*':'×','/':'÷','-':'−','+':'+'}[op]);
const range=digits=>digits===1?[1,9]:[10,99];
export function capacityFor(config) {
  const [minB,maxB]=range(config.rightDigits),maxA=range(config.leftDigits)[1];
  const upper=Math.max(...config.ops.map(op=>calculate({a:maxA,b:(op==='-'||op==='/')?minB:maxB,op})));
  return String(Math.floor(config.within10?Math.min(10,upper):upper)).length;
}
function shuffle(list,random) {
  for(let i=list.length-1;i>0;i--){const j=Math.floor(random()*(i+1));[list[i],list[j]]=[list[j],list[i]];}
  return list;
}
export function createV2(code) {
  const config=decodeCode(code);
  if(!config) throw Error('Invalid worksheet code');
  let h=hash(`${VERSION_V2}:${code}`),number=0;
  const used=new Set();
  const random=()=>{h=(h+0x6D2B79F5)>>>0;let t=h;t=Math.imul(t^(t>>>15),t|1);t^=t+Math.imul(t^(t>>>7),t|61);return ((t^(t>>>14))>>>0)/4294967296;};
  const gates=config.map((c,g)=>{
    const [aMin,aMax]=range(c.leftDigits),[bMin,bMax]=range(c.rightDigits);
    const pools=c.ops.map(op=>{
      const pool=[];
      for(let a=aMin;a<=aMax;a++)for(let b=bMin;b<=bMax;b++){
        const q={a,b,op},result=calculate(q);
        if(result>=0&&Number.isInteger(result)&&(!c.within10||result<=10)&&!used.has(`${a}${op}${b}`))pool.push(q);
      }
      return shuffle(pool,random);
    });
    const questions=[];
    for(let i=0;i<[6,7,7][g];i++){
      const q=pools[i%pools.length].pop();
      if(!q)throw Error('Insufficient questions');
      used.add(`${q.a}${q.op}${q.b}`);questions.push(q);
    }
    return {id:g+1,config:c,answerDigits:capacityFor(c),questions:shuffle(questions,random).map(q=>({...q,id:++number}))};
  });
  return {version:VERSION_V2,code,config,gates};
}
