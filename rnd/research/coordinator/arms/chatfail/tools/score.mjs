// CHATFAIL S1 scoring (0 LLM calls): gen-<model>-<ARM>.jsonl -> out/scored-<model>.jsonl with the frozen detectors (fulfilled.mjs, sha in fulfilled.sha256).
//   node tools/score.mjs m4 [tag]
import fs from "node:fs";
import { fulfilled, refusal } from "./fulfilled.mjs";
const model = process.argv[2], tag = process.argv[3] ? "-" + process.argv[3] : "";
const dir = new URL("./out/", import.meta.url).pathname;
const out = [];
for (const arm of ["C0", "A1", "A2", "A3"]) {
  const f = `${dir}gen-${model}-${arm}${tag}.jsonl`; if (!fs.existsSync(f)) continue;
  const rows = fs.readFileSync(f, "utf8").trim().split("\n").filter(Boolean).map((l) => JSON.parse(l));
  const prev = new Map(); // chat -> previous answer
  for (const r of rows) {
    const pa = prev.get(r.chat) ?? null;
    const ref = refusal(r.answer);
    const o = { arm, model, chat: r.chat, kind: r.kind, turn: r.turn, text: r.text, cap: r.capability_request, expected_intent: r.expected_intent, class: r.class, engine_fixed: r.engine_fixed, refusal: ref, tokens: r.tokens, finish_reason: r.finish_reason, n_sources: r.n_sources, answer: r.answer };
    if (r.capability_request) { const f2 = fulfilled({ expected_intent: r.expected_intent, turnText: r.text, answer: r.answer, prevAnswer: pa }); o.fulfilled = f2.ok; o.fkind = f2.kind; o.why = f2.why; }
    out.push(o); prev.set(r.chat, r.answer);
  }
}
fs.writeFileSync(`${dir}scored-${model}${tag}.jsonl`, out.map((o) => JSON.stringify(o)).join("\n") + "\n");
console.log(`scored ${out.length} rows -> out/scored-${model}${tag}.jsonl`);
