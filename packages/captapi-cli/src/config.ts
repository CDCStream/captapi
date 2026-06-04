// Local CLI config: stores the API key + base URL under ~/.captapi/config.json.
// Environment variables (CAPTAPI_API_KEY / CAPTAPI_BASE_URL) always win so the
// CLI works in CI without a saved login.
import { homedir } from "node:os";
import { join } from "node:path";
import {
  existsSync,
  mkdirSync,
  readFileSync,
  writeFileSync,
  chmodSync,
} from "node:fs";

export const DEFAULT_BASE_URL = "https://api.captapi.com";

export interface CliConfig {
  apiKey?: string;
  baseUrl?: string;
}

const CONFIG_DIR = join(homedir(), ".captapi");
const CONFIG_FILE = join(CONFIG_DIR, "config.json");

export function configPath(): string {
  return CONFIG_FILE;
}

function readFileConfig(): CliConfig {
  if (!existsSync(CONFIG_FILE)) return {};
  try {
    return JSON.parse(readFileSync(CONFIG_FILE, "utf8")) as CliConfig;
  } catch {
    return {};
  }
}

/** Effective config: env vars override the saved file. */
export function loadConfig(): Required<Pick<CliConfig, "baseUrl">> & CliConfig {
  const file = readFileConfig();
  const apiKey = process.env.CAPTAPI_API_KEY?.trim() || file.apiKey;
  const baseUrl = (
    process.env.CAPTAPI_BASE_URL?.trim() ||
    file.baseUrl ||
    DEFAULT_BASE_URL
  ).replace(/\/$/, "");
  return { apiKey, baseUrl };
}

export function saveConfig(update: CliConfig): void {
  if (!existsSync(CONFIG_DIR)) mkdirSync(CONFIG_DIR, { recursive: true });
  const merged = { ...readFileConfig(), ...update };
  writeFileSync(CONFIG_FILE, JSON.stringify(merged, null, 2) + "\n", "utf8");
  try {
    chmodSync(CONFIG_FILE, 0o600);
  } catch {
    // best-effort on platforms without POSIX perms (Windows)
  }
}

export function clearApiKey(): void {
  const file = readFileConfig();
  delete file.apiKey;
  if (!existsSync(CONFIG_DIR)) mkdirSync(CONFIG_DIR, { recursive: true });
  writeFileSync(CONFIG_FILE, JSON.stringify(file, null, 2) + "\n", "utf8");
}

/** Mask a key for display: capt_live_abcd…wxyz. */
export function maskKey(key: string): string {
  if (key.length <= 14) return key;
  return `${key.slice(0, 10)}…${key.slice(-4)}`;
}
