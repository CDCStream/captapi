import { apiGet, printJson, c } from "../client.js";

interface UsageResponse {
  data?: {
    balance?: {
      plan?: string;
      monthlyQuota?: number;
      subscriptionCredits?: number;
      topupCredits?: number;
      totalCredits?: number;
      subscriptionRenewsAt?: string | null;
    };
    recentRequests?: Array<{
      endpoint?: string;
      creditsUsed?: number;
      cacheHit?: boolean;
      statusCode?: number;
      createdAt?: string;
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
  const total = bal.totalCredits ?? 0;
  const color = total <= 0 ? c.red : total < 50 ? c.yellow : c.green;
  console.log(c.bold("Captapi balance"));
  console.log(`  Plan:            ${bal.plan ?? "free"}`);
  console.log(`  Total credits:   ${color(String(total))}`);
  console.log(`    subscription:  ${bal.subscriptionCredits ?? 0}`);
  console.log(`    top-up:        ${bal.topupCredits ?? 0}`);
  if (bal.subscriptionRenewsAt)
    console.log(`  Renews:          ${bal.subscriptionRenewsAt}`);

  const recent = body.data?.recentRequests ?? [];
  if (recent.length) {
    console.log("\n" + c.bold("Recent requests"));
    for (const r of recent) {
      const tag = r.cacheHit ? c.dim("[cache]") : "";
      console.log(
        `  ${c.dim(r.createdAt ?? "")}  ${r.endpoint ?? "?"}  ` +
          `${r.creditsUsed ?? 0}cr ${r.statusCode ?? ""} ${tag}`.trimEnd(),
      );
    }
  }
}
