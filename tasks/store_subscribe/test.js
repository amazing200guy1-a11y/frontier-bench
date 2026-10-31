const assert = require('assert');
const { createStore } = require('./solution');
try {
  { // listener unsubscribing itself must not make the next listener skip
    const s = createStore(0); let calls = []; let unsubA;
    unsubA = s.subscribe(() => { calls.push('a'); unsubA(); });
    s.subscribe(() => calls.push('b'));
    s.subscribe(() => calls.push('c'));
    s.setState(1);
    assert.deepStrictEqual(calls, ['a', 'b', 'c'], 'self-unsubscribe during dispatch skipped a listener');
    calls = []; s.setState(2);
    assert.deepStrictEqual(calls, ['b', 'c'], 'unsubscribed listener must not be called again');
  }
  { // calling unsubscribe twice must not remove someone else's listener
    const s = createStore(0); const c = [];
    const un1 = s.subscribe(() => c.push(1));
    s.subscribe(() => c.push(2));
    un1(); un1();
    s.setState(1);
    assert.deepStrictEqual(c, [2], 'double unsubscribe removed another listener');
  }
  { // subscribing during dispatch: not called in the current dispatch
    const s = createStore(0); const c = []; let added = false;
    s.subscribe(() => { c.push('a'); if (!added) { added = true; s.subscribe(() => c.push('late')); } });
    s.setState(1);
    assert.deepStrictEqual(c, ['a'], 'listener added during dispatch must wait for the next dispatch');
    s.setState(2);
    assert.deepStrictEqual(c, ['a', 'a', 'late']);
  }
  { // Redux snapshot: listener removed by an earlier listener is still called in this dispatch
    const s = createStore(0); const c = []; let unsubB;
    s.subscribe(() => { c.push('a'); unsubB(); });
    unsubB = s.subscribe(() => c.push('b'));
    s.setState(1);
    assert.deepStrictEqual(c, ['a', 'b'], 'listeners are snapshotted at the start of each dispatch');
    s.setState(2);
    assert.deepStrictEqual(c, ['a', 'b', 'a']);
  }
  { // same function subscribed twice is two subscriptions
    const s = createStore(0); let n = 0; const f = () => n++;
    const u1 = s.subscribe(f); s.subscribe(f);
    s.setState(1); assert.strictEqual(n, 2);
    u1(); u1();
    s.setState(2); assert.strictEqual(n, 3, 'one unsubscribe removes exactly one subscription');
  }
  console.log('PASS');
} catch (e) { console.error('FAIL:', e.message.split('\n')[0]); process.exit(1); }
