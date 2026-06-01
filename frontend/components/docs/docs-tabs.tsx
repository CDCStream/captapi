"use client";

import Link from "next/link";
import { usePathname } from "next/navigation";
import { cn } from "@/lib/utils";

const TABS = [
  { href: "/docs", label: "API Reference" },
  { href: "/docs/integrations", label: "Integrations" },
];

export function DocsTabs() {
  const pathname = usePathname();
  return (
    <div className="border-b">
      <div className="flex items-center gap-1">
        {TABS.map((t) => {
          const active =
            t.href === "/docs"
              ? pathname === "/docs"
              : pathname.startsWith(t.href);
          return (
            <Link
              key={t.href}
              href={t.href}
              className={cn(
                "relative px-4 py-3 text-sm font-medium transition-colors",
                active
                  ? "text-foreground"
                  : "text-muted-foreground hover:text-foreground",
              )}
            >
              {t.label}
              {active && (
                <span className="absolute inset-x-3 -bottom-px h-0.5 rounded-full bg-primary" />
              )}
            </Link>
          );
        })}
      </div>
    </div>
  );
}
