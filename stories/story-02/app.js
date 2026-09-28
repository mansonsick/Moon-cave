import { StoryEngine } from '../../engine/story-engine.js?v=camera-1';
import * as model from './state.js';

const root = document.getElementById('story');
const baseURL = new URL('./', import.meta.url);
async function start() {
  const [config, textManifest] = await Promise.all(['story.json', 'assets/text/text.json'].map(async path => {
    const response = await fetch(new URL(path, baseURL), { cache: 'no-cache' });
    if (!response.ok) throw new Error(`Unable to load ${path}`);
    return response.json();
  }));
  const engine = new StoryEngine({ root, config, textManifest, baseURL, model });
  window.addEventListener('pagehide', () => engine.audio.setHidden(true));
  window.addEventListener('pageshow', () => engine.audio.setHidden(false));
}
start().catch(error => {
  console.error(error);
  const message = document.createElement('p'); message.className = 'load-error'; message.setAttribute('aria-label', '故事暫時打不開，請重新整理再試一次。');
  for (let i = 0; i < 3; i++) { const img = document.createElement('img'); img.src = `./assets/text/load-error-${i}.png`; img.alt = ''; message.append(img); }
  const reload = document.createElement('button'); reload.className = 'button'; reload.textContent = '↻'; reload.setAttribute('aria-label', '重新整理'); reload.onclick = () => location.reload(); root.replaceChildren(message, reload);
});
