import Link from "next/link";
import { McpIcon, CliIcon, N8nIcon, MakeIcon, ApifyIcon } from "./integration-icons";

type IntegrationCard = {
  id: string;
  title: string;
  description: string;
  icon: React.ReactNode;
};

function buildCards(total: number): IntegrationCard[] {
  return [
    {
      id: "mcp",
      title: "MCP Server",
      description: `Model Context Protocol server exposing all ${total} endpoints as typed tools for Claude, Cursor, VS Code, and any MCP agent.`,
      icon: <McpIcon className="size-5" />,
    },
    {
      id: "cli",
      title: "CLI",
      description: `Call every one of the ${total} endpoints from your terminal, scripts, or CI — one command, JSON to stdout.`,
      icon: <CliIcon className="size-5" />,
    },
    {
      id: "n8n",
      title: "n8n",
      description: `Community node (n8n-nodes-captapi) that brings all ${total} endpoints into your n8n workflows.`,
      icon: <N8nIcon className="size-5" />,
    },
    {
      id: "make",
      title: "Make.com",
      description: `Custom app with an action module for every endpoint, grouped by platform — no code required.`,
      icon: <MakeIcon className="size-5" />,
    },
    {
      id: "apify",
      title: "Apify Actor",
      description: `Bring-your-own-key Actor that wraps the REST API (no scraping) and returns the same structured JSON.`,
      icon: <ApifyIcon className="size-5" />,
    },
  ];
}

export function IntegrationCards({
  total,
  basePath = "",
}: {
  total: number;
  /** Prefix for the anchor links. Use "/docs/integrations" from other pages, "" on the integrations page itself. */
  basePath?: string;
}) {
  const cards = buildCards(total);
  return (
    <div className="not-prose grid gap-4 sm:grid-cols-2 lg:grid-cols-3">
      {cards.map((c) => (
        <Link
          key={c.id}
          href={`${basePath}#${c.id}`}
          className="group flex flex-col gap-3 rounded-xl border bg-card p-5 transition-colors hover:border-primary/50 hover:bg-muted/40"
        >
          <div className="flex items-center gap-2.5">
            <span className="flex size-9 shrink-0 items-center justify-center rounded-lg border bg-background text-foreground">
              {c.icon}
            </span>
            <span className="font-semibold group-hover:text-primary">{c.title}</span>
          </div>
          <p className="text-sm leading-relaxed text-muted-foreground">{c.description}</p>
        </Link>
      ))}
    </div>
  );
}
