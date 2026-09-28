// Missing/undelivered audio entries are inert, with no HTTP requests or substitute sounds.
export class AudioManager {
  constructor(manifest, baseURL, enabled = true) {
    this.manifest = manifest; this.baseURL = baseURL; this.enabled = enabled;
    this.context = null; this.unlocked = false; this.hidden = false;
    this.desired = null; this.current = null; this.revision = 0;
    this.cache = new Map(); this.voices = new Set(); this.lastSfx = new Map();
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
      if (this.unlocked && !this.hidden) void this.setAmbience(this.desired);
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
  stopSfx() { for (const voice of [...this.voices]) this.stopVoice(voice); }
  stopAmbience() {
    this.revision++;
    if (this.current) { this.stopVoice(this.current); this.current = null; }
  }
  async setAmbience(id) {
    this.desired = id || null;
    const revision = ++this.revision;
    if (!this.enabled || !this.unlocked || this.hidden || !id) { this.stopAmbience(); return false; }
    if (this.current?.id === id) {
      // A rapid A -> B -> A selection can cancel a fade already in progress.
      this.current.gain.gain.cancelScheduledValues(this.context.currentTime);
      this.current.gain.gain.setTargetAtTime(.28, this.context.currentTime, .15);
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
    const buffer = await this.buffer(id);
    if (!buffer || revision !== this.revision || this.hidden || !this.enabled) return false;
    const source = this.context.createBufferSource(), gain = this.context.createGain();
    source.buffer = buffer; source.loop = true; source.connect(gain); gain.connect(this.context.destination);
    gain.gain.setValueAtTime(0, this.context.currentTime);
    gain.gain.linearRampToValueAtTime(.28, this.context.currentTime + .6);
    try { source.start(); } catch { source.disconnect(); gain.disconnect(); return false; }
    this.current = { source, gain, id }; return true;
  }
  async playSfx(id) {
    if (!this.enabled || !this.unlocked || this.hidden || this.voices.size >= 3) return false;
    const now = performance.now();
    if (now - (this.lastSfx.get(id) ?? -Infinity) < 250) return false;
    this.lastSfx.set(id, now);
    const revision = this.revision, buffer = await this.buffer(id);
    if (!buffer || revision !== this.revision || !this.enabled || this.hidden || this.voices.size >= 3) return false;
    const source = this.context.createBufferSource(), gain = this.context.createGain();
    source.buffer = buffer; gain.gain.value = id === 'secret-bell' ? .7 : .55;
    source.connect(gain); gain.connect(this.context.destination);
    const voice = { source, gain }; this.voices.add(voice);
    const ambience = this.current;
    if (id === 'secret-bell' && ambience) ambience.gain.gain.setTargetAtTime(.08, this.context.currentTime, .1);
    source.onended = () => {
      source.disconnect(); gain.disconnect(); this.voices.delete(voice);
      if (id === 'secret-bell' && this.current === ambience && ambience && this.enabled && !this.hidden)
        ambience.gain.gain.setTargetAtTime(.28, this.context.currentTime, .3);
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
    else if (this.unlocked && this.enabled && this.context?.state === 'running') void this.setAmbience(this.desired);
  }
  dispose() { this.stopAmbience(); this.stopSfx(); void this.context?.close().catch(() => {}); }
}
