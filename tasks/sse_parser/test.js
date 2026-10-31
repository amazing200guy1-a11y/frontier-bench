const assert = require('assert');
const { createSSEParser } = require('./solution');
const run = (chunks) => {
  const out = [];
  const p = createSSEParser((e) => out.push(e));
  chunks.forEach((c) => p.write(c));
  return out;
};
const msg = (data, event = 'message') => ({ event, data });
try {
  assert.deepStrictEqual(run(['data: hel', 'lo\n\ndata: wor', 'ld\n\n']), [msg('hello'), msg('world')], 'event split across chunks');
  assert.deepStrictEqual(run(['data: a\ndata: b\n\n']), [msg('a\nb')], 'multi-line data joined with newline');
  assert.deepStrictEqual(run(['data: x\r\n\r\n']), [msg('x')], 'CRLF line endings');
  assert.deepStrictEqual(run(['data: q\r', '\n\r', '\n']), [msg('q')], 'CRLF split across chunks');
  assert.deepStrictEqual(run([': keepalive\n\ndata: y\n\n']), [msg('y')], 'comment-only block is not an event');
  assert.deepStrictEqual(run(['event: delta\ndata: z\n\n']), [msg('z', 'delta')], 'named event');
  assert.deepStrictEqual(run(['data:  two spaces\n\n']), [msg(' two spaces')], 'only ONE leading space is stripped');
  assert.deepStrictEqual(run(['data:nospace\n\n']), [msg('nospace')], 'no space after colon');
  assert.deepStrictEqual(run(['id: 7\nretry: 100\ndata: k\n\n']), [msg('k')], 'id and retry fields are not data');
  assert.deepStrictEqual(run(['data: incomplete']), [], 'incomplete event is not dispatched');
  assert.deepStrictEqual(run(['data: a\n', '\ndata: b\n', '\n']), [msg('a'), msg('b')], 'blank line arriving in its own chunk');
  console.log('PASS');
} catch (e) { console.error('FAIL:', e.message.split('\n')[0]); process.exit(1); }
