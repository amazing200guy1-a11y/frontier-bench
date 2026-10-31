const assert = require('assert');
const { extractJson } = require('./solution');
const cases = [
  ['fenced + trailing braces', 'Sure! Here you go:\n```json\n{"a":1}\n```\nHope that helps {not json}', { a: 1 }],
  ['brace inside string', '{"msg":"use } carefully","n":{"x":[1,2]}} trailing {x}', { msg: 'use } carefully', n: { x: [1, 2] } }],
  ['escaped quote + brace in string', 'He said "hi" then {"k":"va\\"l}ue"} end', { k: 'va"l}ue' }],
  ['malformed first candidate', 'Use {curly} braces: {"ok":true}', { ok: true }],
  ['two objects, first wins', '{"a":1} and {"b":2}', { a: 1 }],
  ['skips arrays', 'values [1,2,3] and {"z":0}', { z: 0 }],
  ['no json', 'no json here', null],
  ['empty string', '', null],
  ['unbalanced', 'broken {"a":1', null],
  ['undefined input', undefined, null],
  ['null input', null, null],
];
try {
  for (const [name, input, expected] of cases) {
    let out;
    try { out = extractJson(input); } catch (e) { assert.fail(`${name}: threw ${e.message}`); }
    assert.deepStrictEqual(out, expected, name);
  }
  console.log('PASS');
} catch (e) { console.error('FAIL:', e.message.split('\n')[0]); process.exit(1); }
