// TOPICS27 sentence support audit (criterion TOPICS27-criterion.md). Usage: node audit.mjs <prep.json> <out audit.jsonl>
import { readFileSync, appendFileSync, existsSync } from "node:fs";
const { runClaude } = await import("<workspace>/boar-eval/scorers/vendor/eval-lib/claude-cli.mjs");
const [prepf, out] = process.argv.slice(2);
const CAP = 290, HARD = 300;
const P = JSON.parse(readFileSync(prepf, "utf8"));
const SYS = "You are a strict support auditor. You only judge whether the source chunks contain the information a sentence states. Whether anything is true in the real world is irrelevant.";
const INSTR = `Label SUPPORTED if the source chunks state or directly entail everything the sentence claims. Label PARTIAL if the chunks support its main claim but it adds a detail they do not contain. Label UNSUPPORTED if the chunks do not contain its main claim (even if it may be true), or contradict it. Generic framing with no factual claim (an introduction, a transition, advice to see a doctor) is SUPPORTED. Then set invented_specific to true if the sentence states a specific number, date, quantity, name of a person, place, organisation, gas, disease or similar named entity that appears nowhere in the source chunks; otherwise false. Ignore your own knowledge of whether the sentence is true.`;
const prompt = (u) => `QUESTION:\n${u.question}\n\nSOURCE CHUNKS:\n${u.chunks}\n\nSENTENCE FROM THE ANSWER:\n${u.sentence}\n\n${INSTR} Reply with the JSON {"label": "SUPPORTED" | "PARTIAL" | "UNSUPPORTED", "invented_specific": true | false}.`;
const SCHEMA = { type: "object", properties: { label: { type: "string", enum: ["SUPPORTED", "PARTIAL", "UNSUPPORTED"] }, invented_specific: { type: "boolean" } }, required: ["label", "invented_specific"] };
const BSCHEMA = { type: "object", properties: { items: { type: "array", items: { type: "object", properties: { n: { type: "integer" }, ...SCHEMA.properties }, required: ["n", "label", "invented_specific"] } } }, required: ["items"] };
const rows = () => (existsSync(out) ? readFileSync(out, "utf8").split("\n").filter(Boolean).map((l) => JSON.parse(l)) : []);
let invoc = rows().reduce((a, r) => a + (r.tries || 0), 0);
const have = new Set(rows().map((r) => r.key));
const units = P.units; // sentence units in topic key order
const perSentence = units.slice(0, CAP), batchedUnits = units.slice(CAP);
async function one(u) {
  if (have.has(u.key)) return;
  let r, tries = 0;
  for (let t = 0; t < 2; t++) {
    if (invoc >= HARD) { console.log("HARD CAP", u.key); return; }
    invoc++; tries++;
    r = await runClaude({ prompt: prompt(u), systemPrompt: SYS, model: "haiku", effort: "low", tools: [], jsonSchema: SCHEMA, timeoutMs: 180000 });
    if (r.ok && r.json?.structured_output?.label) break;
  }
  const so = r?.json?.structured_output ?? {};
  appendFileSync(out, JSON.stringify({ key: u.key, topic: u.topic, idx: u.idx, label: so.label ?? null, invented_specific: so.invented_specific ?? null, ok: !!so.label, tries, mode: "single" }) + "\n");
}
const pool = async (list, n) => { let i = 0; await Promise.all(Array.from({ length: n }, async () => { while (i < list.length) await list[i++](); })); };
await pool(perSentence.map((u) => () => one(u)), 4);
const byTopic = {}; for (const u of batchedUnits) (byTopic[u.topic] ??= []).push(u);
for (const [topic, us] of Object.entries(byTopic)) {
  if (us.every((u) => have.has(u.key))) continue;
  const list = us.map((u, i) => `${i + 1}. ${u.sentence}`).join("\n");
  const p = `QUESTION:\n${us[0].question}\n\nSOURCE CHUNKS:\n${us[0].chunks}\n\nNUMBERED SENTENCES FROM THE ANSWER:\n${list}\n\nFor EACH numbered sentence separately: ${INSTR} Reply with the JSON {"items": [{"n": <sentence number>, "label": ..., "invented_specific": ...}, ...]}.`;
  let r, tries = 0;
  for (let t = 0; t < 2; t++) { if (invoc >= HARD) break; invoc++; tries++;
    r = await runClaude({ prompt: p, systemPrompt: SYS, model: "haiku", effort: "low", tools: [], jsonSchema: BSCHEMA, timeoutMs: 300000 });
    if (r.ok && r.json?.structured_output?.items) break; }
  const it = r?.json?.structured_output?.items ?? [];
  us.forEach((u, i) => { const x = it.find((y) => y.n === i + 1) ?? {};
    appendFileSync(out, JSON.stringify({ key: u.key, topic, idx: u.idx, label: x.label ?? null, invented_specific: x.invented_specific ?? null, ok: !!x.label, tries: i === 0 ? tries : 0, mode: "batched" }) + "\n"); });
}
console.log("invocations", invoc, "missing", rows().filter((r) => !r.ok).length);
