import { createWorksheet, normalizeCode, GATE_SIZES, checkAnswers, answerCapacity, gatePasswords, checkPasswords } from '../../engine/math-worksheet.js';
export const KEY = 'adventure.story-03.state';
export const PASSWORD_RULE = 'extremes-v1';
const scenes = ['cover','intro','gate1','passage','gate2','window','gate3','chest','roof','ordinary','secret','secret-home'];
export function fresh(code) {
  return { schema: 2, passwordRule: PASSWORD_RULE, version: createWorksheet(code).version, code: normalizeCode(code), scene: 'cover',
    entries: GATE_SIZES.map(n => Array(n).fill('')), checked: GATE_SIZES.map(n => Array(n).fill(false)), solved: [false,false,false],
    passwords: GATE_SIZES.map(()=>['','']), passwordChecked: GATE_SIZES.map(()=>[false,false]),
    wood: false, seed: false, placed: false, scale: 1 };
}
export function validate(value) {
  if (!value || ![1,2].includes(value.schema) || !normalizeCode(value.code)) return null;
  if(value.schema===2&&value.passwordRule!==PASSWORD_RULE)return null;
  const state = fresh(value.code), worksheet = createWorksheet(state.code);
  if(value.version!==worksheet.version)return null;
  const digits=(entry,g)=>typeof entry==='string'&&new RegExp(`^[0-9]{0,${answerCapacity(worksheet.gates[g])}}$`).test(entry.trimEnd())?entry.trimEnd():'';
  state.entries=GATE_SIZES.map((n,g)=>Array.from({length:n},(_,i)=>digits(value.entries?.[g]?.[i],g)));
  state.checked=GATE_SIZES.map((n,g)=>Array.from({length:n},(_,i)=>value.checked?.[g]?.[i]===true));
  if(value.schema===1){
    // Preserve genuinely completed doors; never manufacture passwords from partial work.
    state.entries.forEach((entries,g)=>{
      if(checkAnswers(worksheet,g,entries).every(Boolean)){
        state.passwords[g]=gatePasswords(worksheet,g);state.passwordChecked[g]=[true,true];
      }
    });
  }else{
    state.passwords=GATE_SIZES.map((_,g)=>Array.from({length:2},(_,i)=>digits(value.passwords?.[g]?.[i],g)));
    state.passwordChecked=GATE_SIZES.map((_,g)=>Array.from({length:2},(_,i)=>value.passwordChecked?.[g]?.[i]===true));
  }
  state.solved=state.passwords.map((entries,g)=>checkPasswords(worksheet,g,entries).every(Boolean));
  state.solved.forEach((solved,g)=>{if(solved)state.passwordChecked[g]=[true,true];});
  state.wood = value.wood === true;
  state.seed = value.seed === true && state.solved.every(Boolean);
  state.placed = value.placed === true && state.wood && state.seed;
  state.scale = Math.min(1.5, Math.max(.85, Number(value.scale) || 1));
  state.scene = scenes.includes(value.scene) ? value.scene : 'cover';
  const required = {passage:1,gate2:1,window:2,gate3:2,chest:3,roof:3,ordinary:3,secret:3,'secret-home':3};
  const count = required[state.scene] || 0;
  const incomplete = state.solved.slice(0,count).findIndex(s => !s);
  if (incomplete >= 0) state.scene = `gate${incomplete+1}`;
  if (['roof','ordinary','secret','secret-home'].includes(state.scene) && !state.seed) state.scene = 'chest';
  if (['secret','secret-home'].includes(state.scene) && !state.placed) state.scene = 'roof';
  return state;
}
