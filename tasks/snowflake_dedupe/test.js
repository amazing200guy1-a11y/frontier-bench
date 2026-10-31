const assert = require('assert');
const { dedupeById } = require('./solution');

const json = '[{"id":9007199254740993,"v":"a"},{"id":9007199254740992,"v":"b"},' +
             '{"id":9007199254740993,"v":"c"},{"id":5,"v":"d"},{"id":5,"v":"e"}]';
try {
  const out = dedupeById(json);
  assert.deepStrictEqual(out.map((r) => String(r.id)),
    ['9007199254740993', '9007199254740992', '5'], 'ids must keep full precision and dedupe exactly');
  assert.deepStrictEqual(out.map((r) => r.v), ['a', 'b', 'd'], 'first row per id must win');
  console.log('PASS');
} catch (e) { console.error('FAIL:', e.message); process.exit(1); }
