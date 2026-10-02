# Story 05 美術交付與分層

日期：2026-10-02；對應 [STORY_SPEC.md](STORY_SPEC.md)。本輪以內建 imagegen 製作 29 張 PNG：3 基準圖（含保留的兩次初稿）、8 背景、10 角色姿勢／狀態、8 道具。原圖保留，完整指令收錄 [PROMPTS.json](assets/images/PROMPTS.json)。交付尺寸／透明性以 [ASSET_MANIFEST.json](assets/ASSET_MANIFEST.json) 核對，實際檢查結果見 [QA_RESULTS.md](QA_RESULTS.md)。

## 基準圖

`assets/images/anchor-v3.png` 是正式角色／世界觀 reference；`anchor.png` 與 `anchor-v2.png` 保留作被取代的初稿，都不是正式場景。阿通、小松鼠沿用第三本身份；納別奇改為與小天使差不多高、暗紅破布披風、黑色破舊翅膀，懸飛在空中，與淨化天使同一靈體；紅色是布料，沒有血跡。冷藍霧夜、溫暖微光、細膩水彩／不透明水彩和細墨線。基準圖同時展示怪物與天使，不直接作封面或正式場景，以免提前揭露結局和寶石。

## 背景與場景

| 檔案（assets/images/backgrounds/） | 對應場景 | 必需元素與後續獨立層 |
| --- | --- | --- |
| night-path.png | S01／S02 | 回村林路、遠處石亭；阿通行走／奔跑與樹後怪物手分層 |
| stone-shelter.png | S03／L1 學習 | 保護性的石亭、紙張桌面、看得見的出口；小紙和字母後疊 |
| forest-lamps.png | S04 | 林路與守夜屋出口；答案燈座在中右，主角在左，九盞進度燈另疊 |
| watch-house.png | S05／S06／L2 學習 | 寬空桌面、門縫、右後出口；四個答案燭台、門葉與怪物分層 |
| moon-wall.png | S07／H01 | 守夜屋後牆、低處空石塊、通往橋的路；月刻紋後疊且不發光 |
| bridge-gate.png | S08／S09／S10／H02／H03 | 完整橋面與村口；五處答案燈座、八盞進度燈、五輪怪物位置各留安全區 |
| rock-hideout.png | R01 | 安全石縫、森林出口；完整無傷的兩主角，怪物在外部不抓咬 |
| dawn-village.png | E01／E02 | 完整成功的晨光村路；普通有兩主角，祕密加天使與月亮石 |

背景先畫清楚全貌，霧／黑暗／燈光遮罩由未來程式分層，不烘焙成無法恢復的黑圖。不把 26 盞進度燈、字母或提示畫在底圖；答案／進度各有明確層。背景與互動保持完整比例，不裁切出口來遷就版面。

## 角色透明 PNG

| 檔案（assets/images/characters/） | 用途 |
| --- | --- |
| atong-alert.png | 初遇、閱讀、觀察、藏身；沒有提早持寶石 |
| atong-running.png | 森林／空屋／橋間追逐，回頭觀察 |
| atong-listening.png | 手靠耳朵聽字母、手準備點燈 |
| atong-moonlight.png | 取得寶石後、五輪月光與祕密收尾 |
| squirrel-alert.png | 注意怪物、陪讀、看小紙 |
| squirrel-running.png | 陪伴逃跑，視線向後確認 |
| nabieqi-stalking.png | 遠處／門縫／追逐初段，黑破翅懸飛的同一小怪物 |
| nabieqi-reaching.png | 空中伸手追逐和月光第一、二輪，黑翅動作明確不同 |
| nabieqi-cleansing.png | 月光第三、四輪，仍懸飛，紅披布與黑破翅變淡，困惑／怕光 |
| angel.png | 第五輪後才出現的小天使，保持輪廓特徵連結 |

同場景可共用底圖，但事件不同必須改人物動作、怪物位置、燈／出口／霧狀態，不能只有標題換字。角色完整頭髮、腳、翅膀、尾巴與手指都在圖內，人物不是底圖烘焙的一部分。

## 道具透明 PNG

| 檔案（assets/images/props/） | 用途與約束 |
| --- | --- |
| lantern-unlit.png／lantern-lit.png | 答案／進度燈，前方空白牌可疊字母；同一造型、只換燈火與照明 |
| candle-unlit.png／candle-lit.png | 第二關燭台，同一造型、空白小寫字母牌；不在圖內拼寫字母 |
| moonstone.png | 圓潤銀藍、內部月牙光，正式名月亮石；可拖曳，光圈由獨立層產生 |
| watch-note.png | 空白淺色紙，注音／學習文字在後續階段另疊 |
| moon-mark.png | 灰褐石塊的淺月刻紋，融入後牆，無亮邊／箭頭 |
| watch-door.png | 關閉門葉，覆在空屋右後門口；燈完成後移除以顯示同位置出口 |

所有字母與中文字由後續工程加入，圖上不能有猜錯／模糊的 AI 英文。中文使用指定字型本機渲染右側注音，不 commit 字型。音效／音樂／26 字母名稱錄音另待製作，本輪圖片不當成音訊交付。

## 交付前檢查

逐張人工檢查身份、姿勢、場景必要元素、無血腥、沒有提前揭露、透明邊界與留白；核對所有節點皆可由背景＋角色＋道具組合。影像尺寸、alpha、檔案與指令清單自動核對，實際觸控／fog／拖曳／全螢幕待工程後測試，不能用這次圖片檢查宣稱遊戲可玩。
