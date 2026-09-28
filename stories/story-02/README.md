# Story 02｜逃出虎姑婆的山屋

狀態：故事與互動規格 v1.0 已由使用者確認；本分支只整理文件與素材目錄，尚未開始故事工程或發布。

- 故事 ID：`story-02`
- 規格分支：`docs/story-02-plan`
- 下一工程分支：`feature/story-02-foundation`，等圖片與資產交接完成後才進入。
- 預定存檔：`adventure.story-02.state`
- 基準 `main`：`436861ce6e00fa68646ab800bd35894312f9cb5b`

## 文件入口

| 文件 | 用途／狀態 |
| --- | --- |
| [STORY_SPEC.md](STORY_SPEC.md) | 使用者確認版，原文收錄自 `STORY02_STORY_SPEC_v1.md`；本故事的內容與互動依據。 |
| [ASSET_MANIFEST.md](ASSET_MANIFEST.md) | 素材需求、預定檔名與交接欄位；所有素材目前待交接。 |
| [AUDIO_PLAN.md](AUDIO_PLAN.md) | 音效製作方向，依確認版補齊預設開啟與不阻塞故事的規則。 |
| [ENGINEERING_PLAN.md](ENGINEERING_PLAN.md) | 下一階段模組、檔案、順序與驗收規劃；不代表已實作。 |
| [DEVLOG.md](DEVLOG.md) | Story 02 文件及工程進度。 |
| [協作 SOP](../../CHATGPT_DESKTOP_COLLABORATION_SOP.md) | 線上 ChatGPT 與 Codex 的內容／工程交接分工。 |

## 目前目錄

```text
story-02/
├─ README.md
├─ STORY_SPEC.md
├─ ASSET_MANIFEST.md
├─ AUDIO_PLAN.md
├─ ENGINEERING_PLAN.md
├─ DEVLOG.md
└─ assets/
   ├─ images/
   ├─ text/
   └─ audio/
      ├─ ambience/
      └─ sfx/
```

素材目錄僅以 `.gitkeep` 保留；沒有圖片、音檔、字型或可執行故事。`index.html`、`story.json`、`story.css` 及共用 engine 留待後續工程階段建立。首頁尚未加入 Story 02 卡片，不能把預定故事路徑當作已上線網址。

## 下一次交接

請依 [ASSET_MANIFEST.md](ASSET_MANIFEST.md) 交付角色／世界觀基準、場景圖片、竹林挑戰圖層或 mini-game 方案、座標及 UI 安全區、文字與音訊素材資訊。Codex 核對交接完整性後，再進入 `feature/story-02-foundation`；本規格分支不合併 `main`，發布仍需使用者另行確認。
