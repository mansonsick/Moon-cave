// Published worksheet-v1 is immutable. New algorithms must use a new version.
// The code, not the date/device/save progress, determines every question.
import {decodeCode,createV2,calculate,randomCode} from './math-worksheet-v2.js';
export {DEFAULT_CONFIG,OPERATORS,operatorSign} from './math-worksheet-v2.js';
export const VERSION = 'story03-math-v1';
export const GATE_SIZES = [6, 7, 7];
export function normalizeCode(value) {
  if (typeof value !== 'string') return null;
  const code = value.trim().toLowerCase();
  if(code.startsWith('m2-')) return decodeCode(code) ? code : null;
  return /^[a-z0-9]{1,24}$/.test(code) ? code : null;
}
function randomFor(code) {
  let h = 2166136261;
  for (const c of `${VERSION}:${code}`) h = Math.imul(h ^ c.charCodeAt(0), 16777619) >>> 0;
  return () => {
    h = (h + 0x6D2B79F5) >>> 0;
    let t = h;
    t = Math.imul(t ^ (t >>> 15), t | 1);
    t ^= t + Math.imul(t ^ (t >>> 7), t | 61);
    return ((t ^ (t >>> 14)) >>> 0) / 4294967296;
  };
}
function shuffle(list, random) {
  for (let i = list.length - 1; i > 0; i--) {
    const j = Math.floor(random() * (i + 1));
    [list[i], list[j]] = [list[j], list[i]];
  }
  return list;
}
export function resultOf(question) {
  return calculate(question);
}
export function createWorksheet(value) {
  const code = normalizeCode(value);
  if (!code) throw new Error('Invalid worksheet code');
  if(code.startsWith('m2-')) return createV2(code);
  const random = randomFor(code), add = [], subtract = [];
  // One handwritten digit per answer box in v1. Includes minuends of 10.
  for (let a = 1; a <= 8; a++) for (let b = 1; b <= 9 - a; b++) add.push({ a, b, op: '+' });
  for (let a = 1; a <= 10; a++) for (let b = 1; b <= a; b++) subtract.push({ a, b, op: '-' });
  shuffle(add, random); shuffle(subtract, random);
  let number = 0;
  const gates = [[3,3],[4,3],[3,4]].map(([plus, minus], gate) => ({
    id: gate + 1,
    questions: shuffle([...add.splice(0, plus), ...subtract.splice(0, minus)], random)
      .map(q => ({ ...q, id: ++number })),
  }));
  return { version: VERSION, code, gates };
}
export function gateAnswers(worksheet, gate) {
  return worksheet.gates[gate].questions.map(q => String(resultOf(q)));
}
export function checkAnswers(worksheet, gate, entries) {
  return gateAnswers(worksheet, gate).map((expected, i) => entries[i] === expected);
}
export const newCode = randomCode;
export const answerCapacity = gate => gate.answerDigits || 1;
