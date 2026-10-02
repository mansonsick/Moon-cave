# 第五本工程接法｜2026-10-02

本輪基於 main `25f061fa479bc237cea44d6c9f82f1ba0d908a4e` 和美術 Draft PR #15 的 `d2c009a`，在 `feature/story-05-foundation` 實作。使用者已確認美術與三顆心規則、授權開始網頁，不包含發布。最新規格為本分支 STORY_SPEC v1.3，取代美術階段「連續三錯但保留本關燈」的舊提案。

## 檔案與共用邊界

- `index.html`／`app.js`／`styles.css`：本書選單、16 場景、三關、分層圖、霧／燈、學習、心、成功停留、寶石淨化、全螢幕與家長設定。
- `story.json`：由 `scripts/build_story05_content.py` 從已確認規格的短句編譯，包含場景和 label；中文不散落在 SVG／圖片生成指令中。
- `state.js`：字母組、題序、三顆心、完成／輔助／獨立集合及存檔驗證；每次正確最多發一盞燈，重試只清本關。
- `text.js`／`assets/text/`：指定私有字型本機渲染，283 個可換行短片段、161 個中文 label；字型不複製／不發布。
- `alphabet-audio.js`：繼承既有 AudioManager；單一字母聲完成或取消後才啟動答題，配樂壓至平常的 12%。來源清單見 `assets/audio/manifest.json`。
- `engine/moving-targets.js`：新增可共用的有界運動、按下快照／拖出取消和原圖 alpha 命中；既有 engine 模組與前四本程式沒有修改。
- 根目錄 `index.html`：英文科目新增第五本故事卡，封面只放霧夜、阿通、松鼠，沒有天使或月亮石破梗。

## 移動與觸控

字母在分離的寬鬆格位中以兩組不同週期作 X/Y 平滑漂移，同一怪物在右側活動區飄動；分離活動區直接保證不遮答案，比加入複雜避障物理更適合第一版。字母至少 64px；平板第三關可三欄兩排，窄手機增加場景內暗色活動空間和兩欄三排，原 16:9 插圖完整呈現、不裁切。

第一／二／三關運動速度係數 .9／1.2／1.5；慢速 .48 倍，停止 0 倍。逐幀時間最多 .06 秒，背景頁不追補，低幀率時寧可變慢。首輪保留右側答案間隔、怪物用較小完整翼形呈現，具體速度及怪物尺寸仍待孩子實機回饋。

按下目標時即凍結運動、鎖定同一 pointer，正常放開且移動不到 18px 才提交。拖出、取消、多指、空白或透明處不扣心；怪物使用原 PNG alpha ≥100 的區域，不算透明 padding／淡光暈。鍵盤 Enter／空白亦可選字母或怪物。成功／失誤／音訊播放／提示／家長設定／暫停都停止運動與計時。

第三顆心用完進石縫場景；按重新挑戰恢復三心、清本關三個完成集合、重新洗牌，前關、學習及寶石保留。重播、回學習、刷新、回選單不補心。從石縫回學習後再開始也執行同樣的本關重置。

## 音訊

首次按開始／繼續冒險才解鎖 Web Audio。26 字母改用 Wikimedia Commons 真人美式字母名称錄音；來源／作者／Public domain 或 CC BY-SA 3.0／4.0 授權逐檔保存，轉換 WAV 依原授權。詳見 assets/audio/letters/CREDITS.md。A /eɪ/ 與 I /aɪ/ 不再共用舊 TTS 的錯誤內容。學習卡可對照文字聽音，聽音挑戰在播音及重播期間隱藏、禁用全部字卡，播完才顯示並開始運動／倒數。音訊 URL 帶內容雜湊版本，避免快取舊聲音。

`scripts/build_story05_audio.py` 產生四個 12 秒原創八音盒／低哼／拍翅／低鼓配樂循環及四種提示音，沒有網路樣本或 Hide and Seek 旋律。背景 gain .18，字母 gain .9；播字母時背景再乘 .12，只有一條 ambience。總音訊約 4 MB。靜音／缺檔／解碼失敗改為看字輔助，字形提示需按準備好了才開始；完成標為 assisted，不誤記為獨立聽辨。

## 存檔與導覽

只讀寫 `adventure.story-05.state` 和共用 `adventure.settings.sound`。保存當前場景／關、心、洗牌順序、學習卡、三關完成／independent／assisted、寶石、淨化輪次、結局、字級與倒數／移動設定。無聲音、禁止 localStorage 或損壞資料不阻擋通關。

刷新先進本書選單，繼續後重新播放目前未答字母，不保存動畫位置或正在播放的時間。回本書選單保留全部進度、停止聲音與運動；再玩一次只重置本書，保留字級／家長難度設定。閱讀上一幕保留已領道具／完成字母，完成關卡只顯示成功而不重發獎；學習可回看。

取得月亮石前沒有空道具格／提示。隱藏刻紋不發光；有石仍能普通結局。S10 拖／先點寶石再點怪物才開淨化；五輪每輪手動照射、回饋等再照一次、同輪重複命中不計，過程不扣心，允許離開回村。第五輪化為天使並停留等繼續。

## 重建與測試

使用本機 Python、Pillow、numpy、Playwright；真人錄音重建使用 repo 保存的原檔／轉碼與 Chromium 解碼，不依賴 Windows 語音、網路或裝置 TTS。

```powershell
python scripts/build_story05_content.py
python scripts/build_story05_letters.py
python scripts/build_story05_audio.py
python scripts/render_story_text.py --font '../BpmfGenRyuMin-H.ttf' --story stories/story-05
python -X utf8 tests/story_05_test.py
python -X utf8 tests/story_05_visual_test.py
python -X utf8 tests/subject_hub_test.py
```

測試結果與實機限制詳見 QA_RESULTS.md。未授權直接合併或發布 main；美術 PR #15 保留作歷史文件來源，工程 PR 包含該批已確認美術。
