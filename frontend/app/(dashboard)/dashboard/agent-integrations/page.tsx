"use client";

import { useEffect, useMemo, useState } from "react";
import { toast } from "sonner";
import {
  Bot,
  Check,
  Copy,
  ExternalLink,
  KeyRound,
  Plug,
  Sparkles,
  Terminal,
} from "lucide-react";
import { Button } from "@/components/ui/button";
import { Input } from "@/components/ui/input";
import { Label } from "@/components/ui/label";
import { Badge } from "@/components/ui/badge";
import { Tabs, TabsContent, TabsList, TabsTrigger } from "@/components/ui/tabs";
import { api } from "@/lib/api-client";
import {
  PLATFORM_GROUPS,
  params as endpointParams,
  mcpToolName,
} from "@/lib/api-catalog";

const PLACEHOLDER = "capt_live_xxxxxxxxxxxxxxxx";

function CodeBlock({ code, label }: { code: string; label?: string }) {
  const [copied, setCopied] = useState(false);
  async function copy() {
    await navigator.clipboard.writeText(code);
    setCopied(true);
    toast.success(`${label ?? "Snippet"} copied`);
    setTimeout(() => setCopied(false), 2000);
  }
  return (
    <div className="relative rounded-xl border bg-zinc-950 text-zinc-100">
      <Button
        type="button"
        size="icon"
        variant="ghost"
        onClick={copy}
        className="absolute right-2 top-2 size-8 text-zinc-400 hover:text-zinc-50 hover:bg-zinc-800"
        title="Copy"
      >
        {copied ? <Check className="size-4" /> : <Copy className="size-4" />}
      </Button>
      <pre className="overflow-x-auto p-4 pr-12 text-xs leading-relaxed">
        <code>{code}</code>
      </pre>
    </div>
  );
}

export default function AgentIntegrationsPage() {
  const [apiKey, setApiKey] = useState("");
  const [hintPrefix, setHintPrefix] = useState<string | null>(null);
  const [toolQuery, setToolQuery] = useState("");

  useEffect(() => {
    api
      .listKeys()
      .then((d) => {
        const active = d.keys.filter((k) => !k.revoked_at);
        if (active[0]) setHintPrefix(active[0].key_prefix);
      })
      .catch(() => {});
  }, []);

  const key = apiKey.trim() || PLACEHOLDER;

  const serverEntry = useMemo(
    () => ({
      command: "npx",
      args: ["-y", "@captapi/mcp"],
      env: { CAPTAPI_API_KEY: key },
    }),
    [key],
  );

  const cursorConfig = useMemo(
    () => JSON.stringify({ mcpServers: { captapi: serverEntry } }, null, 2),
    [serverEntry],
  );
  const claudeConfig = cursorConfig;
  const vscodeConfig = useMemo(
    () => JSON.stringify({ servers: { captapi: serverEntry } }, null, 2),
    [serverEntry],
  );
  const cliInstall = `npm install -g @captapi/mcp\nCAPTAPI_API_KEY=${key} captapi-mcp`;
  const n8nInstall = `# In n8n: Settings -> Community Nodes -> Install\nn8n-nodes-captapi\n\n# Self-hosted (npm), then restart n8n:\nnpm install n8n-nodes-captapi`;
  const makeInstall = `# In Make.com: add the Captapi custom app, then\n# create a "Captapi API Key" connection:\nAPI Key = ${key}\n\n# Drop any module (grouped by platform) into a scenario.`;
  const apifyInstall = `// Run the Captapi Actor on Apify with this input:\n{\n  "apiKey": "${key}",\n  "operation": "youtube_transcript",\n  "url": "https://youtube.com/watch?v=dQw4w9WgXcQ"\n}`;

  const cursorDeeplink = useMemo(() => {
    const b64 =
      typeof window !== "undefined"
        ? window.btoa(JSON.stringify(serverEntry))
        : "";
    return `cursor://anysphere.cursor-deeplink/mcp/install?name=captapi&config=${encodeURIComponent(
      b64,
    )}`;
  }, [serverEntry]);

  const vscodeDeeplink = useMemo(() => {
    const obj = { name: "captapi", ...serverEntry };
    return `vscode:mcp/install?${encodeURIComponent(JSON.stringify(obj))}`;
  }, [serverEntry]);

  const hasKey = Boolean(apiKey.trim());

  function guardInstall(e: React.MouseEvent) {
    if (!hasKey) {
      e.preventDefault();
      toast.error("Paste your Captapi API key first.");
    }
  }

  return (
    <div className="max-w-4xl mx-auto space-y-8">
      {/* Header */}
      <div className="flex items-start gap-3">
        <span className="mt-1 flex size-10 shrink-0 items-center justify-center rounded-xl bg-primary/10 text-primary">
          <Bot className="size-5" />
        </span>
        <div>
          <h1 className="text-3xl font-bold tracking-tight">
            Agent Integrations
          </h1>
          <p className="text-muted-foreground mt-1">
            Wire up Claude, Cursor, VS Code, and any MCP-compatible AI agent to
            all 62 Captapi endpoints in seconds.
          </p>
        </div>
      </div>

      {/* API key */}
      <div className="rounded-2xl border bg-background p-5 space-y-3">
        <div className="flex items-center gap-2">
          <KeyRound className="size-4 text-muted-foreground" />
          <Label htmlFor="mcp-key" className="text-sm font-semibold">
            Your API key
          </Label>
        </div>
        <Input
          id="mcp-key"
          placeholder={PLACEHOLDER}
          value={apiKey}
          onChange={(e) => setApiKey(e.target.value)}
          className="font-mono"
          autoComplete="off"
          spellCheck={false}
        />
        <p className="text-xs text-muted-foreground">
          {hintPrefix ? (
            <>
              Paste the full key for{" "}
              <code className="font-mono">{hintPrefix}••••</code>. Keys are shown
              only once when created — manage them in{" "}
              <a href="/dashboard/api-keys" className="underline">
                API Keys
              </a>
              .
            </>
          ) : (
            <>
              Create a key in{" "}
              <a href="/dashboard/api-keys" className="underline">
                API Keys
              </a>{" "}
              and paste it here. It is embedded into the snippets below and never
              leaves your browser.
            </>
          )}
        </p>
      </div>

      {/* MCP Server */}
      <div className="rounded-2xl border bg-background overflow-hidden">
        <div className="flex items-center gap-2 border-b px-5 py-4">
          <Plug className="size-4 text-primary" />
          <h2 className="font-semibold">MCP Server</h2>
          <Badge variant="outline" className="ml-auto font-mono text-[11px]">
            @captapi/mcp
          </Badge>
        </div>

        <div className="p-5 space-y-4">
          <p className="text-sm text-muted-foreground">
            Direct API access for your agent over the Model Context Protocol.
            Add the config to your client, then ask the agent to fetch
            transcripts, comments, profiles, search results, and more.
          </p>

          <Tabs defaultValue="cursor">
            <TabsList className="flex-wrap h-auto">
              <TabsTrigger value="cursor">Cursor</TabsTrigger>
              <TabsTrigger value="claude">Claude Desktop</TabsTrigger>
              <TabsTrigger value="vscode">VS Code</TabsTrigger>
              <TabsTrigger value="cli">CLI</TabsTrigger>
              <TabsTrigger value="n8n">n8n</TabsTrigger>
              <TabsTrigger value="make">Make.com</TabsTrigger>
              <TabsTrigger value="apify">Apify</TabsTrigger>
            </TabsList>

            <TabsContent value="cursor" className="space-y-3">
              <p className="text-xs text-muted-foreground">
                One-click install, or add to{" "}
                <code className="font-mono">~/.cursor/mcp.json</code>.
              </p>
              <a href={cursorDeeplink} onClick={guardInstall}>
                <Button className="gap-2">
                  <Sparkles className="size-4" /> Install in Cursor
                </Button>
              </a>
              <CodeBlock code={cursorConfig} label="Cursor config" />
            </TabsContent>

            <TabsContent value="claude" className="space-y-3">
              <p className="text-xs text-muted-foreground">
                Settings → Developer → Edit Config, then paste into{" "}
                <code className="font-mono">claude_desktop_config.json</code> and
                restart Claude.
              </p>
              <CodeBlock code={claudeConfig} label="Claude config" />
            </TabsContent>

            <TabsContent value="vscode" className="space-y-3">
              <p className="text-xs text-muted-foreground">
                One-click install, or add to{" "}
                <code className="font-mono">.vscode/mcp.json</code>.
              </p>
              <a href={vscodeDeeplink} onClick={guardInstall}>
                <Button className="gap-2">
                  <ExternalLink className="size-4" /> Install in VS Code
                </Button>
              </a>
              <CodeBlock code={vscodeConfig} label="VS Code config" />
            </TabsContent>

            <TabsContent value="cli" className="space-y-3">
              <p className="text-xs text-muted-foreground">
                Run the server directly from any terminal or container.
              </p>
              <CodeBlock code={cliInstall} label="CLI command" />
            </TabsContent>

            <TabsContent value="n8n" className="space-y-3">
              <p className="text-xs text-muted-foreground">
                For no-code workflows: install the{" "}
                <code className="font-mono">n8n-nodes-captapi</code> community
                node, add a <strong>Captapi API</strong> credential with your
                key, then use the <strong>Captapi</strong> node (Platform →
                Operation) in any workflow.
              </p>
              <CodeBlock code={n8nInstall} label="n8n community node" />
            </TabsContent>

            <TabsContent value="make" className="space-y-3">
              <p className="text-xs text-muted-foreground">
                For no-code scenarios: add the Captapi app in{" "}
                <strong>Make.com</strong>, create a{" "}
                <strong>Captapi API Key</strong> connection with your key, then
                drop any module (grouped by platform) into a scenario — it
                returns the same JSON as the REST API.
              </p>
              <CodeBlock code={makeInstall} label="Make.com app" />
            </TabsContent>

            <TabsContent value="apify" className="space-y-3">
              <p className="text-xs text-muted-foreground">
                On <strong>Apify</strong>: run the Captapi Actor (a
                bring-your-own-key wrapper, no scraping). Set your key as the{" "}
                <code className="font-mono">apiKey</code> input, pick an
                operation, and get one dataset item with the same JSON as the
                REST API.
              </p>
              <CodeBlock code={apifyInstall} label="Apify Actor input" />
            </TabsContent>
          </Tabs>
        </div>
      </div>

      {/* Capabilities */}
      <div className="grid gap-4 sm:grid-cols-3">
        <div className="rounded-2xl border bg-background p-5">
          <Terminal className="size-5 text-primary" />
          <h3 className="mt-3 font-semibold">62 tools</h3>
          <p className="mt-1 text-sm text-muted-foreground">
            Every Captapi endpoint across YouTube, TikTok, Instagram, and
            Facebook, exposed as a typed tool.
          </p>
        </div>
        <div className="rounded-2xl border bg-background p-5">
          <KeyRound className="size-5 text-primary" />
          <h3 className="mt-3 font-semibold">One key</h3>
          <p className="mt-1 text-sm text-muted-foreground">
            No OAuth, no per-platform setup. Credits are billed to your account;
            cached results are free.
          </p>
        </div>
        <div className="rounded-2xl border bg-background p-5">
          <Bot className="size-5 text-primary" />
          <h3 className="mt-3 font-semibold">Any agent</h3>
          <p className="mt-1 text-sm text-muted-foreground">
            Works with Cursor, Claude, VS Code, and any MCP-compatible client
            over stdio.
          </p>
        </div>
      </div>

      {/* Tool reference */}
      <div className="rounded-2xl border bg-background overflow-hidden">
        <div className="flex flex-wrap items-center gap-3 border-b px-5 py-4">
          <Terminal className="size-4 text-primary" />
          <h2 className="font-semibold">Tools &amp; parameters</h2>
          <div className="relative ml-auto w-full max-w-xs">
            <Input
              placeholder="Filter tools…"
              value={toolQuery}
              onChange={(e) => setToolQuery(e.target.value)}
              className="h-9"
            />
          </div>
        </div>

        <div className="p-5 space-y-6">
          <p className="text-sm text-muted-foreground">
            Exactly what each tool expects. Required parameters are marked{" "}
            <span className="font-mono text-rose-500">*</span>. The agent fills
            these in for you — this is just a reference.
          </p>

          {PLATFORM_GROUPS.map((group) => {
            const q = toolQuery.trim().toLowerCase();
            const eps = group.endpoints.filter((ep) => {
              if (!q) return true;
              const tool = mcpToolName(ep).toLowerCase();
              return (
                tool.includes(q) ||
                ep.name.toLowerCase().includes(q) ||
                endpointParams(ep).some((p) => p.name.includes(q))
              );
            });
            if (eps.length === 0) return null;
            return (
              <div key={group.id}>
                <h3 className="mb-2 text-sm font-semibold text-muted-foreground">
                  {group.name}{" "}
                  <span className="font-normal">({eps.length})</span>
                </h3>
                <div className="overflow-hidden rounded-xl border">
                  <table className="w-full text-sm">
                    <tbody className="divide-y">
                      {eps.map((ep) => (
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
                                  {p.required && (
                                    <span className="text-rose-500">*</span>
                                  )}
                                  <span className="text-muted-foreground">
                                    {p.type}
                                  </span>
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
            );
          })}
        </div>
      </div>
    </div>
  );
}
