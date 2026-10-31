const assert = require('assert');
const { allocate } = require('./solution');
try {
  assert.deepStrictEqual(allocate(100, [1, 1, 1]), [34, 33, 33], 'ties go to the earlier index');
  assert.deepStrictEqual(allocate(10, [1, 1, 1]), [4, 3, 3]);
  assert.deepStrictEqual(allocate(2, [1, 1, 1]), [1, 1, 0]);
  assert.deepStrictEqual(allocate(1, [1, 1, 1]), [1, 0, 0]);
  assert.deepStrictEqual(allocate(7, [1, 2]), [2, 5], 'largest remainder wins');
  assert.deepStrictEqual(allocate(100, [1, 2, 3]), [17, 33, 50], 'largest remainder is index 0 here, not the last recipient');
  assert.deepStrictEqual(allocate(100, [50, 30, 20]), [50, 30, 20]);
  assert.deepStrictEqual(allocate(10, [0, 5, 5]), [0, 5, 5], 'zero weight gets nothing');
  assert.deepStrictEqual(allocate(1, [0, 1]), [0, 1]);
  assert.throws(() => allocate(10, [0, 0]), RangeError);

  let seed = 12345;
  const rnd = (n) => { seed = (seed * 16807) % 2147483647; return seed % n; };
  for (let t = 0; t < 2000; t++) {
    const k = 1 + rnd(6);
    const w = Array.from({ length: k }, () => rnd(1000));
    if (w.every((x) => x === 0)) w[0] = 1;
    const total = rnd(1000000);
    const out = allocate(total, w);
    assert.strictEqual(out.reduce((a, b) => a + b, 0), total, `sum mismatch for total=${total} weights=${w}`);
    const S = BigInt(w.reduce((a, b) => a + b, 0));
    w.forEach((wi, i) => {
      const fl = Number((BigInt(total) * BigInt(wi)) / S);
      assert.ok(out[i] === fl || out[i] === fl + 1, `share out of range for total=${total} weights=${w}`);
    });
  }
  console.log('PASS');
} catch (e) { console.error('FAIL:', e.message); process.exit(1); }
