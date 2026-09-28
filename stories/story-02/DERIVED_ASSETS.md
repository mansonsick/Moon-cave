# 衍生圖製作紀錄

2026-09-28；使用者授權最少量衍生圖，保留原圖。工具：內建 imagegen（imagegen skill）。
兩張圖均已在場景與平板截圖檢視，等待使用者視覺確認。遊戲引用下列新增檔案，未覆寫原圖。

## 古廟空鈴鉤

來源：[shrine.png](assets/images/shrine.png)；成品：[temple-empty-hook.png](assets/images/temple-empty-hook.png)。
移除原有大鈴／垂飾，保留屋簷空鉤，沒有額外提示發光。

實際 prompt：

> Use case: precise-object-edit. Edit target: supplied moonlit forest shrine illustration. Make an alternate game background with an EMPTY BELL HOOK. Remove ONLY the large brass hanging bell, red hanging tassel, and the lower dangling chain. Preserve the small dark metal attachment ring/hook under the horizontal roof beam at the same location so the child can later drag a bell there. Restore the wooden shrine wall naturally behind removed object. Preserve everything else: exact boy Atong and squirrel identity, pose, proportions, warm lanterns, stone deity statue, steps, trees, moon, lighting, landscape framing and original aspect ratio. No glow around the empty hook, no highlight, arrow, UI, text, or new objects. Keep all original art as unchanged as possible.

## 岔路小腳印

來源：[mountain-path.png](assets/images/mountain-path.png)；成品：[fork.png](assets/images/fork.png)。
保留阿通、小松鼠及原插圖風格，補木橋方向與自然小腳印；可點區與圖中腳印對齊。

實際 prompt：

> Use case: narrative scene variant. Using this exact landscape illustration as the visual identity reference, make a minimal alternate scene of a fork in the forest path after the escape. Preserve the exact boy Atong (short black hair, pale grey shirt, brown shorts and backpack), friendly squirrel, painterly storybook texture, mountain forest and moonlit palette. Keep the boy and squirrel on the left at similar scale. On the right midground show the clear main path leading to the near entrance of a weathered wooden footbridge. In the lower middle foreground, near x=48% y=83% of the image, a small less-travelled side trail enters grass, with just 3 or 4 small natural brown animal pawprints in the earth (each visible but subtle, no glow). Do not include a bell, temple, signs, arrows, text, UI, magical highlighting or scary violence. Landscape 1672x941 composition. Keep the important animal prints around the lower middle, separate from characters and bridge; this is a hidden clickable detail, not an obvious button.

尺寸與 SHA-256 見 [sources.json](assets/images/sources.json)。設定總覽圖未作為正式場景或角色切片。
