"use client";

import { useState } from "react";
import { Check, Copy } from "lucide-react";
import { PrismLight as SyntaxHighlighter } from "react-syntax-highlighter";
import { vscDarkPlus } from "react-syntax-highlighter/dist/esm/styles/prism";
import bash from "react-syntax-highlighter/dist/esm/languages/prism/bash";
import python from "react-syntax-highlighter/dist/esm/languages/prism/python";
import javascript from "react-syntax-highlighter/dist/esm/languages/prism/javascript";
import php from "react-syntax-highlighter/dist/esm/languages/prism/php";
import go from "react-syntax-highlighter/dist/esm/languages/prism/go";
import java from "react-syntax-highlighter/dist/esm/languages/prism/java";
import json from "react-syntax-highlighter/dist/esm/languages/prism/json";

SyntaxHighlighter.registerLanguage("bash", bash);
SyntaxHighlighter.registerLanguage("python", python);
SyntaxHighlighter.registerLanguage("javascript", javascript);
SyntaxHighlighter.registerLanguage("php", php);
SyntaxHighlighter.registerLanguage("go", go);
SyntaxHighlighter.registerLanguage("java", java);
SyntaxHighlighter.registerLanguage("json", json);

export interface CodeSample {
  label: string;
  code: string;
  lang?: string;
}

const LANG_BY_LABEL: Record<string, string> = {
  curl: "bash",
  cli: "bash",
  python: "python",
  node: "javascript",
  javascript: "javascript",
  js: "javascript",
  typescript: "javascript",
  php: "php",
  go: "go",
  java: "java",
};

function langFor(s: CodeSample): string {
  if (s.lang) return s.lang;
  const key = s.label.trim().toLowerCase();
  if (LANG_BY_LABEL[key]) return LANG_BY_LABEL[key];
  // Config blocks (Cursor, Claude Desktop, VS Code) and responses are JSON.
  if (s.code.trimStart().startsWith("{") || s.code.trimStart().startsWith("//")) {
    return "json";
  }
  return "text";
}

export function CodeTabs({ samples }: { samples: CodeSample[] }) {
  const [active, setActive] = useState(0);
  const [copied, setCopied] = useState(false);

  const copy = async () => {
    try {
      await navigator.clipboard.writeText(samples[active].code);
      setCopied(true);
      setTimeout(() => setCopied(false), 1500);
    } catch {
      /* clipboard unavailable */
    }
  };

  return (
    <div className="overflow-hidden rounded-xl border border-white/10 bg-[#0d1117] text-sm">
      <div className="flex items-center justify-between border-b border-white/10 bg-white/[0.03] pl-1 pr-2">
        <div className="flex items-center overflow-x-auto">
          {samples.map((s, i) => (
            <button
              key={s.label}
              onClick={() => setActive(i)}
              className={`whitespace-nowrap px-3 py-2.5 text-xs font-medium transition-colors ${
                i === active
                  ? "text-white border-b-2 border-primary"
                  : "text-slate-400 hover:text-slate-200 border-b-2 border-transparent"
              }`}
            >
              {s.label}
            </button>
          ))}
        </div>
        <button
          onClick={copy}
          className="flex shrink-0 items-center gap-1.5 rounded-md px-2 py-1 text-xs text-slate-400 transition-colors hover:bg-white/10 hover:text-white"
          aria-label="Copy code"
        >
          {copied ? (
            <>
              <Check className="size-3.5" /> Copied
            </>
          ) : (
            <>
              <Copy className="size-3.5" /> Copy
            </>
          )}
        </button>
      </div>
      <SyntaxHighlighter
        language={langFor(samples[active])}
        style={vscDarkPlus}
        customStyle={{
          margin: 0,
          background: "transparent",
          padding: "1rem",
          fontSize: "0.8125rem",
          lineHeight: 1.6,
        }}
        codeTagProps={{
          style: { fontFamily: "var(--font-mono, ui-monospace, monospace)" },
        }}
      >
        {samples[active].code}
      </SyntaxHighlighter>
    </div>
  );
}
