// Generates the Captapi Make.com custom app (local app definition) from the
// shared endpoint catalog. Single source of truth: ../captapi-n8n/src/catalog.ts
//
// Run with Node >= 22.6 (TypeScript type-stripping enabled):
//   node generate.mjs
//
// Output goes to ./app/, which is the folder you open in VS Code with the
// "Make Apps Editor" extension and then deploy to your Make organization.

import { mkdirSync, rmSync, writeFileSync } from "node:fs";
import { dirname } from "node:path";
import { fileURLToPath } from "node:url";

const { ENDPOINTS } = await import("../captapi-n8n/src/catalog.ts");

const HERE = dirname(fileURLToPath(import.meta.url));
const APP = `${HERE}/app`;
const API_BASE = "https://api.captapi.com";

const PLATFORM_LABELS = {
  youtube: "YouTube",
  tiktok: "TikTok",
  instagram: "Instagram",
  facebook: "Facebook",
  twitter: "Twitter / X",
  reddit: "Reddit",
  threads: "Threads",
  bluesky: "Bluesky",
  pinterest: "Pinterest",
  linkedin: "LinkedIn",
  rumble: "Rumble",
  google: "Google",
  twitch: "Twitch",
  spotify: "Spotify",
  soundcloud: "SoundCloud",
  linktree: "Linktree",
  snapchat: "Snapchat",
  truth_social: "Truth Social",
  kick: "Kick",
  amazon_shop: "Amazon Shop",
  age_gender: "Age and Gender",
  account: "Account",
  kwai: "Kwai",
  komi: "Komi",
  pillar: "Pillar",
  linkbio: "Linkbio",
  linkme: "Linkme",
  tiktok_shop: "TikTok Shop",
  github: "GitHub",
  ad_library: "Ad Library",
};

const PARAM_LABELS = {
  url: "URL",
  q: "Search Query",
  query: "Query",
  limit: "Limit",
  language: "Language",
  comment_id: "Comment ID",
  country: "Country",
};

// MCP tool name (snake_case) -> Make module name (camelCase, [a-zA-Z][0-9a-zA-Z]*).
function moduleName(tool) {
  return tool.replace(/_([a-z0-9])/g, (_, c) => c.toUpperCase());
}

function paramLabel(name) {
  if (PARAM_LABELS[name]) return PARAM_LABELS[name];
  return name
    .split(/[_-]/)
    .map((w) => w.charAt(0).toUpperCase() + w.slice(1))
    .join(" ");
}

function writeJson(relPath, value) {
  const full = `${APP}/${relPath}`;
  mkdirSync(dirname(full), { recursive: true });
  writeFileSync(full, JSON.stringify(value, null, 2) + "\n", "utf8");
}

function writeText(relPath, value) {
  const full = `${APP}/${relPath}`;
  mkdirSync(dirname(full), { recursive: true });
  writeFileSync(full, value, "utf8");
}

// --- Reset output ----------------------------------------------------------
rmSync(APP, { recursive: true, force: true });
mkdirSync(APP, { recursive: true });

// --- Base (inherited by every module) --------------------------------------
writeJson("general/base.iml.json", {
  baseUrl: API_BASE,
  headers: {
    Authorization: "Bearer {{connection.apiKey}}",
  },
  response: {
    error: {
      message:
        "[{{statusCode}}] {{ifempty(body.detail, ifempty(body.error, ifempty(body.message, 'Request failed')))}}",
    },
  },
  log: {
    sanitize: ["request.headers.authorization"],
  },
});

// --- Connection (API key) ---------------------------------------------------
writeJson("connections/captapi/params.iml.json", [
  {
    name: "apiKey",
    type: "password",
    label: "API Key",
    required: true,
    editable: true,
    help: "Your Captapi API key. Create one at https://captapi.com/dashboard.",
  },
]);

writeJson("connections/captapi/communication.iml.json", {
  url: `${API_BASE}/v1/account/limits`,
  method: "GET",
  headers: {
    Authorization: "Bearer {{parameters.apiKey}}",
  },
  response: {
    error: {
      message: "[{{statusCode}}] Invalid API key or request failed.",
    },
  },
  log: {
    sanitize: ["request.headers.authorization"],
  },
});

// --- Modules (one action per endpoint) --------------------------------------
const moduleComponents = {};
const groups = {};

for (const e of ENDPOINTS) {
  const name = moduleName(e.tool);
  const platformLabel = PLATFORM_LABELS[e.platform] ?? e.platform;

  // Communication
  const qs = {};
  for (const p of e.params) qs[p.name] = `{{parameters.${p.name}}}`;
  writeJson(`modules/${name}/communication.iml.json`, {
    url: e.path,
    method: "GET",
    qs,
    response: {
      output: "{{body.data}}",
    },
  });

  // Mappable parameters
  const mappable = e.params.map((p) => ({
    name: p.name,
    type: p.type === "number" ? "number" : p.type === "boolean" ? "boolean" : "text",
    label: paramLabel(p.name),
    required: !!p.required,
    help: p.description,
  }));
  writeJson(`modules/${name}/mappable-params.iml.json`, mappable);

  moduleComponents[name] = {
    label: e.name,
    description: `${e.summary} Costs ~${e.credits} credit${e.credits === 1 ? "" : "s"} (cached results free, failures never charged).`,
    connection: "captapi",
    altConnection: null,
    webhook: null,
    moduleType: "action",
    actionCrud: "read",
    codeFiles: {
      communication: `modules/${name}/communication.iml.json`,
      staticParams: null,
      mappableParams: `modules/${name}/mappable-params.iml.json`,
      interface: null,
      samples: null,
      scope: null,
    },
  };

  (groups[platformLabel] ??= []).push(name);
}

// --- Module groups (organizes the picker by platform) -----------------------
writeJson(
  "modules/groups.json",
  Object.entries(groups).map(([label, modules]) => ({ label, modules })),
);

// --- App manifest -----------------------------------------------------------
writeJson("makecomapp.json", {
  fileVersion: 1,
  generalCodeFiles: {
    base: "general/base.iml.json",
    common: null,
    readme: "README.md",
    groups: "modules/groups.json",
  },
  components: {
    connection: {
      captapi: {
        label: "Captapi API Key",
        connectionType: "basic",
        codeFiles: {
          communication: "connections/captapi/communication.iml.json",
          params: "connections/captapi/params.iml.json",
          common: null,
        },
      },
    },
    module: moduleComponents,
    function: {},
    rpc: {},
    webhook: {},
  },
  origins: [],
});

// --- In-app README ----------------------------------------------------------
const moduleCount = ENDPOINTS.length;
writeText(
  "README.md",
  `# Captapi for Make.com

Structured social media data from 29 platforms — YouTube, TikTok, Instagram,
Facebook, X (Twitter), Reddit, Threads, Bluesky, Pinterest, LinkedIn, Rumble,
GitHub, Google Search, Twitch, Spotify, SoundCloud, Linktree, Snapchat, Truth
Social, Kick, Kwai, Komi, Pillar, Linkbio, Linkme, Amazon Shop, TikTok Shop,
Age/Gender and public Ad Libraries —
transcripts, AI summaries, comments, stats, search, commerce data and downloads.

- **${moduleCount} action modules**, one per Captapi endpoint.
- **One connection**: paste your Captapi API key (Bearer auth).
- Every module returns the API \`data\` payload directly.

## Connection

Create a **Captapi API Key** connection and paste the key from
https://captapi.com/dashboard. The key is validated against
\`GET /v1/account/limits\`.

## Modules

Modules are grouped by platform in the Make picker. Pick the operation you need,
fill in the URL, search query, or platform-specific fields, and the module
returns the structured result.

Docs: https://captapi.com/docs
`,
);

console.log(`Generated Make app with ${moduleCount} modules into ${APP}`);
