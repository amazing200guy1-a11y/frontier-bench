const ALLOWED_ORIGIN = 'https://app.example.com';

function isSafeRedirect(url) {
  if (typeof url !== 'string' || url === '') return false;
  if (/[\u0000-\u001f\u007f]/.test(url)) return false;
  let parsed;
  try {
    parsed = new URL(url, ALLOWED_ORIGIN);
  } catch (_) {
    return false;
  }
  return parsed.origin === ALLOWED_ORIGIN;
}

module.exports = { isSafeRedirect };
