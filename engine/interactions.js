export function place(element, box) {
  Object.assign(element.style, { left: `${box[0]}%`, top: `${box[1]}%`, width: `${box[2]}%`, height: `${box[3]}%` });
}

export function bindDrag(source, target, onPlaced) {
  let ghost = null, pointer = null, placed = false;
  const clear = () => { ghost?.remove(); ghost = null; pointer = null; };
  const move = event => { if (ghost) { ghost.style.left = `${event.clientX}px`; ghost.style.top = `${event.clientY}px`; } };
  const down = event => {
    if (placed || !event.isPrimary || (event.pointerType === 'mouse' && event.button !== 0)) return;
    event.preventDefault(); pointer = event.pointerId;
    ghost = source.cloneNode(true); ghost.removeAttribute('id'); ghost.removeAttribute('aria-label');
    ghost.className = 'drag-ghost'; ghost.setAttribute('aria-hidden', 'true'); document.body.append(ghost);
    source.setPointerCapture?.(pointer); move(event);
  };
  const up = event => {
    if (event.pointerId !== pointer || !ghost) return;
    const rect = target.getBoundingClientRect();
    const hit = event.clientX >= rect.left && event.clientX <= rect.right && event.clientY >= rect.top && event.clientY <= rect.bottom;
    clear();
    if (hit && !placed) { placed = true; source.disabled = true; onPlaced(); }
    else source.animate?.([{ transform: 'translateX(-5px)' }, { transform: 'translateX(5px)' }, { transform: 'none' }], { duration: 220 });
  };
  const moving = event => { if (event.pointerId === pointer) move(event); };
  source.addEventListener('pointerdown', down); source.addEventListener('pointermove', moving);
  source.addEventListener('pointerup', up); source.addEventListener('pointercancel', clear);
  source.addEventListener('lostpointercapture', clear);
  return () => {
    clear(); source.removeEventListener('pointerdown', down); source.removeEventListener('pointermove', moving);
    source.removeEventListener('pointerup', up); source.removeEventListener('pointercancel', clear);
    source.removeEventListener('lostpointercapture', clear);
  };
}

// Small interactive objects are native UI graphics, separate from the supplied scene art.
// Keep the forgiving touch area while making the object itself blend into the drawer.
export const keyGraphic = `<svg viewBox="0 0 100 50" aria-hidden="true"><g transform="translate(26 13) scale(.48) rotate(-18 50 25)" fill="none" stroke="#78664b" stroke-width="7" stroke-linecap="round"><circle cx="22" cy="25" r="14" fill="#807052"/><path d="M36 25h51m-12 0v12m11-12v9"/><circle cx="22" cy="25" r="5" stroke="#504535" stroke-width="3"/></g></svg>`;
