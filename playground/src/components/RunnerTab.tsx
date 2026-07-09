import { useState } from "react";
import type { Endpoint } from "../catalog.generated";
import { runRequest, type RunResult } from "../lib/api";
import { costBreakdown, usd } from "../lib/cost";
import { guessSource } from "../lib/native";
import type { RunRecord, Settings } from "../lib/storage";

interface Props {
  endpoint: Endpoint;
  params: Record<string, string>;
  settings: Settings;
  onRecord: (rec: RunRecord) => void;
}

/** List endpoints bill per returned item; scale the catalog credit estimate. */
function estimateCredits(e: Endpoint, result: RunResult): number {
  if (result.itemCount && result.itemCount > 0 && e.credits >= 10) {
    // Heuristic: big base_credits => per-item scaled endpoint. Assume the
    // catalog credits reflect the default limit; scale by returned share.
    return Math.max(2, Math.round(result.itemCount * (e.credits / defaultLimit(e))));
  }
  return e.credits;
}

function defaultLimit(e: Endpoint): number {
  const limit = e.params.find((p) => p.name === "limit");
  return limit ? Number((limit.description.match(/\d+/) || [])[0] || 20) : 1;
}

export function RunnerTab({ endpoint, params, settings, onRecord }: Props) {
  const [busy, setBusy] = useState(false);
  const [result, setResult] = useState<RunResult | null>(null);

  const missingRequired = endpoint.params
    .filter((p) => p.required)
    .filter((p) => !params[p.name] || params[p.name].trim() === "")
    .map((p) => p.name);

  async function run() {
    if (!settings.apiKey) {
      alert("Set your API key in the top bar first.");
      return;
    }
    setBusy(true);
    setResult(null);
    const res = await runRequest(settings.target, settings.apiKey, endpoint.path, params);
    setResult(res);
    setBusy(false);

    // Prefer the real values from the X-Captapi-* headers; fall back to the
    // catalog-based guess for backends that predate the headers.
    const source = res.serverSource ?? guessSource(endpoint);
    const credits = res.serverCredits ?? (res.ok ? estimateCredits(endpoint, res) : 0);
    const cost = costBreakdown(credits, source, settings.rates);
    onRecord({
      id: `${Date.now()}-${Math.random().toString(36).slice(2, 7)}`,
      at: Date.now(),
      tool: endpoint.tool,
      name: endpoint.name,
      platform: endpoint.platform,
      path: endpoint.path,
      target: settings.target,
      params: { ...params },
      status: res.status,
      ok: res.ok,
      durationMs: res.durationMs,
      credits: cost.credits,
      customerPrice: cost.customerPrice,
      upstreamCost: cost.upstreamCost,
      source: cost.source,
      itemCount: res.itemCount,
      error: res.error,
      response: res.body,
    });
  }

  return (
    <div className="card runner">
      <div className="run-row">
        <button className="run" disabled={busy || missingRequired.length > 0} onClick={run}>
          {busy ? "Running…" : `Run → ${settings.target}`}
        </button>
        {missingRequired.length > 0 && (
          <span className="warn">required: {missingRequired.join(", ")}</span>
        )}
      </div>

      {result && (
        <div className="result">
          <div className="stats">
            <Stat label="Status" value={String(result.status || "ERR")} tone={result.ok ? "ok" : "bad"} />
            <Stat label="Time" value={`${result.durationMs} ms`} />
            {result.itemCount !== undefined && <Stat label="Items" value={String(result.itemCount)} />}
            {result.serverSource && (
              <Stat
                label="Source"
                value={result.serverSource}
                tone={result.serverSource === "apify" ? "bad" : "ok"}
              />
            )}
            {result.ok && (
              <>
                <Stat
                  label={result.serverCredits !== undefined ? "Credits" : "Credits (est.)"}
                  value={String(lastCost(result, endpoint, settings).credits)}
                />
                <Stat label="Price (customer)" value={usd(lastCost(result, endpoint, settings).customerPrice)} />
                <Stat
                  label={result.serverSource ? "Our cost" : "Our cost (est.)"}
                  value={usd(lastCost(result, endpoint, settings).upstreamCost)}
                  tone="dim"
                />
              </>
            )}
          </div>
          {result.error && <div className="err">{result.error}</div>}
          <pre className="json">{safeJson(result.body)}</pre>
        </div>
      )}
    </div>
  );
}

function lastCost(result: RunResult, endpoint: Endpoint, settings: Settings) {
  const source = result.serverSource ?? guessSource(endpoint);
  const credits = result.serverCredits ?? (result.ok ? estimateCredits(endpoint, result) : 0);
  return costBreakdown(credits, source, settings.rates);
}

function Stat({ label, value, tone }: { label: string; value: string; tone?: "ok" | "bad" | "dim" }) {
  return (
    <div className={`stat ${tone ?? ""}`}>
      <span className="k">{label}</span>
      <span className="v">{value}</span>
    </div>
  );
}

function safeJson(body: unknown): string {
  try {
    return JSON.stringify(body, null, 2);
  } catch {
    return String(body);
  }
}
