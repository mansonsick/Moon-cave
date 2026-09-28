// Only transient, local body coordinates. Camera frames are never saved or uploaded.
export function bodyCenter(poses) {
  if (poses?.length !== 1) return null;
  const points = poses[0];
  const valid = p => p && Number.isFinite(p.x) && Number.isFinite(p.y) && p.x >= 0 && p.x <= 1 && p.y >= 0 && p.y <= 1 && p.visibility >= .55 && (p.presence === undefined || p.presence >= .55);
  // Prefer the hips: waving a hand must not change the lane. Shoulders allow a closer view.
  for (const [a, b] of [[23, 24], [11, 12]]) {
    if (valid(points[a]) && valid(points[b]) && Math.abs(points[a].x - points[b].x) >= .025)
      return 1 - (points[a].x + points[b].x) / 2; // Matches the mirrored preview.
  }
  return null;
}

export class CameraLaneTracker {
  constructor() { this.reset(); }
  reset() { this.lane = null; this.x = null; this.candidate = null; this.since = 0; this.last = 0; }
  update(x, at) {
    if (!Number.isFinite(x) || x < 0 || x > 1) { this.reset(); return null; }
    if (at - this.last > 600) this.reset();
    this.last = at; this.x = this.x === null ? x : this.x * .35 + x * .65;
    let next = Math.min(2, Math.floor(this.x * 3));
    // A small boundary margin prevents rapid left/centre/right flicker.
    if (this.lane !== null && this.x >= this.lane / 3 - .025 && this.x <= (this.lane + 1) / 3 + .025) next = this.lane;
    if (next !== this.candidate) { this.candidate = next; this.since = at; }
    if (at - this.since >= (this.lane === null ? 450 : 140)) this.lane = next;
    return this.lane === null ? null : { lane: this.lane, x: this.x };
  }
}

const timeout = (promise, ms) => {
  let timer;
  return Promise.race([promise, new Promise((_, reject) => { timer = setTimeout(() => reject(new Error('camera-timeout')), ms); })]).finally(() => clearTimeout(timer));
};
const stopTracks = stream => stream?.getTracks().forEach(track => track.stop());

export class CameraLaneSource {
  constructor() { this.generation = 0; this.tracker = new CameraLaneTracker(); }
  async start(video, onFault = () => {}) {
    this.stop(); const ticket = this.generation;
    if (!window.isSecureContext || !navigator.mediaDevices?.getUserMedia || !window.Worker || !window.OffscreenCanvas || !window.createImageBitmap) return false;
    this.video = video; this.onFault = onFault;
    try {
      // Called directly by the camera button. Never ask for microphone access.
      const permission = navigator.mediaDevices.getUserMedia({ audio: false, video: { facingMode: 'user', width: { ideal: 640 }, height: { ideal: 480 }, frameRate: { ideal: 15, max: 20 } } });
      permission.then(stream => { if (ticket !== this.generation) stopTracks(stream); }, () => {});
      const stream = await timeout(permission, 15000);
      if (ticket !== this.generation) { stopTracks(stream); return false; }
      this.stream = stream; video.srcObject = stream;
      for (const track of stream.getVideoTracks()) track.addEventListener('ended', () => { if (ticket === this.generation) this.fail(); }, { once: true });
      await timeout(video.play(), 8000);
      if (ticket !== this.generation) return false;
      this.canvas = document.createElement('canvas'); this.canvas.width = 480; this.canvas.height = 360;
      this.ctx = this.canvas.getContext('2d', { alpha: false });
      if (!this.ctx) throw new Error('camera-canvas');
      const worker = new Worker(new URL('./camera-worker.js?v=camera-1', import.meta.url)); this.worker = worker;
      await timeout(new Promise((resolve, reject) => {
        worker.onerror = () => { reject(new Error('camera-worker')); if (this.active) this.fail(); };
        worker.onmessage = ({ data }) => {
          if (ticket !== this.generation) return;
          if (data.type === 'ready') resolve();
          else if (data.type === 'error') { reject(new Error('camera-model')); if (this.active) this.fail(); }
          else if (data.type === 'pose') {
            this.busy = false;
            this.sample = this.tracker.update(bodyCenter(data.poses), data.at);
            this.sampleAt = data.at;
          }
        };
        worker.postMessage({ type: 'init' });
      }), 30000);
      if (ticket !== this.generation) return false;
      this.active = true; this.busy = false; this.lastCapture = 0; this.lastVideoTime = -1;
      const tick = async now => {
        if (!this.active || ticket !== this.generation) return;
        this.frame = requestAnimationFrame(tick);
        if (this.busy || document.hidden || now - this.lastCapture < 100 || video.readyState < 2 || video.currentTime === this.lastVideoTime) return;
        this.busy = true; this.lastCapture = now; this.lastVideoTime = video.currentTime;
        try {
          const ratio = Math.min(480 / video.videoWidth, 480 / video.videoHeight);
          const width = Math.max(1, Math.round(video.videoWidth * ratio)), height = Math.max(1, Math.round(video.videoHeight * ratio));
          if (this.canvas.width !== width || this.canvas.height !== height) { this.canvas.width = width; this.canvas.height = height; }
          // Preserve the entire camera frame: no crop that would misalign the thirds.
          this.ctx.drawImage(video, 0, 0, width, height);
          const bitmap = await createImageBitmap(this.canvas);
          if (!this.active || ticket !== this.generation) { bitmap.close(); return; }
          worker.postMessage({ type: 'frame', bitmap, at: now }, [bitmap]);
        } catch { if (ticket === this.generation) this.fail(); }
      };
      this.frame = requestAnimationFrame(tick);
      return true;
    } catch { if (ticket === this.generation) this.stop(); return false; }
  }
  read(now = performance.now()) {
    return this.active && this.sample && now - this.sampleAt < 600 ? this.sample : null;
  }
  fail() { const callback = this.onFault; this.stop(); callback?.(); }
  stop() {
    this.generation++; this.active = false; this.sample = null; this.tracker.reset();
    cancelAnimationFrame(this.frame); this.worker?.terminate(); this.worker = null;
    stopTracks(this.stream); this.stream = null;
    if (this.video) { this.video.pause(); this.video.srcObject = null; this.video = null; }
    if (this.canvas) { this.canvas.width = 0; this.canvas.height = 0; this.canvas = null; }
  }
}
