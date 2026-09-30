# 統一注音文字圖

所有後續故事、首頁及新增介面的兒童可見中文，使用使用者提供的 **BpmfGenRyuMin-H.ttf**。字型本體留在本機，網站只部署透明 PNG；不需要在網站載入字型或執行產圖程式。

```sh
python -m pip install Pillow==12.2.0
python scripts/render_zhuyin.py --font "/private/path/BpmfGenRyuMin-H.ttf" --manifest assets/hub-text/text.json
```

`--font` 指向使用者提供的原檔，請勿把範例路徑當成實際位置。不要複製字型進專案，也不要 commit 字型。`.gitignore` 已排除常見字型副檔名；未來若確認可公開嵌入，需另行調整政策。

`text.json` 保留純文字、顏色及尺寸；產出的每張 PNG 與它放在同一目錄。字型以 192 px 渲染並保留透明邊界，所有文字使用相同高度基準，以利縮放與排版。

製作新故事時，可在該故事資產目錄新增同格式 manifest，再使用同一支離線工具。不涉及共用 story engine 重構。

Story 02 使用同一字型與 Pillow 產圖策略，另以 `render_story_text.py` 從 `story.json.labels` 分成可換行短片段，輸出尺寸及整句可存取文字：

```sh
python scripts/render_story_text.py --font "/private/path/BpmfGenRyuMin-H.ttf"
```

預設更新 `stories/story-02/assets/text/`；修改文案後應重新產圖並核對，不把字型原檔放入 repository。

修改文字後：

1. 重新產圖並逐句檢查多音字與輕聲；字型的預設讀音不保證適合所有語境。
2. 檢查中文字右側的注音、聲調與最末字不被裁切，確認平板小尺寸和雙指縮放後可讀。
3. 更新圖片對應的 `alt`、按鈕名稱、圖片尺寸與必要的排版比例，保留可存取文字。
4. 只提交 manifest、PNG、引用它們的頁面及文件，不提交字型檔。

## Story 03 可列印練習紙

首頁的科目入口使用獨立 `assets/hub-text/subject-text.json`，避免新增文字時連帶重算既有故事文字圖的共同高度：

```sh
python scripts/render_zhuyin.py --font /private/path/BpmfGenRyuMin-H.ttf --manifest assets/hub-text/subject-text.json
```

只會更新這份 manifest 的科目標籤與說明；原字型仍留在本機。

另有 Story 03 列印檔產生工具 `build_story03_worksheets.py`，從題卷 JSON 輸出三頁 A4 練習紙、獨立解答及答案格座標。中文仍使用本機指定字型渲染，PDF 不嵌入字型；重建方式與驗證見 [列印說明](../stories/story-03/worksheets/README.md)。

## Story 02 原創合成音訊

重建已交付的 9 個 WAV 及音訊 manifest：

```sh
python -m pip install numpy scipy
python scripts/build_story02_audio.py
```

固定亂數種子，以波形與濾波雜訊合成，不讀取第三方音訊。素材與播放規則見 [AUDIO_ASSETS.md](../stories/story-02/AUDIO_ASSETS.md)。網站直接播放 WAV，不需執行此工具。
