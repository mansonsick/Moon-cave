// Classic worker keeps MediaPipe's WASM loader compatible with importScripts.
// Self-hosted assets only; no camera data leaves this worker/page.
let detector;
self.onmessage = async ({ data }) => {
  try {
    if (data.type === 'init') {
      const base = new URL('./vendor/mediapipe/', self.location.href);
      const { FilesetResolver, PoseLandmarker } = await import(new URL('vision_bundle.mjs', base).href);
      const wasm = await FilesetResolver.forVisionTasks(new URL('wasm/', base).href.replace(/\/$/, ''));
      detector = await PoseLandmarker.createFromOptions(wasm, {
        baseOptions: { modelAssetPath: new URL('pose_landmarker_lite.task', base).href, delegate: 'CPU' },
        runningMode: 'VIDEO', numPoses: 2, minPoseDetectionConfidence: .6,
        minPosePresenceConfidence: .6, minTrackingConfidence: .6, outputSegmentationMasks: false,
      });
      self.postMessage({ type: 'ready' });
    } else if (data.type === 'frame') {
      try {
        const result = detector.detectForVideo(data.bitmap, data.at);
        self.postMessage({ type: 'pose', poses: result.landmarks, at: data.at });
      } finally { data.bitmap.close(); }
    }
  } catch { self.postMessage({ type: 'error' }); }
};
