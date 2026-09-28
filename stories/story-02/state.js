export const freshState = () => ({ version: 1, scene: 'cover', clues: [], inventory: [], completed: [], placed: [], ending: null, textScale: 1 });
const allowed = (values, list) => Array.isArray(values) ? [...new Set(values.filter(value => list.includes(value)))] : [];
export const revealed = state => ['prints', 'fur', 'tail'].every(id => state.clues.includes(id));
export function validateState(raw) {
  const state = freshState();
  if (!raw || raw.version !== 1) return state;
  state.clues = allowed(raw.clues, ['prints', 'fur', 'tail']);
  state.inventory = allowed(raw.inventory, ['key', 'bell']);
  state.completed = allowed(raw.completed, ['hide', 'bamboo', 'bridge']);
  state.placed = allowed(raw.placed, ['bell']);
  state.textScale = typeof raw.textScale === 'number' && Number.isFinite(raw.textScale) ? Math.max(.85, Math.min(1.4, raw.textScale)) : 1;
  const order = ['cover', 'path', 'house', 'welcome', 'clues', 'key', 'hide', 'bamboo', 'fork', 'shrine', 'bridge', 'temple', 'ordinary', 'secret', 'secret-after'];
  state.scene = order.includes(raw.scene) ? raw.scene : 'cover';
  // Repair corrupt/incompatible progress at the nearest playable point, never skip a requirement.
  if (!revealed(state)) { state.inventory = []; state.completed = []; state.placed = []; if (order.indexOf(state.scene) > 4) state.scene = 'clues'; }
  if (!state.inventory.includes('key')) { state.completed = []; state.inventory = state.inventory.filter(id => id !== 'bell'); state.placed = []; if (order.indexOf(state.scene) > 5) state.scene = 'key'; }
  if (!state.completed.includes('hide')) { state.completed = []; state.inventory = state.inventory.filter(id => id !== 'bell'); state.placed = []; if (order.indexOf(state.scene) > 6) state.scene = 'hide'; }
  if (!state.completed.includes('bamboo')) { state.completed = state.completed.filter(id => id !== 'bridge'); state.inventory = state.inventory.filter(id => id !== 'bell'); state.placed = []; if (order.indexOf(state.scene) > 7) state.scene = 'bamboo'; }
  if (!state.completed.includes('bridge')) { state.placed = []; if (order.indexOf(state.scene) > 10) state.scene = 'bridge'; }
  if (!state.inventory.includes('bell')) state.placed = [];
  if (['secret', 'secret-after'].includes(state.scene) && !state.placed.includes('bell')) state.scene = 'temple';
  state.ending = state.scene === 'ordinary' ? 'ordinary' : ['secret', 'secret-after'].includes(state.scene) ? 'secret' : null;
  return state;
}
