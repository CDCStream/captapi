// Offline/edge smoke test for the Zapier app definition.
// Run: node smoke.test.mjs   (optionally set CAPTAPI_API_KEY for a live call)
import zapier from "zapier-platform-core";
import { createRequire } from "node:module";

const require = createRequire(import.meta.url);
const App = require("./index.js");
const appTester = zapier.createAppTester(App);
zapier.tools.env.inject();

let failures = 0;
const check = (name, cond, extra = "") => {
  console.log(`${cond ? "PASS" : "FAIL"} ${name}${extra ? " - " + extra : ""}`);
  if (!cond) failures++;
};

// 1. Structure
const createKeys = Object.keys(App.creates);
check("has 29 creates", createKeys.length === 29, `got ${createKeys.length}`);
check("has custom_api_request", createKeys.includes("custom_api_request"));

// 2. Dynamic fields for custom request
const custom = App.creates.custom_api_request;
const dynFields = custom.operation.inputFields[1];
const fields = dynFields(null, { inputData: { endpoint: "youtube_transcript" } });
check(
  "dynamic fields for youtube_transcript",
  Array.isArray(fields) && fields.some((f) => f.key === "url") && fields.some((f) => f.key === "language"),
);

// 3. Invalid key must raise an auth error
try {
  await appTester(App.authentication.test, { authData: { api_key: "invalid_key_123" } });
  check("invalid key rejected", false, "no error thrown");
} catch (err) {
  check("invalid key rejected", /RefreshAuthError|401|403/i.test(String(err.name) + String(err.message)), String(err.message).slice(0, 120));
}

// 4. Optional live test when a real key is present
const liveKey = process.env.CAPTAPI_API_KEY;
if (liveKey) {
  const result = await appTester(App.creates.youtube_video_details.operation.perform, {
    authData: { api_key: liveKey },
    inputData: { url: "https://www.youtube.com/watch?v=dQw4w9WgXcQ" },
  });
  check("live youtube_video_details", !!result && typeof result === "object", JSON.stringify(result).slice(0, 100));
} else {
  console.log("SKIP live perform test (CAPTAPI_API_KEY not set)");
}

process.exit(failures ? 1 : 0);
