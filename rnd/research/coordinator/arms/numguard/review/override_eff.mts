import { readFileSync } from "node:fs";
import { join } from "node:path";
const [finalTree, fixTree, ...files] = process.argv.slice(2);
const load = async (t: string) => ({ NG: await import(join(t, "src/routing/numguard.ts")) as any, CX: await import(join(t, "src/routing/context.ts")) as any, CA: await import(join(t, "src/routing/calculators.ts")) as any, AR: await import(join(t, "src/routing/arithmetic.ts")) as any, TR: await import(join(t, "src/routing/travelDistance.ts")) as any });
const F = await load(finalTree), X = await load(fixTree);
const EH: any = await import(join(finalTree, "src/routing/emergencyHead.ts"));
const head = JSON.parse(readFileSync(process.env.BOAR_DETECTOR_HEAD!, "utf8"));
const url = process.env.BOAR_DETECTOR_URL!;
const post = async (p: string, b: any) => (await fetch(`${url}${p}`, { method: "POST", headers: { "content-type": "application/json" }, body: JSON.stringify(b) })).json() as any;
const embed = async (c: string) => { const j = await post("/embedding", { content: c, embd_normalize: -1 }); const e = Array.isArray(j) ? j[0].embedding : j.embedding; return Array.isArray(e[0]) ? e[0] : e; };
const ct = async (c: string) => (await post("/tokenize", { content: c, add_special: false })).tokens.length;
const score = async (turns: string[], q: string) => EH.mmbertProbability(head, await embed(await EH.detectorText(turns, q, ct)));
for (const f of files) {
  const [name, path] = f.split("=");
  let nf = 0, nx = 0, n = 0; const ef: string[] = [], ex: string[] = [];
  for (const l of readFileSync(path, "utf8").split("\n").filter(Boolean)) {
    const q = JSON.parse(l); const turns: string[] = q.turns ?? []; n++;
    const pw = await score(turns, q.question); const pa = turns.length ? await score([], q.question) : pw;
    const windowFire = turns.length > 0 && pw >= EH.DETECTOR_THRESHOLD; const fire = pw >= EH.DETECTOR_THRESHOLD || pa >= EH.DETECTOR_THRESHOLD;
    const pt = F.CX.isPortugueseQuestion(q.question);
    const gF = fire && !windowFire && F.NG.numericGuard(q.question, pt, turns);
    const det = (M: any) => M.CA.calculate(q.question, pt)?.kind ?? (pt || M.CX.isSpanishQuestion(q.question) ? null : M.AR.arithmeticAnswer(q.question)?.kind) ?? (pt || M.CX.isSpanishQuestion(q.question) ? null : M.TR.travelDistanceAnswer(q.question) ? "travel" : null) ?? null;
    const gX = fire && !windowFire && X.NG.numericGuard(q.question, pt, turns) && det(X) !== null;
    if (gF) ef.push(`${q.id}(${det(F) ?? "model"})`); if (gX) ex.push(`${q.id}(${det(X)})`);
    console.log(`${name}\t${q.id}\tp=${Math.max(pw, pa).toFixed(3)}\tfinal=${gF ? "OVERRIDE:" + (det(F) ?? "model") : "-"}\tfix=${gX ? "OVERRIDE:" + det(X) : "-"}`);
  }
  console.log(`== ${name}: n=${n} final overrides=${ef.length} [${ef.join(" ")}] | fix overrides=${ex.length} [${ex.join(" ")}]`);
}
