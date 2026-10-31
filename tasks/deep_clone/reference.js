function cloneConfig(value, seen = new WeakMap()) {
  if (value === null || (typeof value !== 'object' && typeof value !== 'function')) return value;
  if (typeof value === 'function') return value;
  if (seen.has(value)) return seen.get(value);
  if (value instanceof Date) { const d = new Date(value.getTime()); seen.set(value, d); return d; }
  if (value instanceof RegExp) { const r = new RegExp(value.source, value.flags); seen.set(value, r); return r; }
  const out = Array.isArray(value) ? [] : Object.create(Object.getPrototypeOf(value));
  seen.set(value, out);
  for (const key of Reflect.ownKeys(value)) {
    const desc = Object.getOwnPropertyDescriptor(value, key);
    if (desc && 'value' in desc) desc.value = cloneConfig(desc.value, seen);
    Object.defineProperty(out, key, desc);
  }
  return out;
}

module.exports = { cloneConfig };
