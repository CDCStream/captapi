// Generates docs/weekly-endpoint-audit.md — a Notion-paste-ready weekly
// audit checklist of every endpoint, grouped by platform.
// Run: node scripts/generate-audit-checklist.mjs
import fs from "node:fs";
import path from "node:path";
import { fileURLToPath } from "node:url";

const root = path.dirname(path.dirname(fileURLToPath(import.meta.url)));
const src = fs.readFileSync(path.join(root, "frontend/lib/api-catalog.ts"), "utf8");

// Display names, e.g. tiktok_shop -> "TikTok Shop"
const displayNames = {};
const nameBlock = src.match(/PlatformId, string> = \{([\s\S]*?)\};/);
if (nameBlock) {
  for (const m of nameBlock[1].matchAll(/(\w+): "([^"]+)"/g)) {
    displayNames[m[1]] = m[2];
  }
}

// Spec arrays: const YOUTUBE: Spec[] = [ ... ];
const groups = [];
for (const m of src.matchAll(/const ([A-Z_]+): Spec\[\] = \[([\s\S]*?)\n\];/g)) {
  const platformId = m[1].toLowerCase();
  const endpoints = [];
  for (const e of m[2].matchAll(
    /slug: "([^"]+)", name: "([^"]+)", shortName: "([^"]+)", category: "([^"]+)", method: "([^"]+)", path: "([^"]+)"/g,
  )) {
    endpoints.push({ shortName: e[3], method: e[5], path: e[6] });
  }
  if (endpoints.length) {
    groups.push({ id: platformId, name: displayNames[platformId] || platformId, endpoints });
  }
}

const total = groups.reduce((n, g) => n + g.endpoints.length, 0);
const lines = [];
lines.push(`# Captapi Weekly Endpoint Audit`);
lines.push("");
lines.push(`Hafta: ____ | Toplam: ${total} endpoint / ${groups.length} platform`);
lines.push("");
lines.push(`Kontrol: 200 doner mi - JSON alanlari dolu mu - sure makul mu (test URL'leri: docs/example-urls.md)`);
lines.push("");
for (const g of groups) {
  lines.push(`## ${g.name} (${g.endpoints.length})`);
  lines.push("");
  for (const e of g.endpoints) {
    lines.push(`- [ ] ${e.shortName} — \`${e.method} ${e.path}\``);
  }
  lines.push("");
}

const out = path.join(root, "docs/weekly-endpoint-audit.md");
fs.writeFileSync(out, lines.join("\n"), "utf8");
console.log(`wrote ${out}: ${total} endpoints across ${groups.length} platforms`);
