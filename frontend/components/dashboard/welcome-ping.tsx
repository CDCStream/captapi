"use client";

import { useEffect } from "react";
import { api } from "@/lib/api-client";

/** Fires the one-time welcome email after the user reaches the dashboard.
 *  The backend is idempotent (guarded by credit_balances.welcomed_at), so
 *  calling this on every load is safe. */
export function WelcomePing() {
  useEffect(() => {
    api.sendWelcome().catch(() => {});
  }, []);
  return null;
}
