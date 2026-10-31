const assert = require('assert');
const { TTLCache } = require('./solution');
let t = 0;
const mk = (capacity) => new TTLCache({ capacity, now: () => t });
try {
  { // updating an existing key at capacity must not evict anything else
    t = 0; const c = mk(2);
    c.set('a', 1, 1000); c.set('b', 2, 1000); c.set('b', 20, 1000);
    assert.strictEqual(c.get('a'), 1, 'updating existing key b evicted a');
    assert.strictEqual(c.get('b'), 20);
  }
  { // expired entries must not push out live ones
    t = 0; const c = mk(2);
    c.set('a', 1, 100); c.set('b', 2, 10000); c.get('a');
    t = 200;
    c.set('c', 3, 10000);
    assert.strictEqual(c.get('b'), 2, 'live entry evicted while an expired entry still held a slot');
    assert.strictEqual(c.get('c'), 3);
    assert.strictEqual(c.get('a'), undefined);
  }
  { // size counts only live entries
    t = 0; const c = mk(3);
    c.set('a', 1, 100); c.set('b', 2, 100); c.set('c', 3, 10000);
    t = 150;
    assert.strictEqual(c.size, 1, 'size must ignore expired entries');
  }
  { // reads refresh recency
    t = 0; const c = mk(2);
    c.set('a', 1, 1e6); c.set('b', 2, 1e6); c.get('a'); c.set('c', 3, 1e6);
    assert.strictEqual(c.get('b'), undefined, 'least recently used entry must be evicted');
    assert.strictEqual(c.get('a'), 1);
  }
  { // expiry boundary: expired when now >= expiresAt
    t = 0; const c = mk(2);
    c.set('a', 1, 100);
    t = 99; assert.strictEqual(c.get('a'), 1);
    t = 100; assert.strictEqual(c.get('a'), undefined, 'entry must be expired at now() === expiresAt');
  }
  console.log('PASS');
} catch (e) { console.error('FAIL:', e.message.split('\n')[0]); process.exit(1); }
