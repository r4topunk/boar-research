// NUMGUARD-2 step 5: 0-LLM route replay. Same detector client and numericGuard as route_replay.mts; adds whether
// NUMGUARD_NORETRIEVE=1 changes the turn vs NUMGUARD=1 alone: ng2_acts = guard acts (fire && guard) AND no instant shortcut
// answers (calculate / arithmeticAnswer / travelDistanceAnswer, EN). FACTS is not evaluated, so ng2_acts over-counts (conservative).
// Usage (cwd = numguard tree): be/node_modules/tsx/dist/cli.mjs route_replay2.mts <tree> <out.jsonl> <name=questions.jsonl>...
import { readFileSync, writeFileSync } from "node:fs";
import { join } from "node:path";
const [tree, out, ...sets] = process.argv.slice(2);
const EH: any = await import(join(tree, "src/routing/emergencyHead.ts"));
const NG: any = await import(join(tree, "src/routing/numguard.ts"));
const CX: any = await import(join(tree, "src/routing/context.ts"));
const CA: any = await import(join(tree, "src/routing/calculators.ts"));
const AR: any = await import(join(tree, "src/routing/arithmetic.ts"));
const TD: any = await import(join(tree, "src/routing/travelDistance.ts"));
const head = JSON.parse(readFileSync(process.env.BOAR_DETECTOR_HEAD!, "utf8"));
const url = process.env.BOAR_DETECTOR_URL ?? "http://127.0.0.1:8094";
const thr = EH.DETECTOR_THRESHOLD;
const post = async (path: string, body: any) => {
  const r = await fetch(`${url}${path}`, { method: "POST", headers: { "content-type": "application/json" }, body: JSON.stringify(body) });
  if (!r.ok) throw new Error(`detector ${path} ${r.status}`);
  return r.json() as any;
};
const embed = async (content: string): Promise<number[]> => { const j = await post("/embedding", { content, embd_normalize: -1 }); const e = Array.isArray(j) ? j[0].embedding : j.embedding; return Array.isArray(e[0]) ? e[0] : e; };
const countTokens = async (content: string) => (await post("/tokenize", { content, add_special: false })).tokens.length;
if (head.kind !== "mmbert-cls") throw new Error("expected the mmbert head");
const rows: any[] = [];
for (const s of sets) {
  const [set, path] = s.split("=");
  for (const q of readFileSync(path, "utf8").split("\n").filter(Boolean).map((l) => JSON.parse(l))) {
    const text = await EH.detectorText([], q.question, countTokens);
    const p = EH.mmbertProbability(head, await embed(text));
    const pt = CX.isPortugueseQuestion(q.question), es = CX.isSpanishQuestion(q.question);
    const fire = p >= thr, guard = NG.numericGuard(q.question, pt), acts = fire && guard;
    const shortcut = !!CA.calculate(q.question, pt) || (!pt && !es && (!!AR.arithmeticAnswer(q.question) || !!TD.travelDistanceAnswer(q.question)));
    rows.push({ set, id: q.id, p: Number(p.toFixed(3)), fire, guard, ng_acts: acts, shortcut, ng2_acts: acts && !shortcut });
  }
}
writeFileSync(out, rows.map((r) => JSON.stringify(r)).join("\n") + "\n");
const by = new Map<string, any[]>(); for (const r of rows) by.set(r.set, [...(by.get(r.set) ?? []), r]);
const ids = (rs: any[], k: string) => rs.filter((r) => r[k]).map((r) => r.id).join(" ");
for (const [set, rs] of by) console.log(`${set}: n=${rs.length} fire=${rs.filter((r) => r.fire).length} ng_acts=${rs.filter((r) => r.ng_acts).length} [${ids(rs, "ng_acts")}] ng2_changes=${rs.filter((r) => r.ng2_acts).length} [${ids(rs, "ng2_acts")}]`);
console.log(`threshold ${thr}; total n=${rows.length} ng2_changes=${rows.filter((r) => r.ng2_acts).length}`);
