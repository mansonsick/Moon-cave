# 阿通的冒險世界

低年級兒童的平板互動冒險繪本入口。目前收錄《月光洞的祕密》v3。

| 路徑 | 內容 |
| --- | --- |
| `/Moon-cave/` | 冒險首頁：大型故事卡與「開始冒險」。 |
| `/Moon-cave/stories/moon-cave/` | 《月光洞的祕密》v3；頁底可返回冒險首頁。 |

已於 2026-09-28 經使用者確認上線：[冒險首頁](https://mansonsick.github.io/Moon-cave/)｜[月光洞的祕密](https://mansonsick.github.io/Moon-cave/stories/moon-cave/)。[PR #1](https://github.com/mansonsick/Moon-cave/pull/1) 已合併，[Pages 部署成功](https://github.com/mansonsick/Moon-cave/actions/runs/36401343293)。

正式《月光洞》仍為單一 HTML，原圖片、注音與程式內嵌；本工程分支的共用 engine 僅用於 Story 02。首頁沒有建置程序或外部服務依賴。

首頁與以後所有故事統一使用 `BpmfGenRyuMin-H.ttf` 的右側注音。公開網站使用本機預先渲染的透明文字圖，字型本體不公開；改字方式見 [scripts/README.md](scripts/README.md)。

## 開發與測試

- [PROJECT_HANDOFF.md](PROJECT_HANDOFF.md)：工程分工、目前範圍與存檔遷移提案。
- [INTERACTIVE_STORY_SOP.md](INTERACTIVE_STORY_SOP.md)：故事製作及發布標準。
- [CHATGPT_DESKTOP_COLLABORATION_SOP.md](CHATGPT_DESKTOP_COLLABORATION_SOP.md)：內容／視覺與工程／GitHub 分工。
- [MOON_CAVE_DEVLOG.md](MOON_CAVE_DEVLOG.md)：版本與變更紀錄。
- [tests/README.md](tests/README.md)：瀏覽器回歸測試。
- [ADVENTURE_HUB_QA.md](ADVENTURE_HUB_QA.md)：本機、正式網站驗證結果與待實機項目。

GitHub `main` 最新內容是正式來源。修改在分支完成並建立 PR，使用者確認前不合併或發布。

## Story 02 平板測試版

《逃出虎姑婆的山屋》第一輪完整工程已通過瀏覽器驗收。使用者已於 2026-09-28 要求先上線供平板實測，經 PR #3／#4 合併至 main 發布：[平板測試入口](https://mansonsick.github.io/Moon-cave/stories/story-02/)。首頁卡片及月光洞保持原樣，正式音檔與感測實機驗收仍待完成。詳細方式見 [stories/story-02/README.md](stories/story-02/README.md)。

## v3 保存基準

原 root `index.html` 保存在 commit `50841bd009b1a14e00f673b23fa5e5b7828dfb66`，blob 為 `2071c1f9b662637e7db6708217d8d3c20c8cec5d`。回歸測試直接讀取此基準，比對移動版只有獨立返回導覽的差異。

存檔仍使用 `moonCaveState` 與 `moonCaveTextScale`，不因更換路徑而清除或更名；未來故事使用各自 namespace。
