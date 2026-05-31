"use client";

import { useEffect } from "react";
import Link from "next/link";
import { Plus } from "lucide-react";
import {
  renderCanvas,
  ShineBorder,
  TypeWriter,
  HeadlineTypeWriter,
} from "@/components/ui/hero-designali";
import { GoogleButton } from "@/components/auth/google-button";
import { Button } from "@/components/ui/button";
import { PLATFORM_GROUPS } from "@/lib/api-catalog";

const ENDPOINT_COUNT = PLATFORM_GROUPS.reduce(
  (n, g) => n + g.endpoints.length,
  0,
);

const platformsTyped = [
  "YouTube",
  "TikTok",
  "Instagram",
  "Facebook",
  "Shorts",
  "Reels",
];

const contentTyped = [
  "videos",
  "posts",
  "comments",
  "hashtags",
  "followers",
  "transcripts",
  "reels",
  "shorts",
];

export function CaptapiHero() {
  useEffect(() => {
    renderCanvas();
  }, []);

  return (
    <section id="home" className="relative overflow-x-hidden">
      {/* grid backdrop */}
      <div className="absolute inset-0 top-[300px] -z-10 h-[400px] w-full bg-[linear-gradient(to_right,#cbd5e1_1px,transparent_1px),linear-gradient(to_bottom,#cbd5e1_1px,transparent_1px)] bg-[size:3rem_3rem] opacity-30 [mask-image:radial-gradient(ellipse_80%_50%_at_50%_0%,#000_70%,transparent_110%)] dark:bg-[linear-gradient(to_right,#1e293b_1px,transparent_1px),linear-gradient(to_bottom,#1e293b_1px,transparent_1px)]" />
      {/* top glow — capped to viewport so it never causes horizontal scroll */}
      <div className="absolute left-1/2 top-0 -z-10 h-[400px] w-full max-w-[700px] -translate-x-1/2 rounded-full bg-gradient-to-b from-blue-500/20 to-transparent blur-3xl" />

      <div className="flex min-h-[calc(100svh-4rem)] flex-col items-center justify-center px-4 sm:px-6 text-center">
        {/* badge pill */}
        <div className="mb-5 mt-6 md:mb-6 md:mt-12">
          <div className="relative flex items-center rounded-full border bg-popover px-3 py-1 text-xs text-primary/70">
            Social Media Data API
            <Link
              href="/docs"
              className="ml-1 flex items-center font-semibold text-primary"
            >
              <span className="absolute inset-0" aria-hidden="true" />
              Explore →
            </Link>
          </div>
        </div>

        <div className="mx-auto w-full max-w-6xl">
          {/* headline box with plus corners */}
          <div className="relative mx-auto h-full border border-border bg-background px-6 py-6 sm:py-8 [mask-image:radial-gradient(600rem_96rem_at_center,white,transparent)]">
            {/* Plus corners — smaller on mobile to avoid clipping */}
            <Plus strokeWidth={4} className="absolute -left-3 -top-3 h-6 w-6 sm:-left-5 sm:-top-5 sm:h-10 sm:w-10 text-primary" />
            <Plus strokeWidth={4} className="absolute -bottom-3 -left-3 h-6 w-6 sm:-bottom-5 sm:-left-5 sm:h-10 sm:w-10 text-primary" />
            <Plus strokeWidth={4} className="absolute -right-3 -top-3 h-6 w-6 sm:-right-5 sm:-top-5 sm:h-10 sm:w-10 text-primary" />
            <Plus strokeWidth={4} className="absolute -bottom-3 -right-3 h-6 w-6 sm:-bottom-5 sm:-right-5 sm:h-10 sm:w-10 text-primary" />

            <h1 className="text-center text-3xl font-semibold leading-tight tracking-tight sm:text-4xl md:text-6xl lg:text-7xl">
              One API for getting{" "}
              <span className="gradient-text">
                structured data from Social Media
              </span>{" "}
              {/* Reserve width of the longest word ("transcripts") so the line
                  wrapping never changes and the box height stays constant. */}
              <span className="inline-block min-w-[11ch] text-left align-baseline">
                <HeadlineTypeWriter strings={contentTyped} />
              </span>
            </h1>

            <div className="mt-5 flex items-center justify-center gap-1">
              <span className="relative flex h-3 w-3 items-center justify-center">
                <span className="absolute inline-flex h-full w-full animate-ping rounded-full bg-green-500 opacity-75" />
                <span className="relative inline-flex h-2 w-2 rounded-full bg-green-500" />
              </span>
              <p className="text-xs text-green-500">
                {ENDPOINT_COUNT} endpoints live across 4 platforms
              </p>
            </div>
          </div>

          {/* subtext with typewriter */}
          <p className="text-primary/60 mx-auto max-w-2xl py-4 text-sm sm:text-base md:text-lg">
            Extract transcripts, AI summaries, comments, followers, engagement
            metrics &amp; more from{" "}
            <span className="font-semibold text-primary">
              <TypeWriter strings={platformsTyped} />
            </span>{" "}
            — with a single request.
          </p>

          {/* CTAs — stack vertically on mobile */}
          <div className="flex flex-col items-center gap-3 sm:flex-row sm:justify-center">
            <Link href="/signup" className="w-full sm:w-auto">
              <ShineBorder
                borderWidth={3}
                className="h-auto w-full cursor-pointer border bg-white/5 p-1 backdrop-blur-md dark:bg-black/5 sm:w-auto"
                color={["#3b82f6", "#0ea5e9", "#06b6d4"]}
              >
                <Button className="w-full rounded-2xl">
                  Start Free — 100 credits
                </Button>
              </ShineBorder>
            </Link>
            <GoogleButton className="w-full rounded-2xl sm:w-auto" />
          </div>
          <p className="mt-3 text-xs text-muted-foreground">
            No credit card required.
          </p>

          {/* API client mockup */}
          <div className="relative mx-auto mt-6 sm:mt-8 w-full max-w-2xl text-left">
            <div className="absolute -inset-4 -z-10 rounded-3xl bg-gradient-to-br from-blue-500/20 to-sky-400/10 blur-2xl" />
            <div className="relative overflow-hidden rounded-xl border border-white/10 bg-zinc-950 shadow-2xl">
              {/* window bar with platform tabs */}
              <div className="flex items-center gap-2 border-b border-white/10 px-3 py-2.5 sm:gap-3 sm:px-4">
                <div className="flex gap-1.5">
                  <span className="size-2.5 rounded-full bg-red-500" />
                  <span className="size-2.5 rounded-full bg-amber-400" />
                  <span className="size-2.5 rounded-full bg-green-500" />
                </div>
                <div className="ml-1 flex items-center gap-1 text-[10px] sm:ml-2">
                  <span className="rounded bg-blue-500/20 px-2 py-0.5 font-medium text-blue-300">
                    youtube
                  </span>
                  <span className="px-1 py-0.5 text-zinc-500 sm:px-2">tiktok</span>
                  <span className="hidden px-2 py-0.5 text-zinc-500 sm:inline">instagram</span>
                  <span className="hidden px-2 py-0.5 text-zinc-500 sm:inline">facebook</span>
                </div>
              </div>

              {/* request line */}
              <div className="overflow-x-auto px-3 pb-2 pt-3 font-mono text-[11px] sm:px-4 md:text-xs">
                <span className="rounded bg-sky-500/20 px-1.5 py-0.5 font-semibold text-sky-300">
                  GET
                </span>{" "}
                <span className="text-zinc-400">/v1/</span>
                <span className="text-green-400">youtube/summarize</span>
                <span className="text-zinc-600">?url=…dQw4w9WgXcQ</span>
              </div>

              {/* response status bar */}
              <div className="flex items-center gap-2 border-y border-white/10 bg-white/[0.03] px-3 py-1.5 font-mono text-[10px] sm:gap-3 sm:px-4">
                <span className="flex items-center gap-1 text-green-400">
                  <span className="size-1.5 rounded-full bg-green-400" />
                  200 OK
                </span>
                <span className="text-zinc-500">312 ms</span>
                <span className="text-sky-400">4 credits</span>
                <span className="ml-auto rounded bg-amber-400/15 px-1.5 py-0.5 text-amber-300">
                  cached 24h
                </span>
              </div>

              {/* JSON response body */}
              <pre className="overflow-x-auto px-3 py-3 font-mono text-[10px] leading-relaxed sm:px-4 sm:text-[11px] md:text-xs">
                <code>
                  <span className="text-zinc-500">{"{"}</span>
                  {"\n  "}
                  <span className="text-sky-300">&quot;platform&quot;</span>
                  <span className="text-zinc-500">: </span>
                  <span className="text-emerald-400">&quot;youtube&quot;</span>
                  <span className="text-zinc-500">,</span>
                  {"\n  "}
                  <span className="text-sky-300">&quot;title&quot;</span>
                  <span className="text-zinc-500">: </span>
                  <span className="text-emerald-400">
                    &quot;INNA - Amazing&quot;
                  </span>
                  <span className="text-zinc-500">,</span>
                  {"\n  "}
                  <span className="text-sky-300">&quot;summary&quot;</span>
                  <span className="text-zinc-500">: </span>
                  <span className="text-emerald-400">
                    &quot;An energetic music video…&quot;
                  </span>
                  <span className="text-zinc-500">,</span>
                  {"\n  "}
                  <span className="text-sky-300">&quot;keyPoints&quot;</span>
                  <span className="text-zinc-500">: [</span>
                  <span className="text-emerald-400">&quot;hook&quot;</span>
                  <span className="text-zinc-500">, </span>
                  <span className="text-emerald-400">&quot;chorus&quot;</span>
                  <span className="text-zinc-500">],</span>
                  {"\n  "}
                  <span className="text-sky-300">&quot;sentiment&quot;</span>
                  <span className="text-zinc-500">: </span>
                  <span className="text-emerald-400">&quot;positive&quot;</span>
                  <span className="text-zinc-500">,</span>
                  {"\n  "}
                  <span className="text-sky-300">&quot;stats&quot;</span>
                  <span className="text-zinc-500">: {"{"} </span>
                  <span className="text-sky-300">&quot;views&quot;</span>
                  <span className="text-zinc-500">: </span>
                  <span className="text-amber-300">1284339</span>
                  <span className="text-zinc-500">, </span>
                  <span className="text-sky-300">&quot;likes&quot;</span>
                  <span className="text-zinc-500">: </span>
                  <span className="text-amber-300">48201</span>
                  <span className="text-zinc-500"> {"}"}</span>
                  {"\n"}
                  <span className="text-zinc-500">{"}"}</span>
                </code>
              </pre>
            </div>
          </div>
        </div>
      </div>

      <canvas
        className="pointer-events-none absolute inset-0 h-screen w-full"
        id="canvas"
      />
    </section>
  );
}
