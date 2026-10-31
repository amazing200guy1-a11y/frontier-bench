function cloneConfig(obj) {
  return JSON.parse(JSON.stringify(obj));
}

module.exports = { cloneConfig };
