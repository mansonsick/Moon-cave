# 第五本美術試閱

本輪是故事與美術，尚未加入遊戲。以下全部是本專案以內建 imagegen 製作的圖；角色／道具為透明 PNG，背景與文字分層。[完整故事](STORY_SPEC.md)、[圖片清單](assets/ASSET_MANIFEST.json)、[製作指令](assets/images/PROMPTS.json)。

## 修訂後的角色基準

納別奇和小天使的身體高度相近，披風為暗紅色舊破布，背後是黑色破舊翅膀，懸飛在空中。這張只供檢查造型，含祕密結局，不能直接作封面或正式故事場景。前兩版保留為被取代的初稿。

![小體型紅披風黑破翅納別奇與天使](assets/images/anchor-v3.png)

## 場景順序

背景先保留清楚的道路與出口，遊戲工程再加霧／暗罩，逐盞亮燈後移除遮罩。背景沒有字母或角色。

### 回村夜路

![回村夜路](assets/images/backgrounds/night-path.png)

### 石亭：先學第一組字母

![石亭](assets/images/backgrounds/stone-shelter.png)

### 第一關：森林點燈

![森林點燈](assets/images/backgrounds/forest-lamps.png)

### 第二關：守夜屋燭台

![守夜屋](assets/images/backgrounds/watch-house.png)

### 屋後：隱藏月亮記號

![屋後的牆](assets/images/backgrounds/moon-wall.png)

### 第三關與五輪月光：逃生橋

![逃生橋與村口](assets/images/backgrounds/bridge-gate.png)

### 重試插曲：安全的石縫

![安全石縫](assets/images/backgrounds/rock-hideout.png)

### 普通／祕密收尾：晨光村路

![晨光村路](assets/images/backgrounds/dawn-village.png)

## 阿通的四種動作

| 觀察／躲藏 | 跑與回頭 | 聽字母 | 月光照射 |
| --- | --- | --- | --- |
| ![觀察](assets/images/characters/atong-alert.png) | ![奔跑](assets/images/characters/atong-running.png) | ![聽音](assets/images/characters/atong-listening.png) | ![月光](assets/images/characters/atong-moonlight.png) |

## 松鼠、怪物與天使

角色的 PNG 畫布各自含透明留白，不能直接以相同圖片框高度當成人物身高。manifest 的 visibleBounds 供透明留白與碰撞範圍參考；工程另以身體高度縮放，使三種納別奇狀態約與小天使一致、阿通較高，不能把展翼範圍當作身高。最終場景比例尚待工程校正。門縫中的眼睛由角色和門葉的遮罩層呈現；沒有另外烘焙新怪物。

| 松鼠觀察 | 松鼠奔跑 |
| --- | --- |
| ![松鼠觀察](assets/images/characters/squirrel-alert.png) | ![松鼠奔跑](assets/images/characters/squirrel-running.png) |

| 安靜觀察 | 張嘴伸手準備抓人 | 逐漸淨化 | 小天使 |
| --- | --- | --- | --- |
| ![觀察納別奇](assets/images/characters/nabieqi-stalking.png) | ![張嘴雙手準備抓人的納別奇](assets/images/characters/nabieqi-reaching-v2.png) | ![淨化納別奇](assets/images/characters/nabieqi-cleansing.png) | ![小天使](assets/images/characters/angel.png) |

追逐圖依最新意見更新為張嘴、雙手向前準備抓人；舊 nabieqi-reaching.png 保留但不再使用。答題設計已加入上下左右移動的字母與飄動怪物，孩子須點對字母、避開納別奇，第一關慢、後兩關逐漸加快；學習／重播／成功暫停移動。這是已確認的工程規格，圖片試閱本身尚無動畫遊戲。

## 道具

燈牌與紙上保持空白，清楚的英文字母與注音台詞由後續工程另外加入。月亮刻紋不發光。

| 燈未亮 | 燈亮 | 蠟燭未亮 | 蠟燭亮 |
| --- | --- | --- | --- |
| ![燈未亮](assets/images/props/lantern-unlit.png) | ![燈亮](assets/images/props/lantern-lit.png) | ![燭未亮](assets/images/props/candle-unlit.png) | ![燭亮](assets/images/props/candle-lit.png) |

| 月亮石 | 空白紙 | 月亮刻紋 | 門葉 |
| --- | --- | --- | --- |
| ![月亮石](assets/images/props/moonstone.png) | ![空白紙](assets/images/props/watch-note.png) | ![月亮刻紋](assets/images/props/moon-mark.png) | ![門葉](assets/images/props/watch-door.png) |

音樂、26 個字母名稱錄音、注音文字圖和可玩故事在下一階段製作。本輪未發布。
