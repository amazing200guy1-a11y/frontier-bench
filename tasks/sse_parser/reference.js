function createSSEParser(onEvent) {
  let buf = '';

  function dispatch(block) {
    let event = '';
    const data = [];
    for (const line of block.split('\n')) {
      if (line === '' || line.startsWith(':')) continue;
      const idx = line.indexOf(':');
      const field = idx === -1 ? line : line.slice(0, idx);
      let value = idx === -1 ? '' : line.slice(idx + 1);
      if (value.startsWith(' ')) value = value.slice(1);
      if (field === 'data') data.push(value);
      else if (field === 'event') event = value;
    }
    if (data.length) onEvent({ event: event || 'message', data: data.join('\n') });
  }

  return {
    write(chunk) {
      buf += chunk;
      let pending = '';
      if (buf.endsWith('\r')) { pending = '\r'; buf = buf.slice(0, -1); }
      buf = buf.replace(/\r\n|\r/g, '\n');
      let i;
      while ((i = buf.indexOf('\n\n')) !== -1) {
        dispatch(buf.slice(0, i));
        buf = buf.slice(i + 2);
      }
      buf += pending;
    },
  };
}

module.exports = { createSSEParser };
