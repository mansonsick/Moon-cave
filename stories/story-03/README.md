# Story 03《阿通與星光寶箱》

2026-09-29：工程試玩版，branch `feature/story-03-foundation`。尚未 merge 或部署，首頁未增加入口。規格／紙本來源為 Draft PR #9；本次工程另開 PR。

- [最新故事與工程規格](STORY_SPEC.md)
- [分層素材與重用方式](LAYERED_ART.md)
- [測試紀錄與限制](QA.md)
- [開發紀錄](DEVLOG.md)
- [故事入口](index.html)：在「準備探險紙」選難度、產生新題卷並列印。
- [舊版固定 PDF](worksheets/README.md)：保留作紙本練習，不是新版題卷碼對應題目。

## 使用

以本機 HTTP server 或經核准的 Pages 預覽開啟故事。展開「準備探險紙」，每關選前後數字各為一／兩位數與加減乘除，按「產生新題卷」，再列印三張紙。預設第一關 10 以內加減，第二關兩位數與一位數加減，第三關兩位數與兩位數加減。減法不出負數，除法可整除。

每張有同一題卷碼，依序 6／7／7 題；平板輸入完整同碼即可玩同一組。新碼含難度設定，格式為 `m2-六碼設定-八碼種子-兩碼檢查值`，不區分大小寫。舊的 1–24 位英數碼仍還原原來的簡單題卷，不會被新預設覆蓋。

孩子完成一頁，先在紙上寫數字，再查每頁的數字圖案對照表，在平板按題號逐位點選圖案密碼。每題靠左填，多的格子留白；例如 23 是兩個圖案，不是只取個位數。綠色勾勾表示正確，紅色叉號只要求修改該題，其他答案保留。問號提供解題提示。答對後等「繼續」。普通與祕密結局皆可達。新列印頁只有算式與空格，不再有計數圓圈或劃掉說明。

使用者已選擇 **符號密碼**，本版不需要鏡頭，也不要求機器辨認孩子的字跡。原 [鏡頭計畫](PAPER_AND_CAMERA_PLAN.md) 保留作未來研究，不是本版通關的前置條件。

中文為私有字型在本機產生的注音文字圖，字型檔沒有公開。重建：

```sh
python scripts/render_story_text.py --font /private/BpmfGenRyuMin-H.ttf --story stories/story-03
python tests/story_03_test.py --output ../hub-review/story03-web
python tests/story_03_difficulty_test.py --output ../hub-review/story03-difficulty
```
