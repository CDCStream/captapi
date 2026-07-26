"use client";

import { useCallback, useEffect, useState } from "react";
import { usePathname, useRouter, useSearchParams } from "next/navigation";
import { toast } from "sonner";
import { initializePaddle, type Paddle, CheckoutEventNames } from "@paddle/paddle-js";
import {
  Boxes,
  Layers,
  Loader2,
  Package,
  Rocket,
  Star,
  Zap,
} from "lucide-react";
import {
  Dialog,
  DialogContent,
  DialogDescription,
  DialogHeader,
  DialogTitle,
} from "@/components/ui/dialog";
import { CreativePricing, type PricingTier } from "@/components/ui/creative-pricing";
import { api } from "@/lib/api-client";
import { ENDPOINT_COUNT } from "@/lib/api-catalog";
import { createClient } from "@/lib/supabase/client";
import { track } from "@/lib/analytics";
import { gaEvent, adsConversion } from "@/lib/gtag";
import { cn } from "@/lib/utils";

type Cycle = "monthly" | "yearly" | "payg";

const SESSION_KEY = "captapi_buy_credits_modal";

const PLANS = [
  {
    id: "starter",
    name: "Starter",
    icon: <Zap className="w-6 h-6" />,
    color: "blue",
    monthly: 9,
    description: "For side projects",
    features: [
      "2,000 credits / month",
      "120 requests / minute",
      `All ${ENDPOINT_COUNT} APIs included`,
      "Email support",
    ],
  },
  {
    id: "pro",
    name: "Pro",
    icon: <Star className="w-6 h-6" />,
    color: "amber",
    monthly: 27,
    popular: true,
    description: "For growing products",
    features: [
      "6,000 credits / month",
      "300 requests / minute",
      `All ${ENDPOINT_COUNT} APIs included`,
      "Priority support",
      "Bulk endpoints (beta)",
    ],
  },
  {
    id: "business",
    name: "Business",
    icon: <Rocket className="w-6 h-6" />,
    color: "purple",
    monthly: 90,
    description: "For data pipelines",
    features: [
      "20,000 credits / month",
      "600 requests / minute",
      `All ${ENDPOINT_COUNT} APIs included`,
      "Slack support + SLA",
      "Custom rate limits",
    ],
  },
] as const;

const PACKS = [
  {
    id: "starter",
    name: "Starter Pack",
    icon: <Package className="w-6 h-6" />,
    color: "blue",
    price: 10,
    description: "2,000 credits",
    features: [
      "$5.00 per 1k credits",
      "Never expires",
      "No subscription required",
      "All APIs included",
    ],
  },
  {
    id: "growth",
    name: "Growth Pack",
    icon: <Boxes className="w-6 h-6" />,
    color: "amber",
    price: 53,
    popular: true,
    description: "10,000 credits",
    features: [
      "$5.30 per 1k credits",
      "Never expires",
      "No subscription required",
      "All APIs included",
    ],
  },
  {
    id: "scale",
    name: "Scale Pack",
    icon: <Layers className="w-6 h-6" />,
    color: "purple",
    price: 275,
    description: "50,000 credits",
    features: [
      "$5.50 per 1k credits",
      "Never expires",
      "No subscription required",
      "All APIs included",
    ],
  },
] as const;

const HEADERS: Record<Cycle, { tag: string; title: string; description: string }> = {
  monthly: {
    tag: "Get credits",
    title: "Pick a plan to keep going.",
    description: "Free tool tries are used up. Subscribe for monthly credits, or buy a one-time pack.",
  },
  yearly: {
    tag: "Save 30% yearly",
    title: "Pick a plan to keep going.",
    description: "Two months free when you pay yearly. Cancel anytime.",
  },
  payg: {
    tag: "Pay As You Go",
    title: "Buy credits once.",
    description: "One-time packs that never expire — no subscription required.",
  },
};

const yearlyPrice = (monthly: number) => Math.round(monthly * 0.7);

/**
 * Auto-opens for free-tool converters (and other free users at 0 credits)
 * with the same pricing UI as Billing, so they can buy without hunting.
 */
export function BuyCreditsDialog() {
  const pathname = usePathname();
  const router = useRouter();
  const searchParams = useSearchParams();
  const [open, setOpen] = useState(false);
  const [ready, setReady] = useState(false);
  const [busy, setBusy] = useState(false);
  const [cycle, setCycle] = useState<Cycle>("payg");
  const [paddle, setPaddle] = useState<Paddle>();

  const fromTools =
    searchParams.get("from") === "tools" || searchParams.get("buy") === "1";

  const stripLandingParams = useCallback(() => {
    if (!fromTools) return;
    const params = new URLSearchParams(searchParams.toString());
    params.delete("from");
    params.delete("buy");
    const qs = params.toString();
    router.replace(qs ? `${pathname}?${qs}` : pathname, { scroll: false });
  }, [fromTools, pathname, router, searchParams]);

  useEffect(() => {
    const token = process.env.NEXT_PUBLIC_PADDLE_CLIENT_TOKEN;
    if (!token) return;
    const environment =
      process.env.NEXT_PUBLIC_PADDLE_ENV === "production" ? "production" : "sandbox";
    initializePaddle({
      environment,
      token,
      eventCallback: (event) => {
        if (event.name === CheckoutEventNames.CHECKOUT_COMPLETED) {
          toast.success("Payment complete — credits are on the way.");
          setOpen(false);
        }
      },
    }).then((instance) => {
      if (instance) setPaddle(instance);
    });
  }, []);

  useEffect(() => {
    let cancelled = false;
    (async () => {
      try {
        const sb = createClient();
        const {
          data: { user },
        } = await sb.auth.getUser();
        if (!user || cancelled) return;

        const { data } = await sb
          .from("credit_balances")
          .select("plan, subscription_credits, topup_credits")
          .eq("user_id", user.id)
          .maybeSingle();

        const total =
          (data?.subscription_credits ?? 0) + (data?.topup_credits ?? 0);
        const plan = (data?.plan ?? "free").toLowerCase();
        const isFree = plan === "free" || !data?.plan;
        const seen =
          typeof window !== "undefined" &&
          sessionStorage.getItem(SESSION_KEY) === "1";

        // Free-tool converters always get the modal once; other 0-credit free
        // users see it once per session if they haven't dismissed it.
        const shouldOpen =
          total === 0 && isFree && (fromTools || !seen);

        if (shouldOpen && !cancelled) {
          setOpen(true);
          sessionStorage.setItem(SESSION_KEY, "1");
          track("buy_credits_modal_open", { from_tools: fromTools });
          // Drop landing flags so refresh doesn't force-reopen after dismiss.
          stripLandingParams();
        }
      } finally {
        if (!cancelled) setReady(true);
      }
    })();
    return () => {
      cancelled = true;
    };
  }, [fromTools, stripLandingParams]);

  function onOpenChange(next: boolean) {
    setOpen(next);
    if (!next) {
      sessionStorage.setItem(SESSION_KEY, "1");
      stripLandingParams();
    }
  }

  async function checkout(body: {
    plan?: string;
    cycle?: "monthly" | "yearly";
    pack?: string;
  }) {
    setBusy(true);
    track("checkout_started", { ...body, source: "buy_credits_modal" });
    gaEvent("begin_checkout", { ...body, source: "buy_credits_modal" });
    adsConversion();
    try {
      const sb = createClient();
      const {
        data: { user },
      } = await sb.auth.getUser();
      const res = await api.createCheckout(body);
      if (res.transaction_id && paddle) {
        paddle.Checkout.open({
          transactionId: res.transaction_id,
          ...(user?.email ? { customer: { email: user.email } } : {}),
        });
        setBusy(false);
        return;
      }
      if (res.url) {
        window.location.href = res.url;
        return;
      }
      throw new Error("Checkout could not be started. Please try again.");
    } catch (e) {
      toast.error(String(e));
      setBusy(false);
    }
  }

  const planTiers: PricingTier[] = PLANS.map((p) => {
    const billingCycle: "monthly" | "yearly" =
      cycle === "yearly" ? "yearly" : "monthly";
    return {
      name: p.name,
      icon: p.icon,
      price: cycle === "yearly" ? yearlyPrice(p.monthly) : p.monthly,
      period: cycle === "yearly" ? "/mo billed yearly" : "/month",
      description: p.description,
      features: [...p.features],
      popular: "popular" in p ? p.popular : undefined,
      color: p.color,
      cta: busy ? "Starting…" : "Subscribe",
      onClick: () => checkout({ plan: p.id, cycle: billingCycle }),
      disabled: busy,
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
    cta: busy ? "Starting…" : "Buy credits",
    onClick: () => checkout({ pack: p.id }),
    disabled: busy,
  }));

  const tiers = cycle === "payg" ? packTiers : planTiers;
  const header = HEADERS[cycle];

  const cycleOptions: { id: Cycle; label: string; badge?: string }[] = [
    { id: "payg", label: "PAYG" },
    { id: "monthly", label: "Monthly" },
    { id: "yearly", label: "Yearly", badge: "(30% off)" },
  ];

  if (!ready && !open) return null;

  return (
    <Dialog open={open} onOpenChange={onOpenChange}>
      <DialogContent className="max-w-5xl max-h-[92vh] overflow-y-auto p-5 sm:p-8">
        <DialogHeader className="sr-only">
          <DialogTitle>Buy credits</DialogTitle>
          <DialogDescription>
            Choose a credit pack or subscription to keep using Captapi.
          </DialogDescription>
        </DialogHeader>

        <div className="flex justify-center mb-2">
          <div className="inline-flex items-center gap-1 rounded-full border bg-muted/40 p-1">
            {cycleOptions.map((o) => (
              <button
                key={o.id}
                type="button"
                onClick={() => setCycle(o.id)}
                className={cn(
                  "group rounded-full px-3.5 py-1.5 text-sm transition-colors",
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

        {busy && (
          <div className="flex items-center justify-center gap-2 text-sm text-muted-foreground py-1">
            <Loader2 className="size-4 animate-spin" />
            Opening checkout…
          </div>
        )}

        <CreativePricing
          key={cycle}
          compact
          tag={header.tag}
          title={header.title}
          description={header.description}
          tiers={tiers}
        />

        <p className="mt-4 text-center text-xs text-muted-foreground">
          Same tools you tried for free — billed to your credits. Cancel anytime on
          subscriptions.
        </p>
      </DialogContent>
    </Dialog>
  );
}
