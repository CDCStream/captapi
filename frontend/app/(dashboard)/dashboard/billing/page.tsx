"use client";

import { useEffect, useState } from "react";
import { toast } from "sonner";
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

const PLANS = [
  { id: "starter", name: "Starter", price: "$9", credits: 2000 },
  { id: "pro", name: "Pro", price: "$27", credits: 6000 },
  { id: "business", name: "Business", price: "$90", credits: 20000 },
];

const PACKS = [
  { id: "starter", name: "Starter Pack", price: "$10", credits: 2000 },
  { id: "growth", name: "Growth Pack", price: "$53", credits: 10000 },
  { id: "scale", name: "Scale Pack", price: "$275", credits: 50000 },
];

export default function BillingPage() {
  const [balance, setBalance] = useState<Balance | null>(null);
  const [busy, setBusy] = useState(false);

  useEffect(() => {
    (async () => {
      const sb = createClient();
      const { data: { user } } = await sb.auth.getUser();
      if (!user) return;
      const { data } = await sb
        .from("credit_balances")
        .select("plan, subscription_credits, topup_credits, subscription_renews_at")
        .eq("user_id", user.id)
        .maybeSingle();
      setBalance(data as Balance | null);
    })();
  }, []);

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

  async function portal() {
    setBusy(true);
    try {
      const { url } = await api.createPortal();
      window.location.href = url;
    } catch (e) {
      toast.error(String(e));
      setBusy(false);
    }
  }

  return (
    <div className="max-w-5xl mx-auto space-y-8">
      <div className="flex items-center justify-between flex-wrap gap-3">
        <div>
          <h1 className="text-3xl font-bold">Billing</h1>
          <p className="text-muted-foreground mt-1">Manage your subscription and credits.</p>
        </div>
        <Button onClick={portal} variant="outline" disabled={busy}>Manage subscription</Button>
      </div>

      <Card>
        <CardHeader>
          <CardTitle>Current plan</CardTitle>
          <CardDescription>
            <Badge variant="secondary" className="uppercase mr-2">{balance?.plan ?? "free"}</Badge>
            {balance?.subscription_renews_at
              ? `Renews ${new Date(balance.subscription_renews_at).toLocaleDateString()}`
              : "No active subscription"}
          </CardDescription>
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

      <div>
        <h2 className="text-xl font-semibold mb-4">Plans</h2>
        <div className="grid md:grid-cols-3 gap-4">
          {PLANS.map((p) => (
            <Card key={p.id} className={balance?.plan === p.id ? "border-primary" : ""}>
              <CardHeader>
                <CardTitle>{p.name}</CardTitle>
                <CardDescription>{p.credits.toLocaleString()} credits / month</CardDescription>
                <div className="mt-2 text-2xl font-bold">{p.price}<span className="text-sm font-normal text-muted-foreground">/mo</span></div>
              </CardHeader>
              <CardContent>
                <Button
                  className="w-full"
                  disabled={busy || balance?.plan === p.id}
                  onClick={() => checkout({ plan: p.id, cycle: "monthly" })}
                >
                  {balance?.plan === p.id ? "Current plan" : "Upgrade"}
                </Button>
              </CardContent>
            </Card>
          ))}
        </div>
      </div>

      <div>
        <h2 className="text-xl font-semibold mb-4">One-time credit packs (PAYG)</h2>
        <div className="grid md:grid-cols-3 gap-4">
          {PACKS.map((p) => (
            <Card key={p.id}>
              <CardHeader>
                <CardTitle>{p.name}</CardTitle>
                <CardDescription>
                  {p.credits.toLocaleString()} credits · never expire
                </CardDescription>
                <div className="mt-2 text-2xl font-bold">{p.price}</div>
              </CardHeader>
              <CardContent>
                <Button
                  className="w-full"
                  variant="outline"
                  disabled={busy}
                  onClick={() => checkout({ pack: p.id })}
                >
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
