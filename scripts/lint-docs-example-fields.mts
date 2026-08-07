/**
 * Fail when docs promise a response field that the generated example lacks.
 * Run after python backend/gen_examples.py.
 */
import { lintDocsExampleFieldCoverage } from "../frontend/lib/api-catalog.ts";

const errors = lintDocsExampleFieldCoverage();
if (errors.length) {
  console.error("docs example field coverage: " + String(errors.length) + " issues");
  for (const e of errors.slice(0, 80)) console.error(" -", e);
  if (errors.length > 80) console.error(" ... +" + String(errors.length - 80) + " more");
  process.exit(1);
}
console.log("docs example field coverage: ok");
