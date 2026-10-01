// First immutable reading pool: original authored questions, reproducible option order.
export function hash(value) {
  let n=2166136261; for(const c of value) n=Math.imul(n^c.charCodeAt(0),16777619);
  return n>>>0;
}
const checksum=seed=>(hash('forest-v1:'+seed)%1296).toString(36).padStart(2,'0');
export function newReadingCode() {
  const values=new Uint32Array(1); crypto.getRandomValues(values);
  const seed=values[0].toString(36).padStart(7,'0'); return `c1-${seed}-${checksum(seed)}`;
}
export function normalizeReadingCode(value) {
  if(typeof value!=='string') return null;
  const code=value.trim().toLowerCase(), m=/^c1-([a-z0-9]{7})-([a-z0-9]{2})$/.exec(code);
  return m&&m[2]===checksum(m[1])?code:null;
}
export function readingWorksheet(config,code) {
  code=normalizeReadingCode(code); if(!code) throw new Error('Invalid reading worksheet code');
  if(config.poolVersion!=='forest-v1') throw new Error('Unsupported reading pool version');
  const questions=config.questions.map(q=>{
    let seed=hash(code+':'+q.id); const choices=[...q.choices];
    for(let i=choices.length-1;i>0;i--){seed=(Math.imul(seed,1664525)+1013904223)>>>0;const j=seed%(i+1);[choices[i],choices[j]]=[choices[j],choices[i]];}
    return {...q,choices};
  });
  return {code,version:config.poolVersion,questions,stages:[0,1,2].map(stage=>questions.filter(q=>q.stage===stage))};
}
