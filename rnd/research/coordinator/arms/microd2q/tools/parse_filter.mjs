// MICROD2Q parse + Doc2Query-- filter + inflation flag (0 LLM generation). Parse: one question per non-empty line, leading
// bullets/numbering/quotes stripped, >= 3 words; a chunk "parses" when it yields 3-5 questions (more than 5: first 5 kept).
// Language filter (addendum 1, before dedup and the cosine filter): drop questions with letters outside Latin-1.
// Duplicates: identical normalized question within a chunk. Filter: bge-small-en-v1.5 q8_0 GGUF through node-llama-cpp 3.21.1
// (the engine's own embedding path: embed.ts -> llama.rn shim -> getEmbeddingFor, n_ctx 512, no prefix), cosine(question,
// chunk text); global threshold = 30th percentile of all parsed questions' cosines (drop the lowest 30 %), then keep <= 3 per
// chunk by cosine. Inflation: max token-Jaccard (lowercase alnum words minus stopwords) between a fact chunk's questions and the
// item's self-test question. usage: node parse_filter.mjs <gen.jsonl> <targets.json> <out.json>
import { readFileSync, writeFileSync } from "node:fs";
import { chunkInfo } from "./gen.mjs";
const ROOT = "<workspace>";
const { getLlama } = await import(`${ROOT}/wt/eval/eval/node_modules/node-llama-cpp/dist/index.js`);
const [genF, targetsF, outF] = process.argv.slice(2);
const rows = readFileSync(genF, "utf8").split("\n").filter(Boolean).map((l) => JSON.parse(l));
const T = JSON.parse(readFileSync(targetsF, "utf8"));
const STOP = new Set(("a about above after again against all also am an and any are as at be because been before being below between both but by can could compare comparison describe did difference differences do does doing down during each explain few for from further give had has have having he her here hers him his how i if in into is it its itself just know like me mean means more most much my no nor not now of off on once only or other our out over own please same she should show so some such summarize tell than that the their them then there these they this those through to too under until up us very versus vs was we were what when where which while who whom whose why will with would you your").split(" "));
const toks = (s) => new Set((s.toLowerCase().match(/[a-z0-9]+/g) ?? []).filter((w) => !STOP.has(w)));
const jac = (a, b) => { const A = toks(a), B = toks(b); let i = 0; for (const x of A) if (B.has(x)) i++; return A.size + B.size - i ? i / (A.size + B.size - i) : 0; };
const norm = (s) => s.toLowerCase().replace(/[^a-z0-9 ]/g, "").replace(/\s+/g, " ").trim();
function parse(raw) {
  const qs = String(raw ?? "").split("\n").map((l) => l.replace(/^\s*(?:[-*•]|\d+[.)]|Q\d*[:.)])\s*/i, "").replace(/^["“]|["”]$/g, "").trim()).filter((l) => l.split(/\s+/).length >= 3);
  return qs.slice(0, 5);
}
const llama = await getLlama({ gpu: "auto" });
const model = await llama.loadModel({ modelPath: `${ROOT}/shared-models/bge-small-en-v1.5-q8_0.gguf` });
const ctx = await model.createEmbeddingContext({ contextSize: 512 });
const embed = async (t) => { let s = t; for (;;) { try { return (await ctx.getEmbeddingFor(s)).vector; } catch (e) { if (s.length < 200) throw e; s = s.slice(0, Math.floor(s.length * 0.75)); } } };
const cos = (a, b) => { let d = 0, x = 0, y = 0; for (let i = 0; i < a.length; i++) { d += a[i] * b[i]; x += a[i] * a[i]; y += b[i] * b[i]; } return d / Math.sqrt(x * y); };
const per = []; let nq = 0, dup = 0, over20 = 0, nonLatin = 0;
const NONLATIN = /[\p{L}]/u; const badLang = (q) => [...q].some((ch) => ch.codePointAt(0) > 0xff && NONLATIN.test(ch)); // addendum 1: letters outside Latin-1
for (const r of rows) {
  const qs = parse(r.raw); const seen = new Set(); const uniq = [];
  for (const q of qs) { if (badLang(q)) { nonLatin++; continue; } const k = norm(q); if (seen.has(k)) { dup++; continue; } seen.add(k); uniq.push(q); }
  nq += qs.length; over20 += qs.filter((q) => q.split(/\s+/).length > 20).length;
  const cv = await embed(chunkInfo(r.pack, r.chunk).text);
  const sims = []; for (const q of uniq) sims.push(+cos(await embed(q), cv).toFixed(4));
  per.push({ pack: r.pack, chunk: r.chunk, n: qs.length, parsed: qs.length >= 3, qs: uniq, sims, finish: r.finish, ms: r.ms, ctoks: r.usage?.completion_tokens ?? null });
}
const all = per.flatMap((p) => p.sims).sort((a, b) => a - b); const thr = all[Math.floor(all.length * 0.3)] ?? 0;
for (const p of per) { const ord = p.qs.map((q, i) => [q, p.sims[i]]).filter(([, s]) => s >= thr).sort((a, b) => b[1] - a[1]).slice(0, 3); p.kept = ord.map(([q]) => q); }
// inflation: fact chunks -> items
const ST = {}; const qOf = (id, pack) => { if (!ST[pack]) ST[pack] = Object.fromEntries(readFileSync(`${ROOT}/rnd/research/packs/selftest/${pack}.jsonl`, "utf8").split("\n").filter(Boolean).map((l) => { const o = JSON.parse(l); return [o.id, o.question]; })); return ST[pack][id]; };
const infl = [];
for (const [id, it] of Object.entries(T.items)) for (const c of it.fact_chunks) {
  const p = per.find((x) => x.pack === it.pack && x.chunk === c); if (!p) continue;
  const q = qOf(id, it.pack);
  infl.push({ id, pack: it.pack, chunk: c, split: it.split, jac_all: Math.max(0, ...p.qs.map((x) => jac(x, q))), jac_kept: Math.max(0, ...p.kept.map((x) => jac(x, q))) });
}
const sum = { chunks: per.length, parse_rate: per.filter((p) => p.parsed).length / per.length, questions: nq, dup_rate: nq ? dup / nq : 0, non_latin1_dropped: nonLatin, over20_rate: nq ? over20 / nq : 0,
  filter_threshold: thr, kept_questions: per.reduce((a, p) => a + p.kept.length, 0), keep_rate: per.reduce((a, p) => a + p.kept.length, 0) / Math.max(1, per.reduce((a, p) => a + p.qs.length, 0)),
  finish_length: per.filter((p) => p.finish === "length").length, ms_mean: per.reduce((a, p) => a + p.ms, 0) / per.length, ctoks_mean: per.reduce((a, p) => a + (p.ctoks ?? 0), 0) / per.length,
  inflation: { n: infl.length, jac_all_sorted: infl.map((x) => +x.jac_all.toFixed(3)).sort((a, b) => a - b), jac_kept_sorted: infl.map((x) => +x.jac_kept.toFixed(3)).sort((a, b) => a - b) } };
writeFileSync(outF, JSON.stringify({ summary: sum, inflation: infl, per }, null, 1));
const byPack = {}; for (const p of per) if (p.kept.length) (byPack[p.pack] ??= {})[p.chunk] = p.kept;
writeFileSync(outF.replace(/\.json$/, ".questions.json"), JSON.stringify(byPack));
console.log(JSON.stringify(sum));
await ctx.dispose(); await model.dispose();
