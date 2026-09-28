# Story 02｜逃出虎姑婆的山屋

完整故事第一輪工程與瀏覽器驗收完成。2026-09-28 使用者要求先上線供平板實測，已授權將規格與工程 PR 合併至 main，由 GitHub Pages 發布測試版；真機與正式素材驗收仍待完成。

- 規格來源：`docs/story-02-plan`，[PR #3](https://github.com/mansonsick/Moon-cave/pull/3)。
- 工程分支：`feature/story-02-foundation`，由規格 head 接續。
- 基準 main：`436861ce6e00fa68646ab800bd35894312f9cb5b`。
- 存檔：`adventure.story-02.state`；音效設定：`adventure.settings.sound`。

| 文件 | 用途 |
| --- | --- |
| [STORY_SPEC.md](STORY_SPEC.md) | 確認版 v1.0 加本次資產／工程交接補充。 |
| [ASSET_MANIFEST.md](ASSET_MANIFEST.md) | 實際圖片、點位、注音與音訊資產。 |
| [AUDIO_PLAN.md](AUDIO_PLAN.md) | 音效規格與製作方向。 |
| [AUDIO_ASSETS.md](AUDIO_ASSETS.md) | 九種原創合成音效、來源與重建方法。 |
| [CAMERA_LANES.md](CAMERA_LANES.md) | 竹林鏡頭站位、直接測試入口及裝置限制。 |
| [ENGINEERING_PLAN.md](ENGINEERING_PLAN.md) | 已實作模組、存檔及生命週期。 |
| [QA.md](QA.md) | 測試結果與真機／視覺限制。 |
| [DEVLOG.md](DEVLOG.md) | 工程紀錄。 |
| [協作 SOP](../../CHATGPT_DESKTOP_COLLABORATION_SOP.md) | 內容／視覺與工程／GitHub 分工。 |

## 執行檔案

入口 `index.html`／`app.js`；設定 `story.json`；存檔校驗 `state.js`；專用樣式 `story.css`。
共用模組位於 [engine](../../engine/)，只由本故事及獨立實驗頁引用。
正式首頁未加入 Story 02 卡片，《月光洞》維持 v3。測試版使用直接網址。

## 平板測試入口

[Story 02 平板測試版](https://mansonsick.github.io/Moon-cave/stories/story-02/)。以平板 Safari／Chrome 直接開啟 HTTPS 頁面。

躲藏與木橋按「開始」後，若跳出動作／方向權限請允許，再穩穩拿好校正兩秒；竹林按「試試傾斜控制」。若感測不支援，仍可使用普通倒數／左右按鈕。
竹林可選「試試鏡頭站位」：固定平板，以左／中／右站位控制。可先用 [獨立測試頁](https://mansonsick.github.io/Moon-cave/experiments/camera-lanes/)，不讀寫故事存檔。首次需載入約 18 MB；按鈕玩法不下載模型。
回報時提供平板型號、瀏覽器、場景與看到的情況。已加入九種柔和合成音效；按「開始冒險」後才播放。若上方是 🔇，點一下改成 🔊；更新會保留原本的靜音偏好。

## 本機試玩

在 repository root 執行 `python -m http.server 8000 --bind 127.0.0.1`，開啟 `http://127.0.0.1:8000/stories/story-02/`。
不要直接雙擊 HTML；ES modules／fetch 需要 HTTP。跨裝置感測需安全來源，真機另安排 HTTPS 預覽，不修改正式 Pages。

普通路線：開始 → 山路 → 山屋 → 招待 → 三線索 → 鑰匙 → 躲藏 → 竹林 → 木橋 → 古廟等天亮。

祕密路線：竹林後點地上小腳印 → 找鈴 → 木橋 → 自行把背包的鈴拖到古廟空鉤。
所有獎勵等「繼續」。重整先顯示「開始冒險」，點後恢復進度；未完成的挑戰重新開始。

## 下一步

確認新增音效在平板喇叭的音量／音色、兩張衍生圖與竹林視覺，完成 iPad／Android 真機驗收。
本次先依使用者授權提供線上測試版；首頁故事卡與完整正式版驗收另行確認。
