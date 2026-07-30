import { NextResponse } from "next/server";
import { loadFunnelOverview } from "@/lib/funnel-data";
import { requireFunnelAdmin } from "@/lib/require-funnel-admin";

export const runtime = "nodejs";
export const dynamic = "force-dynamic";

export async function GET() {
  const gate = await requireFunnelAdmin();
  if (!gate.ok) return gate.response;
  const data = await loadFunnelOverview(gate.sb);
  return NextResponse.json(data);
}
