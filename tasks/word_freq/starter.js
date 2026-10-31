function wordFreq(text) {
  const counts = {};
  const words = typeof text === 'string' ? text.match(/\S+/g) || [] : [];
  for (const w of words) {
    counts[w] = (counts[w] || 0) + 1;
  }
  return counts;
}

module.exports = { wordFreq };
