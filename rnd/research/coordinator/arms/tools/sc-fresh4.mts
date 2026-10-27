// S5″ runner (criterion arms/sc-v3-S5second-criterion.md): scores every *.jsonl in arms/sc-fresh4/ ONCE against the frozen
// SC v2 trigger. Lines: {"id", "text", "expect_card": "water"|"snakebite"|"none"}. The engineer never opens that folder.
// usage: tsx sc-fresh4.mts <engine-tree at db7406c9 or a tree with the same trigger sha256s> [dir (default arms/sc-fresh4)]
import fs from "node:fs";
import path from "node:path";
import crypto from "node:crypto";
const tree = process.argv[2];
const R = path.join(tree, "src/routing");
const FROZEN: Record<string, string> = {
  "waterSafety.ts": "032c8ab2480501367c4702aba4c579c2d6fc160e402eb567ca9ab10bf0b92575",
  "firstAidCards.ts": "93ee13f15e54f1c4a052be60cfbafe33f9374fafcfc32006e3e35f47c1afe836",
  "conditionCards.ts": "5c4b5334560e1b00df42cac0bc2d034065d39650e1723ea80a9b81675b4509bc",
};
for (const [f, h] of Object.entries(FROZEN)) {
  const got = crypto.createHash("sha256").update(fs.readFileSync(path.join(R, f))).digest("hex");
  if (got !== h) { console.error(`FROZEN MISMATCH ${f}: ${got} != ${h}`); process.exit(2); }
}
const W = await import(path.join(R, "waterSafety.ts"));
const F = await import(path.join(R, "firstAidCards.ts"));
const CO = await import(path.join(R, "coHazard.ts"));
const C = await import(path.join(R, "conditionCards.ts"));
const { isPortugueseQuestion, isSpanishQuestion } = await import(path.join(R, "context.ts"));
// The engine's fast-path order (answer.ts): snakebite card, CO hazard (EN), water card (EN).
function card(q: string): string {
  if (F.isSnakebiteFirstAid(q)) return "snakebite";
  const en = !isPortugueseQuestion(q) && !isSpanishQuestion(q);
  if (en && CO.isCoHazardQuestion(q)) return "co";
  if (en && W.isWaterSafetyQuestion(q)) return "water";
  return "none";
}
const dir = process.argv[3] ?? path.join(path.dirname(new URL(import.meta.url).pathname), "..", "sc-fresh4");
const files = fs.readdirSync(dir).filter((f) => f.endsWith(".jsonl"));
if (!files.length) { console.error(`no .jsonl in ${dir}`); process.exit(1); }
const items = files.flatMap((f) => fs.readFileSync(path.join(dir, f), "utf8").split("\n").filter(Boolean).map((l) => JSON.parse(l)));
const out: string[] = [`S5″ on ${files.join(", ")} (${items.length} items), trigger sha256s verified`];
let pass = true;
for (const k of ["water", "snakebite"]) {
  const pos = items.filter((d: any) => d.expect_card === k);
  const hit = pos.filter((d: any) => card(d.text) === k);
  const ok = pos.length > 0 && hit.length / pos.length >= 0.8;
  pass &&= ok;
  out.push(`  ${k}: recall ${hit.length}/${pos.length} (${pos.length ? ((100 * hit.length) / pos.length).toFixed(0) : "-"} %) ${ok ? "PASS" : "FAIL"}; misses ${pos.filter((d: any) => card(d.text) !== k).map((d: any) => `${d.id}->${card(d.text)}`).join(" ")}`);
}
// A false fire = a water or snakebite card on an item that doesn't expect that card (incl. a swap between the two).
const ff = items.filter((d: any) => { const c = card(d.text); return (c === "water" || c === "snakebite") && c !== d.expect_card; });
const negN = items.filter((d: any) => d.expect_card === "none").length;
const ffOk = ff.length <= Math.max(1, Math.floor(negN / 25));
pass &&= ffOk;
out.push(`  false fires ${ff.length} on ${negN} expect=none items (bar ≤ 1 per 25) ${ffOk ? "PASS" : "FAIL"}: ${ff.map((d: any) => `${d.id}:${d.expect_card}->${card(d.text)}`).join(" ")}`);
const cond = items.filter((d: any) => d.expect_card === "snakebite").filter((d: any) => C.conversationCondition(d.text, []).condition === "snakebite").length;
out.push(`  (info) health-route snakebite condition on snakebite items: ${cond}/${items.filter((d: any) => d.expect_card === "snakebite").length}`);
out.push(`S5″ ${pass ? "PASS" : "FAIL"}`);
console.log(out.join("\n"));
