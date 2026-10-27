// PARA135 set A sentence support audit (criterion PARA135-criterion.md): exact TOPICS27 prompts/schema (topics27/tools/audit.mjs), per-sentence only, sampled keys
// from judge/prep.json, hard cap 450 invocations incl. retries. Usage: node audit_a.mjs judge/prep.json judge/audit.jsonl
import { readFileSync, appendFileSync, existsSync } from "node:fs";
const { runClaude } = await import("<workspace>/boar-eval/scorers/vendor/eval-lib/claude-cli.mjs");
const [prepf, out] = process.argv.slice(2);
const HARD = 450;
const P = JSON.parse(readFileSync(prepf, "utf8"));
const SYS = "You are a strict support auditor. You only judge whether the source chunks contain the information a sentence states. Whether anything is true in the real world is irrelevant.";
const INSTR = `Label SUPPORTED if the source chunks state or directly entail everything the sentence claims. Label PARTIAL if the chunks support its main claim but it adds a detail they do not contain. Label UNSUPPORTED if the chunks do not contain its main claim (even if it may be true), or contradict it. Generic framing with no factual claim (an introduction, a transition, advice to see a doctor) is SUPPORTED. Then set invented_specific to true if the sentence states a specific number, date, quantity, name of a person, place, organisation, gas, disease or similar named entity that appears nowhere in the source chunks; otherwise false. Ignore your own knowledge of whether the sentence is true.`;
const prompt = (u) => `QUESTION:\n${u.question}\n\nSOURCE CHUNKS:\n${u.chunks}\n\nSENTENCE FROM THE ANSWER:\n${u.sentence}\n\n${INSTR} Reply with the JSON {"label": "SUPPORTED" | "PARTIAL" | "UNSUPPORTED", "invented_specific": true | false}.`;
const SCHEMA = { type: "object", properties: { label: { type: "string", enum: ["SUPPORTED", "PARTIAL", "UNSUPPORTED"] }, invented_specific: { type: "boolean" } }, required: ["label", "invented_specific"] };
const rows = () => (existsSync(out) ? readFileSync(out, "utf8").split("\n").filter(Boolean).map((l) => JSON.parse(l)) : []);
let invoc = rows().reduce((a, r) => a + (r.tries || 0), 0);
const have = new Set(rows().filter((r) => r.ok).map((r) => r.key));
const byKey = {}; for (const a of ["p1", "p3", "p5"]) for (const u of P.arms[a].units) byKey[u.key] = u;
const list = ["p1", "p3", "p5"].flatMap((a) => P.sample[a].map((k) => byKey[k]));
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
  appendFileSync(out, JSON.stringify({ key: u.key, arm: u.arm, topic: u.topic, idx: u.idx, pos: u.pos, label: so.label ?? null, invented_specific: so.invented_specific ?? null, ok: !!so.label, tries, mode: "single" }) + "\n");
}
const pool = async (fs, n) => { let i = 0; await Promise.all(Array.from({ length: n }, async () => { while (i < fs.length) await fs[i++](); })); };
await pool(list.map((u) => () => one(u)), 4);
console.log("units", list.length, "invocations", invoc, "missing", list.length - new Set(rows().filter((r) => r.ok).map((r) => r.key)).size);
