import { useEffect, useMemo, useState } from "react";
import { ENDPOINTS, type Endpoint } from "./catalog.generated";
import { TARGETS, type Target } from "./lib/api";
import {
  addRecord,
  loadHistory,
  loadSettings,
  saveHistory,
  saveSettings,
  type RunRecord,
  type Settings,
} from "./lib/storage";
import { EndpointPicker } from "./components/EndpointPicker";
import { RunnerTab } from "./components/RunnerTab";
import { IntegrationsTab } from "./components/IntegrationsTab";
import { HistoryPanel } from "./components/HistoryPanel";

type Tab = "endpoints" | "integrations";

const PLATFORMS = Array.from(new Set(ENDPOINTS.map((e) => e.platform))).sort();

export function App() {
  const [settings, setSettings] = useState<Settings>(loadSettings);
  const [history, setHistory] = useState<RunRecord[]>(loadHistory);
  const [tab, setTab] = useState<Tab>("endpoints");

  const [platform, setPlatform] = useState<string>(PLATFORMS[0]);
  const endpointsForPlatform = useMemo(
    () => ENDPOINTS.filter((e) => e.platform === platform),
    [platform],
  );
  const [tool, setTool] = useState<string>(endpointsForPlatform[0]?.tool ?? "");
  const endpoint: Endpoint | undefined = useMemo(
    () => ENDPOINTS.find((e) => e.tool === tool) ?? endpointsForPlatform[0],
    [tool, endpointsForPlatform],
  );
  const [params, setParams] = useState<Record<string, string>>({});

  useEffect(() => saveSettings(settings), [settings]);
  useEffect(() => saveHistory(history), [history]);

  // Reset the selected tool + params when platform changes.
  useEffect(() => {
    const first = ENDPOINTS.find((e) => e.platform === platform);
    if (first && !ENDPOINTS.some((e) => e.tool === tool && e.platform === platform)) {
      setTool(first.tool);
    }
  }, [platform]); // eslint-disable-line react-hooks/exhaustive-deps

  // Clear param values when the endpoint changes.
  useEffect(() => setParams({}), [tool]);

  function record(rec: RunRecord) {
    setHistory((h) => addRecord(h, rec));
  }

  return (
    <div className="app">
      <header className="topbar">
        <div className="brand">
          <span className="dot" /> Captapi Playground
        </div>
        <div className="settings">
          <label>
            API key
            <input
              type="password"
              placeholder="capt_live_… / capt_test_…"
              value={settings.apiKey}
              onChange={(e) => setSettings({ ...settings, apiKey: e.target.value })}
            />
          </label>
          <label>
            Target
            <select
              value={settings.target}
              onChange={(e) => setSettings({ ...settings, target: e.target.value as Target })}
            >
              {(Object.keys(TARGETS) as Target[]).map((t) => (
                <option key={t} value={t}>
                  {TARGETS[t].label}
                </option>
              ))}
            </select>
          </label>
          <label>
            $/credit
            <input
              type="number"
              step="0.0001"
              value={settings.rates.costPerCredit}
              onChange={(e) =>
                setSettings({
                  ...settings,
                  rates: { ...settings.rates, costPerCredit: Number(e.target.value) },
                })
              }
            />
          </label>
          <label>
            markup×
            <input
              type="number"
              step="0.1"
              value={settings.rates.markup}
              onChange={(e) =>
                setSettings({
                  ...settings,
                  rates: { ...settings.rates, markup: Number(e.target.value) },
                })
              }
            />
          </label>
        </div>
      </header>

      <div className="tabs">
        <button className={tab === "endpoints" ? "active" : ""} onClick={() => setTab("endpoints")}>
          Endpoints
        </button>
        <button
          className={tab === "integrations" ? "active" : ""}
          onClick={() => setTab("integrations")}
        >
          Integrations
        </button>
        <span className="count">{ENDPOINTS.length} endpoints • {PLATFORMS.length} platforms</span>
      </div>

      <main className="layout">
        <section className="left">
          <EndpointPicker
            platforms={PLATFORMS}
            platform={platform}
            onPlatform={setPlatform}
            endpoints={endpointsForPlatform}
            tool={tool}
            onTool={setTool}
            endpoint={endpoint}
            params={params}
            onParams={setParams}
          />

          {endpoint &&
            (tab === "endpoints" ? (
              <RunnerTab
                endpoint={endpoint}
                params={params}
                settings={settings}
                onRecord={record}
              />
            ) : (
              <IntegrationsTab endpoint={endpoint} params={params} settings={settings} />
            ))}
        </section>

        <aside className="right">
          <HistoryPanel
            history={history}
            onClear={() => setHistory([])}
            onDelete={(id) => setHistory((h) => h.filter((r) => r.id !== id))}
            onNote={(id, note) =>
              setHistory((h) => h.map((r) => (r.id === id ? { ...r, note } : r)))
            }
          />
        </aside>
      </main>
    </div>
  );
}
