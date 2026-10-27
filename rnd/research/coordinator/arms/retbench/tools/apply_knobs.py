#!/usr/bin/env python3
"""RETBENCH: apply the switch-guarded knobs to a clone of kiln-local/rs-SEFIX (in place). usage: python3 -I apply_knobs.py <tree>
Every knob reads an RS_RB_* env var; absent = the rs-SEFIX code path byte-for-byte (behaviour), so identity with the switches off is required."""
import sys, re
T = sys.argv[1]
def sub(path, old, new, count=1):
    p = f"{T}/{path}"; s = open(p).read()
    assert s.count(old) == count, (path, old[:80], s.count(old)); open(p, "w").write(s.replace(old, new))
ENV = "(globalThis as any).process?.env"
BYTES = '''
/** RETBENCH (bench-only): RS_BYTES_LOG=<file> appends one JSON line per vector read {k: kind, b: bytes}. */
export function rbBytes(kind: string, bytes: number): void {
  const f = (globalThis as any).process?.env?.RS_BYTES_LOG;
  if (!f || !bytes) return;
  (globalThis as any).process.getBuiltinModule("node:fs").appendFileSync(f, JSON.stringify({ k: kind, b: bytes }) + "\\n");
}
'''
# ---------------- pure.ts: floor + bytes helper
sub("src/rag/pure.ts", "export function gateByRelevance<T extends { similarity?: number }>(\n  chunks: T[],\n  minSimilarity = ANSWER_MIN_SIMILARITY\n): T[] {\n",
    "export function gateByRelevance<T extends { similarity?: number }>(\n  chunks: T[],\n  minSimilarity = ANSWER_MIN_SIMILARITY\n): T[] {\n"
    f"  // RETBENCH floor (RS_RB_FLOOR, bench-only, default off = 0.7): the cosine relevance floor of the fused lists.\n  if (minSimilarity === ANSWER_MIN_SIMILARITY && Number({ENV}?.RS_RB_FLOOR) > 0) minSimilarity = Number({ENV}?.RS_RB_FLOOR);\n")
s = open(f"{T}/src/rag/pure.ts").read(); open(f"{T}/src/rag/pure.ts", "w").write(s + BYTES)
# ---------------- context.ts: compress floor
sub("src/routing/context.ts", "chunkBest[ci] >= RELATIVE_RELEVANCE_FLOOR * topBest;",
    f"chunkBest[ci] >= (Number({ENV}?.RS_RB_COMPRESS) > 0 ? Number({ENV}?.RS_RB_COMPRESS) : RELATIVE_RELEVANCE_FLOOR) * topBest; // RETBENCH RS_RB_COMPRESS")
# ---------------- answer.ts: k override + lead header
sub("src/routing/answer.ts", "          ? deps.retrieve(searchQuery, gen?.retrieveK ?? 6, { packDense2:",
    f"          ? deps.retrieve(searchQuery, Number({ENV}?.RS_RB_K) > 0 ? Number({ENV}?.RS_RB_K) : gen?.retrieveK ?? 6, {{ packDense2:")
sub("src/routing/answer.ts", "          : deps.retrieve(searchQuery, gen?.retrieveK ?? 6)\n",
    f"          : deps.retrieve(searchQuery, Number({ENV}?.RS_RB_K) > 0 ? Number({ENV}?.RS_RB_K) : gen?.retrieveK ?? 6) // RETBENCH RS_RB_K\n")
sub("src/routing/answer.ts", """      if (sources.length && gen?.mode !== "multipass") {
        emit({ type: "sources", answerId""", f"""      // RETBENCH lead header (RS_RB_LEAD=1, bench-only; = ARTCAP cap4lead's header): title + lead sentence of the first kept user-pack article.
      if ({ENV}?.RS_RB_LEAD === "1" && gen?.mode !== "multipass" && sources.length) {{
        let lead = await (await import("../rag/packs")).packLeadHeader(sources);
        if (lead && health && !healthFallback && !onHealthTopic(healthTopicTerms(req.query, english), lead)) {{
          reasonCodes.push("rb:lead:health-dropped");
          lead = null;
        }}
        if (lead) {{
          reasonCodes.push(`rb:lead:add:${{lead.chunkId}}`);
          sources = [...sources, lead];
        }}
      }}
      if (sources.length && gen?.mode !== "multipass") {{
        emit({{ type: "sources", answerId""")
# ---------------- packs.ts: format-1 FTS pool, lead header, bytes
sub("src/rag/packs.ts", 'import { buildLexicalQuery, cosineSimilarityInt8, filterByMinScore, filterByTermCoverage, MIN_SEMANTIC_SIMILARITY } from "./pure";',
    'import { buildLexicalQuery, cosineSimilarityInt8, filterByMinScore, filterByTermCoverage, MIN_SEMANTIC_SIMILARITY, rbBytes } from "./pure";')
sub("src/rag/packs.ts", "        [lexicalQuery.match, PACK_CANDIDATES]\n      );\n",
    f"        [lexicalQuery.match, Number({ENV}?.RS_RB_POOL) > 0 ? Number({ENV}?.RS_RB_POOL) : PACK_CANDIDATES] // RETBENCH RS_RB_POOL\n      );\n"
    "      rbBytes(\"f1-pool\", rows.reduce((n, r) => n + (r.vec?.length ?? 0), 0));\n")
sub("src/rag/packs.ts", "type PackRow = { id: number; title: string; body: string; vec: Uint8Array; rank: number };", '''/** RETBENCH RS_RB_LEAD (bench-only; ARTCAP cap4lead's header): for the first of `kept` from a user-installed (non-kit) format-2 pack, a short header
 *  chunk (article title + first sentence of its lead chunk), unless that lead chunk is already in `kept`; null when none. */
export async function packLeadHeader(kept: RetrievedChunk[]): Promise<RetrievedChunk | null> {
  for (const c of kept) {
    const m = /^pack:([^:]+):(\\d+)$/.exec(c.chunkId);
    if (!m) continue;
    const packId = m[1];
    if (HEADPASS_KIT.has(packId.replace(/^local-/, ""))) continue;
    const wp = wikiPacks.get(packId);
    if (!wp) continue;
    const h = await wp.rsLeadHeaderOf(Number(m[2]));
    if (!h) return null;
    const chunk = packHitToChunk(packId, h);
    return kept.some((x) => x.chunkId === chunk.chunkId) ? null : chunk;
  }
  return null;
}

type PackRow = { id: number; title: string; body: string; vec: Uint8Array; rank: number };''')
# ---------------- wikiPack.ts: cap/pick regroup, format-2 pool, SEMANTIC_KEEP floor, bytes
W = "src/rag/wikiPack.ts"
sub(W, 'import { cosineSimilarityInt8, MIN_SEMANTIC_SIMILARITY } from "./pure";', 'import { cosineSimilarityInt8, MIN_SEMANTIC_SIMILARITY, rbBytes } from "./pure";')
sub(W, "      keyword = await this.bm25Candidates(stems);\n      const sem = queryVec ? await this.leadSimilarity(keyword.map((c) => c.articleId), queryVec) : null;\n",
    f"""      // RETBENCH (bench-only, default off = unchanged): RS_RB_CAP (per-article cap, 2 = stock) / RS_RB_PICK=vec (within-article pick by chunk vector)
      // re-group the uncapped keyword pool (ARTCAP's mechanism); RS_RB_POOL scales the format-2 bm25 pool by RS_RB_POOL / 400 (the format-1 default).
      const rbEnv = {ENV};
      const rbCap = Number(rbEnv?.RS_RB_CAP ?? 2) || 2;
      const rbPick = rbEnv?.RS_RB_PICK === "vec";
      const rbGroup = rbCap !== 2 || rbPick;
      const rbPool = Number(rbEnv?.RS_RB_POOL) > 0 ? Math.round((this.tuning.pool * Number(rbEnv?.RS_RB_POOL)) / 400) : this.tuning.pool;
      keyword = await this.bm25Candidates(stems, rbPool, this.tuning.prior, rbGroup ? Number.MAX_SAFE_INTEGER : 2);
      const sem = queryVec ? await this.leadSimilarity(keyword.map((c) => c.articleId), queryVec) : null;
""")
sub(W, "        keyword = [...keyword].sort((a, b) => blended(b) - blended(a));\n      }\n      // Text is read only for candidates in rank order, until the result is full.\n",
    "        keyword = [...keyword].sort((a, b) => blended(b) - blended(a));\n      }\n"
    "      if (rbGroup) keyword = await this.rsArtcapGroup(keyword, rbPick ? queryVec : undefined, rbCap);\n"
    "      // Text is read only for candidates in rank order, until the result is full.\n")
sub(W, "(sem?.get(c.articleId) ?? 0) >= SEMANTIC_KEEP;",
    f"(sem?.get(c.articleId) ?? 0) >= (Number({ENV}?.RS_RB_FLOOR) > 0 ? Number({ENV}?.RS_RB_FLOOR) : SEMANTIC_KEEP); // RETBENCH RS_RB_FLOOR")
sub(W, "  /** RS_MERGE_CHECK only: sum over `terms` of the one-term bm25", '''  /**
   * RETBENCH cap/pick (bench-only; = ARTCAP's rsArtcapGroup): `pool` is the uncapped keyword list in rank order. Each of the first `maxArticles`
   * distinct articles keeps its first chunk at its own rank, followed immediately by up to `cap - 1` other chunks of the same article chosen by
   * the within-article pick (queryVec given and the pack has chunk_vecs: cosine of every other chunk of the article; else the article's other
   * pool rows in rank order); later rows of that article are dropped. Articles past `maxArticles` keep the base cap of 2.
   */
  async rsArtcapGroup(pool: Candidate[], queryVec: Float32Array | undefined, cap: number, maxArticles = 12): Promise<Candidate[]> {
    const out: Candidate[] = [];
    const done = new Map<number, boolean>();
    const per = new Map<number, number>();
    let grouped = 0;
    for (const c of pool) {
      const g = done.get(c.articleId);
      if (g === true) continue;
      if (g === false) {
        const n = per.get(c.articleId) ?? 0;
        if (n < 2) (out.push(c), per.set(c.articleId, n + 1));
        continue;
      }
      if (grouped >= maxArticles) {
        done.set(c.articleId, false);
        out.push(c);
        per.set(c.articleId, 1);
        continue;
      }
      grouped++;
      done.set(c.articleId, true);
      out.push(c);
      let extra: Candidate[];
      if (this.hasChunkVecs && queryVec) {
        const rows = await this.db.getAllAsync<{ id: number; start: number; end: number; vec: Uint8Array }>(
          `SELECT c.id, c.start, c.end, v.vec FROM chunks c JOIN chunk_vecs v ON v.chunk_id = c.id WHERE c.article_id = ? AND c.id != ?`,
          [c.articleId, c.chunkId]
        );
        rbBytes("pick-vec", rows.reduce((n, r) => n + r.vec.length, 0));
        extra = rows
          .map((r) => ({ r, s: cosineSimilarityInt8(queryVec, new Uint8Array(r.vec)) }))
          .sort((a, b) => b.s - a.s || a.r.id - b.r.id)
          .slice(0, cap - 1)
          .map(({ r }) => ({ chunkId: r.id, articleId: c.articleId, start: r.start, end: r.end, score: c.score }));
      } else {
        extra = pool.filter((x) => x.articleId === c.articleId && x.chunkId !== c.chunkId).slice(0, cap - 1).map((x) => ({ ...x, score: c.score }));
      }
      out.push(...extra);
    }
    return out;
  }

  /** RETBENCH RS_RB_LEAD: the lead chunk of the article holding `chunkId` (lowest start), its title and first sentence (<= 240 chars). */
  async rsLeadHeaderOf(chunkId: number): Promise<PackHit | null> {
    const row = await this.db.getFirstAsync<{ article_id: number }>("SELECT article_id FROM chunks WHERE id = ?", [chunkId]);
    if (!row) return null;
    const lead = await this.db.getFirstAsync<{ id: number; start: number; end: number }>("SELECT id, start, end FROM chunks WHERE article_id = ? ORDER BY start LIMIT 1", [row.article_id]);
    if (!lead) return null;
    const h = await this.hit(row.article_id, lead.id, lead.start, lead.end, 0, "bm25", true);
    const t = h.text.replace(/\\s+/g, " ").trim();
    const m = /^.{20,}?[.!?](?=\\s|$)/.exec(t);
    let first = (m ? m[0] : t).slice(0, 240);
    if (first.length === 240 && t.length > 240) first = first.replace(/\\s+\\S*$/, "") + "…";
    return { ...h, section: "", text: first };
  }

  /** RS_MERGE_CHECK only: sum over `terms` of the one-term bm25''')
# bytes: dense stage 1 + 2, seLead scan, leadSimilarity
sub(W, "    const scored = rows\n      .map((r) => ({ r, s: cosineSimilarityInt8(queryVec, new Uint8Array(r.vec)) }))\n      .filter((x) => x.s >= floor)",
    "    rbBytes(\"dense1\", ids.length * dims);\n    rbBytes(\"dense2\", rows.reduce((n, r) => n + r.vec.length, 0));\n"
    "    const scored = rows\n      .map((r) => ({ r, s: cosineSimilarityInt8(queryVec, new Uint8Array(r.vec)) }))\n      .filter((x) => x.s >= floor)")
sub(W, "      if (s < tau) continue;\n", "      if (s < tau) continue;\n")
sub(W, "    const out: PackHit[] = [];\n    for (const t of top) {\n      const rows = await this.db.getAllAsync<{ id: number; start: number; end: number }>(\"SELECT id, start, end FROM chunks WHERE article_id = ? ORDER BY start\", [t.id]);",
    "    rbBytes(\"selead\", ids.length * dims);\n    const out: PackHit[] = [];\n    for (const t of top) {\n      const rows = await this.db.getAllAsync<{ id: number; start: number; end: number }>(\"SELECT id, start, end FROM chunks WHERE article_id = ? ORDER BY start\", [t.id]);")
sub(W, "    for (const r of rows) out.set(r.article_id, new Uint8Array(r.vec));\n    return out;\n  }\n}",
    "    for (const r of rows) out.set(r.article_id, new Uint8Array(r.vec));\n    rbBytes(\"lead-sim\", rows.reduce((n, r) => n + r.vec.length, 0));\n    return out;\n  }\n}")
print("ok")
