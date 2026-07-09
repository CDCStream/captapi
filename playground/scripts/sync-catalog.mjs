// Copies the canonical endpoint catalog from the MCP package into the
// playground so the console always mirrors the real API surface (tool names,
// paths, credits, exact query params). The source file is pure TS data with no
// imports, so Vite compiles the copy directly. Run via `npm run sync-catalog`
// (also runs automatically before `npm run dev`).
import { copyFileSync, mkdirSync, readFileSync, writeFileSync } from "node:fs";
import { dirname, resolve } from "node:path";
import { fileURLToPath } from "node:url";

const here = dirname(fileURLToPath(import.meta.url));
const src = resolve(here, "../../packages/captapi-mcp/src/catalog.ts");
const destDir = resolve(here, "../src");
const dest = resolve(destDir, "catalog.generated.ts");

mkdirSync(destDir, { recursive: true });

const banner =
  "// GENERATED — do not edit. Source: packages/captapi-mcp/src/catalog.ts\n" +
  "// Refresh with: npm run sync-catalog\n\n";

const body = readFileSync(src, "utf8");
writeFileSync(dest, banner + body, "utf8");

const count = (body.match(/tool:\s*"/g) || []).length;
console.log(`synced catalog -> src/catalog.generated.ts (~${count} endpoints)`);
