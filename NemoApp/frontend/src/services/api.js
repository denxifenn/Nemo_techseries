// Lightweight fetch-based API client with Firebase and manual token support

import { getIdToken } from './firebase';

const DEFAULT_BASE_URL = process.env.VUE_APP_API_URL || 'http://localhost:5000';
const LS_KEYS = {
  manualToken: 'apiTester.manualToken',
  baseUrl: 'apiTester.baseUrl',
};

function getStoredBaseUrl() {
  try {
    return localStorage.getItem(LS_KEYS.baseUrl) || DEFAULT_BASE_URL;
  } catch {
    return DEFAULT_BASE_URL;
  }
}

function setStoredBaseUrl(url) {
  try {
    if (url) localStorage.setItem(LS_KEYS.baseUrl, url);
  } catch {
    // ignore
  }
}

function getManualToken() {
  try {
    return localStorage.getItem(LS_KEYS.manualToken) || '';
  } catch {
    return '';
  }
}

function setManualToken(token) {
  try {
    if (token) {
      localStorage.setItem(LS_KEYS.manualToken, token);
    }
  } catch {
    // ignore
  }
}

function clearManualToken() {
  try {
    localStorage.removeItem(LS_KEYS.manualToken);
  } catch {
    // ignore
  }
}

async function resolveAuthHeader() {
  // Priority: manual token in localStorage -> Firebase ID token -> none
  const manual = getManualToken();
  if (manual && manual.trim().length > 0) {
    console.debug('[api] resolveAuthHeader: using manual token from localStorage');
    return { Authorization: `Bearer ${manual.trim()}` };
  }
  const fbToken = await getIdToken();
  if (fbToken) {
    console.debug('[api] resolveAuthHeader: using Firebase ID token');
    return { Authorization: `Bearer ${fbToken}` };
  }
  console.debug('[api] resolveAuthHeader: no token available');
  return {};
}

function buildUrl(path, params = undefined) {
  const base = getStoredBaseUrl().replace(/\/+$/, '');
  const p = String(path || '').startsWith('/') ? path : `/${path || ''}`;
  const url = new URL(base + p);
  if (params && typeof params === 'object') {
    Object.entries(params).forEach(([k, v]) => {
      if (v !== undefined && v !== null && v !== '') {
        url.searchParams.set(k, String(v));
      }
    });
  }
  return url.toString();
}

async function parseJsonSafe(response) {
  const text = await response.text();
  if (!text) return null;
  try {
    return JSON.parse(text);
  } catch {
    return text; // non-JSON, return raw
  }
}

async function request(path, options = {}) {
  const {
    method = 'GET',
    headers = {},
    params,
    body,
    json = true, // if body is object, serialize as JSON by default
    skipAuth = false,
    baseUrl, // optional override per call
  } = options;

  if (baseUrl) {
    // Ephemeral override for this request; not persisted
  }

  const url = (function () {
    if (baseUrl) {
      const base = baseUrl.replace(/\/+$/, '');
      const p = String(path || '').startsWith('/') ? path : `/${path || ''}`;
      const u = new URL(base + p);
      if (params && typeof params === 'object') {
        Object.entries(params).forEach(([k, v]) => {
          if (v !== undefined && v !== null && v !== '') {
            u.searchParams.set(k, String(v));
          }
        });
      }
      return u.toString();
    }
    return buildUrl(path, params);
  })();

  let finalHeaders = { ...(headers || {}) };

  if (!skipAuth && !('Authorization' in finalHeaders)) {
    const authHeader = await resolveAuthHeader();
    finalHeaders = { ...finalHeaders, ...authHeader };
  } else if (!skipAuth && ('Authorization' in finalHeaders)) {
    console.debug('[api] request: explicit Authorization header provided; not overriding');
  } else if (skipAuth) {
    console.debug('[api] request: skipAuth=true; not attaching auth header');
  }

  let finalBody = body;
  if (json && body && typeof body === 'object' && !(body instanceof FormData)) {
    finalHeaders['Content-Type'] = finalHeaders['Content-Type'] || 'application/json';
    finalBody = JSON.stringify(body);
  }

  const hasAuth = 'Authorization' in finalHeaders;
  console.debug(`[api] ${method.toUpperCase()} ${url}`, { hasAuth, skipAuth: !!skipAuth });

  const resp = await fetch(url, {
    method,
    headers: finalHeaders,
    body: ['GET', 'HEAD'].includes(method.toUpperCase()) ? undefined : finalBody,
  });

  const data = await parseJsonSafe(resp);
  const result = {
    ok: resp.ok,
    status: resp.status,
    statusText: resp.statusText,
    data,
  };

  if (!resp.ok) {
    const errMsg =
      (data && (data.error || data.message)) ||
      `HTTP ${resp.status} ${resp.statusText}`;
    const error = new Error(errMsg);
    error.response = result;
    throw error;
  }

  return result;
}

// Convenience HTTP verbs
const api = {
  setBaseUrl: setStoredBaseUrl,
  getBaseUrl: getStoredBaseUrl,
  setManualToken,
  getManualToken,
  clearManualToken,

  async get(path, params, options = {}) {
    return request(path, { ...options, method: 'GET', params });
  },
  async post(path, body, options = {}) {
    return request(path, { ...options, method: 'POST', body });
  },
  async put(path, body, options = {}) {
    return request(path, { ...options, method: 'PUT', body });
  },
  async del(path, body, options = {}) {
    return request(path, { ...options, method: 'DELETE', body });
  },

  // Auth helpers specific to Nemo backend
  async backendLoginWithIdToken(idToken) {
    // Send token BOTH in body and as Authorization header to maximize compatibility
    // Backend [auth.login()](NemoApp/backend/api/auth.py:12) now accepts either.
    return request('/api/auth/login', {
      method: 'POST',
      headers: { Authorization: `Bearer ${String(idToken || '').trim()}` },
      body: { idToken },
      skipAuth: true, // avoid overriding explicit Authorization
    });
  },
  async backendVerify() {
    return request('/api/auth/verify', { method: 'GET' });
  },
};

export default api;