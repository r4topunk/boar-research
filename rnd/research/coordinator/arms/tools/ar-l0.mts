// AR L0 (criterion arms/ar-L0-criterion.md). usage: tsx ar-l0.mts <engine-tree> [heldout.jsonl]
import fs from "node:fs";
import path from "node:path";
const tree = process.argv[2];
const { arithmeticAnswer } = await import(path.join(tree, "src/routing/arithmetic.ts"));
const B = "<workspace>";
const A = path.join(B, "rnd/research/coordinator/arms");
const jl = (p: string) => fs.readFileSync(p, "utf8").split("\n").filter(Boolean).map((l) => JSON.parse(l));
const lastUser = (d: any) => { const t = d.turns[d.turns.length - 1]; return typeof t === "string" ? t : d.turns.filter((x: any) => x.role === "user").at(-1).text; };

const out: string[] = [];
const v01 = jl(`${B}/boar-eval/bench/v0.1/questions.public.jsonl`).filter((q: any) => q.lang === "en");
const sci = arithmeticAnswer(v01.find((q: any) => q.id === "vit-sci-003").question);
const a1 = !!sci && Math.abs(sci.value - 83.333) < 0.05 && /43\.3/.test(sci.text) && /40 seconds/.test(sci.text);
out.push(`A1 vit-sci-003: ${sci ? sci.text : "no fire"} -> ${a1 ? "PASS" : "FAIL"}`);
const cry = arithmeticAnswer(v01.find((q: any) => q.id === "vit-cry-009").question);
out.push(`A2 vit-cry-009: ${cry ? cry.text : "no fire (no constants in the question; pinned-passage constants not implemented)"} -> ${cry ? "check" : "FAIL"}`);

// A3: dev probe positives (unit tests are counted from vitest separately).
const probes = jl(`${A}/probes/arithmetic.probes.jsonl`);
let pos = 0, posOk = 0, wrong: string[] = [];
for (const p of probes.filter((p: any) => p.expect === "pos")) {
  pos++;
  const r = arithmeticAnswer(p.text);
  if (r && Math.abs(r.value - p.answer) < 0.51) posOk++;
  else if (r) wrong.push(`${p.id} got ${r.value} want ${p.answer}`);
}
out.push(`A3 dev-probe positives: ${posOk}/${pos} exact, wrong numbers ${wrong.length} ${wrong.join("; ")}`);

// A4: non-arithmetic EN dev messages.
const E = `${B}/rnd/research/sonar/exp/30-learned-detector/data/`;
const chat: string[] = [];
for (const f of ["slice.v0.jsonl", "v1-fresh/slice.v1.jsonl", "v2-fresh/slice.v2.jsonl"])
  for (const d of jl(`${B}/rnd/research/compass/chat-slice/${f}`)) if (d.lang === "en") chat.push(d.turns.filter((t: any) => t.role === "user").at(-1).text);
const pools: [string, string[]][] = [
  ["aligned-en", jl(E + "aligned-en.jsonl").map(lastUser)],
  ["terse-live-en", jl(E + "terse-live.jsonl").filter((d: any) => d.lang === "en").map(lastUser)],
  ["compass-dev-en", jl(`${B}/rnd/research/compass/exp/emergency-dev/dev.jsonl`).filter((d: any) => (d.lang ?? "en") === "en").map(lastUser)],
  ["chat-slice-en", chat],
  ["v0.1-en (minus the 2 AR items)", v01.filter((q: any) => !["vit-sci-003", "vit-cry-009"].includes(q.id)).map((q: any) => q.question)],
  ["dev-probe negatives", probes.filter((p: any) => p.expect === "neg").map((p: any) => p.text)],
];
let n4 = 0, f4: string[] = [];
for (const [name, qs] of pools) {
  const fires = qs.filter((q) => arithmeticAnswer(q));
  n4 += qs.length;
  f4.push(...fires.map((q) => `${name}: ${q.slice(0, 120)}`));
  out.push(`  ${name}: ${fires.length}/${qs.length}`);
}
out.push(`A4 non-arithmetic EN dev: fires ${f4.length}/${n4}${f4.length ? "\n    " + f4.join("\n    ") : ""}`);

// A5: guard on emergency-dev (all 300, any language): any item the calculator would answer = a guarded emergency.
const ed = jl(`${B}/rnd/research/compass/exp/emergency-dev/dev.jsonl`);
const guarded = ed.filter((d: any) => arithmeticAnswer(lastUser(d)));
out.push(`A5 emergency-dev guard applies: ${guarded.length}/${ed.length}${guarded.map((d: any) => `\n    ${d.id}`).join("")}`);

// A6: held-out (optional second arg), scored once.
if (process.argv[3]) {
  const H = jl(process.argv[3]);
  let hp = 0, hok = 0, hw: string[] = [], hn = 0, hf: string[] = [];
  for (const p of H) {
    const r = arithmeticAnswer(p.text);
    if (p.expect === "pos") { hp++; if (r && Math.abs(r.value - p.answer) < 0.51) hok++; else if (r) hw.push(`${p.id} got ${r.value} want ${p.answer}`); }
    else { hn++; if (r) hf.push(`${p.id}: ${p.text}`); }
  }
  out.push(`A6 held-out: recall ${hok}/${hp}; wrong numbers ${hw.length} ${hw.join("; ")}; false fires ${hf.length}/${hn} ${hf.join(" | ")}`);
}
console.log(out.join("\n"));
