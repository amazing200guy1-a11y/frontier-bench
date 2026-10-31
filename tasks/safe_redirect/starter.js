const ALLOWED_ORIGIN = 'https://app.example.com';

function isSafeRedirect(url) {
  if (typeof url !== 'string') return false;
  return url.startsWith('/') || url.startsWith(ALLOWED_ORIGIN);
}

module.exports = { isSafeRedirect };
