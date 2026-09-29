import {loadText,button} from '../../stories/story-03/text.js';
import {mountCameraAction} from '../../engine/camera-action-panel.js';
const host=document.querySelector('#panel');
try{
  const text=await loadText();let dispose=()=>{},currentKind=null;
  const render=(kind=null)=>{
    dispose();currentKind=kind;host.replaceChildren();const heading=document.createElement('h1');heading.append(text('action-test-title'));host.append(heading);
    const links=document.createElement('nav');links.className='actions';
    for(const action of ['balance','jump','catch'])links.append(button(text,`${action}-title`,()=>render(action),action));
    const back=document.createElement('a');back.href='../../stories/story-03/';back.append(text('back'));links.append(back);host.append(links);
    if(kind)dispose=mountCameraAction(host,{kind,text,button,onContinue:()=>render()});
  };
  render();document.body.dataset.ready='true';window.addEventListener('pagehide',()=>dispose());
  window.addEventListener('pageshow',event=>{if(event.persisted)render(currentKind);});
}catch{host.textContent='暫時無法開啟，請重新整理。';}
