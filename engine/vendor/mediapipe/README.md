# MediaPipe camera lane dependency

Self-hosted, unmodified runtime files from `@mediapipe/tasks-vision` **1.0.1** (npm archive verified against its SHA-512 integrity), plus **Pose Landmarker Lite float16 v1** from Google's official model distribution. Exact files, source URLs and SHA-256 hashes are in `manifest.json`.

- Runtime: Copyright The MediaPipe Authors, Apache License 2.0. See `LICENSE` and [official source](https://github.com/google-ai-edge/mediapipe).
- Model: Google / BlazePose GHUM, Apache License 2.0 as specified on page 2 of the [official model card](https://storage.googleapis.com/mediapipe-assets/Model%20Card%20BlazePose%20GHUM%203D.pdf).
- API and model: [official Web guide](https://developers.google.com/edge/mediapipe/solutions/vision/pose_landmarker/web_js).

The camera option lazily loads the runtime, one compatible WASM binary and model, approximately 18 MB (29.3 MB stored including the alternative non-SIMD binary). Ordinary buttons and tilt never request these assets. No CDN, recognition service, telemetry integration, microphone, recording, image storage or uploads are used by the feature. Only temporary body coordinates cross from the worker to the game.

Only one person should be in view. Poor light, occlusion, device performance and browser support can prevent tracking; the game pauses and retains its button fallback. Physical tablet performance remains a separate acceptance check.
