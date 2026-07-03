"use client";

import { useEffect, useState } from "react";
import Link from "next/link";
import { usePathname } from "next/navigation";
import { ChevronDown, Menu, X } from "lucide-react";
import { Button } from "@/components/ui/button";

const LINKS = [
  { href: "/pricing", label: "Pricing" },
  { href: "/tools", label: "Free Tools" },
  { href: "/blog", label: "Blog" },
  { href: "/docs", label: "Docs" },
] as const;

export interface MobileNavPlatform {
  label: string;
  href: string;
}

export function MobileNav({ platforms = [] }: { platforms?: MobileNavPlatform[] }) {
  const [open, setOpen] = useState(false);
  const [apisOpen, setApisOpen] = useState(false);
  const pathname = usePathname();

  // Close on navigation.
  useEffect(() => {
    setOpen(false);
    setApisOpen(false);
  }, [pathname]);

  // Lock body scroll while the menu is open.
  useEffect(() => {
    document.body.style.overflow = open ? "hidden" : "";
    return () => {
      document.body.style.overflow = "";
    };
  }, [open]);

  return (
    <div className="md:hidden">
      <button
        type="button"
        aria-label={open ? "Close menu" : "Open menu"}
        aria-expanded={open}
        onClick={() => setOpen((v) => !v)}
        className="inline-flex size-9 items-center justify-center rounded-md border text-foreground transition-colors hover:bg-muted"
      >
        {open ? <X className="size-5" /> : <Menu className="size-5" />}
      </button>

      {open && (
        <>
          <button
            type="button"
            aria-label="Close menu"
            onClick={() => setOpen(false)}
            className="fixed inset-x-0 bottom-0 top-16 z-40 cursor-default bg-black/20 backdrop-blur-sm"
          />
          <div className="fixed inset-x-0 top-16 z-50 max-h-[calc(100vh-4rem)] overflow-y-auto border-b bg-background p-4 shadow-lg">
            <nav className="flex flex-col gap-1">
              <div className="flex items-center">
                <Link
                  href="/apis"
                  className="flex-1 rounded-md px-3 py-2.5 text-sm font-medium text-muted-foreground transition-colors hover:bg-muted hover:text-foreground"
                >
                  APIs
                </Link>
                {platforms.length > 0 && (
                  <button
                    type="button"
                    aria-label={apisOpen ? "Collapse API list" : "Expand API list"}
                    aria-expanded={apisOpen}
                    onClick={() => setApisOpen((v) => !v)}
                    className="inline-flex size-9 items-center justify-center rounded-md text-muted-foreground hover:bg-muted hover:text-foreground"
                  >
                    <ChevronDown
                      className={`size-4 transition-transform ${apisOpen ? "rotate-180" : ""}`}
                    />
                  </button>
                )}
              </div>
              {apisOpen && (
                <div className="mb-1 ml-3 max-h-64 overflow-y-auto border-l pl-3">
                  {platforms.map((p) => (
                    <Link
                      key={p.href}
                      href={p.href}
                      className="block rounded-md px-2 py-2 text-sm text-muted-foreground transition-colors hover:bg-muted hover:text-foreground"
                    >
                      {p.label} API
                    </Link>
                  ))}
                </div>
              )}
              {LINKS.map((l) => (
                <Link
                  key={l.href}
                  href={l.href}
                  className="rounded-md px-3 py-2.5 text-sm font-medium text-muted-foreground transition-colors hover:bg-muted hover:text-foreground"
                >
                  {l.label}
                </Link>
              ))}
            </nav>
            <div className="mt-3 flex flex-col gap-2 border-t pt-3">
              <Button asChild variant="outline">
                <Link href="/login">Sign in</Link>
              </Button>
              <Button asChild>
                <Link href="/signup">Start Free</Link>
              </Button>
            </div>
          </div>
        </>
      )}
    </div>
  );
}
