import { lintFieldDescPlatformBleed } from "../frontend/lib/api-catalog.ts";

const errors = lintFieldDescPlatformBleed();
if (errors.length) {
  console.error(`field-desc platform bleed: ${errors.length} issue(s)`);
  for (const e of errors.slice(0, 80)) console.error(" -", e);
  if (errors.length > 80) console.error(` … +${errors.length - 80} more`);
  process.exit(1);
}
console.log("field-desc platform bleed: ok");
