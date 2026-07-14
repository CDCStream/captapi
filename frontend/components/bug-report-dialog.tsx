"use client";

import { useState } from "react";
import { usePathname } from "next/navigation";
import { Bug, CheckCircle2 } from "lucide-react";
import { toast } from "sonner";
import { Button } from "@/components/ui/button";
import {
  Dialog,
  DialogContent,
  DialogDescription,
  DialogFooter,
  DialogHeader,
  DialogTitle,
  DialogTrigger,
} from "@/components/ui/dialog";
import { Input } from "@/components/ui/input";
import { Label } from "@/components/ui/label";
import { PLATFORM_GROUPS } from "@/lib/api-catalog";

interface BugReportDialogProps {
  /** Preselects the endpoint — users can still change it. */
  defaultEndpointSlug?: string;
  /** When true the email field is skipped (dashboard users are logged in). */
  loggedIn?: boolean;
  variant?: "outline" | "ghost";
  size?: "sm" | "lg" | "default";
  className?: string;
}

export function BugReportDialog({
  defaultEndpointSlug = "",
  loggedIn = false,
  variant = "outline",
  size = "default",
  className,
}: BugReportDialogProps) {
  const pathname = usePathname();
  const [open, setOpen] = useState(false);
  const [sent, setSent] = useState(false);
  const [endpointSlug, setEndpointSlug] = useState(defaultEndpointSlug);
  const [message, setMessage] = useState("");
  const [email, setEmail] = useState("");
  const [sending, setSending] = useState(false);

  function onOpenChange(next: boolean) {
    setOpen(next);
    if (next) setSent(false);
  }

  async function onSubmit(e: React.FormEvent) {
    e.preventDefault();
    if (message.trim().length < 3) {
      toast.error("Please describe the bug first.");
      return;
    }
    setSending(true);
    try {
      const res = await fetch("/api/bug-report", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({
          endpointSlug: endpointSlug || null,
          message: message.trim(),
          email: email.trim() || null,
          page: pathname,
        }),
      });
      if (!res.ok) {
        const body = (await res.json().catch(() => null)) as { error?: string } | null;
        throw new Error(body?.error || "Failed to send the report.");
      }
      setSent(true);
      setMessage("");
      setEmail("");
      setEndpointSlug(defaultEndpointSlug);
    } catch (err) {
      toast.error(err instanceof Error ? err.message : "Failed to send the report.");
    } finally {
      setSending(false);
    }
  }

  return (
    <Dialog open={open} onOpenChange={onOpenChange}>
      <DialogTrigger asChild>
        <Button variant={variant} size={size} className={className}>
          <Bug className="size-4" />
          Report a bug
        </Button>
      </DialogTrigger>
      <DialogContent className="max-w-md">
        {sent ? (
          <div className="flex flex-col items-center py-6 text-center">
            <span className="flex size-16 items-center justify-center rounded-full bg-emerald-500/10">
              <CheckCircle2 className="size-9 text-emerald-500" />
            </span>
            <h2 className="mt-5 text-xl font-semibold tracking-tight">
              Thanks for your report!
            </h2>
            <p className="mt-2 max-w-xs text-sm leading-relaxed text-muted-foreground">
              We&apos;ve received your bug report and will look into it — we
              fix these as fast as we can.
            </p>
            <Button className="mt-6" onClick={() => setOpen(false)}>
              Done
            </Button>
          </div>
        ) : (
          <>
            <DialogHeader>
              <DialogTitle>Report a bug</DialogTitle>
              <DialogDescription>
                Spotted a wrong response, an error, or something slow? Tell us
                and we&apos;ll look into it.
              </DialogDescription>
            </DialogHeader>
            <form onSubmit={onSubmit} className="space-y-4">
              <div className="space-y-2">
                <Label htmlFor="bug-endpoint">Endpoint (optional)</Label>
                <select
                  id="bug-endpoint"
                  value={endpointSlug}
                  onChange={(e) => setEndpointSlug(e.target.value)}
                  className="flex h-10 w-full rounded-md border border-input bg-background px-3 py-2 text-sm focus-visible:outline-none focus-visible:ring-2 focus-visible:ring-ring focus-visible:ring-offset-2"
                >
                  <option value="">Not endpoint-specific</option>
                  {PLATFORM_GROUPS.map((g) => (
                    <optgroup key={g.id} label={g.name}>
                      {g.endpoints.map((ep) => (
                        <option key={ep.slug} value={ep.slug}>
                          {ep.name.replace(/ API$/, "")}
                        </option>
                      ))}
                    </optgroup>
                  ))}
                </select>
              </div>
              <div className="space-y-2">
                <Label htmlFor="bug-message">What went wrong?</Label>
                <textarea
                  id="bug-message"
                  value={message}
                  onChange={(e) => setMessage(e.target.value)}
                  required
                  minLength={3}
                  maxLength={5000}
                  rows={5}
                  placeholder="Describe the bug — the URL you called, what you expected, and what you got instead."
                  className="flex w-full rounded-md border border-input bg-background px-3 py-2 text-sm placeholder:text-muted-foreground focus-visible:outline-none focus-visible:ring-2 focus-visible:ring-ring focus-visible:ring-offset-2 resize-y"
                />
              </div>
              {!loggedIn && (
                <div className="space-y-2">
                  <Label htmlFor="bug-email">Email (optional)</Label>
                  <Input
                    id="bug-email"
                    type="email"
                    value={email}
                    onChange={(e) => setEmail(e.target.value)}
                    placeholder="you@example.com — only if you want a reply"
                  />
                </div>
              )}
              <DialogFooter>
                <Button type="button" variant="ghost" onClick={() => setOpen(false)}>
                  Cancel
                </Button>
                <Button type="submit" disabled={sending}>
                  {sending ? "Sending…" : "Send report"}
                </Button>
              </DialogFooter>
            </form>
          </>
        )}
      </DialogContent>
    </Dialog>
  );
}
