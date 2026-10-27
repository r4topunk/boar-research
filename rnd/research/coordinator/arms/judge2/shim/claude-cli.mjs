// JUDGE2 shim (Kiln, 2026-10-07): BOAR_EVAL_LIB points here. Everything is re-exported from the vendored eval-lib
// claude-cli.mjs except runClaude, which POSTs the unchanged judge.v1 system + user bytes to a local llama-server
// (Gemma 4 26B-A4B UD-Q2_K_XL) with the VERDICT_SCHEMA as a json_schema grammar. No tracked boar-eval file is edited.
// Env: JUDGE2_URL (default http://127.0.0.1:18091), JUDGE2_LOG_DIR (sidecars calls.jsonl + failures.jsonl).
import { appendFileSync, mkdirSync } from "node:fs";
import { join } from "node:path";
export * from "<workspace>/boar-eval/scorers/vendor/eval-lib/claude-cli.mjs";

const URL_ = process.env.JUDGE2_URL ?? "http://127.0.0.1:18091";
const LOG_DIR = process.env.JUDGE2_LOG_DIR ?? process.cwd();
const MODEL = "gemma-4-26B-A4B-it-UD-Q2_K_XL";
const TIMEOUT_MS = 240_000;
mkdirSync(LOG_DIR, { recursive: true });
const log = (f, o) => appendFileSync(join(LOG_DIR, f), JSON.stringify({ at: new Date().toISOString(), ...o }) + "\n");

// Strict check against the judge.v1 VERDICT_SCHEMA shape (integers 1-5, winner enum, no extra keys).
function validate(v, schema) {
  if (!v || typeof v !== "object" || Array.isArray(v)) return "not an object";
  const keys = Object.keys(schema.properties);
  for (const k of Object.keys(v)) if (!keys.includes(k)) return `extra key ${k}`;
  for (const k of schema.required) if (!(k in v)) return `missing ${k}`;
  for (const side of ["scores_A", "scores_B"]) {
    const s = v[side], sp = schema.properties[side];
    if (!s || typeof s !== "object") return `${side} not an object`;
    for (const k of Object.keys(s)) if (!(k in sp.properties)) return `extra key ${side}.${k}`;
    for (const k of sp.required) if (!Number.isInteger(s[k]) || s[k] < 1 || s[k] > 5) return `bad ${side}.${k}=${s[k]}`;
  }
  if (!schema.properties.winner.enum.includes(v.winner)) return `bad winner ${v.winner}`;
  if (typeof v.rationale !== "string") return "rationale not a string";
  return null;
}

export async function runClaude({ prompt, systemPrompt, jsonSchema }) {
  const start = performance.now();
  const body = {
    model: MODEL,
    messages: [{ role: "system", content: systemPrompt }, { role: "user", content: prompt }],
    temperature: 0, seed: 7, max_tokens: 400, cache_prompt: true,
    chat_template_kwargs: { enable_thinking: false },
    response_format: { type: "json_schema", json_schema: { name: "verdict", strict: true, schema: jsonSchema } },
  };
  let raw = null, data = null, error, kind;
  try {
    const res = await fetch(`${URL_}/v1/chat/completions`, { method: "POST", headers: { "content-type": "application/json" },
      body: JSON.stringify(body), signal: AbortSignal.timeout(TIMEOUT_MS) });
    raw = await res.text();
    if (!res.ok) { kind = "http"; error = `HTTP ${res.status}: ${raw.slice(0, 300)}`; }
    else data = JSON.parse(raw);
  } catch (e) { kind = e?.name === "TimeoutError" ? "timeout" : "transport"; error = `${kind}: ${e?.message ?? e}`; }
  const wallMs = performance.now() - start;
  const msg = data?.choices?.[0]?.message, finish = data?.choices?.[0]?.finish_reason;
  const content = msg?.content ?? null, reasoning = msg?.reasoning_content ?? null;
  const thinkLeak = /<think>|<\|channel\|>|<\|think\|>|<start_of_turn>|<end_of_turn>/i.test(content ?? "") || !!reasoning;
  let verdict = null;
  if (data && !error) {
    try { verdict = JSON.parse(content); const bad = validate(verdict, jsonSchema); if (bad) { kind = "schema"; error = `schema: ${bad}`; verdict = null; } }
    catch (e) { kind = "json"; error = `json: ${e.message}`; }
  }
  const tel = { ok: !error, kind: kind ?? null, wallMs: Math.round(wallMs), finish, promptTokens: data?.usage?.prompt_tokens,
    completionTokens: data?.usage?.completion_tokens, cachedTokens: data?.timings?.cache_n, prefillTokS: data?.timings?.prompt_per_second,
    decodeTokS: data?.timings?.predicted_per_second, reasoningChars: reasoning ? reasoning.length : 0, thinkLeak, contentChars: content?.length ?? 0 };
  log("calls.jsonl", tel);
  if (error) {
    log("failures.jsonl", { ...tel, error, content, reasoning, raw: data ? undefined : raw?.slice(0, 2000) });
    return { ok: false, toolCalls: [], stderr: "", wallMs, error };
  }
  return { ok: true, toolCalls: [], stderr: "", wallMs,
    json: { type: "result", structured_output: verdict, modelUsage: { [MODEL]: {} }, duration_ms: Math.round(wallMs), total_cost_usd: 0 } };
}
