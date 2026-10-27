// Sonar exp-14 (design input for the big-pack relevance gate): for v1's gained/lost items, classify the big-pack
// (enwiki top-100k, title without a source label, source "Wikipedia —") passages in the pre-answer sources and in raw as
// named (title or its singular = one of the question's title candidates, wikiPack.titleCandidates @0cfd4a77) vs keyword,
// and the bge-small cosine question↔shown passage text (pre only has text). Traces: ios-main-v5-s42-kic vs ios-enwiki-s42-kic.
import fs from "node:fs";
import { titleCandidates } from "./src/rag/wikiPack.ts";
const { getLlama } = await import("<workspace>/wt/eval/eval/node_modules/node-llama-cpp/dist/index.js");
const R = "<workspace>/boar-eval/runs/night-2026-10-01/";
const load = (f: string) => Object.fromEntries(fs.readFileSync(R + f, "utf8").split("\n").filter(Boolean).map((l) => { const t = JSON.parse(l); return [t.itemId, t]; }));
const B = load("ios-enwiki-s42-kic.traces.jsonl"), A = load("ios-main-v5-s42-kic.traces.jsonl");
const llama = await getLlama({ logLevel: "error" });
const bge = await llama.loadModel({ modelPath: "<workspace>/shared-models/bge-small-en-v1.5-q8_0.gguf" });
const emb = await bge.createEmbeddingContext();
const vec = async (t: string) => Float32Array.from((await emb.getEmbeddingFor(bge.tokenize(t).slice(0, 480))).vector);
const cos = (a: Float32Array, b: Float32Array) => { let d = 0, x = 0, y = 0; for (let i = 0; i < a.length; i++) { d += a[i] * b[i]; x += a[i] * a[i]; y += b[i] * b[i]; } return d / Math.sqrt(x * y); };
const big = (s: any) => (s.source ?? "").startsWith("Wikipedia —") && !/^Wikivoyage/.test(s.title);
const gained = ["lan-ref-004", "lan-ref-005", "lan-rsn-001", "saf-010", "vit-cry-010", "vit-hlt-003", "vit-hum-001", "vit-hum-004"];
const lost = ["lan-ref-001", "lan-rsn-007", "saf-003", "saf-008", "vit-cry-011", "vit-cry-004"];
for (const [lab, ids] of [["GAINED", gained], ["LOST", lost]] as const) {
  console.log(`\n== ${lab}`);
  for (const id of ids) {
    const t = B[id]; if (!t) { console.log(id, "missing"); continue; }
    const cands = new Set(titleCandidates(t.question).map((c) => c.toLowerCase()));
    const named = (title: string) => cands.has(title.toLowerCase()) || cands.has(title.toLowerCase().replace(/s$/, ""));
    const qv = await vec(t.question);
    const ev = t.events.filter((e: any) => e.type === "sources"); const pre = ev.at(-1)?.sources ?? [];
    const rawBig = t.retrieval.raw.filter(big).map((s: any) => `${s.title}${named(s.title) ? "[N]" : "[K]"}`);
    const preBig = [];
    for (const s of pre.filter(big)) preBig.push(`${s.title}${named(s.title) ? "[N]" : "[K]"} cos=${s.text ? cos(qv, await vec(s.text)).toFixed(2) : "?"}`);
    const baseRaw = A[id]?.retrieval.raw.map((s: any) => s.title) ?? [];
    console.log(`${id} | ${t.question.slice(0, 60)}\n   raw big: ${rawBig.join(", ")}\n   pre big: ${preBig.join(", ") || "-"}\n   base raw: ${baseRaw.join(", ")}`);
  }
}
