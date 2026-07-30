import { NextRequest, NextResponse } from "next/server";
import { isFunnelExcluded } from "@/lib/funnel-admin";
import { loadUserJourney } from "@/lib/funnel-data";
import { requireFunnelAdmin } from "@/lib/require-funnel-admin";

export const runtime = "nodejs";
export const dynamic = "force-dynamic";

type Ctx = { params: Promise<{ userId: string }> };

export async function GET(_req: NextRequest, ctx: Ctx) {
  const gate = await requireFunnelAdmin();
  if (!gate.ok) return gate.response;
  const { userId } = await ctx.params;

  if (!userId || isFunnelExcluded(userId)) {
    return NextResponse.json({ error: "user not available" }, { status: 404 });
  }

  const data = await loadUserJourney(gate.sb, userId);
  return NextResponse.json(data);
}
