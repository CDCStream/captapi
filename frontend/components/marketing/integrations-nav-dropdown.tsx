"use client";

import { useEffect, useRef, useState } from "react";
import Link from "next/link";
import { usePathname } from "next/navigation";
import { Braces, ChevronDown } from "lucide-react";
import {
  McpIcon,
  CliIcon,
  N8nIcon,
  MakeIcon,
  ApifyIcon,
  TypeScriptIcon,
  PythonIcon,
} from "@/components/docs/integration-icons";

export const INTEGRATION_NAV_ITEMS = [
  { label: "MCP Server", note: "Claude, Cursor, VS Code", href: "/docs/integrations#mcp", Icon: McpIcon },
  { label: "TypeScript SDK", note: "@captapi/sdk", href: "/docs/integrations#sdk", Icon: TypeScriptIcon },
  { label: "Python SDK", note: "pip install captapi", href: "/docs/integrations#sdk", Icon: PythonIcon },
  { label: "CLI", note: "@captapi/cli", href: "/docs/integrations#cli", Icon: CliIcon },
  { label: "n8n", note: "n8n-nodes-captapi", href: "/docs/integrations#n8n", Icon: N8nIcon },
  { label: "Make.com", note: "no-code scenarios", href: "/docs/integrations#make", Icon: MakeIcon },
  { label: "Apify Actor", note: "bring your own key", href: "/docs/integrations#apify", Icon: ApifyIcon },
  { label: "REST API", note: "OpenAPI 3 + llms.txt", href: "/docs", Icon: Braces },
] as const;

export function IntegrationsNavDropdown() {
  const [open, setOpen] = useState(false);
  const rootRef = useRef<HTMLDivElement>(null);
  const closeTimer = useRef<ReturnType<typeof setTimeout> | null>(null);
  const pathname = usePathname();

  // Close on navigation.
  useEffect(() => {
    setOpen(false);
  }, [pathname]);

  // Close on outside click / Escape.
  useEffect(() => {
    if (!open) return;
    const onClick = (e: MouseEvent) => {
      if (rootRef.current && !rootRef.current.contains(e.target as Node)) {
        setOpen(false);
      }
    };
    const onKey = (e: KeyboardEvent) => {
      if (e.key === "Escape") setOpen(false);
    };
    document.addEventListener("mousedown", onClick);
    document.addEventListener("keydown", onKey);
    return () => {
      document.removeEventListener("mousedown", onClick);
      document.removeEventListener("keydown", onKey);
    };
  }, [open]);

  const cancelClose = () => {
    if (closeTimer.current) clearTimeout(closeTimer.current);
  };
  const scheduleClose = () => {
    cancelClose();
    closeTimer.current = setTimeout(() => setOpen(false), 150);
  };

  return (
    <div
      ref={rootRef}
      className="relative"
      onMouseEnter={() => {
        cancelClose();
        setOpen(true);
      }}
      onMouseLeave={scheduleClose}
    >
      <Link
        href="/integrations"
        aria-expanded={open}
        aria-haspopup="menu"
        className="inline-flex items-center gap-1 text-sm text-muted-foreground transition-colors hover:text-foreground"
      >
        Integrations
        <ChevronDown
          className={`size-3.5 transition-transform ${open ? "rotate-180" : ""}`}
        />
      </Link>

      {open && (
        <div className="absolute left-0 top-full z-50 mt-3 w-72 overflow-hidden rounded-xl border bg-background shadow-xl">
          <div className="max-h-[70vh] overflow-y-auto p-2">
            <Link
              href="/integrations"
              className="block rounded-lg px-3 py-2 text-sm font-medium text-primary transition-colors hover:bg-muted"
            >
              Browse all integrations →
            </Link>
            <div className="my-1 border-t" />
            {INTEGRATION_NAV_ITEMS.map(({ label, note, href, Icon }) => (
              <Link
                key={label}
                href={href}
                className="flex items-center gap-2.5 rounded-lg px-3 py-2 text-sm transition-colors hover:bg-muted"
              >
                <Icon className="size-4 shrink-0" />
                <span>{label}</span>
                <span className="ml-auto text-xs text-muted-foreground">{note}</span>
              </Link>
            ))}
          </div>
        </div>
      )}
    </div>
  );
}
