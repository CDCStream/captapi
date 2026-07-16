"use client";

import { useState, useCallback, useRef } from "react";
import { Loader2, Copy, Sparkles, RefreshCw } from "lucide-react";
import { toast } from "sonner";

type FieldBase = { name: string; label: string; required?: boolean; help?: string };
export type Field =
  | (FieldBase & { type: "text"; placeholder?: string })
  | (FieldBase & { type: "textarea"; placeholder?: string })
  | (FieldBase & { type: "select"; options: { value: string; label: string }[] });

export interface AiToolConfig {
  slug: string;
  fields: Field[];
  submitLabel?: string;
}

type Item = { title?: string; value: string; meta?: string; fields?: { label: string; value: string }[] };
type Group = { title: string; items: Item[] };
type ApiResult = { text?: string; items?: Item[]; groups?: Group[]; combined?: string };

async function copy(text: string, label = "Copied to clipboard") {
  try {
    await navigator.clipboard.writeText(text);
    toast.success(label);
  } catch {
    toast.error("Couldn't copy — please copy manually.");
  }
}

function CopyButton({ text, label }: { text: string; label?: string }) {
  return (
    <button
      type="button"
      onClick={() => copy(text, label)}
      className="inline-flex shrink-0 items-center gap-1 rounded-md border border-white/15 px-2 py-1 text-xs text-gray-300 transition-colors hover:bg-white/10 hover:text-white"
      aria-label="Copy"
    >
      <Copy className="size-3.5" />
      Copy
    </button>
  );
}

function ItemRow({ item }: { item: Item }) {
  return (
    <div className="flex items-start justify-between gap-3 rounded-lg border border-white/10 bg-white/5 p-3">
      <div className="min-w-0">
        {item.title && <p className="font-medium text-white">{item.title}</p>}
        <p className="break-words text-sm text-gray-200">{item.value}</p>
        {item.fields?.map((f) => (
          <p key={f.label} className="mt-1 text-xs text-gray-400">
            <span className="font-medium text-gray-300">{f.label}:</span> {f.value}
          </p>
        ))}
        {item.meta && <p className="mt-1 text-xs text-gray-500">{item.meta}</p>}
      </div>
      <CopyButton text={item.fields ? [item.title, item.value, ...item.fields.map((f) => `${f.label}: ${f.value}`)].filter(Boolean).join("\n") : item.value} />
    </div>
  );
}

export function AiToolClient({ config }: { config: AiToolConfig }) {
  const initial = Object.fromEntries(
    config.fields.map((f) => [f.name, f.type === "select" ? f.options[0]?.value ?? "" : ""]),
  );
  const [values, setValues] = useState<Record<string, string>>(initial);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const [result, setResult] = useState<ApiResult | null>(null);
  // Ref guard blocks a second submit before React flushes the loading state.
  const inFlight = useRef(false);

  const submit = useCallback(async () => {
    if (inFlight.current) return;
    const missing = config.fields.find((f) => f.required && !values[f.name]?.trim());
    if (missing) {
      toast.error(`Please fill in "${missing.label}".`);
      return;
    }
    inFlight.current = true;
    setLoading(true);
    setError(null);
    try {
      const res = await fetch("/api/ai-generate", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ slug: config.slug, inputs: values }),
      });
      const data = await res.json();
      if (!res.ok) throw new Error(data?.error || "Generation failed. Please try again.");
      setResult(data as ApiResult);
    } catch (e) {
      setError(e instanceof Error ? e.message : "Something went wrong.");
    } finally {
      setLoading(false);
      inFlight.current = false;
    }
  }, [config, values]);

  return (
    <div className="mt-8 grid gap-6 lg:grid-cols-[minmax(0,380px)_1fr]">
      {/* Form */}
      <div className="rounded-2xl border border-white/10 bg-zinc-950 p-5">
        <div className="space-y-4">
          {config.fields.map((f) => (
            <div key={f.name}>
              <label htmlFor={f.name} className="mb-1.5 block text-sm font-medium text-white">
                {f.label} {f.required && <span className="text-rose-400">*</span>}
              </label>
              {f.type === "textarea" ? (
                <textarea
                  id={f.name}
                  rows={3}
                  placeholder={f.placeholder}
                  value={values[f.name]}
                  onChange={(e) => setValues((v) => ({ ...v, [f.name]: e.target.value }))}
                  className="w-full resize-y rounded-lg border border-white/15 bg-zinc-900 px-3 py-2 text-sm text-white placeholder:text-gray-500 outline-none focus:border-primary"
                />
              ) : f.type === "select" ? (
                <select
                  id={f.name}
                  value={values[f.name]}
                  onChange={(e) => setValues((v) => ({ ...v, [f.name]: e.target.value }))}
                  className="w-full rounded-lg border border-white/15 bg-zinc-900 px-3 py-2 text-sm text-white outline-none focus:border-primary"
                >
                  {f.options.map((o) => (
                    <option key={o.value} value={o.value} className="bg-zinc-900">
                      {o.label}
                    </option>
                  ))}
                </select>
              ) : (
                <input
                  id={f.name}
                  type="text"
                  placeholder={f.placeholder}
                  value={values[f.name]}
                  onChange={(e) => setValues((v) => ({ ...v, [f.name]: e.target.value }))}
                  className="w-full rounded-lg border border-white/15 bg-zinc-900 px-3 py-2 text-sm text-white placeholder:text-gray-500 outline-none focus:border-primary"
                />
              )}
              {f.help && <p className="mt-1 text-xs text-gray-500">{f.help}</p>}
            </div>
          ))}
          <button
            type="button"
            onClick={submit}
            disabled={loading}
            className="inline-flex w-full items-center justify-center gap-2 rounded-lg bg-primary px-4 py-2.5 text-sm font-semibold text-primary-foreground transition-opacity hover:opacity-90 disabled:opacity-60"
          >
            {loading ? <Loader2 className="size-4 animate-spin" /> : <Sparkles className="size-4" />}
            {loading ? "Generating…" : config.submitLabel ?? "Generate"}
          </button>
          <p className="text-center text-xs text-gray-500">Free · no sign-up required</p>
        </div>
      </div>

      {/* Results */}
      <div className="min-h-[240px] rounded-2xl border border-white/10 bg-zinc-950 p-5">
        {!result && !loading && !error && (
          <div className="flex h-full min-h-[200px] flex-col items-center justify-center text-center text-gray-500">
            <Sparkles className="mb-2 size-6" />
            <p className="text-sm">Your results will appear here.</p>
          </div>
        )}
        {loading && (
          <div className="flex h-full min-h-[200px] items-center justify-center text-gray-400">
            <Loader2 className="mr-2 size-5 animate-spin" /> Generating…
          </div>
        )}
        {error && !loading && (
          <div className="flex h-full min-h-[200px] flex-col items-center justify-center text-center">
            <p className="text-sm text-rose-400">{error}</p>
            <button
              type="button"
              onClick={submit}
              className="mt-3 inline-flex items-center gap-1.5 rounded-md border border-white/15 px-3 py-1.5 text-sm text-gray-200 hover:bg-white/10"
            >
              <RefreshCw className="size-3.5" /> Try again
            </button>
          </div>
        )}
        {result && !loading && (
          <div className="space-y-4">
            {result.combined && (
              <div className="flex items-center justify-between gap-3 rounded-lg border border-primary/30 bg-primary/10 p-3">
                <p className="break-words text-sm text-gray-100">{result.combined}</p>
                <CopyButton text={result.combined} label="Copied all" />
              </div>
            )}
            {result.text && (
              <div className="rounded-lg border border-white/10 bg-black/20 p-3">
                <div className="mb-2 flex justify-end">
                  <CopyButton text={result.text} label="Copied" />
                </div>
                <pre className="whitespace-pre-wrap break-words font-sans text-sm text-gray-200">{result.text}</pre>
              </div>
            )}
            {result.items && (
              <div className="space-y-2">
                {result.items.map((it, i) => (
                  <ItemRow key={i} item={it} />
                ))}
              </div>
            )}
            {result.groups?.map((g) => (
              <div key={g.title}>
                <div className="mb-2 flex items-center justify-between">
                  <p className="text-sm font-semibold text-white">{g.title}</p>
                  <CopyButton text={g.items.map((i) => i.value).join(" ")} label={`Copied ${g.title}`} />
                </div>
                <div className="flex flex-wrap gap-2">
                  {g.items.map((it, i) => (
                    <button
                      key={i}
                      type="button"
                      onClick={() => copy(it.value)}
                      className="rounded-full border border-white/15 bg-white/5 px-3 py-1 text-sm text-gray-200 transition-colors hover:bg-white/10"
                    >
                      {it.value}
                    </button>
                  ))}
                </div>
              </div>
            ))}
          </div>
        )}
      </div>
    </div>
  );
}
