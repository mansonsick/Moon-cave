const finite = value => typeof value === 'number' && Number.isFinite(value);
export const angleDistance = (a, b) => Math.abs(((a - b + 540) % 360) - 180);
export const screenAngle = () => screen.orientation?.angle ?? window.orientation ?? 0;

// Permission is requested only by start(), which is called from a child-initiated button.
export class MotionSource {
  constructor() { this.sample = null; this.motion = null; this.active = false; this.generation = 0; }
  async start() {
    this.stop(); const generation = ++this.generation;
    if (!window.isSecureContext || !window.DeviceOrientationEvent) return false;
    let timer;
    try {
      const permissions = [window.DeviceOrientationEvent, window.DeviceMotionEvent]
        .filter(api => typeof api?.requestPermission === 'function')
        .map(api => api.requestPermission());
      const results = await Promise.race([
        Promise.all(permissions),
        new Promise(resolve => { timer = setTimeout(() => resolve(['denied']), 10000); }),
      ]);
      if (generation !== this.generation || results.some(value => value !== 'granted')) return false;
      this.active = true;
      this.onOrientation = event => {
        if (!finite(event.beta) || !finite(event.gamma)) return;
        this.sample = { beta: event.beta, gamma: event.gamma, at: performance.now(), screen: screenAngle() };
      };
      this.onMotion = event => {
        const a = event.acceleration;
        if (a && [a.x, a.y, a.z].every(finite)) this.motion = { amount: Math.hypot(a.x, a.y, a.z), at: performance.now() };
      };
      window.addEventListener('deviceorientation', this.onOrientation);
      window.addEventListener('devicemotion', this.onMotion);
      return true;
    } catch { return false; } finally { clearTimeout(timer); }
  }
  read(now = performance.now()) {
    if (!this.active || !this.sample || now - this.sample.at > 600) return null;
    return { ...this.sample, shake: this.motion && now - this.motion.at < 600 ? this.motion.amount : 0 };
  }
  stop() {
    this.generation++; this.active = false; this.sample = null; this.motion = null;
    if (this.onOrientation) window.removeEventListener('deviceorientation', this.onOrientation);
    if (this.onMotion) window.removeEventListener('devicemotion', this.onMotion);
  }
}

// Pure calibration/timing state, shared by both sensor challenges and deterministic tests.
export class StabilityTracker {
  constructor(kind, config = {}) {
    this.kind = kind;
    this.config = { duration: 8000, calibration: 2000, softAngle: 8, hardAngle: 18,
      shake: 3, grace: kind === 'stillness' ? 800 : 1000, ...config };
    this.reset();
  }
  reset() { this.baseline = null; this.candidate = null; this.calibrated = 0; this.elapsed = 0; this.bad = 0; this.status = 'calibrating'; }
  upright(s) { return Math.abs(s.screen % 180) === 90 ? Math.abs(Math.abs(s.gamma) - 90) < 25 : Math.abs(Math.abs(s.beta) - 90) < 25; }
  step(sample, dt) {
    dt = Math.min(Math.max(dt, 0), 120);
    if (this.status === 'complete' || this.status === 'failed') return this.status;
    if (!sample) { this.calibrated = 0; this.candidate = null; return this.status = 'waiting'; }
    if (!this.baseline) {
      if (this.kind === 'stillness' && !this.upright(sample)) {
        this.calibrated = 0; this.candidate = null; return this.status = 'upright';
      }
      const c = this.candidate;
      if (!c || c.screen !== sample.screen || angleDistance(c.beta, sample.beta) > 5 || angleDistance(c.gamma, sample.gamma) > 5 || sample.shake > this.config.shake) {
        this.candidate = sample; this.calibrated = 0;
      } else this.calibrated += dt;
      if (this.calibrated >= this.config.calibration) { this.baseline = this.candidate; this.elapsed = 0; }
      return this.status = 'calibrating';
    }
    if (sample.screen !== this.baseline.screen) { this.reset(); return this.status; }
    const deviation = Math.max(angleDistance(sample.beta, this.baseline.beta), angleDistance(sample.gamma, this.baseline.gamma));
    const hard = deviation > this.config.hardAngle || sample.shake > this.config.shake || (this.kind === 'stillness' && !this.upright(sample));
    const soft = deviation > this.config.softAngle;
    if (hard || (soft && this.kind === 'stillness')) {
      this.bad += dt;
      // No credit for a moving interval, even before the grace period elapses.
      if (this.bad >= this.config.grace) { this.elapsed = 0; return this.status = 'failed'; }
      return this.status = 'paused';
    }
    this.bad = 0;
    if (soft) return this.status = 'paused';
    this.elapsed += dt;
    return this.status = this.elapsed >= this.config.duration ? 'complete' : 'steady';
  }
}
