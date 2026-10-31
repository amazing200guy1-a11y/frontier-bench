const assert = require('assert');
const { compose } = require('./solution');
const sleep = (ms) => new Promise((r) => setTimeout(r, ms));

(async () => {
  { // onion order with mixed sync/async middleware
    const log = [];
    await compose([
      async (ctx, next) => { log.push('1a'); await next(); log.push('1b'); },
      async (ctx, next) => { log.push('2a'); await sleep(5); await next(); log.push('2b'); },
      () => { log.push('3'); },
    ])({});
    assert.deepStrictEqual(log, ['1a', '2a', '3', '2b', '1b'], 'onion order');
  }
  { // next() twice in one middleware must surface an error to that middleware
    const ctx = {};
    await compose([
      async (c, next) => { await next(); try { await next(); c.err = null; } catch (e) { c.err = e; } },
      () => {},
    ])(ctx);
    assert.ok(ctx.err instanceof Error, 'second next() call must reject with an Error');
  }
  { // sync throw becomes a rejected promise, never a sync exception
    let p;
    try { p = compose([() => { throw new Error('x'); }])({}); }
    catch (e) { assert.fail('compose()(ctx) threw synchronously'); }
    await assert.rejects(p, /x/);
  }
  { // downstream error reaches upstream try/catch
    const ctx = {};
    await compose([
      async (c, next) => { try { await next(); } catch (e) { c.caught = e.message; } },
      async () => { await sleep(1); throw new Error('boom'); },
    ])(ctx);
    assert.strictEqual(ctx.caught, 'boom');
  }
  { // empty stack
    await compose([])({});
  }
  console.log('PASS');
})().catch((e) => { console.error('FAIL:', e.message.split('\n')[0]); process.exit(1); });
