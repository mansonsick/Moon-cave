# 已驗收的體感與鏡頭方法：後續故事重用筆記

2026-09-28：使用者確認 Story 02 成品可保留，鏡頭與移動偵測功能 OK。以下記錄目前已使用的方法供下一本故事重用；本次沒有修改 engine 或既有故事。未提供測試裝置／瀏覽器版本，這份驗收不代表所有裝置均相容。

## 可用模組

| 需求 | 現有方法與入口 | 判定及替代操作 |
| --- | --- | --- |
| 躲藏不動 | `stabilityChallenge` + `MotionSource` + `StabilityTracker('stillness')` | 平板近直立、校正約 2 秒、穩定 8 秒；晃動約 800 ms 後重試。可用普通 8 秒倒數。 |
| 保持平衡 | 同上，`StabilityTracker('balance')` | 以校正姿勢為準；輕微偏移暫停，明顯偏移約 1 秒重試。可用普通 8 秒倒數。 |
| 傾斜閃躲 | `tiltDodge` + `MotionSource` | 三條路、五障礙；校正約 2 秒，依直橫向取 gamma／beta，左右約 12° 換路；保留左右按鈕。 |
| 鏡頭三區站位 | `tiltDodge` + `CameraLaneSource` + `camera-worker.js` | 固定平板、前鏡頭鏡像。髖部中心優先，肩膀備援；左右三等分。無人／多人先暫停，8 秒無有效結果回按鈕。 |

檔案：`challenges.js`（挑戰）、`sensors.js`（動作感測）、`camera-lanes.js`（取樣／換區）、`camera-worker.js`（本機模型推論）。

## 用 StoryEngine 接新故事

1. 新故事以自己的 `story.json`、文字圖、圖片及 state 接入，不修改 Story 02 設定。
2. 場景 `type` 可選 `stillnessSensor`、`balanceSensor`、`tiltDodge`；每幕仍配置 `title`、`text`、`image`、`reward`、`next`。
3. 只有要用鏡頭的 `tiltDodge` 場景設定 `cameraEnabled: true`。原按鈕與傾斜會同時保留；不要把相機變成通關必需。
4. 穩定挑戰參數放 `config.challenges.stillness`／`balance`。Story 02 是 8 秒，不是月光洞舊版的 15 秒。門檻目前 soft 8°、hard 18°、線性加速度 3 m/s²；新故事若調整，另外實測。
5. 接上挑戰共用介面標籤、成功／重試文字及 `camera-*` 標籤；使用同一注音產圖流程，不公開字型。`StoryEngine` 會傳入 `text`、`button`、`audio` 與完成回呼。
6. 由新故事自己的狀態保存挑戰是否完成。相機畫面、姿勢、permission、目前路線及瞬時計時不保存，也不接觸其他故事的存檔。

## 單獨重用控制器

`tiltDodge({ panel, text, button, audio, onComplete, cameraEnabled: true })` 回傳 cleanup。`text(id)` 產生標籤節點、`button(id, handler)` 產生按鈕；`audio` 可省略。完成後及離場都要呼叫 cleanup，成功訊息等待孩子下一次操作。

若只要站位資料：由明確按鈕手勢呼叫 `CameraLaneSource.start(video, onFault)`，成功後用 `read()` 取得 `{ lane: 0|1|2, x }`，資料缺失時回傳 null；離場呼叫 `stop()`。預覽必須鏡像且完整顯示，不能任意裁切造成三區位置不一致。

鏡頭換區使用約 450 ms 初次穩定、140 ms 換區確認、2.5% 分界緩衝；超過 600 ms 的結果不採用。動作感測同樣拒絕空值與過期資料；旋轉螢幕後重新校正。

## 必須一起保留的行為

- 權限由明確手勢觸發；相機只要求 video，不開麥克風、不錄影、不上傳、不存影像。
- 相機固定版 MediaPipe 1.0.1／Lite v1 在本站、worker 在本機運算。只在鏡頭模式載入，首次約 18 MB；保留 [授權及雜湊](vendor/mediapipe/README.md)，更新版本時重驗。
- 拒絕／忽略權限、不支援、模型載入失敗、感測中斷都可使用普通操作。取消後才授權的 stream 立即停止。
- 完成、切換模式、離場、背景、pagehide 均清理軌道、worker、事件與計時。恢復前景需孩子重新操作，背景時間不算進度。
- 只做可恢復的碰撞或重試，不設 Game Over。

## 可直接使用的測試

- [鏡頭三區試玩](https://mansonsick.github.io/Moon-cave/experiments/camera-lanes/)：不讀寫故事存檔。
- [穩定感測試玩](https://mansonsick.github.io/Moon-cave/experiments/balance-sensor/)。
- `tests/camera_lanes_test.py`：12 組鏡頭／資源清理與整合檢查。
- `tests/sensor_audio_test.py`：感測校正、門檻、替代及前背景流程。
- `tests/story_02_test.py`：既有故事的按鈕、觸控、存檔與完整路線基準。

工程自動測試使用合成影像／事件；後續每本仍要在目標平板測站位距離、光線、鏡頭方向、權限及操作手感。Story 02 的詳細實作／歷史測試見 [CAMERA_LANES.md](../stories/story-02/CAMERA_LANES.md)。
