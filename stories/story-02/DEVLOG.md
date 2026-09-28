# Story 02《逃出虎姑婆的山屋》開發紀錄

故事 ID：`story-02`。規格版本 v1.0 已確認；可執行故事尚未開發、未發布。

## 2026-09-28｜規格文件與目錄準備

### Changed

- 從 `main` commit `436861ce6e00fa68646ab800bd35894312f9cb5b` 建立 `docs/story-02-plan`。
- 原文收錄使用者已確認的 `STORY02_STORY_SPEC_v1.md` 為 [STORY_SPEC.md](STORY_SPEC.md)，不沿用 Draft v0.1 的待確認清單。
- 建立文件入口、資產清單、音效計畫、工程交接計畫與素材目錄；沒有可執行故事或佔位網頁。
- 納入協作 SOP，補充《月光洞》現有存檔例外；同步 HANDOFF／SOP 的故事可設定背包、Story 02 8 秒倒數與隱藏鈴鉤規則。
- 音效依確認版為首次預設開啟、點「開始冒險」後才啟用；保留使用者已有的關閉設定。

### Test performed

- 核對 `STORY_SPEC.md` 與使用者確認稿原文一致。
- 檢查文件相對連結、場景／音效清單與目錄。
- 檢查變更僅限 Markdown 與目錄占位；首頁、《月光洞》及所有既有執行程式／資產均未修改。
- 文件格式差異檢查；保留確認稿的 Markdown 換行語法。

### Known limitations / Next

- 所有 Story 02 圖片與音效均待交接；清單中的檔名為預定位置，並非已存在的成品。
- 沒有 `story.json`、故事入口、engine、感測／音效測試頁；未執行尚不存在功能的瀏覽器或平板測試。
- 本規格分支不合併 `main`、不發布；等圖片與資產交接後再進 `feature/story-02-foundation`。
