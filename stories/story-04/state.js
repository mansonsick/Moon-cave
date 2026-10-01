import {readingWorksheet,normalizeReadingCode} from '../../engine/reading-worksheet.js';
export function fresh(code) {
  return {schema:1,version:'forest-v1',code,scene:'S01',scale:1,learned:[false,false,false],learning:[0,0,0],
    full:[false,false,false],answers:{},checked:[],assisted:[false,false,false],delivered:[false,false,false],leaf:false,placed:false,badge:false,ending:null};
}
export function passed(config,state,stage) {
  if(!state.learned[stage])return false;
  if(state.assisted[stage])return true;
  const ids=state.full[stage]?config.questions.filter(q=>q.stage===stage).map(q=>q.id):config.representatives[stage];
  return ids.every(id=>state.checked.includes(id)&&state.answers[id]===config.questions.find(q=>q.id===id).answer);
}
export function validate(config,value) {
  const code=normalizeReadingCode(value?.code);
  if(!code||value.schema!==1||value.version!=='forest-v1')return null;
  const state=fresh(code),sheet=readingWorksheet(config,code);
  state.scale=Math.max(.85,Math.min(1.5,Number(value.scale)||1));
  for(let i=0;i<3;i++) {
    for(const key of ['learned','full','assisted'])state[key][i]=value[key]?.[i]===true;
    state.learning[i]=Math.min(config.learning[i].length-1,Math.max(0,Number.isInteger(value.learning?.[i])?value.learning[i]:0));
  }
  for(const q of sheet.questions)if(q.choices.includes(value.answers?.[q.id]))state.answers[q.id]=value.answers[q.id];
  state.checked=sheet.questions.filter(q=>Array.isArray(value.checked)&&value.checked.includes(q.id)).map(q=>q.id);
  for(let i=0;i<3;i++)state.delivered[i]=value.delivered?.[i]===true&&passed(config,state,i)&&(i===0||state.delivered[i-1]);
  state.leaf=value.leaf===true&&state.delivered[1]; state.placed=value.placed===true&&state.leaf&&state.delivered.every(Boolean);
  state.scene=Object.hasOwn(config.scenes,value.scene)?value.scene:'S01';
  const rank=['S01','S02','S03','S04','S05','S06','S07','S08','H01','S09','S10','S11','E01','E02','E03'];
  const at=rank.indexOf(state.scene);
  if(at>=3&&!passed(config,state,0))state.scene='S03';
  else if(at>=5&&!state.delivered[0])state.scene='S05';
  else if(at>=6&&!passed(config,state,1))state.scene='S06';
  else if(at>=7&&!state.delivered[1])state.scene='S07';
  else if(at>=10&&!passed(config,state,2))state.scene='S09';
  else if(at>=11&&!state.delivered[2])state.scene='S10';
  else if(['E02','E03'].includes(state.scene)&&!state.placed)state.scene='S11';
  state.ending=['E01','E03'].includes(state.scene)?(state.scene==='E01'?'ordinary':'secret'):null;
  state.badge=value.badge===true&&state.delivered.every(Boolean);
  return state;
}
