// One-shot audit: list null / empty fields in the live example snapshots so we
// can prioritize mapping fixes against competitor output quality.
const fs = require("fs");

const src = fs.readFileSync("lib/api-examples.generated.ts", "utf8");
const start = src.indexOf("= {");
const end = src.lastIndexOf("};");
const obj = JSON.parse(src.slice(start + 2, end + 1));

const issues = {};
function add(slug, msg) {
  (issues[slug] ||= []).push(msg);
}
function walk(slug, path, v) {
  if (v === null) return add(slug, `${path} = null`);
  if (Array.isArray(v)) {
    if (v.length === 0) return add(slug, `${path} = []`);
    return walk(slug, `${path}[0]`, v[0]);
  }
  if (typeof v === "object") {
    for (const [k, val] of Object.entries(v)) walk(slug, path ? `${path}.${k}` : k, val);
    return;
  }
  if (v === "") add(slug, `${path} = empty-string`);
}
for (const [slug, data] of Object.entries(obj)) walk(slug, "", data);

const slugs = Object.keys(issues).sort();
console.log(`Endpoints with null/empty fields: ${slugs.length} of ${Object.keys(obj).length}`);
for (const s of slugs) console.log(`\n${s}:\n  ${issues[s].join("\n  ")}`);
