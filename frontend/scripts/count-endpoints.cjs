const fs = require("fs");
const t = fs.readFileSync("lib/api-catalog.ts", "utf8");
const slugs = [...t.matchAll(/slug:\s*"([a-z0-9-]+)"/g)].map((m) => m[1]);
const uniq = [...new Set(slugs)];
console.log("catalog endpoints:", uniq.length);
const gen = fs.readFileSync("lib/api-examples.generated.ts", "utf8");
const ex = [...new Set([...gen.matchAll(/"([a-z0-9-]+)":\s*\{/g)].map((m) => m[1]))];
const withExample = uniq.filter((s) => ex.includes(s));
const withoutExample = uniq.filter((s) => !ex.includes(s));
console.log("with generated example:", withExample.length);
console.log("without example:", withoutExample.length);
// group missing by platform prefix
const groups = {};
for (const s of withoutExample) {
  const p = s.split("-")[0];
  groups[p] = groups[p] || [];
  groups[p].push(s);
}
for (const [p, list] of Object.entries(groups).sort()) {
  console.log(`  ${p} (${list.length}): ${list.join(", ")}`);
}
