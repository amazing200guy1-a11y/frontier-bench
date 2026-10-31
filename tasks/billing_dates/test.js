const assert = require('assert');
const { nextBillingDates } = require('./solution');
try {
  assert.deepStrictEqual(nextBillingDates('2024-01-31', 5),
    ['2024-02-29', '2024-03-31', '2024-04-30', '2024-05-31', '2024-06-30'], 'Jan 31 anchor (leap year) must return to the 31st after short months');
  assert.deepStrictEqual(nextBillingDates('2023-01-31', 3),
    ['2023-02-28', '2023-03-31', '2023-04-30'], 'Jan 31 anchor (non-leap year)');
  assert.deepStrictEqual(nextBillingDates('2024-01-30', 2), ['2024-02-29', '2024-03-30'], 'Jan 30 anchor');
  const feb29 = nextBillingDates('2024-02-29', 13);
  assert.strictEqual(feb29[9], '2024-12-29', 'Feb 29 anchor, December');
  assert.strictEqual(feb29[10], '2025-01-29', 'Feb 29 anchor must stay on the 29th across the year boundary');
  assert.strictEqual(feb29[11], '2025-02-28', 'Feb 29 anchor in a non-leap February');
  assert.strictEqual(feb29[12], '2025-03-29', 'Feb 29 anchor must recover to the 29th');
  assert.deepStrictEqual(nextBillingDates('2024-12-15', 2), ['2025-01-15', '2025-02-15'], 'year rollover');
  assert.deepStrictEqual(nextBillingDates('2024-05-10', 0), [], 'count 0');
  console.log('PASS');
} catch (e) { console.error('FAIL:', e.message); process.exit(1); }
