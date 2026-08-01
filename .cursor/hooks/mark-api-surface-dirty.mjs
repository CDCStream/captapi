#!/usr/bin/env node
/**
 * afterFileEdit: mark when API surface source files change so the stop hook
 * can remind the agent to run scripts/sync-api-surface.mts.
 */
import { appendFileSync, mkdirSync } from "node:fs";
import { dirname, join, relative, sep } from "node:path";
import { fileURLToPath } from "node:url";

const ROOT = dirname(dirname(dirname(fileURLToPath(import.meta.url))));
const DIRTY = join(ROOT, ".cursor", ".api-surface-dirty");

const PATTERNS = [
  /^backend[/\\]app[/\\]routers[/\\].+\.py$/i,
  /^backend[/\\]app[/\\]main\.py$/i,
  /^frontend[/\\]lib[/\\]api-catalog\.ts$/i,
  /^frontend[/\\]lib[/\\]api-examples\.generated\.ts$/i,
  /^frontend[/\\]lib[/\\]changelog\.ts$/i,
  /^packages[/\\]captapi-(mcp|cli|n8n)[/\\]src[/\\]catalog\.ts$/i,
];

function readStdin() {
  return new Promise((resolve) => {
    const chunks = [];
    process.stdin.on("data", (c) => chunks.push(c));
    process.stdin.on("end", () => resolve(Buffer.concat(chunks).toString("utf8")));
  });
}

const raw = await readStdin();
let input = {};
try {
  input = JSON.parse(raw || "{}");
} catch {
  /* ignore */
}

const abs = String(input.file_path || "");
if (!abs) process.exit(0);

let rel = abs;
try {
  rel = relative(ROOT, abs).split(sep).join("/");
} catch {
  /* keep abs */
}

const norm = rel.replace(/\\/g, "/");
const hit = PATTERNS.some((re) => re.test(norm));
if (hit) {
  mkdirSync(dirname(DIRTY), { recursive: true });
  appendFileSync(DIRTY, norm + "\n", "utf8");
}
process.exit(0);
