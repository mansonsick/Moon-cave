"""Build Story 04 data from its approved prose and original practice plan."""
import json, re
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1]
STORY=ROOT/'stories/story-04'
labels={}
def label(key,value):
    labels[key]=value
    return key

ui={
'title':'阿通與森林郵局','start':'開始冒險','resume':'繼續冒險','continue':'繼續','home':'回首頁','menu':'回本書選單',
'replay':'再玩一次','cancel':'先不要','yes-replay':'重新開始','reset-help':'只重新開始這一本故事。','code':'題卷碼',
'apply-code':'使用這份題卷','new-paper':'產生新題卷','paper':'列印練習紙','answers':'家長解答','print':'列印',
'code-help':'紙本和平板要用相同的題卷碼。','bad-code':'題卷碼不正確，請再看一次。','change-help':'換題卷會重新開始這一本。',
'paper-help':'先學圖卡，再完成紙本練習。','no-printer':'沒有紙本，也能在平板練習。','learn':'一起學習','practice':'練習看看',
'learn-help':'大人陪孩子一起念，也看看圖。','next-card':'下一張圖卡','previous-card':'上一張圖卡','learn-done':'學完了，來練習',
'review':'回看學習卡','check':'核對答案','correct':'答對了！','try':'再看一次，也可以回學習卡。','hint':'看看提示',
'together':'一起讀一讀','adult-confirm':'大人確認共同完成','adult-help':'請大人陪孩子讀題、指圖，再確認完成。',
'station-done':'這一站完成了！','representative':'核對這兩題，再繼續送信。','not-all':'這裡核對兩題，其他紙本題請大人核對。',
'all-mode':'平板練習全部題目','two-mode':'核對紙本代表題','next-question':'下一題','finish-practice':'完成練習',
'bag':'郵差包','leaf-name':'金色葉片','badge':'郵差徽章','letters':'送信進度','got-leaf':'阿通把葉片收好了！',
'delivered':'信送到了！','wrong-place':'再看看小紙，找出正確的位置。','wrong-road':'這裡是山邊。小兔在木橋那邊。',
'observe-box':'箱上刻著一片葉。','into-office':'走進郵局','prepared':'準備好了','mountain-road':'往山邊走','bridge-road':'往木橋走',
'door-tray':'門口的信盤','tree-basket':'樹下的籃子','table-top':'桌上','under-table':'桌下','walk-tree':'往大樹走',
'root-tray':'樹下的信盤','nest':'樹上的鳥巢','back-office':'回郵局','visit-tree':'到樹下看看','ending':'我們把話送到了！',
'optional-break':'休息一下，動一動。','bird-break':'張開雙手，像小鳥飛一下。','clap-break':'拍手三下，再出發。','break-done':'休息好了',
'paper-title':'森林郵局探險紙','answer-title':'森林郵局家長解答','choose-help':'讀一讀，圈選一個答案。','name':'姓名',
'passage-title':'一起讀小段落','sheet-1':'第一站：看圖認字','sheet-2':'第二站：讀懂詞語','sheet-3':'第三站：短句找線索',
'writing':'想寫寫看，也可以練習。','card-picture':'看看圖','card-shape':'記住形狀','card-read':'讀一讀','word-cards':'再看一次圖卡',
'learn-stages':'先看圖，再讀詞，最後讀短句。','paper-warning':'練習紙不含解答。','answer-warning':'這份是大人核對用的解答。',
'load-error':'故事暫時沒有載入。請重新整理。','loading':'故事準備中。','saved':'進度已保留。','return-story':'回故事',
'sample':'先一起看一個例子。','reread':'讀句子，找出裡面的線索。','empty-answer':'先選一個答案吧。',
'learn-unfinished':'先把這一站的圖卡看完吧。','stage-ready':'路牌修好了！','sign-note':'請把信放在門口。','bear-note':'把信放在桌上。',
'bird-note':'我在樹上。請把信放在樹下。','secret-note':'請來樹下。一起種花。','atong-name':'阿通','squirrel-name':'小松鼠',
'hub-chapter':'阿通的第四場冒險','hub-first':'看看圖，讀一讀，','hub-second':'一起把信送到森林朋友手中。',
}
for k,v in ui.items():label(k,v)

spec=(STORY/'STORY_SPEC.md').read_text(encoding='utf-8')
scenes={}
for m in re.finditer(r'^### ((?:S|H|E)\d{2}) (.*?)\n(.*?)(?=^### |^## |\Z)',spec,re.M|re.S):
    sid,title,body=m.groups()
    lines=[x[1:-1] for x in body.splitlines() if x.startswith('「') and x.endswith('」')]
    scenes[sid]={'title':label(sid+'-title',title),'lines':[label(sid+f'-line-{i}',s) for i,s in enumerate(lines)]}
assert len(scenes)==15
visuals={
'S01':('postoffice-opening','walking',[16,20,26,74]),'S02':('postoffice-inside','walking',[10,20,26,72]),
'S03':('postoffice-inside','reading',[8,22,25,70]),'S04':('bridge-fork','walking',[12,27,24,70]),
'S05':('rabbit-door','reading',[30,24,26,72]),'S06':('bridge-fork','reading',[17,24,24,70]),
'S07':('bear-room','reading',[8,22,25,72]),'S08':('leaf-path','walking',[35,24,26,72]),
'H01':('leaf-path','leaf',[31,12,34,83]),'S09':('big-tree','looking',[19,20,25,73]),
'S10':('big-tree','delivering',[31,38,30,55]),'S11':('old-mailbox','walking',[26,24,25,69]),
'E01':('postoffice-outside','walking',[11,22,25,73]),'E02':('old-mailbox-open','reading',[25,22,25,72]),
'E03':('garden','gardening',[31,34,28,57])}
for sid,(bg,pose,box) in visuals.items():
    scenes[sid].update(background=bg+'.png',pose='atong-'+pose+'.png',actorBox=box)

learning=[
[("山","mountain","山，像高高低低的山峰。"),("水","water","小溪裡有水。看看流動的水。"),("日","sun","日是太陽。先看圓圓的太陽。"),
 ("月","moon","月是月亮。看看彎彎的月亮。"),("木","tree","木有樹幹、樹枝和樹根。木也可以是木頭。"),("口","mouth","口，像張開的小嘴。")],
[("上","bird-above","小鳥在樹上。上，在比較高的位置。"),("下","tray-below","信盤在樹下。下，在比較低的位置。"),
 ("拿","taking","把信拿起來，信在手裡。"),("放","placing","把信放好，信留在信盤。"),("隻","bird","一隻小鳥。說小鳥時，用隻。"),("朵","flower","一朵花。說花時，用朵。")],
[("門口","door","小兔在門口等信。找一找地點：門口。"),("樹下","tray-below","小鳥在樹上。信要放在樹下。找的是信的位置。"),
 ("阿通","taking","阿通拿信，小松鼠拿花。找一找，誰拿信？"),("先讀，再放","placing","先讀小紙，再把信放好。先讀，再放。"),
 ("一起種花","flower","小兔帶花，小熊拿水。大家一起種花。讀一讀，再找人和動作。")]
]
cards=[]
for stage,entries in enumerate(learning):
    group=[]
    for i,(word,picture,help_text) in enumerate(entries):
        group.append({'word':label(f'learn-{stage}-{i}-word',word),'picture':picture,'help':label(f'learn-{stage}-{i}-help',help_text),
          'shape':picture+'-shape' if stage==0 else None})
    cards.append(group)

prompts=['圈出圖中的字。']*6+['小鳥在樹＿＿。','信盤在樹＿＿。','阿通＿＿起信。','阿通把信＿＿好。','一＿＿小鳥。','一＿＿花。','把信放在桌＿＿。',
 '小兔在哪裡？','信要放在哪裡？','誰拿著信？','先做什麼？','小兔帶了什麼？','誰先到樹下？','最後大家做什麼？']
pics=['mountain','water','sun','moon','wood','mouth','bird-above','tray-below','taking','placing','bird','flower','table-top',None,None,None,None,None,None,None]
passages={14:'小兔在門口等信。',15:'小鳥在樹上。請把信放在樹下。',16:'阿通拿信，小松鼠拿花。',17:'阿通先讀小紙，再把信放好。'}
shared='小兔帶著花，先到樹下。小熊拿著水，也來了。大家一起種花。'
questions=[]
for row in re.findall(r'^\| Q\d{2} \|.*$',(STORY/'PRACTICE_PLAN.md').read_text(encoding='utf-8'),re.M):
    cells=[x.strip() for x in row.split('|')[1:-1]]
    qid,_,choices_text,answer_text=cells
    n=int(qid[1:]);choices=re.findall(r'[ABC] ([^、]+)',choices_text)
    answer=answer_text[2:]
    assert len(choices)==3 and answer in choices
    options=[label(f'{qid}-choice-{i}',x) for i,x in enumerate(choices)]
    questions.append({'id':qid,'stage':0 if n<=6 else 1 if n<=13 else 2,'prompt':label(qid+'-prompt',prompts[n-1]),
      'choices':options,'answer':options[choices.index(answer)],'picture':pics[n-1],
      'passage':label(qid+'-passage',passages[n] if n in passages else shared) if n>=14 else None,
      'hint':label(qid+'-hint', '看看圖，再讀一讀每個選項。' if n<=13 else '再讀一次句子，找題目問的線索。')})
assert len(questions)==20
data={'id':'story-04','poolVersion':'forest-v1','title':'title','scenes':scenes,'labels':labels,'learning':cards,'questions':questions,
 'representatives':[['Q02','Q05'],['Q08','Q13'],['Q15','Q18']],
 'audio':{name:{'category':'sfx','available':True,'src':'../story-02/assets/audio/sfx/'+name+'.wav','volume':.3} for name in ['success','found-item','fail-soft','drag-lock']}}
(STORY/'story.json').write_text(json.dumps(data,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
print(f'Built {len(scenes)} scenes, {len(questions)} original questions, {sum(map(len,cards))} teaching cards, {len(labels)} text labels.')
