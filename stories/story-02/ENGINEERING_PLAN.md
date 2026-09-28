# Story 02 工程實作與後續計畫

2026-09-28 完成第一輪完整工程，使用者後續授權先發布供平板實測。依據 [STORY_SPEC.md](STORY_SPEC.md) v1.0 及本次工程交接補充。

## 來源與分支

main 基準 `436861ce6e00fa68646ab800bd35894312f9cb5b`；規格 PR #3 head `a07d24c8bd48e3be2aefb5a045389b29ed995cc7`。
工程 `feature/story-02-foundation` 從規格 head 建立，PR #4 最初以 `docs/story-02-plan` 為 base。使用者授權線上實測後，先合併規格 PR #3，再將工程 PR #4 改以 main 為 base 並合併發布；規格分支不刪除。
首頁及《月光洞》的程式、圖文、挑戰、存檔不變。

## 已實作模組

| 路徑 | 責任 |
| --- | --- |
| index.html / app.js | 靜態入口、ES modules、設定載入。 |
| story.json | 全場景、文字、圖片、點位、分支、道具、挑戰及音訊設定。 |
| state.js | schema、校驗、修復不完整進度、身份揭露判定。 |
| story.css | 竹林獨立小遊戲視覺。 |
| ../../engine/story-engine.js | 場景生命週期、背包、Reward、分支、文字圖、提示、重玩。 |
| ../../engine/storage.js | 故事 namespace、聲音偏好、儲存失敗仍可遊玩。 |
| ../../engine/interactions.js | 原圖百分比點位、Pointer Events 拖曳、放置鎖定、鑰匙圖形。 |
| ../../engine/challenges.js | findObjects、sensor／普通倒數、tiltDodge 按鈕及傾斜同一碰撞規則。 |
| ../../engine/sensors.js | 使用者手勢請求權限、資料有效性、校正、穩定判定及清理。 |
| ../../engine/audio-manager.js | 單 AudioContext／單 ambience、SFX、靜音、duck、過期操作取消。 |
| ../../engine/styles.css | 平板閱讀、點位、背包、A−／A+、Reward。 |
| ../../scripts/render_story_text.py | 指定本機字型產注音 PNG，不複製字型。 |
| ../../experiments/balance-sensor/index.html | 獨立 stillness／balance 與 8 秒 fallback。 |
| ../../experiments/audio/index.html | 實際音效、解鎖、靜音、切換與失敗處理。 |
| ../../tests/story_02_test.py / sensor_audio_test.py / story_02_audio_test.py | Pages 前綴 UI、觸控、存檔、感測、音訊輸出與場景觸發測試。 |

不把月光洞遷入 engine；沒有框架、打包器或遠端執行依賴。

## 場景與存檔

主線：`cover → path → house → welcome → clues → key → hide → bamboo → fork → bridge → temple → ordinary`。

隱藏：`fork → shrine → bridge`；`temple + bell + 自行拖入空鉤 → secret → secret-after`。

schema v1 保存 `version, scene, clues, inventory, completed, placed, ending, textScale`。
clues 為 prints／fur／tail；inventory 為 key／bell；completed 為 hide／bamboo／bridge；placed 為 bell。
只接受已知 ID、去重，缺少必要前提的存檔回到最近可玩節點；壞 JSON／未知 schema 安全重開。

固定 key `adventure.story-02.state`；音效 `adventure.settings.sound` 保存字串 true／false，預設 true。
重整等待「開始冒險」才恢復場景，已完成獎勵與放置結果保存，未完成挑戰重啟。
重玩僅重置 Story 02，保留共用音效偏好；不讀寫 moonCaveState／moonCaveTextScale，也不使用 localStorage.clear()。

## 挑戰及生命週期

- 鑰匙 15 秒可請求抽屜區域提示，30 秒可請求位置提示及「拿起鑰匙」，必要物不會卡死；背景時間不計入。
- stillness／balance：2 秒校正、8 秒計時；拒絕、無 API、無有效資料、中途斷訊均可普通 8 秒，替代按鈕一直可用。
- 初版可調參數：soft 8°、hard 18°、線性加速度 3 m/s²；stillness grace 800 ms，balance 1000 ms，真機待校正。
- stillness 距垂直 25° 內；balance 維持校正角度。換螢幕方向重新校正。輕微平衡偏移暫停、持續明顯偏移溫和重試。
- tiltDodge 三條路、五個障礙；碰撞回退並停約 650 ms，無 Game Over。預設按鈕，傾斜另按啟用，無資料回按鈕。
- 背景暫停，回前景須再操作；離場清理事件、frame、interval、拖曳殘影。Reward 永不自動消失。

## 音訊

九個 ID 與 ambience／sfx 目錄已有原創合成 WAV，全部 available: true；來源、hash 與重建方法見 AUDIO_ASSETS.md。沒有第三方錄音或網路取樣。
首次「開始冒險」才建立／resume AudioContext；封面聲音開關只改偏好。
同 ambience 不重啟，切換先停舊音，快速 A → B → A 不讓過期 callback 停掉目前音軌。
SFX 限連點／最多三聲，放鈴呼叫 drag-lock 與 secret-bell，鈴聲期間 duck 環境音。神光場景的 keepSfx 只保留同一次神鈴聲；其他場景取消過期 SFX。普通結局的 entrySfx 播放成功音，躲藏使用 ambienceScale: 0.5。短音效在解鎖後預載，背景返回若被瀏覽器暫停，下一次明確觸控再嘗試恢復。
音訊載入／解碼／播放失敗不阻塞，故事不等待音訊完成。

瀏覽器策略依 [MDN 感測權限](https://developer.mozilla.org/en-US/docs/Web/API/DeviceOrientationEvent/requestPermission_static) 與 [Web Audio 建議](https://developer.mozilla.org/en-US/docs/Web/API/Web_Audio_API/Best_practices)。

## 接續順序

1. 審工程 PR，確認衍生圖、點位與小遊戲外觀。
2. iPad／Android 真機測姿勢、觸控與縮放；sensor 不穩可固定按鈕／普通倒數。
3. 在實體平板確認原創合成音效的音量／音色，必要時調整各檔 volume 或替換同 ID 音檔。
4. 本次先依使用者授權發布直接網址供平板實測；完成上述驗收後，再確認首頁卡片與完整正式版。
