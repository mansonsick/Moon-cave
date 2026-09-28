# Story 02 資產實際交接清單

2026-09-28 收到 `story02_tiger_grandma_assets.zip`，先讀取並保留 [包內 manifest](ASSET_PACKAGE_MANIFEST.txt)。
12 張正式圖以原始 PNG 位元組保存，均為 1672 × 941，完整呈現，不裁切成直圖。
原檔名、SHA-256、尺寸見 [sources.json](assets/images/sources.json)。

`虎姑婆山屋逃脫遊戲設定圖.png` 是 **REFERENCE ONLY**：只在本機解壓參考，不加入遊戲資產或任何場景。

## 圖片對應

| 工程檔名（assets/images/） | 包內原檔／來源 | 使用場景 |
| --- | --- | --- |
| cover.png | 夕陽山谷的冒險啟程.png | 中性名稱封面。 |
| mountain-path.png | 月升山徑上的男孩與松鼠.png | 山路迷途。 |
| warm-house.png | 月光下的溫暖山林小屋.png | 溫暖山屋。 |
| welcome.png | 月夜山屋的温暖晚餐.png | 老婆婆招待。 |
| clues.png | 月光山屋的神秘腳印.png | 腳印、床上虎毛、廚房尾巴。 |
| key-search.png | 月夜山屋_男孩與松鼠的探險.png | 夜間找鑰匙。 |
| hide.png | 月光下的木屋捉迷藏.png | 躲藏不動。 |
| bamboo.png | 月下竹林驚魂追逐.png | 竹林故事圖，小遊戲另畫於 UI。 |
| bridge.png | 月夜吊橋上的勇敢旅程.png | 木橋平衡。 |
| shrine.png | 月夜山林中的神社奇遇.png | 隱藏場景找鈴。 |
| ordinary.png | 晨光下的山村歸途.png | 普通成功結局。 |
| secret.png | 神光守護下的虎靈退散.png | 神威祕密結局與收尾。 |
| fork.png | imagegen 衍生自 mountain-path.png | 自然岔路、木橋、小動物腳印。 |
| temple-empty-hook.png | imagegen 衍生自 shrine.png | 移除大鈴與垂飾、保留空鉤。 |

使用者授權「沿用原圖風格補製最少量衍生圖，原圖保留」；兩張衍生圖待視覺確認。
完整 prompts 與來源見 [DERIVED_ASSETS.md](DERIVED_ASSETS.md)。
原圖由使用者交付，本包沒有獨立授權文件，不另宣稱素材為公有領域或授予第三方再散布權。

## 互動點位

原圖百分比 `[x,y,width,height]`，執行設定以 [story.json](story.json) 為準。
舞台與原圖比例一致，沒有 object-fit 裁切。

| 物件 | 點位 | 規則 |
| --- | --- | --- |
| 地上腳印 | [45,62,20,16] | 透明，找到才標記；不重算。 |
| 床上虎毛 | [84,39,15,11] | 同上。 |
| 廚房尾巴 | [26,30,8,15] | 同上。 |
| 後門鑰匙 | [22,55,9,9] | 原圖未見清楚鑰匙；原創 SVG 疊於抽屜邊。依實測回饋縮為 48% 並降低色彩對比，透明觸控範圍不變。 |
| 岔路腳印 | [45,77,11,20] | 圖內自然印記，透明點位，不發光／可見按鈕。 |
| 石龕大鈴 | [64,24,9,23] | 原圖的鈴，取得前背包無空格。 |
| 古廟空鉤 | [64.7,16,8,14] | 不描邊／發光／提示使用；放入才保留發光圖示。 |

鑰匙 15／30 秒兩層提示，第二層含「拿起鑰匙」，必要物不會卡死。

## 注音與竹林 UI

[assets/text/text.json](assets/text/text.json) 保存 97 個中文文案及 PNG 尺寸。正常流程的可見中文皆用指定 `BpmfGenRyuMin-H.ttf` 本機產圖。
來源為 `story.json.labels`，短片段可換行，保留整句可存取名稱與 A−／A+、雙指縮放。
使用者提供版與已安裝版 SHA-256 相同：`94eb915a604403e5502583ed407b16f611c197474249ae48050f653cd2d4988c`。
沒有複製字型進 repository。

竹林使用規格允許的獨立 mini-game：原創簡化阿通 SVG、松鼠／竹子／石頭／倒木系統 emoji 與程式化道路。
沒有裁切設定總覽圖當 sprite，沒有網路取圖。
若要與插圖同等精細的跑步角色，可再補透明角色圖；不影響完整玩法。

注音多音字、輕聲與實際平板小字級仍需內容端逐句確認。

## 音訊已補齊（原創合成 v1，9／9）

| ID | 正式路徑 |
| --- | --- |
| forest-evening | assets/audio/ambience/forest-evening.wav |
| creepy-house | assets/audio/ambience/creepy-house.wav |
| bamboo-chase | assets/audio/ambience/bamboo-chase.wav |
| temple-night | assets/audio/ambience/temple-night.wav |
| found-item | assets/audio/sfx/found-item.wav |
| success | assets/audio/sfx/success.wav |
| fail-soft | assets/audio/sfx/fail-soft.wav |
| drag-lock | assets/audio/sfx/drag-lock.wav |
| secret-bell | assets/audio/sfx/secret-bell.wav |

全部已由專案程式原創合成，設定 `available: true`；22,050 Hz mono PCM16 WAV，合計 3.80 MB。來源、時長、hash 與聽感見 [AUDIO_ASSETS.md](AUDIO_ASSETS.md) 及 [音訊 manifest](assets/audio/manifest.json)。
沒有第三方錄音／取樣或未授權網路音效；實體平板喇叭的音量與音色待使用者回饋。

## 尚待視覺確認

- 兩張衍生圖、抽屜鑰匙、小遊戲角色與系統 emoji。
- 石龕與古廟使用同一構圖的有鈴／空鉤版本；若需明確區分兩地點，可再補古廟圖。
- 山路原圖未清楚畫出木屋、古廟圖未畫追來的虎影；以場景文字銜接，不宣稱所有 v1 美術要素已齊全。
- 9 個音訊已用原創合成版本補齊；沒有阻塞主線或任一結局的素材缺件，可再依聽感替換精緻音檔。
