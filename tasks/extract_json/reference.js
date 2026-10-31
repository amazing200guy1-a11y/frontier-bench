function extractJson(text) {
  if (typeof text !== 'string') return null;
  for (let start = text.indexOf('{'); start !== -1; start = text.indexOf('{', start + 1)) {
    let depth = 0, inStr = false, esc = false;
    for (let i = start; i < text.length; i++) {
      const c = text[i];
      if (inStr) {
        if (esc) esc = false;
        else if (c === '\\') esc = true;
        else if (c === '"') inStr = false;
        continue;
      }
      if (c === '"') inStr = true;
      else if (c === '{') depth++;
      else if (c === '}') {
        depth--;
        if (depth === 0) {
          try {
            const v = JSON.parse(text.slice(start, i + 1));
            if (v && typeof v === 'object' && !Array.isArray(v)) return v;
          } catch (_) { /* try next candidate */ }
          break;
        }
      }
    }
  }
  return null;
}

module.exports = { extractJson };
