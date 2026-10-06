export async function loadText() {
  const response=await fetch(new URL('./assets/text/text.json',import.meta.url));
  if(!response.ok)throw new Error('Missing Story 06 text');
  const manifest=await response.json();
  return (id,className='')=>{
    const e=manifest.labels[id];if(!e)throw new Error('Missing text: '+id);
    const span=document.createElement('span');span.className='bpmf '+className;
    span.setAttribute('role','img');span.setAttribute('aria-label',e.text);
    for(const part of e.parts){const img=document.createElement('img');img.src=new URL('./assets/text/'+part.src,import.meta.url);img.alt='';img.width=part.width;img.height=part.height;img.draggable=false;img.style.width=(part.width/part.height*1.12)+'em';span.append(img);}
    return span;
  };
}
export function symbolImage(symbol) {
  const img=document.createElement('img');img.src=new URL('./assets/symbols/'+symbol.codePointAt(0).toString(16)+'.png',import.meta.url);img.alt=symbol;img.className='symbol';img.draggable=false;return img;
}
