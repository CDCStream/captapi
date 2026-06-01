"use client";

import { useMemo, useState } from "react";
import { RotateCcw } from "lucide-react";
import {
  params as getParams,
  exampleValues,
  paramPlaceholder,
  requestSamples,
  type ApiEndpoint,
} from "@/lib/api-catalog";
import { CodeTabs } from "./code-tabs";

export function ApiPlayground({ ep }: { ep: ApiEndpoint }) {
  const eps = useMemo(() => getParams(ep), [ep]);
  const defaults = useMemo(() => exampleValues(ep), [ep]);
  const [values, setValues] = useState<Record<string, string>>(defaults);
  const [apiKey, setApiKey] = useState("");

  const samples = useMemo(
    () => requestSamples(ep, values, apiKey),
    [ep, values, apiKey],
  );

  const set = (name: string, value: string) =>
    setValues((v) => ({ ...v, [name]: value }));

  const reset = () => {
    setValues(defaults);
    setApiKey("");
  };

  return (
    <div className="grid gap-5 lg:grid-cols-2">
      {/* Parameter form */}
      <div className="rounded-xl border bg-card p-5">
        <div className="mb-4 flex items-center justify-between">
          <h3 className="text-sm font-semibold">Parameters</h3>
          <button
            onClick={reset}
            className="inline-flex items-center gap-1.5 rounded-md px-2 py-1 text-xs text-muted-foreground transition-colors hover:bg-muted hover:text-foreground"
          >
            <RotateCcw className="size-3.5" /> Reset
          </button>
        </div>

        <div className="space-y-4">
          {eps.map((p) => {
            const missing = p.required && !values[p.name]?.trim();
            return (
              <label key={p.name} className="block">
                <span className="flex flex-wrap items-center gap-1.5">
                  <code className="font-mono text-xs font-semibold">{p.name}</code>
                  {p.required ? (
                    <span className="text-rose-500" title="Required">
                      *
                    </span>
                  ) : (
                    <span className="text-[10px] uppercase tracking-wide text-muted-foreground">
                      optional
                    </span>
                  )}
                  <span className="text-[11px] text-muted-foreground">{p.type}</span>
                </span>
                <input
                  type={p.type === "integer" || p.type === "number" ? "number" : "text"}
                  inputMode={p.type === "integer" || p.type === "number" ? "numeric" : undefined}
                  value={values[p.name] ?? ""}
                  onChange={(e) => set(p.name, e.target.value)}
                  placeholder={paramPlaceholder(ep, p)}
                  className={`mt-1.5 w-full rounded-md border bg-background px-3 py-2 font-mono text-xs outline-none transition-colors focus:border-primary ${
                    missing ? "border-rose-400/60" : ""
                  }`}
                />
                <span className="mt-1 block text-xs text-muted-foreground">
                  {p.description}
                </span>
              </label>
            );
          })}

          <label className="block border-t pt-4">
            <span className="flex items-center gap-1.5">
              <code className="font-mono text-xs font-semibold">API key</code>
              <span className="text-[10px] uppercase tracking-wide text-muted-foreground">
                optional
              </span>
            </span>
            <input
              type="text"
              value={apiKey}
              onChange={(e) => setApiKey(e.target.value)}
              placeholder="capt_live_..."
              className="mt-1.5 w-full rounded-md border bg-background px-3 py-2 font-mono text-xs outline-none transition-colors focus:border-primary"
            />
            <span className="mt-1 block text-xs text-muted-foreground">
              Paste your key to get a ready-to-run snippet. It stays in your browser.
            </span>
          </label>
        </div>
      </div>

      {/* Live code */}
      <div className="min-w-0">
        <CodeTabs samples={samples} />
        <p className="mt-2 text-xs text-muted-foreground">
          Edit the parameters and the code updates instantly. Switch languages
          and hit copy.
        </p>
      </div>
    </div>
  );
}
