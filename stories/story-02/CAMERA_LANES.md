# 竹林鏡頭站位模式

2026-09-28 後續驗收：使用者確認鏡頭及移動偵測功能 OK，故事本階段完成，維持目前實作。方法已整理於 [共用重用筆記](../../engine/SENSORS_REUSE.md)；未提供機型／瀏覽器版本，不據此推論全面相容。

依使用者 2026-09-28 要求，新增可選的左／中／右人體站位控制。原按鈕、傾斜、碰撞、五障礙、獎勵、進度與雙結局規則不變。

## 試玩

- [直接測試竹林](https://mansonsick.github.io/Moon-cave/experiments/camera-lanes/)：不用重玩故事，不讀寫故事存檔。
- [Story 02](https://mansonsick.github.io/Moon-cave/stories/story-02/)：竹林關卡選「試試鏡頭站位」。
- 固定放好平板，允許前鏡頭，讓頭及身體入鏡；一次一人，左右小步移動，留出方便移動的空間。不需拿著平板跑動。
- 鏡像畫面分成三等分；淡綠色表示目前控制區。站在左／中／右即控制同側路線。
- 鏡頭不穩可隨時選「使用左右按鈕」；不支援／拒絕權限也能通關。

## 模組及判定

`engine/camera-lanes.js` 管理權限、取樣、身體中心及三區判定；`camera-worker.js` 在背景執行 MediaPipe 推論。固定版 JS、WASM、Lite 模型及 Apache 2.0 授權位於 `engine/vendor/mediapipe/`。`challenges.js` 沿用同一 tiltDodge 碰撞規則，只有 `scene.cameraEnabled: true` 才出現選項，目前僅 Story 02 竹林。

優先用左右髖部中心，髖部看不清時用肩膀中心；揮手不直接改變路線。需有效座標與足夠可見度，多於一人或無人時不猜測路線。鏡像座標加約 450 ms 初次穩定、140 ms 換區確認及 2.5% 分界緩衝，減少抖動。超過 600 ms 的辨識結果視為過期，障礙暫停，重新辨識後繼續。

## 權限及失敗處理

- 只在點鏡頭模式後要求 video，不要求麥克風。沒有錄影、上傳、影像存檔、身份識別或外部辨識服務；只暫存本機畫面與身體座標。
- 全部資源由本站提供；按鈕／傾斜不載入模型。首次約 18 MB，兩種 WASM 相容版本合計儲存約 29.3 MB。來源與雜湊見 [vendor README](../../engine/vendor/mediapipe/README.md)。
- 權限等待最多 15 秒、模型準備最多 30 秒；失敗回按鈕。取消／逾時後才同意的 stream 立即停止。
- 看不清人先暫停，8 秒仍無有效站位則關鏡頭並回按鈕。人物離場、畫面停住、模型失敗、鏡頭中斷均不永久卡關。
- 切回按鈕／傾斜、完成、離場、背景、pagehide 時，停止影像軌道、終止 worker、清空預覽與 canvas。回來需再點選，背景時間不算進度。
- 相機狀態及姿勢不存檔。Story 02 schema、月光洞 key、首頁及既有插圖均不變。

## 已測與限制

`camera_lanes_test.py` 12 組通過：真實模型／WASM 對空白影像推論、合成 video／landmarks 驅動正式遊戲、三區／五障礙、鏡像、防抖、無人／多人暫停、權限拒絕／忽略／不支援／延遲授權、模型失敗、前背景清理、正式故事存檔隔離及多寬度排版。原故事／感測／音訊 25 組也重跑通過。

工程未自行操作實體鏡頭；使用者已回報鏡頭／移動偵測可用。其他 Safari／Chrome 機型的方向、距離、光線、速度與兒童身形效果不因此保證一致。較舊或缺少 Worker／OffscreenCanvas／ImageBitmap 的瀏覽器使用按鈕；此模式保持可選。

官方依據：[MediaPipe Web guide](https://developers.google.com/edge/mediapipe/solutions/vision/pose_landmarker/web_js)、[camera permission / HTTPS](https://developer.mozilla.org/en-US/docs/Web/API/MediaDevices/getUserMedia)。
