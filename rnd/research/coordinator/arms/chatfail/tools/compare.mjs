// Tables for CHATFAIL-S0.md from tools/out/before.json and after.json.  node tools/compare.mjs [--detail]
import fs from "node:fs";
const B = JSON.parse(fs.readFileSync(new URL("./out/before.json", import.meta.url))), A = JSON.parse(fs.readFileSync(new URL("./out/after.json", import.meta.url)));
const rows = B.rows.map((b, i) => ({ b, a: A.rows[i] }));
const pct = (n, d) => (d ? (100 * n / d).toFixed(1) + "% (" + n + "/" + d + ")" : "n/a");
const sub = (f) => rows.filter(({ b }) => f(b));
const line = (name, f, key) => { const s = sub(f); return `| ${name} | ${pct(s.filter(({ b }) => key(b)).length, s.length)} | ${pct(s.filter(({ a }) => key(a)).length, s.length)} |`; };
const ok = (r) => r.intent_ok, w = (r) => r.anchor_worst === r.exp_anchor, bst = (r) => r.anchor_best === r.exp_anchor, capped = (r) => r.capped;
console.log("| metric | before | after L2+L3 |\n|---|---|---|");
console.log(line("intent acc, all turns", () => true, ok));
console.log(line("intent acc, capability turns", (r) => r.cap, ok));
console.log(line("  code asks", (r) => r.cap && r.exp_intent === "code", ok));
console.log(line("  format asks (table/shorter)", (r) => r.cap && r.exp_intent === "format", ok));
console.log(line("  translate asks", (r) => r.cap && r.exp_intent === "translate", ok));
console.log(line("intent acc, non-capability turns", (r) => !r.cap, ok));
console.log(line("capability turns left on a capped (retrieval + 2-3 sentence) class", (r) => r.cap, capped));
console.log(line("  of which code asks", (r) => r.cap && r.exp_intent === "code", capped));
console.log(line("anchor acc, turns >= 3 (fallback borrows)", (r) => r.turn >= 3, w));
console.log(line("anchor acc, turns >= 3 (fallback keeps own turn)", (r) => r.turn >= 3, bst));
console.log(line("  direct-plan turns >= 3 only (no bound ambiguity)", (r) => r.turn >= 3 && r.plan === "direct", w));
const cap = sub((r) => r.cap);
const mis = cap.filter(({ b }) => !b.intent_ok), fixed = mis.filter(({ a }) => a.intent_ok);
const capCode = cap.filter(({ b }) => b.exp_intent === "code"), misCode = capCode.filter(({ b }) => !b.intent_ok), fixCode = misCode.filter(({ a }) => a.intent_ok);
console.log(`\ncapability misrouted before: ${pct(mis.length, cap.length)}; fixed by L2+L3: ${pct(fixed.length, mis.length)}`);
console.log(`code asks misrouted before: ${pct(misCode.length, capCode.length)}; fixed: ${pct(fixCode.length, misCode.length)}`);
const late = sub((r) => r.turn >= 3), lost = late.filter(({ b }) => !(b.anchor_worst === b.exp_anchor)), regained = lost.filter(({ a }) => a.anchor_worst === a.exp_anchor);
console.log(`anchor lost before (turn>=3, fallback borrows): ${pct(lost.length, late.length)}; regained after: ${pct(regained.length, lost.length)}`);
const ctl = rows.filter(({ b }) => b.kind === "control"), chg = ctl.filter(({ b, a }) => b.class !== a.class);
console.log(`\ncontrol chats: ${ctl.length} turns, intent class changes: ${chg.length}; intent acc ${pct(ctl.filter(({ b }) => b.intent_ok).length, ctl.length)} -> ${pct(ctl.filter(({ a }) => a.intent_ok).length, ctl.length)}; anchor changes ${ctl.filter(({ b, a }) => b.anchor_worst !== a.anchor_worst).length}`);
for (const { b, a } of chg) console.log("  CONTROL CHANGE", b.chat, b.turn, b.text, b.class, "->", a.class);
const ch = rows.filter(({ b, a }) => b.class !== a.class && b.kind === "change");
console.log(`intent-change chats: class changed on ${ch.length} turns; wrongly ${ch.filter(({ b, a }) => b.intent_ok && !a.intent_ok).length} (ok -> not ok)`);
for (const { b, a } of ch.filter(({ b, a }) => b.intent_ok && !a.intent_ok)) console.log("  NEW ERROR", b.chat, b.turn, b.text, b.class, "->", a.class);
if (B.v01 && A.v01) {
  const d = B.v01.map((x, i) => [x, A.v01[i]]).filter(([x, y]) => x.class !== y.class);
  console.log(`\nv0.1 public single turns: classify unchanged ${B.v01.length - d.length}/${B.v01.length}`);
  for (const [x, y] of d) console.log("  V01 CHANGE", x.id, JSON.stringify(x.q), x.class, "->", y.class);
}
if (process.argv.includes("--detail")) {
  console.log("\nREMAINING misrouted capability turns after:");
  for (const { b, a } of cap.filter(({ a }) => !a.intent_ok)) console.log(" ", b.chat, b.turn, JSON.stringify(b.text), "exp", b.exp_intent, "before", b.class, "after", a.class);
  console.log("\nANCHOR misses after (turn>=3, fallback borrows):");
  for (const { b, a } of late.filter(({ a }) => a.anchor_worst !== a.exp_anchor)) console.log(" ", b.chat, b.turn, JSON.stringify(b.text), "plan", a.plan, "exp", a.exp_anchor, "before", b.anchor_worst, "after", a.anchor_worst);
}
