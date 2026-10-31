const assert = require('assert');
const { createFilter } = require('./solution');

try {
  const f = createFilter(['bad', 'danger']);

  // Statefulness trap on repeat calls
  assert.strictEqual(f.isFlagged('this is bad'), true, 'first isFlagged call should return true');
  assert.strictEqual(f.isFlagged('this is bad'), true, 'repeat isFlagged call with same text must also return true (RegExp /g statefulness bug)');
  assert.strictEqual(f.isFlagged('this is bad'), true, 'third isFlagged call must still return true');

  // Interleaved redact and isFlagged
  assert.strictEqual(f.redact('so bad and danger'), 'so *** and ******');
  assert.strictEqual(f.isFlagged('bad'), true, 'isFlagged after redact must return true');

  // Case insensitivity & word boundary
  assert.strictEqual(f.isFlagged('BAD'), true, 'case insensitive match');
  assert.strictEqual(f.isFlagged('badge'), false, 'should not match partial word');
  assert.strictEqual(f.isFlagged('danger!'), true, 'should match punctuation boundary');

  console.log('PASS');
} catch (e) {
  console.error('FAIL:', e.message.split('\n')[0]);
  process.exit(1);
}
