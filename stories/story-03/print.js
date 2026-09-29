import {createWorksheet, normalizeCode, resultOf, VERSION} from '../../engine/math-worksheet.js';
import {loadText,button,readyImages} from './text.js';
import {codeLegend} from '../../engine/symbol-code.js';

// Draw mathematical signs as paths: stable black-and-white print output,
// independent of the printer/PDF viewer's font subsetting.
function symbol(sign) {
  const node=document.createElementNS('http://www.w3.org/2000/svg','svg');
  node.setAttribute('viewBox','0 0 30 30');node.setAttribute('class','math-symbol');node.setAttribute('role','img');node.setAttribute('aria-label',sign);
  const path=document.createElementNS(node.namespaceURI,'path');
  path.setAttribute('d',sign==='='?'M4 10H26M4 20H26':sign==='+'?'M4 15H26M15 4V26':'M4 15H26');
  path.setAttribute('stroke','#111');path.setAttribute('stroke-width','3');path.setAttribute('fill','none');node.append(path);return node;
}

try {
  const text = await loadText(), params = new URLSearchParams(location.search);
  const code = normalizeCode(params.get('code'));
  const tools = document.querySelector('#print-tools'), pages = document.querySelector('#pages');
  pages.replaceChildren();
  const back = document.createElement('a'); back.href = code ? `./?code=${code}` : './'; back.append(text('back')); tools.append(back);
  if (!code) {
    pages.append(text('invalid-code')); document.body.dataset.ready = 'invalid';
  } else {
    const worksheet = createWorksheet(code), answers = params.get('mode') === 'answers';
    const print = button(text,'print-now',async () => {await readyImages(); window.print();});
    print.disabled = true; tools.append(print, text('print-help'));
    const companion = document.createElement('a');
    companion.href = `?code=${code}${answers ? '' : '&mode=answers'}`;
    companion.append(text(answers ? 'print' : 'answers')); tools.append(companion);
    for (const [g,gate] of worksheet.gates.entries()) {
      const page = document.createElement('section'); page.className = `paper${answers?' answer-paper':''}`;
      page.dataset.gate = g + 1;
      const title = document.createElement('h1'); title.append(text(answers?'answers-title':'title')); page.append(title);
      const subtitle = document.createElement('h2'); subtitle.append(text(`gate${g+1}-label`),text(`gate${g+1}-name`)); page.append(subtitle);
      const packet = document.createElement('div'); packet.className='paper-code'; packet.append(text('code'));
      const stamp = document.createElement('strong'); stamp.className='packet-code'; stamp.textContent=code;
      packet.append(stamp); page.append(packet);
      const instructions = document.createElement('div'); instructions.className='paper-instructions';
      instructions.append(text(answers?'answers-warning':'paper-instruction'),text(answers?'paper-order':'paper-subtract')); page.append(instructions);
      page.append(codeLegend());
      gate.questions.forEach((q,i) => {
        const row=document.createElement('div'); row.className='paper-row'; row.style.top=`${79+i*29}mm`;
        const number=document.createElement('span'); number.className='question-number'; number.textContent=String(q.id).padStart(2,'0');
        const equation=document.createElement('div'); equation.className='equation';
        equation.append(String(q.a),symbol(q.op),String(q.b),symbol('='));
        const picture=document.createElement('div'); picture.className='paper-dots';
        const dots=(n)=>{const group=document.createElement('span'); group.className='dot-group'; for(let j=0;j<n;j++){const dot=document.createElement('i');dot.className='dot';group.append(dot);}return group;};
        picture.append(dots(q.a));
        if(q.op==='+')picture.append(symbol('+'),dots(q.b));
        const box=document.createElement('div'); box.className='answer-box'; box.dataset.question=q.id;
        if(answers) box.textContent=resultOf(q);
        row.append(number,equation,picture,box); page.append(row);
      });
      for(const [x,y] of [[153,75],[190,75],[153,79+gate.questions.length*29],[190,79+gate.questions.length*29]]){
        const marker=document.createElement('i');marker.className='marker';marker.style.left=`${x}mm`;marker.style.top=`${y}mm`;page.append(marker);
      }
      const footer=document.createElement('footer'); footer.textContent=`${VERSION} · ${code} · ${g+1}/3`; page.append(footer);
      pages.append(page);
    }
    await readyImages(); print.disabled=false; document.body.dataset.ready='true';
  }
} catch(error) {
  document.querySelector('#pages').textContent='暫時無法準備練習紙，請重新整理。'; console.error(error);
}
