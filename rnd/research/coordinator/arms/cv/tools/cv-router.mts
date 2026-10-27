// cv-router: L0 routing of the CV router on the DEV probe questions (question text and kind only; never arms/cv/gold)
// and on Sonar's EN dev messages.
// usage: tsx cv-router.mts [--tree <workspace>/wt/cv] [--out router-dev.txt] [--fires dev-fires.jsonl] [--show-misses]
import fs from "node:fs";
const arg = (k: string, d: string) => { const i = process.argv.indexOf(k); return i >= 0 ? process.argv[i + 1] : d; };
const tree = arg("--tree", "<workspace>/wt/cv");
const B = "<workspace>", A = `${B}/rnd/research/coordinator/arms`;
const { routeVerdict } = await import(`${tree}/src/routing/computedVerdict.ts`);
const jl = (p: string) => fs.readFileSync(p, "utf8").split("\n").filter(Boolean).map((l) => JSON.parse(l));
const items = [...jl(`${A}/vg-probe-q/items.jsonl`), ...jl(`${A}/vg-probe-q2/items.jsonl`)];
const out: string[] = [];
const say = (s: string) => { out.push(s); console.log(s); };
const verdictItems = items.filter((i) => i.kind !== "control");
const controls = items.filter((i) => i.kind === "control");
const fired = verdictItems.filter((i) => routeVerdict(i.question));
say(`CV router on DEV probe questions (vg-probe-q 90 + vg-probe-q2 120 = ${items.length}); tree ${tree}`);
say(`verdict items: ${fired.length}/${verdictItems.length} fire (${(100 * fired.length / verdictItems.length).toFixed(1)} %), bar >= 80 %`);
const kinds: Record<string, [number, number]> = {};
for (const i of verdictItems) { const k = i.kind; kinds[k] ??= [0, 0]; kinds[k][1]++; if (routeVerdict(i.question)) kinds[k][0]++; }
for (const [k, [f, n]] of Object.entries(kinds)) say(`  ${k}: ${f}/${n}`);
const byPlan: Record<string, number> = {};
for (const i of fired) { const p = routeVerdict(i.question)!; const k = p.kind + (p.kind === "compare" ? `/${p.form}` : ""); byPlan[k] = (byPlan[k] ?? 0) + 1; }
say(`  plan kinds: ${JSON.stringify(byPlan)}`);
const ff = controls.filter((i) => routeVerdict(i.question));
say(`controls: ${ff.length}/${controls.length} false fires (bar 0)${ff.length ? "\n  " + ff.map((i) => `${i.id} ${i.question}`).join("\n  ") : ""}`);
if (process.argv.includes("--show-misses")) say("misses:\n  " + verdictItems.filter((i) => !routeVerdict(i.question)).map((i) => `${i.id} [${i.kind}] ${i.question}`).join("\n  "));
// Sonar's EN dev messages (same loader as arms/tools/vg4-gate.mts)
const E = `${B}/rnd/research/sonar/exp/30-learned-detector/data/`;
const last = (d: any) => { const t = d.turns.at(-1); return typeof t === "string" ? t : d.turns.filter((x: any) => x.role === "user").at(-1).text; };
const qs: string[] = [...jl(E + "aligned-en.jsonl"), ...jl(E + "terse-live.jsonl").filter((d: any) => d.lang === "en"), ...jl(`${B}/rnd/research/compass/exp/emergency-dev/dev.jsonl`).filter((d: any) => (d.lang ?? "en") === "en")].map(last);
const fires = qs.map((q) => ({ q, p: routeVerdict(q) })).filter((x) => x.p);
say(`Sonar EN dev messages: ${qs.length}; CV fires ${fires.length}`);
for (const f of fires) say(`  FIRE [${f.p!.kind}] ${f.q}`);
fs.writeFileSync(arg("--out", `${A}/cv/router-dev.txt`), out.join("\n") + "\n");
fs.writeFileSync(arg("--fires", `${A}/cv/dev-fires.jsonl`), fires.map((f) => JSON.stringify({ question: f.q, kind: f.p!.kind, plan: f.p })).join("\n") + (fires.length ? "\n" : ""));
