#!/usr/bin/env node
/**
 * stop: if API surface sources were edited this session and sync artifacts
 * look stale / marker still present, auto-follow-up once to run the sync script.
 */
import { existsSync, readFileSync, unlinkSync } from "node:fs";
import { dirname, join } from "node:path";
import { fileURLToPath } from "node:url";
import { spawnSync } from "node:child_process";

const ROOT = dirname(dirname(dirname(fileURLToPath(import.meta.url))));
const DIRTY = join(ROOT, ".cursor", ".api-surface-dirty");

function readStdin() {
  return new Promise((resolve) => {
    const chunks = [];
    process.stdin.on("data", (c) => chunks.push(c));
    process.stdin.on("end", () => resolve(Buffer.concat(chunks).toString("utf8")));
  });
}

function porcelain() {
  const r = spawnSync("git", ["status", "--porcelain"], {
    cwd: ROOT,
    encoding: "utf8",
    shell: true,
  });
  if (r.status !== 0) return "";
  return r.stdout || "";
}

function linesMatching(status, re) {
  return status
    .split(/\r?\n/)
    .map((l) => l.trimEnd())
    .filter(Boolean)
    .map((l) => l.slice(3).replace(/\\/g, "/"))
    .filter((p) => re.test(p));
}

const raw = await readStdin();
let input = {};
try {
  input = JSON.parse(raw || "{}");
} catch {
  /* ignore */
}

const status = String(input.status || "");
const loopCount = Number(input.loop_count || 0);

if (status !== "completed" || loopCount > 0) {
  console.log("{}");
  process.exit(0);
}

const hasMarker = existsSync(DIRTY);
const git = porcelain();

const sourceDirty = linesMatching(
  git,
  /^(backend\/app\/routers\/.+\.py|backend\/app\/main\.py|frontend\/lib\/api-catalog\.ts|packages\/captapi-(mcp|cli|n8n)\/src\/catalog\.ts)$/,
);
const syncDirty = linesMatching(
  git,
  /^(backend\/openapi\.snapshot\.json|backend\/app\/services\/mcp_catalog\.json|packages\/captapi-sdk\/src\/generated\.ts|packages\/captapi-python\/captapi\/_generated\.py|packages\/captapi-zapier\/catalog\.json|packages\/captapi-apify\/src\/endpoints\.json)$/,
);

// If generated artifacts already changed this turn, treat sync as started and
// clear the marker so we do not nag again.
if (syncDirty.length > 0) {
  if (hasMarker) {
    try {
      unlinkSync(DIRTY);
    } catch {
      /* ignore */
    }
  }
  console.log("{}");
  process.exit(0);
}

const needsSync = hasMarker || sourceDirty.length > 0;

if (!needsSync) {
  console.log("{}");
  process.exit(0);
}

const touched = hasMarker
  ? readFileSync(DIRTY, "utf8").trim().split(/\r?\n/).filter(Boolean)
  : sourceDirty;

const unique = [...new Set(touched)].slice(0, 12);

const msg = [
  "API surface sync incomplete after this turn.",
  "Touched: " + (unique.join(", ") || "router/catalog sources"),
  "",
  "Finish docs sync now (do not stop until parity passes):",
  "1. Update frontend/lib/api-catalog.ts and packages/captapi-mcp, captapi-cli, captapi-n8n catalog.ts (plus api-examples/changelog if response shape changed).",
  "2. Run: npx tsx scripts/sync-api-surface.mts",
  "   (dumps OpenAPI, regenerates hosted MCP + Zapier/Apify mirrors + SDKs, runs check-catalog-parity).",
  "3. If parity fails, fix catalog params to match the backend, then re-run the sync script.",
].join("\n");

console.log(JSON.stringify({ followup_message: msg }));
process.exit(0);
