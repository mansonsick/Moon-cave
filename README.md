# 阿通的冒險世界

低年級兒童的平板互動冒險繪本入口。目前收錄《月光洞的祕密》v3。

| 路徑 | 內容 |
| --- | --- |
| `/Moon-cave/` | 冒險首頁：大型故事卡與「開始冒險」。 |
| `/Moon-cave/stories/moon-cave/` | 《月光洞的祕密》v3；頁底可返回冒險首頁。 |

此架構在 PR 確認、合併 `main` 並完成 Pages 部署後生效。合併前正式 root 仍是《月光洞》v3。

故事仍為單一 HTML，原圖片、注音與程式內嵌；尚未重構共用 engine。首頁沒有建置程序或外部服務依賴。

首頁與以後所有故事統一使用 `BpmfGenRyuMin-H.ttf` 的右側注音。公開網站使用本機預先渲染的透明文字圖，字型本體不公開；改字方式見 [scripts/README.md](scripts/README.md)。

## 開發與測試

- [PROJECT_HANDOFF.md](PROJECT_HANDOFF.md)：工程分工、目前範圍與存檔遷移提案。
- [INTERACTIVE_STORY_SOP.md](INTERACTIVE_STORY_SOP.md)：故事製作及發布標準。
- [MOON_CAVE_DEVLOG.md](MOON_CAVE_DEVLOG.md)：版本與變更紀錄。
- [tests/README.md](tests/README.md)：瀏覽器回歸測試。
- [ADVENTURE_HUB_QA.md](ADVENTURE_HUB_QA.md)：本次驗證結果與待實機／上線項目。

GitHub `main` 最新內容是正式來源。修改在分支完成並建立 PR，使用者確認前不合併或發布。

## v3 保存基準

原 root `index.html` 保存在 commit `50841bd009b1a14e00f673b23fa5e5b7828dfb66`，blob 為 `2071c1f9b662637e7db6708217d8d3c20c8cec5d`。回歸測試直接讀取此基準，比對移動版只有獨立返回導覽的差異。

存檔仍使用 `moonCaveState` 與 `moonCaveTextScale`，不因更換路徑而清除或更名；未來故事使用各自 namespace。
