// Copies the canonical endpoint catalog from the MCP package into the
// playground so the console always mirrors the real API surface (tool names,
// paths, credits, exact query params). The source file is pure TS data with no
// imports, so Vite compiles the copy directly. Run via `npm run sync-catalog`
// (also runs automatically before `npm run dev`).
import { mkdirSync, readFileSync, writeFileSync } from "node:fs";
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

// Billing-note guards: Playground params are copied from MCP. When a summary
// promises a special credit rule, the limit helper description must match —
// docs FE and Playground are generated separately; this catches the split.
function assertBillingNotes(catalog) {
  const streamsMatch = catalog.match(
    /tool:\s*"youtube_channel_streams"[\s\S]*?params:\s*\[[\s\S]*?\]/
  );
  if (!streamsMatch) {
    throw new Error("sync-catalog: youtube_channel_streams entry missing");
  }
  const block = streamsMatch[0];
  if (!/0 credits when hasLiveTab/i.test(block)) {
    throw new Error(
      "sync-catalog: youtube_channel_streams summary promises 0-credit empty " +
        "but the params block does not mention '0 credits when hasLiveTab' " +
        "(Playground limit note must use limitFlatOrZeroLiveTab, not limitFlat)."
    );
  }
  if (/Flat 2 credits per call/.test(block) && !/hasLiveTab is false/.test(block)) {
    throw new Error(
      "sync-catalog: youtube_channel_streams still uses plain 'Flat 2 credits " +
        "per call' without the hasLiveTab=false exception."
    );
  }
}

assertBillingNotes(body);

writeFileSync(dest, banner + body, "utf8");

const count = (body.match(/tool:\s*"/g) || []).length;
console.log(`synced catalog -> src/catalog.generated.ts (~${count} endpoints)`);
