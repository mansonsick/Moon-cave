# ChatGPT × Desktop/Codex 協作分工 SOP

版本：v1.0  
專案：阿通的冒險世界 / 互動兒童冒險繪本  
正式來源：GitHub `mansonsick/Moon-cave` 的 `main`

收錄狀態：2026-09-28 在 `docs/story-02-plan` 規格分支整理，尚未合併 `main`。Story 02 使用者確認稿見 [STORY_SPEC.md](stories/story-02/STORY_SPEC.md)；本次只做正式文件與素材目錄，等圖片與資產交接後才進 `feature/story-02-foundation`。

---

## 1. 核心分工

### ChatGPT 對話端：產品／故事／視覺主責
負責：
- 故事概念與教育主題
- 完整劇情、分支、普通／祕密結局
- 道具與挑戰設計
- 每幕文字與低年級閱讀負擔
- 每幕圖片必要元素與 UI 安全區
- 角色／世界觀設定
- 逐幕產圖與圖文一致性
- UI/UX 產品規則
- 產品 Roadmap 與平台級規劃
- 驗收標準與問題判斷：區分單頁問題、共用引擎問題、平台架構問題
- 必要時更新 SOP / STORY_SPEC / ASSET_MANIFEST 的內容規格

不主責：
- 正式程式碼長期維護
- Git branch / commit / PR
- GitHub Pages 正式部署
- 同一時間與 Desktop/Codex 修改相同程式檔

### Desktop / Codex：工程／GitHub／發布主責
負責：
- 每次開工前讀 GitHub 最新 HANDOFF / SOP / DEVLOG / STORY_SPEC
- HTML / CSS / JavaScript 實作
- reusable engine 與 challenge library
- hotspot / dropzone / Pointer Events
- localStorage namespace 與資料 migration
- sensor / DeviceMotion / DeviceOrientation 實作與 fallback
- 本機與瀏覽器測試
- branch / commit / PR
- GitHub Pages 部署
- DEVLOG / HANDOFF 的工程變更回寫
- 回報 Changed / Fixed / Test performed / Known limitations

不主責：
- 未經確認自行改寫故事
- 自行改變教育目的
- 自行新增會影響故事方向的角色／結局
- 因局部 bug 順手進行未確認的大型重構

---

## 2. Source of Truth

優先順序：

1. GitHub `main`
2. `PROJECT_HANDOFF.md`
3. `INTERACTIVE_STORY_SOP.md`
4. 對應故事 `STORY_SPEC.md`
5. 對應故事 DEVLOG
6. 對話內容

若衝突，以 GitHub 最新正式文件為準。

重要決策不得只留在聊天裡；確認後要回寫 GitHub 文件。

使用者新確認但尚未合併的規格，須註明所在分支與待審狀態；不能宣稱它已在 `main` 或已發布。Story 02 本次確認的可設定背包、8 秒倒數、預設音效開啟等差異，同步記入該分支的 HANDOFF／SOP，避免沿用舊草案；不改寫《月光洞》的既定玩法。

---

## 3. 新故事標準流程

### Phase A — 產品與故事
由 ChatGPT 對話端主責。

順序：
1. 故事主題
2. 教育／做人處事核心
3. 完整故事
4. 所有選項與分支
5. 道具與狀態
6. 普通／祕密結局
7. 挑戰與可能體感
8. 每幕文字
9. 每幕圖片必要元素
10. hotspot / hidden hotspot 規劃

在使用者確認「故事定稿」前，不進正式程式開發。

### Phase B — 視覺
由 ChatGPT 對話端主責。

順序：
1. 角色／世界觀 anchor image
2. 每幕構圖與 UI 安全區
3. 逐幕產圖
4. 圖文一致性檢查
5. 圖片命名與 asset manifest

重要原則：
- 產圖前先知道 hotspot / 文字會放哪裡
- 圖片不能做好後才硬塞 UI
- 圖片必須能單靠畫面支援低閱讀能力兒童理解故事

### Phase C — 工程交接
ChatGPT 交付 Desktop/Codex：
- `STORY_SPEC.md`
- `ASSET_MANIFEST.md`
- `story.json` / story config 草案
- 圖片資產
- 驗收條件
- 必須沿用的 SOP / HANDOFF

### Phase D — 工程施工
Desktop/Codex：
1. 建 feature branch
2. 套用共用 engine
3. 建 scene / state / challenge
4. 設定 hotspot / hidden hotspot / dropzone
5. 設定故事專屬 localStorage namespace
6. 實作 sensor 與 fallback（如有）
7. 自動／桌面測試
8. 建 PR
9. 不直接 merge `main`

### Phase E — 驗收
使用者以平板實測。

ChatGPT 協助判斷問題層級：
- 單一場景 → story-specific 修正
- 多故事都會遇到 → engine 修正
- 影響整體入口／資料／發布 → 平台層修正

Desktop/Codex 依結論修正。

### Phase F — 發布
使用者確認後：
- merge PR
- GitHub Pages 更新
- DEVLOG / HANDOFF 更新

---

## 4. 檔案所有權原則

同一時間避免兩邊修改同一檔案。

### ChatGPT 對話端主要產出
- 故事企劃
- `STORY_SPEC.md`
- `ASSET_MANIFEST.md`
- 圖片
- roadmap / SOP 的產品規格草案

### Desktop/Codex 主要修改
- `index.html`
- `engine/*.js`
- `engine/*.css`
- stories 下正式可執行程式
- Git branch / PR
- DEVLOG 的工程版本紀錄

若 ChatGPT 需要 review 程式，原則上先讀 GitHub，不直接和 Desktop 同時改正式程式檔。

---

## 5. 多故事平台目標

Root `index.html` 為「阿通的冒險世界」入口。

建議方向：

```text
/
├─ index.html
├─ engine/
│  ├─ story-engine.js
│  ├─ challenges.js
│  ├─ interactions.js
│  ├─ sensors.js
│  └─ styles.css
├─ stories/
│  ├─ moon-cave/
│  ├─ story-02/
│  └─ story-03/
├─ PROJECT_HANDOFF.md
├─ INTERACTIVE_STORY_SOP.md
└─ PRODUCT_ROADMAP.md
```

長期原則：**換故事，不重寫 engine。**

---

## 6. localStorage 標準

故事狀態必須分 namespace：

```text
adventure.moon-cave.state
adventure.story-02.state
adventure.story-03.state
```

上列為新架構命名標準；《月光洞》目前仍使用 `moonCaveState` 與 `moonCaveTextScale`。`adventure.moon-cave.state` 是未來遷移目標，未實作前不得直接更名。Story 02 從第一版使用 `adventure.story-02.state`，詳見 [HANDOFF 存檔說明](PROJECT_HANDOFF.md#12-存檔現況與未來-namespace-遷移提案)。

跨故事共用設定：

```text
adventure.settings.fontSize
adventure.settings.sound
adventure.settings.motionEnabled
```

不可讓新故事的背包、道具、scene state 汙染舊故事。

---

## 7. 新功能判斷原則

每次需求先問：

> 這只是這一幕的需求，還是 5～10 本故事後也會需要？

### 僅本故事
做 story-specific config。

### 多故事可重用
優先加入共用 engine / challenge library。

### 影響整體平台
先提出架構方案，不直接局部 patch。

避免「頭痛醫頭、腳痛醫腳」。

---

## 8. Roadmap 原則

功能分為：

### Now
目前故事／平台運作必要。

### Next
第二、三個故事明確會用到。

### Later
有價值，但目前不值得增加複雜度。

例如：
- reusable engine：Next
- balanceSensor：Next
- tiltMaze：Next / Later
- 成就系統：Later
- 家長模式：Later
- 全站角色圖鑑：Later

---

## 9. 每次 Desktop/Codex 接手的簡短 Prompt

> 請先讀 GitHub `main` 最新的 `PROJECT_HANDOFF.md`、`INTERACTIVE_STORY_SOP.md`、對應故事 `STORY_SPEC.md` 與 DEVLOG。GitHub 是 source of truth。依已確認故事規格實作，不自行改寫故事。請先建立 feature branch，完成後回報 Changed / Fixed / Test performed / Known limitations 並建立 PR；使用者確認前不要 merge 到 main。

---

## 10. 產品層主動規劃要求

ChatGPT 在收到新需求時，不只回答「怎麼做」，還必須主動檢查：
- 對多故事入口是否有影響？
- 對共用 engine 是否有影響？
- 對 state / localStorage 是否有影響？
- 對圖片製作 SOP 是否有影響？
- 對平板 UI 是否有影響？
- 對 Git / 發布流程是否有影響？
- 5～10 本故事後是否仍可維護？

若有更完整的專案方案，應主動提出，而不是只做單點修補。
