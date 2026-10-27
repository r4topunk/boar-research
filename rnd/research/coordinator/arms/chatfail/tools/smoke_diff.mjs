// CHATFAIL S1 smoke: C0's assembled prompts vs HONESTPROMPT's S0 prompts (raw/answers-a2.jsonl, arm S0) for the same chat/turn.
// Compared where C0 had no context and no extra style piece: system message and final user message must be byte-identical (history differs: own answers).
// Also reports the fixed strings that differ for A1 (expected: GROUNDING + styleReminder only).  node tools/smoke_diff.mjs [gen file for C0] [gen file for A1]
import fs from "node:fs";
const rd = (p) => fs.readFileSync(p, "utf8").trim().split("\n").filter(Boolean).map((l) => JSON.parse(l));
const c0 = rd(process.argv[2] ?? new URL("./out/gen-m4-C0-smoke.jsonl", import.meta.url).pathname);
const s0 = new Map(rd("<workspace>/rnd/research/coordinator/arms/honestprompt/raw/answers-a2.jsonl").filter((r) => r.arm === "S0").map((r) => [`${r.chat}|${r.turn}`, r]));
let cmp = 0, same = 0; const diffs = [];
for (const r of c0) {
  const h = s0.get(`${r.chat}|${r.turn}`); if (!h || r.n_sources > 0 || r.engine_fixed) continue;
  const u = r.messages.at(-1).content;
  if (u.split("\n\n(Response style:").length > 1 && !/^.*\n\n\(Response style: Keep it short: 2-3 sentences\. No lists unless the question asks for one\.\)$/s.test(u)) continue; // engine added a style piece
  cmp++;
  const a = [r.messages[0].content, u], b = [h.messages[0].content, h.messages.at(-1).content];
  if (a[0] === b[0] && a[1] === b[1]) same++; else diffs.push({ id: `${r.chat}-t${r.turn}`, sys: a[0] === b[0], user: a[1] === b[1] });
}
console.log(`C0 vs HONESTPROMPT S0: ${same}/${cmp} turns byte-identical (system + final user message), diffs: ${JSON.stringify(diffs)}`);
const f1 = process.argv[3]; if (f1 && fs.existsSync(f1)) {
  const a1 = new Map(rd(f1).map((r) => [`${r.chat}|${r.turn}`, r]));
  let n = 0, ok = 0;
  for (const r of c0) { const x = a1.get(`${r.chat}|${r.turn}`); if (!x || r.engine_fixed) continue; n++;
    const s = r.messages[0].content, t = x.messages[0].content, ur = r.messages.at(-1).content, ut = x.messages.at(-1).content;
    if (t.includes("You can write text, code and examples: writing is not a physical action.") && ut.includes("unless the user asks for code, an example, a table or a translation") && t.replace(" You can write text, code and examples: writing is not a physical action.", "") === s && ut.replace(", unless the user asks for code, an example, a table or a translation", "") === ur) ok++; }
  console.log(`A1 vs C0 (same chat/turn, ignoring context/history): ${ok}/${n} system+user messages differ only by the two L1 strings`);
}
