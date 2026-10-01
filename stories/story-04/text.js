export async function loadText() {
  const r=await fetch(new URL('./assets/text/text.json',import.meta.url));
  if(!r.ok)throw new Error('Missing text assets');const manifest=await r.json();
  return function text(id,className='') {
    const entry=manifest.labels[id];if(!entry)throw new Error('Missing label '+id);
    const span=document.createElement('span');span.className='bpmf '+className;span.setAttribute('role','img');span.setAttribute('aria-label',entry.text);
    for(const part of entry.parts){const image=document.createElement('img');image.src=new URL('./assets/text/'+part.src,import.meta.url);image.alt='';image.draggable=false;image.width=part.width;image.height=part.height;image.style.width=(part.width/part.height*1.12)+'em';span.append(image);}
    return span;
  };
}
export function button(text,label,click,action=label) {
  const b=document.createElement('button');b.type='button';b.append(text(label));b.dataset.action=action;b.addEventListener('click',click);return b;
}
