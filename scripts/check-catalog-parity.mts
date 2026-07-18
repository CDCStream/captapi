/**
 * Catalog parity check.
 *
 * Validates that every published Captapi catalog stays in sync with the REAL
 * backend API surface (path, method, and required query params). It guards
 * against accidental drift like documenting `url` for an endpoint that actually
 * requires `username`/`repo`/`advertiser`.
 *
 * Catalogs checked:
 *   - frontend/lib/api-catalog.ts        (docs, playground, pSEO pages)
 *   - packages/captapi-cli/src/catalog.ts
 *   - packages/captapi-mcp/src/catalog.ts
 *   - packages/captapi-n8n/src/catalog.ts
 *   - backend/app/services/mcp_catalog.json (hosted MCP)
 *   - packages/captapi-zapier/catalog.json
 *   - packages/captapi-apify/src/endpoints.json
 *
 * Source of truth for the backend surface (in priority order):
 *   1. $OPENAPI_URL              e.g. http://127.0.0.1:8000/v1/openapi.json
 *   2. backend/openapi.snapshot.json   (committed; refresh with
 *                                       `python scripts/dump_openapi.py`)
 *
 * Run:  npx tsx scripts/check-catalog-parity.mts
 * Exits non-zero when any HIGH severity mismatch is found.
 */

import { readFileSync, existsSync } from "node:fs";
import { fileURLToPath } from "node:url";
import { dirname, resolve } from "node:path";

const HERE = dirname(fileURLToPath(import.meta.url));
const ROOT = resolve(HERE, "..");

interface BackendOp {
  query: Record<string, boolean>; // name -> required
}
type BackendMap = Record<string, Record<string, BackendOp>>; // path -> METHOD -> op

interface DocEntry {
  id: string;
  path: string;
  method: string;
  params: { name: string; required: boolean }[];
}
interface Issue {
  sev: "HIGH" | "MED";
  catalog: string;
  id: string;
  path: string;
  method: string;
  msg: string;
}

async function loadSpec(): Promise<any> {
  const url = process.env.OPENAPI_URL;
  if (url) {
    const res = await fetch(url);
    if (!res.ok) throw new Error(`OPENAPI_URL returned ${res.status}`);
    return res.json();
  }
  const snap = resolve(ROOT, "backend/openapi.snapshot.json");
  if (!existsSync(snap)) {
    console.error(
      "No backend spec available. Set OPENAPI_URL or run `python scripts/dump_openapi.py` in backend/.",
    );
    process.exit(2);
  }
  return JSON.parse(readFileSync(snap, "utf8"));
}

function buildBackendMap(spec: any): BackendMap {
  const map: BackendMap = {};
  for (const [path, methods] of Object.entries<any>(spec.paths ?? {})) {
    map[path] = {};
    for (const [method, op] of Object.entries<any>(methods)) {
      const query: Record<string, boolean> = {};
      for (const p of op.parameters ?? []) {
        if (p.in === "query") query[p.name] = !!p.required;
      }
      map[path][method.toUpperCase()] = { query };
    }
  }
  return map;
}

function checkCatalog(name: string, entries: DocEntry[], backend: BackendMap): Issue[] {
  const issues: Issue[] = [];
  for (const e of entries) {
    const beForPath = backend[e.path];
    if (!beForPath) {
      issues.push({ sev: "HIGH", catalog: name, id: e.id, path: e.path, method: e.method, msg: "path not found in backend OpenAPI" });
      continue;
    }
    // Prefer the documented method; fall back to the only method present.
    const methods = Object.keys(beForPath);
    const method = beForPath[e.method] ? e.method : methods.length === 1 ? methods[0] : e.method;
    const beOp = beForPath[method];
    if (!beOp) {
      issues.push({ sev: "HIGH", catalog: name, id: e.id, path: e.path, method: e.method, msg: `method ${e.method} not on backend (has: ${methods.join(",")})` });
      continue;
    }
    const docNames = new Set(e.params.map((p) => p.name));
    for (const [pname, required] of Object.entries(beOp.query)) {
      if (required && !docNames.has(pname)) {
        issues.push({ sev: "HIGH", catalog: name, id: e.id, path: e.path, method, msg: `backend REQUIRES query '${pname}' but catalog omits it` });
      }
    }
    for (const p of e.params) {
      if (!(p.name in beOp.query) && method === "GET") {
        issues.push({ sev: "MED", catalog: name, id: e.id, path: e.path, method, msg: `catalog param '${p.name}' not accepted as query by backend` });
      }
    }
  }
  return issues;
}

const spec = await loadSpec();
const backend = buildBackendMap(spec);

// --- Frontend catalog ------------------------------------------------------
const fe = await import("../frontend/lib/api-catalog.ts");
const frontendEntries: DocEntry[] = fe.ALL_ENDPOINTS.map((ep: any) => ({
  id: ep.slug,
  path: ep.path,
  method: ep.method,
  params: fe.params(ep).map((p: any) => ({ name: p.name, required: p.required })),
}));

// --- Package catalogs (no method field -> GET) -----------------------------
async function pkgEntries(rel: string): Promise<DocEntry[]> {
  const mod = await import(rel);
  return mod.ENDPOINTS.map((e: any) => ({
    id: e.tool,
    path: e.path,
    method: "GET",
    params: (e.params ?? []).map((p: any) => ({ name: p.name, required: p.required })),
  }));
}

function jsonCatalogEntries(rel: string, mapItem: (e: any) => DocEntry): DocEntry[] {
  const raw = JSON.parse(readFileSync(resolve(ROOT, rel), "utf8"));
  const list = Array.isArray(raw) ? raw : raw.endpoints ?? Object.values(raw);
  return list.map(mapItem);
}

const catalogs: Record<string, DocEntry[]> = {
  "frontend/lib/api-catalog.ts": frontendEntries,
  "packages/captapi-cli": await pkgEntries("../packages/captapi-cli/src/catalog.ts"),
  "packages/captapi-mcp": await pkgEntries("../packages/captapi-mcp/src/catalog.ts"),
  "packages/captapi-n8n": await pkgEntries("../packages/captapi-n8n/src/catalog.ts"),
  "backend/app/services/mcp_catalog.json": jsonCatalogEntries(
    "backend/app/services/mcp_catalog.json",
    (e) => ({
      id: e.tool,
      path: e.path,
      method: "GET",
      params: (e.params ?? []).map((p: any) => ({ name: p.name, required: !!p.required })),
    }),
  ),
  "packages/captapi-zapier/catalog.json": jsonCatalogEntries(
    "packages/captapi-zapier/catalog.json",
    (e) => ({
      id: e.tool ?? e.key ?? e.name,
      path: e.path,
      method: "GET",
      params: (e.params ?? e.inputFields ?? []).map((p: any) => ({
        name: p.name ?? p.key,
        required: !!p.required,
      })),
    }),
  ),
  "packages/captapi-apify/src/endpoints.json": jsonCatalogEntries(
    "packages/captapi-apify/src/endpoints.json",
    (e) => ({
      id: e.tool ?? e.id ?? e.name,
      path: e.path,
      method: "GET",
      params: (e.params ?? []).map((p: any) => ({ name: p.name, required: !!p.required })),
    }),
  ),
};

let allIssues: Issue[] = [];
console.log(`Backend spec: ${Object.keys(spec.paths ?? {}).length} paths\n`);
for (const [name, entries] of Object.entries(catalogs)) {
  const issues = checkCatalog(name, entries, backend);
  const high = issues.filter((i) => i.sev === "HIGH").length;
  const med = issues.filter((i) => i.sev === "MED").length;
  const status = high ? "FAIL" : med ? "warn" : "ok";
  console.log(`[${status}] ${name}: ${entries.length} endpoints, ${high} high, ${med} med`);
  allIssues = allIssues.concat(issues);
}

const order = { HIGH: 0, MED: 1 } as const;
allIssues.sort((a, b) => order[a.sev] - order[b.sev] || a.catalog.localeCompare(b.catalog));
if (allIssues.length) {
  console.log("\n" + "=".repeat(90));
  for (const i of allIssues) {
    console.log(`[${i.sev}] ${i.catalog} :: ${i.id} (${i.method} ${i.path})\n      ${i.msg}`);
  }
}

const highCount = allIssues.filter((i) => i.sev === "HIGH").length;
console.log("\n" + "=".repeat(90));
if (highCount) {
  console.log(`FAILED: ${highCount} high-severity catalog/API mismatch(es).`);
  process.exit(1);
}
console.log("PASSED: all catalogs match the backend API surface.");
