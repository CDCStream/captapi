import Link from "next/link";
import {
  Activity,
  ArrowRight,
  CalendarClock,
  Code2,
  Coins,
  Key,
  PlayCircle,
  Sparkles,
} from "lucide-react";
import { createClient } from "@/lib/supabase/server";
import { Card, CardContent } from "@/components/ui/card";
import { Button } from "@/components/ui/button";
import { Badge } from "@/components/ui/badge";
import { cn, formatNumber } from "@/lib/utils";

export const dynamic = "force-dynamic";

const QUICK_ACTIONS = [
  {
    href: "/dashboard/api-keys",
    icon: Key,
    title: "Create API key",
    desc: "Generate a key to start making requests.",
  },
  {
    href: "/dashboard/playground",
    icon: PlayCircle,
    title: "Open Playground",
    desc: "Test any endpoint right in the browser.",
  },
  {
    href: "/docs",
    icon: Code2,
    title: "Read the docs",
    desc: "Endpoint reference and code examples.",
  },
];

function statusColor(code: number | null | undefined): string {
  if (!code) return "bg-muted-foreground";
  if (code >= 500) return "bg-red-500";
  if (code >= 400) return "bg-amber-500";
  return "bg-green-500";
}

export default async function DashboardOverview() {
  const sb = await createClient();
  const { data: { user } } = await sb.auth.getUser();

  const { data: balance } = await sb
    .from("credit_balances")
    .select("plan, subscription_credits, topup_credits, subscription_renews_at")
    .eq("user_id", user!.id)
    .maybeSingle();

  const { data: recent } = await sb
    .from("requests")
    .select("endpoint, platform, credits_used, cache_hit, status_code, created_at")
    .eq("user_id", user!.id)
    .order("created_at", { ascending: false })
    .limit(10);

  const subCredits = balance?.subscription_credits ?? 0;
  const topupCredits = balance?.topup_credits ?? 0;
  const total = subCredits + topupCredits;
  const subPct = total > 0 ? Math.round((subCredits / total) * 100) : 0;

  const meta = user?.user_metadata ?? {};
  const metaName =
    meta.full_name ||
    meta.name ||
    [meta.first_name, meta.last_name].filter(Boolean).join(" ");
  const name =
    (typeof metaName === "string" && metaName.trim()) ||
    user?.email?.split("@")[0] ||
    "there";
  const renews = balance?.subscription_renews_at
    ? new Date(balance.subscription_renews_at).toLocaleDateString(undefined, {
        month: "short",
        day: "numeric",
        year: "numeric",
      })
    : "—";

  return (
    <div className="max-w-6xl mx-auto space-y-8">
      {/* Header */}
      <div className="flex items-end justify-between flex-wrap gap-4">
        <div>
          <p className="text-sm text-muted-foreground">Welcome back</p>
          <h1 className="text-3xl font-bold tracking-tight capitalize">{name}</h1>
        </div>
        <Badge
          variant="secondary"
          className="uppercase tracking-wider text-xs px-3 py-1"
        >
          {balance?.plan ?? "free"} plan
        </Badge>
      </div>

      {/* Stat cards */}
      <div className="grid gap-5 md:grid-cols-3">
        {/* Credits — highlighted */}
        <Card className="relative overflow-hidden border-primary/20 bg-gradient-to-br from-primary/5 to-transparent">
          <div className="absolute -right-6 -top-6 size-24 rounded-full bg-primary/10 blur-2xl" />
          <CardContent className="p-6">
            <div className="flex items-center gap-2 text-sm text-muted-foreground">
              <span className="flex size-8 items-center justify-center rounded-lg bg-primary/10 text-primary">
                <Coins className="size-4" />
              </span>
              Total credits
            </div>
            <div className="mt-4 text-4xl font-bold tracking-tight">
              {formatNumber(total)}
            </div>
            <div className="mt-4 space-y-2">
              <div className="h-1.5 w-full overflow-hidden rounded-full bg-muted">
                <div
                  className="h-full rounded-full bg-primary transition-all"
                  style={{ width: `${subPct}%` }}
                />
              </div>
              <div className="flex justify-between text-xs text-muted-foreground">
                <span>Subscription {formatNumber(subCredits)}</span>
                <span>Top-up {formatNumber(topupCredits)}</span>
              </div>
            </div>
          </CardContent>
        </Card>

        {/* Requests */}
        <Card>
          <CardContent className="p-6">
            <div className="flex items-center gap-2 text-sm text-muted-foreground">
              <span className="flex size-8 items-center justify-center rounded-lg bg-sky-500/10 text-sky-500">
                <Activity className="size-4" />
              </span>
              Recent requests
            </div>
            <div className="mt-4 text-4xl font-bold tracking-tight">
              {recent?.length ?? 0}
            </div>
            <p className="mt-4 text-xs text-muted-foreground">
              Last 10 calls. Cached hits don&apos;t consume credits.
            </p>
          </CardContent>
        </Card>

        {/* Renews */}
        <Card>
          <CardContent className="p-6">
            <div className="flex items-center gap-2 text-sm text-muted-foreground">
              <span className="flex size-8 items-center justify-center rounded-lg bg-emerald-500/10 text-emerald-500">
                <CalendarClock className="size-4" />
              </span>
              Renews at
            </div>
            <div className="mt-4 text-2xl font-bold tracking-tight">{renews}</div>
            <Button
              asChild
              variant="outline"
              size="sm"
              className="mt-4 w-full"
            >
              <Link href="/dashboard/billing">Manage billing</Link>
            </Button>
          </CardContent>
        </Card>
      </div>

      {/* Quick actions */}
      <div>
        <h2 className="mb-4 flex items-center gap-2 text-sm font-semibold text-muted-foreground">
          <Sparkles className="size-4" /> Quick actions
        </h2>
        <div className="grid gap-5 md:grid-cols-3">
          {QUICK_ACTIONS.map((a) => (
            <Link key={a.href} href={a.href} className="group">
              <Card className="h-full transition-all hover:border-primary/40 hover:shadow-md">
                <CardContent className="flex h-full flex-col p-5">
                  <span className="flex size-10 items-center justify-center rounded-xl bg-primary/10 text-primary">
                    <a.icon className="size-5" />
                  </span>
                  <h3 className="mt-4 font-semibold">{a.title}</h3>
                  <p className="mt-1 text-sm text-muted-foreground">{a.desc}</p>
                  <span className="mt-4 flex items-center gap-1 text-sm font-medium text-primary">
                    Go
                    <ArrowRight className="size-4 transition-transform group-hover:translate-x-1" />
                  </span>
                </CardContent>
              </Card>
            </Link>
          ))}
        </div>
      </div>

      {/* Recent requests */}
      <Card>
        <CardContent className="p-6">
          <div className="mb-4 flex items-center justify-between">
            <h2 className="font-semibold">Recent requests</h2>
            <Button asChild variant="ghost" size="sm">
              <Link href="/dashboard/usage">
                View all <ArrowRight className="ml-1 size-4" />
              </Link>
            </Button>
          </div>
          {(recent ?? []).length === 0 ? (
            <div className="rounded-lg border border-dashed py-12 text-center">
              <p className="text-sm text-muted-foreground">
                No requests yet. Make your first API call to see it here.
              </p>
              <Button asChild size="sm" className="mt-4">
                <Link href="/dashboard/playground">Open Playground</Link>
              </Button>
            </div>
          ) : (
            <div className="divide-y">
              {recent!.map((r, i) => (
                <div
                  key={i}
                  className="flex items-center justify-between gap-3 py-3 text-sm"
                >
                  <div className="flex min-w-0 items-center gap-3">
                    <span
                      className={cn(
                        "size-2 shrink-0 rounded-full",
                        statusColor(r.status_code),
                      )}
                    />
                    <Badge variant="outline" className="font-mono shrink-0">
                      {r.platform}
                    </Badge>
                    <span className="truncate text-muted-foreground">
                      {r.endpoint}
                    </span>
                  </div>
                  <div className="flex shrink-0 items-center gap-3">
                    {r.cache_hit && <Badge variant="success">cache</Badge>}
                    <span className="text-muted-foreground">
                      {r.credits_used} credit{r.credits_used === 1 ? "" : "s"}
                    </span>
                    <span className="hidden text-xs text-muted-foreground sm:inline">
                      {new Date(r.created_at).toLocaleTimeString()}
                    </span>
                  </div>
                </div>
              ))}
            </div>
          )}
        </CardContent>
      </Card>
    </div>
  );
}
