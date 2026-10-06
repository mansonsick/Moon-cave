# Story 06 audio attribution

## The 37 Zhuyin recordings

- Work: 國語注音符號手冊 — independently downloadable audio materials (2017).
- Author / publisher: 教育部終身教育司 (Ministry of Education, Taiwan).
- [Official source and separate audio licence](https://language.moe.gov.tw/001/Upload/files/site_content/M0001/juyin/).
- [Official symbol / playback table](https://language.moe.gov.tw/001/Upload/files/site_content/M0001/juyin/html_ch/index.html).
- [Independent materials ZIP](https://language.moe.gov.tw/001/Upload/files/site_content/M0001/juyin/bopomofo_materials_20170213.zip).
- Licence for these independent audio files: [Creative Commons Attribution 4.0 International](https://creativecommons.org/licenses/by/4.0/).
- Changes: none to the recordings. Each `symbols/<Unicode>.wav` contains the original WAV bytes from `audio/F1.WAV` through `audio/F37.WAV`. Playback volume / ambience ducking are applied in the browser.
- `manifest.json` records each symbol, original ZIP entry, duration, SHA-256 and the source package / official mapping SHA-256. The HTML table's `play('aN')`, symbol's stroke entry and `audio/FN.WAV` were matched rather than inferring identity from the sound or a text-to-speech engine.

The complete handbook's separate BY-ND 3.0 TW licence is **not** the licence for this independently downloaded audio package. No handbook pages or official font have been redistributed.

## Project-created ambience and feedback

`quiet-forest`, `cricket-song`, `stream-song`, `bird-song`, `found-item`, `success`, `fail-soft`, `secret-bell`, and `forest-celebration` are original deterministic synthesis in `scripts/build_story06_audio.py`. There are no downloaded music samples, recordings from previous stories, or commercial songs.

The original forest ambience is quiet and advances with restored sounds; one ambience plays at a time. Symbol voice further ducks ambience. Both endings stop the loop.

`forest-celebration` is a new original 10.8-second wordless melody with choir-like harmonic synthesis, gentle chords and bell accents. It contains no human vocal recording or sampled song. It plays once on stage completion and on each ending; explicit replay is available on endings. Continuing, leaving, muting or hiding the page cancels it. Completion does not require listening until it ends.

## Review limits

All 37 recordings were mapped, decoded, checked for distinct nonempty PCM and played to completion in a browser. This is not a claim that a human listened to every recording. The parent-facing [trial page](../../audio-review.html) allows each symbol to be heard; family tablet listening remains part of final acceptance.
