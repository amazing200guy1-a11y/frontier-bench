class TTLCache {
  constructor({ capacity, now = Date.now }) {
    this.capacity = capacity;
    this.now = now;
    this.map = new Map();
  }

  get(key) {
    const entry = this.map.get(key);
    if (!entry) return undefined;
    if (entry.expiresAt <= this.now()) {
      this.map.delete(key);
      return undefined;
    }
    this.map.delete(key);
    this.map.set(key, entry);
    return entry.value;
  }

  set(key, value, ttlMs) {
    if (this.map.size >= this.capacity) {
      this.map.delete(this.map.keys().next().value);
    }
    this.map.set(key, { value, expiresAt: this.now() + ttlMs });
  }

  get size() {
    return this.map.size;
  }
}

module.exports = { TTLCache };
