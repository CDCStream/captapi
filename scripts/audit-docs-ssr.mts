/**
 * Live SSR audit for every /apis/{slug} docs page.
 *
 * Usage:
 *   npx tsx scripts/audit-docs-ssr.mts
 *   WEB_BASE=https://captapi.com npx tsx scripts/audit-docs-ssr.mts
 *
 * Fails when a page is missing a body element, has multiple body closers,
 * tiny visible text, or lacks the endpoint name.
 */
import { ALL_ENDPOINTS, PLATFORM_PAGES, platformSlug } from "../frontend/lib/api-catalog.ts";

const BASE = (process.env.WEB_BASE || "https://captapi.com").replace(/\/$/, "");
const UA = process.env.AUDIT_UA || "captapi-docs-ssr-audit/1.0";

type Row = { slug: string; name: string; path: string };

const rows: Row[] = [
  ...PLATFORM_PAGES.map((g) => ({
    slug: platformSlug(g.id),
    name: g.name,
    path: `/apis/${platformSlug(g.id)}`,
  })),
  ...ALL_ENDPOINTS.map((ep) => ({
    slug: ep.slug,
    name: ep.name,
    path: `/apis/${ep.slug}`,
  })),
];

const RE_SCRIPT = new RegExp("<" + "script[\\s\\S]*?<" + "/script>", "gi");
const RE_STYLE = new RegExp("<" + "style[\\s\\S]*?<" + "/style>", "gi");
const RE_BODY_CLOSE = new RegExp("<" + "/body>", "gi");
const RE_BODY_OPEN = new RegExp("<" + "body[\\s>]", "i");

function stripScripts(html: string): string {
  return html.replace(RE_SCRIPT, "");
}

function visibleText(html: string): string {
  return stripScripts(html)
    .replace(RE_STYLE, "")
    .replace(/<[^>]+>/g, " ")
    .replace(/\s+/g, " ")
    .trim();
}

const failures: string[] = [];
let ok = 0;

for (const row of rows) {
  const url = `${BASE}${row.path}`;
  try {
    const res = await fetch(url, {
      headers: { "User-Agent": UA, Accept: "text/html" },
      redirect: "follow",
    });
    const html = await res.text();
    const bodyCloses = (html.match(RE_BODY_CLOSE) || []).length;
    const hasBodyOpen = RE_BODY_OPEN.test(html);
    const text = visibleText(html);
    const nameHint = row.name.slice(0, Math.min(18, row.name.length));
    const firstWord = nameHint.split(" ")[0] || "";

    const problems: string[] = [];
    if (!res.ok) problems.push("HTTP " + res.status);
    if (!hasBodyOpen) problems.push("missing body open tag");
    if (bodyCloses !== 1) problems.push("body close count=" + bodyCloses);
    if (html.length < 8000) problems.push("tiny html (" + html.length + "b)");
    if (text.length < 800) problems.push("tiny visible text (" + text.length + ")");
    if (nameHint && !html.includes(nameHint) && !text.includes(firstWord)) {
      problems.push("missing name hint");
    }

    if (problems.length) {
      failures.push(row.slug + ": " + problems.join("; ") + " (" + url + ")");
    } else {
      ok += 1;
    }
  } catch (e) {
    failures.push(row.slug + ": fetch error " + (e instanceof Error ? e.message : String(e)));
  }
}

console.log("docs SSR audit: " + ok + "/" + rows.length + " ok against " + BASE);
if (failures.length) {
  console.error("failures: " + failures.length);
  for (const f of failures.slice(0, 60)) console.error(" -", f);
  if (failures.length > 60) console.error(" ... +" + (failures.length - 60) + " more");
  process.exit(1);
}
console.log("docs SSR audit: ok");
