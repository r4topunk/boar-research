import fs from "fs";
const { classifyTask } = await import("./classify.ts");
const E = fs.readFileSync("../health-embed/eval.jsonl", "utf8").trim().split("\n").map(JSON.parse);
const out = E.map((e) => ({ id: e.id, label: e.label, task: classifyTask(e.q), q: e.q }));
fs.writeFileSync("tasks.json", JSON.stringify(out));
const c = {};
for (const o of out) { const k = `${o.label}:${o.task}`; c[k] = (c[k] ?? 0) + 1; }
console.log(c);
for (const o of out.filter((o) => o.label !== "neg" && o.task === "chat")) console.log(" ", o.id, "|", o.q.slice(0, 90));
