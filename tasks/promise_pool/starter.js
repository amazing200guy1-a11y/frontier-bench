async function runPool(tasks, limit) {
  const results = [];
  for (let i = 0; i < tasks.length; i += limit) {
    const batch = tasks.slice(i, i + limit).map((task) => task());
    results.push(...(await Promise.all(batch)));
  }
  return results;
}

module.exports = { runPool };
