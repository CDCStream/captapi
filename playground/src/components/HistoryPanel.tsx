import { useMemo, useState } from "react";
import { usd } from "../lib/cost";
import { exportHistory, type RunRecord } from "../lib/storage";

interface Props {
  history: RunRecord[];
  onClear: () => void;
  onDelete: (id: string) => void;
  onNote: (id: string, note: string) => void;
}

export function HistoryPanel({ history, onClear, onDelete, onNote }: Props) {
  const [filter, setFilter] = useState("");
  const [selected, setSelected] = useState<string[]>([]);
  const [openId, setOpenId] = useState<string | null>(null);

  const filtered = useMemo(() => {
    const q = filter.trim().toLowerCase();
    if (!q) return history;
    return history.filter(
      (r) => r.tool.includes(q) || r.platform.includes(q) || r.name.toLowerCase().includes(q),
    );
  }, [history, filter]);

  function toggle(id: string) {
    setSelected((s) =>
      s.includes(id) ? s.filter((x) => x !== id) : [...s, id].slice(-2),
    );
  }

  const compare = selected
    .map((id) => history.find((r) => r.id === id))
    .filter((r): r is RunRecord => Boolean(r));

  return (
    <div className="card history">
      <div className="hist-head">
        <b>History ({history.length})</b>
        <div className="hist-actions">
          <button onClick={() => exportHistory(history)} disabled={!history.length}>
            Export
          </button>
          <button onClick={onClear} disabled={!history.length} className="danger">
            Clear
          </button>
        </div>
      </div>
      <input
        className="filter"
        placeholder="filter by tool / platform"
        value={filter}
        onChange={(e) => setFilter(e.target.value)}
      />

      {compare.length === 2 && <CompareBox a={compare[0]} b={compare[1]} />}

      <div className="hist-list">
        {filtered.length === 0 && <p className="muted">No runs yet.</p>}
        {filtered.map((r) => (
          <div key={r.id} className={`hist-item ${selected.includes(r.id) ? "sel" : ""}`}>
            <div className="hi-top">
              <input
                type="checkbox"
                checked={selected.includes(r.id)}
                onChange={() => toggle(r.id)}
                title="select to compare (max 2)"
              />
              <span className={`badge ${r.ok ? "ok" : "bad"}`}>{r.status || "ERR"}</span>
              <span className="hi-tool">{r.tool}</span>
              <span className="hi-time">{r.durationMs}ms</span>
            </div>
            <div className="hi-meta">
              <span className={`badge ${r.source}`}>{r.source}</span>
              <span>{usd(r.customerPrice)} / {usd(r.upstreamCost)}</span>
              <span className="hi-tgt">{r.target}</span>
              <span className="hi-date">{new Date(r.at).toLocaleTimeString()}</span>
            </div>
            {Object.keys(r.params).length > 0 && (
              <div className="hi-params">
                {Object.entries(r.params)
                  .filter(([, v]) => v)
                  .map(([k, v]) => (
                    <code key={k}>
                      {k}={v}
                    </code>
                  ))}
              </div>
            )}
            <div className="hi-foot">
              <button className="link" onClick={() => setOpenId(openId === r.id ? null : r.id)}>
                {openId === r.id ? "hide json" : "view json"}
              </button>
              <input
                className="note"
                placeholder="note…"
                value={r.note ?? ""}
                onChange={(e) => onNote(r.id, e.target.value)}
              />
              <button className="link danger" onClick={() => onDelete(r.id)}>
                delete
              </button>
            </div>
            {openId === r.id && <pre className="json small">{safeJson(r.response)}</pre>}
          </div>
        ))}
      </div>
    </div>
  );
}

function CompareBox({ a, b }: { a: RunRecord; b: RunRecord }) {
  const dt = b.durationMs - a.durationMs;
  const dc = b.upstreamCost - a.upstreamCost;
  const faster = dt < 0;
  return (
    <div className="compare">
      <b>Compare</b>
      <div className="cmp-row">
        <span>{a.tool}</span>
        <span>{a.durationMs}ms · {usd(a.upstreamCost)}</span>
      </div>
      <div className="cmp-row">
        <span>{b.tool}</span>
        <span>{b.durationMs}ms · {usd(b.upstreamCost)}</span>
      </div>
      <div className={`cmp-delta ${faster ? "good" : "bad"}`}>
        Δ time {dt > 0 ? "+" : ""}
        {dt}ms · Δ our-cost {dc > 0 ? "+" : ""}
        {usd(dc)}
      </div>
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
