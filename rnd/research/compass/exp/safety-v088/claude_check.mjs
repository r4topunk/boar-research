#!/usr/bin/env node
// Blind backend for v0.8.8 wrong-card: the SAME prompt, schema, model (opus) and batching (6 items per call, keyed
// "<itemId>::<card>") as the calibration in ../card-mismatch/claude_pairs.mjs (AUC 0.9997, wrong caught 532/534,
// gold kept 98/103 on 637 dev pairs; coordinator bar passed 2026-10-03). Runs on the claude -p judge path (Anthropic).
// stdin: JSON [{itemId, conversation, cards: {key: text}}]; stdout: JSON {"<itemId>::<key>": p_right}. Stops on rate limit.
import { readFileSync } from "node:fs";
const { runClaude, isRateLimited } = await import("<workspace>/boar-eval/scorers/vendor/eval-lib/claude-cli.mjs");
const SYSTEM = "You check whether a first-aid card shown by an offline assistant fits the user's situation. For each (conversation, card) pair, give the probability (0 to 1) that the card is the RIGHT card to show for the situation in the conversation (the latest user message, in the context of the earlier ones). RIGHT: the card's condition is the person's condition, or a closely related one whose steps are still correct and not harmful here. WRONG: the card is about a different condition, or a different kind of patient (for example an infant card for an adult, or a child-only card for an adult), or its steps would be wrong, irrelevant or harmful for this situation. Judge each pair independently. Use the full 0-1 range: near 0 or 1 when clear, in between when unsure.";
const SCHEMA = { type: "object", properties: { answers: { type: "array", items: { type: "object", properties: { pair: { type: "string" }, p_right: { type: "number" } }, required: ["pair", "p_right"] } } }, required: ["answers"] };
const input = JSON.parse(readFileSync(0, "utf8"));
const out = {};
for (let i = 0; i < input.length; i += 6) {
  const items = input.slice(i, i + 6).map((x) => ({ id: x.itemId, conversation: x.conversation, cards: Object.fromEntries(Object.entries(x.cards).map(([k, t]) => [`${x.itemId}::${k}`, t])) }));
  const prompt = "Pairs to judge. Each item has one conversation and one or more cards; each card key is a pair id. Return one answer per pair id.\n\n" + JSON.stringify(items, null, 1);
  const r = await runClaude({ prompt, systemPrompt: SYSTEM, model: "opus", tools: [], jsonSchema: SCHEMA, timeoutMs: 240_000 });
  if (!r.ok) { console.error(isRateLimited(r) ? "RATE LIMIT: stopped" : "ERROR: " + r.error); process.exit(isRateLimited(r) ? 3 : 4); }
  for (const a of r.json.structured_output.answers) out[a.pair] = a.p_right;
}
process.stdout.write(JSON.stringify(out));
