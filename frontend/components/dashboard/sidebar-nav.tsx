"use client";

import Link from "next/link";
import { usePathname } from "next/navigation";
import {
  BarChart3,
  Bot,
  CreditCard,
  Key,
  LayoutDashboard,
  LineChart,
  PlayCircle,
  UserCog,
} from "lucide-react";
import { cn } from "@/lib/utils";

const nav = [
  { href: "/dashboard", label: "Overview", icon: LayoutDashboard },
  { href: "/dashboard/api-keys", label: "API Keys", icon: Key },
  { href: "/dashboard/playground", label: "Playground", icon: PlayCircle },
  { href: "/dashboard/usage", label: "Usage", icon: BarChart3 },
  { href: "/dashboard/analytics", label: "Dashboard", icon: LineChart },
  { href: "/dashboard/agent-integrations", label: "Agent Integrations", icon: Bot },
  { href: "/dashboard/billing", label: "Billing", icon: CreditCard },
  { href: "/dashboard/account", label: "Account", icon: UserCog },
];

export function SidebarNav() {
  const pathname = usePathname();

  return (
    <nav className="flex flex-col gap-1">
      {nav.map((n) => {
        const active =
          n.href === "/dashboard"
            ? pathname === "/dashboard"
            : pathname.startsWith(n.href);
        return (
          <Link
            key={n.href}
            href={n.href}
            className={cn(
              "group flex items-center gap-3 rounded-lg px-3 py-2 text-sm font-medium transition-colors",
              active
                ? "bg-primary/10 text-primary"
                : "text-muted-foreground hover:bg-muted hover:text-foreground",
            )}
          >
            <n.icon
              className={cn(
                "size-4 transition-colors",
                active ? "text-primary" : "text-muted-foreground group-hover:text-foreground",
              )}
            />
            {n.label}
          </Link>
        );
      })}
    </nav>
  );
}
