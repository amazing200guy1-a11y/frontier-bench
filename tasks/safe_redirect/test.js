const assert = require('assert');
const { isSafeRedirect } = require('./solution');
const allowed = ['/', '/dashboard', '/dashboard?tab=1#x', 'https://app.example.com', 'https://app.example.com/x?y=1'];
const blocked = [
  ['protocol-relative', '//evil.com'],
  ['backslash', '/\\evil.com'],
  ['tab inside //', '/\t/evil.com'],
  ['newline inside //', '/\n/evil.com'],
  ['lookalike domain', 'https://app.example.com.evil.com/'],
  ['userinfo host', 'https://app.example.com@evil.com/'],
  ['other host with allowed host in query', 'https://evil.com/?https://app.example.com'],
  ['http downgrade', 'http://app.example.com/x'],
  ['javascript scheme', 'javascript:alert(1)'],
  ['leading space', ' //evil.com'],
  ['CRLF header injection', '/ok\r\nSet-Cookie: a=b'],
  ['empty', ''],
  ['null', null],
  ['number', 123],
  ['object', {}],
];
try {
  for (const u of allowed) assert.strictEqual(isSafeRedirect(u), true, `should allow ${JSON.stringify(u)}`);
  for (const [name, u] of blocked) {
    let r;
    try { r = isSafeRedirect(u); } catch (e) { assert.fail(`${name}: threw ${e.message}`); }
    assert.strictEqual(r, false, `should block (${name}) ${JSON.stringify(u)}`);
  }
  console.log('PASS');
} catch (e) { console.error('FAIL:', e.message.split('\n')[0]); process.exit(1); }
