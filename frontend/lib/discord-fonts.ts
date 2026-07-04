// Unicode "font" styles. These map A-Z, a-z, 0-9 to look-alike Unicode
// codepoints so the text renders styled anywhere that accepts Unicode,
// including Discord display names, statuses, and (visually) messages.

const UP = "ABCDEFGHIJKLMNOPQRSTUVWXYZ";
const LOW = "abcdefghijklmnopqrstuvwxyz";
const DIG = "0123456789";

type Style = { name: string; map: (c: string) => string };

// Build a translator from explicit target strings (must be same length or a
// generator function based on codepoint offset).
function fromRanges(upStart: number, lowStart: number, digStart?: number): (c: string) => string {
  return (c: string) => {
    const i = UP.indexOf(c);
    if (i >= 0) return String.fromCodePoint(upStart + i);
    const j = LOW.indexOf(c);
    if (j >= 0) return String.fromCodePoint(lowStart + j);
    if (digStart !== undefined) {
      const k = DIG.indexOf(c);
      if (k >= 0) return String.fromCodePoint(digStart + k);
    }
    return c;
  };
}

function fromExplicit(up: string[], low: string[], dig?: string[]): (c: string) => string {
  return (c: string) => {
    const i = UP.indexOf(c);
    if (i >= 0) return up[i] ?? c;
    const j = LOW.indexOf(c);
    if (j >= 0) return low[j] ?? c;
    if (dig) {
      const k = DIG.indexOf(c);
      if (k >= 0) return dig[k] ?? c;
    }
    return c;
  };
}

const s = (str: string) => Array.from(str);

export const DISCORD_FONT_STYLES: Style[] = [
  { name: "Bold", map: fromRanges(0x1d400, 0x1d41a, 0x1d7ce) },
  { name: "Italic", map: fromRanges(0x1d434, 0x1d44e) },
  { name: "Bold Italic", map: fromRanges(0x1d468, 0x1d482) },
  { name: "Script", map: fromRanges(0x1d49c, 0x1d4b6) },
  { name: "Bold Script", map: fromRanges(0x1d4d0, 0x1d4ea) },
  { name: "Fraktur", map: fromRanges(0x1d504, 0x1d51e) },
  { name: "Bold Fraktur", map: fromRanges(0x1d56c, 0x1d586) },
  { name: "Double-struck", map: fromRanges(0x1d538, 0x1d552, 0x1d7d8) },
  { name: "Sans-serif", map: fromRanges(0x1d5a0, 0x1d5ba, 0x1d7e2) },
  { name: "Sans Bold", map: fromRanges(0x1d5d4, 0x1d5ee, 0x1d7ec) },
  { name: "Monospace", map: fromRanges(0x1d670, 0x1d68a, 0x1d7f6) },
  {
    name: "Circled",
    map: fromExplicit(
      s("\u24B6\u24B7\u24B8\u24B9\u24BA\u24BB\u24BC\u24BD\u24BE\u24BF\u24C0\u24C1\u24C2\u24C3\u24C4\u24C5\u24C6\u24C7\u24C8\u24C9\u24CA\u24CB\u24CC\u24CD\u24CE\u24CF"),
      s("\u24D0\u24D1\u24D2\u24D3\u24D4\u24D5\u24D6\u24D7\u24D8\u24D9\u24DA\u24DB\u24DC\u24DD\u24DE\u24DF\u24E0\u24E1\u24E2\u24E3\u24E4\u24E5\u24E6\u24E7\u24E8\u24E9"),
    ),
  },
  {
    name: "Squared",
    map: fromExplicit(
      s("\u{1F130}\u{1F131}\u{1F132}\u{1F133}\u{1F134}\u{1F135}\u{1F136}\u{1F137}\u{1F138}\u{1F139}\u{1F13A}\u{1F13B}\u{1F13C}\u{1F13D}\u{1F13E}\u{1F13F}\u{1F140}\u{1F141}\u{1F142}\u{1F143}\u{1F144}\u{1F145}\u{1F146}\u{1F147}\u{1F148}\u{1F149}"),
      s("\u{1F130}\u{1F131}\u{1F132}\u{1F133}\u{1F134}\u{1F135}\u{1F136}\u{1F137}\u{1F138}\u{1F139}\u{1F13A}\u{1F13B}\u{1F13C}\u{1F13D}\u{1F13E}\u{1F13F}\u{1F140}\u{1F141}\u{1F142}\u{1F143}\u{1F144}\u{1F145}\u{1F146}\u{1F147}\u{1F148}\u{1F149}"),
    ),
  },
  {
    name: "Fullwidth",
    map: fromRanges(0xff21, 0xff41, 0xff10),
  },
  {
    name: "Bubble (lower)",
    map: fromExplicit(
      s("\u24B6\u24B7\u24B8\u24B9\u24BA\u24BB\u24BC\u24BD\u24BE\u24BF\u24C0\u24C1\u24C2\u24C3\u24C4\u24C5\u24C6\u24C7\u24C8\u24C9\u24CA\u24CB\u24CC\u24CD\u24CE\u24CF"),
      s("\u24D0\u24D1\u24D2\u24D3\u24D4\u24D5\u24D6\u24D7\u24D8\u24D9\u24DA\u24DB\u24DC\u24DD\u24DE\u24DF\u24E0\u24E1\u24E2\u24E3\u24E4\u24E5\u24E6\u24E7\u24E8\u24E9"),
    ),
  },
];

export function styleText(text: string, map: (c: string) => string): string {
  return Array.from(text).map(map).join("");
}

export interface MarkdownRule {
  label: string;
  syntax: string;
  note: string;
}

export const DISCORD_MARKDOWN: MarkdownRule[] = [
  { label: "Bold", syntax: "**text**", note: "Wrap text in two asterisks on each side." },
  { label: "Italic", syntax: "*text*", note: "One asterisk (or underscore) each side." },
  { label: "Bold Italic", syntax: "***text***", note: "Three asterisks each side." },
  { label: "Underline", syntax: "__text__", note: "Two underscores each side." },
  { label: "Strikethrough", syntax: "~~text~~", note: "Two tildes each side." },
  { label: "Spoiler", syntax: "||text||", note: "Two pipes each side; hidden until clicked." },
  { label: "Inline code", syntax: "`code`", note: "Single backticks around the text." },
  { label: "Code block", syntax: "```lang\\ncode\\n```", note: "Triple backticks; add a language for syntax highlighting." },
  { label: "Quote", syntax: "> text", note: "Greater-than sign and a space start a block quote." },
  { label: "Block quote", syntax: ">>> text", note: "Three greater-than signs quote everything after it." },
  { label: "Big header", syntax: "# Heading", note: "One hash and a space (H1). Use ## and ### for smaller." },
  { label: "Masked link", syntax: "[label](https://url)", note: "Shows the label as a clickable link (in embeds/channels that allow it)." },
];
