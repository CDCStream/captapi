/**
 * Sync generated API surface artifacts after router / catalog edits.
 *
 * Run from repo root:
 *   npx tsx scripts/sync-api-surface.mts
 *
 * Steps:
 *   1. dump backend/openapi.snapshot.json
 *   2. regenerate backend/app/services/mcp_catalog.json from packages/captapi-mcp
 *   3. mirror that catalog into Zapier + Apify packages
 *   4. regenerate TS/Python SDKs
 *   5. run catalog parity check (fails on HIGH drift)
 *
 * Does NOT invent MCP/CLI/n8n catalog entries — update those (and
 * frontend/lib/api-catalog.ts + examples/changelog) before running this.
 */

import { spawnSync } from "node:child_process";
import { existsSync, readFileSync, unlinkSync, writeFileSync } from "node:fs";
import { dirname, join, resolve } from "node:path";
import { fileURLToPath } from "node:url";

const HERE = dirname(fileURLToPath(import.meta.url));
const ROOT = resolve(HERE, "..");
const DIRTY = join(ROOT, ".cursor", ".api-surface-dirty");

function run(cmd: string, args: string[], cwd: string): void {
  console.log(`\n>> ${cmd} ${args.join(" ")}  (cwd=${cwd})`);
  const r = spawnSync(cmd, args, { cwd, stdio: "inherit", shell: true });
  if (r.status !== 0) {
    throw new Error(`Command failed (${r.status}): ${cmd} ${args.join(" ")}`);
  }
}

function syncZapierApifyFromMcp(): void {
  const mcpPath = join(ROOT, "backend", "app", "services", "mcp_catalog.json");
  const mcp = JSON.parse(readFileSync(mcpPath, "utf8")) as Array<{
    tool: string;
    params?: unknown;
    summary?: string;
    credits?: number;
  }>;
  const byTool = new Map(mcp.map((r) => [r.tool, r]));

  for (const rel of [
    "packages/captapi-zapier/catalog.json",
    "packages/captapi-apify/src/endpoints.json",
  ]) {
    const p = join(ROOT, rel);
    const data = JSON.parse(readFileSync(p, "utf8")) as Array<Record<string, unknown>>;
    let n = 0;
    for (const row of data) {
      const tool = String(row.tool ?? "");
      const src = byTool.get(tool);
      if (!src) continue;
      row.params = src.params;
      row.summary = src.summary;
      row.credits = src.credits;
      n += 1;
    }
    writeFileSync(p, JSON.stringify(data, null, 2) + "\n", "utf8");
    console.log(`mirrored mcp -> ${rel} (${n} tools updated)`);
  }
}

function clearDirtyMarker(): void {
  if (existsSync(DIRTY)) {
    unlinkSync(DIRTY);
    console.log("cleared .cursor/.api-surface-dirty");
  }
}

function main(): void {
  const py = process.env.PYTHON || "python";
  run(py, ["scripts/dump_openapi.py"], join(ROOT, "backend"));
  run("npx", ["tsx", "scripts/gen-hosted-mcp-catalog.mts"], ROOT);
  syncZapierApifyFromMcp();
  run("npx", ["tsx", "scripts/gen-sdk.mts"], ROOT);
  run("npx", ["tsx", "scripts/check-catalog-parity.mts"], ROOT);
  clearDirtyMarker();
  console.log("\nAPI surface sync OK.");
}

main();
