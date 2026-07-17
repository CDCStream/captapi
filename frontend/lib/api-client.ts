"use client";

import { createClient } from "@/lib/supabase/client";

const API_URL = process.env.NEXT_PUBLIC_API_URL || "http://localhost:8000";

async function authHeader(): Promise<Record<string, string>> {
  const sb = createClient();
  const { data } = await sb.auth.getSession();
  const token = data.session?.access_token;
  return token ? { Authorization: `Bearer ${token}` } : {};
}

export async function apiFetch<T = unknown>(
  path: string,
  init: RequestInit = {},
): Promise<T> {
  const headers = {
    "Content-Type": "application/json",
    ...(await authHeader()),
    ...(init.headers || {}),
  };
  const res = await fetch(`${API_URL}${path}`, { ...init, headers });
  if (!res.ok) {
    const body = await res.text();
    throw new Error(`${res.status}: ${body}`);
  }
  return res.json();
}

export interface ApiKey {
  id: string;
  name: string;
  key_prefix: string;
  last_used_at: string | null;
  created_at: string;
  revoked_at: string | null;
}

export interface CreatedKey extends ApiKey {
  key: string;
  warning: string;
}

export const api = {
  listKeys: () => apiFetch<{ keys: ApiKey[] }>("/v1/auth/keys"),
  createKey: (name: string) =>
    apiFetch<CreatedKey>("/v1/auth/keys", {
      method: "POST",
      body: JSON.stringify({ name }),
    }),
  revokeKey: (id: string) =>
    apiFetch<{ revoked: boolean }>(`/v1/auth/keys/${id}`, {
      method: "DELETE",
    }),
  createCheckout: (body: {
    plan?: string;
    cycle?: "monthly" | "yearly";
    pack?: string;
  }) =>
    apiFetch<{
      provider: string;
      url?: string | null;
      transaction_id?: string | null;
    }>("/v1/billing/checkout", {
      method: "POST",
      body: JSON.stringify(body),
    }),
  createPortal: () =>
    apiFetch<{ url: string }>("/v1/billing/portal", { method: "POST" }),
  getSubscription: () =>
    apiFetch<{
      active: boolean;
      status?: string;
      plan?: string;
      current_period_end?: string | null;
      cancel_at_period_end?: boolean;
    }>("/v1/billing/subscription"),
  changePlan: (plan: string, cycle: "monthly" | "yearly" = "monthly") =>
    apiFetch<{ plan: string; credits: number }>(
      "/v1/billing/subscription/change-plan",
      { method: "POST", body: JSON.stringify({ plan, cycle }) },
    ),
  cancelSubscription: () =>
    apiFetch<{ cancel_at_period_end: boolean }>(
      "/v1/billing/subscription/cancel",
      { method: "POST" },
    ),
  reactivateSubscription: () =>
    apiFetch<{ cancel_at_period_end: boolean }>(
      "/v1/billing/subscription/reactivate",
      { method: "POST" },
    ),
  sendWelcome: () =>
    apiFetch<{ data: { sent: boolean } }>("/v1/account/welcome", {
      method: "POST",
    }),
};
