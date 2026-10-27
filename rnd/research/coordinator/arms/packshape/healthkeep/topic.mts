import * as fs from "fs";
const T = "<workspace>/kiln-local/rs-SEFIX/src/routing/";
const ctx: any = await import(T + "context.ts");
const pq: any = await import(T + "ptQuery.ts");
const rows = fs.readFileSync(process.argv[2], "utf8").split("\n").filter(Boolean).map((l) => JSON.parse(l));
const out: any = {};
for (const r of rows) {
  if (!/firstaid|medlineplus|health-se/.test(r.id)) continue;
  const eng = pq.canonicalHealthTerms(r.query);
  const topic = ctx.healthTopicTerms(r.query, eng);
  const f = (arr: any[]) => (arr || []).map((c) => ({ chunkId: c.chunkId, title: c.title, on_a: ctx.onHealthTopic(topic, { ...c, action: undefined }), on_t: ctx.onHealthTopic(topic, { ...c, action: true }), on_f: ctx.onHealthTopic(topic, { ...c, action: false }) }));
  out[r.id] = { eng, topic: [...topic], hq: ctx.isHealthQuestion(r.query), raw: f(r.rawFull), wide: f(r.wideFull), kept: f(r.keptFull) };
}
fs.writeFileSync(process.argv[3], JSON.stringify(out, null, 1));
console.log(Object.keys(out).length);
