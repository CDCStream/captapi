import { NextRequest, NextResponse } from "next/server";
import { getEndpoint } from "@/lib/api-catalog";
import { getServiceClient } from "@/lib/supabase/admin";
import { createClient } from "@/lib/supabase/server";

export const runtime = "nodejs";
export const dynamic = "force-dynamic";

export async function POST(req: NextRequest) {
  const sb = getServiceClient();
  if (!sb) {
    return NextResponse.json(
      { error: "Supabase service role not configured" },
      { status: 500 },
    );
  }

  let body: Record<string, unknown>;
  try {
    body = (await req.json()) as Record<string, unknown>;
  } catch {
    return NextResponse.json({ error: "invalid JSON body" }, { status: 400 });
  }

  const message = String(body.message ?? "").trim();
  if (message.length < 3 || message.length > 5000) {
    return NextResponse.json(
      { error: "Please describe the bug (3-5000 characters)." },
      { status: 400 },
    );
  }

  const rawSlug = String(body.endpointSlug ?? "").trim();
  const endpointSlug = rawSlug && getEndpoint(rawSlug) ? rawSlug : null;

  const rawEmail = String(body.email ?? "").trim().slice(0, 320);
  const email = rawEmail && rawEmail.includes("@") ? rawEmail : null;

  const page = String(body.page ?? "").trim().slice(0, 500) || null;

  // Attach the logged-in reporter server-side when a session cookie exists.
  let userId: string | null = null;
  let userEmail: string | null = null;
  try {
    const auth = await createClient();
    const {
      data: { user },
    } = await auth.auth.getUser();
    if (user) {
      userId = user.id;
      userEmail = user.email ?? null;
    }
  } catch {
    // No session — anonymous report is fine.
  }

  const { error } = await sb.from("bug_reports").insert({
    endpoint_slug: endpointSlug,
    message,
    email,
    user_id: userId,
    user_email: userEmail,
    page,
  });
  if (error) {
    return NextResponse.json({ error: error.message }, { status: 500 });
  }
  return NextResponse.json({ ok: true });
}
