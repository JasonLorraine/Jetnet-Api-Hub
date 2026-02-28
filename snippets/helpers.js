const axios = require("axios");

const baseUrl = process.env.JETNET_BASE_URL || "https://customer.jetnetconnect.com";
const apiToken = process.env.JETNET_API_TOKEN;

if (!baseUrl) throw new Error("Missing JETNET_BASE_URL");
if (!apiToken) throw new Error("Missing JETNET_API_TOKEN");

const http = axios.create({ baseURL: baseUrl, timeout: 30000 });

function success(status) {
  return typeof status === "string" && status.startsWith("SUCCESS");
}

function asArray(v) {
  return Array.isArray(v) ? v : v == null ? [] : [v];
}

module.exports = { http, apiToken, success, asArray };
