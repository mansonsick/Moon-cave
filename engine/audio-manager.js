// Missing/undelivered audio entries are inert, with no HTTP requests or substitute sounds.
export class AudioManager {
  constructor(manifest, baseURL, enabled = true) {
    this.manifest = manifest; this.baseURL = baseURL; this.enabled = enabled;
    this.context = null; this.unlocked = false; this.hidden = false;
    this.desired = null; this.current = null; this.revision = 0;
    this.cache = new Map(); this.voices = new Set(); this.lastSfx = new Map();
    this.pendingSfx = new Set(); this.ambienceScale = 1;
  }
  async unlock() {
    if (!this.enabled) return false;
    try {
      const Context = window.AudioContext || window.webkitAudioContext;
      if (!Context) return false;
      this.context ||= new Context();
      // Called immediately in the click handler, before fetching/decoding anything.
      await this.context.resume();
      this.unlocked = this.context.state === 'running';
      if (this.unlocked && this.enabled && !this.hidden) {
        void this.setAmbience(this.desired, this.ambienceScale);
        // Warm short cues only after the first gesture; never play them while preloading.
        for (const [id, entry] of Object.entries(this.manifest)) if (entry.category === 'sfx') void this.buffer(id);
      }
      return this.unlocked;
    } catch { return false; }
  }
  async buffer(id) {
    const entry = this.manifest[id];
    if (!entry?.available || !entry.src || !this.context) return null;
    if (!this.cache.has(id)) {
      this.cache.set(id, (async () => {
        const controller = new AbortController();
        const timer = setTimeout(() => controller.abort(), 6000);
        try {
          const response = await fetch(new URL(entry.src, this.baseURL), { signal: controller.signal });
          if (!response.ok) return null;
          return await this.context.decodeAudioData(await response.arrayBuffer());
        } catch { return null; } finally { clearTimeout(timer); }
      })());
    }
    return this.cache.get(id);
  }
  stopVoice(voice) {
    try { voice.source.stop(); } catch { /* Already ended. */ }
    voice.source.disconnect(); voice.gain.disconnect(); this.voices.delete(voice);
  }
  stopSfx(keep = []) {
    for (const pending of this.pendingSfx) if (!keep.includes(pending.id)) pending.cancelled = true;
    for (const voice of [...this.voices]) if (!keep.includes(voice.id)) this.stopVoice(voice);
    this.refreshAmbience();
  }
  level(id, fallback) {
    const volume = this.manifest[id]?.volume;
    return typeof volume === 'number' && Number.isFinite(volume) ? Math.max(0, Math.min(1, volume)) : fallback;
  }
  ambienceLevel() {
    const duck = [...this.voices].some(voice => voice.id === 'secret-bell') ? .28 : 1;
    return this.level(this.current?.id || this.desired, .28) * this.ambienceScale * duck;
  }
  refreshAmbience() {
    if (!this.current || this.current.id !== this.desired || !this.context || !this.enabled || this.hidden) return;
    this.current.gain.gain.cancelScheduledValues(this.context.currentTime);
    this.current.gain.gain.setTargetAtTime(this.ambienceLevel(), this.context.currentTime, .15);
  }
  stopAmbience() {
    this.revision++;
    if (this.current) { this.stopVoice(this.current); this.current = null; }
  }
  async setAmbience(id, scale = 1) {
    this.desired = id || null;
    this.ambienceScale = Number.isFinite(scale) ? Math.max(0, Math.min(1, scale)) : 1;
    const revision = ++this.revision;
    if (!this.enabled || !this.unlocked || this.hidden) { this.stopAmbience(); return false; }
    if (this.current?.id === id) {
      // A rapid A -> B -> A selection can cancel a fade already in progress.
      this.refreshAmbience();
      return true;
    }
    const old = this.current;
    if (old) {
      old.gain.gain.cancelScheduledValues(this.context.currentTime);
      old.gain.gain.setTargetAtTime(0, this.context.currentTime, .15);
      await new Promise(resolve => setTimeout(resolve, 500));
      if (revision !== this.revision) return false;
      if (this.current === old) { this.stopVoice(old); this.current = null; }
    }
    if (!id) return true;
    const buffer = await this.buffer(id);
    if (!buffer || revision !== this.revision || this.hidden || !this.enabled) return false;
    const source = this.context.createBufferSource(), gain = this.context.createGain();
    source.buffer = buffer; source.loop = true; source.connect(gain); gain.connect(this.context.destination);
    gain.gain.setValueAtTime(0, this.context.currentTime);
    gain.gain.linearRampToValueAtTime(this.ambienceLevel(), this.context.currentTime + .6);
    try { source.start(); } catch { source.disconnect(); gain.disconnect(); return false; }
    this.current = { source, gain, id }; return true;
  }
  async playSfx(id) {
    if (!this.enabled || !this.unlocked || this.hidden || this.voices.size >= 3) return false;
    const now = performance.now();
    if (now - (this.lastSfx.get(id) ?? -Infinity) < 250) return false;
    this.lastSfx.set(id, now);
    const pending = { id, cancelled: false }; this.pendingSfx.add(pending);
    const buffer = await this.buffer(id); this.pendingSfx.delete(pending);
    if (!buffer || pending.cancelled || !this.enabled || this.hidden || this.voices.size >= 3) return false;
    const source = this.context.createBufferSource(), gain = this.context.createGain();
    source.buffer = buffer; gain.gain.value = this.level(id, id === 'secret-bell' ? .7 : .55);
    source.connect(gain); gain.connect(this.context.destination);
    const voice = { source, gain, id }; this.voices.add(voice);
    this.refreshAmbience();
    source.onended = () => {
      source.disconnect(); gain.disconnect(); this.voices.delete(voice);
      this.refreshAmbience();
    };
    try { source.start(); return true; } catch { this.stopVoice(voice); return false; }
  }
  setEnabled(enabled) {
    this.enabled = Boolean(enabled);
    if (!this.enabled) { this.stopAmbience(); this.stopSfx(); }
  }
  setHidden(hidden) {
    this.hidden = hidden;
    if (hidden) { this.stopAmbience(); this.stopSfx(); }
    else if (this.unlocked && this.enabled && this.context?.state === 'running') void this.setAmbience(this.desired, this.ambienceScale);
  }
  dispose() { this.stopAmbience(); this.stopSfx(); void this.context?.close().catch(() => {}); }
}
