function allocate(totalMinor, weights) {
  const sum = weights.reduce((a, b) => a + b, 0);
  if (sum <= 0) throw new RangeError('weights must sum to a positive number');
  return weights.map((w) => Math.round((totalMinor * w) / sum));
}

module.exports = { allocate };
