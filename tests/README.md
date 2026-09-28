# 冒險首頁與《月光洞》搬移回歸測試

使用 Python、Playwright 及 Chromium。網站本身不需要建置或安裝套件。

```sh
python -m pip install playwright==1.59.0
python -m playwright install chromium
python tests/adventure_hub_test.py --output ../hub-review
```

可使用 `--browser-executable /path/to/chrome` 指定已安裝的 Chromium。

測試會啟動暫時的 localhost 伺服器，使用 `/Moon-cave/` 路徑前綴模擬 GitHub Pages project site。每個測試使用獨立瀏覽器環境，不會接觸使用者的正式存檔。輸出截圖與 `test-results.json` 到指定目錄，不需 commit。

原 v3 從 Git commit `50841bd009b1a14e00f673b23fa5e5b7828dfb66` 讀取；clone 需保留此 commit。測試先確認移動版只新增獨立返回導覽，再對原版及移動版執行相同操作：

- 平板直向、橫向及手機排版；封面與按鈕進入故事、返回首頁。
- 首頁注音文字圖載入及可存取名稱，確認瀏覽器不要求下載原字型。
- 原根目錄存檔改從子目錄讀取；首頁不讀寫或遷移存檔。
- A−／A+、重新整理與再玩一次。
- 盾牌首次點擊計時、錯誤回饋、超時及重試。
- 月亮石逐顆點亮 10 顆星、古老鑰匙手動啟動 15 秒倒數。
- 成功卡片等待「繼續」、不發光的隱藏入口。
- 真實瀏覽器觸控事件拖曳、錯位彈回、正確凹槽發光及圖示保留。
- 普通／祕密結局及最終存檔一致性。

倒數以瀏覽器測試時鐘加速；不修改產品程式。實體平板、雙指手勢與實際 GitHub Pages 上線驗收仍須另做，不以模擬結果代替。

原 v3 的 Chromium 模擬在「觸控拖曳 → 結局 → 重新整理」後，第一次點完成有時只有 touch／pointer 事件，第二次才觸發 click。測試只對這個情境記錄最多兩次點擊，並要求原版與搬移版次數一致；詳見 [ADVENTURE_HUB_QA.md](../ADVENTURE_HUB_QA.md)。可用 `--only baseline`、`--only relocated` 或 `--only hub` 針對該組檢查重跑。
# Story 02 工程測試（追加）

```sh
python tests/story_02_test.py --output ../hub-review/story02-tests
python tests/sensor_audio_test.py --output ../hub-review/story02-tests
python tests/story_02_audio_test.py --output ../hub-review/story02-tests
```

自建 `/Moon-cave/` 前綴本機伺服器、隔離 Chromium context 與虛擬時鐘；不改正式網站或使用者存檔。
25 組測試含完整普通路線、隱藏／祕密路線、真實滑鼠／觸控拖曳、存檔隔離、感測事件／失敗替代及 Web Audio。
`sensor_audio_test.py` 使用記憶體 WAV 驗證音訊切換與失敗處理；`story_02_audio_test.py` 使用實際交付的 9 個 WAV，驗證雜湊、解碼、非零聲音輸出、關鍵場景觸發、神鈴跨場景延續與靜音記憶。結果與截圖輸出 repository 外。
具體已測與未測範圍見 [Story 02 QA](../stories/story-02/QA.md)；這些測試不取代 iPad／Android 真機驗收。
