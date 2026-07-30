"use client";

import Link from "next/link";
import { useMemo, useState } from "react";

export type FunnelUserRow = {
  userId: string;
  requests: number;
  errors: number;
  lastAt: string | null;
  lastEndpoint: string | null;
  firstAt: string | null;
  paid: boolean;
  paidCredits: number;
  plan: string | null;
  creditsLeft: number | null;
};

function shortEp(ep: string | null) {
  if (!ep) return "—";
  return ep.replace(/^\/v1\//, "");
}

function fmtWhen(iso: string | null) {
  if (!iso) return "—";
  try {
    return new Date(iso).toLocaleString();
  } catch {
    return iso;
  }
}

export function FunnelUsersTable({ users }: { users: FunnelUserRow[] }) {
  const [paidOnly, setPaidOnly] = useState(false);
  const [q, setQ] = useState("");

  const filtered = useMemo(() => {
    let list = users;
    if (paidOnly) list = list.filter((u) => u.paid);
    const needle = q.trim().toLowerCase();
    if (needle) {
      list = list.filter(
        (u) =>
          u.userId.toLowerCase().includes(needle) ||
          (u.lastEndpoint || "").toLowerCase().includes(needle) ||
          (u.plan || "").toLowerCase().includes(needle),
      );
    }
    return list;
  }, [users, paidOnly, q]);

  return (
    <div className="space-y-3">
      <div className="flex flex-wrap items-center gap-3">
        <input
          type="search"
          value={q}
          onChange={(e) => setQ(e.target.value)}
          placeholder="Filter by user id / endpoint / plan"
          className="h-9 w-full max-w-sm rounded-md border bg-background px-3 text-sm"
        />
        <label className="flex items-center gap-2 text-sm text-muted-foreground">
          <input
            type="checkbox"
            checked={paidOnly}
            onChange={(e) => setPaidOnly(e.target.checked)}
            className="size-4 rounded border"
          />
          Paid only
        </label>
        <span className="text-xs text-muted-foreground">{filtered.length} users</span>
      </div>

      <div className="overflow-x-auto rounded-lg border">
        <table className="w-full min-w-[720px] text-left text-sm">
          <thead className="border-b bg-muted/40 text-xs uppercase tracking-wide text-muted-foreground">
            <tr>
              <th className="px-3 py-2 font-medium">User</th>
              <th className="px-3 py-2 font-medium">Plan</th>
              <th className="px-3 py-2 font-medium">Reqs</th>
              <th className="px-3 py-2 font-medium">Errors</th>
              <th className="px-3 py-2 font-medium">Last endpoint</th>
              <th className="px-3 py-2 font-medium">Last seen</th>
              <th className="px-3 py-2 font-medium">Paid</th>
            </tr>
          </thead>
          <tbody>
            {filtered.map((u) => (
              <tr key={u.userId} className="border-b last:border-0 hover:bg-muted/30">
                <td className="px-3 py-2">
                  <Link
                    href={`/dashboard/admin/funnel/${u.userId}`}
                    className="font-mono text-xs text-primary hover:underline"
                  >
                    {u.userId.slice(0, 8)}…
                  </Link>
                </td>
                <td className="px-3 py-2 text-muted-foreground">{u.plan || "—"}</td>
                <td className="px-3 py-2">{u.requests}</td>
                <td className="px-3 py-2">{u.errors}</td>
                <td className="px-3 py-2 font-mono text-xs">{shortEp(u.lastEndpoint)}</td>
                <td className="px-3 py-2 text-xs text-muted-foreground">
                  {fmtWhen(u.lastAt)}
                </td>
                <td className="px-3 py-2">
                  {u.paid ? (
                    <span className="text-emerald-700">+{u.paidCredits}</span>
                  ) : (
                    <span className="text-muted-foreground">—</span>
                  )}
                </td>
              </tr>
            ))}
            {!filtered.length && (
              <tr>
                <td colSpan={7} className="px-3 py-8 text-center text-muted-foreground">
                  No users in this window.
                </td>
              </tr>
            )}
          </tbody>
        </table>
      </div>
    </div>
  );
}
