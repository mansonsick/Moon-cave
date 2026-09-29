"""V2 configurable worksheets, multi-digit symbol entry and print layout.
Run after story_03_test.py (which freezes v1 and covers both story endings).
"""
import argparse
import json
from pathlib import Path
from playwright.sync_api import sync_playwright
from story_test_support import serve
from story_03_test import act, ready, scene, state

RESULTS = []
DEFAULT_EQUATIONS = ['7+2','7+3','5-3','9-6','4+4','6-1','97-5','21+4','34-1','68+9','55-2','99+7','20+3','71+47','56+29','70-36','86+61','68+38','77-74','80-45']
CUSTOM_EQUATIONS = ['15*83','84*44','45*85','68*70','26*18','80*55','58/2','50/1','48/2','12/4','54/3','76/2','33/1','18+82','98-31','65*80','17*44','36+64','65-58','77/11']

def record(name):
    print('PASS', name, flush=True)
    RESULTS.append(name)

def answer(q):
    a,b,op=q['a'],q['b'],q['op']
    return str({'+':lambda:a+b,'-':lambda:a-b,'*':lambda:a*b,'/':lambda:a//b}[op]())

def enter(page,i,value):
    for d,digit in enumerate(value):
        page.locator(f'[data-answer="{i}"][data-position="{d}"]').click()
        page.locator(f'[data-digit="{digit}"]').click()

def solve(page,gate):
    for i,q in enumerate(gate['questions']): enter(page,i,answer(q))
    act(page,'check')
    assert page.locator('.multi-answer-card.correct').count()==len(gate['questions'])
    assert page.locator('.multi-answer-card .answer-mark').all_text_contents()==['✓']*len(gate['questions'])
    assert page.locator('[data-layer="door"]').count()==0

def main():
    parser=argparse.ArgumentParser();parser.add_argument('--output',type=Path,default=Path('../hub-review/story03-difficulty'))
    out=parser.parse_args().output;out.mkdir(parents=True,exist_ok=True)
    server,root=serve();url=root+'stories/story-03/'
    with sync_playwright() as p:
        browser=p.chromium.launch();context=browser.new_context(viewport={'width':820,'height':1180},has_touch=True)
        page=context.new_page();errors=[];missing=[]
        page.on('pageerror',lambda e:errors.append(str(e)))
        page.on('response',lambda r:missing.append(r.url) if r.status>=400 else None)
        page.goto(url);ready(page)
        props=page.evaluate('''async()=>{
          const m=await import('../../engine/math-worksheet.js'),v=await import('../../engine/math-worksheet-v2.js');
          const code=v.encodeCode(v.DEFAULT_CONFIG,'test0001'),w=m.createWorksheet(code);
          const valid=[];
          for(const a of[1,2])for(const b of[1,2])for(let mask=1;mask<16;mask++)for(const within10 of[false,true]){
            const c={leftDigits:a,rightDigits:b,ops:v.OPERATORS.filter((_,i)=>mask&(1<<i)),within10};
            try{v.normalizeConfig([c,c,c]);valid.push(c);}catch{}
          }
          for(const c of valid)for(let n=0;n<8;n++){
            const code=v.encodeCode([c,c,c],('matrix'+n).padStart(8,'0')),w=m.createWorksheet(code),qs=w.gates.flatMap(g=>g.questions);
            if(JSON.stringify(w)!==JSON.stringify(m.createWorksheet(code.toUpperCase())))throw Error('not reproducible');
            if(JSON.stringify(v.decodeCode(code))!==JSON.stringify([c,c,c]))throw Error('settings roundtrip');
            if(qs.length!==20||new Set(qs.map(q=>`${q.a}${q.op}${q.b}`)).size!==20)throw Error('duplicate');
            for(const gate of w.gates){
              const counts=c.ops.map(op=>gate.questions.filter(q=>q.op===op).length);
              if(Math.max(...counts)-Math.min(...counts)>1)throw Error('unbalanced operations');
              for(const q of gate.questions){
                const value=m.resultOf(q);
                if(String(q.a).length!==c.leftDigits||String(q.b).length!==c.rightDigits)throw Error('operand digits');
                if(value<0||!Number.isInteger(value)||q.b===0||(c.within10&&value>10))throw Error('arithmetic range');
                if(String(value).length>gate.answerDigits)throw Error('capacity');
              }
            }
          }
          for(let i=0;i<code.length;i++){
            const bad=code.slice(0,i)+(code[i]==='z'?'y':'z')+code.slice(i+1);
            if(m.normalizeCode(bad)!==null)throw Error('typo accepted');
          }
          const custom=[{leftDigits:2,rightDigits:2,ops:['*'],within10:false},{leftDigits:2,rightDigits:1,ops:['/'],within10:false},{leftDigits:2,rightDigits:2,ops:['+','-','*','/'],within10:false}];
          const customCode=v.encodeCode(custom,'test0002');
          const s=await import('./state.js'),save=s.fresh(customCode);save.entries[0][0]='9 01';save.entries[0][1]='9801';save.entries[0][2]='12345';
          const loaded=s.validate(save);if(loaded.entries[0].join('|')!=='9 01|9801||||')throw Error('multidigit save');
          const newCodes=new Set(Array.from({length:50},()=>m.newCode(custom)));
          if(newCodes.size!==50||[...newCodes].some(c=>JSON.stringify(v.decodeCode(c))!==JSON.stringify(custom)))throw Error('new code');
          return {code,w,customCode,custom:m.createWorksheet(customCode),cases:valid.length*8};
        }''')
        (out/'fixtures.json').write_text(json.dumps(props,indent=2),encoding='utf-8')
        assert props['code']=='m2-240d0f-test0001-gf'
        assert props['customCode']=='m2-0j0x1r-test0002-bx'
        for key,expected in [('w',DEFAULT_EQUATIONS),('custom',CUSTOM_EQUATIONS)]:
            assert [f"{q['a']}{q['op']}{q['b']}" for g in props[key]['gates'] for q in g['questions']]==expected
        record(f"{props['cases']} configurable arithmetic cases, integer division, nonnegative subtraction, code checksums, uniqueness and reproducibility")
        page.goto(url+'?code='+props['code']);ready(page)
        assert state(page)['code']==props['code']
        page.locator('.prepare summary').click()
        for g,(a,b) in enumerate([(1,1),(2,1),(2,2)]):
            assert page.locator(f'[name="leftDigits-{g}"]').input_value()==str(a)
            assert page.locator(f'[name="rightDigits-{g}"]').input_value()==str(b)
        page.screenshot(path=str(out/'settings-tablet.png'),full_page=True)
        # Invalid selection keeps current code and gives a visible explanation.
        for checkbox in page.locator('[name="ops-0"]').all():checkbox.uncheck()
        act(page,'new-code');assert state(page)['code']==props['code']
        assert page.locator('.setup [role="alert"] img').count()>0
        page.reload();ready(page)
        act(page,'sound');act(page,'start');act(page,'continue')
        qs=props['w']['gates'][0]['questions']
        enter(page,0,'9' if answer(qs[0])!='9' else '8');enter(page,1,answer(qs[1]));act(page,'check')
        assert page.locator('.multi-answer-card').nth(0).get_attribute('class').endswith('wrong')
        assert page.locator('.multi-answer-card').nth(1).get_attribute('class').endswith('correct')
        page.reload();ready(page);assert page.locator('.multi-answer-card.correct').count()==1
        # The single-digit answer leaves a spare slot blank; it must still validate.
        solve(page,props['w']['gates'][0]);page.reload();ready(page)
        act(page,'continue');act(page,'continue');solve(page,props['w']['gates'][1]);act(page,'continue')
        act(page,'upstairs');solve(page,props['w']['gates'][2]);act(page,'continue');act(page,'open-chest');act(page,'continue');act(page,'go-home');scene(page,'ordinary')
        record('default progressive 20-question ordinary route, per-question green/red feedback, trailing blank slots, refresh and muted play')
        # Import a custom packet and solve all four operations without changing the old packet.
        page.goto(url+'?code='+props['customCode']);ready(page);act(page,'yes-change');scene(page,'cover')
        page.locator('.prepare summary').click()
        assert page.locator('[name="ops-0"]:checked').input_value()=='*'
        act(page,'start');act(page,'continue');scene(page,'gate1')
        assert page.locator('.digit-slots').first.locator('button').count()==4
        enter(page,0,'9801');page.reload();ready(page);assert state(page)['entries'][0][0]=='9801'
        # Clear all four slots before solving, including possible trailing symbols.
        for d in range(4):page.locator(f'[data-answer="0"][data-position="{d}"]').click();act(page,'erase')
        page.locator('[data-answer="0"][data-position="1"]').click();page.locator('[data-digit="2"]').click();act(page,'check')
        assert page.locator('.multi-answer-card.wrong').count()==6
        page.locator('[data-answer="0"][data-position="1"]').click();act(page,'erase')
        page.locator('.hint-button').first.click();assert page.locator('.count-dot').count()==0;act(page,'close')
        solve(page,props['custom']['gates'][0]);act(page,'continue');act(page,'continue');solve(page,props['custom']['gates'][1]);act(page,'continue')
        act(page,'find-wood');act(page,'continue');act(page,'upstairs');solve(page,props['custom']['gates'][2]);act(page,'continue');act(page,'open-chest');act(page,'continue')
        # Same accessible drag target path as the legacy pointer-drag test.
        page.locator('[data-item="wood"]').focus();page.keyboard.press('Enter');page.keyboard.press('Enter')
        assert state(page)['placed'];act(page,'continue');scene(page,'secret');act(page,'continue');scene(page,'secret-home')
        record('four-digit multiplication, division, all four operations, internal gaps rejected, corrected answers and complete secret route')
        before=state(page);printing=context.new_page()
        for name,packet in [('default',props['w']),('custom',props['custom'])]:
            printing.goto(url+'print.html?code='+packet['code']);ready(printing)
            assert printing.locator('.paper').count()==3
            assert printing.locator('.paper-dots,.dot,.marker').count()==0
            assert printing.locator('[aria-label*="劃掉"]').count()==0
            assert all(v=='' for v in printing.locator('.answer-box').all_text_contents())
            assert printing.locator('.packet-code').all_text_contents()==[packet['code']]*3
            assert printing.locator('.paper-row').evaluate_all('''rows=>rows.every(r=>{
              const eq=r.querySelector('.equation').getBoundingClientRect(),box=r.querySelector('.answer-boxes').getBoundingClientRect();
              return eq.right+10<box.left&&Math.abs(eq.top-box.top)<40;
            })''')
            printing.pdf(path=str(out/f'{name}.pdf'),prefer_css_page_size=True,print_background=True)
            for g in range(3):printing.locator('.paper').nth(g).screenshot(path=str(out/f'{name}-paper-{g+1}.png'))
            printing.goto(url+'print.html?code='+packet['code']+'&mode=answers');ready(printing)
            assert printing.locator('.answer-boxes').all_text_contents()==[answer(q) for gate in packet['gates'] for q in gate['questions']]
        assert state(page)==before
        record('3 A4 pages for default/four-digit packets, no circles or subtraction note, separate answers, consistent code, no overlap or storage mutation')
        for width,height in [(390,844),(820,1180),(1180,820)]:
            mobile=browser.new_page(viewport={'width':width,'height':height});mobile.goto(url+'?code='+props['customCode']);ready(mobile)
            for _ in range(6):act(mobile,'larger')
            mobile.locator('.prepare summary').click()
            assert mobile.evaluate('document.documentElement.scrollWidth<=innerWidth')
            act(mobile,'start');act(mobile,'continue');ready(mobile)
            assert mobile.evaluate('document.documentElement.scrollWidth<=innerWidth')
            enter(mobile,0,'9801');assert state(mobile)['entries'][0][0]=='9801'
            mobile.screenshot(path=str(out/f'multi-{width}.png'),full_page=True);mobile.close()
        record('phone/tablet portrait and landscape with maximum A+, four-symbol entry and settings without horizontal overflow')
        # Generate a new packet from chosen settings and restore it independently via URL.
        other=browser.new_page();other.goto(url);ready(other);other.locator('.prepare summary').click()
        other.locator('[name="leftDigits-0"]').select_option('2');other.locator('[name="rightDigits-0"]').select_option('2')
        for n in other.locator('[name="ops-0"]').all():n.uncheck()
        other.locator('[name="ops-0"][value="*"]').check();act(other,'new-code');new=state(other)['code']
        assert new.startswith('m2-')
        other.locator('.prepare summary').click();assert other.locator('[name="ops-0"]:checked').input_value()=='*'
        restored=browser.new_page();restored.goto(url+'?code='+new);ready(restored);restored.locator('.prepare summary').click()
        assert restored.locator('[name="leftDigits-0"]').input_value()=='2'
        assert restored.locator('[name="ops-0"]:checked').input_value()=='*'
        record('parent settings create a new code; code alone restores settings on another device/session')
        assert not errors,errors;assert not missing,missing
        browser.close()
    server.shutdown();(out/'results.json').write_text(json.dumps({'passed':RESULTS},ensure_ascii=False,indent=2),encoding='utf-8')
    print(f'{len(RESULTS)} groups passed')

if __name__=='__main__':main()
