export function cleanSubtitleText(text = "") {
  return String(text)
    .replace(/\*\*/g, "")
    .replace(/__/g, "")
    .replace(/[*`#]/g, "")
    .replace(/\s+/g, " ")
    .trim();
}

export function createSubtitleChunks(text = "") {
  const clean = cleanSubtitleText(text);
  if (!clean) return [];

  const words = clean.split(" ");
  const chunks = [];
  let current = [];

  for (const word of words) {
    current.push(word);
    const line = current.join(" ");
    if (current.length >= 8 || line.length >= 54) {
      chunks.push(line);
      current = [];
    }
  }

  if (current.length) chunks.push(current.join(" "));
  return chunks;
}

export function subtitleAtTime(chunks, currentTime, duration) {
  if (!Array.isArray(chunks) || !chunks.length) return "";
  if (!Number.isFinite(duration) || duration <= 0) return chunks[0];

  const progress = Math.max(0, Math.min(0.999999, currentTime / duration));
  const index = Math.min(chunks.length - 1, Math.floor(progress * chunks.length));
  return chunks[index];
}
