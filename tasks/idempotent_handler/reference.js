function createIdempotentHandler(processFn) {
  const inflight = new Map();
  return function handle(key, payload) {
    if (inflight.has(key)) return inflight.get(key);
    const p = Promise.resolve().then(() => processFn(payload));
    inflight.set(key, p);
    p.catch(() => { if (inflight.get(key) === p) inflight.delete(key); });
    return p;
  };
}

module.exports = { createIdempotentHandler };
