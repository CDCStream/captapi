"use strict";

const CATALOG = require("./catalog.json");

const API_BASE = "https://api.captapi.com";

// Endpoints promoted to first-class Zapier actions. Everything else is
// reachable through the "Custom API Request" action below.
const FEATURED = [
  "youtube_transcript",
  "youtube_summarize",
  "youtube_video_details",
  "youtube_comments",
  "youtube_channel_details",
  "youtube_search",
  "tiktok_transcript",
  "tiktok_summarize",
  "tiktok_video_details",
  "tiktok_comments",
  "tiktok_channel_details",
  "tiktok_search",
  "instagram_transcript",
  "instagram_summarize",
  "instagram_details",
  "instagram_comments",
  "instagram_channel_details",
  "instagram_channel_posts",
  "facebook_transcript",
  "facebook_page_details",
  "twitter_tweet_details",
  "twitter_profile",
  "reddit_post_comments",
  "reddit_search",
  "linkedin_profile",
  "linkedin_company",
  "threads_profile",
  "account_balance",
];

const PARAM_LABELS = {
  url: "URL",
  q: "Search Query",
  query: "Query",
  limit: "Limit",
  language: "Language",
  comment_id: "Comment ID",
  country: "Country",
};

function paramLabel(name) {
  if (PARAM_LABELS[name]) return PARAM_LABELS[name];
  return name
    .split(/[_-]/)
    .map((w) => w.charAt(0).toUpperCase() + w.slice(1))
    .join(" ");
}

function toInputField(p) {
  return {
    key: p.name,
    label: paramLabel(p.name),
    type: p.type === "number" ? "integer" : p.type === "boolean" ? "boolean" : "string",
    required: !!p.required,
    helpText: p.description,
  };
}

// Zapier actions must return a single object; wrap list payloads.
function normalizeOutput(payload) {
  const data = payload && payload.data !== undefined ? payload.data : payload;
  if (Array.isArray(data)) {
    return { items: data, count: data.length };
  }
  if (data === null || typeof data !== "object") {
    return { result: data };
  }
  return data;
}

function buildQueryParams(endpoint, inputData) {
  const params = {};
  for (const p of endpoint.params) {
    const v = inputData[p.name];
    if (v !== undefined && v !== null && v !== "") params[p.name] = v;
  }
  return params;
}

function makePerform(tool) {
  return async (z, bundle) => {
    const endpoint = CATALOG.find((e) => e.tool === tool);
    const response = await z.request({
      url: `${API_BASE}${endpoint.path}`,
      params: buildQueryParams(endpoint, bundle.inputData),
    });
    return normalizeOutput(response.data);
  };
}

function makeCreate(endpoint) {
  const creditNote =
    endpoint.credits > 0
      ? ` Costs ~${endpoint.credits} credit${endpoint.credits === 1 ? "" : "s"} (cached results are free, failed requests are never charged).`
      : "";
  return {
    key: endpoint.tool,
    noun: endpoint.name,
    display: {
      label: endpoint.name,
      description: `${endpoint.summary}${creditNote}`,
    },
    operation: {
      inputFields: endpoint.params.map(toInputField),
      perform: makePerform(endpoint.tool),
      sample: { id: 1, success: true },
      outputFields: [],
    },
  };
}

// --- Custom API Request (covers all endpoints) -------------------------------

const endpointChoices = {};
for (const e of CATALOG) {
  endpointChoices[e.tool] = `${e.platform}: ${e.name} (~${e.credits} cr)`;
}

const dynamicEndpointFields = (z, bundle) => {
  const tool = bundle.inputData.endpoint;
  const endpoint = CATALOG.find((e) => e.tool === tool);
  if (!endpoint) return [];
  return endpoint.params.map(toInputField);
};

const customRequest = {
  key: "custom_api_request",
  noun: "API Request",
  display: {
    label: "Custom API Request",
    description:
      "Call any of the 179 Captapi endpoints across 29 platforms. Pick an endpoint and the matching input fields appear.",
  },
  operation: {
    inputFields: [
      {
        key: "endpoint",
        label: "Endpoint",
        type: "string",
        required: true,
        choices: endpointChoices,
        altersDynamicFields: true,
        helpText: "The Captapi endpoint to call. See https://captapi.com/docs for details.",
      },
      dynamicEndpointFields,
    ],
    perform: async (z, bundle) => {
      const endpoint = CATALOG.find((e) => e.tool === bundle.inputData.endpoint);
      if (!endpoint) {
        throw new z.errors.Error(`Unknown endpoint: ${bundle.inputData.endpoint}`, "InvalidInput", 400);
      }
      const response = await z.request({
        url: `${API_BASE}${endpoint.path}`,
        params: buildQueryParams(endpoint, bundle.inputData),
      });
      return normalizeOutput(response.data);
    },
    sample: { id: 1, success: true },
    outputFields: [],
  },
};

const creates = {};
for (const tool of FEATURED) {
  const endpoint = CATALOG.find((e) => e.tool === tool);
  if (endpoint) creates[tool] = makeCreate(endpoint);
}
creates[customRequest.key] = customRequest;

module.exports = creates;
