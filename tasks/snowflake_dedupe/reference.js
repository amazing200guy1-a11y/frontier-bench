/** Quote 16+ digit integer ids before parsing so they never become doubles. */
const dedupeById = (json) => {
  const safe = json.replace(/("id"\s*:\s*)(\d{16,})/g, '$1"$2"');
  const seen = new Set();
  return JSON.parse(safe).filter((row) => {
    const key = String(row.id);
    if (seen.has(key)) return false;
    seen.add(key);
    return true;
  });
};

module.exports = { dedupeById };
