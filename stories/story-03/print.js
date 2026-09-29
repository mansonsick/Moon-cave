import {createWorksheet, normalizeCode, resultOf, answerCapacity, operatorSign} from '../../engine/math-worksheet.js';
import {loadText,button,readyImages} from './text.js';
import {codeLegend} from '../../engine/symbol-code.js';

// Draw mathematical signs as paths: stable black-and-white print output,
// independent of the printer/PDF viewer's font subsetting.
function symbol(sign) {
  const node=document.createElementNS('http://www.w3.org/2000/svg','svg');
  node.setAttribute('viewBox','0 0 30 30');node.setAttribute('class','math-symbol');node.setAttribute('role','img');node.setAttribute('aria-label',operatorSign(sign)||sign);
  const path=document.createElementNS(node.namespaceURI,'path');
  path.setAttribute('d',{'=':'M4 10H26M4 20H26','+':'M4 15H26M15 4V26','-':'M4 15H26','*':'M6 6L24 24M24 6L6 24','/':'M4 15H26M15 4V8M15 22V26'}[sign]);
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
      instructions.append(text(answers?'answers-warning':'paper-instruction'),text('paper-order')); page.append(instructions);
      page.append(codeLegend());
      gate.questions.forEach((q,i) => {
        const row=document.createElement('div'); row.className='paper-row'; row.style.top=`${79+i*29}mm`;
        const number=document.createElement('span'); number.className='question-number'; number.textContent=String(q.id).padStart(2,'0');
        const equation=document.createElement('div'); equation.className='equation';
        equation.append(String(q.a),symbol(q.op),String(q.b),symbol('='));
        const boxes=document.createElement('div');boxes.className='answer-boxes';boxes.dataset.question=q.id;
        const capacity=answerCapacity(gate);boxes.style.setProperty('--box-width',capacity>3?'24mm':'28mm');
        for(let d=0;d<capacity;d++){
          const box=document.createElement('div'); box.className='answer-box';box.dataset.question=q.id;
          if(answers)box.textContent=String(resultOf(q))[d]||'';boxes.append(box);
        }
        row.append(number,equation,boxes); page.append(row);
      });
      const footer=document.createElement('footer'); footer.textContent=`${worksheet.version} · ${code} · ${g+1}/3`; page.append(footer);
      pages.append(page);
    }
    await readyImages(); print.disabled=false; document.body.dataset.ready='true';
  }
} catch(error) {
  document.querySelector('#pages').textContent='暫時無法準備練習紙，請重新整理。'; console.error(error);
}
