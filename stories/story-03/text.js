export async function loadText() {
  const response = await fetch(new URL('./assets/text/text.json', import.meta.url));
  if (!response.ok) throw new Error('Text assets unavailable');
  const manifest = await response.json();
  return function text(id, className = '') {
    const entry = manifest.labels[id];
    if (!entry) throw new Error(`Unknown text label: ${id}`);
    const span = document.createElement('span');
    span.className = `bpmf ${className}`;
    span.setAttribute('role','img'); span.setAttribute('aria-label', entry.text);
    for (const part of entry.parts) {
      const img = document.createElement('img'); img.src = new URL(`./assets/text/${part.src}`, import.meta.url);
      img.alt = ''; img.setAttribute('aria-hidden','true'); img.width=part.width; img.height=part.height;
      span.append(img);
    }
    return span;
  };
}
export function button(text, id, handler, action = id) {
  const node = document.createElement('button'); node.type='button'; node.append(text(id));
  node.dataset.action = action; node.addEventListener('click', handler); return node;
}
export async function readyImages(root = document) {
  await Promise.all([...root.querySelectorAll('img')].map(img => img.decode()));
}
