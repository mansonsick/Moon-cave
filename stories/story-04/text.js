export async function loadText() {
  const r=await fetch(new URL('./assets/text/text.json',import.meta.url));
  if(!r.ok)throw new Error('Missing text assets');const manifest=await r.json();
  function text(id,className='') {
    const entry=manifest.labels[id];if(!entry)throw new Error('Missing label '+id);
    const span=document.createElement('span');span.className='bpmf '+className;span.setAttribute('role','img');span.setAttribute('aria-label',entry.text);
    for(const part of entry.parts){const image=document.createElement('img');image.src=new URL('./assets/text/'+part.src,import.meta.url);image.alt='';image.draggable=false;image.width=part.width;image.height=part.height;image.style.width=(part.width/part.height*1.12)+'em';span.append(image);}
    return span;
  }
  // A scene sign is a contained image: never let Chinese chunks reflow outside paper.
  text.scene=function(id){
    const entry=manifest.labels[id];if(!entry)throw new Error('Missing scene label '+id);
    const part=entry.scene||entry.parts[0];
    if(!entry.scene&&entry.parts.length!==1)throw new Error('Scene label needs fixed lines '+id);
    const span=document.createElement('span');span.className='scene-writing';span.setAttribute('role','img');span.setAttribute('aria-label',entry.text);
    const img=document.createElement('img');img.src=new URL('./assets/text/'+part.src,import.meta.url);img.alt='';img.draggable=false;img.width=part.width;img.height=part.height;span.append(img);return span;
  };
  return text;
}
export function button(text,label,click,action=label) {
  const b=document.createElement('button');b.type='button';b.append(text(label));b.dataset.action=action;b.addEventListener('click',click);return b;
}
