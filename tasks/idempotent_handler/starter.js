function createIdempotentHandler(processFn) {
  const done = new Map();
  return async function handle(key, payload) {
    if (done.has(key)) return done.get(key);
    const result = await processFn(payload);
    done.set(key, result);
    return result;
  };
}

module.exports = { createIdempotentHandler };
