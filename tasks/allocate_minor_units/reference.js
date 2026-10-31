function allocate(totalMinor, weights) {
  const sum = weights.reduce((a, b) => a + b, 0);
  if (sum <= 0) throw new RangeError('weights must sum to a positive number');

  const shares = [];
  const remainders = [];
  let used = 0;
  weights.forEach((w, i) => {
    const num = totalMinor * w;
    const r = num % sum;
    shares[i] = (num - r) / sum;
    remainders[i] = r;
    used += shares[i];
  });

  const order = weights.map((_, i) => i).sort((a, b) => remainders[b] - remainders[a] || a - b);
  for (let k = 0; k < totalMinor - used; k++) shares[order[k]] += 1;
  return shares;
}

module.exports = { allocate };
