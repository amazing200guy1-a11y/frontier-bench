function createSearch(fetchResults, render, onError) {
  let latest = null;

  return async function search(query) {
    latest = query;
    try {
      const results = await fetchResults(query);
      if (latest === query) render(results, query);
    } catch (err) {
      onError(err, query);
    }
  };
}

module.exports = { createSearch };
