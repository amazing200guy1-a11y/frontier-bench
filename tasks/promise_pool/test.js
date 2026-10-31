const assert = require('assert');
const { runPool } = require('./solution');
const sleep = (ms) => new Promise((r) => setTimeout(r, ms));

(async () => {
  { // order + concurrency bound, and the limit is actually used
    let active = 0, maxActive = 0;
    const mk = (i, ms) => async () => { active++; maxActive = Math.max(maxActive, active); await sleep(ms); active--; return i; };
    const tasks = Array.from({ length: 12 }, (_, i) => mk(i, 5 + ((i * 7) % 20)));
    const out = await runPool(tasks, 3);
    assert.deepStrictEqual(out, [0, 1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 11], 'results must be in input order');
    assert.strictEqual(maxActive, 3, 'must use the full concurrency limit and never exceed it');
  }
  { // a slow task must not stall the rest (no batch barrier)
    let t0done = false, t2startedBeforeT0Done = null;
    const out = await runPool([
      async () => { await sleep(150); t0done = true; return 0; },
      async () => { await sleep(10); return 1; },
      async () => { t2startedBeforeT0Done = !t0done; await sleep(10); return 2; },
      async () => { await sleep(10); return 3; },
    ], 2);
    assert.deepStrictEqual(out, [0, 1, 2, 3]);
    assert.strictEqual(t2startedBeforeT0Done, true, 'task 2 should start as soon as a slot frees up, not after the slow task finishes');
  }
  { // after the first failure, no new tasks start, and the pool rejects with that error
    let started = 0;
    const mk = (ms, fail) => () => { started++; return new Promise((res, rej) => setTimeout(() => (fail ? rej(new Error('boom')) : res('ok')), ms)); };
    await assert.rejects(runPool([mk(10, true), mk(60, false), mk(10, false), mk(10, false), mk(10, false)], 2), /boom/);
    await sleep(150);
    assert.ok(started <= 2, `started ${started} tasks; no new task may start after a failure`);
  }
  { // edge cases
    assert.deepStrictEqual(await runPool([], 4), []);
    assert.deepStrictEqual(await runPool([async () => 1], 10), [1]);
  }
  console.log('PASS');
})().catch((e) => { console.error('FAIL:', e.message.split('\n')[0]); process.exit(1); });
