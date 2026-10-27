#!/usr/bin/env node
// Card-condition mismatch via the judge path we already use for blind data (claude -p, Anthropic CLI login), for
// calibration against Jev on the same 637 dev pairs (coordinator 2026-10-03: blind text may not go to a new third party).
// Same definition as jev_pairs.py; 6 items per call, keyed ids, one probability per (item, card). Cached per batch.
// Run: node claude_pairs.mjs [--model opus] [--conc 3]
import { createHash } from "node:crypto";
import { existsSync, mkdirSync, readFileSync, writeFileSync } from "node:fs";
import { dirname, join } from "node:path";
import { fileURLToPath } from "node:url";
const H = dirname(fileURLToPath(import.meta.url));
const { runClaude, isRateLimited } = await import("<workspace>/boar-eval/scorers/vendor/eval-lib/claude-cli.mjs");
const a = process.argv.slice(2); const get = (k, d) => (a.includes(k) ? a[a.indexOf(k) + 1] : d);
const model = get("--model", "opus"); const conc = Number(get("--conc", "3"));
const CARDS = JSON.parse(readFileSync(join(H, "../first-aid-cards/conditionCards.v1.json"), "utf8")).cards;
const pairs = JSON.parse(readFileSync(join(H, "pairs.json"), "utf8")); // [[id, gold, {key: jevP}]]
const dev = Object.fromEntries(readFileSync(join(H, "../emergency-dev/dev.jsonl"), "utf8").split("\n").filter(Boolean).map((l) => { const r = JSON.parse(l); return [r.id, r]; }));
export const SYSTEM = "You check whether a first-aid card shown by an offline assistant fits the user's situation. For each (conversation, card) pair, give the probability (0 to 1) that the card is the RIGHT card to show for the situation in the conversation (the latest user message, in the context of the earlier ones). RIGHT: the card's condition is the person's condition, or a closely related one whose steps are still correct and not harmful here. WRONG: the card is about a different condition, or a different kind of patient (for example an infant card for an adult, or a child-only card for an adult), or its steps would be wrong, irrelevant or harmful for this situation. Judge each pair independently. Use the full 0-1 range: near 0 or 1 when clear, in between when unsure.";
const SCHEMA = { type: "object", properties: { answers: { type: "array", items: { type: "object", properties: { pair: { type: "string" }, p_right: { type: "number" } }, required: ["pair", "p_right"] } } }, required: ["answers"] };
const conv = (r) => r.turns.map((t) => (t.role === "user" ? "User: " : "Assistant: ") + t.text).join("\n");
const batches = []; for (let i = 0; i < pairs.length; i += 6) batches.push(pairs.slice(i, i + 6));
mkdirSync(join(H, "cache-claude"), { recursive: true });
const results = {}; let stop = false;
async function runBatch(b) {
  const items = b.map(([id, , o]) => ({ id, conversation: conv(dev[id]), cards: Object.fromEntries(Object.keys(o).map((k) => [`${id}::${k}`, CARDS[k].en])) }));
  const prompt = "Pairs to judge. Each item has one conversation and one or more cards; each card key is a pair id. Return one answer per pair id.\n\n" + JSON.stringify(items, null, 1);
  const f = join(H, "cache-claude", createHash("sha256").update(model + SYSTEM + prompt).digest("hex") + ".json");
  if (existsSync(f)) return JSON.parse(readFileSync(f, "utf8"));
  if (stop) return null;
  const r = await runClaude({ prompt, systemPrompt: SYSTEM, model, tools: [], jsonSchema: SCHEMA, timeoutMs: 240_000 });
  if (!r.ok) { if (isRateLimited(r)) stop = true; console.error("batch failed", r.error?.slice(0, 200)); return null; }
  const ans = r.json.structured_output?.answers ?? JSON.parse(r.json.result).answers;
  writeFileSync(f, JSON.stringify(ans)); return ans;
}
let next = 0;
await Promise.all(Array.from({ length: conc }, async () => { while (next < batches.length) { const b = batches[next++]; const ans = await runBatch(b); for (const x of ans ?? []) results[x.pair] = x.p_right; } }));
writeFileSync(join(H, `claude_pairs.${model}.json`), JSON.stringify(results, null, 0));
console.log("pairs answered", Object.keys(results).length, "of", pairs.reduce((n, [, , o]) => n + Object.keys(o).length, 0), stop ? "(STOPPED: rate limit)" : "");
