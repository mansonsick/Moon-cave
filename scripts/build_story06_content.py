"""Compile approved prose and labels; font/official audio stay outside the repository."""
import json,re
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1]
STORY=ROOT/'stories/story-06'
LABELS={
 'title':'阿通與失聲森林','loading':'故事準備中。','home':'回首頁','menu':'故事選單','previous':'上一幕',
 'start':'開始冒險','resume':'繼續冒險','replay':'再玩一次','new-confirm':'換一組聲音，重新冒險嗎？','new-note':'這本的進度會重新開始。','confirm':'開始新冒險','cancel':'先不要',
 'cover-first':'森林的聲音不見了。','cover-second':'跟阿通一起聽聲音，找回歌聲！','cover-third':'每次十八題，先學六個再闖關。',
 'hub-chapter':'阿通的第六場冒險','hub-first':'聽聽注音，找回森林的聲音。','hub-second':'神祕森林，先學再玩。',
 'enter-forest':'往森林裡看看','take-lamp':'接過聽音燈','go-grass':'到草地找聲音','go-stream':'到溪邊找聲音','go-tree':'去看看古樹','go-birds':'幫小鳥找聲音','go-home':'沿著歌聲回家','together':'一起回家',
 'learning':'先聽一聽，再看一看。','learn-touch':'點卡片，聽聽它的聲音。','learn-count':'已認識','learn-next':'下一張','learn-again':'再聽一次','learn-first':'先認識全部六張聲音卡。','learn-return':'回看聲音卡',
 'begin-question':'聽聲音','listen-wait':'先聽清楚，卡片就會出現。','choose':'找找剛才的聲音。','listen-again':'再聽一次','assist':'看符號幫忙','assist-note':'這題用看符號一起找。','audio-unavailable':'聲音暫時聽不到。可以再試一次，或看符號幫忙。','paused':'先休息一下。再按聽聲音繼續。',
 'right':'找到了！','wrong':'再聽一次，慢慢找。','next-question':'下一個聲音','continue':'繼續','stage-one':'蟲兒的聲音回來了！','stage-two':'溪水的聲音回來了！','stage-three':'小鳥的歌聲回來了！',
 'lamp':'聽音燈','bell':'露珠鈴','bell-found':'找到露珠鈴了！','bag':'我的背包','selected':'已拿起','bell-back':'回到大路','completed':'這裡的聲音都回來了。','progress':'找回聲音','ending':'森林的聲音回來了！',
 'settings':'家長設定','motion':'卡片移動','slow':'慢慢飄動','static':'固定位置','audio-review':'試聽全部注音','review-note':'教育部的三十七個注音讀音。點符號可試聽。','credits':'聲音來源','close':'回到故事','font-larger':'字放大','font-smaller':'字縮小','fullscreen':'全螢幕','fullscreen-fail':'這台裝置可用瀏覽器放大畫面。','sound-on':'聲音開啟','sound-off':'聲音關閉','website':'網站說明',
 'summary':'這趟找回的聲音','independent':'自己聽出','assisted':'看符號幫忙','readings':'中文與右側注音，使用本機字型預先渲染。','audio-credit-title':'教育部國語注音符號手冊','audio-credit-note':'注音讀音來自教育部獨立音訊素材包，未改動原始錄音。依姓名標示授權使用。森林背景與操作音效為本專案製作。',
 'sound-check':'聲音試聽完成。','sound-fail':'聲音暫時無法播放，請再試一次。','sound-playing':'聲音播放中。',
 'mistakes':'常錯的聲音','mistakes-tip':'點符號，再聽一次。','mistakes-none':'目前沒有常錯的聲音。','mistakes-note':'答錯的聲音會留下，方便慢慢練。','mistakes-keep':'常錯聲音會留下，方便再練習。','mistakes-count':'答錯','times':'次','confused-with':'常和這個混淆','clear-review':'清除複習紀錄','clear-review-confirm':'要清除常錯聲音的紀錄嗎？','clear-review-note':'故事進度不會改變。','clear-review-yes':'清除紀錄','replay-song':'再聽歌聲',
}
def main():
 spec=(STORY/'STORY_SPEC.md').read_text(encoding='utf-8')
 scenes=[]
 for m in re.finditer(r'^### ((?:S|H|E)\d{2}) ([^\n]+)\n(.*?)(?=^### |^## |\Z)',spec,re.M|re.S):
  sid,title,body=m.groups();LABELS[sid+'-title']=title.strip()
  prose=body.split('畫面：')[0].strip();lines=[p.strip() for p in prose.split('\n\n') if p.strip()]
  assert len(lines)==2,(sid,lines)
  for i,line in enumerate(lines):LABELS[f'{sid}-line-{i}']=line
  scenes.append({'id':sid,'title':sid+'-title','lines':[f'{sid}-line-{i}' for i in range(len(lines))]})
 assert len(scenes)==14
 result={'storyId':'story-06','version':1,'labels':LABELS,'scenes':scenes,
         'stages':[{'learn':'S03','quiz':'S04','choices':3,'card':'leaf-card.png','next':'S05','success':'stage-one','ambience':'cricket-song','answerSafe':{'x':17,'y':38,'width':66,'height':25}},
                   {'learn':'S05','quiz':'S06','choices':4,'card':'bubble-card.png','next':'S07','success':'stage-two','ambience':'stream-song','answerSafe':{'x':30,'y':38,'width':64,'height':27}},
                   {'learn':'S08','quiz':'S09','choices':5,'card':'feather-card-v2.png','next':'S10','success':'stage-three','ambience':'bird-song','answerSafe':{'x':8,'y':38,'width':66,'height':27}}]}
 (STORY/'story.json').write_text(json.dumps(result,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
 print('Compiled 14 approved scenes and',len(LABELS),'labels.')
if __name__=='__main__':main()
