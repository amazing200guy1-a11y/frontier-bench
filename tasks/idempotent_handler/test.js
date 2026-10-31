const assert = require('assert');
const { createIdempotentHandler } = require('./solution');
const sleep = (ms) => new Promise((r) => setTimeout(r, ms));

(async () => {
  // 1. concurrent same-key calls run processFn exactly once
  let calls = 0;
  const h = createIdempotentHandler(async (p) => { calls++; await sleep(20); return { charged: p.amount }; });
  const res = await Promise.all(Array.from({ length: 20 }, () => h('k1', { amount: 5 })));
  assert.strictEqual(calls, 1, 'processFn ran more than once for concurrent same-key calls');
  res.forEach((r) => assert.deepStrictEqual(r, { charged: 5 }));

  // 2. different keys are independent
  calls = 0;
  await Promise.all([h('a', { amount: 1 }), h('b', { amount: 2 })]);
  assert.strictEqual(calls, 2, 'distinct keys must each be processed');

  // 3. a failure must not poison the key
  let attempts = 0;
  const h2 = createIdempotentHandler(async () => { attempts++; await sleep(10); if (attempts === 1) throw new Error('boom'); return 'ok'; });
  const settled = await Promise.allSettled([h2('k', {}), h2('k', {}), h2('k', {})]);
  assert.ok(settled.every((s) => s.status === 'rejected'), 'concurrent callers should share the failure');
  assert.strictEqual(attempts, 1, 'failure path ran processFn more than once');
  assert.strictEqual(await h2('k', {}), 'ok', 'retry after failure must re-run processFn');
  assert.strictEqual(attempts, 2);

  // 4. synchronous throw inside processFn becomes a rejected promise
  const h3 = createIdempotentHandler(() => { throw new Error('sync'); });
  let p;
  try { p = h3('x', {}); } catch (e) { assert.fail('handle() threw synchronously'); }
  await assert.rejects(p);

  console.log('PASS');
})().catch((e) => { console.error('FAIL:', e.message); process.exit(1); });
