// Generates copy-paste integration snippets for a chosen endpoint + params,
// matching how each Captapi connector package invokes the REST API:
//   curl, CLI (@captapi/cli), SDK (@captapi/sdk), MCP tool call, Apify actor.
import type { Endpoint } from "../catalog.generated";
import type { Target } from "./api";
import { TARGETS } from "./api";

export type Connector = "curl" | "cli" | "sdk" | "mcp" | "apify";

export const CONNECTORS: { id: Connector; label: string }[] = [
  { id: "curl", label: "cURL" },
  { id: "cli", label: "CLI (@captapi/cli)" },
  { id: "sdk", label: "SDK (@captapi/sdk)" },
  { id: "mcp", label: "MCP tool call" },
  { id: "apify", label: "Apify actor" },
];

function camel(s: string): string {
  return s.replace(/_([a-z0-9])/g, (_, c: string) => c.toUpperCase());
}

/** SDK API group + method, e.g. youtube_video_details -> youtube.videoDetails. */
function sdkCall(e: Endpoint): { group: string; method: string } {
  const group = camel(e.platform);
  const rest = e.tool.startsWith(e.platform + "_")
    ? e.tool.slice(e.platform.length + 1)
    : e.tool;
  return { group, method: camel(rest) || "call" };
}

function cliCommand(tool: string): string {
  return tool.replace(/_/g, "-");
}

function nonEmpty(params: Record<string, string>): [string, string][] {
  return Object.entries(params).filter(([, v]) => v !== undefined && String(v).trim() !== "");
}

function jsLiteral(v: string, type: string): string {
  if (type === "number") return v;
  if (type === "boolean") return v === "true" ? "true" : "false";
  return JSON.stringify(v);
}

function baseUrlFor(target: Target): string {
  // For snippets we always show the real origin (never the Vite proxy path).
  return target === "prod" ? "https://api.captapi.com" : "http://localhost:8000";
}

export function buildSnippet(
  connector: Connector,
  e: Endpoint,
  params: Record<string, string>,
  target: Target,
  apiKey: string,
): string {
  const key = apiKey || "$CAPTAPI_API_KEY";
  const base = baseUrlFor(target);
  const entries = nonEmpty(params);
  const typeOf = (name: string) => e.params.find((p) => p.name === name)?.type ?? "string";

  if (connector === "curl") {
    const qs = entries
      .map(([k, v]) => `${encodeURIComponent(k)}=${encodeURIComponent(v)}`)
      .join("&");
    const url = `${base}${e.path}${qs ? `?${qs}` : ""}`;
    return `curl "${url}" \\\n  -H "Authorization: Bearer ${key}"`;
  }

  if (connector === "cli") {
    const flags = entries
      .map(([k, v]) => (typeOf(k) === "boolean" ? (v === "true" ? `--${k}` : "") : `--${k} ${JSON.stringify(v)}`))
      .filter(Boolean)
      .join(" ");
    return `# npm i -g @captapi/cli ; captapi login\ncaptapi ${cliCommand(e.tool)} ${flags}`.trim();
  }

  if (connector === "sdk") {
    const { group, method } = sdkCall(e);
    const args = entries.map(([k, v]) => `  ${k}: ${jsLiteral(v, typeOf(k))},`).join("\n");
    const baseOpt = target === "prod" ? "" : `, baseUrl: ${JSON.stringify(base)}`;
    return [
      `import { Captapi } from "@captapi/sdk";`,
      ``,
      `const captapi = new Captapi({ apiKey: ${JSON.stringify(key)}${baseOpt} });`,
      ``,
      `const { data } = await captapi.${group}.${method}({`,
      args,
      `});`,
      `console.log(data);`,
    ].join("\n");
  }

  if (connector === "mcp") {
    const argObj: Record<string, string | number | boolean> = {};
    for (const [k, v] of entries) {
      const t = typeOf(k);
      argObj[k] = t === "number" ? Number(v) : t === "boolean" ? v === "true" : v;
    }
    return [
      `// MCP tool call (server: @captapi/mcp)`,
      JSON.stringify({ name: e.tool, arguments: argObj }, null, 2),
    ].join("\n");
  }

  // apify
  const input: Record<string, unknown> = { endpoint: e.path };
  for (const [k, v] of entries) {
    const t = typeOf(k);
    input[k] = t === "number" ? Number(v) : t === "boolean" ? v === "true" : v;
  }
  return [
    `// Apify actor input (actor: captapi/captapi-api)`,
    `// Set CAPTAPI_API_KEY in the actor's env or input.`,
    JSON.stringify(input, null, 2),
  ].join("\n");
}

export { TARGETS };
