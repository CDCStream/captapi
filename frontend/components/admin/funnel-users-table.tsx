"use client";

import Link from "next/link";
import { useMemo, useState } from "react";

export type FunnelUserRow = {
  id: string;
  kind: "user" | "anon";
  userId: string | null;
  anonId: string | null;
  requests: number;
  errors: number;
  events: number;
  hasApiKey: boolean;
  signedUp: boolean;
  checkoutStarted: boolean;
  lastAt: string | null;
  lastEndpoint: string | null;
  lastPath: string | null;
  firstAt: string | null;
  lastEventAt: string | null;
  paid: boolean;
  paidCredits: number;
  plan: string | null;
  creditsLeft: number | null;
};

type Segment =
  | "all"
  | "visitors"
  | "signups"
  | "api_key"
  | "api_callers"
  | "checkout"
  | "paid"
  | "no_api"
  | "no_key";

const SEGMENTS: { id: Segment; label: string }[] = [
  { id: "all", label: "All rows" },
  { id: "visitors", label: "Still anon" },
  { id: "signups", label: "Signups" },
  { id: "api_key", label: "API key created" },
  { id: "api_callers", label: "API callers" },
  { id: "checkout", label: "Checkout started" },
  { id: "paid", label: "Paid" },
  { id: "no_key", label: "No API key" },
  { id: "no_api", label: "No API call" },
];

function shortEp(ep: string | null) {
  if (!ep) return "-";
  return ep.replace(/^\/v1\//, "");
}

function fmtWhen(iso: string | null) {
  if (!iso) return "-";
  try {
    return new Date(iso).toLocaleString();
  } catch {
    return iso;
  }
}

function hrefFor(u: FunnelUserRow) {
  if (u.kind === "anon" && u.anonId) {
    return `/dashboard/admin/funnel/anon/${encodeURIComponent(u.anonId)}`;
  }
  return `/dashboard/admin/funnel/${u.userId}`;
}

export function FunnelUsersTable({ users }: { users: FunnelUserRow[] }) {
  const [segment, setSegment] = useState<Segment>("all");
  const [q, setQ] = useState("");

  const counts = useMemo(() => {
    const c: Record<Segment, number> = {
      all: users.length,
      visitors: 0,
      signups: 0,
      api_key: 0,
      api_callers: 0,
      checkout: 0,
      paid: 0,
      no_api: 0,
      no_key: 0,
    };
    for (const u of users) {
      if (u.kind === "anon") c.visitors += 1;
      if (u.kind === "user" || u.signedUp) c.signups += 1;
      if (u.hasApiKey) c.api_key += 1;
      if (u.requests > 0) c.api_callers += 1;
      if (u.checkoutStarted) c.checkout += 1;
      if (u.paid) c.paid += 1;
      if (u.kind === "user" && u.requests === 0) c.no_api += 1;
      if (u.kind === "user" && !u.hasApiKey) c.no_key += 1;
    }
    return c;
  }, [users]);

  const filtered = useMemo(() => {
    let list = users;
    switch (segment) {
      case "visitors":
        list = list.filter((u) => u.kind === "anon");
        break;
      case "signups":
        list = list.filter((u) => u.kind === "user" || u.signedUp);
        break;
      case "api_key":
        list = list.filter((u) => u.hasApiKey);
        break;
      case "api_callers":
        list = list.filter((u) => u.requests > 0);
        break;
      case "checkout":
        list = list.filter((u) => u.checkoutStarted);
        break;
      case "paid":
        list = list.filter((u) => u.paid);
        break;
      case "no_api":
        list = list.filter((u) => u.kind === "user" && u.requests === 0);
        break;
      case "no_key":
        list = list.filter((u) => u.kind === "user" && !u.hasApiKey);
        break;
      default:
        break;
    }
    const needle = q.trim().toLowerCase();
    if (needle) {
      list = list.filter(
        (u) =>
          u.id.toLowerCase().includes(needle) ||
          (u.userId || "").toLowerCase().includes(needle) ||
          (u.anonId || "").toLowerCase().includes(needle) ||
          (u.lastEndpoint || "").toLowerCase().includes(needle) ||
          (u.lastPath || "").toLowerCase().includes(needle) ||
          (u.plan || "").toLowerCase().includes(needle),
      );
    }
    return list;
  }, [users, segment, q]);

  return (
    <div className="space-y-3">
      <div className="flex flex-wrap gap-2">
        {SEGMENTS.map((s) => {
          const active = segment === s.id;
          return (
            <button
              key={s.id}
              type="button"
              onClick={() => setSegment(s.id)}
              className={
                active
                  ? "rounded-full bg-primary px-3 py-1 text-xs font-medium text-primary-foreground"
                  : "rounded-full border bg-background px-3 py-1 text-xs font-medium text-muted-foreground hover:bg-muted hover:text-foreground"
              }
            >
              {s.label}
              <span className="ml-1 opacity-70">{counts[s.id]}</span>
            </button>
          );
        })}
      </div>

      <div className="flex flex-wrap items-center gap-3">
        <input
          type="search"
          value={q}
          onChange={(e) => setQ(e.target.value)}
          placeholder="Filter by id / path / endpoint / plan"
          className="h-9 w-full max-w-sm rounded-md border bg-background px-3 text-sm"
        />
        <span className="text-xs text-muted-foreground">{filtered.length} rows</span>
      </div>

      <div className="overflow-x-auto rounded-lg border">
        <table className="w-full min-w-[860px] text-left text-sm">
          <thead className="border-b bg-muted/40 text-xs uppercase tracking-wide text-muted-foreground">
            <tr>
              <th className="px-3 py-2 font-medium">Identity</th>
              <th className="px-3 py-2 font-medium">Type</th>
              <th className="px-3 py-2 font-medium">Signup</th>
              <th className="px-3 py-2 font-medium">Plan</th>
              <th className="px-3 py-2 font-medium">API key</th>
              <th className="px-3 py-2 font-medium">Reqs</th>
              <th className="px-3 py-2 font-medium">Events</th>
              <th className="px-3 py-2 font-medium">Last path / endpoint</th>
              <th className="px-3 py-2 font-medium">Last seen</th>
              <th className="px-3 py-2 font-medium">Paid</th>
            </tr>
          </thead>
          <tbody>
            {filtered.map((u) => (
              <tr key={`${u.kind}-${u.id}`} className="border-b last:border-0 hover:bg-muted/30">
                <td className="px-3 py-2">
                  <Link
                    href={hrefFor(u)}
                    className="font-mono text-xs text-primary hover:underline"
                  >
                    {u.id.slice(0, 8)}…
                  </Link>
                </td>
                <td className="px-3 py-2">
                  {u.kind === "anon" ? (
                    <span className="rounded bg-slate-500/10 px-1.5 py-0.5 text-[11px] font-medium text-slate-700">
                      anon
                    </span>
                  ) : (
                    <span className="rounded bg-sky-500/10 px-1.5 py-0.5 text-[11px] font-medium text-sky-700">
                      user
                    </span>
                  )}
                </td>
                <td className="px-3 py-2">
                  {u.kind === "user" || u.signedUp ? (
                    <span className="text-emerald-700">yes</span>
                  ) : (
                    <span className="rounded bg-amber-500/10 px-1.5 py-0.5 text-[11px] font-medium text-amber-700">
                      no
                    </span>
                  )}
                </td>
                <td className="px-3 py-2 text-muted-foreground">{u.plan || "-"}</td>
                <td className="px-3 py-2">
                  {u.kind === "anon" ? (
                    <span className="text-muted-foreground">-</span>
                  ) : u.hasApiKey ? (
                    <span className="text-emerald-700">yes</span>
                  ) : (
                    <span className="rounded bg-amber-500/10 px-1.5 py-0.5 text-[11px] font-medium text-amber-700">
                      no
                    </span>
                  )}
                </td>
                <td className="px-3 py-2">
                  {u.kind === "anon" ? (
                    <span className="text-muted-foreground">-</span>
                  ) : u.requests === 0 ? (
                    <span className="rounded bg-amber-500/10 px-1.5 py-0.5 text-[11px] font-medium text-amber-700">
                      0
                    </span>
                  ) : (
                    u.requests
                  )}
                </td>
                <td className="px-3 py-2">{u.events}</td>
                <td className="px-3 py-2 font-mono text-xs">
                  {u.lastEndpoint ? shortEp(u.lastEndpoint) : u.lastPath || "-"}
                </td>
                <td className="px-3 py-2 text-xs text-muted-foreground">
                  {fmtWhen(u.lastAt || u.lastEventAt)}
                </td>
                <td className="px-3 py-2">
                  {u.paid ? (
                    <span className="text-emerald-700">+{u.paidCredits}</span>
                  ) : (
                    <span className="text-muted-foreground">-</span>
                  )}
                </td>
              </tr>
            ))}
            {!filtered.length && (
              <tr>
                <td colSpan={10} className="px-3 py-8 text-center text-muted-foreground">
                  No rows in this filter.
                </td>
              </tr>
            )}
          </tbody>
        </table>
      </div>
    </div>
  );
}
