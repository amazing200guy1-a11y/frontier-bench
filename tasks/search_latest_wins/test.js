const assert = require('assert');
const { createSearch } = require('./solution');
const flush = () => new Promise((r) => setImmediate(r));
function deferred() {
  let resolve, reject;
  const promise = new Promise((a, b) => { resolve = a; reject = b; });
  return { promise, resolve, reject };
}
function setup(defs) {
  let n = 0;
  const renders = [], errors = [];
  const search = createSearch(() => defs[n++].promise, (r, q) => renders.push([r, q]), (e) => errors.push(e.message));
  const go = (q) => { const p = search(q); if (p && p.catch) p.catch(() => {}); return p; };
  return { go, renders, errors };
}

(async () => {
  { // out-of-order responses for different queries
    const d = [deferred(), deferred()];
    const s = setup(d);
    s.go('a'); s.go('ab');
    d[1].resolve('R_ab'); await flush();
    d[0].resolve('R_a'); await flush();
    assert.deepStrictEqual(s.renders, [['R_ab', 'ab']], 'stale response for an older query must not render');
  }
  { // stale response arrives first
    const d = [deferred(), deferred()];
    const s = setup(d);
    s.go('a'); s.go('ab');
    d[0].resolve('R_a'); await flush();
    assert.deepStrictEqual(s.renders, [], 'older response must not render while a newer request is pending');
    d[1].resolve('R_ab'); await flush();
    assert.deepStrictEqual(s.renders, [['R_ab', 'ab']]);
  }
  { // Refresh: same query issued twice, older response arrives last
    const d = [deferred(), deferred()];
    const s = setup(d);
    s.go('a'); s.go('a');
    d[1].resolve('new'); await flush();
    d[0].resolve('old'); await flush();
    assert.deepStrictEqual(s.renders, [['new', 'a']], 'older response for the SAME query must not overwrite a newer one');
  }
  { // stale rejection must be swallowed, latest rejection reported
    const d = [deferred(), deferred()];
    const s = setup(d);
    s.go('a'); s.go('b');
    d[0].reject(new Error('stale')); await flush();
    assert.deepStrictEqual(s.errors, [], 'error from a superseded request must not reach onError');
    d[1].reject(new Error('latest')); await flush();
    assert.deepStrictEqual(s.errors, ['latest']);
  }
  console.log('PASS');
})().catch((e) => { console.error('FAIL:', e.message); process.exit(1); });
