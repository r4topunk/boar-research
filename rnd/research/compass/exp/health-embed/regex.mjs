import fs from "fs";
const E = fs.readFileSync("eval.jsonl", "utf8").trim().split("\n").map(JSON.parse);
const out = {};
for (const v of ["iosmain", "fix08c", "upstream"]) {
  const m = await import(`./context.${v}.ts`);
  out[v] = E.map(e => m.isHealthQuestion(e.q));
}
fs.writeFileSync("regex.json", JSON.stringify(out));
console.log("ok");
