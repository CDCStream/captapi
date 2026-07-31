import type { SupabaseClient } from "@supabase/supabase-js";
import { funnelExcludeUserIds, funnelSinceIso } from "@/lib/funnel-admin";

/** PostgREST `in` filter payload for the excluded account ids. */
function excludeFilter(ids: string[]): string {
  return `(${ids.join(",")})`;
}

export async function loadFunnelOverview(sb: SupabaseClient) {
  const since = funnelSinceIso(14);
  const excludeIds = funnelExcludeUserIds();
  const excluded = new Set(excludeIds);
  const notIn = excludeFilter(excludeIds);

  // Funnel step counts come from the same row set as the users table so the
  // cards and filter pills never disagree.
  const [
    usersPayload,
    { data: requestRows },
    { count: sampleCount },
  ] = await Promise.all([
    loadFunnelUsers(sb),
    sb
      .from("requests")
      .select("user_id, endpoint, status_code, response_time_ms, created_at")
      .gte("created_at", since)
      .not("user_id", "in", notIn)
      .order("created_at", { ascending: false })
      .limit(5000),
    sb
      .from("response_samples")
      .select("*", { count: "exact", head: true })
      .gte("created_at", since)
      .not("user_id", "in", notIn),
  ]);

  const paidUsers = new Set(
    usersPayload.users.filter((u) => u.paid && u.userId).map((u) => u.userId!),
  );
  const lastEndpoint = new Map<string, string>();
  const times: number[] = [];
  let errors = 0;
  for (const row of requestRows || []) {
    const uid = row.user_id as string;
    if (!uid || excluded.has(uid)) continue;
    if (!lastEndpoint.has(uid)) {
      lastEndpoint.set(uid, row.endpoint as string);
    }
    if (typeof row.response_time_ms === "number") times.push(row.response_time_ms);
    if ((row.status_code ?? 0) >= 400) errors += 1;
  }

  const dropOff: Record<string, number> = {};
  for (const [uid, ep] of lastEndpoint) {
    if (paidUsers.has(uid)) continue;
    dropOff[ep] = (dropOff[ep] || 0) + 1;
  }
  const topDropOffEndpoints = Object.entries(dropOff)
    .sort((a, b) => b[1] - a[1])
    .slice(0, 12)
    .map(([endpoint, users]) => ({ endpoint, users }));

  times.sort((a, b) => a - b);
  const p50 = times.length ? times[Math.floor(times.length * 0.5)] : null;
  const p95 = times.length ? times[Math.floor(times.length * 0.95)] : null;

  return {
    since,
    excludedUserIds: excludeIds,
    funnel: usersPayload.funnel,
    users: usersPayload.users,
    traffic: {
      requests: (requestRows || []).length,
      errors,
      responseSamples: sampleCount ?? 0,
      latencyMs: { p50, p95 },
    },
    topDropOffEndpoints,
  };
}

export type FunnelUserAgg = {
  /** user uuid or anon_id */
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

/** Funnel cards — must match the users table filter pills (same rows). */
export function funnelStatsFromUsers(users: FunnelUserAgg[]) {
  let signups = 0;
  let apiKeyHolders = 0;
  let apiCallers = 0;
  let checkoutStarted = 0;
  let paid = 0;
  let stillAnon = 0;
  for (const u of users) {
    if (u.kind === "anon") stillAnon += 1;
    if (u.kind === "user" || u.signedUp) signups += 1;
    if (u.hasApiKey) apiKeyHolders += 1;
    if (u.requests > 0) apiCallers += 1;
    if (u.checkoutStarted) checkoutStarted += 1;
    if (u.paid) paid += 1;
  }
  return {
    /** Top of funnel = every identity in the table (anon + users). */
    visitors: users.length,
    stillAnon,
    signups,
    apiKeyHolders,
    apiCallers,
    checkoutStarted,
    paid,
  };
}

export async function loadFunnelUsers(
  sb: SupabaseClient,
  opts?: { paidOnly?: boolean },
): Promise<{
  since: string;
  users: FunnelUserAgg[];
  funnel: ReturnType<typeof funnelStatsFromUsers>;
}> {
  const since = funnelSinceIso(14);
  const excludeIds = funnelExcludeUserIds();
  const excluded = new Set(excludeIds);
  const notIn = excludeFilter(excludeIds);

  const [
    { data: requestRows },
    { data: paidRows },
    { data: balances },
    { data: eventRows },
    { data: apiKeyRows },
    { data: anonPageViews },
    { data: anonEventRows },
    { data: checkoutEventRows },
    { data: signupEventRows },
  ] = await Promise.all([
    sb
      .from("requests")
      .select("user_id, endpoint, status_code, created_at, response_time_ms")
      .gte("created_at", since)
      .not("user_id", "in", notIn)
      .order("created_at", { ascending: false })
      .limit(8000),
    sb
      .from("credit_transactions")
      .select("user_id, amount, type, created_at")
      .gte("created_at", since)
      .gt("amount", 0)
      .in("type", ["topup", "subscription_grant"])
      .not("user_id", "in", notIn)
      .limit(3000),
    sb
      .from("credit_balances")
      .select("user_id, plan, subscription_credits, topup_credits")
      .not("user_id", "in", notIn)
      .limit(5000),
    sb
      .from("events")
      .select("user_id, anon_id, event, path, created_at")
      .gte("created_at", since)
      .not("user_id", "is", null)
      .not("user_id", "in", notIn)
      .order("created_at", { ascending: false })
      .limit(10000),
    // Keys created in-window (same definition as overview "API key").
    sb
      .from("api_keys")
      .select("user_id")
      .gte("created_at", since)
      .not("user_id", "in", notIn)
      .limit(5000),
    // One row per anonymous browser page_view (matches overview Visitors).
    sb
      .from("events")
      .select("anon_id, path, created_at")
      .eq("event", "page_view")
      .gte("created_at", since)
      .is("user_id", null)
      .not("anon_id", "is", null)
      .order("created_at", { ascending: false })
      .limit(20000),
    // Extra anon events (CTA clicks etc.) for event counts / last path.
    sb
      .from("events")
      .select("anon_id, event, path, created_at")
      .gte("created_at", since)
      .is("user_id", null)
      .not("anon_id", "is", null)
      .order("created_at", { ascending: false })
      .limit(10000),
    sb
      .from("events")
      .select("user_id")
      .eq("event", "checkout_started")
      .gte("created_at", since)
      .not("user_id", "is", null)
      .not("user_id", "in", notIn)
      .limit(3000),
    sb
      .from("events")
      .select("user_id, anon_id")
      .eq("event", "signup")
      .gte("created_at", since)
      .limit(5000),
  ]);

  const paidAt = new Map<string, string>();
  const paidAmount = new Map<string, number>();
  for (const row of paidRows || []) {
    const uid = row.user_id as string;
    if (!uid) continue;
    paidAmount.set(uid, (paidAmount.get(uid) || 0) + Number(row.amount || 0));
    if (!paidAt.has(uid)) paidAt.set(uid, row.created_at as string);
  }

  const checkoutUsers = new Set(
    (checkoutEventRows || [])
      .map((r) => r.user_id as string)
      .filter((id) => id && !excluded.has(id)),
  );

  const signedUpUsers = new Set<string>();
  const signedUpAnons = new Set<string>();
  for (const row of signupEventRows || []) {
    const uid = row.user_id as string | null;
    const aid = row.anon_id as string | null;
    if (uid && !excluded.has(uid)) signedUpUsers.add(uid);
    if (aid) signedUpAnons.add(aid);
  }

  // Anon ids that later appear on logged-in events — don't duplicate them as anon rows.
  const claimedAnons = new Set<string>();
  for (const row of eventRows || []) {
    const aid = row.anon_id as string | null;
    if (aid) claimedAnons.add(aid);
  }
  for (const aid of signedUpAnons) claimedAnons.add(aid);

  const eventCount = new Map<string, number>();
  const lastEvent = new Map<string, string>();
  const lastPathByUser = new Map<string, string>();
  for (const row of eventRows || []) {
    const uid = row.user_id as string;
    if (!uid || excluded.has(uid)) continue;
    eventCount.set(uid, (eventCount.get(uid) || 0) + 1);
    if (!lastEvent.has(uid)) {
      lastEvent.set(uid, row.created_at as string);
      if (row.path) lastPathByUser.set(uid, row.path as string);
    }
  }

  const usersWithKeys = new Set(
    (apiKeyRows || [])
      .map((r) => r.user_id as string)
      .filter((id) => id && !excluded.has(id)),
  );

  const emptyUser = (uid: string): FunnelUserAgg => ({
    id: uid,
    kind: "user",
    userId: uid,
    anonId: null,
    requests: 0,
    errors: 0,
    events: 0,
    hasApiKey: usersWithKeys.has(uid),
    signedUp: signedUpUsers.has(uid),
    checkoutStarted: checkoutUsers.has(uid),
    lastAt: null,
    lastEndpoint: null,
    lastPath: null,
    firstAt: null,
    lastEventAt: null,
    paid: paidAt.has(uid),
    paidCredits: paidAmount.get(uid) || 0,
    plan: null,
    creditsLeft: null,
  });

  const byUser = new Map<string, FunnelUserAgg>();
  for (const row of requestRows || []) {
    const uid = row.user_id as string;
    if (!uid || excluded.has(uid)) continue;
    let agg = byUser.get(uid);
    if (!agg) {
      agg = emptyUser(uid);
      byUser.set(uid, agg);
    }
    agg.requests += 1;
    if ((row.status_code ?? 0) >= 400) agg.errors += 1;
    const ts = row.created_at as string;
    if (!agg.lastAt) {
      agg.lastAt = ts;
      agg.lastEndpoint = row.endpoint as string;
    }
    agg.firstAt = ts;
  }

  for (const uid of eventCount.keys()) {
    if (!byUser.has(uid)) byUser.set(uid, emptyUser(uid));
  }
  for (const uid of paidAt.keys()) {
    if (!byUser.has(uid)) byUser.set(uid, emptyUser(uid));
  }
  for (const uid of usersWithKeys) {
    if (!byUser.has(uid)) byUser.set(uid, emptyUser(uid));
  }
  for (const uid of signedUpUsers) {
    if (!byUser.has(uid)) byUser.set(uid, emptyUser(uid));
  }

  for (const agg of byUser.values()) {
    agg.events = eventCount.get(agg.userId!) || 0;
    agg.lastEventAt = lastEvent.get(agg.userId!) || null;
    agg.lastPath = lastPathByUser.get(agg.userId!) || null;
    agg.hasApiKey = usersWithKeys.has(agg.userId!);
    agg.signedUp = true; // present as a user row
    agg.checkoutStarted = checkoutUsers.has(agg.userId!);
  }

  const balMap = new Map(
    (balances || []).map((b) => [
      b.user_id as string,
      b as {
        plan: string;
        subscription_credits: number;
        topup_credits: number;
      },
    ]),
  );
  for (const agg of byUser.values()) {
    const bal = balMap.get(agg.userId!);
    if (bal) {
      agg.plan = bal.plan;
      agg.creditsLeft =
        Number(bal.subscription_credits || 0) + Number(bal.topup_credits || 0);
    }
  }

  // Anonymous visitors (never claimed by a logged-in user in this window).
  // Seed from page_view so the list matches overview Visitors (minus converters).
  const emptyAnon = (aid: string): FunnelUserAgg => ({
    id: aid,
    kind: "anon",
    userId: null,
    anonId: aid,
    requests: 0,
    errors: 0,
    events: 0,
    hasApiKey: false,
    signedUp: false,
    checkoutStarted: false,
    lastAt: null,
    lastEndpoint: null,
    lastPath: null,
    firstAt: null,
    lastEventAt: null,
    paid: false,
    paidCredits: 0,
    plan: null,
    creditsLeft: null,
  });

  const byAnon = new Map<string, FunnelUserAgg>();
  for (const row of anonPageViews || []) {
    const aid = row.anon_id as string;
    if (!aid || claimedAnons.has(aid)) continue;
    let agg = byAnon.get(aid);
    if (!agg) {
      agg = emptyAnon(aid);
      byAnon.set(aid, agg);
    }
    agg.events += 1;
    const ts = row.created_at as string;
    if (!agg.lastEventAt) {
      agg.lastEventAt = ts;
      agg.lastPath = (row.path as string) || null;
    }
    agg.firstAt = ts;
  }
  // Enrich existing page_view visitors only — do not invent extra anon rows
  // from CTA/other events (that inflated the table past the Visitors card).
  for (const row of anonEventRows || []) {
    const aid = row.anon_id as string;
    if (!aid || claimedAnons.has(aid)) continue;
    const agg = byAnon.get(aid);
    if (!agg) continue;
    if ((row.event as string) !== "page_view") {
      agg.events += 1;
    }
    const ts = row.created_at as string;
    if (!agg.lastEventAt || ts > agg.lastEventAt) {
      agg.lastEventAt = ts;
      if (row.path) agg.lastPath = row.path as string;
    }
    if (!agg.firstAt || ts < agg.firstAt) agg.firstAt = ts;
  }

  let users = [...byUser.values(), ...byAnon.values()];
  if (opts?.paidOnly) users = users.filter((u) => u.paid);
  users.sort((a, b) => {
    const aTs = a.lastAt || a.lastEventAt || "";
    const bTs = b.lastAt || b.lastEventAt || "";
    return bTs.localeCompare(aTs);
  });

  return { since, users, funnel: funnelStatsFromUsers(users) };
}

export async function loadUserJourney(sb: SupabaseClient, userId: string) {
  const since = funnelSinceIso(14);

  const [
    authUser,
    { data: balance },
    { data: events },
    { data: requests },
    { data: samples },
    { data: payments },
  ] = await Promise.all([
    sb.auth.admin.getUserById(userId),
    sb
      .from("credit_balances")
      .select("plan, subscription_credits, topup_credits, subscription_renews_at")
      .eq("user_id", userId)
      .maybeSingle(),
    sb
      .from("events")
      .select("id, event, path, properties, anon_id, created_at")
      .eq("user_id", userId)
      .gte("created_at", since)
      .order("created_at", { ascending: true })
      .limit(500),
    sb
      .from("requests")
      .select(
        "id, endpoint, status_code, response_time_ms, credits_used, error_message, created_at",
      )
      .eq("user_id", userId)
      .gte("created_at", since)
      .order("created_at", { ascending: true })
      .limit(500),
    sb
      .from("response_samples")
      .select(
        "id, request_id, endpoint, status_code, truncated, response_json, created_at",
      )
      .eq("user_id", userId)
      .gte("created_at", since)
      .order("created_at", { ascending: true })
      .limit(500),
    sb
      .from("credit_transactions")
      .select("id, type, amount, description, created_at")
      .eq("user_id", userId)
      .gte("created_at", since)
      .order("created_at", { ascending: true })
      .limit(200),
  ]);

  const profile = authUser.data?.user ?? null;

  // Pre-signup / logged-out activity: events rows share the browser anon_id
  // with the user's logged-in events, so pull anonymous rows for those ids too
  // (signup fires before the session exists, so it only has anon_id).
  const anonIds = [
    ...new Set(
      (events || [])
        .map((e) => e.anon_id as string | null)
        .filter((id): id is string => Boolean(id)),
    ),
  ].slice(0, 20);

  let anonEvents: typeof events = [];
  if (anonIds.length) {
    const { data } = await sb
      .from("events")
      .select("id, event, path, properties, anon_id, created_at")
      .is("user_id", null)
      .in("anon_id", anonIds)
      .gte("created_at", since)
      .order("created_at", { ascending: true })
      .limit(300);
    anonEvents = data || [];
  }

  const sampleByRequestId = new Map<string, NonNullable<typeof samples>[number]>();
  const sampleByEndpointTime: Array<{
    endpoint: string;
    created_at: string;
    sample: NonNullable<typeof samples>[number];
  }> = [];
  for (const s of samples || []) {
    if (s.request_id) sampleByRequestId.set(s.request_id as string, s);
    sampleByEndpointTime.push({
      endpoint: s.endpoint as string,
      created_at: s.created_at as string,
      sample: s,
    });
  }

  const usedSampleIds = new Set<string>();
  const requestJourney = (requests || []).map((r) => {
    let sample = sampleByRequestId.get(r.id as string) || null;
    if (!sample) {
      const near = sampleByEndpointTime.find(
        (s) =>
          !usedSampleIds.has(s.sample.id as string) &&
          s.endpoint === r.endpoint &&
          Math.abs(
            new Date(s.created_at).getTime() - new Date(r.created_at as string).getTime(),
          ) < 5000,
      );
      if (near) sample = near.sample;
    }
    if (sample?.id) usedSampleIds.add(sample.id as string);
    return {
      kind: "request" as const,
      id: r.id,
      at: r.created_at,
      endpoint: r.endpoint,
      method: null as string | null,
      statusCode: r.status_code,
      responseTimeMs: r.response_time_ms,
      creditsUsed: r.credits_used,
      errorMessage: r.error_message,
      hasSample: Boolean(sample),
      truncated: sample?.truncated ?? null,
      responseJson: sample?.response_json ?? null,
      sampleId: sample?.id ?? null,
    };
  });

  const seenEventIds = new Set<string>();
  const eventJourney = [...(anonEvents || []), ...(events || [])]
    .filter((e) => {
      const id = e.id as string;
      if (seenEventIds.has(id)) return false;
      seenEventIds.add(id);
      return true;
    })
    .map((e) => ({
      kind: "event" as const,
      id: e.id,
      at: e.created_at,
      event: e.event,
      path: e.path,
      properties: e.properties,
      anonId: e.anon_id,
    }));

  const paymentJourney = (payments || []).map((p) => ({
    kind: "payment" as const,
    id: p.id,
    at: p.created_at,
    type: p.type,
    amount: p.amount,
    description: p.description,
  }));

  const timeline = [...eventJourney, ...requestJourney, ...paymentJourney].sort(
    (a, b) => new Date(a.at as string).getTime() - new Date(b.at as string).getTime(),
  );

  return {
    since,
    user: {
      id: userId,
      email: profile?.email ?? null,
      fullName:
        (profile?.user_metadata?.full_name as string | undefined) ||
        (profile?.user_metadata?.name as string | undefined) ||
        null,
      createdAt: profile?.created_at ?? null,
      plan: balance?.plan ?? null,
      subscriptionCredits: balance?.subscription_credits ?? 0,
      topupCredits: balance?.topup_credits ?? 0,
      renewsAt: balance?.subscription_renews_at ?? null,
    },
    stats: {
      events: eventJourney.length,
      requests: (requests || []).length,
      samples: (samples || []).length,
      payments: (payments || []).length,
    },
    timeline,
  };
}


export async function loadAnonJourney(sb: SupabaseClient, anonId: string) {
  const since = funnelSinceIso(14);

  const { data: events } = await sb
    .from("events")
    .select("id, event, path, properties, anon_id, user_id, created_at")
    .eq("anon_id", anonId)
    .gte("created_at", since)
    .order("created_at", { ascending: true })
    .limit(500);

  const timeline = (events || []).map((e) => ({
    kind: "event" as const,
    id: e.id,
    at: e.created_at,
    event: e.event,
    path: e.path,
    properties: e.properties,
    anonId: e.anon_id,
  }));

  return {
    since,
    anonId,
    stats: {
      events: timeline.length,
      requests: 0,
      samples: 0,
      payments: 0,
    },
    timeline,
  };
}

