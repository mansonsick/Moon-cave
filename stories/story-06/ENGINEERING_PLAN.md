# 第六本工程交接

使用者於 2026-10-05 確認完整分層美術並要求繼續。工程在 `feature/story-06-foundation`，接續規格／美術分支 `docs/story-06-concept`（Draft PR #17，保留來源）；正式基準 main 為 `cdd23029978f3030aeec5bf830de1598ca9b1cb3`。發布另待使用者確認。

## 檔案與共用範圍

- `index.html`、`app.js`、`styles.css`：直向完整圖層、故事、先學再聽音闖關、背包／拖鈴、普通／祕密結局與返回。
- `story.json`：由正式 STORY_SPEC 的十四幕文字與 UI 標籤產生；不從歷史草稿出題。
- `state.js`：37 池抽 18 個不同符號，保存實際三組、種子與版本；保存學習、獨立／輔助結果、當題看字記錄、道具、場景、返回紀錄與結局。損坏記錄修復，不憑任意 progress 跳關。
- `symbol-audio.js`：沿用共用 AudioManager，只為本書加符號完成／取消、音訊版本、重試與背景壓低。播放完成才顯示答案，沒有倒數。
- `text.js`、`assets/text`、`assets/symbols`：中文右側注音與 37 符號均為指定私有字型離線 PNG；不發佈字型。`還`使用本書語境讀音，`ㄧ`為橫畫，單符號以實際筆墨範圍置中。
- `audio-review.html/js`、`assets/audio/manifest.json`／`CREDITS.md`：教育部 37 原始 WAV、官方映射／來源／授權／雜湊、家長逐符號试聽；四條原創環境音、四個操作提示。
- `scripts/build_story06_content.py`、`render_story06_text.py`、`build_story06_audio.py`：可重建文字／符號／音訊的離線來源。教育部來源 ZIP、HTML 與字型留 repo 外。

共用僅引用既有 `storage.js`、`audio-manager.js`、`moving-targets.js`、`interactions.js`，未改其行為。前五本維持，首頁只增國文第六本卡、平台測試補六本與新試聽入口。

## 狀態與流程

key：`adventure.story-06.state`。共用聲音：`adventure.settings.sound`。新冒險二次確認，只清本書進度。刷新、重試、回看、選單保留題組與已完成結果。以六張學習卡為本關唯一干擾選項池。

第一關三個固定葉片；第二關四個慢泡；第三關五個慢羽卡。沿用按下即暫停、放開確定的觸控判定；家長可固定卡片。隱藏窄路、水窪鈴、樹洞保持無發光答案標示。取鈴後不自動切結局；拖入原圖樹洞後，鈴留在洞口發光。鍵盤或點選道具再點樹洞亦可。

中文故事仍在每幕圖片旁讀取，答案本身置於場景內。保留回首頁、故事選單、上一幕、A−／A+、雙指縮放和全螢幕。家庭入口與網站說明沿用；這仍是公開靜態網站，沒有新增伺服器認證。

## 驗收與後續

自動化及已知限制見 `QA_RESULTS.md`。實際平板的聲音清晰度、拖曳、全螢幕、雙指縮放與慢移手感由家長確認；沒有把桌機模擬當實機。此版沒有鏡頭、體感、聲調或拼音組合，不自動發布或開始下一本。
