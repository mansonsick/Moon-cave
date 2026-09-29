# 分層素材約定

使用者確認人物、場景分開；Story 03 開始實作，後續故事可沿用。繪圖使用 built-in `image_gen`，最終提示詞見 [PROMPTS.json](assets/images/PROMPTS.json)、[寶箱開啟](assets/images/PROMPT_CHEST_OPEN.md)、[石門](assets/images/PROMPT_STONE_DOOR.md)。

| 圖層 | 檔案／做法 | 用途 |
| --- | --- | --- |
| 底圖 | `forest-bg.png`、`tower-bg.png`、`roof-bg.png` | 不含阿通、小松鼠或可取寶箱。塔內保留開放門洞，屋頂保留空星形凹槽。 |
| 人物 | `atong.png`、`squirrel.png` | 獨立 PNG alpha；同一造型跨幕重用。 |
| 道具狀態 | `door-stone.png`、`door.png`、`chest.png`、`chest-open.png` | 第一門為石材；開門移除門片，開寶箱切換狀態圖。 |
| 互動物件 | 木片、種子使用程式內 SVG | 木片從探索點移至背包與凹槽；數量與狀態由程式控制。 |
| 效果 | 星燈光、星座線、木片光 | CSS / SVG，不烘焙在底圖。 |
| 文字與題目 | 注音文字 PNG、算式、答案欄 | 獨立 UI，依題卷碼改變；AI 畫面裝飾不作計數答案。 |

所有圖層使用相同 16:9 舞台，以百分比 `[x,y,width,height]` 定位。整個舞台在直橫向等比例縮放，不裁切底圖；裝飾層不攔截觸控。互動區沿同座標定位，凹槽不添加醒目邊框或說明。

透明圖片保留原 alpha。素材原圖由工具保存，本專案使用副本。背景已透過影像編輯移除人物／道具，不是用不透明方塊蓋住；角色也不是 CSS 從完整插畫裁出來。

日後新增姿勢：使用同一角色參考圖產生站立、指向、拿物等透明圖，保持光源、腳底基準、比例，再在該幕切換。需要遮擋時增前景層；不為每幕重畫整張人物＋背景。重要特殊構圖仍可用完整插畫，但不能與人物層重複出現。

2026-09-29 補上 `courtyard-bg.png`、`atong-balance.png`、`atong-jump.png`、`atong-catch.png`，原圖保留。使用 built-in image_gen，同一 `atong.png` 角色參考，透明 PNG 保留 alpha；提示詞見 [PROMPTS_ACTIONS.json](assets/images/PROMPTS_ACTIONS.json)。單腳站和跳躍使用庭院，但人物位置／姿勢不同；接星光球在塔頂使用接球姿勢。通道、小窗、第二／三門也調整阿通與小松鼠站位。

隱藏木片與凹槽所在的原背景和熱區沒有移動。題目與相機預覽不烘焙在畫面裡。
