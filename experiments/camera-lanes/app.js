import { tiltDodge } from '../../engine/challenges.js?v=camera-1';
const base = new URL('../../stories/story-02/', import.meta.url);
const manifest = await (await fetch(new URL('assets/text/text.json', base), { cache: 'no-cache' })).json();
function text(id) {
  const label = manifest.labels[id], span = document.createElement('span'); span.className = 'zhuyin'; span.setAttribute('role', 'img'); span.setAttribute('aria-label', label.text);
  for (const part of label.parts) { const img = document.createElement('img'); img.src = new URL(`assets/text/${part.src}`, base); img.alt = ''; img.width = part.width; img.height = part.height; img.style.width = `${part.width / manifest.fontSize}em`; img.style.height = `${part.height / manifest.fontSize}em`; span.append(img); }
  return span;
}
function button(id, fn) { const b = document.createElement('button'); b.type = 'button'; b.className = 'button'; b.append(text(id)); b.onclick = fn; return b; }
const home = document.createElement('a'); home.className = 'button'; home.href = '../../stories/story-02/'; home.append(text('continue')); document.querySelector('#nav').append(home);
const panel = document.querySelector('#panel'); let cleanup;
function start() {
  cleanup?.(); panel.replaceChildren();
  cleanup = tiltDodge({ panel, text, button, cameraEnabled: true, onComplete: () => {
    cleanup(); const reward = document.createElement('div'); reward.className = 'reward'; reward.append(text('dodge-success'), button('retry', start)); panel.replaceChildren(reward);
  } });
}
start();
