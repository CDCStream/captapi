import { createClient } from "@/lib/supabase/server";
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from "@/components/ui/card";
import { Badge } from "@/components/ui/badge";
import { formatDate, formatNumber } from "@/lib/utils";

export const dynamic = "force-dynamic";

async function sumCreditsUsed(
  sb: Awaited<ReturnType<typeof createClient>>,
  userId: string,
): Promise<number> {
  let sum = 0;
  let from = 0;
  const page = 1000;
  for (;;) {
    const { data } = await sb
      .from("credit_transactions")
      .select("amount")
      .eq("user_id", userId)
      .lt("amount", 0)
      .range(from, from + page - 1);
    if (!data?.length) break;
    sum += data.reduce((s, t) => s + Math.abs(t.amount ?? 0), 0);
    if (data.length < page) break;
    from += page;
  }
  return sum;
}

export default async function UsagePage() {
  const sb = await createClient();
  const { data: { user } } = await sb.auth.getUser();
  const userId = user!.id;

  const [
    { data: txs },
    { data: reqs },
    { count: requestCount },
    { count: cacheHitCount },
    totalUsed,
  ] = await Promise.all([
    sb
      .from("credit_transactions")
      .select("type, amount, description, created_at")
      .eq("user_id", userId)
      .order("created_at", { ascending: false })
      .limit(50),
    sb
      .from("requests")
      .select("endpoint, platform, resource_url, credits_used, cache_hit, status_code, response_time_ms, created_at")
      .eq("user_id", userId)
      .order("created_at", { ascending: false })
      .limit(100),
    sb
      .from("requests")
      .select("*", { count: "exact", head: true })
      .eq("user_id", userId),
    sb
      .from("requests")
      .select("*", { count: "exact", head: true })
      .eq("user_id", userId)
      .eq("cache_hit", true),
    sumCreditsUsed(sb, userId),
  ]);

  return (
    <div className="max-w-6xl mx-auto space-y-8">
      <div>
        <h1 className="text-3xl font-bold">Usage</h1>
        <p className="text-muted-foreground mt-1">Recent requests and credit transactions.</p>
      </div>

      <div className="grid md:grid-cols-3 gap-6">
        <Card>
          <CardHeader className="pb-2">
            <CardDescription>Total credits used (lifetime)</CardDescription>
            <CardTitle className="text-3xl">{formatNumber(totalUsed)}</CardTitle>
          </CardHeader>
        </Card>
        <Card>
          <CardHeader className="pb-2">
            <CardDescription>Requests logged (lifetime)</CardDescription>
            <CardTitle className="text-3xl">{formatNumber(requestCount ?? 0)}</CardTitle>
          </CardHeader>
        </Card>
        <Card>
          <CardHeader className="pb-2">
            <CardDescription>Cache hits (lifetime)</CardDescription>
            <CardTitle className="text-3xl">
              {formatNumber(cacheHitCount ?? 0)}
            </CardTitle>
          </CardHeader>
        </Card>
      </div>

      <Card>
        <CardHeader>
          <CardTitle>Recent requests</CardTitle>
          <CardDescription>Showing the last {reqs?.length ?? 0} requests.</CardDescription>
        </CardHeader>
        <CardContent>
          {(reqs ?? []).length === 0 ? (
            <p className="text-sm text-muted-foreground">No requests yet.</p>
          ) : (
            <div className="space-y-2 max-h-[500px] overflow-y-auto">
              {reqs!.map((r, i) => (
                <div key={i} className="flex items-center justify-between text-sm py-2 border-b last:border-0 gap-3">
                  <div className="flex items-center gap-3 min-w-0 flex-1">
                    <Badge variant="outline">{r.platform}</Badge>
                    <span className="font-mono text-xs truncate">{r.endpoint}</span>
                    {r.resource_url && (
                      <span className="text-xs text-muted-foreground truncate hidden md:inline">{r.resource_url}</span>
                    )}
                  </div>
                  <div className="flex items-center gap-3 text-xs shrink-0">
                    {r.cache_hit && <Badge variant="success">cache</Badge>}
                    <span>{r.response_time_ms}ms</span>
                    <span className="font-medium">{r.credits_used} credit{r.credits_used === 1 ? "" : "s"}</span>
                    <Badge variant={r.status_code && r.status_code < 400 ? "secondary" : "destructive"}>
                      {r.status_code}
                    </Badge>
                  </div>
                </div>
              ))}
            </div>
          )}
        </CardContent>
      </Card>

      <Card>
        <CardHeader>
          <CardTitle>Credit transactions</CardTitle>
          <CardDescription>Showing the last {txs?.length ?? 0} transactions.</CardDescription>
        </CardHeader>
        <CardContent>
          {(txs ?? []).length === 0 ? (
            <p className="text-sm text-muted-foreground">No transactions yet.</p>
          ) : (
            <div className="space-y-2">
              {txs!.map((t, i) => (
                <div key={i} className="flex items-center justify-between text-sm py-2 border-b last:border-0">
                  <div className="flex items-center gap-3 min-w-0">
                    <Badge variant="outline">{t.type}</Badge>
                    <span className="truncate text-muted-foreground">{t.description ?? "—"}</span>
                  </div>
                  <div className="flex items-center gap-3 shrink-0">
                    <span className={t.amount >= 0 ? "text-emerald-600 font-medium" : "text-muted-foreground"}>
                      {t.amount >= 0 ? "+" : ""}{t.amount}
                    </span>
                    <span className="text-xs text-muted-foreground">{formatDate(t.created_at)}</span>
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
