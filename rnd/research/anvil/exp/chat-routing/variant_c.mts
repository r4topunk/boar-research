// C: the engine's current rule (upstream/main 0cfd4a77 classify.ts): retrieval runs unless isRetrievalIrrelevant(classifyTask(msg)).
import fs from "node:fs";
import { classifyTask, isRetrievalIrrelevant } from "./classify.ts";
for (const l of fs.readFileSync("items.jsonl", "utf8").trim().split("\n")) {
  const it = JSON.parse(l); const t0 = performance.now();
  const task = classifyTask(it.msg); const decision = isRetrievalIrrelevant(task) ? "ANSWER" : "SEARCH";
  console.log(JSON.stringify({ id: it.id, label: it.label, kind: it.kind, variant: "C", task, decision, ms: +(performance.now() - t0).toFixed(3) }));
}
