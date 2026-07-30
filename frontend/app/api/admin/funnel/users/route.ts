import { NextRequest, NextResponse } from "next/server";
import { loadFunnelUsers } from "@/lib/funnel-data";
import { requireFunnelAdmin } from "@/lib/require-funnel-admin";

export const runtime = "nodejs";
export const dynamic = "force-dynamic";

export async function GET(req: NextRequest) {
  const gate = await requireFunnelAdmin();
  if (!gate.ok) return gate.response;
  const paidOnly = req.nextUrl.searchParams.get("paid") === "1";
  const data = await loadFunnelUsers(gate.sb, { paidOnly });
  return NextResponse.json(data);
}
