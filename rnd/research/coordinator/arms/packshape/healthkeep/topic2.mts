import * as fs from "fs";
const T = "<workspace>/kiln-local/rs-SEFIX/src/routing/";
const ctx: any = await import(T + "context.ts");
const pq: any = await import(T + "ptQuery.ts");
const rows = fs.readFileSync(process.argv[2], "utf8").split("\n").filter(Boolean).map((l) => JSON.parse(l));
const out: any[] = [];
for (const r of rows) {
  const q = r.query ?? r.question; const codes: string[] = r.reasonCodes ?? r.route?.reasonCodes ?? [];
  const eng = pq.canonicalHealthTerms(q); const topic = ctx.healthTopicTerms(q, eng);
  out.push({ id: r.id ?? r.itemId, q, topic: [...topic], health: codes.includes("grounding:health-strict"), fire: codes.includes("detector:fire"), nosrc: codes.includes("grounding:health-no-source"), layer: codes.filter((c) => /^answer:|health-refusal|health-extractive|instant:off-health/.test(c)), p: codes.find((c) => c.startsWith("detector:p=")), keptN: (r.keptFull ?? r.retrieval?.kept ?? []).length, codes });
}
fs.writeFileSync(process.argv[3], JSON.stringify(out, null, 1));
console.log(out.length);
