import fs from "node:fs";
const W = await import(process.argv[2] + "/src/routing/waterSafety.ts");
for (const f of process.argv.slice(3)) for (const l of fs.readFileSync(f, "utf8").split("\n").filter(Boolean)) {
  const p = JSON.parse(l); const got = W.isWaterSafetyQuestion(p.text);
  if ((p.expect === "pos") !== got) console.log(p.id, p.expect, "|", p.text);
}
