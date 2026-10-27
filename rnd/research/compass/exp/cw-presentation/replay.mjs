import fs from "node:fs";
import { citationSupport, ATTRIBUTION_MIN_SUPPORT } from "./engine/citations.ts";
const D = "<workspace>/boar-eval/runs/and-qwen-s44/and-qwen-s44.";
const load = (p) => fs.readFileSync(p, "utf8").trim().split("\n").map((l) => JSON.parse(l));
const dump = Object.fromEntries(load(D + "prompts.jsonl").map((r) => [r.itemId, r.messages]));
const NEG = /\b(no|not|never|cannot|can't|isn't|aren't|wasn't|weren't|doesn't|don't|didn't|won't|none|nothing|neither|nor|without)\b/gi;
const CMP = /\b(only|largest|biggest|smallest|highest|lowest|longest|most|least|larger|bigger|smaller|higher|lower|more|less|first|last)\b/gi;
const nums = (t) => (t.replace(/(\d)[,\s](?=\d{3}\b)/g, "$1").match(/\d+(?:\.\d+)?/g) || []);
const guard = (s, src) => {
  const st = (src.title + " " + src.body).toLowerCase(), sl = s.toLowerCase().replace(/’/g, "'");
  const miss = [];
  for (const m of sl.match(NEG) || []) if (!new RegExp(`\\b${m}\\b`).test(st.replace(/’/g, "'"))) miss.push(m);
  for (const m of sl.match(CMP) || []) if (!new RegExp(`\\b${m}\\b`).test(st)) miss.push(m);
  const sn = new Set(nums(st));
  for (const n of nums(sl)) if (!sn.has(n)) miss.push(n);
  return miss;
};
const out = [];
for (const t of load(D + "traces.jsonl")) {
  const msgs = dump[t.itemId]; if (!msgs || t.answer.declined) continue;
  const sys = msgs.find((m) => m.role === "system").content;
  if (!sys.includes("Context:") || t.route.reasonCodes.some((c) => c.startsWith("grounding:health"))) continue;
  const ctx = sys.split("Context:")[1];
  const srcs = [...ctx.matchAll(/\[(\d+)\]\s*([^\n]*)\n([\s\S]*?)(?=\n\s*\n\[\d+\]|$)/g)].map((m) => ({ title: m[2], body: m[3] }));
  const text0 = t.answer.text.replace(/\s*\[\d+\]/g, "");
  for (const s of text0.match(/[^.!?\n]+[.!?]*/g) || []) {
    if (citationSupport(s, { title: "", body: "" }) === 1) continue; // < MIN_KEY_TERMS: attribution skips it
    let best = -1, bs = 0;
    srcs.forEach((src, i) => { const v = citationSupport(s, src); if (v >= ATTRIBUTION_MIN_SUPPORT && v > bs) { best = i; bs = v; } });
    if (best < 0) continue;
    const miss = guard(s, srcs[best]);
    out.push({ id: t.itemId, sentence: s.trim(), n: best + 1, support: +bs.toFixed(2), blocked: miss.length > 0, miss, source: (srcs[best].title + " | " + srcs[best].body).slice(0, 700) });
  }
}
fs.writeFileSync("replay-s44.json", JSON.stringify(out, null, 1));
console.log(`attributions ${out.length} over ${new Set(out.map((o) => o.id)).size} answers; G1 blocks ${out.filter((o) => o.blocked).length}`);
