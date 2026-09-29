// Camera actions opt in to the existing local pose model; Story 02 stays unchanged.
const timeout = (promise, ms) => {
  let timer;
  return Promise.race([promise, new Promise((_, reject) => { timer = setTimeout(() => reject(new Error('camera-timeout')), ms); })]).finally(() => clearTimeout(timer));
};
const stopTracks = stream => stream?.getTracks().forEach(track => track.stop());

export class CameraActionSource {
  constructor(kind) { this.generation = 0; this.kind = kind; }
  async start(video, onFault = () => {}) {
    this.stop(); const ticket = this.generation;
    if (!window.isSecureContext || !navigator.mediaDevices?.getUserMedia || !window.Worker || !window.OffscreenCanvas || !window.createImageBitmap) return false;
    this.video = video; this.onFault = onFault;
    try {
      // Called directly by the camera button. Never ask for microphone access.
      const permission = navigator.mediaDevices.getUserMedia({ audio: false, video: { facingMode: 'user', width: { ideal: 640 }, height: { ideal: 480 }, frameRate: { ideal: 30, max: 30 } } });
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
      const worker = new Worker(new URL('./camera-action-worker.js?v=actions-2', import.meta.url)); this.worker = worker;
      await timeout(new Promise((resolve, reject) => {
        worker.onerror = () => { reject(new Error('camera-worker')); if (this.active) this.fail(); };
        worker.onmessage = ({ data }) => {
          if (ticket !== this.generation) return;
          if (data.type === 'ready') resolve();
          else if (data.type === 'error') { reject(new Error('camera-model')); if (this.active) this.fail(); }
          else if (data.type === 'pose') {
            this.busy = false;
            if (!this.paused) { this.sample = data; this.sampleAt = performance.now(); }
          }
        };
        worker.postMessage({ type: 'init' });
      }), 30000);
      if (ticket !== this.generation) return false;
      this.active = true; this.paused = false; this.busy = false; this.lastCapture = 0; this.lastVideoTime = -1;
      const tick = async now => {
        if (!this.active || ticket !== this.generation) return;
        this.frame = requestAnimationFrame(tick);
        if (this.paused || this.busy || document.hidden || now - this.lastCapture < 50 || video.readyState < 2 || video.currentTime === this.lastVideoTime) return;
        this.busy = true; this.lastCapture = now; this.lastVideoTime = video.currentTime;
        try {
          const ratio = Math.min(480 / video.videoWidth, 480 / video.videoHeight);
          const width = Math.max(1, Math.round(video.videoWidth * ratio)), height = Math.max(1, Math.round(video.videoHeight * ratio));
          if (this.canvas.width !== width || this.canvas.height !== height) { this.canvas.width = width; this.canvas.height = height; }
          // Preserve the entire camera frame: no crop that would hide feet or misalign the ball picker.
          this.ctx.drawImage(video, 0, 0, width, height);
          const bitmap = await createImageBitmap(this.canvas);
          if (!this.active || ticket !== this.generation) { bitmap.close(); return; }
          worker.postMessage({ type: 'frame', bitmap, at: now, catch: this.kind === 'catch' }, [bitmap]);
        } catch { if (ticket === this.generation) this.fail(); }
      };
      this.frame = requestAnimationFrame(tick);
      return true;
    } catch { if (ticket === this.generation) this.stop(); return false; }
  }
  pause(value) { this.paused = value; this.sample = null; }
  setColour(colour) { this.sample = null; this.worker?.postMessage({type:'colour',colour}); }
  capturePhoto(canvas) {
    if (!this.active || this.video.readyState < 2 || !this.video.videoWidth) return false;
    const ratio = 480 / Math.max(this.video.videoWidth, this.video.videoHeight);
    canvas.width = Math.round(this.video.videoWidth * ratio); canvas.height = Math.round(this.video.videoHeight * ratio);
    const ctx = canvas.getContext('2d', {willReadFrequently:true});
    if (!ctx) return false;
    ctx.drawImage(this.video, 0, 0, canvas.width, canvas.height); return true;
  }
  read(now = performance.now()) {
    // Freshness uses delivery time; inference latency must not make every result
    // instantly stale. Old captures and repeated timestamps still cannot earn credit.
    return this.active && !this.paused && this.sample && now - this.sampleAt < 1000 && now - this.sample.at < 2000 ? this.sample : null;
  }
  fail() { const callback = this.onFault; this.stop(); callback?.(); }
  stop() {
    this.generation++; this.active = false; this.sample = null;
    cancelAnimationFrame(this.frame); this.worker?.terminate(); this.worker = null;
    stopTracks(this.stream); this.stream = null;
    if (this.video) { this.video.pause(); this.video.srcObject = null; this.video = null; }
    if (this.canvas) { this.canvas.width = 0; this.canvas.height = 0; this.canvas = null; }
  }
}
