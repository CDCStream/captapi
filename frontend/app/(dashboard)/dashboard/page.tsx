import Link from "next/link";
import { createClient } from "@/lib/supabase/server";
import { Card, CardContent, CardHeader, CardTitle, CardDescription } from "@/components/ui/card";
import { Button } from "@/components/ui/button";
import { Badge } from "@/components/ui/badge";
import { formatNumber } from "@/lib/utils";
import { Sparkles, Zap, Code2 } from "lucide-react";

export const dynamic = "force-dynamic";

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

  const total = (balance?.subscription_credits ?? 0) + (balance?.topup_credits ?? 0);

  return (
    <div className="max-w-6xl mx-auto space-y-8">
      <div className="flex items-center justify-between flex-wrap gap-4">
        <div>
          <h1 className="text-3xl font-bold">Dashboard</h1>
          <p className="text-muted-foreground mt-1">Welcome back, {user?.email}</p>
        </div>
        <Badge variant="secondary" className="uppercase tracking-wide">
          {balance?.plan ?? "free"} plan
        </Badge>
      </div>

      <div className="grid md:grid-cols-3 gap-6">
        <Card>
          <CardHeader className="pb-2">
            <CardDescription>Total credits</CardDescription>
            <CardTitle className="text-4xl">{formatNumber(total)}</CardTitle>
          </CardHeader>
          <CardContent className="text-sm text-muted-foreground">
            <div>Subscription: {formatNumber(balance?.subscription_credits ?? 0)}</div>
            <div>Top-up: {formatNumber(balance?.topup_credits ?? 0)}</div>
          </CardContent>
        </Card>
        <Card>
          <CardHeader className="pb-2">
            <CardDescription>Requests (24h)</CardDescription>
            <CardTitle className="text-4xl">{recent?.length ?? 0}</CardTitle>
          </CardHeader>
          <CardContent className="text-sm text-muted-foreground">
            Cached hits don&apos;t consume credits.
          </CardContent>
        </Card>
        <Card>
          <CardHeader className="pb-2">
            <CardDescription>Renews at</CardDescription>
            <CardTitle className="text-xl">
              {balance?.subscription_renews_at
                ? new Date(balance.subscription_renews_at).toLocaleDateString()
                : "—"}
            </CardTitle>
          </CardHeader>
          <CardContent>
            <Button asChild variant="outline" size="sm"><Link href="/dashboard/billing">Manage</Link></Button>
          </CardContent>
        </Card>
      </div>

      <div className="grid md:grid-cols-3 gap-6">
        <Card>
          <CardHeader>
            <Sparkles className="size-5 text-primary mb-2" />
            <CardTitle className="text-base">First API key</CardTitle>
            <CardDescription>Create a key to start making requests.</CardDescription>
          </CardHeader>
          <CardContent>
            <Button asChild className="w-full"><Link href="/dashboard/api-keys">Create key</Link></Button>
          </CardContent>
        </Card>
        <Card>
          <CardHeader>
            <Zap className="size-5 text-primary mb-2" />
            <CardTitle className="text-base">Try the Playground</CardTitle>
            <CardDescription>Test endpoints right in the browser.</CardDescription>
          </CardHeader>
          <CardContent>
            <Button asChild variant="outline" className="w-full"><Link href="/dashboard/playground">Open</Link></Button>
          </CardContent>
        </Card>
        <Card>
          <CardHeader>
            <Code2 className="size-5 text-primary mb-2" />
            <CardTitle className="text-base">Read the docs</CardTitle>
            <CardDescription>Endpoint reference + examples.</CardDescription>
          </CardHeader>
          <CardContent>
            <Button asChild variant="outline" className="w-full"><Link href="/docs">View docs</Link></Button>
          </CardContent>
        </Card>
      </div>

      <Card>
        <CardHeader><CardTitle>Recent requests</CardTitle></CardHeader>
        <CardContent>
          {(recent ?? []).length === 0 ? (
            <p className="text-sm text-muted-foreground">No requests yet. Make your first API call to see it here.</p>
          ) : (
            <div className="space-y-2">
              {recent!.map((r, i) => (
                <div key={i} className="flex items-center justify-between text-sm py-2 border-b last:border-0">
                  <div className="flex items-center gap-3 min-w-0">
                    <Badge variant="outline" className="font-mono">{r.platform}</Badge>
                    <span className="truncate text-muted-foreground">{r.endpoint}</span>
                  </div>
                  <div className="flex items-center gap-3 shrink-0">
                    {r.cache_hit && <Badge variant="success">cache</Badge>}
                    <span className="text-muted-foreground">{r.credits_used} cr</span>
                    <span className="text-xs text-muted-foreground">
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
