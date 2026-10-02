"""Compile approved Story 05 prose; PNG text rendering stays in render_story_text.py."""
import json, re
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
STORY = ROOT / 'stories/story-05'
labels = {
    'title':'阿通與霧夜的字母門','start':'開始冒險','resume':'繼續冒險','continue':'繼續','home':'回首頁',
    'menu':'回本書選單','previous':'回上一幕','replay':'再玩一次','confirm-replay':'只重新開始這一本。',
    'yes-replay':'重新開始','cancel':'先不要','loading':'故事準備中。','load-error':'故事暫時沒有載入，請重新整理。',
    'listen':'聽字母','listen-again':'再聽一次','listen-first':'先聽聲音，再找字母。','learning':'一起學大小寫',
    'next-card':'下一張','previous-card':'上一張','start-lamps':'開始點燈','start-candles':'解開燭台鎖',
    'start-bridge':'點亮橋上的燈','review':'回看字母','learn-done':'字母都學過了，來點燈吧！',
    'correct':'答對了！一盞燈亮了。','next-lamp':'下一盞','wrong':'再聽一次，找出那個字母。',
    'monster-wrong':'小心，是納別奇！再聽一次。','timeout':'時間到了，先喘口氣，再聽一次。',
    'retry-question':'再試一次','retry-stage':'重新挑戰','hearts-rule':'有三顆心，點錯字母或怪物會少一顆。',
    'hearts-reset':'三顆心用完，就從這一關重新點燈。','listen-help':'先一起聽，再找一找。',
    'visual-help':'聲音沒有播放。可以看字找一找。','show-letter':'看看字母','assisted':'這題有看字幫忙。',
    'pause':'暫停','unpause':'繼續點燈','paused':'休息一下，字母和時間都停住了。',
    'settings':'家長設定','close':'回故事','timer':'限時挑戰','no-timer':'關閉倒數','movement':'字母移動',
    'normal-motion':'一般','slow-motion':'慢速','static-motion':'停止','settings-help':'可關倒數，也可讓字母慢下來。',
    'sound':'聲音','fullscreen':'全螢幕','exit-fullscreen':'離開全螢幕','fullscreen-help':'這個瀏覽器先用原本畫面。',
    'walk-ahead':'看看前面的路','shelter':'躲進石亭','learn-first':'先一起學字母','bridge':'往橋走','village':'回到村裡',
    'take-stone':'阿通拿出了月亮石！','moonstone':'月亮石','purify-help':'把月亮石的光，照向它。',
    'purify-touch':'也可以先點月亮石，再點它。','light-hit':'照到了！哭聲變小了。','next-light':'再照一次',
    'ordinary-route':'先回到村裡','angel-success':'黑霧散了，是個小天使！','ordinary-success':'我們平安回村了！',
    'secret-success':'月光帶來了一位新朋友！','stage-1':'第一關：黑森林的燈','stage-2':'第二關：空屋的燭台',
    'stage-3':'第三關：霧中的木橋','stage-1-done':'九盞燈亮了！屋子的門出現了。',
    'stage-2-done':'燭台都亮了！通往木橋的後門開了。','stage-3-done':'最後一盞燈，照出了村口！',
    'cover-first':'聽清字母，點亮霧裡的燈，','cover-second':'跟著阿通找到回家的路。',
    'hub-chapter':'阿通的第五場冒險','ending-learned':'我們一起練習了全部字母！','lost-hearts':'躲好後，再從這關開始。',
    'save-help':'前面完成的關卡會保留。','heard':'聽一聽，再看大小寫。','ready':'準備好了','back-learning':'回到學習',
}

spec = (STORY/'STORY_SPEC.md').read_text(encoding='utf-8')
visuals = {
    'S01':('night-path','alert','alert'),'S02':('night-path','running','running'),
    'S03':('stone-shelter','listening','alert'),'S04':('forest-lamps','listening','alert'),
    'S05':('watch-house','alert','alert'),'S06':('watch-house','listening','alert'),
    'S07':('moon-wall','alert','alert'),'H01':('moon-wall','moonlight','alert'),
    'S08':('bridge-gate','listening','alert'),'S09':('bridge-gate','listening','alert'),
    'R01':('rock-hideout','alert','alert'),'S10':('bridge-gate','alert','alert'),
    'H02':('bridge-gate','moonlight','alert'),'H03':('bridge-gate','moonlight','alert'),
    'E01':('dawn-village','alert','alert'),'E02':('dawn-village','moonlight','alert'),
}
scenes = {}
for match in re.finditer(r'^### ((?:S|H|E|R)\d{2}) (.*?)\n(.*?)(?=^### |^## |\Z)', spec, re.M|re.S):
    sid, title, body = match.groups()
    key = sid.lower()
    labels[key+'-title'] = title.split('（')[0].split('：')[-1]
    lines = [line[1:-1] for line in body.splitlines() if line.startswith('「') and line.endswith('」')]
    ids = []
    for i, line in enumerate(lines):
        lid = key+f'-line-{i}'; labels[lid] = line; ids.append(lid)
    bg, person, squirrel = visuals[sid]
    scenes[sid] = dict(title=key+'-title', lines=ids, background=bg, person=person, squirrel=squirrel)
assert len(scenes) == 16
config = dict(id='story-05', version=1, title='title', labels=labels, scenes=scenes,
              stages=[dict(letters=list(group),count=count,seconds=seconds,scene=scene,learn=learn,next=next_scene)
                      for group,count,seconds,scene,learn,next_scene in
                      [('ABCDEFGHI',3,0,'S04','S03','S05'),('JKLMNOPQR',4,12,'S06','S05','S07'),('STUVWXYZ',5,10,'S09','S08','S10')]])
(STORY/'story.json').write_text(json.dumps(config, ensure_ascii=False, indent=2)+'\n', encoding='utf-8')
print(f'Compiled {len(scenes)} scenes and {len(labels)} Chinese labels.')
