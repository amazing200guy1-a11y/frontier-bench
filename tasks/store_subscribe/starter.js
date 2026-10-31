function createStore(initial) {
  let state = initial;
  const listeners = [];

  return {
    getState: () => state,
    setState(next) {
      state = next;
      for (let i = 0; i < listeners.length; i++) listeners[i](state);
    },
    subscribe(fn) {
      listeners.push(fn);
      return () => {
        listeners.splice(listeners.indexOf(fn), 1);
      };
    },
  };
}

module.exports = { createStore };
