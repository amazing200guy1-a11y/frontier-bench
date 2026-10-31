function createStore(initial) {
  let state = initial;
  let listeners = [];

  return {
    getState: () => state,
    setState(next) {
      state = next;
      const snapshot = listeners;
      for (const entry of snapshot) entry.fn(state);
    },
    subscribe(fn) {
      const entry = { fn };
      listeners = [...listeners, entry];
      let subscribed = true;
      return () => {
        if (!subscribed) return;
        subscribed = false;
        listeners = listeners.filter((l) => l !== entry);
      };
    },
  };
}

module.exports = { createStore };
