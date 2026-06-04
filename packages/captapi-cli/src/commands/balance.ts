import { apiGet, printJson, c } from "../client.js";

interface UsageResponse {
  data?: {
    balance?: {
      plan?: string;
      subscription_credits?: number;
      topup_credits?: number;
      total_credits?: number;
      subscription_renews_at?: string | null;
    };
    recent_requests?: Array<{
      endpoint?: string;
      credits_used?: number;
      cache_hit?: boolean;
      status_code?: number;
      created_at?: string;
    }>;
  };
}

export async function balance(opts: { json?: boolean }): Promise<void> {
  const body = (await apiGet("/v1/account/usage", { limit: 5 })) as UsageResponse;
  if (opts.json) {
    printJson(body);
    return;
  }
  const bal = body.data?.balance ?? {};
  const total = bal.total_credits ?? 0;
  const color = total <= 0 ? c.red : total < 50 ? c.yellow : c.green;
  console.log(c.bold("Captapi balance"));
  console.log(`  Plan:            ${bal.plan ?? "free"}`);
  console.log(`  Total credits:   ${color(String(total))}`);
  console.log(`    subscription:  ${bal.subscription_credits ?? 0}`);
  console.log(`    top-up:        ${bal.topup_credits ?? 0}`);
  if (bal.subscription_renews_at)
    console.log(`  Renews:          ${bal.subscription_renews_at}`);

  const recent = body.data?.recent_requests ?? [];
  if (recent.length) {
    console.log("\n" + c.bold("Recent requests"));
    for (const r of recent) {
      const tag = r.cache_hit ? c.dim("[cache]") : "";
      console.log(
        `  ${c.dim(r.created_at ?? "")}  ${r.endpoint ?? "?"}  ` +
          `${r.credits_used ?? 0}cr ${r.status_code ?? ""} ${tag}`.trimEnd(),
      );
    }
  }
}
