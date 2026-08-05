/**
 * Fail CI when docs example payloads contain HTML closers that can break
 * Next.js SSR (literal </script> / </body> / </html> -> crawlers see head-only).
 */
import { API_EXAMPLES } from "../frontend/lib/api-examples.generated.ts";
import { API_EXAMPLE_VARIANTS } from "../frontend/lib/api-example-variants.ts";

const POISON = /<\/(?:script|body|html)\b/i;

function walk(value: unknown, path: string, hits: string[]): void {
  if (typeof value === "string") {
    if (POISON.test(value)) hits.push(path + ": contains HTML closer");
    return;
  }
  if (Array.isArray(value)) {
    value.forEach((v, i) => walk(v, path + "[" + i + "]", hits));
    return;
  }
  if (value && typeof value === "object") {
    for (const [k, v] of Object.entries(value as Record<string, unknown>)) {
      walk(v, path ? path + "." + k : k, hits);
    }
  }
}

const hits: string[] = [];
for (const [slug, data] of Object.entries(API_EXAMPLES)) {
  walk(data, slug, hits);
}
for (const [slug, variants] of Object.entries(API_EXAMPLE_VARIANTS)) {
  variants.forEach((v, i) => walk(v.data, slug + "#" + i, hits));
}

if (hits.length) {
  console.error("docs example SSR poison: " + hits.length + " issue(s)");
  for (const h of hits.slice(0, 40)) console.error(" -", h);
  if (hits.length > 40) console.error(" ... +" + (hits.length - 40) + " more");
  process.exit(1);
}
console.log("docs example SSR poison: ok");
