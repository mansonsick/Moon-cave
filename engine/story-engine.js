import { createStorage } from './storage.js';
import { AudioManager } from './audio-manager.js?v=story02-audio-1';
import { findObjects, stabilityChallenge, tiltDodge } from './challenges.js';
import { bindDrag, place, keyGraphic } from './interactions.js';

export class StoryEngine {
  constructor({ root, config, textManifest, baseURL, model }) {
    Object.assign(this, { root, config, textManifest, baseURL, model });
    this.storage = createStorage(config.id, model.freshState, model.validateState);
    this.state = this.storage.load(); this.cleanups = []; this.started = false;
    this.audio = new AudioManager(config.audio, baseURL, this.storage.sound());
    this.text = this.text.bind(this); this.button = this.button.bind(this);
    this.visibility = () => this.audio.setHidden(document.hidden);
    document.addEventListener('visibilitychange', this.visibility);
    this.resumeAudio = () => {
      if (this.started && this.audio.enabled && this.audio.context && this.audio.context.state !== 'running') void this.audio.unlock();
    };
    this.root.addEventListener('pointerdown', this.resumeAudio, true);
    // Even a resumed save waits for an explicit Start before audio or sensors can activate.
    this.renderGate();
  }
  text(id) {
    const label = this.textManifest.labels[id];
    if (!label) throw new Error(`Missing rendered label: ${id}`);
    const span = document.createElement('span'); span.className = 'zhuyin';
    span.setAttribute('role', 'img'); span.setAttribute('aria-label', label.text);
    for (const part of label.parts) {
      const img = document.createElement('img'); img.src = new URL(`assets/text/${part.src}`, this.baseURL);
      img.alt = ''; img.width = part.width; img.height = part.height;
      img.style.width = `${part.width / this.textManifest.fontSize}em`; img.style.height = `${part.height / this.textManifest.fontSize}em`;
      img.draggable = false; span.append(img);
    }
    return span;
  }
  button(label, action, className = '') {
    const button = document.createElement('button'); button.type = 'button'; button.className = `button ${className}`;
    button.append(this.text(label)); button.addEventListener('click', action); return button;
  }
  save() { this.storage.save(this.state); }
  clearScene(keepSfx = []) { this.cleanups.splice(0).forEach(cleanup => cleanup()); this.audio.stopSfx(keepSfx); }
  go(scene) {
    const target = this.config.scenes[scene];
    this.state.scene = scene; this.state.ending = target.ending || null; this.save(); this.render(target.keepSfx || []);
    if (target.entrySfx) this.audio.playSfx(target.entrySfx);
  }
  header() {
    const toolbar = document.createElement('nav'); toolbar.className = 'toolbar'; toolbar.setAttribute('aria-label', '閱讀工具');
    const home = document.createElement('a'); home.href = '../../'; home.className = 'button home'; home.append(this.text('home'));
    const small = document.createElement('button'), large = document.createElement('button');
    small.type = large.type = 'button'; small.className = large.className = 'button font-control'; small.textContent = 'A−'; large.textContent = 'A+';
    small.setAttribute('aria-label', '縮小文字'); large.setAttribute('aria-label', '放大文字');
    const scale = delta => { this.state.textScale = Math.max(.85, Math.min(1.4, +(this.state.textScale + delta).toFixed(2))); this.applyScale(); this.save(); };
    small.addEventListener('click', () => scale(-.1)); large.addEventListener('click', () => scale(.1));
    const sound = document.createElement('button'); sound.type = 'button'; sound.className = 'button sound'; sound.dataset.action = 'sound';
    const soundUI = () => { sound.textContent = this.audio.enabled ? '🔊' : '🔇'; sound.setAttribute('aria-label', this.config.labels[this.audio.enabled ? 'sound-on' : 'sound-off']); sound.setAttribute('aria-pressed', String(this.audio.enabled)); };
    soundUI(); sound.addEventListener('click', () => {
      this.audio.setEnabled(!this.audio.enabled); this.storage.setSound(this.audio.enabled); soundUI();
      if (this.started && this.audio.enabled) this.audio.unlock();
    });
    toolbar.append(home, small, large, sound);
    if (this.started) { const reset = this.button('replay', () => this.confirmReplay(), 'reset'); reset.dataset.action = 'replay'; toolbar.append(reset); }
    return toolbar;
  }
  applyScale() { this.root.style.setProperty('--text-scale', this.state.textScale); }
  renderGate() {
    this.clearScene(); this.root.replaceChildren(this.header()); this.applyScale();
    const cover = this.config.scenes.cover, wrapper = document.createElement('main'); wrapper.className = 'story-card';
    const h1 = document.createElement('h1'); h1.append(this.text(this.model.revealed(this.state) ? this.config.title : this.config.neutralTitle));
    const stage = this.stage(cover), p = document.createElement('p'); p.className = 'story-line'; p.append(this.text(cover.text));
    const start = this.button('start-adventure', () => {
      this.started = true; if (this.audio.enabled) this.audio.unlock();
      if (this.state.scene === 'cover') this.go(cover.next); else this.render();
    }, 'primary'); start.dataset.action = 'start-adventure';
    wrapper.append(h1, stage, p, start); this.root.append(wrapper); this.updateTitle();
  }
  updateTitle() { document.title = this.config.labels[this.model.revealed(this.state) ? this.config.title : this.config.neutralTitle]; }
  stage(scene) {
    const stage = document.createElement('div'); stage.className = 'stage';
    const art = document.createElement('img'); art.src = new URL(`assets/images/${scene.image}`, this.baseURL);
    art.className = 'scene-art'; art.alt = this.config.labels[scene.title]; art.width = 1672; art.height = 941; art.draggable = false;
    stage.append(art); return stage;
  }
  owned(target) { return (target.kind === 'clue' ? this.state.clues : this.state.inventory).includes(target.id); }
  renderInventory() {
    const inventory = document.createElement('aside'); inventory.className = 'inventory'; inventory.dataset.testid = 'inventory';
    if (!this.state.inventory.length) { inventory.hidden = true; return inventory; }
    const label = document.createElement('span'); label.append(this.text('inventory')); inventory.append(label);
    for (const id of this.state.inventory) {
      const item = this.config.items[id], el = document.createElement('button'); el.type = 'button'; el.className = 'inventory-item'; el.dataset.item = id;
      el.setAttribute('aria-label', this.config.labels[item.label]);
      const icon = document.createElement('span'); icon.className = 'item-icon'; icon.textContent = item.icon; icon.setAttribute('aria-hidden', 'true');
      el.append(icon, this.text(item.label)); inventory.append(el);
    }
    return inventory;
  }
  render(keepSfx = []) {
    this.clearScene(keepSfx); this.updateTitle(); this.applyScale();
    const id = this.state.scene, scene = this.config.scenes[id];
    this.root.dataset.scene = id; this.root.replaceChildren(this.header());
    const main = document.createElement('main'); main.className = 'story-card';
    const title = document.createElement('h1'); title.tabIndex = -1; title.append(this.text(scene.title));
    const stage = this.stage(scene), body = document.createElement('section'); body.className = 'reading';
    const p = document.createElement('p'); p.className = 'story-line'; p.append(this.text(scene.text)); body.append(p);
    const inventory = this.renderInventory();
    const panel = document.createElement('section'); panel.className = 'challenge'; panel.dataset.testid = 'challenge';
    main.append(title, stage, body, inventory, panel); this.root.append(main);
    this.audio.setAmbience(scene.ambience, scene.ambienceScale ?? 1);
    const reward = () => this.reward(panel, scene.reward, scene.next);
    const done = () => { if (!this.state.completed.includes(id)) this.state.completed.push(id); this.save(); this.render(); this.audio.playSfx('success'); };
    const isDragComplete = scene.type === 'drag' && this.state.placed.includes('bell');
    for (const action of scene.actions || []) {
      if (isDragComplete) break;
      const target = action.hidden ? document.createElement('button') : this.button(action.label, () => this.go(action.to));
      target.type = 'button'; target.classList.add('hotspot', action.hidden ? 'hidden-hotspot' : 'choice-hotspot');
      target.dataset.action = action.id; place(target, action.box);
      if (action.hidden) { target.setAttribute('aria-label', action.label); target.addEventListener('click', () => this.go(action.to)); }
      stage.append(target);
    }
    if (scene.type === 'findObjects') {
      (scene.prompt || []).forEach(label => { const p = document.createElement('p'); p.append(this.text(label)); panel.append(p); });
      const complete = scene.targets.every(target => this.owned(target));
      const counter = document.createElement('div'); counter.className = 'find-counter'; counter.setAttribute('role', 'status');
      counter.textContent = `${scene.targets.filter(target => this.owned(target)).length} / ${scene.targets.length}`; panel.append(counter);
      this.cleanups.push(findObjects({ stage, targets: scene.targets.map(target => ({ ...target, graphic: target.graphic === 'key' ? keyGraphic : null })),
        found: target => this.owned(target), onFind: target => {
          if (this.owned(target)) return;
          (target.kind === 'clue' ? this.state.clues : this.state.inventory).push(target.id); this.save();
          this.render(); this.audio.playSfx(target.kind === 'clue' && this.model.revealed(this.state) ? 'success' : 'found-item');
          if (target.feedback && !this.model.revealed(this.state)) { const feedback = document.createElement('p'); feedback.className = 'find-feedback'; feedback.setAttribute('role', 'status'); feedback.append(this.text(target.feedback)); this.root.querySelector('.challenge').append(feedback); }
        } }));
      if (complete) reward();
      else {
        if (scene.hints) this.keyHints(stage, panel);
        if (scene.optional) { const leave = this.button('leave-shrine', () => this.go(scene.next)); leave.dataset.action = 'leave-shrine'; panel.append(leave); }
      }
    } else if (['stillnessSensor', 'balanceSensor', 'tiltDodge'].includes(scene.type)) {
      if (this.state.completed.includes(id)) reward();
      else if (scene.type === 'tiltDodge') this.cleanups.push(tiltDodge({ panel, text: this.text, button: this.button, audio: this.audio, onComplete: done }));
      else {
        const kind = scene.type === 'stillnessSensor' ? 'stillness' : 'balance';
        this.cleanups.push(stabilityChallenge({ panel, kind, config: this.config.challenges[kind], text: this.text, button: this.button, audio: this.audio, onComplete: done }));
      }
    } else if (scene.type === 'drag') {
      const hook = document.createElement('div'); hook.className = 'bell-hook'; hook.dataset.testid = 'bell-hook'; place(hook, scene.dropzone); stage.append(hook);
      if (isDragComplete) { hook.classList.add('placed'); hook.textContent = '🔔'; reward(); }
      else if (this.state.inventory.includes('bell')) {
        const bell = inventory.querySelector('[data-item="bell"]'); bell.classList.add('draggable');
        this.cleanups.push(bindDrag(bell, hook, () => {
          if (this.state.placed.includes('bell')) return;
          this.state.placed.push('bell'); this.save(); this.render();
          this.audio.playSfx('drag-lock'); this.audio.playSfx('secret-bell');
        }));
      }
    } else if (scene.type === 'ending') {
      for (const label of [scene.extra, scene.last].filter(Boolean)) { const p = document.createElement('p'); p.append(this.text(label)); body.append(p); }
      if (scene.next) { const next = this.button('continue', () => this.go(scene.next), 'primary'); next.dataset.action = 'continue'; panel.append(next); }
      else panel.append(this.button('replay', () => this.confirmReplay(), 'primary'));
    } else if (scene.next) { const next = this.button(scene.nextLabel || 'continue', () => this.go(scene.next), 'primary'); next.dataset.action = 'continue'; panel.append(next); }
    // Keep reading position predictable while preserving the browser's two-finger zoom.
    title.focus({ preventScroll: true }); window.scrollTo({ top: 0, behavior: 'instant' });
  }
  reward(panel, label, next) {
    const reward = document.createElement('section'); reward.className = 'reward'; reward.dataset.testid = 'reward'; reward.setAttribute('role', 'status');
    const p = document.createElement('p'); p.append(this.text(label));
    const proceed = this.button('continue', () => this.go(next), 'primary'); proceed.dataset.action = 'continue';
    reward.append(p, proceed); panel.append(reward);
    // No timer: the child owns the pace. Completion is derived from the saved state.
  }
  keyHints(stage, panel) {
    let elapsed = 0, level = 0, last = performance.now();
    const area = document.createElement('div'); area.className = 'hint-area'; panel.append(area);
    const reveal = () => {
      area.replaceChildren(this.text('key-hint-two'));
      stage.querySelector('[data-target="key"]').classList.add('hinted');
      // The optional explicit pick-up action appears only after both hint delays.
      const take = this.button('take-key', () => stage.querySelector('[data-target="key"]').click()); take.dataset.action = 'take-key'; area.append(take);
    };
    const timer = setInterval(() => {
      const now = performance.now(); if (!document.hidden) elapsed += Math.min(now - last, 300); last = now;
      if (elapsed >= 15000 && level === 0) { level = 1; const hint = this.button('need-hint', () => { area.replaceChildren(this.text('key-hint-one')); }); hint.dataset.action = 'hint-one'; area.append(hint); }
      if (elapsed >= 30000 && level === 1) { level = 2; const hint = this.button('more-hint', reveal); hint.dataset.action = 'hint-two'; area.append(hint); }
    }, 250);
    this.cleanups.push(() => clearInterval(timer));
  }
  confirmReplay() {
    const dialog = document.createElement('dialog'); dialog.className = 'replay-dialog';
    const p = document.createElement('p'); p.append(this.text('replay-confirm'));
    const yes = this.button('yes-replay', () => { dialog.close(); dialog.remove(); this.clearScene(); this.state = this.storage.reset(); this.audio.stopAmbience(); this.started = false; this.renderGate(); }); yes.dataset.action = 'confirm-replay';
    const cancel = this.button('cancel', () => { dialog.close(); dialog.remove(); });
    dialog.append(p, yes, cancel); this.root.append(dialog); dialog.showModal();
    dialog.addEventListener('close', () => dialog.remove(), { once: true });
  }
  dispose() { this.clearScene(); this.audio.dispose(); document.removeEventListener('visibilitychange', this.visibility); this.root.removeEventListener('pointerdown', this.resumeAudio, true); }
}
