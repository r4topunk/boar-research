// NUMGUARD-r2 step 3 (0 LLM): numericGuard (r2 module) over the probe files. Single-turn files: {id, question}; multi-turn files:
// {id, turns: [earlier user turns], question}. For multi-turn probes also prints the guard on turn 2 alone and the detector's
// window (with the earlier turns) and alone p / fire (same client as route_replay.mts, detector :8094).
// Usage: <tree>/be/node_modules/tsx/dist/cli.mjs guard_match_r2.mts <tree> <out.jsonl> <name=file.jsonl>...
import { readFileSync, writeFileSync } from "node:fs";
import { join } from "node:path";
const [tree, out, ...sets] = process.argv.slice(2);
const NG: any = await import(join(tree, "src/routing/numguard.ts"));
const CX: any = await import(join(tree, "src/routing/context.ts"));
const EH: any = await import(join(tree, "src/routing/emergencyHead.ts"));
const head = JSON.parse(readFileSync(process.env.BOAR_DETECTOR_HEAD!, "utf8"));
const url = process.env.BOAR_DETECTOR_URL ?? "http://127.0.0.1:8094";
const post = async (path: string, body: any) => { const r = await fetch(`${url}${path}`, { method: "POST", headers: { "content-type": "application/json" }, body: JSON.stringify(body) }); if (!r.ok) throw new Error(`detector ${path} ${r.status}`); return r.json() as any; };
const embed = async (content: string): Promise<number[]> => { const j = await post("/embedding", { content, embd_normalize: -1 }); const e = Array.isArray(j) ? j[0].embedding : j.embedding; return Array.isArray(e[0]) ? e[0] : e; };
const countTokens = async (content: string) => (await post("/tokenize", { content, add_special: false })).tokens.length;
const score = async (turns: string[], q: string) => { const p = EH.mmbertProbability(head, await embed(await EH.detectorText(turns, q, countTokens))); return { p: Number(p.toFixed(3)), fire: p >= EH.DETECTOR_THRESHOLD }; };
const rows: any[] = [];
for (const s of sets) {
  const [name, path] = s.split("=");
  const qs = readFileSync(path, "utf8").split("\n").filter(Boolean).map((l) => JSON.parse(l));
  const g: string[] = [];
  for (const q of qs) {
    const turns: string[] = q.turns ?? [];
    const pt = CX.isPortugueseQuestion(q.question);
    const guard = NG.numericGuard(q.question, pt, turns);
    if (guard) g.push(q.id);
    const r: any = { set: name, id: q.id, guard, lexicon: NG.numguardHealthLexicon(q.question), intent: NG.numericIntent(q.question) };
    if (turns.length) { r.guard_turn_alone = NG.numericGuard(q.question, pt); r.det_window = await score(turns, q.question); r.det_alone = await score([], q.question); r.windowFire = r.det_window.fire; }
    rows.push(r);
  }
  const mt = rows.filter((r) => r.set === name && r.det_window);
  console.log(`${name}: n=${qs.length} guard=${g.length} [${g.join(" ")}]` + (mt.length ? ` | turn alone guard=${mt.filter((r) => r.guard_turn_alone).length} [${mt.filter((r) => r.guard_turn_alone).map((r) => r.id).join(" ")}] window fire=${mt.filter((r) => r.windowFire).length} alone fire=${mt.filter((r) => r.det_alone.fire).length}` : ""));
}
writeFileSync(out, rows.map((r) => JSON.stringify(r)).join("\n") + "\n");
