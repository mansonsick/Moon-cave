// Storage is optional: a blocked or damaged save must never block a story.
export function createStorage(storyId, fresh, validate) {
  const key = `adventure.${storyId}.state`;
  let memory = fresh();
  const read = (name) => { try { return localStorage.getItem(name); } catch { return null; } };
  const write = (name, value) => { try { localStorage.setItem(name, value); return true; } catch { return false; } };
  return {
    key,
    load() {
      try { memory = validate(JSON.parse(read(key))) || fresh(); } catch { memory = fresh(); }
      return memory;
    },
    save(state) { memory = state; return write(key, JSON.stringify(state)); },
    reset() { memory = fresh(); this.save(memory); return memory; },
    sound() { return read('adventure.settings.sound') !== 'false'; },
    setSound(value) { write('adventure.settings.sound', String(Boolean(value))); },
  };
}
