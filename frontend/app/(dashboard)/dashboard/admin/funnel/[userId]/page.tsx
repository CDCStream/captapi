import Link from "next/link";
import { redirect, notFound } from "next/navigation";
import { createClient } from "@/lib/supabase/server";
import { getServiceClient } from "@/lib/supabase/admin";
import { FUNNEL_EXCLUDE_USER_ID, isFunnelAdmin } from "@/lib/funnel-admin";
import { loadUserJourney } from "@/lib/funnel-data";
import { FunnelJourney } from "@/components/admin/funnel-journey";

export const dynamic = "force-dynamic";

type Props = { params: Promise<{ userId: string }> };

export default async function AdminFunnelUserPage({ params }: Props) {
  const { userId } = await params;
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
        <p className="text-sm text-muted-foreground">Your user id:</p>
        <code className="block break-all rounded-md border bg-muted/40 px-3 py-2 text-xs">
          {user.id}
        </code>
        <p className="text-xs text-muted-foreground">Email: {user.email || "—"}</p>
        <Link href="/dashboard" className="text-sm text-primary hover:underline">
          Back to dashboard
        </Link>
      </div>
    );
  }
  if (!userId || userId === FUNNEL_EXCLUDE_USER_ID) {
    notFound();
  }

  const sb = getServiceClient();
  if (!sb) {
    return (
      <div className="mx-auto max-w-3xl">
        <p className="text-sm text-muted-foreground">Service role client is not configured.</p>
      </div>
    );
  }

  const data = await loadUserJourney(sb, userId);
  const u = data.user;

  return (
    <div className="mx-auto max-w-3xl space-y-6">
      <div>
        <Link
          href="/dashboard/admin/funnel"
          className="text-xs text-muted-foreground hover:text-foreground"
        >
          ← Funnel
        </Link>
        <h1 className="mt-2 text-2xl font-semibold tracking-tight">
          {u.email || u.id.slice(0, 8)}
        </h1>
        <p className="mt-1 font-mono text-xs text-muted-foreground">{u.id}</p>
        <p className="mt-2 text-sm text-muted-foreground">
          Plan {u.plan || "—"} · {u.subscriptionCredits + u.topupCredits} credits left ·{" "}
          {data.stats.requests} requests · {data.stats.samples} samples · last 14 days
        </p>
      </div>

      <section className="space-y-3">
        <h2 className="text-sm font-semibold">Journey</h2>
        <p className="text-xs text-muted-foreground">
          Click a request row with &quot;View JSON&quot; to expand the stored response body.
        </p>
        <FunnelJourney timeline={data.timeline} />
      </section>
    </div>
  );
}
