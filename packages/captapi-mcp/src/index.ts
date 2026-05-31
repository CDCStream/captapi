#!/usr/bin/env node
/**
 * Captapi MCP server.
 *
 * Exposes every Captapi REST endpoint as an MCP tool so AI agents
 * (Claude, Cursor, VS Code, and any MCP-compatible client) can pull
 * structured social-media data with a single tool call.
 *
 * Auth: set CAPTAPI_API_KEY to your `capt_live_...` / `capt_test_...` key.
 * Base URL override (optional): CAPTAPI_BASE_URL (default https://api.captapi.com).
 */

import { McpServer } from "@modelcontextprotocol/sdk/server/mcp.js";
import { StdioServerTransport } from "@modelcontextprotocol/sdk/server/stdio.js";
import { z } from "zod";
import { ENDPOINTS, describe, type Endpoint } from "./catalog.js";

const API_KEY = process.env.CAPTAPI_API_KEY?.trim();
const BASE_URL = (
  process.env.CAPTAPI_BASE_URL?.trim() || "https://api.captapi.com"
).replace(/\/$/, "");

const VERSION = "0.1.0";

type ToolArgs = {
  url?: string;
  q?: string;
  limit?: number;
  language?: string;
};

/** Build the Zod raw-shape input schema for an endpoint. */
function inputSchema(e: Endpoint): Record<string, z.ZodTypeAny> {
  const shape: Record<string, z.ZodTypeAny> = {};

  if (e.category === "search") {
    shape.q = z.string().describe("Search query or keywords.");
  } else {
    shape.url = z
      .string()
      .url()
      .describe(
        e.category === "channel"
          ? "Public profile / channel URL."
          : e.category === "list"
            ? "Public channel, profile, playlist, group, or music URL."
            : "Public video / post URL.",
      );
  }

  if (["comments", "search", "list"].includes(e.category)) {
    shape.limit = z
      .number()
      .int()
      .positive()
      .max(1000)
      .optional()
      .describe("Max items to return (default 20). Billed per result.");
  }

  if (e.category === "transcript" || e.category === "summarize") {
    shape.language = z
      .string()
      .optional()
      .describe('Preferred caption language as an ISO code, e.g. "en".');
  }

  return shape;
}

async function callEndpoint(e: Endpoint, args: ToolArgs) {
  if (!API_KEY) {
    return {
      isError: true as const,
      content: [
        {
          type: "text" as const,
          text:
            "CAPTAPI_API_KEY is not set. Add your Captapi key (capt_live_...) " +
            "to the MCP server env. Get one at https://captapi.com/dashboard/api-keys.",
        },
      ],
    };
  }

  const qs = new URLSearchParams();
  if (args.url) qs.set("url", args.url);
  if (args.q) qs.set("q", args.q);
  if (typeof args.limit === "number") qs.set("limit", String(args.limit));
  if (args.language) qs.set("language", args.language);

  const requestUrl = `${BASE_URL}${e.path}?${qs.toString()}`;

  let res: Response;
  try {
    res = await fetch(requestUrl, {
      method: "GET",
      headers: {
        Authorization: `Bearer ${API_KEY}`,
        Accept: "application/json",
        "User-Agent": `captapi-mcp/${VERSION}`,
      },
    });
  } catch (err) {
    return {
      isError: true as const,
      content: [
        {
          type: "text" as const,
          text: `Network error calling Captapi: ${String(err)}`,
        },
      ],
    };
  }

  const raw = await res.text();
  let body: unknown;
  try {
    body = JSON.parse(raw);
  } catch {
    body = raw;
  }

  if (!res.ok) {
    const detail =
      body && typeof body === "object" && "detail" in body
        ? (body as { detail: unknown }).detail
        : body;
    let hint = "";
    if (res.status === 401)
      hint = " Check that CAPTAPI_API_KEY is a valid, non-revoked key.";
    else if (res.status === 402)
      hint =
        " You are out of credits. Top up at https://captapi.com/dashboard/billing.";
    else if (res.status === 429)
      hint = " Rate limit reached — slow down or upgrade your plan.";
    return {
      isError: true as const,
      content: [
        {
          type: "text" as const,
          text: `Captapi request failed (HTTP ${res.status}): ${JSON.stringify(
            detail,
          )}.${hint}`,
        },
      ],
    };
  }

  return {
    content: [
      {
        type: "text" as const,
        text: typeof body === "string" ? body : JSON.stringify(body, null, 2),
      },
    ],
  };
}

async function main() {
  const server = new McpServer({
    name: "captapi",
    version: VERSION,
  });

  for (const e of ENDPOINTS) {
    server.registerTool(
      e.tool,
      {
        title: e.name,
        description: describe(e),
        inputSchema: inputSchema(e),
      },
      async (args: ToolArgs) => callEndpoint(e, args),
    );
  }

  const transport = new StdioServerTransport();
  await server.connect(transport);
  console.error(
    `[captapi-mcp] ready on stdio — ${ENDPOINTS.length} tools, base ${BASE_URL}` +
      (API_KEY ? "" : " (warning: CAPTAPI_API_KEY not set)"),
  );
}

main().catch((err) => {
  console.error("[captapi-mcp] fatal:", err);
  process.exit(1);
});
