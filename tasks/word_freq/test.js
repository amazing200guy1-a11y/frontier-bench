const assert = require('assert');
const { wordFreq } = require('./solution');

try {
  // Normal counting
  const basic = wordFreq('apple banana apple');
  assert.strictEqual(basic.apple, 2);
  assert.strictEqual(basic.banana, 1);

  // Prototype pollution & collision trap
  const prototypeWords = 'constructor constructor __proto__ toString valueOf hasOwnProperty word word';
  const result = wordFreq(prototypeWords);

  assert.strictEqual(result.constructor, 2, 'constructor should have count 2');
  assert.strictEqual(result.toString, 1, 'toString should have count 1, not function string concatenation');
  assert.strictEqual(result.valueOf, 1, 'valueOf should have count 1');
  assert.strictEqual(result.hasOwnProperty, 1, 'hasOwnProperty should have count 1');
  assert.strictEqual(result.word, 2, 'word should have count 2');

  // __proto__ own property test
  const protoResult = wordFreq('__proto__ __proto__');
  assert.strictEqual(Object.hasOwn(protoResult, '__proto__'), true, '__proto__ must be an own property');
  assert.strictEqual(Object.getOwnPropertyDescriptor(protoResult, '__proto__').value, 2, '__proto__ property value must be number 2');

  console.log('PASS');
} catch (e) {
  console.error('FAIL:', e.message.split('\n')[0]);
  process.exit(1);
}
