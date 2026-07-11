"use strict";

const API_BASE = "https://api.captapi.com";

const test = async (z) => {
  const response = await z.request({ url: `${API_BASE}/v1/account/limits` });
  return response.data;
};

module.exports = {
  type: "custom",
  fields: [
    {
      key: "api_key",
      label: "API Key",
      required: true,
      type: "password",
      helpText:
        "Your Captapi API key. Create one for free at [captapi.com/dashboard](https://captapi.com/dashboard).",
    },
  ],
  test,
  connectionLabel: (z, bundle) => {
    const d = bundle.inputData || {};
    return d.plan ? `Captapi (${d.plan})` : "Captapi";
  },
};
