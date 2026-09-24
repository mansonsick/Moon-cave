# 統一注音文字圖

所有後續故事、首頁及新增介面的兒童可見中文，使用使用者提供的 **BpmfGenRyuMin-H.ttf**。字型本體留在本機，網站只部署透明 PNG；不需要在網站載入字型或執行產圖程式。

```sh
python -m pip install Pillow==12.2.0
python scripts/render_zhuyin.py --font "/private/path/BpmfGenRyuMin-H.ttf" --manifest assets/hub-text/text.json
```

`--font` 指向使用者提供的原檔，請勿把範例路徑當成實際位置。不要複製字型進專案，也不要 commit 字型。`.gitignore` 已排除常見字型副檔名；未來若確認可公開嵌入，需另行調整政策。

`text.json` 保留純文字、顏色及尺寸；產出的每張 PNG 與它放在同一目錄。字型以 192 px 渲染並保留透明邊界，所有文字使用相同高度基準，以利縮放與排版。

製作新故事時，可在該故事資產目錄新增同格式 manifest，再使用同一支離線工具。不涉及共用 story engine 重構。

修改文字後：

1. 重新產圖並逐句檢查多音字與輕聲；字型的預設讀音不保證適合所有語境。
2. 檢查中文字右側的注音、聲調與最末字不被裁切，確認平板小尺寸和雙指縮放後可讀。
3. 更新圖片對應的 `alt`、按鈕名稱、圖片尺寸與必要的排版比例，保留可存取文字。
4. 只提交 manifest、PNG、引用它們的頁面及文件，不提交字型檔。
