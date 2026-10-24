const API_BASE = import.meta.env.VITE_API_URL || "http://127.0.0.1:8000";

async function request(path, options = {}) {
  const res = await fetch(`${API_BASE}${path}`, {
    headers: { "Content-Type": "application/json", ...options.headers },
    ...options,
  });
  if (!res.ok) {
    let detail = res.statusText;
    try {
      const body = await res.json();
      detail = body.detail || JSON.stringify(body);
    } catch {
      /* ignore */
    }
    throw new Error(typeof detail === "string" ? detail : "Request failed");
  }
  return res.json();
}

export function analyzeMessage(message, model) {
  return request("/analyze", {
    method: "POST",
    body: JSON.stringify({ message, model: model || undefined }),
  });
}

export function fetchModels() {
  return request("/models");
}

export function fetchEvaluation() {
  return request("/evaluation");
}

export function fetchHealth() {
  return request("/health");
}
