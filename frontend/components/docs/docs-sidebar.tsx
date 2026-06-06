"use client";

import { useEffect, useMemo, useState } from "react";
import { usePathname } from "next/navigation";
import { Search, LayoutGrid, Download, Settings2, Wrench, Boxes } from "lucide-react";
import {
  McpIcon,
  CliIcon,
  N8nIcon,
  MakeIcon,
  ApifyIcon,
} from "@/components/docs/integration-icons";

const NAV_ICONS: Record<string, React.ReactNode> = {
  integrations: <Boxes className="size-4" />,
  overview: <LayoutGrid className="size-4" />,
  mcp: <McpIcon className="size-4" />,
  "mcp-install": <Download className="size-4" />,
  "mcp-config": <Settings2 className="size-4" />,
  "mcp-tools": <Wrench className="size-4" />,
  cli: <CliIcon className="size-4" />,
  n8n: <N8nIcon className="size-4" />,
  make: <MakeIcon className="size-4" />,
  apify: <ApifyIcon className="size-4" />,
};

interface NavItem {
  id: string;
  label: string;
  badge?: string;
}
interface NavSection {
  title: string;
  items: NavItem[];
}

export const DOCS_NAV: NavSection[] = [
  {
    title: "Getting Started",
    items: [
      { id: "introduction", label: "Introduction" },
      { id: "quickstart", label: "Quickstart" },
      { id: "authentication", label: "Authentication" },
      { id: "making-requests", label: "Making Requests" },
      { id: "response-format", label: "Response Format" },
      { id: "credits-caching", label: "Credits & Caching" },
      { id: "errors", label: "Errors" },
      { id: "rate-limits", label: "Rate Limits" },
    ],
  },
  {
    title: "API Reference",
    items: [
      { id: "api-youtube", label: "YouTube", badge: "13" },
      { id: "api-tiktok", label: "TikTok", badge: "7" },
      { id: "api-instagram", label: "Instagram", badge: "9" },
      { id: "api-facebook", label: "Facebook", badge: "5" },
      { id: "api-video-files", label: "Video Files", badge: "2" },
    ],
  },
  {
    title: "More",
    items: [{ id: "integrations", label: "Integrations" }],
  },
];

export const INTEGRATIONS_NAV: NavSection[] = [
  {
    title: "Integrations",
    items: [
      { id: "overview", label: "Overview" },
      { id: "mcp", label: "MCP Server" },
      { id: "mcp-install", label: "Installation" },
      { id: "mcp-config", label: "Configuration" },
      { id: "mcp-tools", label: "Tools & Parameters" },
      { id: "cli", label: "Command-line (CLI)" },
      { id: "n8n", label: "Workflow automation (n8n)" },
      { id: "make", label: "No-code scenarios (Make.com)" },
      { id: "apify", label: "Apify Actor" },
    ],
  },
];

function useScrollSpy(ids: string[]) {
  const [active, setActive] = useState<string>(ids[0] ?? "");
  useEffect(() => {
    const observer = new IntersectionObserver(
      (entries) => {
        const visible = entries
          .filter((e) => e.isIntersecting)
          .sort((a, b) => a.boundingClientRect.top - b.boundingClientRect.top);
        if (visible[0]) setActive(visible[0].target.id);
      },
      { rootMargin: "-80px 0px -70% 0px", threshold: 0 },
    );
    ids.forEach((id) => {
      const el = document.getElementById(id);
      if (el) observer.observe(el);
    });
    return () => observer.disconnect();
  }, [ids]);
  return active;
}

export function DocsSidebar() {
  const [query, setQuery] = useState("");
  const pathname = usePathname();
  const nav = pathname.startsWith("/docs/integrations")
    ? INTEGRATIONS_NAV
    : DOCS_NAV;
  const allIds = useMemo(
    () => nav.flatMap((s) => s.items.map((i) => i.id)),
    [nav],
  );
  const active = useScrollSpy(allIds);

  const sections = useMemo(() => {
    if (!query.trim()) return nav;
    const q = query.toLowerCase();
    return nav.map((s) => ({
      ...s,
      items: s.items.filter((i) => i.label.toLowerCase().includes(q)),
    })).filter((s) => s.items.length > 0);
  }, [query, nav]);

  return (
    <aside className="hidden lg:block w-60 shrink-0">
      <div className="sticky top-20 max-h-[calc(100vh-6rem)] overflow-y-auto pr-2 pb-10">
        <div className="relative mb-5">
          <Search className="pointer-events-none absolute left-3 top-1/2 size-4 -translate-y-1/2 text-muted-foreground" />
          <input
            value={query}
            onChange={(e) => setQuery(e.target.value)}
            placeholder="Search docs"
            className="h-9 w-full rounded-md border bg-background pl-9 pr-10 text-sm outline-none focus:border-primary"
          />
          <kbd className="pointer-events-none absolute right-2.5 top-1/2 -translate-y-1/2 rounded border bg-muted px-1.5 py-0.5 text-[10px] font-medium text-muted-foreground">
            ⌘K
          </kbd>
        </div>

        <nav className="space-y-6 text-sm">
          {sections.map((section) => (
            <div key={section.title}>
              <p className="mb-2 px-2 text-xs font-semibold uppercase tracking-wide text-muted-foreground/70">
                {section.title}
              </p>
              <ul className="space-y-0.5">
                {section.items.map((item) => (
                  <li key={item.id}>
                    <a
                      href={`#${item.id}`}
                      className={`flex items-center justify-between rounded-md px-2 py-1.5 transition-colors ${
                        active === item.id
                          ? "bg-primary/10 font-medium text-primary"
                          : "text-muted-foreground hover:bg-muted hover:text-foreground"
                      }`}
                    >
                      <span className="flex items-center gap-2">
                        {NAV_ICONS[item.id] && (
                          <span className="shrink-0">{NAV_ICONS[item.id]}</span>
                        )}
                        {item.label}
                      </span>
                      {item.badge && (
                        <span className="rounded bg-muted px-1.5 py-0.5 text-[10px] text-muted-foreground">
                          {item.badge}
                        </span>
                      )}
                    </a>
                  </li>
                ))}
              </ul>
            </div>
          ))}
          {sections.length === 0 && (
            <p className="px-2 text-muted-foreground">No results.</p>
          )}
        </nav>
      </div>
    </aside>
  );
}
