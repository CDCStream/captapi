import type { Metadata } from "next";
import Link from "next/link";
import { CodeTabs } from "@/components/docs/code-tabs";
import {
  PLATFORM_GROUPS,
  API_URL,
  SITE_URL,
  params as endpointParams,
  mcpToolName,
} from "@/lib/api-catalog";

export const metadata: Metadata = {
  title: "Integrations — Captapi MCP Server for AI Agents",
  description:
    "Connect Captapi to Claude, Cursor, VS Code, and any MCP-compatible AI agent. Install the official @captapi/mcp server and give your agent all 62 social media data endpoints.",
  alternates: { canonical: `${SITE_URL}/docs/integrations` },
};

const TOTAL = PLATFORM_GROUPS.reduce((n, g) => n + g.endpoints.length, 0);

const mcpInstall = [
  {
    label: "Cursor",
    code: `// ~/.cursor/mcp.json  (or .cursor/mcp.json per project)
{
  "mcpServers": {
    "captapi": {
      "command": "npx",
      "args": ["-y", "@captapi/mcp"],
      "env": { "CAPTAPI_API_KEY": "capt_live_xxxxxxxxxxxxxxxx" }
    }
  }
}`,
  },
  {
    label: "Claude Desktop",
    code: `// claude_desktop_config.json
{
  "mcpServers": {
    "captapi": {
      "command": "npx",
      "args": ["-y", "@captapi/mcp"],
      "env": { "CAPTAPI_API_KEY": "capt_live_xxxxxxxxxxxxxxxx" }
    }
  }
}`,
  },
  {
    label: "VS Code",
    code: `// .vscode/mcp.json
{
  "servers": {
    "captapi": {
      "command": "npx",
      "args": ["-y", "@captapi/mcp"],
      "env": { "CAPTAPI_API_KEY": "capt_live_xxxxxxxxxxxxxxxx" }
    }
  }
}`,
  },
  {
    label: "CLI",
    code: `npm install -g @captapi/mcp
CAPTAPI_API_KEY=capt_live_xxxxxxxxxxxxxxxx captapi-mcp`,
  },
];

function H2({ id, children }: { id: string; children: React.ReactNode }) {
  return (
    <h2
      id={id}
      className="scroll-mt-24 text-2xl font-bold tracking-tight mt-14 mb-4 first:mt-0"
    >
      {children}
    </h2>
  );
}
function H3({ id, children }: { id: string; children: React.ReactNode }) {
  return (
    <h3 id={id} className="scroll-mt-24 text-lg font-semibold mt-8 mb-3">
      {children}
    </h3>
  );
}

export default function IntegrationsPage() {
  return (
    <div className="prose-docs">
      <p className="text-sm font-medium text-primary mb-2">Integrations</p>
      <H2 id="overview">Overview</H2>
      <p className="text-muted-foreground leading-relaxed max-w-3xl">
        Captapi plugs straight into your AI tooling. The official{" "}
        <a
          href="https://www.npmjs.com/package/@captapi/mcp"
          className="text-primary hover:underline"
          target="_blank"
          rel="noreferrer"
        >
          <code className="rounded bg-muted px-1.5 py-0.5 text-xs">@captapi/mcp</code>
        </a>{" "}
        server exposes all {TOTAL} endpoints as typed tools over the Model
        Context Protocol, so Claude, Cursor, VS Code, and any MCP-compatible
        agent can pull transcripts, comments, profiles, search results, and more
        — billed to your account, with cached results free.
      </p>
      <p className="mt-3 text-muted-foreground max-w-3xl">
        Prefer a one-click setup? Open{" "}
        <Link
          href="/dashboard/agent-integrations"
          className="text-primary hover:underline"
        >
          Agent Integrations
        </Link>{" "}
        in your dashboard for install buttons with your key pre-filled.
      </p>

      <H2 id="mcp">MCP Server</H2>
      <p className="text-muted-foreground max-w-3xl">
        The server runs locally via <code className="rounded bg-muted px-1.5 py-0.5 text-xs">npx</code>{" "}
        and talks to your client over stdio. It needs your Captapi key, which it
        reads from the <code className="rounded bg-muted px-1.5 py-0.5 text-xs">CAPTAPI_API_KEY</code>{" "}
        environment variable.
      </p>

      <H3 id="mcp-install">Installation</H3>
      <p className="text-muted-foreground max-w-3xl mb-4">
        Add the config for your client (replace the key with your own from{" "}
        <Link href="/dashboard/api-keys" className="text-primary hover:underline">
          API Keys
        </Link>
        ), then restart the client.
      </p>
      <CodeTabs samples={mcpInstall} />

      <H3 id="mcp-config">Configuration</H3>
      <div className="overflow-hidden rounded-lg border">
        <table className="w-full text-sm">
          <thead className="bg-muted/50 text-left">
            <tr>
              <th className="px-4 py-2.5 font-medium">Env var</th>
              <th className="px-4 py-2.5 font-medium w-24">Required</th>
              <th className="px-4 py-2.5 font-medium">Description</th>
            </tr>
          </thead>
          <tbody>
            <tr className="border-t">
              <td className="px-4 py-2.5 font-mono text-xs">CAPTAPI_API_KEY</td>
              <td className="px-4 py-2.5 text-muted-foreground">yes</td>
              <td className="px-4 py-2.5 text-muted-foreground">
                Your <code className="rounded bg-muted px-1 py-0.5 text-xs">capt_live_…</code> key.
              </td>
            </tr>
            <tr className="border-t">
              <td className="px-4 py-2.5 font-mono text-xs">CAPTAPI_BASE_URL</td>
              <td className="px-4 py-2.5 text-muted-foreground">no</td>
              <td className="px-4 py-2.5 text-muted-foreground">
                Override the API base URL (default{" "}
                <code className="rounded bg-muted px-1 py-0.5 text-xs">{API_URL}</code>).
              </td>
            </tr>
          </tbody>
        </table>
      </div>

      <H3 id="mcp-tools">Tools &amp; Parameters</H3>
      <p className="text-muted-foreground max-w-3xl mb-4">
        Each endpoint is a tool named{" "}
        <code className="rounded bg-muted px-1.5 py-0.5 text-xs">platform_action</code>.
        Required parameters are marked{" "}
        <span className="font-mono text-rose-500">*</span>. The agent fills these
        in for you.
      </p>

      {PLATFORM_GROUPS.map((group) => (
        <div key={group.id} className="mb-6">
          <p className="mb-2 text-sm font-semibold text-muted-foreground">
            {group.name}{" "}
            <span className="font-normal">({group.endpoints.length})</span>
          </p>
          <div className="overflow-hidden rounded-lg border">
            <table className="w-full text-sm">
              <tbody className="divide-y">
                {group.endpoints.map((ep) => (
                  <tr key={ep.slug} className="align-top">
                    <td className="w-1/3 px-4 py-3">
                      <code className="font-mono text-xs text-primary">
                        {mcpToolName(ep)}
                      </code>
                    </td>
                    <td className="px-4 py-3">
                      <div className="flex flex-wrap gap-1.5">
                        {endpointParams(ep).map((p) => (
                          <span
                            key={p.name}
                            title={p.description}
                            className="inline-flex items-center gap-1 rounded-md border bg-muted/40 px-1.5 py-0.5 font-mono text-[11px]"
                          >
                            {p.name}
                            {p.required && <span className="text-rose-500">*</span>}
                            <span className="text-muted-foreground">{p.type}</span>
                          </span>
                        ))}
                      </div>
                    </td>
                  </tr>
                ))}
              </tbody>
            </table>
          </div>
        </div>
      ))}

      <div className="mt-12 rounded-xl border bg-muted/30 p-6 text-center">
        <p className="font-semibold">Connect your agent in 60 seconds</p>
        <p className="mt-1 text-sm text-muted-foreground">
          Grab a key, paste the config, and start pulling social data from your
          AI tool.
        </p>
        <Link
          href="/dashboard/agent-integrations"
          className="mt-4 inline-flex h-10 items-center rounded-md bg-primary px-5 text-sm font-medium text-primary-foreground hover:opacity-90"
        >
          Open Agent Integrations
        </Link>
      </div>
    </div>
  );
}
