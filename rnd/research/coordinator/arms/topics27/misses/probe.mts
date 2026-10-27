// VITAL-MISSES stage probe (0 LLM; embedding only). usage: tsx probe.mts <out.json>
// For each probe query and expected title chunk: FTS5 OR-query bm25 rank (pool = first 400), term coverage vs required,
// cosine to the query (pack int8 vec, bge-small as the engine), 0.70 gate, onTopic strict / relaxed (F4), and the
// compression chunk score (best sentence) vs 0.5 x best of the base replay's raw list.
import { DatabaseSync } from "node:sqlite";
import { readFileSync, writeFileSync } from "node:fs";
const B = "<workspace>";
const T = `${B}/kiln-local/be-0cfd4a77-cut7-litepacks/src`;
const S = `${B}/kiln-local/rs-SEFIX/src`;
const pure: any = await import(`${T}/rag/pure.ts`);
const ctx: any = await import(`${T}/routing/context.ts`);
const ctxS: any = await import(`${S}/routing/context.ts`);
const { getLlama } = await import(`${B}/wt/eval/eval/node_modules/node-llama-cpp/dist/index.js`);
const llama = await getLlama({ gpu: false });
const model = await llama.loadModel({ modelPath: `${B}/shared-models/bge-small-en-v1.5-q8_0.gguf` });
const ec = await model.createEmbeddingContext({ contextSize: 512 });
const embed = async (t: string) => Float32Array.from((await ec.getEmbeddingFor(t)).vector);
const db = new DatabaseSync(`${B}/shared-data/packs/wiki-vital5.sqlite`, { readOnly: true });
const D = "<workspace>/rnd/research/coordinator/arms/topics27";
const base = Object.fromEntries(readFileSync(`${D}/replay/misses.A0.jsonl`, "utf8").trim().split("\n").map((l) => JSON.parse(l)).map((r) => [r.id, r]));
const probes: [string, string, string[]][] = [
  ["b13", "How mosquitoes spread disease, and why HIV isn't one of them", ["Mosquito-borne disease", "Mosquito", "HIV", "HIV/AIDS"]],
  ["b15", "Kyoto's role in Japanese history and culture", ["Kyoto", "Heian-kyō", "Kyoto Prefecture"]],
  ["b19", "Travelling in Brazil: plugs, voltage and emergency numbers", ["AC power plugs and sockets", "Mains electricity", "Brazil"]],
  ["b20", "Japan and Germany compared: population density and an aging society", ["Japan", "Germany", "Population density", "Population ageing"]],
  ["b13q", "How do mosquitoes spread disease, and why can't they spread HIV?", ["Mosquito-borne disease", "Mosquito", "HIV"]],
  ["b15q", "What role has Kyoto played in Japanese history and culture?", ["Kyoto", "Heian-kyō"]],
  ["b19s", "What plugs and voltage does Brazil use?", ["AC power plugs and sockets", "Mains electricity", "Brazil"]],
  ["b20q", "How do Japan and Germany compare in population density and aging society?", ["Japan", "Germany", "Population density", "Population ageing"]],
];
const out: any[] = [];
for (const [id, q, titles] of probes) {
  const lq = pure.buildLexicalQuery(q);
  const qv = await embed(q);
  const pool = db.prepare(`SELECT c.id, c.title FROM chunks_fts f JOIN chunks c ON c.id = f.rowid WHERE chunks_fts MATCH ? ORDER BY bm25(chunks_fts)`).all(lq.match) as any[];
  const rankOf = new Map(pool.map((r, i) => [r.id, i + 1]));
  const rawFull = base[id.slice(0, 3)]?.rawFull ?? [];
  const rows: any[] = [];
  for (const t of titles) {
    for (const c of db.prepare(`SELECT id, title, body, vec FROM chunks WHERE title = ? ORDER BY id`).all(t) as any[]) {
      const chunk = { chunkId: `pack:wiki-vital5:${c.id}`, docId: `pack:wiki-vital5:${c.title}`, title: c.title, body: c.body, score: 0 };
      const sim = pure.cosineSimilarityInt8(qv, new Uint8Array(c.vec));
      const cov = pure.countMatchedTerms(`${c.title} ${c.body}`, lq.terms);
      // compression: chunk best-sentence score with this chunk added to the base raw list (same query)
      const list = [...rawFull.filter((x: any) => x.chunkId !== chunk.chunkId), chunk];
      const sc = ctx.scoreSentences(q, list);
      const best = list.map((_: any, ci: number) => Math.max(0, ...sc.filter((s: any) => s.chunkIndex === ci).map((s: any) => s.score)));
      const top = Math.max(0, ...best);
      rows.push({
        title: c.title, chunk: c.id, rank: rankOf.get(c.id) ?? null, inPool: (rankOf.get(c.id) ?? 1e9) <= 400,
        cov, req: pure.requiredTermMatches(lq.terms.length), sim: +sim.toFixed(4), gate70: sim >= 0.7, sem55: sim >= 0.55,
        onTopic: ctx.onTopic(q, chunk), onTopicRelaxed: ctxS.onTopic(q, chunk, true),
        compressShare: top ? +(best[best.length - 1] / top).toFixed(3) : null, body: c.body.slice(0, 140),
      });
    }
  }
  out.push({ id, q, terms: lq.terms.map((t: any) => t.forms[0]), required: pure.requiredTermMatches(lq.terms.length), poolSize: pool.length, proper: (q.match(/[\p{L}][\p{L}\p{N}'’-]*/gu) ?? []).slice(1).filter((w) => /^\p{Lu}/u.test(w)), tokens: ctx.tokenizeTerms(q), rows });
}
writeFileSync(process.argv[2], JSON.stringify(out, null, 1));
for (const o of out) {
  console.log(`\n${o.id} terms=${o.terms.join(",")} req=${o.required} matches=${o.poolSize} proper=${o.proper.join(",")}`);
  for (const r of o.rows) console.log(`  ${r.title} #${r.chunk} rank=${r.rank} pool=${r.inPool} cov=${r.cov}/${r.req} sim=${r.sim} g70=${r.gate70} onTopic=${r.onTopic}/${r.onTopicRelaxed} cmp=${r.compressShare}`);
}
process.exit(0);
