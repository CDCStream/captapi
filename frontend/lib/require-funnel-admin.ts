import { NextResponse } from "next/server";
import { createClient } from "@/lib/supabase/server";
import { getServiceClient } from "@/lib/supabase/admin";
import { isFunnelAdmin } from "@/lib/funnel-admin";

export async function requireFunnelAdmin(): Promise<
  | { ok: true; userId: string; sb: NonNullable<ReturnType<typeof getServiceClient>> }
  | { ok: false; response: NextResponse }
> {
  const auth = await createClient();
  const {
    data: { user },
  } = await auth.auth.getUser();
  if (!user || !isFunnelAdmin(user.id)) {
    return {
      ok: false,
      response: NextResponse.json({ error: "forbidden" }, { status: 403 }),
    };
  }
  const sb = getServiceClient();
  if (!sb) {
    return {
      ok: false,
      response: NextResponse.json({ error: "supabase not configured" }, { status: 500 }),
    };
  }
  return { ok: true, userId: user.id, sb };
}
