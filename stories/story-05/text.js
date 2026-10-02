export async function loadText() {
  const response = await fetch(new URL('./assets/text/text.json', import.meta.url));
  if (!response.ok) throw new Error('Missing Story 05 text');
  const manifest = await response.json();
  return (id, className = '') => {
    const entry = manifest.labels[id];
    if (!entry) throw new Error('Missing text: ' + id);
    const span = document.createElement('span');
    span.className = 'bpmf ' + className; span.setAttribute('role','img'); span.setAttribute('aria-label', entry.text);
    for (const part of entry.parts) {
      const img = document.createElement('img'); img.src = new URL('./assets/text/' + part.src, import.meta.url);
      img.alt = ''; img.width = part.width; img.height = part.height; img.draggable = false;
      img.style.width = (part.width / part.height * 1.12) + 'em'; span.append(img);
    }
    return span;
  };
}
