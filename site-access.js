/* This is only a visitor reminder. Anyone can bypass it or fetch public files.
 * Never reuse a real account password here; no server validates this gate.
 */
(() => {
  const base=new URL('./',document.currentScript.src);
  const key='adventure.session.siteAccess';let labels,config;
  const text=id=>{
    const span=document.createElement('span');span.className='access-text';span.setAttribute('role','img');span.setAttribute('aria-label',labels[id].text);
    for(const part of labels[id].parts){const img=new Image();img.src=new URL('legal/assets/text/'+part.src,base);img.alt='';img.width=part.width;img.height=part.height;span.append(img);}return span;
  };
  const remembered=()=>{try{return sessionStorage.getItem(key)===config.sha256;}catch{return false;}};
  const ready=()=>document.readyState==='loading'?new Promise(r=>document.addEventListener('DOMContentLoaded',r,{once:true})):Promise.resolve();
  async function start(){
    try {
      [config,labels]=await Promise.all([fetch(new URL('site-access.json',base),{cache:'no-store'}).then(r=>{if(!r.ok)throw Error('access config');return r.json();}),fetch(new URL('legal/assets/text/text.json',base)).then(r=>{if(!r.ok)throw Error('access labels');return r.json();}).then(m=>m.labels)]);
      await ready();
      if(remembered()){document.documentElement.dataset.siteAccess='granted';footer();return;}
      const gate=document.createElement('section');gate.className='site-access';gate.setAttribute('role','dialog');gate.setAttribute('aria-modal','true');gate.setAttribute('aria-label',labels['access-title'].text);
      const form=document.createElement('form');const title=document.createElement('h1');title.append(text('access-title'));
      const help=document.createElement('p');help.append(text('access-help'));
      const label=document.createElement('label');label.htmlFor='family-password';label.append(text('access-label'));
      const input=document.createElement('input');input.id='family-password';input.type='password';input.inputMode='numeric';input.autocomplete='off';input.maxLength=12;input.required=true;
      const submit=document.createElement('button');submit.type='submit';submit.append(text('access-submit'));
      const error=document.createElement('p');error.className='access-error';error.setAttribute('role','status');error.setAttribute('aria-live','polite');
      const note=document.createElement('p');note.className='access-small';note.append(text('access-public'));
      const legal=document.createElement('a');legal.href=new URL('legal/',base);legal.append(text('site-link'));
      form.append(title,help,label,input,submit,error,note,legal);gate.append(form);
      const hidden=[...document.body.children].map(n=>[n,n.inert]);for(const [n] of hidden)n.inert=true;
      document.body.append(gate);input.focus({preventScroll:true});
      gate.addEventListener('keydown',e=>{if(e.key!=='Tab')return;const list=[input,submit,legal].filter(n=>!n.disabled);const i=list.indexOf(document.activeElement);if(e.shiftKey&&i<=0){e.preventDefault();list.at(-1).focus();}else if(!e.shiftKey&&i===list.length-1){e.preventDefault();list[0].focus();}});
      form.addEventListener('submit',async e=>{
        e.preventDefault();submit.disabled=true;error.replaceChildren();
        try{
          const buffer=await crypto.subtle.digest('SHA-256',new TextEncoder().encode(input.value.trim()));
          const hash=[...new Uint8Array(buffer)].map(n=>n.toString(16).padStart(2,'0')).join('');
          if(hash!==config.sha256){error.append(text('access-error'));input.select();return;}
          try{sessionStorage.setItem(key,hash);}catch{/* This page still opens when browser storage is denied. */}
          document.documentElement.dataset.siteAccess='granted';for(const [n,inert] of hidden)n.inert=inert;gate.remove();footer();
          const first=document.querySelector('main a, main button, #app button');first?.focus({preventScroll:true});
        }catch{error.append(text('access-unavailable'));}finally{submit.disabled=false;}
      });
    }catch{
      await ready();const gate=document.createElement('section');gate.className='access-nojs';
      const image=new Image();image.src=new URL('legal/assets/text/access-unavailable-0.png',base);image.alt='入口驗證暫時無法載入，請重新整理。';gate.append(image);document.body.append(gate);
    }
  }
  function footer(){
    if(document.querySelector('.site-links'))return;
    const links=document.createElement('footer');links.className='site-links';
    const legal=document.createElement('a');legal.href=new URL('legal/',base);legal.append(text('site-link'));
    const logout=document.createElement('button');logout.type='button';logout.append(text('logout'));
    logout.addEventListener('click',()=>{try{sessionStorage.removeItem(key);}catch{}location.reload();});
    links.append(legal,logout);document.body.append(links);
  }
  void start();
})();
