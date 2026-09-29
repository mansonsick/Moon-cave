"""V2 configurable worksheets, multi-digit symbol entry and print layout.
Run after story_03_test.py (which freezes v1 and covers both story endings).
"""
import argparse
import json
from pathlib import Path
from playwright.sync_api import sync_playwright
from story_test_support import serve
from story_03_test import act, ready, scene, state, enter

RESULTS = []
DEFAULT_EQUATIONS = ['7+2','7+3','5-3','9-6','4+4','6-1','97-5','21+4','34-1','68+9','55-2','99+7','20+3','71+47','56+29','70-36','86+61','68+38','77-74','80-45']
CUSTOM_EQUATIONS = ['15*83','84*44','45*85','68*70','26*18','80*55','58/2','50/1','48/2','12/4','54/3','76/2','33/1','18+82','98-31','65*80','17*44','36+64','65-58','77/11']

def record(name):
    print('PASS', name, flush=True)
    RESULTS.append(name)

def answer(q):
    a,b,op=q['a'],q['b'],q['op']
    return str({'+':lambda:a+b,'-':lambda:a-b,'*':lambda:a*b,'/':lambda:a//b}[op]())

def passwords(gate):
    values=[int(answer(q)) for q in gate['questions']]
    return [str(max(values)),str(min(values))]

def solve(page,gate):
    for i,value in enumerate(passwords(gate)): enter(page,i,value)
    act(page,'check')
    assert page.locator('.password-card.correct').count()==2
    assert page.locator('.password-card .answer-mark').all_text_contents()==['✓']*2
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
          const loaded=s.validate(save);if(loaded.entries[0].join('|')!=='|9801||||')throw Error('multidigit save');
          // Old completed gates/endings migrate, while partial answers remain optional review only.
          const legacy={...s.fresh(customCode),schema:1,scene:'secret',seed:true,wood:true,placed:true};
          legacy.entries=[0,1,2].map(g=>m.gateAnswers(m.createWorksheet(customCode),g));
          const migrated=s.validate(legacy);
          if(migrated.scene!=='secret'||!migrated.solved.every(Boolean)||migrated.schema!==3)throw Error('legacy completion lost');
          if(JSON.stringify(migrated.passwords)!==JSON.stringify([0,1,2].map(g=>m.gatePasswords(m.createWorksheet(customCode),g))))throw Error('legacy password migration');
          legacy.entries[1][0]='';const partial=s.validate(legacy);
          if(partial.scene!=='gate2'||partial.passwords[1].join('')!==''||partial.solved[1])throw Error('partial work unlocked');
          if(JSON.stringify(partial.entries[1])!==JSON.stringify(legacy.entries[1]))throw Error('partial review lost');
          const reviewOnly=s.fresh(customCode);reviewOnly.entries=legacy.entries;
          if(s.validate(reviewOnly).solved.some(Boolean))throw Error('review unlocked door');
          const repeated={gates:[{questions:[{a:4,b:3,op:'-'},{a:2,b:1,op:'-'}]}]};
          if(m.gatePasswords(repeated,0).join()!=='1,1'||!m.checkPasswords(repeated,0,['1','1']).every(Boolean))throw Error('tied extrema');
          if(m.checkPasswords(repeated,0,['01','01']).some(Boolean))throw Error('padded values');
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
        expected=passwords(props['w']['gates'][0])
        enter(page,0,'9' if expected[0]!='9' else '8');enter(page,1,expected[1]);act(page,'check')
        assert page.locator('.password-card').nth(0).get_attribute('class').endswith('wrong')
        assert page.locator('.password-card').nth(1).get_attribute('class').endswith('correct')
        assert page.locator('[data-answer="1"] .numbered-symbol').count()==len(expected[1])
        page.reload();ready(page);assert page.locator('.password-card.correct').count()==1
        # Single-digit values need no zero padding or extra empty slots.
        solve(page,props['w']['gates'][0]);page.reload();ready(page)
        act(page,'continue');act(page,'continue');solve(page,props['w']['gates'][1]);act(page,'continue')
        act(page,'upstairs');solve(page,props['w']['gates'][2]);act(page,'continue');act(page,'open-chest');act(page,'continue');act(page,'go-home');scene(page,'ordinary')
        record('20 unchanged questions, just two extrema per gate, variable-length entries without padding, green/red feedback, refresh and muted ordinary route')
        # Import a custom packet and solve all four operations without changing the old packet.
        page.goto(url+'?code='+props['customCode']);ready(page);act(page,'yes-change');scene(page,'cover')
        page.locator('.prepare summary').click()
        assert page.locator('[name="ops-0"]:checked').input_value()=='*'
        act(page,'start');act(page,'continue');scene(page,'gate1')
        assert page.locator('[data-answer]').count()==2
        assert page.locator('[data-answer] .numbered-symbol').count()==0
        enter(page,0,'9801');page.reload();ready(page);assert state(page)['passwords'][0][0]=='9801'
        act(page,'erase');assert page.locator('[data-answer="0"] .numbered-symbol').count()==3
        act(page,'clear-answer');act(page,'check');assert page.locator('.password-card.wrong').count()==2
        enter(page,0,'0007');assert state(page)['passwords'][0][0]=='7'
        act(page,'clear-answer')
        act(page,'review-questions');assert page.locator('.count-dot').count()==0;act(page,'close')
        solve(page,props['custom']['gates'][0]);act(page,'continue');act(page,'continue');solve(page,props['custom']['gates'][1]);act(page,'continue')
        act(page,'find-wood');act(page,'continue');act(page,'upstairs');solve(page,props['custom']['gates'][2]);act(page,'continue');act(page,'open-chest');act(page,'continue')
        # Same accessible drag target path as the legacy pointer-drag test.
        page.locator('[data-item="wood"]').focus();page.keyboard.press('Enter');page.keyboard.press('Enter')
        assert state(page)['placed'];act(page,'continue');scene(page,'secret');act(page,'continue');scene(page,'secret-home')
        record('four-digit extrema, automatic removal of leading zeros, backspace, legacy migration, tied extrema, all operations and secret route')
        before=state(page);printing=context.new_page()
        for name,packet in [('default',props['w']),('custom',props['custom'])]:
            printing.goto(url+'print.html?code='+packet['code']);ready(printing)
            assert printing.locator('.paper').count()==3
            assert printing.locator('.paper-dots,.dot,.marker').count()==0
            assert printing.locator('[aria-label*="劃掉"]').count()==0
            assert all(v=='' for v in printing.locator('.answer-box').all_text_contents())
            assert printing.locator('.answer-box').count()==20
            assert printing.locator('.paper-password-answer').all_text_contents()==['']*6
            assert printing.locator('.packet-code').all_text_contents()==[packet['code']]*3
            assert printing.locator('.paper-row').evaluate_all('''rows=>rows.every(r=>{
              const eq=r.querySelector('.equation').getBoundingClientRect(),box=r.querySelector('.answer-boxes').getBoundingClientRect();
              return eq.right+10<box.left&&Math.abs(eq.top-box.top)<40;
            })''')
            printing.pdf(path=str(out/f'{name}.pdf'),prefer_css_page_size=True,print_background=True)
            for g in range(3):printing.locator('.paper').nth(g).screenshot(path=str(out/f'{name}-paper-{g+1}.png'))
            printing.goto(url+'print.html?code='+packet['code']+'&mode=answers');ready(printing)
            assert printing.locator('.answer-boxes').all_text_contents()==[answer(q) for gate in packet['gates'] for q in gate['questions']]
            assert printing.locator('.paper-password-answer').all_text_contents()==[v for gate in packet['gates'] for v in passwords(gate)]
        assert state(page)==before
        record('3 A4 pages for default/four-digit packets, no circles or subtraction note, separate answers, consistent code, no overlap or storage mutation')
        for width,height in [(390,844),(820,1180),(1180,820)]:
            mobile=browser.new_page(viewport={'width':width,'height':height});mobile.goto(url+'?code='+props['customCode']);ready(mobile)
            for _ in range(6):act(mobile,'larger')
            mobile.locator('.prepare summary').click()
            assert mobile.evaluate('document.documentElement.scrollWidth<=innerWidth')
            act(mobile,'start');act(mobile,'continue');ready(mobile)
            assert mobile.evaluate('document.documentElement.scrollWidth<=innerWidth')
            enter(mobile,0,'9801');assert state(mobile)['passwords'][0][0]=='9801'
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
        legacy_save={'schema':1,'version':props['custom']['version'],'code':props['customCode'],'scene':'secret','seed':True,'wood':True,'placed':True,'scale':1,
            'entries':[[answer(q) for q in gate['questions']] for gate in props['custom']['gates']],
            'checked':[[True]*len(gate['questions']) for gate in props['custom']['gates']]}
        migration=browser.new_context();migration.add_init_script("localStorage.setItem('adventure.story-03.state',"+json.dumps(json.dumps(legacy_save))+ ")")
        upgraded=migration.new_page();upgraded.goto(url+'?code='+props['customCode']);ready(upgraded);scene(upgraded,'secret')
        assert state(upgraded)['schema']==3
        assert state(upgraded)['passwords']==[passwords(gate) for gate in props['custom']['gates']]
        assert state(upgraded)['placed'] and state(upgraded)['seed']
        migration.close();record('browser startup upgrades a completed schema-1 save without losing the secret ending or items')
        assert not errors,errors;assert not missing,missing
        browser.close()
    server.shutdown();(out/'results.json').write_text(json.dumps({'passed':RESULTS},ensure_ascii=False,indent=2),encoding='utf-8')
    print(f'{len(RESULTS)} groups passed')

if __name__=='__main__':main()
