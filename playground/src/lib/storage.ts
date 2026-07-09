// localStorage-backed persistence: settings (key, target, rates) + run history.
// History survives reloads so you can compare a call before/after a code change.

import { DEFAULT_RATES, type Rates, type SourceGuess } from "./cost";
import type { Target } from "./api";

const SETTINGS_KEY = "captapi.playground.settings.v1";
const HISTORY_KEY = "captapi.playground.history.v1";
const HISTORY_LIMIT = 500;

export interface Settings {
  apiKey: string;
  target: Target;
  rates: Rates;
}

export interface RunRecord {
  id: string;
  at: number; // epoch ms
  tool: string;
  name: string;
  platform: string;
  path: string;
  target: Target;
  params: Record<string, string>;
  status: number;
  ok: boolean;
  durationMs: number;
  credits: number;
  customerPrice: number;
  upstreamCost: number;
  source: SourceGuess;
  itemCount?: number;
  error?: string;
  response: unknown; // full JSON body we got back
  note?: string;
}

export function loadSettings(): Settings {
  try {
    const raw = localStorage.getItem(SETTINGS_KEY);
    if (raw) {
      const parsed = JSON.parse(raw) as Partial<Settings>;
      return {
        apiKey: parsed.apiKey ?? "",
        target: parsed.target ?? "prod",
        rates: { ...DEFAULT_RATES, ...(parsed.rates ?? {}) },
      };
    }
  } catch {
    /* ignore corrupt settings */
  }
  return { apiKey: "", target: "prod", rates: { ...DEFAULT_RATES } };
}

export function saveSettings(s: Settings): void {
  localStorage.setItem(SETTINGS_KEY, JSON.stringify(s));
}

export function loadHistory(): RunRecord[] {
  try {
    const raw = localStorage.getItem(HISTORY_KEY);
    if (raw) return JSON.parse(raw) as RunRecord[];
  } catch {
    /* ignore */
  }
  return [];
}

export function saveHistory(records: RunRecord[]): void {
  localStorage.setItem(HISTORY_KEY, JSON.stringify(records.slice(0, HISTORY_LIMIT)));
}

export function addRecord(records: RunRecord[], rec: RunRecord): RunRecord[] {
  return [rec, ...records].slice(0, HISTORY_LIMIT);
}

export function exportHistory(records: RunRecord[]): void {
  const blob = new Blob([JSON.stringify(records, null, 2)], { type: "application/json" });
  const url = URL.createObjectURL(blob);
  const a = document.createElement("a");
  a.href = url;
  a.download = `captapi-playground-history-${new Date().toISOString().slice(0, 19)}.json`;
  a.click();
  URL.revokeObjectURL(url);
}
