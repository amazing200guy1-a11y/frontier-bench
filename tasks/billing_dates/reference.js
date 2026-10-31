function nextBillingDates(anchorIso, count) {
  const [ay, am, ad] = anchorIso.split('-').map(Number);
  const out = [];
  for (let i = 1; i <= count; i++) {
    const m0 = am - 1 + i;
    const y = ay + Math.floor(m0 / 12);
    const m = m0 % 12;
    const dim = new Date(Date.UTC(y, m + 1, 0)).getUTCDate();
    const day = Math.min(ad, dim);
    out.push(`${y}-${String(m + 1).padStart(2, '0')}-${String(day).padStart(2, '0')}`);
  }
  return out;
}

module.exports = { nextBillingDates };
