"use client";

import { useEffect, useRef, useState } from "react";
import Link from "next/link";
import { usePathname } from "next/navigation";
import {
  ChevronDown,
  Youtube,
  AtSign,
  Cloud,
  Music2,
  Instagram,
  Facebook,
  Github,
  Linkedin,
  Megaphone,
  MessagesSquare,
  Pin,
  ShoppingBag,
  Twitter,
  Video,
  Search,
  LinkIcon,
  Ghost,
  type LucideIcon,
} from "lucide-react";

const ICONS: Record<string, LucideIcon> = {
  youtube: Youtube,
  music: Music2,
  instagram: Instagram,
  facebook: Facebook,
  twitter: Twitter,
  reddit: MessagesSquare,
  threads: AtSign,
  bluesky: Cloud,
  pinterest: Pin,
  linkedin: Linkedin,
  rumble: Video,
  github: Github,
  megaphone: Megaphone,
  shoppingBag: ShoppingBag,
  video: Video,
  cloud: Cloud,
  search: Search,
  link: LinkIcon,
  ghost: Ghost,
};

export interface NavPlatform {
  label: string;
  href: string;
  icon: string;
  color: string;
  endpoints: { name: string; href: string }[];
}

export function ApisNavDropdown({ platforms }: { platforms: NavPlatform[] }) {
  const [open, setOpen] = useState(false);
  const [expanded, setExpanded] = useState<string | null>(null);
  const rootRef = useRef<HTMLDivElement>(null);
  const pathname = usePathname();

  // Close on navigation.
  useEffect(() => {
    setOpen(false);
    setExpanded(null);
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

  return (
    <div ref={rootRef} className="relative">
      <button
        type="button"
        aria-expanded={open}
        aria-haspopup="menu"
        onClick={() => setOpen((v) => !v)}
        className="inline-flex items-center gap-1 text-sm text-muted-foreground transition-colors hover:text-foreground"
      >
        APIs
        <ChevronDown
          className={`size-3.5 transition-transform ${open ? "rotate-180" : ""}`}
        />
      </button>

      {open && (
        <div className="absolute left-0 top-full z-50 mt-3 w-80 overflow-hidden rounded-xl border bg-background shadow-xl">
          <div className="max-h-[70vh] overflow-y-auto p-2">
            <Link
              href="/apis"
              className="block rounded-lg px-3 py-2 text-sm font-medium text-primary transition-colors hover:bg-muted"
            >
              Browse all APIs →
            </Link>
            <div className="my-1 border-t" />
            {platforms.map((p) => {
              const Icon = ICONS[p.icon] ?? Search;
              const isExpanded = expanded === p.href;
              return (
                <div key={p.href}>
                  <div className="flex items-center rounded-lg transition-colors hover:bg-muted">
                    <Link
                      href={p.href}
                      className="flex flex-1 items-center gap-2.5 px-3 py-2 text-sm"
                    >
                      <Icon className={`size-4 shrink-0 ${p.color}`} />
                      <span>{p.label} API</span>
                    </Link>
                    <button
                      type="button"
                      aria-label={
                        isExpanded
                          ? `Collapse ${p.label} endpoints`
                          : `Expand ${p.label} endpoints`
                      }
                      aria-expanded={isExpanded}
                      onClick={() => setExpanded(isExpanded ? null : p.href)}
                      className="mr-1 inline-flex size-7 items-center justify-center rounded-md text-muted-foreground hover:bg-muted-foreground/10 hover:text-foreground"
                    >
                      <ChevronDown
                        className={`size-3.5 transition-transform ${isExpanded ? "rotate-180" : ""}`}
                      />
                    </button>
                  </div>
                  {isExpanded && (
                    <div className="mb-1 ml-6 border-l pl-3">
                      {p.endpoints.map((ep) => (
                        <Link
                          key={ep.href}
                          href={ep.href}
                          className="block rounded-md px-2 py-1.5 text-xs text-muted-foreground transition-colors hover:bg-muted hover:text-foreground"
                        >
                          {ep.name}
                        </Link>
                      ))}
                    </div>
                  )}
                </div>
              );
            })}
          </div>
        </div>
      )}
    </div>
  );
}
