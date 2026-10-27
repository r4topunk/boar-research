// quick look: tsx ar-probe.mts <tree> <probes.jsonl>
import fs from "node:fs";
const { arithmeticAnswer } = await import(process.argv[2] + "/src/routing/arithmetic.ts");
for (const l of fs.readFileSync(process.argv[3], "utf8").split("\n").filter(Boolean)) {
  const p = JSON.parse(l); const r = arithmeticAnswer(p.text);
  const ok = p.expect === "pos" ? r && Math.abs(r.value - p.answer) < 0.51 : !r;
  console.log(`${ok ? "ok " : "BAD"} ${p.id} ${p.expect} exp=${p.answer} got=${r ? r.value.toFixed(2) : "-"} | ${r ? r.text : p.text}`);
}
