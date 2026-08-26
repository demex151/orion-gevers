export function createSessionClient(API, fetchImpl = fetch) {
  async function request(path, options = {}) {
    const response = await fetchImpl(`${API}${path}`, options);
    const data = await response.json();
    if (!response.ok) {
      throw new Error(data?.error || `Session API respondió ${response.status}`);
    }
    return data;
  }

  return {
    status() {
      return request("/api/session/status", { method: "GET" });
    },
    listen() {
      return request("/api/session/listen", { method: "POST" });
    },
    open(trigger = "manual") {
      return request("/api/session/open", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ trigger }),
      });
    },
    close() {
      return request("/api/session/close", { method: "POST" });
    },
  };
}
