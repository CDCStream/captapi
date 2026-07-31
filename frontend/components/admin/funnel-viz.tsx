"use client";

import { cn } from "@/lib/utils";

export type FunnelStep = {
  label: string;
  value: number;
  hint?: string;
};

const FILLS = [
  "#0d9488",
  "#0891b2",
  "#0284c7",
  "#d97706",
  "#ea580c",
  "#e11d48",
];

function pct(n: number, d: number) {
  if (!d) return null;
  return Math.round((n / d) * 1000) / 10;
}

function fmt(n: number) {
  return n.toLocaleString();
}

/**
 * Classic marketing funnel: stacked trapezoids, width proportional to count.
 * Designed to screenshot cleanly for X / build-in-public posts.
 */
export function FunnelViz({
  steps,
  title = "Captapi",
  subtitle = "14-day funnel",
  className,
}: {
  steps: FunnelStep[];
  title?: string;
  subtitle?: string;
  className?: string;
}) {
  const max = Math.max(...steps.map((s) => s.value), 1);
  const top = steps[0]?.value || 1;
  const W = 400;
  const H = 52;
  const GAP = 18;
  const PAD_X = 8;
  const MIN_HALF = W * 0.09;
  const totalH = steps.length * H + Math.max(0, steps.length - 1) * GAP;

  const halfFor = (value: number) =>
    Math.max(MIN_HALF, (value / max) * (W / 2 - PAD_X));

  return (
    <div
      className={cn(
        "relative overflow-hidden rounded-2xl border border-zinc-200/80 bg-gradient-to-b from-zinc-50 via-white to-teal-50/50 p-6 sm:p-8",
        className,
      )}
    >
      <div
        aria-hidden
        className="pointer-events-none absolute -right-16 -top-20 size-56 rounded-full bg-teal-400/15 blur-3xl"
      />
      <div
        aria-hidden
        className="pointer-events-none absolute -bottom-24 -left-10 size-48 rounded-full bg-amber-400/10 blur-3xl"
      />

      <div className="relative mb-6 flex items-end justify-between gap-4">
        <div>
          <p className="text-[11px] font-semibold uppercase tracking-[0.18em] text-teal-700/80">
            {title}
          </p>
          <h2 className="mt-1 text-xl font-semibold tracking-tight text-zinc-900 sm:text-2xl">
            {subtitle}
          </h2>
        </div>
        <p className="hidden text-right text-xs text-zinc-500 sm:block">
          Visitors → paid
          <br />
          conversion path
        </p>
      </div>

      <div className="relative mx-auto max-w-lg">
        <svg
          viewBox={`0 0 ${W} ${totalH}`}
          className="h-auto w-full drop-shadow-sm"
          role="img"
          aria-label="Conversion funnel"
        >
          {steps.map((step, i) => {
            const y = i * (H + GAP);
            const topHalf = halfFor(step.value);
            const next = steps[i + 1];
            const botHalf = next ? halfFor(next.value) : Math.max(MIN_HALF * 0.7, topHalf * 0.55);
            const cx = W / 2;
            const x1 = cx - topHalf;
            const x2 = cx + topHalf;
            const x3 = cx + botHalf;
            const x4 = cx - botHalf;
            const fill = FILLS[i % FILLS.length];
            const midY = y + H / 2;

            return (
              <g key={step.label}>
                <polygon
                  points={`${x1},${y} ${x2},${y} ${x3},${y + H} ${x4},${y + H}`}
                  fill={fill}
                />
                <text
                  x={cx - topHalf + 14}
                  y={midY}
                  dominantBaseline="middle"
                  fill="white"
                  fontSize="13"
                  fontWeight="600"
                  style={{ fontFamily: "ui-sans-serif, system-ui, sans-serif" }}
                >
                  {step.label}
                </text>
                <text
                  x={cx + topHalf - 14}
                  y={midY}
                  dominantBaseline="middle"
                  textAnchor="end"
                  fill="white"
                  fontSize="16"
                  fontWeight="700"
                  style={{ fontFamily: "ui-sans-serif, system-ui, sans-serif" }}
                >
                  {fmt(step.value)}
                </text>
                {i < steps.length - 1 && (
                  <text
                    x={cx}
                    y={y + H + GAP / 2 + 1}
                    textAnchor="middle"
                    dominantBaseline="middle"
                    fill="#71717a"
                    fontSize="11"
                    fontWeight="600"
                    style={{ fontFamily: "ui-sans-serif, system-ui, sans-serif" }}
                  >
                    {pct(steps[i + 1].value, step.value)}% convert
                  </text>
                )}
              </g>
            );
          })}
        </svg>
      </div>

      <div className="relative mt-6 grid grid-cols-2 gap-2 sm:grid-cols-3 lg:grid-cols-6">
        {steps.map((step, i) => {
          const prev = i > 0 ? steps[i - 1].value : null;
          const ofTop = pct(step.value, top);
          const stepPct = prev != null ? pct(step.value, prev) : null;
          return (
            <div
              key={`m-${step.label}`}
              className="rounded-lg border border-zinc-200/80 bg-white/80 px-3 py-2 backdrop-blur"
            >
              <div className="flex items-center gap-1.5">
                <span
                  className="size-2 shrink-0 rounded-full"
                  style={{ background: FILLS[i % FILLS.length] }}
                />
                <p className="truncate text-[10px] font-medium uppercase tracking-wide text-zinc-500">
                  {step.label}
                </p>
              </div>
              <p className="mt-0.5 text-lg font-semibold tabular-nums text-zinc-900">
                {fmt(step.value)}
              </p>
              <p className="text-[10px] text-zinc-500">
                {i === 0
                  ? "top of funnel"
                  : `${ofTop}% of visitors${stepPct != null ? ` · ${stepPct}% step` : ""}`}
              </p>
            </div>
          );
        })}
      </div>
    </div>
  );
}
