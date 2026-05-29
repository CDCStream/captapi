"use client";

import { useCallback, useEffect, useState } from "react";
import { toast } from "sonner";
import {
  Loader2,
  Zap,
  Star,
  Rocket,
  Package,
  Boxes,
  Layers,
} from "lucide-react";
import { Button } from "@/components/ui/button";
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";
import { Badge } from "@/components/ui/badge";
import { CreativePricing, type PricingTier } from "@/components/ui/creative-pricing";
import { api } from "@/lib/api-client";
import { createClient } from "@/lib/supabase/client";
import { cn } from "@/lib/utils";

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

type Cycle = "monthly" | "yearly" | "payg";

const PLANS = [
  {
    id: "starter",
    name: "Starter",
    icon: <Zap className="w-6 h-6" />,
    color: "blue",
    monthly: 9,
    credits: 2000,
    tier: 1,
    description: "For side projects",
    features: ["2,000 credits / month", "120 requests / minute", "All 34 APIs included", "Email support"],
  },
  {
    id: "pro",
    name: "Pro",
    icon: <Star className="w-6 h-6" />,
    color: "amber",
    monthly: 27,
    credits: 6000,
    tier: 2,
    popular: true,
    description: "For growing products",
    features: ["6,000 credits / month", "300 requests / minute", "Priority support", "Bulk endpoints (beta)"],
  },
  {
    id: "business",
    name: "Business",
    icon: <Rocket className="w-6 h-6" />,
    color: "purple",
    monthly: 90,
    credits: 20000,
    tier: 3,
    description: "For data pipelines",
    features: ["20,000 credits / month", "600 requests / minute", "Slack support + SLA", "Custom rate limits"],
  },
] as const;

const PACKS = [
  {
    id: "starter",
    name: "Starter Pack",
    icon: <Package className="w-6 h-6" />,
    color: "blue",
    price: 10,
    credits: 2000,
    description: "2,000 credits",
    features: ["$5.00 per 1k credits", "Never expires", "Used after monthly credits", "All APIs included", "No subscription required"],
  },
  {
    id: "growth",
    name: "Growth Pack",
    icon: <Boxes className="w-6 h-6" />,
    color: "amber",
    price: 53,
    credits: 10000,
    popular: true,
    description: "10,000 credits",
    features: ["$5.30 per 1k credits", "Never expires", "Used after monthly credits", "All APIs included", "No subscription required"],
  },
  {
    id: "scale",
    name: "Scale Pack",
    icon: <Layers className="w-6 h-6" />,
    color: "purple",
    price: 275,
    credits: 50000,
    description: "50,000 credits",
    features: ["$5.50 per 1k credits", "Never expires", "Used after monthly credits", "All APIs included", "No subscription required"],
  },
] as const;

const HEADERS: Record<Cycle, { tag: string; title: string; description: string }> = {
  monthly: {
    tag: "Subscriptions",
    title: "Pick your plan.",
    description: "Pay only for what you use — cached results are always free.",
  },
  yearly: {
    tag: "Save 30% yearly",
    title: "Pick your plan.",
    description: "Two months free when you pay yearly. Cancel anytime.",
  },
  payg: {
    tag: "Pay As You Go",
    title: "Top up anytime.",
    description: "One-time credit packs that never expire.",
  },
};

const yearlyPrice = (monthly: number) => Math.round(monthly * 0.7);

function tierOf(planId?: string): number {
  return PLANS.find((p) => p.id === planId)?.tier ?? 0;
}

export default function BillingPage() {
  const [balance, setBalance] = useState<Balance | null>(null);
  const [sub, setSub] = useState<Subscription | null>(null);
  const [busy, setBusy] = useState(false);
  const [cycle, setCycle] = useState<Cycle>("monthly");

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

  async function changePlan(planId: string, planCycle: "monthly" | "yearly") {
    setBusy(true);
    try {
      await api.changePlan(planId, planCycle);
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

  async function openPortal() {
    setBusy(true);
    try {
      const { url } = await api.createPortal();
      window.location.href = url;
    } catch (e) {
      const msg = String(e);
      if (msg.includes("404")) {
        toast.error("No billing history yet — subscribe or buy credits first.");
      } else {
        toast.error("Couldn't open the billing portal. Please try again.");
      }
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

  const planTiers: PricingTier[] = PLANS.map((p) => {
    const billingCycle: "monthly" | "yearly" = cycle === "yearly" ? "yearly" : "monthly";
    const price = cycle === "yearly" ? yearlyPrice(p.monthly) : p.monthly;
    const period = cycle === "yearly" ? "/mo billed yearly" : "/month";

    let cta = "Subscribe";
    let onClick: (() => void) | undefined = () => checkout({ plan: p.id, cycle: billingCycle });
    let disabled = busy;

    if (hasActiveSub) {
      if (p.id === currentPlan) {
        cta = "Current plan";
        onClick = undefined;
        disabled = true;
      } else {
        cta = p.tier > currentTier ? "Upgrade" : "Downgrade";
        onClick = () => changePlan(p.id, billingCycle);
      }
    }

    return {
      name: p.name,
      icon: p.icon,
      price,
      period,
      description: p.description,
      features: [...p.features],
      popular: "popular" in p ? p.popular : undefined,
      color: p.color,
      cta,
      onClick,
      disabled,
    };
  });

  const packTiers: PricingTier[] = PACKS.map((p) => ({
    name: p.name,
    icon: p.icon,
    price: p.price,
    period: " one-time",
    description: p.description,
    features: [...p.features],
    popular: "popular" in p ? p.popular : undefined,
    color: p.color,
    cta: "Buy now",
    onClick: () => checkout({ pack: p.id }),
    disabled: busy,
  }));

  const tiers = cycle === "payg" ? packTiers : planTiers;
  const header = HEADERS[cycle];

  const cycleOptions: { id: Cycle; label: string; badge?: string }[] = [
    { id: "monthly", label: "Monthly" },
    { id: "yearly", label: "Yearly", badge: "(30% off)" },
    { id: "payg", label: "PAYG" },
  ];

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
        <Button onClick={openPortal} variant="outline" disabled={busy}>
          Invoices & payment method
        </Button>
      </div>

      {/* Current plan */}
      <Card>
        <CardHeader>
          <div className="flex items-center justify-between gap-3 flex-wrap">
            <div>
              <CardTitle>Current plan</CardTitle>
              <div className="mt-1 flex items-center gap-2 text-sm text-muted-foreground">
                <Badge variant="secondary" className="uppercase">{currentPlan}</Badge>
                {sub?.cancel_at_period_end ? (
                  <span className="text-amber-600 dark:text-amber-400">
                    Cancels on {renewLabel ?? "period end"}
                  </span>
                ) : renewLabel ? (
                  <span>Renews {renewLabel}</span>
                ) : (
                  <span>No active subscription</span>
                )}
              </div>
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

      {/* Plans & packs — creative pricing (matches landing) */}
      <div className="pt-2">
        <div className="flex justify-center mb-10">
          <div className="inline-flex items-center gap-1 rounded-full border bg-muted/40 p-1">
            {cycleOptions.map((o) => (
              <button
                key={o.id}
                onClick={() => setCycle(o.id)}
                className={cn(
                  "group rounded-full px-4 py-1.5 text-sm transition-colors",
                  cycle === o.id
                    ? "bg-primary text-primary-foreground shadow-sm"
                    : "text-muted-foreground hover:text-foreground",
                )}
              >
                {o.label}
                {o.badge && (
                  <span
                    className={cn(
                      "ml-1 font-semibold",
                      cycle === o.id
                        ? "text-primary-foreground"
                        : "text-primary group-hover:text-primary/80",
                    )}
                  >
                    {o.badge}
                  </span>
                )}
              </button>
            ))}
          </div>
        </div>

        <CreativePricing
          key={cycle}
          tag={header.tag}
          title={header.title}
          description={header.description}
          tiers={tiers}
        />

        {hasActiveSub && cycle !== "payg" && (
          <p className="mt-8 text-center text-xs text-muted-foreground">
            Plan changes are prorated immediately. Credits adjust to the new plan right away.
          </p>
        )}
      </div>
    </div>
  );
}
