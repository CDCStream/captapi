"use client";

import { useEffect } from "react";
import Link from "next/link";
import { Plus } from "lucide-react";
import {
  renderCanvas,
  ShineBorder,
  TypeWriter,
} from "@/components/ui/hero-designali";
import { GoogleButton } from "@/components/auth/google-button";
import { Button } from "@/components/ui/button";

const platformsTyped = [
  "YouTube",
  "TikTok",
  "Instagram",
  "Facebook",
  "Shorts",
  "Reels",
];

export function CaptapiHero() {
  useEffect(() => {
    renderCanvas();
  }, []);

  return (
    <section id="home" className="relative overflow-hidden">
      {/* grid backdrop */}
      <div className="absolute inset-0 top-[300px] -z-10 h-[400px] w-full bg-[linear-gradient(to_right,#cbd5e1_1px,transparent_1px),linear-gradient(to_bottom,#cbd5e1_1px,transparent_1px)] bg-[size:3rem_3rem] opacity-30 [mask-image:radial-gradient(ellipse_80%_50%_at_50%_0%,#000_70%,transparent_110%)] dark:bg-[linear-gradient(to_right,#1e293b_1px,transparent_1px),linear-gradient(to_bottom,#1e293b_1px,transparent_1px)]" />
      {/* top glow */}
      <div className="absolute left-1/2 top-0 -z-10 h-[400px] w-[700px] -translate-x-1/2 rounded-full bg-gradient-to-b from-blue-500/20 to-transparent blur-3xl" />

      <div className="flex flex-col items-center justify-center px-6 text-center">
        {/* badge pill */}
        <div className="mb-6 mt-10 sm:justify-center md:mb-6 md:mt-28">
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

        <div className="mx-auto max-w-5xl">
          {/* headline box with plus corners */}
          <div className="relative mx-auto h-full border border-border bg-background p-6 py-12 [mask-image:radial-gradient(800rem_96rem_at_center,white,transparent)]">
            <Plus
              strokeWidth={4}
              className="absolute -left-5 -top-5 h-10 w-10 text-primary"
            />
            <Plus
              strokeWidth={4}
              className="absolute -bottom-5 -left-5 h-10 w-10 text-primary"
            />
            <Plus
              strokeWidth={4}
              className="absolute -right-5 -top-5 h-10 w-10 text-primary"
            />
            <Plus
              strokeWidth={4}
              className="absolute -bottom-5 -right-5 h-10 w-10 text-primary"
            />

            <h1 className="flex flex-col text-center text-4xl font-semibold leading-none tracking-tight md:text-7xl">
              <span>
                One API for getting{" "}
                <span className="gradient-text">
                  structured data from Social Media
                </span>{" "}
                video
              </span>
            </h1>

            <div className="mt-4 flex items-center justify-center gap-1">
              <span className="relative flex h-3 w-3 items-center justify-center">
                <span className="absolute inline-flex h-full w-full animate-ping rounded-full bg-green-500 opacity-75" />
                <span className="relative inline-flex h-2 w-2 rounded-full bg-green-500" />
              </span>
              <p className="text-xs text-green-500">
                31 endpoints live across 4 platforms
              </p>
            </div>
          </div>

          {/* subtext with typewriter */}
          <p className="text-primary/60 mx-auto max-w-2xl py-6 text-base md:text-lg">
            Extract transcripts, AI summaries, comments, downloads &amp;
            engagement metrics from{" "}
            <span className="font-semibold text-primary">
              <TypeWriter strings={platformsTyped} />
            </span>{" "}
            — with a single request.
          </p>

          {/* CTAs */}
          <div className="flex items-center justify-center gap-3">
            <Link href="/signup">
              <ShineBorder
                borderWidth={3}
                className="h-auto w-auto cursor-pointer border bg-white/5 p-1 backdrop-blur-md dark:bg-black/5"
                color={["#3b82f6", "#0ea5e9", "#06b6d4"]}
              >
                <Button className="w-full rounded-2xl">
                  Start Free — 100 credits
                </Button>
              </ShineBorder>
            </Link>
            <GoogleButton className="w-auto rounded-2xl" />
          </div>
          <p className="mt-3 text-xs text-muted-foreground">
            No credit card required.
          </p>

          {/* API client mockup */}
          <div className="relative mx-auto mt-14 w-full max-w-2xl text-left">
            <div className="absolute -inset-4 -z-10 rounded-3xl bg-gradient-to-br from-blue-500/20 to-sky-400/10 blur-2xl" />
            <div className="relative overflow-hidden rounded-xl border border-white/10 bg-zinc-950 shadow-2xl">
              {/* window bar with platform tabs */}
              <div className="flex items-center gap-3 border-b border-white/10 px-4 py-2.5">
                <div className="flex gap-1.5">
                  <span className="size-2.5 rounded-full bg-red-500" />
                  <span className="size-2.5 rounded-full bg-amber-400" />
                  <span className="size-2.5 rounded-full bg-green-500" />
                </div>
                <div className="ml-2 flex items-center gap-1 text-[10px]">
                  <span className="rounded bg-blue-500/20 px-2 py-0.5 font-medium text-blue-300">
                    youtube
                  </span>
                  <span className="px-2 py-0.5 text-zinc-500">tiktok</span>
                  <span className="px-2 py-0.5 text-zinc-500">instagram</span>
                  <span className="px-2 py-0.5 text-zinc-500">facebook</span>
                </div>
              </div>

              {/* request line */}
              <div className="px-4 pb-2 pt-3 font-mono text-[11px] md:text-xs">
                <span className="rounded bg-sky-500/20 px-1.5 py-0.5 font-semibold text-sky-300">
                  GET
                </span>{" "}
                <span className="text-zinc-400">/v1/</span>
                <span className="text-green-400">youtube/summarize</span>
                <span className="text-zinc-600">?url=…dQw4w9WgXcQ</span>
              </div>

              {/* response status bar */}
              <div className="flex items-center gap-3 border-y border-white/10 bg-white/[0.03] px-4 py-1.5 font-mono text-[10px]">
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
              <pre className="overflow-x-auto px-4 py-3 font-mono text-[11px] leading-relaxed md:text-xs">
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

      {/* mouse-trail canvas */}
      <canvas
        className="pointer-events-none absolute inset-0 mx-auto"
        id="canvas"
      />
    </section>
  );
}
