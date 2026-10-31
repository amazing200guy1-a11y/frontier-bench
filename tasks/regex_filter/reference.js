const esc = (s) => s.replace(/[.*+?^${}()|[\]\\]/g, '\\$&');

function createFilter(words) {
  if (!words || words.length === 0) {
    return {
      isFlagged: () => false,
      redact: (t) => (typeof t === 'string' ? t : ''),
    };
  }
  const src = `\\b(?:${words.map(esc).join('|')})\\b`;
  const testRe = new RegExp(src, 'i'); // stateless without /g
  return {
    isFlagged: (text) => {
      if (typeof text !== 'string') return false;
      return testRe.test(text);
    },
    redact: (text) => {
      if (typeof text !== 'string') return '';
      const allRe = new RegExp(src, 'gi');
      return text.replace(allRe, (m) => '*'.repeat(m.length));
    },
  };
}

module.exports = { createFilter };
