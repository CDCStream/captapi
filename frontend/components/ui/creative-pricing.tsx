import Link from "next/link";
import { Button } from "@/components/ui/button";
import { Check } from "lucide-react";
import { cn } from "@/lib/utils";

interface PricingTier {
  name: string;
  icon: React.ReactNode;
  price: number;
  period?: string;
  description: string;
  features: string[];
  popular?: boolean;
  color: string;
  cta?: string;
  href?: string;
  /** Action when the card has no href (e.g. dashboard billing). */
  onClick?: () => void;
  /** Disable the CTA (e.g. current plan, busy state). */
  disabled?: boolean;
}

// Static map so Tailwind keeps these classes (dynamic `text-${color}-500` would be purged).
const ICON_COLORS: Record<string, string> = {
  amber: "text-amber-500",
  blue: "text-blue-500",
  purple: "text-purple-500",
  emerald: "text-emerald-500",
  rose: "text-rose-500",
};

const GRID_COLS: Record<number, string> = {
  1: "md:grid-cols-1 max-w-sm",
  2: "md:grid-cols-2 max-w-3xl",
  3: "md:grid-cols-3",
  4: "sm:grid-cols-2 lg:grid-cols-4",
};

function CreativePricing({
  tag = "Simple Pricing",
  title = "Make Short Videos That Pop",
  description = "Edit, enhance, and go viral in minutes",
  tiers,
}: {
  tag?: string;
  title?: string;
  description?: string;
  tiers: PricingTier[];
}) {
  return (
    <div className="w-full max-w-6xl mx-auto px-4">
      <div className="text-center space-y-6 mb-16">
        <div className="font-handwritten text-xl text-blue-500 rotate-[-1deg]">
          {tag}
        </div>
        <div className="relative">
          <h2 className="text-4xl md:text-5xl font-bold font-handwritten text-zinc-900 dark:text-white rotate-[-1deg]">
            {title}
            <div className="absolute -right-12 top-0 text-amber-500 rotate-12">
              ✨
            </div>
            <div className="absolute -left-8 bottom-0 text-blue-500 -rotate-12">
              ⭐️
            </div>
          </h2>
          <div
            className="absolute -bottom-4 left-1/2 -translate-x-1/2 w-44 h-3 bg-blue-500/20 
                        rotate-[-1deg] rounded-full blur-sm"
          />
        </div>
        <p className="font-handwritten text-xl text-zinc-600 dark:text-zinc-400 rotate-[-1deg]">
          {description}
        </p>
      </div>

      <div
        className={cn(
          "grid grid-cols-1 gap-8 mx-auto",
          GRID_COLS[tiers.length] ?? "md:grid-cols-3",
        )}
      >
        {tiers.map((tier, index) => (
          <div
            key={tier.name}
            className={cn(
              "relative group",
              "transition-all duration-300",
              index % 3 === 0 && "rotate-[-1deg]",
              index % 3 === 1 && "rotate-[1deg]",
              index % 3 === 2 && "rotate-[-2deg]",
            )}
          >
            <div
              className={cn(
                "absolute inset-0 bg-white dark:bg-zinc-900",
                "border-2 border-zinc-900 dark:border-white",
                "rounded-lg shadow-[4px_4px_0px_0px] shadow-zinc-900 dark:shadow-white",
                "transition-all duration-300",
                "group-hover:shadow-[8px_8px_0px_0px]",
                "group-hover:translate-x-[-4px]",
                "group-hover:translate-y-[-4px]",
              )}
            />

            <div className="relative p-6">
              {tier.popular && (
                <div
                  className="absolute -top-2 -right-2 bg-amber-400 text-zinc-900 
                                    font-handwritten px-3 py-1 rounded-full rotate-12 text-sm border-2 border-zinc-900"
                >
                  Popular!
                </div>
              )}

              <div className="mb-6">
                <div
                  className={cn(
                    "w-12 h-12 rounded-full mb-4",
                    "flex items-center justify-center",
                    "border-2 border-zinc-900 dark:border-white",
                    ICON_COLORS[tier.color] ?? "text-blue-500",
                  )}
                >
                  {tier.icon}
                </div>
                <h3 className="font-handwritten text-2xl text-zinc-900 dark:text-white">
                  {tier.name}
                </h3>
                <p className="font-handwritten text-zinc-600 dark:text-zinc-400">
                  {tier.description}
                </p>
              </div>

              {/* Price */}
              <div className="mb-6 font-handwritten">
                <span className="text-4xl font-bold text-zinc-900 dark:text-white">
                  ${tier.price}
                </span>
                <span className="text-zinc-600 dark:text-zinc-400">
                  {tier.period ?? "/month"}
                </span>
              </div>

              <div className="space-y-3 mb-6">
                {tier.features.map((feature) => (
                  <div key={feature} className="flex items-center gap-3">
                    <div
                      className="w-5 h-5 rounded-full border-2 border-zinc-900 
                                            dark:border-white flex items-center justify-center"
                    >
                      <Check className="w-3 h-3" />
                    </div>
                    <span className="font-handwritten text-lg text-zinc-900 dark:text-white">
                      {feature}
                    </span>
                  </div>
                ))}
              </div>

              <Button
                asChild={Boolean(tier.href)}
                onClick={tier.href ? undefined : tier.onClick}
                disabled={tier.disabled}
                className={cn(
                  "w-full h-12 font-handwritten text-lg relative",
                  tier.disabled && "opacity-60 cursor-not-allowed",
                  "border-2 border-zinc-900 dark:border-white",
                  "transition-all duration-300",
                  "shadow-[4px_4px_0px_0px] shadow-zinc-900 dark:shadow-white",
                  "hover:shadow-[6px_6px_0px_0px]",
                  "hover:translate-x-[-2px] hover:translate-y-[-2px]",
                  tier.popular
                    ? [
                        "bg-amber-400 text-zinc-900",
                        "hover:bg-amber-300",
                        "active:bg-amber-400",
                        "dark:hover:bg-amber-300",
                        "dark:active:bg-amber-400",
                      ]
                    : [
                        "bg-zinc-50 dark:bg-zinc-800",
                        "text-zinc-900 dark:text-white",
                        "hover:bg-white dark:hover:bg-zinc-700",
                        "active:bg-zinc-50 dark:active:bg-zinc-800",
                      ],
                )}
              >
                {tier.href ? (
                  <Link href={tier.href}>{tier.cta ?? "Get Started"}</Link>
                ) : (
                  <span>{tier.cta ?? "Get Started"}</span>
                )}
              </Button>
            </div>
          </div>
        ))}
      </div>
    </div>
  );
}

export { CreativePricing, type PricingTier };
