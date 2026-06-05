import { readFileSync } from "node:fs";
import { fileURLToPath } from "node:url";

import { Actor } from "apify";

const endpoints = JSON.parse(
  readFileSync(new URL("./endpoints.json", import.meta.url), "utf8"),
);

await Actor.init();

try {
  const input = (await Actor.getInput()) ?? {};
  const { apiKey, operation, baseUrl } = input;

  if (!apiKey) {
    throw new Error(
      "Missing `apiKey`. Provide your capt_live_... key from https://captapi.com/dashboard/api-keys.",
    );
  }
  if (!operation) {
    throw new Error("Missing `operation`. Pick which Captapi endpoint to call.");
  }

  const ep = endpoints.find((e) => e.tool === operation);
  if (!ep) {
    throw new Error(
      `Unknown operation "${operation}". See the Operation dropdown for valid values.`,
    );
  }

  // Build the query string from this operation's declared params.
  const qs = new URLSearchParams();
  const missing = [];
  for (const p of ep.params) {
    const value = input[p.name];
    if (value === undefined || value === null || value === "") {
      if (p.required) missing.push(p.name);
      continue;
    }
    qs.set(p.name, String(value));
  }
  if (missing.length) {
    throw new Error(
      `Operation "${operation}" requires: ${missing.join(", ")}. Fill the matching field(s) in the input.`,
    );
  }

  const base = (baseUrl || "https://api.captapi.com").replace(/\/+$/, "");
  const query = qs.toString();
  const requestUrl = `${base}${ep.path}${query ? `?${query}` : ""}`;

  await Actor.setStatusMessage(`Calling ${operation}...`);

  let res;
  try {
    res = await fetch(requestUrl, {
      headers: {
        Authorization: `Bearer ${apiKey}`,
        Accept: "application/json",
      },
    });
  } catch (err) {
    throw new Error(`Network error calling Captapi: ${err.message}`);
  }

  let body = null;
  try {
    body = await res.json();
  } catch {
    body = null;
  }

  if (!res.ok) {
    const detail =
      (body && (body.detail || body.error || body.message)) || res.statusText;
    await Actor.pushData({
      operation,
      ok: false,
      status: res.status,
      error: detail,
    });
    throw new Error(`Captapi ${operation} failed [${res.status}]: ${detail}`);
  }

  const data = body && "data" in body ? body.data : body;
  await Actor.pushData({
    operation,
    ok: true,
    cached: body?.cached ?? null,
    creditsUsed: body?.creditsUsed ?? null,
    data,
  });

  await Actor.setStatusMessage(`Done: ${operation}`);
  await Actor.exit();
} catch (err) {
  await Actor.fail(err instanceof Error ? err.message : String(err));
}
