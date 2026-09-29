# Story 03《阿通與星光寶箱》

2026-09-29：工程試玩版，branch `feature/story-03-foundation`。尚未 merge 或部署，首頁未增加入口。規格／紙本來源為 Draft PR #9；本次工程另開 PR。

- [最新故事與工程規格](STORY_SPEC.md)
- [分層素材與重用方式](LAYERED_ART.md)
- [測試紀錄與限制](QA.md)
- [開發紀錄](DEVLOG.md)
- [故事入口](index.html)、[範例題卷列印](print.html?code=5a2vgas12)
- [舊版固定 PDF](worksheets/README.md)：保留作紙本練習，不是新版題卷碼對應題目。

## 使用

以本機 HTTP server 或經核准的 Pages 預覽開啟故事。展開「準備探險紙」，輸入紙上的題卷碼，或產生新題卷，再列印三張紙。每張有同一題卷碼，依序 6／7／7 題；平板輸入同碼即可玩同一組。題卷碼不區分大小寫，允許 1–24 個英數字。

孩子完成一頁，在對應關卡輸入六／七格答案。也可按問號逐題點數，減法由孩子自行點掉圓點。答對後等「繼續」。普通與祕密結局皆可達。

目前已完成 **手動數字輸入**，沒有顯示假的相機辨識按鈕。手寫數字辨識依 [鏡頭計畫](PAPER_AND_CAMERA_PLAN.md) 另做獨立實驗、真機驗證後才接入；辨識器不得用正解猜候選。

中文為私有字型在本機產生的注音文字圖，字型檔沒有公開。重建：

```sh
python scripts/render_story_text.py --font /private/BpmfGenRyuMin-H.ttf --story stories/story-03
python tests/story_03_test.py --output ../hub-review/story03-web
```
