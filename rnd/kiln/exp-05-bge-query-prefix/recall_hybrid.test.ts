/**
 * exp-05 (2): recall@6 of the pack's HYBRID search (keywords + the lead-embedding gate SEMANTIC_KEEP, optional
 * lead rerank) with the question vector raw (today) vs BGE-prefixed, on the code of boar-app origin/main 7aa67d5.
 *
 * Runs inside a local copy of origin/main (scratch tree; boar-app is not touched) whose wikiPack.ts reads
 * SEMANTIC_KEEP from KILN_SEMANTIC_KEEP (harness-only change; default 0.7 as in main). Same pattern as boar-app
 * eval/retrieval/recall.test.ts (odd/even gold-id split for dev/test).
 *
 *   KILN_SEMANTIC_KEEP=0.7 KILN_PACK=… KILN_QSET=retrieval-v1|vitalik KILN_OUT=… npx vitest run recall_hybrid.test.ts
 */
import { describe, it } from "vitest";
import { appendFileSync, readFileSync } from "node:fs";
import { decompress } from "fzstd";
import { nodeSqliteDatabase } from "../src/rag/testing/nodeSqlite";
import { DEFAULT_TUNING, SEMANTIC_KEEP, WikiPack } from "../src/rag/wikiPack";

const PACK = process.env.KILN_PACK!;
const QSET = process.env.KILN_QSET ?? "retrieval-v1";
const DIR = process.env.KILN_DIR!;
const OUT = process.env.KILN_OUT!;

type Q = { id: string; query: string; gold: string[] };

function loadQuestions(): Q[] {
  const raw = readFileSync(`${DIR}/questions.${QSET === "vitalik" ? "vitalik58" : "retrieval-v1"}.jsonl`, "utf8").split("\n").filter(Boolean).map((l) => JSON.parse(l));
  if (QSET !== "vitalik") return raw.map((q) => ({ id: q.id, query: q.query, gold: q.gold.filter((g: any) => g.source === "enwiki").map((g: any) => g.title) }));
  return raw
    .filter((q) => !q.duplicate_of)
    .map((q) => {
      const gold: string[] = [];
      for (const u of q.reference_sources ?? []) {
        if (/wikipedia\.org\/wiki\//.test(u)) gold.push(decodeURIComponent(u.split("/wiki/")[1]).replace(/_/g, " "));
        const m = /eips\.ethereum\.org\/EIPS\/eip-(\d+)/.exec(u);
        if (m) gold.push(`EIP-${m[1]}`);
      }
      return { id: q.id, query: q.question, gold };
    });
}

describe("exp-05 hybrid recall", () => {
  it("measures recall@k raw vs prefixed", async () => {
    const db = nodeSqliteDatabase(PACK);
    const pack = await WikiPack.open(db as any, decompress);
    const qvecs = JSON.parse(readFileSync(`${DIR}/qvecs.${QSET === "vitalik" ? "vitalik58" : "retrieval-v1"}.json`, "utf8"));
    const qs = loadQuestions();
    // gold -> article ids present in THIS pack (title, case-insensitive, or a redirect; EIP-n matches "EIP-n: …")
    const goldIds = new Map<string, Set<number>>();
    for (const q of qs) {
      const ids = new Set<number>();
      for (const t of q.gold) {
        const sql = db as any; // expo-sqlite-shaped wrapper (getAllAsync)
        (await sql.getAllAsync("SELECT id FROM articles WHERE title = ? COLLATE NOCASE", [t]) as { id: number }[]).forEach((r) => ids.add(r.id));
        (await sql.getAllAsync("SELECT article_id FROM redirects WHERE title = ?", [t]) as { article_id: number }[]).forEach((r) => ids.add(r.article_id));
        if (/^EIP-\d+$/.test(t)) (await sql.getAllAsync("SELECT id FROM articles WHERE title LIKE ?", [`${t}:%`]) as { id: number }[]).forEach((r) => ids.add(r.id));
      }
      if (ids.size) goldIds.set(q.id, ids);
    }
    const inPack = qs.filter((q) => goldIds.has(q.id));
    for (const variant of ["raw", "prefixed"] as const) {
      for (const w of [0, 0.5]) {
        pack.tuning = { ...DEFAULT_TUNING, semanticWeight: w };
        const ranks: number[] = [];
        for (const q of inPack) {
          const hits = await pack.search(q.query, { k: 10, queryVec: Float32Array.from(qvecs[variant][q.id]) });
          const arts: number[] = [];
          for (const h of hits) if (!arts.includes(h.articleId)) arts.push(h.articleId);
          const g = goldIds.get(q.id)!;
          const r = arts.findIndex((a) => g.has(a));
          ranks.push(r < 0 ? Infinity : r + 1);
        }
        const at = (k: number) => ranks.filter((r) => r <= k).length / ranks.length;
        const mrr = ranks.reduce((s, r) => s + (Number.isFinite(r) ? 1 / r : 0), 0) / ranks.length;
        const row = { qset: QSET, pack: PACK.split("/").pop(), variant, semanticKeep: SEMANTIC_KEEP, semanticWeight: w,
                      n: ranks.length, recall_at_1: +at(1).toFixed(4), recall_at_3: +at(3).toFixed(4), recall_at_6: +at(6).toFixed(4),
                      mrr: +mrr.toFixed(4), ranks: Object.fromEntries(inPack.map((q, i) => [q.id, Number.isFinite(ranks[i]) ? ranks[i] : null])) };
        appendFileSync(OUT, JSON.stringify(row) + "\n");
      }
    }
  }, 600_000);
});
