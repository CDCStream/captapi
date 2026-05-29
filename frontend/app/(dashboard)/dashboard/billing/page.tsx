"use client";

import { useCallback, useEffect, useState } from "react";
import { toast } from "sonner";
import { Check, Loader2 } from "lucide-react";
import { Button } from "@/components/ui/button";
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from "@/components/ui/card";
import { Badge } from "@/components/ui/badge";
import { api } from "@/lib/api-client";
import { createClient } from "@/lib/supabase/client";

interface Balance {
  plan: string;
  subscription_credits: number;
  topup_credits: number;
  subscription_renews_at: string | null;
}

interface Subscription {
  active: boolean;
  status?: string;
  plan?: string;
  current_period_end?: string | null;
  cancel_at_period_end?: boolean;
}

const PLANS = [
  { id: "starter", name: "Starter", price: "$9", credits: 2000, tier: 1 },
  { id: "pro", name: "Pro", price: "$27", credits: 6000, tier: 2 },
  { id: "business", name: "Business", price: "$90", credits: 20000, tier: 3 },
];

const PACKS = [
  { id: "starter", name: "Starter Pack", price: "$10", credits: 2000 },
  { id: "growth", name: "Growth Pack", price: "$53", credits: 10000 },
  { id: "scale", name: "Scale Pack", price: "$275", credits: 50000 },
];

function tierOf(planId?: string): number {
  return PLANS.find((p) => p.id === planId)?.tier ?? 0;
}

export default function BillingPage() {
  const [balance, setBalance] = useState<Balance | null>(null);
  const [sub, setSub] = useState<Subscription | null>(null);
  const [busy, setBusy] = useState(false);

  const load = useCallback(async () => {
    const sb = createClient();
    const { data: { user } } = await sb.auth.getUser();
    if (!user) return;
    const { data } = await sb
      .from("credit_balances")
      .select("plan, subscription_credits, topup_credits, subscription_renews_at")
      .eq("user_id", user.id)
      .maybeSingle();
    setBalance(data as Balance | null);
    try {
      setSub(await api.getSubscription());
    } catch {
      setSub({ active: false, plan: "free" });
    }
  }, []);

  useEffect(() => {
    load();
  }, [load]);

  const currentPlan = sub?.plan ?? balance?.plan ?? "free";
  const hasActiveSub = Boolean(sub?.active);
  const currentTier = tierOf(currentPlan);

  async function checkout(body: { plan?: string; cycle?: "monthly" | "yearly"; pack?: string }) {
    setBusy(true);
    try {
      const { url } = await api.createCheckout(body);
      window.location.href = url;
    } catch (e) {
      toast.error(String(e));
      setBusy(false);
    }
  }

  async function changePlan(planId: string) {
    setBusy(true);
    try {
      await api.changePlan(planId, "monthly");
      toast.success("Plan updated.");
      await load();
    } catch (e) {
      toast.error(String(e));
    } finally {
      setBusy(false);
    }
  }

  async function cancel() {
    if (!confirm("Cancel your subscription? You'll keep access until the end of the current period.")) {
      return;
    }
    setBusy(true);
    try {
      await api.cancelSubscription();
      toast.success("Subscription will cancel at period end.");
      await load();
    } catch (e) {
      toast.error(String(e));
    } finally {
      setBusy(false);
    }
  }

  async function reactivate() {
    setBusy(true);
    try {
      await api.reactivateSubscription();
      toast.success("Subscription resumed.");
      await load();
    } catch (e) {
      toast.error(String(e));
    } finally {
      setBusy(false);
    }
  }

  function planButton(p: (typeof PLANS)[number]) {
    if (!hasActiveSub) {
      return (
        <Button className="w-full" disabled={busy} onClick={() => checkout({ plan: p.id, cycle: "monthly" })}>
          Subscribe
        </Button>
      );
    }
    if (p.id === currentPlan) {
      return (
        <Button className="w-full" variant="secondary" disabled>
          <Check className="size-4" /> Current plan
        </Button>
      );
    }
    const isUpgrade = p.tier > currentTier;
    return (
      <Button
        className="w-full"
        variant={isUpgrade ? "default" : "outline"}
        disabled={busy}
        onClick={() => changePlan(p.id)}
      >
        {isUpgrade ? "Upgrade" : "Downgrade"}
      </Button>
    );
  }

  const renewLabel = balance?.subscription_renews_at
    ? new Date(balance.subscription_renews_at).toLocaleDateString()
    : sub?.current_period_end
      ? new Date(sub.current_period_end).toLocaleDateString()
      : null;

  return (
    <div className="max-w-5xl mx-auto space-y-8">
      <div className="flex items-center justify-between flex-wrap gap-3">
        <div>
          <h1 className="text-3xl font-bold tracking-tight">Billing</h1>
          <p className="text-muted-foreground mt-1">Manage your subscription and credits.</p>
        </div>
        <Button onClick={() => api.createPortal().then(({ url }) => (window.location.href = url)).catch((e) => toast.error(String(e)))} variant="outline" disabled={busy}>
          Invoices & payment method
        </Button>
      </div>

      {/* Current plan */}
      <Card>
        <CardHeader>
          <div className="flex items-center justify-between gap-3 flex-wrap">
            <div>
              <CardTitle>Current plan</CardTitle>
              <CardDescription className="mt-1 flex items-center gap-2">
                <Badge variant="secondary" className="uppercase">{currentPlan}</Badge>
                {sub?.cancel_at_period_end ? (
                  <span className="text-amber-600 dark:text-amber-400">
                    Cancels on {renewLabel ?? "period end"}
                  </span>
                ) : renewLabel ? (
                  `Renews ${renewLabel}`
                ) : (
                  "No active subscription"
                )}
              </CardDescription>
            </div>
            {hasActiveSub &&
              (sub?.cancel_at_period_end ? (
                <Button size="sm" disabled={busy} onClick={reactivate}>
                  {busy && <Loader2 className="size-4 animate-spin" />} Resume subscription
                </Button>
              ) : (
                <Button size="sm" variant="ghost" className="text-destructive hover:text-destructive" disabled={busy} onClick={cancel}>
                  Cancel subscription
                </Button>
              ))}
          </div>
        </CardHeader>
        <CardContent className="grid grid-cols-2 gap-4 max-w-md">
          <div>
            <div className="text-xs text-muted-foreground">Subscription credits</div>
            <div className="text-2xl font-bold">{balance?.subscription_credits ?? 0}</div>
          </div>
          <div>
            <div className="text-xs text-muted-foreground">Top-up credits</div>
            <div className="text-2xl font-bold">{balance?.topup_credits ?? 0}</div>
          </div>
        </CardContent>
      </Card>

      {/* Plans */}
      <div>
        <h2 className="text-xl font-semibold mb-4">Plans</h2>
        <div className="grid md:grid-cols-3 gap-4">
          {PLANS.map((p) => (
            <Card key={p.id} className={p.id === currentPlan ? "border-primary ring-1 ring-primary/20" : ""}>
              <CardHeader>
                <CardTitle>{p.name}</CardTitle>
                <CardDescription>{p.credits.toLocaleString()} credits / month</CardDescription>
                <div className="mt-2 text-2xl font-bold">
                  {p.price}
                  <span className="text-sm font-normal text-muted-foreground">/mo</span>
                </div>
              </CardHeader>
              <CardContent>{planButton(p)}</CardContent>
            </Card>
          ))}
        </div>
        {hasActiveSub && (
          <p className="mt-3 text-xs text-muted-foreground">
            Plan changes are prorated immediately. Credits adjust to the new plan right away.
          </p>
        )}
      </div>

      {/* Packs */}
      <div>
        <h2 className="text-xl font-semibold mb-4">One-time credit packs (PAYG)</h2>
        <div className="grid md:grid-cols-3 gap-4">
          {PACKS.map((p) => (
            <Card key={p.id}>
              <CardHeader>
                <CardTitle>{p.name}</CardTitle>
                <CardDescription>{p.credits.toLocaleString()} credits · never expire</CardDescription>
                <div className="mt-2 text-2xl font-bold">{p.price}</div>
              </CardHeader>
              <CardContent>
                <Button className="w-full" variant="outline" disabled={busy} onClick={() => checkout({ pack: p.id })}>
                  Buy now
                </Button>
              </CardContent>
            </Card>
          ))}
        </div>
      </div>
    </div>
  );
}
