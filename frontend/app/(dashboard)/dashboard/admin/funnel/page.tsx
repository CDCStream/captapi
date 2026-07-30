import Link from "next/link";
import { redirect } from "next/navigation";
import { createClient } from "@/lib/supabase/server";
import { getServiceClient } from "@/lib/supabase/admin";
import { isFunnelAdmin } from "@/lib/funnel-admin";
import { loadFunnelOverview, loadFunnelUsers } from "@/lib/funnel-data";
import { FunnelUsersTable } from "@/components/admin/funnel-users-table";

export const dynamic = "force-dynamic";

export default async function AdminFunnelPage() {
  const auth = await createClient();
  const {
    data: { user },
  } = await auth.auth.getUser();
  if (!user) {
    redirect("/dashboard");
  }
  if (!isFunnelAdmin(user.id)) {
    return (
      <div className="mx-auto max-w-xl space-y-3">
        <h1 className="text-2xl font-semibold">Funnel — access denied</h1>
        <p className="text-sm text-muted-foreground">
          This account is not on the admin allowlist. Your user id:
        </p>
        <code className="block break-all rounded-md border bg-muted/40 px-3 py-2 text-xs">
          {user.id}
        </code>
        <p className="text-xs text-muted-foreground">
          Email: {user.email || "—"}
        </p>
        <Link href="/dashboard" className="text-sm text-primary hover:underline">
          Back to dashboard
        </Link>
      </div>
    );
  }

  const sb = getServiceClient();
  if (!sb) {
    return (
      <div className="mx-auto max-w-3xl">
        <h1 className="text-2xl font-semibold">Funnel</h1>
        <p className="mt-2 text-sm text-muted-foreground">
          Service role client is not configured.
        </p>
      </div>
    );
  }

  const [overview, usersPayload] = await Promise.all([
    loadFunnelOverview(sb),
    loadFunnelUsers(sb),
  ]);
  const f = overview.funnel;

  return (
    <div className="mx-auto max-w-6xl space-y-8">
      <div>
        <p className="text-xs font-medium uppercase tracking-wide text-muted-foreground">
          Admin
        </p>
        <h1 className="mt-1 text-2xl font-semibold tracking-tight">Funnel (14 days)</h1>
        <p className="mt-1 text-sm text-muted-foreground">
          Signup → API usage → checkout → paid. Open a user to inspect their journey and
          each request&apos;s response JSON.
        </p>
      </div>

      <div className="grid gap-3 sm:grid-cols-2 lg:grid-cols-4">
        {[
          { label: "Signups", value: f.signups },
          { label: "API callers", value: f.apiCallers },
          { label: "Checkout started", value: f.checkoutStarted },
          { label: "Paid", value: f.paid },
        ].map((card) => (
          <div key={card.label} className="rounded-lg border bg-background px-4 py-3">
            <p className="text-xs text-muted-foreground">{card.label}</p>
            <p className="mt-1 text-2xl font-semibold tabular-nums">{card.value}</p>
          </div>
        ))}
      </div>

      <div className="grid gap-3 sm:grid-cols-2 lg:grid-cols-4">
        <div className="rounded-lg border bg-background px-4 py-3">
          <p className="text-xs text-muted-foreground">Requests (sample cap)</p>
          <p className="mt-1 text-xl font-semibold tabular-nums">
            {overview.traffic.requests}
          </p>
        </div>
        <div className="rounded-lg border bg-background px-4 py-3">
          <p className="text-xs text-muted-foreground">Errors (≥400)</p>
          <p className="mt-1 text-xl font-semibold tabular-nums">
            {overview.traffic.errors}
          </p>
        </div>
        <div className="rounded-lg border bg-background px-4 py-3">
          <p className="text-xs text-muted-foreground">Response samples</p>
          <p className="mt-1 text-xl font-semibold tabular-nums">
            {overview.traffic.responseSamples}
          </p>
        </div>
        <div className="rounded-lg border bg-background px-4 py-3">
          <p className="text-xs text-muted-foreground">Latency p50 / p95</p>
          <p className="mt-1 text-xl font-semibold tabular-nums">
            {overview.traffic.latencyMs.p50 ?? "—"} /{" "}
            {overview.traffic.latencyMs.p95 ?? "—"} ms
          </p>
        </div>
      </div>

      {overview.topDropOffEndpoints.length > 0 && (
        <section className="space-y-2">
          <h2 className="text-sm font-semibold">Top drop-off endpoints (unpaid)</h2>
          <ul className="divide-y rounded-lg border">
            {overview.topDropOffEndpoints.map((row) => (
              <li
                key={row.endpoint}
                className="flex items-center justify-between gap-3 px-3 py-2 text-sm"
              >
                <code className="truncate font-mono text-xs">{row.endpoint}</code>
                <span className="shrink-0 tabular-nums text-muted-foreground">
                  {row.users} users
                </span>
              </li>
            ))}
          </ul>
        </section>
      )}

      <section className="space-y-3">
        <div className="flex items-end justify-between gap-3">
          <h2 className="text-sm font-semibold">Users</h2>
          <Link
            href="/dashboard"
            className="text-xs text-muted-foreground hover:text-foreground"
          >
            Back to dashboard
          </Link>
        </div>
        <FunnelUsersTable users={usersPayload.users} />
      </section>
    </div>
  );
}
