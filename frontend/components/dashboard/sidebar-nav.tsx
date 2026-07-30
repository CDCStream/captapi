"use client";

import Link from "next/link";
import { usePathname } from "next/navigation";
import { useEffect, useState, type ComponentType } from "react";
import {
  BarChart3,
  Bot,
  ChevronDown,
  CreditCard,
  Filter,
  Key,
  LayoutDashboard,
  LineChart,
  PlayCircle,
  Wrench,
  UserCog,
} from "lucide-react";
import { cn } from "@/lib/utils";
import { TOOL_LIST } from "@/lib/tools";

export const DASHBOARD_NAV = [
  { href: "/dashboard", label: "Overview", icon: LayoutDashboard },
  { href: "/dashboard/api-keys", label: "API Keys", icon: Key },
  { href: "/dashboard/playground", label: "Playground", icon: PlayCircle },
  { href: "/dashboard/usage", label: "Usage", icon: BarChart3 },
  { href: "/dashboard/analytics", label: "Analytics", icon: LineChart },
  { href: "/dashboard/agent-integrations", label: "Agent Integrations", icon: Bot },
  { href: "/dashboard/billing", label: "Billing", icon: CreditCard },
  { href: "/dashboard/account", label: "Account", icon: UserCog },
] as const;

const TOOLS_HREF = "/dashboard/tools";

export function SidebarNav({
  onNavigate,
  showAdminFunnel = false,
}: {
  onNavigate?: () => void;
  showAdminFunnel?: boolean;
}) {
  const pathname = usePathname();
  const toolsActive = pathname.startsWith(TOOLS_HREF);
  const [toolsOpen, setToolsOpen] = useState(toolsActive);

  useEffect(() => {
    if (toolsActive) setToolsOpen(true);
  }, [toolsActive]);

  return (
    <nav className="flex flex-col gap-1">
      {DASHBOARD_NAV.slice(0, 3).map((n) => (
        <NavLink key={n.href} href={n.href} label={n.label} icon={n.icon} pathname={pathname} onNavigate={onNavigate} />
      ))}

      <div>
        <button
          type="button"
          onClick={() => setToolsOpen((o) => !o)}
          className={cn(
            "group flex w-full items-center gap-3 rounded-lg px-3 py-2 text-sm font-medium transition-colors",
            toolsActive
              ? "bg-primary/10 text-primary"
              : "text-muted-foreground hover:bg-muted hover:text-foreground",
          )}
          aria-expanded={toolsOpen}
        >
          <Wrench
            className={cn(
              "size-4 transition-colors",
              toolsActive ? "text-primary" : "text-muted-foreground group-hover:text-foreground",
            )}
          />
          <span className="flex-1 text-left">Tools</span>
          <ChevronDown
            className={cn("size-4 shrink-0 transition-transform", toolsOpen && "rotate-180")}
          />
        </button>
        {toolsOpen && (
          <div className="ml-3 mt-0.5 space-y-0.5 border-l pl-2">
            <Link
              href={TOOLS_HREF}
              onClick={onNavigate}
              className={cn(
                "block rounded-md px-2.5 py-1.5 text-xs font-medium transition-colors",
                pathname === TOOLS_HREF
                  ? "bg-primary/10 text-primary"
                  : "text-muted-foreground hover:bg-muted hover:text-foreground",
              )}
            >
              All tools
            </Link>
            {TOOL_LIST.map((t) => {
              const href = `${TOOLS_HREF}/${t.slug}`;
              const active = pathname === href;
              return (
                <Link
                  key={t.slug}
                  href={href}
                  onClick={onNavigate}
                  className={cn(
                    "block rounded-md px-2.5 py-1.5 text-xs font-medium transition-colors",
                    active
                      ? "bg-primary/10 text-primary"
                      : "text-muted-foreground hover:bg-muted hover:text-foreground",
                  )}
                >
                  {t.shortTitle || t.title}
                </Link>
              );
            })}
          </div>
        )}
      </div>

      {DASHBOARD_NAV.slice(3).map((n) => (
        <NavLink key={n.href} href={n.href} label={n.label} icon={n.icon} pathname={pathname} onNavigate={onNavigate} />
      ))}

      {showAdminFunnel && (
        <NavLink
          href="/dashboard/admin/funnel"
          label="Funnel"
          icon={Filter}
          pathname={pathname}
          onNavigate={onNavigate}
        />
      )}
    </nav>
  );
}

function NavLink({
  href,
  label,
  icon: Icon,
  pathname,
  onNavigate,
}: {
  href: string;
  label: string;
  icon: ComponentType<{ className?: string }>;
  pathname: string;
  onNavigate?: () => void;
}) {
  const active = href === "/dashboard" ? pathname === "/dashboard" : pathname.startsWith(href);
  return (
    <Link
      href={href}
      onClick={onNavigate}
      className={cn(
        "group flex items-center gap-3 rounded-lg px-3 py-2 text-sm font-medium transition-colors",
        active
          ? "bg-primary/10 text-primary"
          : "text-muted-foreground hover:bg-muted hover:text-foreground",
      )}
    >
      <Icon
        className={cn(
          "size-4 transition-colors",
          active ? "text-primary" : "text-muted-foreground group-hover:text-foreground",
        )}
      />
      {label}
    </Link>
  );
}
