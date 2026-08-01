"use client";

import Link from "next/link";
import { usePathname } from "next/navigation";
import type { ComponentType } from "react";
import {
  BarChart3,
  Bot,
  CreditCard,
  Filter,
  Key,
  LayoutDashboard,
  LineChart,
  PlayCircle,
  UserCog,
} from "lucide-react";
import { cn } from "@/lib/utils";

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

export function SidebarNav({
  onNavigate,
  showAdminFunnel = false,
}: {
  onNavigate?: () => void;
  showAdminFunnel?: boolean;
}) {
  const pathname = usePathname();

  return (
    <nav className="flex flex-col gap-1">
      {DASHBOARD_NAV.map((n) => (
        <NavLink
          key={n.href}
          href={n.href}
          label={n.label}
          icon={n.icon}
          pathname={pathname}
          onNavigate={onNavigate}
        />
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
