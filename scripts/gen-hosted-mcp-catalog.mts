/**
 * Generates backend/app/services/mcp_catalog.json from the npm MCP catalog
 * (packages/captapi-mcp/src/catalog.ts) so the hosted MCP server always
 * advertises the exact same tools as the published @captapi/mcp package.
 *
 * Run:  npx tsx scripts/gen-hosted-mcp-catalog.mts
 */
import { writeFileSync } from "node:fs";
import { fileURLToPath } from "node:url";
import { dirname, join } from "node:path";

const { ENDPOINTS } = await import("../packages/captapi-mcp/src/catalog.ts");

const root = dirname(dirname(fileURLToPath(import.meta.url)));
const out = join(root, "backend", "app", "services", "mcp_catalog.json");

const data = ENDPOINTS.map((e: any) => ({
  tool: e.tool,
  platform: e.platform,
  name: e.name,
  path: e.path,
  credits: e.credits,
  summary: e.summary,
  params: e.params.map((p: any) => ({
    name: p.name,
    type: p.type,
    required: p.required,
    description: p.description,
  })),
}));

writeFileSync(out, JSON.stringify(data, null, 2) + "\n", "utf-8");
console.log(`wrote ${out} with ${data.length} tools`);
