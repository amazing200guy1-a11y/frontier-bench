const esc = (s) => s.replace(/[.*+?^${}()|[\]\\]/g, '\\$&');

function createFilter(words) {
  const re = new RegExp(`\\b(?:${words.map(esc).join('|')})\\b`, 'gi');
  return {
    isFlagged: (text) => re.test(text),
    redact: (text) => text.replace(re, (m) => '*'.repeat(m.length)),
  };
}

module.exports = { createFilter };
