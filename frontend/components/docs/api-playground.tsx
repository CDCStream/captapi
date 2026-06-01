"use client";

import { useEffect, useMemo, useState } from "react";
import { Loader2, Play, RotateCcw, Zap } from "lucide-react";
import {
  params as getParams,
  exampleValues,
  paramPlaceholder,
  requestSamples,
  type ApiEndpoint,
} from "@/lib/api-catalog";
import { CodeTabs } from "./code-tabs";

export interface RunResult {
  status: number;
  body: string;
  ms: number;
}

export function ApiPlayground({
  ep,
  onRun,
}: {
  ep: ApiEndpoint;
  /** When provided, a "Send request" button runs the call and shows the response. Omit for copy-only docs. */
  onRun?: (values: Record<string, string>) => Promise<RunResult | null>;
}) {
  const eps = useMemo(() => getParams(ep), [ep]);
  const defaults = useMemo(() => exampleValues(ep), [ep]);
  const [values, setValues] = useState<Record<string, string>>(defaults);
  const [apiKey, setApiKey] = useState("");
  const [loading, setLoading] = useState(false);
  const [result, setResult] = useState<RunResult | null>(null);

  useEffect(() => {
    setValues(defaults);
    setResult(null);
  }, [ep, defaults]);

  const samples = useMemo(
    () => requestSamples(ep, values, apiKey),
    [ep, values, apiKey],
  );

  const missingRequired = eps.filter((p) => p.required && !values[p.name]?.trim());
  const canRun = missingRequired.length === 0;

  const set = (name: string, value: string) =>
    setValues((v) => ({ ...v, [name]: value }));

  const reset = () => {
    setValues(defaults);
    setApiKey("");
    setResult(null);
  };

  async function send() {
    if (!onRun || !canRun) return;
    setLoading(true);
    try {
      const r = await onRun(values);
      if (r) setResult(r);
    } finally {
      setLoading(false);
    }
  }

  const statusTone = (code: number) =>
    code >= 500
      ? "bg-red-500/10 text-red-600 dark:text-red-400"
      : code >= 400
        ? "bg-amber-500/10 text-amber-600 dark:text-amber-400"
        : "bg-emerald-500/10 text-emerald-600 dark:text-emerald-400";

  return (
    <div className="space-y-5">
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

            {!onRun && (
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
            )}

            {onRun && (
              <div className="border-t pt-4">
                <button
                  onClick={send}
                  disabled={loading || !canRun}
                  className="inline-flex h-10 w-full items-center justify-center gap-2 rounded-md bg-primary px-4 text-sm font-medium text-primary-foreground transition-opacity hover:opacity-90 disabled:opacity-50"
                >
                  {loading ? (
                    <>
                      <Loader2 className="size-4 animate-spin" /> Running…
                    </>
                  ) : (
                    <>
                      <Play className="size-4" /> Send request
                    </>
                  )}
                </button>
                {!canRun && (
                  <p className="mt-2 text-xs text-rose-500">
                    Fill in required field
                    {missingRequired.length > 1 ? "s" : ""}:{" "}
                    {missingRequired.map((p) => p.name).join(", ")}
                  </p>
                )}
              </div>
            )}
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

      {/* Response (run mode only) */}
      {onRun && (
        <div>
          <div className="mb-2 flex items-center gap-2">
            <h3 className="text-sm font-semibold">Response</h3>
            {result && (
              <>
                <span
                  className={`rounded-full px-2.5 py-0.5 text-xs font-semibold ${statusTone(result.status)}`}
                >
                  {result.status} {result.status < 400 ? "OK" : "Error"}
                </span>
                <span className="inline-flex items-center gap-1 text-xs text-muted-foreground">
                  <Zap className="size-3" />
                  {result.ms} ms
                </span>
              </>
            )}
          </div>
          {loading ? (
            <div className="flex items-center justify-center gap-2 rounded-xl border bg-[#0d1117] py-16 text-sm text-slate-400">
              <Loader2 className="size-4 animate-spin" /> Fetching response…
            </div>
          ) : result ? (
            <CodeTabs
              samples={[{ label: `${result.status}`, code: result.body, lang: "json" }]}
            />
          ) : (
            <div className="flex flex-col items-center justify-center gap-2 rounded-xl border bg-[#0d1117] py-16 text-center text-sm text-slate-400">
              <Play className="size-5" />
              Fill in the parameters and hit Send request.
            </div>
          )}
        </div>
      )}
    </div>
  );
}
