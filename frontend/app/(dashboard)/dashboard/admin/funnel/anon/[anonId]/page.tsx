import Link from "next/link";
import { redirect, notFound } from "next/navigation";
import { createClient } from "@/lib/supabase/server";
import { getServiceClient } from "@/lib/supabase/admin";
import { isFunnelAdmin } from "@/lib/funnel-admin";
import { loadAnonJourney } from "@/lib/funnel-data";
import { FunnelJourney } from "@/components/admin/funnel-journey";

export const dynamic = "force-dynamic";

type Props = { params: Promise<{ anonId: string }> };

export default async function AdminFunnelAnonPage({ params }: Props) {
  const { anonId: raw } = await params;
  const anonId = decodeURIComponent(raw || "");
  const auth = await createClient();
  const {
    data: { user },
  } = await auth.auth.getUser();
  if (!user) redirect("/dashboard");
  if (!isFunnelAdmin(user.id)) {
    return (
      <div className="mx-auto max-w-xl space-y-3">
        <h1 className="text-2xl font-semibold">Funnel — access denied</h1>
        <Link href="/dashboard" className="text-sm text-primary hover:underline">
          Back to dashboard
        </Link>
      </div>
    );
  }
  if (!anonId) notFound();

  const sb = getServiceClient();
  if (!sb) {
    return (
      <div className="mx-auto max-w-3xl">
        <p className="text-sm text-muted-foreground">Service role client is not configured.</p>
      </div>
    );
  }

  const data = await loadAnonJourney(sb, anonId);

  return (
    <div className="mx-auto max-w-3xl space-y-6">
      <div>
        <Link
          href="/dashboard/admin/funnel"
          className="text-xs text-muted-foreground hover:text-foreground"
        >
          ← Funnel
        </Link>
        <h1 className="mt-2 text-2xl font-semibold tracking-tight">Anonymous visitor</h1>
        <p className="mt-1 font-mono text-xs text-muted-foreground">{anonId}</p>
        <p className="mt-2 text-sm text-muted-foreground">
          {data.stats.events} events · not signed up · last 14 days
        </p>
      </div>

      <section className="space-y-3">
        <h2 className="text-sm font-semibold">Journey</h2>
        <p className="text-xs text-muted-foreground">
          Pre-signup page views and CTA clicks for this browser (anon_id).
        </p>
        <FunnelJourney timeline={data.timeline} />
      </section>
    </div>
  );
}
