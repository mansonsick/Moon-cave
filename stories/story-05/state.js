export const GROUPS = ['ABCDEFGHI','JKLMNOPQR','STUVWXYZ'];
export const QUIZ_SCENES = ['S04','S06','S09'];
export const LEARN_SCENES = ['S03','S05','S08'];
const SCENES = new Set(['S01','S02',...LEARN_SCENES,...QUIZ_SCENES,'S07','H01','S10','H02','H03','E01','E02','R01']);
export function shuffled(items) {
  const result = [...items];
  for (let i=result.length-1;i>0;i--) { const j=Math.floor(Math.random()*(i+1)); [result[i],result[j]]=[result[j],result[i]]; }
  return result;
}
export function freshState() {
  return {version:1,scene:'S01',history:[],stage:0,hearts:3,completed:[[],[],[]],independent:[[],[],[]],assisted:[[],[],[]],
    learned:[[],[],[]],learnIndex:[0,0,0],orders:GROUPS.map(shuffled),gem:false,round:0,ending:null,
    size:1,timer:true,motion:matchMedia('(prefers-reduced-motion: reduce)').matches?'static':'normal'};
}
const bounded = (n, max, fallback=0) => Number.isInteger(n) ? Math.max(0,Math.min(max,n)) : fallback;
export function validateState(saved) {
  if (!saved || saved.version!==1) return null;
  const state = freshState();
  for (const key of ['completed','learned','independent','assisted'])
    state[key]=GROUPS.map((g,i)=>[...new Set(Array.isArray(saved[key]?.[i])?saved[key][i].filter(x=>g.includes(x)&&x.length===1):[])]);
  state.orders=GROUPS.map((g,i)=>Array.isArray(saved.orders?.[i]) && saved.orders[i].length===g.length && new Set(saved.orders[i]).size===g.length && saved.orders[i].every(x=>g.includes(x)&&x.length===1)?saved.orders[i]:shuffled(g));
  state.learnIndex=GROUPS.map((g,i)=>bounded(saved.learnIndex?.[i],g.length-1));
  state.stage=bounded(saved.stage,2);state.hearts=bounded(saved.hearts,3,3);state.gem=saved.gem===true;
  state.round=state.gem?bounded(saved.round,5):0;
  state.size=typeof saved.size==='number'&&Number.isFinite(saved.size)?Math.max(.85,Math.min(1.45,saved.size)):1;
  state.timer=saved.timer!==false;state.motion=['normal','slow','static'].includes(saved.motion)?saved.motion:state.motion;
  state.scene=SCENES.has(saved.scene)?saved.scene:'S01';
  state.history=(Array.isArray(saved.history)?saved.history:[]).filter(x=>SCENES.has(x)&&x!=='R01').slice(-24);
  state.ending=['ordinary','secret'].includes(saved.ending)?saved.ending:null;
  // Damaged saves cannot skip uncompleted stages or claim an unearned secret ending.
  const gated = ['S05','S06','S07','H01','S08','S09','S10','H02','H03','E01','E02'];
  const required = ['S05','S06','S07','H01'].includes(state.scene)?1:['S08','S09'].includes(state.scene)?2:gated.includes(state.scene)?3:0;
  for(let i=0;i<required;i++) if(state.completed[i].length!==GROUPS[i].length) {state.stage=i;state.scene=LEARN_SCENES[i];state.history=[];state.ending=null;break;}
  const q=QUIZ_SCENES.indexOf(state.scene);
  if(q>=0) {state.stage=q;if(state.learned[q].length!==GROUPS[q].length)state.scene=LEARN_SCENES[q];if(state.hearts===0)state.scene='R01';}
  if(['H02','H03','E02'].includes(state.scene)&&!state.gem) {state.scene='S10';state.ending=null;}
  if(['H03','E02'].includes(state.scene)&&state.round<5) {state.scene='H02';state.ending=null;}
  return state;
}
export function currentLetter(state) {return state.orders[state.stage].find(x=>!state.completed[state.stage].includes(x))||null;}
export function recordCorrect(state, letter, assisted=false) {
  const i=state.stage;
  if(!GROUPS[i].includes(letter)||state.completed[i].includes(letter))return false;
  state.completed[i].push(letter);state[assisted?'assisted':'independent'][i].push(letter);return true;
}
export function loseHeart(state) {state.hearts=Math.max(0,state.hearts-1);return state.hearts===0;}
export function resetCurrentStage(state) {
  const i=state.stage;state.completed[i]=[];state.assisted[i]=[];state.independent[i]=[];
  state.orders[i]=shuffled(GROUPS[i]);state.hearts=3;state.scene=QUIZ_SCENES[i];
}
export function choicesFor(state, count) {
  const target=currentLetter(state);const pool=GROUPS.slice(0,state.stage+1).join('').split('').filter(x=>x!==target);
  const result=shuffled([target,...shuffled(pool).slice(0,count-1)]).map(x=>state.stage===0?x:state.stage===1?x.toLowerCase():Math.random()<.5?x:x.toLowerCase());
  if(state.stage===2){if(result.every(x=>x===x.toUpperCase()))result[0]=result[0].toLowerCase();else if(result.every(x=>x===x.toLowerCase()))result[0]=result[0].toUpperCase();}
  return result;
}
