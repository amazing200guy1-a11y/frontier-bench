function wordFreq(text) {
  const map = new Map();
  const words = typeof text === 'string' ? text.match(/\S+/g) || [] : [];
  for (const w of words) {
    map.set(w, (map.get(w) || 0) + 1);
  }
  return Object.fromEntries(map);
}

module.exports = { wordFreq };
