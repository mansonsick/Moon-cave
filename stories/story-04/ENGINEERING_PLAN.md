# Story 04 工程與驗收

日期：2026-10-01；分支 `feature/story-04-foundation`，main 基準 `617d09c634d933d260070e740b8f87460945cade`。原規格 PR 13 保留，本次不合併或發布。

## 檔案與資料

- `story.json`：十五場景、320 文字標籤、6／6／5 張教學卡、二十題及兩題代表題設定，由核准 Markdown 產生。
- `app.js`：場景、學習→練習→實際送信、陪讀確認、選單和雙結局。
- `state.js`：驗證與修復保存資料，`text.js` 顯示注音 PNG；HTML／CSS 支援觸控、字級及瀏覽器縮放。
- `print.html/js/css`：同碼列印三張孩子練習紙；家長解答為獨立一張，不把解答藏在孩子紙的 CSS 裡。
- `assets/images`：角色／底圖；`assets/practice` 原創 SVG 教學圖；`assets/text` 注音 PNG。
- 新增 `engine/reading-worksheet.js`，只由 Story 04 使用。其餘共用模組與三本故事程式保留原樣。

## 題卷碼

格式 `c1-<7 位 base36 種子>-<2 位檢查值>`，忽略大小寫和空白後驗證。使用平台 crypto 產生種子、固定雜湊和 Fisher–Yates 洗牌；紙本、解答、平板讀相同 JSON。`c1` 綁定 `forest-v1`，公開後不改題池內容或答案，擴充用新版本。

本輪固定二十題（6／7／7），新碼更換選項順序。代表題固定 Q02／Q05、Q08／Q13、Q15／Q18；不承諾新碼會生出新的題目或支援家長自訂難度。換碼有進度時須明確確認，錯碼保留原存檔。

## 學習與狀態

三站先看完本組圖卡才能練習，之後可重看；第一站物象、簡化形狀、現代字並排，形狀不是古字／筆順。原創題圖和文字與場景分層；三封信各自更新一次、留下信封，第三封成功台詞在實際送出後才顯示。

`adventure.story-04.state` 保存 schema 1、forest-v1、scene、code、scale、learned／learning、full、answers、checked、assisted、delivered、leaf、placed、badge、ending。回答正確與明確陪讀完成分別記錄；未核對的紙本題不寫成正確。重新開始只寫第四本；損壞資料修復或開新檔，localStorage 被拒絕時仍可在本頁遊玩。

葉片取得前不顯背包空槽；路邊入口、信箱葉形 dropzone 不發光、不顯使用教學。觸控拖放命中才保留發光，放錯退回。保留點選葉片後點信箱的輔助操作；找到而不用仍可普通結局。

## 字音、資產、聲音

`scripts/build_story04_content.py` 和 `build_story04_graphics.py` 產生資料及原創 SVG，`render_reading_text.py --font <本機字型路徑>` 用 Pillow／fontTools 產 PNG。指定字型的替代字形處理背、還、郵差、種子；臨時字型結束後刪除，不提交字型。manifest 保留文字、切片尺寸及語境讀音。

35 張 imagegen 圖：原 23 張角色／場景，加八張情境卡和四張透明道具。原始生成檔在本機保留；沒有覆蓋底圖。PROMPTS.json 與 VISUAL_FIX_PROMPTS.json 保留指令；ASSET_MANIFEST.json 記尺寸與透明性，可由 build_story04_manifest.py 重建。圖片位置按同一未裁切的 16:9 畫面定位。

第二、三站以單張完整圖卡呈現情境；第一站保留物象／形狀／字並排。網頁長句練習使用相符的情境圖，紙本維持三張 A4 的原有圖示／閱讀段落配置。題目及解答不改，題池版本與既有保存進度不需遷移。

場景小紙由 sceneText 定義視覺斷行，原文必須與 label 相同；指定字型、統一畫布和字級產出四張深色注音 PNG，text.scene 以完整圖置中容納。透明道具 crop 是量測 alpha 範圍的定位資料，不裁切或重畫原始 PNG。徽章分姿勢定位，信封按背景桌面／信盤的實際表面落點，小鳥不與已送出的信重疊。

使用既有 AudioManager 和 Story 02 已公開原創 WAV：found-item、success、fail-soft、drag-lock，音量 0.3。首次開始冒險才解鎖，共用 `adventure.settings.sound`；聲音關閉／載入失敗不影響故事。尚無新環境音或朗讀，沒有下載未授權音效，也不改既有音效檔。

## 測試與限制

`python tests/story_04_test.py`：三站先學／回看、錯題提示及回到對應學習卡、全部二十題或六題代表題、送錯再試、普通／祕密及有葉不用、拖放／保留發光／重新整理、換碼確認、損壞／拒絕 storage、舊存檔隔離、獨立孩子／家長列印、390／820／1180 和 A+。另測音效靜音及音檔載入失敗仍能完成學習並繼續。

列印用 Chromium A4 實際輸出後檢查：孩子三頁共二十題，第三頁的 Q18–Q20 完整共用段落同頁；家長一頁；右側注音無裁切。首頁分類、四本入口、已有月光洞回歸另驗證。家庭 Safari／Android 平板的真實觸控、雙指縮放、印表機與孩子難度仍需使用者試用。沒有鏡頭或朗讀的新需求，不回改第三本。
