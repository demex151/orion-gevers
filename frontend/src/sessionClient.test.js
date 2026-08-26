import test from "node:test";
import assert from "node:assert/strict";

import { createSessionClient } from "./sessionClient.js";

test("status reads backend session state", async () => {
  const calls = [];
  const fetchImpl = async (url, options = {}) => {
    calls.push([url, options]);
    return { ok: true, json: async () => ({ state: "SENTINEL" }) };
  };
  const client = createSessionClient("http://127.0.0.1:8000", fetchImpl);
  assert.equal((await client.status()).state, "SENTINEL");
  assert.match(calls[0][0], /\/api\/session\/status$/);
});

test("listen uses only the session listen endpoint", async () => {
  const calls = [];
  const fetchImpl = async (url, options = {}) => {
    calls.push([url, options]);
    return { ok: true, json: async () => ({ ok: true, text: "hola" }) };
  };
  const client = createSessionClient("http://127.0.0.1:8000", fetchImpl);
  await client.listen();
  assert.match(calls[0][0], /\/api\/session\/listen$/);
  assert.equal(calls[0][1].method, "POST");
});

test("close delegates real closure to backend", async () => {
  const fetchImpl = async (url) => ({
    ok: true,
    json: async () => ({ ok: true, state: "SENTINEL", url }),
  });
  const client = createSessionClient("http://127.0.0.1:8000", fetchImpl);
  const result = await client.close();
  assert.equal(result.state, "SENTINEL");
});
