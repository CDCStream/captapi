import Link from "next/link";
import { CodeTabs } from "@/components/docs/code-tabs";
import { IntegrationCards } from "@/components/docs/integration-cards";
import {
  PLATFORM_GROUPS,
  ENDPOINT_COUNT,
  PLATFORM_COUNT,
  API_URL,
  params as endpointParams,
  mcpToolName,
} from "@/lib/api-catalog";
import { buildMetadata } from "@/lib/seo";

export const metadata = buildMetadata({
  title: "Integrations — Captapi MCP Server for AI Agents",
  description: `Connect Captapi to Claude, Cursor, VS Code, and any MCP-compatible AI agent. Install the official @captapi/mcp server, @captapi/cli, the n8n-nodes-captapi community node, the Make.com app, or the Apify Actor and access all ${ENDPOINT_COUNT} endpoints across ${PLATFORM_COUNT} platforms from your agent, terminal, scripts, n8n, Make.com, or Apify.`,
  path: "/docs/integrations",
});

const TOTAL = PLATFORM_GROUPS.reduce((n, g) => n + g.endpoints.length, 0);

const hostedInstall = [
  {
    label: "Cursor",
    code: `// ~/.cursor/mcp.json  (or .cursor/mcp.json per project)
{
  "mcpServers": {
    "captapi": {
      "url": "${API_URL}/mcp",
      "headers": { "Authorization": "Bearer capt_live_xxxxxxxxxxxxxxxx" }
    }
  }
}`,
  },
  {
    label: "Claude Code",
    code: `claude mcp add --transport http captapi ${API_URL}/mcp \\
  --header "Authorization: Bearer capt_live_xxxxxxxxxxxxxxxx"`,
  },
  {
    label: "VS Code",
    code: `// .vscode/mcp.json
{
  "servers": {
    "captapi": {
      "url": "${API_URL}/mcp",
      "headers": { "Authorization": "Bearer capt_live_xxxxxxxxxxxxxxxx" }
    }
  }
}`,
  },
];

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

const cliUsage = [
  {
    label: "Setup",
    code: `npm install -g @captapi/cli      # or just use: npx @captapi/cli <command>

captapi login                    # paste your capt_live_… key (saved to ~/.captapi/config.json)
captapi whoami                   # confirm the active key
captapi balance                  # remaining credits + recent requests`,
  },
  {
    label: "Call endpoints",
    code: `captapi list                     # every endpoint as a command
captapi list youtube             # filter by platform

captapi youtube-transcript --url "https://youtube.com/watch?v=dQw4w9WgXcQ"
captapi tiktok-channel-details --url "https://tiktok.com/@username"
captapi instagram-channel-posts --url "https://instagram.com/nasa/" --limit 12 | jq '.data'`,
  },
  {
    label: "Wire an agent",
    code: `captapi agent add cursor         # writes ~/.cursor/mcp.json
captapi agent add claude         # writes the Claude Desktop config
captapi agent add cursor --print # print the snippet instead of writing`,
  },
];

const n8nUsage = [
  {
    label: "Install",
    code: `# In n8n: Settings → Community Nodes → Install
n8n-nodes-captapi

# Self-hosted (npm), then restart n8n:
npm install n8n-nodes-captapi`,
  },
  {
    label: "Credential",
    code: `// Create a "Captapi API" credential once:
//   API Key  = capt_live_xxxxxxxxxxxxxxxx   (from /dashboard/api-keys)
//   Base URL = ${API_URL}      (default, rarely changed)
// The credential test calls /v1/account/limits to verify the key.`,
  },
  {
    label: "Use the node",
    code: `// Add the "Captapi" node to any workflow:
//   Platform  = YouTube
//   Operation = YouTube Transcript
//   URL       = https://youtube.com/watch?v=dQw4w9WgXcQ
// Output: structured JSON you can map into later nodes.
// Every one of the ${TOTAL} endpoints is available as an Operation.`,
  },
];

const makeUsage = [
  {
    label: "Connection",
    code: `// Create a "Captapi API Key" connection once:
//   API Key = capt_live_xxxxxxxxxxxxxxxx   (from /dashboard/api-keys)
// Make verifies the key against /v1/account/limits.`,
  },
  {
    label: "Add a module",
    code: `// Modules are grouped by platform (YouTube / TikTok / Instagram / Facebook / X / Reddit / LinkedIn / ...).
// Drop one into a scenario, e.g. "YouTube Transcript":
//   URL = https://youtube.com/watch?v=dQw4w9WgXcQ
// Output: the API "data" payload, ready to map into later modules.
// Every one of the ${TOTAL} endpoints is available as a module.`,
  },
];

const apifyUsage = [
  {
    label: "Input",
    code: `{
  "apiKey": "capt_live_xxxxxxxxxxxxxxxx",
  "operation": "youtube_transcript",
  "url": "https://youtube.com/watch?v=dQw4w9WgXcQ"
}`,
  },
  {
    label: "Output (dataset)",
    code: `{
  "operation": "youtube_transcript",
  "ok": true,
  "cached": false,
  "creditsUsed": 2,
  "data": { /* same payload as the REST API */ }
}`,
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
        in your dashboard for install buttons with your key pre-filled. Agents
        can read the machine-readable manifest at{" "}
        <Link href="/mcp.json" className="text-primary hover:underline">
          /mcp.json
        </Link>
        .
      </p>
      <p className="mt-3 text-muted-foreground max-w-3xl">
        Not using MCP? The same {TOTAL} endpoints are also available as a{" "}
        <a href="#cli" className="text-primary hover:underline">
          CLI
        </a>
        , an{" "}
        <a href="#n8n" className="text-primary hover:underline">
          n8n community node
        </a>
        , a{" "}
        <a href="#make" className="text-primary hover:underline">
          Make.com app
        </a>
        ,         and an{" "}
        <a href="#apify" className="text-primary hover:underline">
          Apify Actor
        </a>{" "}
        — or call the REST API directly.
      </p>

      <div className="mt-6">
        <IntegrationCards total={TOTAL} />
      </div>

      {/* 2-step connect flow */}
      <div className="mt-6 grid gap-4 sm:grid-cols-2">
        <div className="rounded-xl border bg-card p-5">
          <div className="mb-2 flex items-center gap-2">
            <span className="flex size-6 items-center justify-center rounded-full bg-primary/10 text-xs font-bold text-primary">
              1
            </span>
            <h3 className="text-sm font-semibold">A human creates the API key</h3>
          </div>
          <p className="text-sm text-muted-foreground">
            Sign-up and key creation can&apos;t be automated by an agent. Create a{" "}
            <code className="rounded bg-muted px-1 py-0.5 text-xs">capt_live_…</code>{" "}
            key once in{" "}
            <Link href="/dashboard/api-keys" className="text-primary hover:underline">
              API Keys
            </Link>{" "}
            (100 free credits) and hand it to your agent.
          </p>
        </div>
        <div className="rounded-xl border bg-card p-5">
          <div className="mb-2 flex items-center gap-2">
            <span className="flex size-6 items-center justify-center rounded-full bg-primary/10 text-xs font-bold text-primary">
              2
            </span>
            <h3 className="text-sm font-semibold">The agent adds the config</h3>
          </div>
          <p className="text-sm text-muted-foreground">
            Point your agent at this page or at{" "}
            <Link href="/mcp.json" className="text-primary hover:underline">
              /mcp.json
            </Link>
            , paste the snippet below with your key, and restart the client.
          </p>
        </div>
      </div>

      <H2 id="mcp">MCP Server</H2>
      <p className="text-muted-foreground max-w-3xl">
        There are two ways to connect — both expose the same {TOTAL} tools.
        Pick <strong>Hosted</strong> for the fastest setup (no install), or{" "}
        <strong>Local</strong> if you prefer running the package on your machine.
        Replace the key with your own from{" "}
        <Link href="/dashboard/api-keys" className="text-primary hover:underline">
          API Keys
        </Link>
        , then restart the client.
      </p>

      <H3 id="mcp-hosted">Option A — Hosted (no install, just a URL)</H3>
      <p className="text-muted-foreground max-w-3xl mb-4">
        Connect over HTTP to{" "}
        <code className="rounded bg-muted px-1.5 py-0.5 text-xs">{API_URL}/mcp</code>.
        Nothing to install — your key is passed as an{" "}
        <code className="rounded bg-muted px-1.5 py-0.5 text-xs">Authorization</code>{" "}
        header (or <code className="rounded bg-muted px-1.5 py-0.5 text-xs">x-api-key</code>).
        Ideal for agents that can&apos;t run local processes.
      </p>
      <CodeTabs samples={hostedInstall} />

      <H3 id="mcp-local">Option B — Local (npx / stdio)</H3>
      <p className="text-muted-foreground max-w-3xl mb-4">
        Run the official{" "}
        <code className="rounded bg-muted px-1.5 py-0.5 text-xs">@captapi/mcp</code>{" "}
        package via <code className="rounded bg-muted px-1.5 py-0.5 text-xs">npx</code>.
        It talks to your client over stdio and reads your key from the{" "}
        <code className="rounded bg-muted px-1.5 py-0.5 text-xs">CAPTAPI_API_KEY</code>{" "}
        environment variable.
      </p>
      <CodeTabs samples={mcpInstall} />

      <H3 id="mcp-config">Configuration (local mode)</H3>
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

      <H2 id="cli">Command-line (CLI)</H2>
      <p className="text-muted-foreground max-w-3xl">
        Prefer the terminal, a shell script, or CI? The official{" "}
        <a
          href="https://www.npmjs.com/package/@captapi/cli"
          className="text-primary hover:underline"
          target="_blank"
          rel="noreferrer"
        >
          <code className="rounded bg-muted px-1.5 py-0.5 text-xs">@captapi/cli</code>
        </a>{" "}
        package exposes all {TOTAL} endpoints as commands. Authenticate once with{" "}
        <code className="rounded bg-muted px-1.5 py-0.5 text-xs">captapi login</code>{" "}
        (or set{" "}
        <code className="rounded bg-muted px-1.5 py-0.5 text-xs">CAPTAPI_API_KEY</code>),
        then call any endpoint — each one is a subcommand, parameters are flags, and
        responses print as JSON to stdout so they pipe cleanly into{" "}
        <code className="rounded bg-muted px-1.5 py-0.5 text-xs">jq</code> and scripts.
        It can even wire the MCP server into your agent with{" "}
        <code className="rounded bg-muted px-1.5 py-0.5 text-xs">captapi agent add</code>.
      </p>
      <div className="mt-4">
        <CodeTabs samples={cliUsage} />
      </div>

      <H2 id="n8n">Workflow automation (n8n)</H2>
      <p className="text-muted-foreground max-w-3xl">
        Building no-code/low-code automations? The official{" "}
        <a
          href="https://www.npmjs.com/package/n8n-nodes-captapi"
          className="text-primary hover:underline"
          target="_blank"
          rel="noreferrer"
        >
          <code className="rounded bg-muted px-1.5 py-0.5 text-xs">n8n-nodes-captapi</code>
        </a>{" "}
        community node brings all {TOTAL} endpoints into{" "}
        <a
          href="https://n8n.io"
          className="text-primary hover:underline"
          target="_blank"
          rel="noreferrer"
        >
          n8n
        </a>
        . Install it from <strong>Settings → Community Nodes</strong>, add a{" "}
        <strong>Captapi API</strong> credential with your{" "}
        <code className="rounded bg-muted px-1.5 py-0.5 text-xs">capt_live_…</code>{" "}
        key, then drop the <strong>Captapi</strong> node into any workflow — pick a{" "}
        platform and operation, and pipe the structured JSON into your other nodes.
      </p>
      <div className="mt-4">
        <CodeTabs samples={n8nUsage} />
      </div>

      <H2 id="make">No-code scenarios (Make.com)</H2>
      <p className="text-muted-foreground max-w-3xl">
        Prefer{" "}
        <a
          href="https://www.make.com"
          className="text-primary hover:underline"
          target="_blank"
          rel="noreferrer"
        >
          Make.com
        </a>{" "}
        (Integromat)? The Captapi custom app exposes all {TOTAL} endpoints as
        action modules grouped by platform. Add a{" "}
        <strong>Captapi API Key</strong> connection with your{" "}
        <code className="rounded bg-muted px-1.5 py-0.5 text-xs">capt_live_…</code>{" "}
        key, then drop the module you need into a scenario — it returns the same
        structured JSON as the REST API for downstream modules.
      </p>
      <div className="mt-4">
        <CodeTabs samples={makeUsage} />
      </div>

      <H2 id="apify">Apify Actor (bring your own key)</H2>
      <p className="text-muted-foreground max-w-3xl">
        Running on{" "}
        <a
          href="https://apify.com"
          className="text-primary hover:underline"
          target="_blank"
          rel="noreferrer"
        >
          Apify
        </a>
        ? The Captapi Actor is a thin bring-your-own-key wrapper around the REST
        API — it does <strong>not</strong> scrape. Set your{" "}
        <code className="rounded bg-muted px-1.5 py-0.5 text-xs">capt_live_…</code>{" "}
        key, pick an operation, and the Actor returns one dataset item with the
        same structured JSON. Credits are billed to your own Captapi account, so
        it stays free to run. Its input and output fields are fully documented,
        so AI agents on{" "}
        <a
          href="https://mcp.apify.com"
          className="text-primary hover:underline"
          target="_blank"
          rel="noreferrer"
        >
          Apify&apos;s MCP server
        </a>{" "}
        can discover and run it too.
      </p>
      <div className="mt-4">
        <CodeTabs samples={apifyUsage} />
      </div>

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
