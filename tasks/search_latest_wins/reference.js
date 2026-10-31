function createSearch(fetchResults, render, onError) {
  let seq = 0;

  return async function search(query) {
    const mine = ++seq;
    try {
      const results = await fetchResults(query);
      if (mine === seq) render(results, query);
    } catch (err) {
      if (mine === seq) onError(err, query);
    }
  };
}

module.exports = { createSearch };
