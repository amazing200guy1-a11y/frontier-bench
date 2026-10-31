function createSSEParser(onEvent) {
  return {
    write(chunk) {
      for (const block of chunk.split('\n\n')) {
        const data = block
          .split('\n')
          .filter((line) => line.startsWith('data:'))
          .map((line) => line.slice(5).trim())
          .join('\n');
        if (data) onEvent({ event: 'message', data });
      }
    },
  };
}

module.exports = { createSSEParser };
