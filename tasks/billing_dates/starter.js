function nextBillingDates(anchorIso, count) {
  const dates = [];
  const d = new Date(`${anchorIso}T00:00:00Z`);

  for (let i = 0; i < count; i++) {
    d.setUTCMonth(d.getUTCMonth() + 1);
    dates.push(d.toISOString().slice(0, 10));
  }
  return dates;
}

module.exports = { nextBillingDates };
