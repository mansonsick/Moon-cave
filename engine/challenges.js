import { MotionSource, StabilityTracker, screenAngle } from './sensors.js';
import { place } from './interactions.js';

// All controllers return cleanup; leaving a scene never leaves a timer or sensor behind.
export function findObjects({ stage, targets, found, onFind }) {
  for (const target of targets) {
    const hit = document.createElement('button');
    hit.type = 'button'; hit.className = 'hotspot find-hit'; hit.dataset.target = target.id;
    hit.setAttribute('aria-label', target.label); place(hit, target.box);
    if (target.graphic) hit.innerHTML = target.graphic;
    const mark = () => { hit.disabled = true; hit.classList.add('found'); hit.setAttribute('aria-label', `${target.label} ✓`); hit.innerHTML = '<span aria-hidden="true">✓</span>'; };
    if (found(target)) mark();
    hit.addEventListener('click', () => { if (found(target)) return; mark(); onFind(target); });
    stage.append(hit);
  }
  return () => {};
}

export function stabilityChallenge({ panel, kind, config = {}, text, button, audio, onComplete }) {
  const source = new MotionSource(), tracker = new StabilityTracker(kind, config);
  let alive = true, running = false, fallback = false, elapsed = 0, absent = 0, last = 0, frame = 0, revision = 0;
  const status = document.createElement('p'); status.className = 'challenge-status'; status.setAttribute('role', 'status');
  const clock = document.createElement('strong'); clock.className = 'countdown'; clock.textContent = '8';
  const bar = document.createElement('progress'); bar.max = config.duration || 8000; bar.value = 0;
  const controls = document.createElement('div'); controls.className = 'actions';
  const show = id => { if (status.dataset.label !== id) { status.dataset.label = id; status.replaceChildren(text(id)); } };
  const normal = button('countdown', () => start(true)); normal.dataset.action = 'fallback';
  const begin = button('start', () => start(false)); begin.dataset.action = 'challenge-start';
  controls.append(begin, normal); panel.append(status, clock, bar, controls);
  show(kind === 'stillness' ? 'still-instruction' : 'balance-instruction');

  function useFallback() { source.stop(); fallback = true; elapsed = 0; absent = 0; tracker.reset(); show('countdown-mode'); }
  async function start(ordinary) {
    const ticket = ++revision; running = false; source.stop(); tracker.reset(); elapsed = 0; absent = 0;
    begin.disabled = true; normal.disabled = false; fallback = ordinary; bar.value = 0; clock.textContent = '8';
    if (!ordinary) {
      show('permission');
      const supported = await source.start();
      if (!alive || ticket !== revision) return;
      if (!supported) useFallback(); else show('calibrating');
    } else useFallback();
    running = true; last = performance.now();
  }
  function tick(now) {
    if (!alive) return;
    const dt = Math.min(Math.max(now - last, 0), 100); last = now;
    if (running && !document.hidden) {
      if (fallback) { elapsed += dt; show('countdown-mode'); }
      else {
        const sample = source.read(now);
        absent = sample ? 0 : absent + dt;
        if (absent >= 2200) useFallback();
        else {
          const state = tracker.step(sample, dt); elapsed = tracker.elapsed;
          show({ waiting: 'sensor-wait', upright: 'upright', calibrating: 'calibrating', steady: 'steady', paused: 'paused', failed: 'retry-message', complete: 'steady' }[state]);
          if (state === 'failed') {
            running = false; source.stop(); begin.disabled = false; begin.replaceChildren(text('retry'));
            audio?.playSfx('fail-soft');
          }
        }
      }
      bar.value = elapsed; clock.textContent = String(Math.max(0, Math.ceil((bar.max - elapsed) / 1000)));
      if (elapsed >= bar.max) { running = false; source.stop(); onComplete(); return; }
    }
    frame = requestAnimationFrame(tick);
  }
  const visibility = () => {
    if (!document.hidden || !running) return;
    // Returning requires a fresh user gesture and calibration; background time never counts.
    revision++; running = false; source.stop(); tracker.reset(); elapsed = 0; bar.value = 0; clock.textContent = '8';
    begin.disabled = false; begin.replaceChildren(text('retry')); show('background-paused');
  };
  document.addEventListener('visibilitychange', visibility); frame = requestAnimationFrame(tick);
  return () => { alive = false; revision++; source.stop(); cancelAnimationFrame(frame); document.removeEventListener('visibilitychange', visibility); };
}

const obstacles = ['🎋', '🪨', '🪵', '🎋', '🪵'];
export function tiltDodge({ panel, text, button, audio, onComplete }) {
  const source = new MotionSource();
  let alive = true, running = false, lane = 1, passed = 0, y = -12, pause = 0, last = performance.now(), frame = 0;
  let useTilt = false, baseline = null, candidate = null, calibration = 0, missing = 0, revision = 0;
  const lanes = [1, 0, 2, 1, 0];
  const status = document.createElement('p'); status.className = 'challenge-status'; status.setAttribute('role', 'status');
  let label;
  const show = id => { if (label !== id) { label = id; status.replaceChildren(text(id)); } };
  show('dodge-instruction');
  const field = document.createElement('div'); field.className = 'dodge-field'; field.dataset.mode = 'buttons';
  field.innerHTML = '<div class="lane-mark left"></div><div class="lane-mark right"></div><div class="obstacle" aria-hidden="true"></div><div class="runner" aria-label="阿通與小松鼠"><svg viewBox="0 0 80 100" aria-hidden="true"><path fill="#c4c8c7" d="M21 52h37l7 26-18 5-7-15-7 15-19-5z"/><path fill="#78623e" d="m22 78 14 1-2 19H20zm23 1 14-1 3 20H47z"/><circle fill="#f1b97b" cx="40" cy="31" r="22"/><path fill="#2b2330" d="M18 29C9-6 72-10 63 31L51 15 39 24 28 17z"/><circle cx="32" cy="31" r="2"/><circle cx="48" cy="31" r="2"/><path stroke="#98523e" fill="none" d="M33 42q7 6 14 0"/></svg><span class="runner-friend" aria-hidden="true">🐿️</span></div>';
  const obstacle = field.querySelector('.obstacle'), runner = field.querySelector('.runner');
  const score = document.createElement('p'); score.className = 'dodge-score'; score.textContent = '0 / 5';
  const controls = document.createElement('div'); controls.className = 'actions dodge-controls';
  function move(next) { lane = Math.max(0, Math.min(2, next)); runner.style.left = `${(lane + .5) / 3 * 100}%`; field.dataset.lane = lane; }
  function buttons() { revision++; useTilt = false; baseline = null; source.stop(); field.dataset.mode = 'buttons'; show('button-mode'); running = true; last = performance.now(); }
  const left = button('left', () => move(lane - 1)), right = button('right', () => move(lane + 1));
  left.dataset.action = 'left'; right.dataset.action = 'right';
  const start = button('start', () => { start.hidden = true; buttons(); }); start.dataset.action = 'challenge-start';
  const tilt = button('tilt-mode', async () => {
    start.hidden = true; const ticket = ++revision; running = false; show('permission');
    const ok = await source.start(); if (!alive || ticket !== revision) return;
    if (!ok) { buttons(); return; }
    baseline = null; candidate = null; calibration = 0; missing = 0; useTilt = true; field.dataset.mode = 'tilt';
    show('calibrating'); running = true; last = performance.now();
  }); tilt.dataset.action = 'tilt';
  const fallback = button('button-mode', buttons); fallback.dataset.action = 'buttons';
  controls.append(left, start, right, tilt, fallback); panel.append(status, field, score, controls); move(1);
  const key = event => { if (event.key === 'ArrowLeft' || event.key === 'ArrowRight') { event.preventDefault(); move(lane + (event.key === 'ArrowLeft' ? -1 : 1)); } };
  document.addEventListener('keydown', key);
  function tick(now) {
    if (!alive) return;
    const dt = Math.min(Math.max(now - last, 0), 60); last = now;
    let canAdvance = true;
    if (running && !document.hidden) {
      if (useTilt) {
        const s = source.read(now); missing = s ? 0 : missing + dt;
        if (missing > 2200) buttons();
        else if (!s) { canAdvance = false; show('sensor-wait'); }
        else {
          // Portrait gamma, landscape beta; invalidate calibration when rotating the screen.
          const angle = Math.abs(screenAngle() % 180) === 90 ? s.beta : s.gamma;
          if (baseline && baseline.screen !== s.screen) { baseline = null; candidate = null; calibration = 0; }
          if (!baseline) {
            canAdvance = false; show('calibrating');
            if (!candidate || Math.abs(angle - candidate.angle) > 5) { candidate = { angle, screen: s.screen }; calibration = 0; }
            else calibration += dt;
            if (calibration >= 2000) baseline = candidate;
          } else {
            const direction = s.screen === 180 || s.screen === 270 || s.screen === -90 ? -1 : 1;
            const offset = (angle - baseline.angle) * direction;
            if (Math.abs(offset) > 12) move(offset > 0 ? 2 : 0);
            // Returning to centre allows either the middle lane or a subsequent button press.
            else if (field.dataset.tiltSide !== 'center') move(1);
            field.dataset.tiltSide = Math.abs(offset) > 12 ? 'side' : 'center';
            show('tilt-instruction');
          }
        }
      }
      if (canAdvance) {
        if (pause > 0) pause -= dt;
        else {
          y += dt * .033;
          if (y >= 71 && y <= 91 && lane === lanes[passed]) {
            y = 32; pause = 650; field.classList.add('bumped'); show('collision'); audio?.playSfx('fail-soft');
          } else if (y > 108) {
            passed++; score.textContent = `${passed} / 5`; y = -12;
            if (passed === 5) { running = false; source.stop(); onComplete(); return; }
          }
        }
        if (pause <= 0) field.classList.remove('bumped');
      }
    }
    obstacle.textContent = obstacles[passed] || ''; obstacle.style.left = `${(lanes[passed] + .5) / 3 * 100}%`; obstacle.style.top = `${y}%`;
    field.dataset.obstacle = lanes[passed]; field.dataset.passed = passed; field.dataset.position = y.toFixed(1);
    frame = requestAnimationFrame(tick);
  }
  const visibility = () => {
    if (document.hidden && running) { running = false; useTilt = false; revision++; source.stop(); start.hidden = false; start.replaceChildren(text('resume')); show('background-paused'); }
  };
  document.addEventListener('visibilitychange', visibility); frame = requestAnimationFrame(tick);
  return () => { alive = false; revision++; source.stop(); cancelAnimationFrame(frame); document.removeEventListener('keydown', key); document.removeEventListener('visibilitychange', visibility); };
}
