function compose(middlewares) {
  return function run(ctx) {
    let i = 0;
    function next() {
      const fn = middlewares[i++];
      return fn ? Promise.resolve(fn(ctx, next)) : Promise.resolve();
    }
    return next();
  };
}

module.exports = { compose };
