import assert from "node:assert"; import fs from "node:fs";
import { splitContext, joinContext, gate } from "./rrgate.ts";
// round trip on every s44 prompt with context
let n = 0;
for (const l of fs.readFileSync("<workspace>/boar-eval/runs/and-qwen-s44/and-qwen-s44.prompts.jsonl", "utf8").split("\n").filter(Boolean)) {
  const s = JSON.parse(l).messages[0].content; const sp = splitContext(s); if (!sp) continue; n++;
  assert.equal(joinContext(sp.head, sp.passages), s); sp.passages.forEach((p, i) => assert.ok(p.text.startsWith(`[${i + 1}] `)));
}
const m = [{ role: "system", content: "Sys.\n\nContext:\n[1] A\na body\n\n[2] B\nb body\n\n[3] C\nc body" }, { role: "user", content: "Q?\n\n(Response style: short)" }];
const r = await gate(m, async (q, d) => { assert.equal(q, "Q?"); return d.startsWith("B") ? 0.01 : 0.9; }, 0.05);
assert.equal(r.messages[0].content, "Sys.\n\nContext:\n[1] A\na body\n\n[3] C\nc body"); assert.deepEqual(r.info!.dropped, [2]);
console.log(`ok: round trip ${n} context prompts; gate drop keeps numbering`);
