// Guard replay (0 model calls): for every single-turn guard question, the rules' task type before (classifyTask) and after
// (the answer path's rule: classifyTaskInContext unless the turn is health/safety/card/health-follow-up). Also the raw
// in-context classifier with no health guard, to show nothing depends on that guard.
import fs from "node:fs";
import { createRequire } from "node:module";
const tree = process.argv[2];
const { createServer } = await import(createRequire(tree + "/package.json").resolve("vite"));
const server = await createServer({ root: tree, logLevel: "error", server: { middlewareMode: true, hmr: false, watch: null }, appType: "custom", optimizeDeps: { noDiscovery: true } });
const C = await server.ssrLoadModule("/src/routing/classify.ts");
const X = await server.ssrLoadModule("/src/routing/context.ts");
const K = await server.ssrLoadModule("/src/routing/conditionCards.ts");
const B = "<workspace>/boar-eval/bench/";
const sets = { "v0.1": B + "v0.1/questions.public.jsonl", safepack: B + "selftest/safepack/questions.jsonl", "packread-v1": B + "slices/packread-v1/questions.jsonl" };
const out = {};
for (const [name, f] of Object.entries(sets)) {
  const rows = fs.readFileSync(f, "utf8").trim().split("\n").map((l) => JSON.parse(l));
  let changedRaw = 0, changedEngine = 0, health = 0, danger = 0;
  const changes = [];
  for (const r of rows) {
    const q = r.question;
    const healthTurn = X.isHealthQuestion(q) || X.isSafetyQuery(q) || K.isCardEmergency(q) || X.isHealthFollowUp(q, []);
    const before = C.classifyTask(q), raw = C.classifyTaskInContext(q, []), after = healthTurn ? before : raw;
    if (healthTurn) health++; if (r.danger) danger++;
    if (raw !== before) { changedRaw++; changes.push({ id: r.id, q, before, raw, after, healthTurn, danger: !!r.danger }); }
    if (after !== before) changedEngine++;
  }
  out[name] = { n: rows.length, danger, lexical_health: health, changed_raw: changedRaw, changed_engine: changedEngine, changes };
}
await server.close();
console.log(JSON.stringify(out, null, 1));
