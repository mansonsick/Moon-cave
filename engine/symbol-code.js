// Published v1 mapping is stable, just like the worksheet code. Icons are native
// vectors so a printed black-and-white legend matches every browser exactly.
const icons = [
  ['太陽','<circle cx="32" cy="32" r="13"/><path d="M32 3v7m0 44v7M3 32h7m44 0h7M11 11l5 5m32 32 5 5M11 53l5-5m32-32 5-5"/>'],
  ['月亮','<path d="M48 9A25 25 0 1 0 53 49 25 25 0 0 1 48 9Z"/>'],
  ['星星','<path d="m32 5 8 18 20 2-15 14 5 20-18-10-18 10 5-20L4 25l20-2Z"/>'],
  ['愛心','<path d="M32 56 8 32C-5 10 23 0 32 20 41 0 69 10 56 32Z"/>'],
  ['葉子','<path d="M10 52C-1 12 32 6 57 7 58 34 42 64 10 52ZM7 58 47 18m-27 27-2-16m12 6 16 0"/>'],
  ['花朵','<path d="M32 45v15m0-7 13-6M32 18C16-5 2 19 19 29-4 39 18 57 30 41 40 62 60 40 43 30 65 19 42-2 32 18Z"/><circle cx="31" cy="30" r="7"/>'],
  ['小魚','<path d="M47 23 61 12v40L47 41C21 67 1 32 3 32 1 32 21-3 47 23Z"/><circle cx="19" cy="29" r="2" fill="currentColor"/><path d="m30 17 3 10m-3 20 3-10"/>'],
  ['房子','<path d="M4 29 32 5l28 24M11 24v35h42V24M27 59V39h13v20M19 28h8v8h-8Z"/>'],
  ['蘋果','<path d="M32 20C7 6 1 34 14 52c7 12 15 4 18 5 4-1 12 7 19-5 14-20 5-45-19-32Zm0 0V7m2 9C33 4 45 3 52 5 49 15 40 19 34 16Z"/>'],
  ['雨傘','<path d="M4 34a28 28 0 0 1 56 0c-6-5-12-5-18 0-6-5-14-5-20 0-6-5-12-5-18 0ZM32 4v30m0 0v18c0 13 17 13 17 0"/>'],
];
export const SYMBOL_VERSION='symbols-v1';
export function symbolName(digit){return icons[Number(digit)]?.[0] || '';}
export function symbolMarkup(digit){
  if(!/^[0-9]$/.test(String(digit)))return '';
  const [name,paths]=icons[Number(digit)];
  return `<svg class="code-symbol" viewBox="0 0 64 64" role="img" aria-label="${name}" fill="none" stroke="currentColor" stroke-width="3.4" stroke-linecap="round" stroke-linejoin="round">${paths}</svg>`;
}
export function codeLegend(){
  const table=document.createElement('div');table.className='code-legend';table.setAttribute('aria-label','數字圖案對照表');
  for(let digit=0;digit<10;digit++){
    const cell=document.createElement('div');cell.className='legend-cell';
    const number=document.createElement('b');number.textContent=digit;
    const icon=document.createElement('span');icon.innerHTML=symbolMarkup(digit);cell.append(number,icon);table.append(cell);
  }
  return table;
}
