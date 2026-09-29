# 鏡頭動作挑戰（Story 03 試玩版）

2026-09-29，使用者要求站立改用影像、單腳站、跳躍、拋接球三次，並把動作穿插在三道數學門之間。先以 `experiments/camera-actions/` 獨立驗證，再由 Story 03 掛載相同元件。Story 02 已驗收的鏡頭三分區檔案保持不動。

## 模組

- `camera-action-source.js`：明確點擊才請求前鏡頭、480 px 長邊、不裁切、最多約 10 fps、一張影格等待推論完成後才送下一張。
- `camera-action-worker.js`：沿用本機 `vendor/mediapipe` 的 Pose Landmarker Lite，最多兩人；回傳短暫姿勢、球座標，不傳原始影像到主執行緒。
- `camera-actions.js`：純座標與時間的判定器，與故事／DOM 分離，可用合成序列測試。
- `ball-vision.js`：點取球色、HSV 色差遮罩、連通區形狀篩選；不是通用球類辨識模型。
- `camera-action-panel.js` / `.css`：預覽、提示、進度、相機／手動切換、成功後繼續；故事提供文字、存檔和下一幕 callback。

## 三種判定

| 挑戰 | 判定與初始參數 | 不計數／重新開始 |
| --- | --- | --- |
| 單腳站 8 秒 | 全身入鏡、雙腳站立校正 2 秒；一腳比另一腳抬高超過身高約 14%，支撐腳留在基準地面附近；身體位置接近校正位置。 | 失去穩定先暫停，連續約 0.75 秒重置；缺人／多人／腳不可見立即清空本次連續時間；換支撐腳須重新開始。 |
| 跳 5 下 | 先站立校正 2 秒；雙腳踝與臀部同時上移，再回到基準地面才加一次；落地後至少 0.45 秒間隔。 | 單腳抬起、只揮手、只移臀部、蹲下均不算；橫向或比例變動過大暫停；追蹤中斷不把落地當新一跳。 |
| 拋接球 3 次 | 請使用和衣服／背景不同的鮮明單色軟球；先點預覽中的球中央。需球在雙手附近停留、離手上升、下降回雙手附近並停留約 0.4 秒，才加一次。 | 沒球、靜止球、同色多個候選、球掉下去或沒在雙手停住均不計；追蹤中斷清除此輪拋接階段，已完成次數保留。 |

身體點需 confidence ≥ 0.65，座標完整且在畫面內；不得用辨識信心不足的腳或腕補算。重複／倒退時間戳不累加；兩影格間隔超過 0.6 秒須重新校正站立，拋接清除此輪階段。這些是可調整的工程初始參數，尚未用兒童平板實測建立誤差範圍。

球色影像縮小至長邊 160 px；球需足夠大且有彩度。以色相 ±16°、緊密近圓的連通區篩選；零個或多個候選都暫停。金色圓框顯示目前追蹤的物件。點畫面可重選球色；黑、白、透明、多色小球和強反光不可靠。雙手附近停留只是「接住」的視覺近似，無法證明手指抓牢；相似顏色的其他物件仍可能誤判。不能用本功能評量動作標準或保證每次準確。

## 失敗、權限與隱私

- 僅 `getUserMedia({audio:false, video:…})`，不錄音、不錄影、不上傳；不把影像、關鍵點、球色或權限保存到 localStorage。
- 相機明確 opt in；進頁不載模型、不彈權限。HTTPS 或 localhost 才能使用鏡頭。第一次讀取既有模型約 18 MB。
- 不支援、拒絕權限、15 秒沒回應、模型失敗、連續 8 秒沒有有效身體資料，回手動模式；任何時候可手動切換。
- 手動站立是普通 8 秒倒數；跳／接球由大人確認每次後按「完成一次」。畫面明說是手動模式，不把按鈕操作偽稱為影像辨識。
- 成功、取消、換模式、換挑戰／故事場景、換分頁、pagehide、題卷被其他分頁更換時，關閉 tracks、worker 和 requestAnimationFrame。晚到的權限同樣關閉；回前景不自動重啟。
- 成功畫面保留，需按「繼續」；無 Game Over。Story 03 只保存三個完成旗標，不保存尚未完成的秒數、姿勢或球軌跡。

## 驗證方式與來源

`tests/camera_actions_rules.js` 覆蓋合成姿勢、時間戳、正反例及實際繪製的像素色塊。`tests/camera_actions_test.py` 用人造 video stream、合成 landmarks 測試實際 UI／source／清理；另用本機真實 MediaPipe/WASM 對空白影格推論，確認模型載入和接線。這些測試不代表真人辨識已通過。

平板待驗收：前鏡頭全身構圖、足夠光線、鏡頭固定不晃、單腳站左右腳、連續跳與中途離鏡、軟球大小／顏色／拋高／遮擋、權限拒絕與回前景、舊款平板速度。人體比例、鏡頭角度、鬆衣服及球速均可能影響結果。

技術依據：[MediaPipe 官方 Web 指南](https://developers.google.com/edge/mediapipe/solutions/vision/pose_landmarker/web_js) 說明 normalized landmarks 與 worker 推論；[MDN getUserMedia](https://developer.mozilla.org/en-US/docs/Web/API/MediaDevices/getUserMedia) 和 [track.stop](https://developer.mozilla.org/en-US/docs/Web/API/MediaStreamTrack/stop) 說明安全來源、權限及清理。既有 vendor 授權與檔案雜湊見 `vendor/mediapipe/README.md` / `manifest.json`，本次沒有新增外部模型或服務。
