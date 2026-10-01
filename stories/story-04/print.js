import {normalizeReadingCode,readingWorksheet} from '../../engine/reading-worksheet.js';
import {loadText,button} from './text.js';
const el=(tag,cls='')=>{const n=document.createElement(tag);n.className=cls;return n;},root=document.querySelector('#app');
async function boot(){
  const response=await fetch('./story.json');if(!response.ok)throw new Error('Missing worksheet');
  const config=await response.json(),text=await loadText(),params=new URL(location.href).searchParams;
  const code=normalizeReadingCode(params.get('code')),answers=params.get('answers')==='1';
  const nav=el('nav','toolbar no-print'),back=el('a','link-button');back.href='./'+(code?'?code='+code:'');back.append(text('return-story'));nav.append(back);root.append(nav);
  if(!code){root.append(text('bad-code'));return;}
  const print=button(text,'print',async()=>{print.disabled=true;try{await Promise.all([...document.images].map(i=>i.decode().catch(()=>{})));window.print();}finally{print.disabled=false;}});nav.append(print);
  const message=el('p','no-print screen-help');message.append(text(answers?'answer-warning':'paper-warning'));root.append(message);
  const sheet=readingWorksheet(config,code);document.title=config.labels[answers?'answer-title':'paper-title']+' '+code;
  if(answers){
    const page=el('section','paper-page answer-page'),title=el('h1');title.append(text('answer-title'));page.append(title);
    const meta=el('p','paper-meta');meta.append(text('code'),' '+code);page.append(meta);const warning=el('p');warning.append(text('answer-warning'));page.append(warning);
    const list=el('div','answer-list');for(const q of sheet.questions){const row=el('div','answer-entry solution');row.dataset.question=q.id;const number=el('strong');number.textContent=q.id+'　'+ 'ABC'[q.choices.indexOf(q.answer)]+'.';row.append(number,text(q.answer));list.append(row);}page.append(list);root.append(page);return;
  }
  for(const [stage,questions] of sheet.stages.entries()){
    const page=el('section','paper-page');page.dataset.stage=stage;const header=el('header'),title=el('h1');title.append(text(answers?'answer-title':'paper-title'));header.append(title);
    const meta=el('div','paper-meta'),codeLabel=el('span');codeLabel.append(text('code'));const literal=el('strong');literal.textContent=code;codeLabel.append(' ',literal);meta.append(codeLabel);
    if(!answers){const name=el('span');name.append(text('name'));name.append(' __________');meta.append(name);}header.append(meta);
    const sub=el('h2');sub.append(text('sheet-'+(stage+1)));header.append(sub);const instruction=el('p');instruction.append(text(answers?'answer-warning':'choose-help'));header.append(instruction);page.append(header);
    const list=el('div','paper-questions');let shared=null;
    for(const q of questions){
      const question=el('article','paper-question');question.dataset.question=q.id;
      if(q.id==='Q18'){shared=el('section','shared-reading');const range=el('strong','q-number');range.textContent='Q18–Q20';const p=el('p','paper-passage');p.append(text(q.passage));shared.append(range,p);list.append(shared);}
      if(q.passage&&Number(q.id.slice(1))<18){const p=el('p','paper-passage');p.append(text(q.passage));question.append(p);}
      const row=el('div','paper-prompt'),number=el('strong','q-number');number.textContent=q.id;
      row.append(number);if(q.picture){const image=el('img','paper-picture');image.src='./assets/practice/'+q.picture+'.svg';image.alt='';row.append(image);}row.append(text(q.prompt));question.append(row);
      const choices=el('div','paper-choices');q.choices.forEach((choice,index)=>{const option=el('div','paper-choice'),letter=el('strong');letter.textContent='ABC'[index]+'.';option.append(letter,text(choice));choices.append(option);});question.append(choices);
      (shared||list).append(question);
    }page.append(list);const footer=el('footer','paper-footer');footer.textContent=(stage+1)+' / 3　'+code;page.append(footer);root.append(page);
  }
}
boot().catch(async()=>{try{const text=await loadText();root.append(text('load-error'));}catch{root.textContent='練習紙暫時沒有載入。請重新整理。';}});
