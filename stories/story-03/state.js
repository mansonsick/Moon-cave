import { createWorksheet, normalizeCode, GATE_SIZES, checkAnswers, answerCapacity } from '../../engine/math-worksheet.js';
export const KEY = 'adventure.story-03.state';
const scenes = ['cover','intro','gate1','passage','gate2','window','gate3','chest','roof','ordinary','secret','secret-home'];
export function fresh(code) {
  return { schema: 1, version: createWorksheet(code).version, code: normalizeCode(code), scene: 'cover',
    entries: GATE_SIZES.map(n => Array(n).fill('')), checked: GATE_SIZES.map(n => Array(n).fill(false)), solved: [false,false,false],
    wood: false, seed: false, placed: false, scale: 1 };
}
export function validate(value) {
  if (!value || value.schema !== 1 || !normalizeCode(value.code)) return null;
  const state = fresh(value.code), worksheet = createWorksheet(state.code);
  if(value.version!==worksheet.version)return null;
  state.entries = GATE_SIZES.map((n, g) => Array.from({length:n}, (_,i) => {
    const entry=value.entries?.[g]?.[i],capacity=answerCapacity(worksheet.gates[g]);
    return typeof entry==='string'&&new RegExp(`^[0-9 ]{0,${capacity}}$`).test(entry)?entry.trimEnd():'';
  }));
  state.solved = state.entries.map((entries,g) => checkAnswers(worksheet,g,entries).every(Boolean));
  state.checked = GATE_SIZES.map((n,g)=>Array.from({length:n},(_,i)=>value.checked?.[g]?.[i]===true||state.solved[g]));
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
