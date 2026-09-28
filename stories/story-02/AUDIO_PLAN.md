> 2026-09-28 音效更新：依使用者要求完成 9 個原創合成 WAV，story.json 全部 available: true；沒有第三方取樣或網路音效。格式／來源／聽感與事件映射見 [AUDIO_ASSETS.md](AUDIO_ASSETS.md)，實作／測試見 ENGINEERING_PLAN.md、QA.md。

# Story 02 音效規劃｜《逃出虎姑婆的山屋》

> 2026-09-28 成品回饋：操作特效聲音 OK；未來背景音再小聲一點，場景特色要更明顯，不要都以風聲為主。本故事已確認完成，這些只列入 [後續改善](../../FUTURE_IMPROVEMENTS.md)，不修改現有音檔或音量。

版本：v1.0  
適用故事：Story 02《逃出虎姑婆的山屋》  
主要平台：平板瀏覽器  
原則：**重點場景使用背景音／環境音，操作只保留少量必要音效。**

文件狀態：由使用者提供的 `STORY02_AUDIO_PLAN.md` 收錄為素材製作參考，已依確認版 [STORY_SPEC.md](STORY_SPEC.md) 第 6 節同步；若有差異，以確認版為準。原創合成第一版已補齊九種聲音，見 [ASSET_MANIFEST.md](ASSET_MANIFEST.md)；下列音色方向可繼續依平板聽感調整。

已確認：**沒有既有設定時，預設音效開啟；孩子點「開始冒險」後才實際啟用 AudioContext。** 已保存的關閉設定必須保留。故事不等待音訊播放完成，聲音不可提前洩漏隱藏互動。

---

## 1. 音效設計原則

本故事不採「每按一下都有聲音」的遊戲化設計，而是：

1. **場景氣氛優先**
   - 用少量背景音／環境音建立「山林、山屋、逃跑、古廟」的氣氛。
   - 不需要每個場景都有不同音樂。

2. **操作音效只保留必要回饋**
   - 找到物品
   - 挑戰成功
   - 挑戰失敗／重試
   - 道具拖曳成功
   - 山神鈴祕密結局

3. **避免過度驚嚇**
   - 不使用突然爆音、尖叫、重低音 Jump Scare。
   - 虎姑婆可以有壓迫感，但整體仍適合低年級兒童。

4. **音效不可搶過故事**
   - 文字閱讀、圖片理解、互動仍是主體。
   - 背景音量必須明顯低於提示音效。

5. **所有音效都要能關閉**
   - 全站共用音效開關：
     - `🔊 音效開`
     - `🔇 音效關`
   - 設定寫入：
     - `adventure.settings.sound`

6. **預設不做全程背景音樂**
   - 只在重點場景播放短循環 BGM / Ambience。
   - 場景切換時淡入淡出，避免突然中斷。

---

## 2. 建議音訊分類

```text
audio/
├─ ambience/
│  ├─ forest-evening.wav
│  ├─ creepy-house.wav
│  ├─ bamboo-chase.wav
│  └─ temple-night.wav
│
└─ sfx/
   ├─ found-item.wav
   ├─ success.wav
   ├─ fail-soft.wav
   ├─ drag-lock.wav
   └─ secret-bell.wav
```

---

## 3. 背景音／環境音規劃

### A. `forest-evening`
用途：
- 封面
- 山路迷途
- 山屋外

聲音方向：
- 黃昏森林
- 風聲
- 蟲鳴
- 遠處鳥叫
- 很淡的神祕音色

感覺：
**陌生、神祕，但還沒有危險感。**

建議：
- 20～40 秒循環
- 音量低
- 無明顯旋律也可以

---

### B. `creepy-house`
用途：
- 虎姑婆山屋內
- 找怪異線索
- 找後門鑰匙
- 「別出聲」挑戰

聲音方向：
- 木屋輕微嘎吱聲
- 爐火／煮湯聲
- 偶爾風聲
- 很淡的低音氛圍
- 可偶爾加入輕微虎呼吸／腳步感，但不要太明顯

感覺：
**孩子開始覺得哪裡怪怪的。**

注意：
- 不要恐怖到蓋過閱讀
- 「別出聲」挑戰開始時可將背景音稍微降低，讓孩子更專注

---

### C. `bamboo-chase`
用途：
- 衝進竹林
- `tiltDodge` 逃跑挑戰
- 前往木橋

聲音方向：
- 快速風聲
- 竹葉摩擦
- 輕微奔跑節奏
- 緊張但有冒險感的節拍

感覺：
**開始真正逃跑。**

注意：
- 這是全故事節奏最快的背景音
- 不用做成恐怖追殺音樂
- 目標是「快跑！」而不是「被嚇到」

---

### D. `temple-night`
用途：
- 古廟
- 普通結局前
- 山神鈴祕密結局前

聲音方向：
- 夜風
- 很淡的鈴音殘響
- 空曠廟宇回音
- 木頭／布幔輕微晃動聲

感覺：
**追逐暫停，轉成神祕。**

若進入普通結局：
- 音樂逐漸放鬆
- 天亮後淡出

若觸發祕密結局：
- 先降低背景
- 播放 `secret-bell`
- 同時進入祕密結局的亮起／破法術畫面，不等待音效播完；音效無法播放時仍繼續。

`temple-night` 的鈴音殘響只是氣氛方向，不能用來指出鈴鉤位置或暗示可操作物件；可辨識的山神鈴回饋僅在成功拖入後觸發。

---

## 4. 操作音效規劃

### `found-item`
用途：
- 找到虎爪印
- 找到虎毛
- 找到尾巴
- 找到後門鑰匙
- 找到山神鈴

聲音：
- 短促、明亮的小提示音
- 不要像手機通知音

建議：
- 0.2～0.5 秒

---

### `success`
用途：
- 找齊三個線索
- 完成平板保持不動
- 完成竹林閃避
- 完成木橋平衡

聲音：
- 溫和的成功音
- 可以是 2～3 個上行音符

建議：
- 0.5～1 秒

---

### `fail-soft`
用途：
- Sensor 晃動過大
- 挑戰時間到
- 操作失敗需重試

聲音：
- 柔和的「咚」或下降提示音
- 不使用刺耳 buzzer

目的：
**告知重來，不讓孩子覺得被懲罰。**

---

### `drag-lock`
用途：
- 山神鈴拖到古廟鈴鉤
- 未來其他故事的正確凹槽放置

聲音：
- 「喀」＋短亮光聲
- 有磁吸／扣上的感覺

建議：
- 0.3～0.6 秒

---

### `secret-bell`
用途：
- **Story 02 最重要的特殊音效**
- 山神鈴放上古廟鈴鉤後播放

聲音方向：
- 清楚的古銅鈴聲
- 有較長回音
- 一聲或兩聲即可
- 之後接古廟亮起／虎姑婆法術解除

建議：
- 2～4 秒
- 此音效播放時，背景 `temple-night` 自動降音量

---

## 5. 場景音效對照表

| 場景 | 背景音 | 操作音效 |
|---|---|---|
| 封面 | forest-evening | 無 |
| 山路迷途 | forest-evening | 無 |
| 虎姑婆山屋 | creepy-house | found-item |
| 找三個怪線索 | creepy-house | found-item / success |
| 找後門鑰匙 | creepy-house | found-item |
| 別出聲 | creepy-house（降低音量） | success / fail-soft |
| 竹林逃跑 | bamboo-chase | success / fail-soft |
| 隱藏小路 | bamboo-chase 或低音量 forest-evening | found-item |
| 木橋 | bamboo-chase | success / fail-soft |
| 古廟 | temple-night | drag-lock |
| 普通結局 | temple-night → 淡出 | success |
| 祕密結局 | temple-night | drag-lock + secret-bell |

---

## 6. Audio Manager 共用規格

音效應做成共用 engine，不只服務 Story 02。

建議介面：

```js
audio.playSfx("found-item");
audio.playSfx("success");
audio.playSfx("fail-soft");

audio.setAmbience("forest-evening");
audio.setAmbience("creepy-house");
audio.stopAmbience();

audio.setEnabled(true);
audio.setEnabled(false);
```

不要在各 Scene 裡直接散落 `new Audio(...)`。

---

## 7. 平板瀏覽器注意事項

### 自動播放限制
手機／平板瀏覽器通常禁止未經使用者互動的自動播放。

因此：

- 無既有偏好時設定為開啟，並提供明顯的開／關；已有關閉偏好時維持關閉。
- 第一次點「開始冒險」後才初始化 Audio。
- 在使用者第一次明確點擊後，再開始播放背景音。
- 重新整理或恢復頁面後，保存的開啟偏好不代表已解除瀏覽器播放限制；必要時等待下一次明確操作，不阻塞故事。

### 頁面切換
- 背景音場景切換時使用約 0.5～1 秒淡出／淡入。
- 不要同時播放兩條長背景音。

### 暫停／切換 App
若頁面進入背景：
- 暫停背景音

回到頁面：
- 僅在先前確實播放且設定仍開啟時嘗試恢復該 Scene 背景音；若被阻擋，等待下一次明確操作，不補播過期 SFX。

---

## 8. 音量建議

相對比例：

```text
背景音 / Ambience：25～35%
操作 SFX：50～65%
山神鈴：65～75%
```

避免任何單一音效突然大聲。

若無全域音量 slider，至少在程式內固定此比例。

---

## 9. 音檔來源與授權

正式上 GitHub Pages 的音檔必須：

- 自製
- AI 生成且授權可使用
- 或明確可商用／可再散布的 royalty-free 音檔

不要直接抓：
- 電影
- 遊戲
- YouTube
- 商業音效包中的未授權素材

每個正式音檔最好在資產清單記錄來源與授權。

---

## 10. 檔案大小原則

背景音：
- 優先壓縮
- 單檔最好控制在約 0.5～2 MB

短 SFX：
- 盡量低於 100～300 KB

Story 02 整體音效資產目標：
- **約 5～8 MB 內**

避免為了音質讓平板第一次載入太慢。

---

## 11. Story Config 建議

未來 Story 02 可把音效寫入 config：

```js
scene: {
  id: "tiger_house",
  image: "scene-02.webp",
  ambience: "creepy-house",
  ...
}
```

互動：

```js
{
  action: "findObject",
  target: "tiger_fur",
  sfx: "found-item"
}
```

如此新故事只指定音效，不重新寫播放邏輯。

---

## 12. MVP 與後續

### Story 02 MVP 必做
- 音效開／關
- 4 個背景／環境音：
  - forest-evening
  - creepy-house
  - bamboo-chase
  - temple-night
- 5 個短 SFX：
  - found-item
  - success
  - fail-soft
  - drag-lock
  - secret-bell

### 暫時不做
- 全程背景配樂
- 語音旁白
- 多層動態混音
- 每個角色專屬聲音
- 複雜音量設定頁

先確認簡單音效是否真的提升小朋友的遊玩體驗，再擴充。
