# Story 02｜逃出虎姑婆的山屋

完整故事第一輪工程與瀏覽器驗收完成，待視覺／平板實機與 PR 審查；尚未合併或發布。

- 規格分支：`docs/story-02-plan`，保留 [Draft PR #3](https://github.com/mansonsick/Moon-cave/pull/3)。
- 工程分支：`feature/story-02-foundation`，由規格 head 接續。
- 基準 main：`436861ce6e00fa68646ab800bd35894312f9cb5b`。
- 存檔：`adventure.story-02.state`；音效設定：`adventure.settings.sound`。

| 文件 | 用途 |
| --- | --- |
| [STORY_SPEC.md](STORY_SPEC.md) | 確認版 v1.0 加本次資產／工程交接補充。 |
| [ASSET_MANIFEST.md](ASSET_MANIFEST.md) | 實際圖片、點位、注音與音訊缺件。 |
| [AUDIO_PLAN.md](AUDIO_PLAN.md) | 音效規格與製作方向。 |
| [ENGINEERING_PLAN.md](ENGINEERING_PLAN.md) | 已實作模組、存檔及生命週期。 |
| [QA.md](QA.md) | 測試結果與真機／視覺限制。 |
| [DEVLOG.md](DEVLOG.md) | 工程紀錄。 |
| [協作 SOP](../../CHATGPT_DESKTOP_COLLABORATION_SOP.md) | 內容／視覺與工程／GitHub 分工。 |

## 執行檔案

入口 `index.html`／`app.js`；設定 `story.json`；存檔校驗 `state.js`；專用樣式 `story.css`。
共用模組位於 [engine](../../engine/)，只由本故事及獨立實驗頁引用。
正式首頁未加入 Story 02 卡片，《月光洞》維持 v3；不能把開發路徑當成已上線網址。

## 本機試玩

在 repository root 執行 `python -m http.server 8000 --bind 127.0.0.1`，開啟 `http://127.0.0.1:8000/stories/story-02/`。
不要直接雙擊 HTML；ES modules／fetch 需要 HTTP。跨裝置感測需安全來源，真機另安排 HTTPS 預覽，不修改正式 Pages。

普通路線：開始 → 山路 → 山屋 → 招待 → 三線索 → 鑰匙 → 躲藏 → 竹林 → 木橋 → 古廟等天亮。

祕密路線：竹林後點地上小腳印 → 找鈴 → 木橋 → 自行把背包的鈴拖到古廟空鉤。
所有獎勵等「繼續」。重整先顯示「開始冒險」，點後恢復進度；未完成的挑戰重新開始。

## 下一步

補 9 個有來源／授權的正式音檔，確認兩張衍生圖、鑰匙與竹林視覺，完成 iPad／Android 真機驗收。
先審 PR；使用者另行確認後才處理合併、首頁故事卡及 Pages 發布。
