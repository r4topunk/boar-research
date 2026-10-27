// NUMGUARD-r3 effective override (0 LLM; after review/override_eff.mts, one tree). Per probe, with the detector live (:8094, v3b head):
// window p (with the earlier turns) and alone p (DETMAX), fire, windowFire, numericGuard, and which deterministic answer the guard
// would let through (calculate() or travelDistanceAnswer; answer.ts r3 lets nothing else answer a guarded turn). effective = fire
// && !windowFire && guard && calculator. Also prints the cut 7 arithmetic shortcut (runs on fired turns with or without the guard; info).
// Usage: <tree>/be/node_modules/tsx/dist/cli.mjs override_r3.mts <tree> <out.jsonl> <name=file.jsonl>...
import { readFileSync, writeFileSync } from "node:fs";
import { join } from "node:path";
const [tree, out, ...files] = process.argv.slice(2);
const NG: any = await import(join(tree, "src/routing/numguard.ts"));
const CX: any = await import(join(tree, "src/routing/context.ts"));
const CA: any = await import(join(tree, "src/routing/calculators.ts"));
const AR: any = await import(join(tree, "src/routing/arithmetic.ts"));
const TR: any = await import(join(tree, "src/routing/travelDistance.ts"));
const EH: any = await import(join(tree, "src/routing/emergencyHead.ts"));
const head = JSON.parse(readFileSync(process.env.BOAR_DETECTOR_HEAD!, "utf8"));
const url = process.env.BOAR_DETECTOR_URL ?? "http://127.0.0.1:8094";
const post = async (p: string, b: any) => { const r = await fetch(`${url}${p}`, { method: "POST", headers: { "content-type": "application/json" }, body: JSON.stringify(b) }); if (!r.ok) throw new Error(`detector ${p} ${r.status}`); return r.json() as any; };
const embed = async (c: string) => { const j = await post("/embedding", { content: c, embd_normalize: -1 }); const e = Array.isArray(j) ? j[0].embedding : j.embedding; return Array.isArray(e[0]) ? e[0] : e; };
const ct = async (c: string) => (await post("/tokenize", { content: c, add_special: false })).tokens.length;
const score = async (turns: string[], q: string) => EH.mmbertProbability(head, await embed(await EH.detectorText(turns, q, ct)));
const rows: any[] = [];
for (const f of files) {
  const [name, path] = f.split("=");
  const qs = readFileSync(path, "utf8").split("\n").filter(Boolean).map((l) => JSON.parse(l));
  for (const q of qs) {
    const turns: string[] = q.turns ?? [];
    const pw = await score(turns, q.question); const pa = turns.length ? await score([], q.question) : pw;
    const windowFire = turns.length > 0 && pw >= EH.DETECTOR_THRESHOLD; const fire = pw >= EH.DETECTOR_THRESHOLD || pa >= EH.DETECTOR_THRESHOLD;
    const pt = CX.isPortugueseQuestion(q.question); const es = CX.isSpanishQuestion(q.question);
    const guard = NG.numericGuard(q.question, pt, turns);
    const calculator = CA.calculate(q.question, pt)?.kind ?? (pt || es ? null : TR.travelDistanceAnswer(q.question) ? "travel" : null);
    const arith = pt || es ? null : AR.arithmeticAnswer(q.question)?.kind ?? null;
    const effective = fire && !windowFire && guard && calculator !== null;
    rows.push({ set: name, id: q.id, p: Number(Math.max(pw, pa).toFixed(3)), fire, windowFire, guard, calculator, effective, no_calculator: fire && !windowFire && guard && calculator === null, arith_cut7: fire ? arith : null });
  }
  const rs = rows.filter((r) => r.set === name);
  const ids = (k: string) => rs.filter((r) => r[k]).map((r) => r.id).join(" ");
  console.log(`${name}: n=${rs.length} fire=${rs.filter((r) => r.fire).length} guard=${rs.filter((r) => r.guard).length} [${ids("guard")}] effective=${rs.filter((r) => r.effective).length} [${ids("effective")}] no-calculator=${rs.filter((r) => r.no_calculator).length} [${ids("no_calculator")}] arith_cut7_on_fire=[${rs.filter((r) => r.arith_cut7).map((r) => r.id).join(" ")}]`);
}
writeFileSync(out, rows.map((r) => JSON.stringify(r)).join("\n") + "\n");
