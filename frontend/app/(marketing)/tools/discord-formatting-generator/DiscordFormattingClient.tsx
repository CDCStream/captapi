"use client";

import { useMemo, useState } from "react";
import { Copy, Check } from "lucide-react";

interface Format {
  name: string;
  wrap: (t: string) => string;
  hint: string;
}

const FORMATS: Format[] = [
  { name: "Bold", wrap: (t) => `**${t}**`, hint: "Two asterisks each side" },
  { name: "Italic", wrap: (t) => `*${t}*`, hint: "One asterisk each side" },
  { name: "Bold italic", wrap: (t) => `***${t}***`, hint: "Three asterisks each side" },
  { name: "Underline", wrap: (t) => `__${t}__`, hint: "Two underscores each side" },
  { name: "Strikethrough", wrap: (t) => `~~${t}~~`, hint: "Two tildes each side" },
  { name: "Spoiler (hidden)", wrap: (t) => `||${t}||`, hint: "Two pipes each side — click to reveal" },
  { name: "Inline code", wrap: (t) => `\`${t}\``, hint: "Single backticks" },
  { name: "Code block", wrap: (t) => `\`\`\`\n${t}\n\`\`\``, hint: "Triple backticks on their own lines" },
  { name: "Quote", wrap: (t) => `> ${t}`, hint: "Greater-than plus a space" },
  { name: "Big header (H1)", wrap: (t) => `# ${t}`, hint: "One hash plus a space" },
  { name: "Medium header (H2)", wrap: (t) => `## ${t}`, hint: "Two hashes plus a space" },
  { name: "Small header (H3)", wrap: (t) => `### ${t}`, hint: "Three hashes plus a space" },
  { name: "Masked link", wrap: (t) => `[${t}](https://example.com)`, hint: "Replace the URL — works in embeds" },
  { name: "Green text (code)", wrap: (t) => `\`\`\`diff\n+ ${t}\n\`\`\``, hint: "diff code block, + prefix" },
  { name: "Red text (code)", wrap: (t) => `\`\`\`diff\n- ${t}\n\`\`\``, hint: "diff code block, - prefix" },
];

export default function DiscordFormattingClient() {
  const [text, setText] = useState("your text here");
  const [copied, setCopied] = useState<string | null>(null);

  const safe = text || "your text here";

  const copy = async (name: string, value: string) => {
    try {
      await navigator.clipboard.writeText(value);
      setCopied(name);
      setTimeout(() => setCopied((c) => (c === name ? null : c)), 1500);
    } catch {
      /* clipboard unavailable */
    }
  };

  const rows = useMemo(() => FORMATS.map((f) => ({ ...f, out: f.wrap(safe) })), [safe]);

  return (
    <div className="mt-8">
      <label className="block">
        <span className="mb-1.5 block text-sm font-medium">Your text</span>
        <input
          value={text}
          onChange={(e) => setText(e.target.value)}
          className="w-full rounded-md border bg-background px-3 py-2.5 text-base outline-none focus:ring-2 focus:ring-primary/40"
          placeholder="Type the text you want to format…"
        />
      </label>

      <div className="mt-5 grid gap-3 sm:grid-cols-2">
        {rows.map((f) => (
          <div key={f.name} className="rounded-xl border bg-card p-4">
            <div className="flex items-center justify-between gap-2">
              <p className="font-medium">{f.name}</p>
              <button
                type="button"
                onClick={() => copy(f.name, f.out)}
                className="inline-flex items-center gap-1.5 rounded-md border px-2.5 py-1 text-xs font-medium hover:bg-muted"
              >
                {copied === f.name ? <Check className="size-3.5 text-emerald-500" /> : <Copy className="size-3.5" />}
                {copied === f.name ? "Copied" : "Copy"}
              </button>
            </div>
            <pre className="mt-2 overflow-x-auto whitespace-pre-wrap break-words rounded-md bg-muted/60 p-2.5 text-sm">{f.out}</pre>
            <p className="mt-1.5 text-xs text-muted-foreground">{f.hint}</p>
          </div>
        ))}
      </div>
    </div>
  );
}
