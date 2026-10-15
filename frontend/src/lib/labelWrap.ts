const WORD_SEPARATOR = /\s+/;
const DANGLING_PUNCTUATION = /^[-–—|·]\s*|\s*[-–—|·]$/g;

export function wrapLabel(label: string, maxLineLength: number): string[] {
  const words = label.split(WORD_SEPARATOR).filter(Boolean);
  const lines = words.reduce<string[]>((wrapped, word) => appendWord(wrapped, word, maxLineLength), []);
  return lines.map(withoutDanglingPunctuation).filter(Boolean);
}

function withoutDanglingPunctuation(line: string): string {
  return line.replace(DANGLING_PUNCTUATION, "");
}

function appendWord(lines: string[], word: string, maxLineLength: number): string[] {
  const currentLine = lines.at(-1);
  const extendedLine = `${currentLine} ${word}`;
  if (currentLine === undefined || extendedLine.length > maxLineLength) return [...lines, word];
  return [...lines.slice(0, -1), extendedLine];
}
