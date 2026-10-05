import assert from 'node:assert/strict';
import {freshState,validateState,canVisit} from '../stories/story-06/state.js';
for(let i=0;i<500;i++){const s=freshState();assert.equal(new Set(s.roundSymbols.flat()).size,18);assert.deepEqual(validateState(s).roundSymbols,s.roundSymbols);}
assert.equal(validateState(null),null);
const draw=freshState();assert.equal(validateState({...draw,roundSymbols:[draw.roundSymbols[0],draw.roundSymbols[0],draw.roundSymbols[2]]}),null);
assert.equal(validateState({...draw,poolVersion:'unknown'}),null);
let forged=validateState({...draw,progress:[6,6,6],scene:'E02',bell:true,bellPlaced:true,endings:['secret']});
assert.equal(forged.scene,'S01');assert.deepEqual(forged.progress,[0,0,0]);assert.equal(forged.bell,false);assert.deepEqual(forged.endings,[]);
const s=freshState();s.lamp=true;s.started=true;s.learned[0]=[...s.roundSymbols[0]];
s.results[0]=s.roundSymbols[0].map(symbol=>({symbol,mode:'independent'}));s.progress[0]=6;s.scene='S05';
assert.equal(validateState(s).progress[0],6);assert.equal(canVisit(validateState(s),'S05'),true);assert.equal(canVisit(validateState(s),'S09'),false);
const gap=structuredClone(s);gap.results[0][1]={symbol:'?',mode:'independent'};assert.equal(validateState(gap).progress[0],1);
const wrongMode=structuredClone(s);wrongMode.results[0][0].mode='perfect';assert.equal(validateState(wrongMode).progress[0],0);
const earlier=structuredClone(s);earlier.lamp=false;assert.deepEqual(validateState(earlier).progress,[0,0,0]);
console.log('PASS: 500 distinct 18-symbol draws, retained saved groups, malformed saves, stage gates and contiguous validated results.');
