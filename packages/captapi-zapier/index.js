"use strict";

const authentication = require("./authentication");
const creates = require("./creates");
const packageJson = require("./package.json");
const zapier = require("zapier-platform-core");

const addBearerHeader = (request, z, bundle) => {
  if (bundle.authData && bundle.authData.api_key) {
    request.headers = request.headers || {};
    request.headers.Authorization = `Bearer ${bundle.authData.api_key}`;
  }
  return request;
};

const handleErrors = (response, z) => {
  if (response.status === 401 || response.status === 403) {
    throw new z.errors.RefreshAuthError();
  }
  if (response.status === 402) {
    throw new z.errors.Error(
      "Not enough Captapi credits. Top up at https://captapi.com/dashboard/billing.",
      "PaymentRequired",
      402,
    );
  }
  if (response.status >= 400) {
    let detail = "Request failed";
    try {
      const body = response.data;
      detail = (body && (body.detail || body.error || body.message)) || detail;
    } catch (e) {
      // keep default detail
    }
    throw new z.errors.Error(`[${response.status}] ${detail}`, "RequestFailed", response.status);
  }
  return response;
};

module.exports = {
  version: packageJson.version,
  platformVersion: zapier.version,
  authentication,
  beforeRequest: [addBearerHeader],
  afterResponse: [handleErrors],
  triggers: {},
  searches: {},
  creates,
  resources: {},
};
