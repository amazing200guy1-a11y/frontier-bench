const dedupeById = (json) => {
  const seen = new Set();
  return JSON.parse(json).filter((row) => !seen.has(row.id) && seen.add(row.id));
};

module.exports = { dedupeById };
