const assert = require('assert');
const { cloneConfig } = require('./solution');

try {
  // 1. undefined properties must survive (JSON.stringify drops them silently)
  const src1 = { a: 1, b: undefined, c: { d: undefined, e: 2 } };
  const c1 = cloneConfig(src1);
  assert.ok(Object.prototype.hasOwnProperty.call(c1, 'b'),
    'undefined property must exist on clone (JSON.parse drops it)');
  assert.strictEqual(c1.b, undefined, 'undefined value must be preserved');
  assert.ok(Object.prototype.hasOwnProperty.call(c1.c, 'd'),
    'nested undefined property must exist on clone');

  // 2. Date must clone as a Date, not a string
  const now = new Date('2024-06-15T08:30:00.000Z');
  const src2 = { created: now };
  const c2 = cloneConfig(src2);
  assert.ok(c2.created instanceof Date,
    'Date must be cloned as a Date instance, not a string (JSON.parse converts to string)');
  assert.strictEqual(c2.created.toISOString(), now.toISOString(), 'Date value must be identical');

  // 3. Modifying a cloned Date must not affect the original
  c2.created.setFullYear(2000);
  assert.strictEqual(now.getFullYear(), 2024,
    'cloned Date must not share a reference with the original');

  // 4. RegExp must clone as a RegExp, not an empty object
  const re = /hello\s+world/gi;
  const src3 = { pattern: re };
  const c3 = cloneConfig(src3);
  assert.ok(c3.pattern instanceof RegExp,
    'RegExp must be cloned as a RegExp instance, not {} (JSON.parse converts to {})');
  assert.strictEqual(c3.pattern.source, re.source, 'RegExp source must match');
  assert.strictEqual(c3.pattern.flags, re.flags, 'RegExp flags must match');

  // 5. No shared nested object references
  const src4 = { settings: { theme: 'dark', count: 0 } };
  const c4 = cloneConfig(src4);
  c4.settings.theme = 'light';
  assert.strictEqual(src4.settings.theme, 'dark',
    'mutating clone must not affect original nested object');

  console.log('PASS');
} catch (e) {
  console.error('FAIL:', e.message.split('\n')[0]);
  process.exit(1);
}
