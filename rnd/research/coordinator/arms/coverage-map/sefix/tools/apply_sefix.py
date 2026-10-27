"""Applies the SEFIX F1-F4 edits (default off = byte-identical) to a clone of rs-H4. python3 -I apply_sefix.py <tree>"""
import sys, re
T = sys.argv[1] + "/src/"
def rep(f, old, new, count=1):
    p = T + f; s = open(p).read()
    assert s.count(old) == count, (f, s.count(old), old[:70])
    open(p, "w").write(s.replace(old, new))

# ---------------- wikiPack.ts: F1 (lead hits), F2 (terms)
rep("rag/wikiPack.ts", """  private rsRows = new Map<string, number>();
""", """  private rsRows = new Map<string, number>();
  /** SEFIX F2 variant (RS_SE_GLOBALDF=1, bench-only): df over all installed format-2 packs for the question's stems, set by searchWikiPacks around a search. */
  rsSeStats: { nRow: number; df: Map<string, number> } | null = null;
  private rsSeCache: boolean | null = null;
""")
rep("rag/wikiPack.ts", """  /** RS_MERGE=gidf: rows of this pack's index (FTS5's nRow). */""", """  /** SEFIX (bench-only): a Stack Exchange Q&A pack (meta.sources names stackexchange). */
  get rsIsSE(): boolean {
    if (this.rsSeCache === null) {
      try { this.rsSeCache = "stackexchange" in JSON.parse(this.meta.sources ?? "{}"); } catch { this.rsSeCache = false; }
    }
    return this.rsSeCache;
  }

  /**
   * SEFIX F2 (RS_SE_MAXDF=<x>, optional RS_SE_GLOBALDF=1; bench-only, default off = queryTerms(stems)): for Stack Exchange packs the
   * df cut is x (default 0.02) instead of 0.02, so a domain word (credit, rice, tax) stays in the OR query; with RS_SE_GLOBALDF=1 the df
   * is counted over all installed packs (rsSeStats) instead of this pack's chunks.
   */
  rsTerms(stems: Stem[]): string[] {
    const env = (globalThis as any).process?.env;
    if (!env || !this.rsIsSE || (env.RS_SE_MAXDF === undefined && env.RS_SE_GLOBALDF !== "1")) return this.queryTerms(stems);
    const maxDf = Number(env.RS_SE_MAXDF ?? 0.02);
    const st = env.RS_SE_GLOBALDF === "1" ? this.rsSeStats : null;
    if (!st) return this.queryTerms(stems, maxDf);
    return this.queryTerms(
      stems.map((s) => (st.df.has(s.stem) ? { stem: s.stem, idf: Math.log(st.nRow / Math.max(1, st.df.get(s.stem)!)) } : s)),
      maxDf
    );
  }

  /**
   * SEFIX F1 (RS_SE_LEAD=<tau>, default 0.78; RS_SE_LEAD_N threads, default 1; bench-only): for a Stack Exchange pack without chunk_vecs, the
   * top thread(s) by lead-vector cosine >= tau, as the chunks at positions 1-2 (accepted answer + next, by start) of each thread's article.
   * The caller appends them after the kept list (answer.ts, headpass:selead:add). The lead matrix is the one denseChunks caches.
   */
  async rsSeLead(queryVec: Float32Array): Promise<PackHit[]> {
    const env = (globalThis as any).process?.env;
    const v = Number(env?.RS_SE_LEAD ?? 0);
    if (!v || !this.rsIsSE || this.hasChunkVecs) return [];
    const tau = v > 0 && v < 1 ? v : 0.78;
    const nThreads = Math.max(1, Number(env?.RS_SE_LEAD_N ?? 1));
    const dims = queryVec.length;
    if (!this.leadMatrix) {
      const rows = await this.db.getAllAsync<{ article_id: number; vec: Uint8Array }>("SELECT article_id, vec FROM lead_vecs ORDER BY article_id", []).catch(() => []);
      const ids = new Int32Array(rows.length);
      const vecs = new Int8Array(rows.length * dims);
      const norms = new Float32Array(rows.length);
      rows.forEach((r, i) => {
        ids[i] = r.article_id;
        const vv = new Int8Array(r.vec.buffer, r.vec.byteOffset, dims);
        vecs.set(vv, i * dims);
        let n = 0;
        for (let d = 0; d < dims; d++) n += vv[d] * vv[d];
        norms[i] = Math.sqrt(n);
      });
      this.leadMatrix = { ids, vecs, norms };
    }
    const { ids, vecs, norms } = this.leadMatrix;
    let qn = 0;
    for (let d = 0; d < dims; d++) qn += queryVec[d] * queryVec[d];
    qn = Math.sqrt(qn) || 1;
    const top: Array<{ id: number; s: number }> = [];
    for (let i = 0; i < ids.length; i++) {
      let dot = 0;
      const o = i * dims;
      for (let d = 0; d < dims; d++) dot += queryVec[d] * vecs[o + d];
      const s = norms[i] ? dot / (qn * norms[i]) : 0;
      if (s < tau) continue;
      if (top.length < nThreads || s > top[top.length - 1].s) {
        let j = top.length < nThreads ? top.length : top.length - 1;
        if (top.length < nThreads) top.push({ id: ids[i], s });
        while (j > 0 && top[j - 1].s < s) (top[j] = top[j - 1]), j--;
        top[j] = { id: ids[i], s };
      }
    }
    const out: PackHit[] = [];
    for (const t of top) {
      const rows = await this.db.getAllAsync<{ id: number; start: number; end: number }>("SELECT id, start, end FROM chunks WHERE article_id = ? ORDER BY start", [t.id]);
      for (const r of rows.slice(1, 3)) out.push({ ...(await this.hit(t.id, r.id, r.start, r.end, t.s, "semantic")), score: t.s });
    }
    return out;
  }

  /** RS_MERGE=gidf: rows of this pack's index (FTS5's nRow). */""")
rep("rag/wikiPack.ts", """  async bm25Candidates(stems: Stem[], pool = this.tuning.pool, prior = this.tuning.prior, perArticle = 2): Promise<Candidate[]> {
    const terms = this.queryTerms(stems);""", """  async bm25Candidates(stems: Stem[], pool = this.tuning.pool, prior = this.tuning.prior, perArticle = 2): Promise<Candidate[]> {
    const terms = this.rsTerms(stems);""")
rep("rag/wikiPack.ts", """  async searchDetailed(query: string, opts: PackSearchOptions = {}): Promise<{ hits: PackHit[]; stems: Stem[]; semantic?: PackHit[] }> {""",
"""  async searchDetailed(query: string, opts: PackSearchOptions = {}): Promise<{ hits: PackHit[]; stems: Stem[]; semantic?: PackHit[]; seLead?: PackHit[] }> {""")
rep("rag/wikiPack.ts", """    if (opts.dense2 && queryVec && this.hasChunkVecs) return { hits: hits.slice(0, limit + lay), stems, semantic: await this.denseChunks(queryVec) };
    return { hits: hits.slice(0, limit + lay), stems };""", """    if (opts.dense2 && queryVec && this.hasChunkVecs) return { hits: hits.slice(0, limit + lay), stems, semantic: await this.denseChunks(queryVec) };
    // SEFIX F1 (RS_SE_LEAD, bench-only, default off): a Stack Exchange pack without chunk_vecs offers its best lead-vector thread's answers.
    if (opts.dense2 && queryVec && (globalThis as any).process?.env?.RS_SE_LEAD) {
      const seLead = await this.rsSeLead(queryVec);
      if (seLead.length) return { hits: hits.slice(0, limit + lay), stems, seLead };
    }
    return { hits: hits.slice(0, limit + lay), stems };""")

# ---------------- packs.ts
rep("rag/packs.ts", """  semantic?: PackHit[];
}""", """  semantic?: PackHit[];
  /** SEFIX F1 (RS_SE_LEAD): lead-vector thread answers of a Stack Exchange pack without chunk_vecs. */
  seLead?: PackHit[];
}""")
rep("rag/packs.ts", """  const gidf = (globalThis as any).process?.env?.RS_MERGE === "gidf";
  const ready: WikiPack[] = [];
  if (gidf) {""", """  const gidf = (globalThis as any).process?.env?.RS_MERGE === "gidf";
  // SEFIX F2 variant (RS_SE_GLOBALDF=1): the Stack Exchange packs' term cut uses the df over all installed packs.
  const seGlobal = (globalThis as any).process?.env?.RS_SE_GLOBALDF === "1";
  const ready: WikiPack[] = [];
  if (gidf || seGlobal) {""")
rep("rag/packs.ts", """    const terms = new Set<string>();
    for (const wp of ready) for (const t of wp.queryTerms(await wp.stems(query))) terms.add(t);
    const df = new Map<string, number>();
    let nRow = 0;
    for (const wp of ready) {
      nRow += wp.rsNRow;
      for (const t of terms) df.set(t, (df.get(t) ?? 0) + (await wp.rsTermRows(t)));
    }
    for (const wp of ready) wp.rsGlobal = { nRow, df };
  }""", """    if (seGlobal) {
      const all = new Set<string>();
      for (const wp of ready) for (const s of await wp.stems(query)) all.add(s.stem);
      const sdf = new Map<string, number>();
      let sRow = 0;
      for (const wp of ready) {
        sRow += wp.rsNRow;
        for (const t of all) sdf.set(t, (sdf.get(t) ?? 0) + (await wp.rsTermRows(t)));
      }
      for (const wp of ready) wp.rsSeStats = { nRow: sRow, df: sdf };
    }
    if (gidf) {
      const terms = new Set<string>();
      for (const wp of ready) for (const t of wp.rsTerms(await wp.stems(query))) terms.add(t);
      const df = new Map<string, number>();
      let nRow = 0;
      for (const wp of ready) {
        nRow += wp.rsNRow;
        for (const t of terms) df.set(t, (df.get(t) ?? 0) + (await wp.rsTermRows(t)));
      }
      for (const wp of ready) wp.rsGlobal = { nRow, df };
    }
  }""")
rep("rag/packs.ts", """        const { hits, stems, semantic } = await wp.searchDetailed(query, opts);
        out.push({ packId: pack.id, pack: wp, hits, stems, ...(semantic ? { semantic } : {}) });""", """        const { hits, stems, semantic, seLead } = await wp.searchDetailed(query, opts);
        out.push({ packId: pack.id, pack: wp, hits, stems, ...(semantic ? { semantic } : {}), ...(seLead ? { seLead } : {}) });""")
rep("rag/packs.ts", """    for (const wp of ready) wp.rsGlobal = null;
  }""", """    for (const wp of ready) { wp.rsGlobal = null; wp.rsSeStats = null; }
  }""")

# ---------------- denseCandidates.ts
rep("rag/denseCandidates.ts", """  sidecar: boolean;
}""", """  sidecar: boolean;
  /** SEFIX F1 (RS_SE_LEAD, bench-only): lead-vector thread answers of Stack Exchange packs without chunk_vecs, best thread first. */
  seLead?: RetrievedChunk[];
}""")

# ---------------- retrieve.ts
rep("rag/retrieve.ts", """  const side = (list: RetrievedChunk[], dense: RetrievedChunk[], sidecar: boolean) =>
    extra ? appendDenseExtra(list, dense) : append ? attachDenseCandidates(list, { candidates: rankDenseCandidates(list, dense), sidecar }) : list;""",
"""  const side = (list: RetrievedChunk[], dense: RetrievedChunk[], sidecar: boolean, seLead: RetrievedChunk[] = []) =>
    extra
      ? appendDenseExtra(list, dense)
      : append
        ? attachDenseCandidates(list, { candidates: rankDenseCandidates(list, dense), sidecar, ...(seLead.length ? { seLead } : {}) })
        : list;""")
rep("rag/retrieve.ts", """  if (!looksPortuguese(query)) return side(main, mainR.dense, mainR.sidecar);""", """  if (!looksPortuguese(query)) return side(main, mainR.dense, mainR.sidecar, mainR.seLead);""")
rep("rag/retrieve.ts", """  if (!names.length) return side(main, mainR.dense, mainR.sidecar);""", """  if (!names.length) return side(main, mainR.dense, mainR.sidecar, mainR.seLead);""")
rep("rag/retrieve.ts", """  return side(out, [...mainR.dense, ...foundR.dense], mainR.sidecar || foundR.sidecar);""", """  return side(out, [...mainR.dense, ...foundR.dense], mainR.sidecar || foundR.sidecar, [...mainR.seLead, ...foundR.seLead]);""")
rep("rag/retrieve.ts", """): Promise<{ chunks: RetrievedChunk[]; dense: RetrievedChunk[]; sidecar: boolean }> {""", """): Promise<{ chunks: RetrievedChunk[]; dense: RetrievedChunk[]; sidecar: boolean; seLead: RetrievedChunk[] }> {""")
rep("rag/retrieve.ts", """  return { chunks: result, dense: extra ? wikiSemantic : [], sidecar: wiki.some((w) => w.pack?.hasChunkVecs === true) };""", """  // SEFIX F1 (RS_SE_LEAD): the Stack Exchange lead-vector thread answers, as semantic candidates at their lead cosine.
  const seLead = wiki.flatMap((w) => (w.seLead ?? []).map((h) => ({ ...packHitToChunk(w.packId, h), matchType: "semantic" as const, similarity: h.score })));
  return { chunks: result, dense: extra ? wikiSemantic : [], sidecar: wiki.some((w) => w.pack?.hasChunkVecs === true), seLead };""")

# ---------------- context.ts: F4 relaxed proper-noun clause
rep("routing/context.ts", """export function onTopic(query: string, chunk: RetrievedChunk): boolean {""", """/** SEFIX F4 (literal variant): the question has proper nouns and none of these sources holds one. */
export function noKeptHoldsProper(query: string, kept: RetrievedChunk[]): boolean {
  const proper = properNounTerms(query);
  if (!proper.length) return false;
  return !kept.some((c) => {
    const words = new Set(tokenizeTerms(`${c.title} ${c.body}`));
    return proper.some((p) => words.has(p));
  });
}

/** `relaxProper` (SEFIX F4, bench-only): the proper-noun requirement becomes "any content term of the question is in the source". */
export function onTopic(query: string, chunk: RetrievedChunk, relaxProper = false): boolean {""")
rep("routing/context.ts", """    const words = new Set(tokenizeTerms(text));
    if (!proper.some((p) => words.has(p))) return false;
  }
  // The article the question names""", """    const words = new Set(tokenizeTerms(text));
    if (relaxProper) {
      if (!tokenizeTerms(query).some((t) => !proper.includes(t) && words.has(t))) return false;
    } else if (!proper.some((p) => words.has(p))) return false;
  }
  // The article the question names""")

# ---------------- answer.ts: F3, F4, F1 append
A = "routing/answer.ts"
rep(A, "  onHealthTopic,\n", "  onHealthTopic,\n  noKeptHoldsProper,\n")
rep(A, """      if (guarded && !health && sources.length) {
        const kept = sources.filter((c) => onSubject(c));""", """      if (guarded && !health && sources.length) {
        let kept = sources.filter((c) => onSubject(c));
        // SEFIX F4 (RS_KEEP_NOPROPER=1 per source / =lit only when no kept source holds a proper noun; bench-only, default off): a source the
        // proper-noun rule alone dropped comes back when it holds any content term of the question and passes the rest of onTopic.
        const noProper = (globalThis as any).process?.env?.RS_KEEP_NOPROPER;
        if (noProper && kept.length < sources.length && (noProper !== "lit" || noKeptHoldsProper(matchQuery, kept))) {
          const relaxed = (c: RetrievedChunk) => (cryptoBlocked(c) ? false : history ? history.isDateArticle(c.title) : names.length ? namedByLexicon(names, c) || onTopic(req.query, c, true) : onTopic(matchQuery, c, true));
          const back = sources.filter((c) => !kept.includes(c) && relaxed(c));
          if (back.length) {
            kept = sources.filter((c) => kept.includes(c) || back.includes(c));
            reasonCodes.push(`grounding:keep-noproper-restored-${back.length}`);
          }
        }""")
rep(A, """      if (health) {
        reasonCodes.push("grounding:health-strict");
        // Health: only sources whose title names the health topic (never a plant, a cave or a TV show).
        const topic = healthTopicTerms(req.query, english);
        const onTopicHealth = sources.filter((c) => onHealthTopic(topic, c));""", """      // SEFIX F3 (RS_HEALTH_NOSOURCE_FALLBACK=1 / =2 appends also filtered by onSubject; bench-only, default off): 0 = not used.
      let healthFallback = 0;
      if (health) {
        reasonCodes.push("grounding:health-strict");
        // Health: only sources whose title names the health topic (never a plant, a cave or a TV show).
        const topic = healthTopicTerms(req.query, english);
        const compressedSources = sources;
        const onTopicHealth = sources.filter((c) => onHealthTopic(topic, c));""")
rep(A, """            sources = [...sources, best];
            reasonCodes.push("grounding:health-best-restored");
          }
        }
      }""", """            sources = [...sources, best];
            reasonCodes.push("grounding:health-best-restored");
          }
        }
        // SEFIX F3: health-strict left nothing and no first-aid card applies: ground the compressed sources like a normal question.
        const fb = (globalThis as any).process?.env?.RS_HEALTH_NOSOURCE_FALLBACK;
        if (fb && !sources.length && compressedSources.length && !healthFollowUp && !cardEmergency && !isCardEmergency(req.query) && !conversationCondition(req.query, userTurns).condition) {
          const back = compressedSources.filter((c) => onSubject(c));
          if (back.length) {
            sources = back;
            healthFallback = fb === "2" ? 2 : 1;
            reasonCodes.push("grounding:health-fallback-subject");
          }
        }
      }""")
rep(A, """            if (health) {
              const topic = healthTopicTerms(req.query, english);
              const ok = add.filter((c) => onHealthTopic(topic, c));
              if (ok.length < add.length) reasonCodes.push(`headpass:health-dropped-${add.length - ok.length}`);
              add = ok;
            }""", """            if (health && !healthFallback) {
              const topic = healthTopicTerms(req.query, english);
              const ok = add.filter((c) => onHealthTopic(topic, c));
              if (ok.length < add.length) reasonCodes.push(`headpass:health-dropped-${add.length - ok.length}`);
              add = ok;
            } else if (healthFallback === 2) add = add.filter((c) => onSubject(c));""")
rep(A, """        if (denseAppend) {
          const dense = denseCandidatesOf(retrievedRaw);
          if (!dense?.sidecar) reasonCodes.push("headpass:dense:nosidecar");
          else {
            let add = pickDenseAppend(dense.candidates, [...sources, ...pendX1], sources.length - hpBefore + pendX1.length, HEADPASS_DENSE_D, HEADPASS_MAX_APPEND);
            if (!dense.candidates.length) reasonCodes.push("headpass:dense:none");
            if (health && add.length) {
              const topic = healthTopicTerms(req.query, english);
              const ok = add.filter((c) => onHealthTopic(topic, c));
              if (ok.length < add.length) reasonCodes.push(`headpass:dense:health-dropped-${add.length - ok.length}`);
              add = ok;
            }""", """        if (denseAppend) {
          const dense = denseCandidatesOf(retrievedRaw);
          // SEFIX F1 (RS_SE_LEAD): the Stack Exchange thread's answers go first among the dense appends, inside the same cap and budget.
          if (dense?.seLead?.length) {
            const have = new Set([...sources, ...pendX1, ...retrievedRaw].map((c) => c.chunkId));
            let se = dense.seLead.filter((c) => !have.has(c.chunkId)).slice(0, Math.max(0, HEADPASS_MAX_APPEND - (sources.length - hpBefore + pendX1.length)));
            if (health && !healthFallback) {
              const topic = healthTopicTerms(req.query, english);
              const ok = se.filter((c) => onHealthTopic(topic, c));
              if (ok.length < se.length) reasonCodes.push(`headpass:selead:health-dropped-${se.length - ok.length}`);
              se = ok;
            } else if (healthFallback === 2) se = se.filter((c) => onSubject(c));
            pendSe = se;
          }
          if (!dense?.sidecar) reasonCodes.push("headpass:dense:nosidecar");
          else {
            let add = pickDenseAppend(dense.candidates, [...sources, ...pendX1, ...pendSe], sources.length - hpBefore + pendX1.length + pendSe.length, HEADPASS_DENSE_D, HEADPASS_MAX_APPEND);
            if (!dense.candidates.length) reasonCodes.push("headpass:dense:none");
            if (health && !healthFallback && add.length) {
              const topic = healthTopicTerms(req.query, english);
              const ok = add.filter((c) => onHealthTopic(topic, c));
              if (ok.length < add.length) reasonCodes.push(`headpass:dense:health-dropped-${add.length - ok.length}`);
              add = ok;
            } else if (healthFallback === 2) add = add.filter((c) => onSubject(c));""")
rep(A, """      let pendDense: RetrievedChunk[] = [];
      if ((settings.packHeadPass""", """      let pendDense: RetrievedChunk[] = [];
      let pendSe: RetrievedChunk[] = [];
      if ((settings.packHeadPass""")
rep(A, """        if (budgeted && (pendX1.length || pendDense.length)) {""", """        if (!budgeted && pendSe.length) {
          for (const c of pendSe) reasonCodes.push(`headpass:selead:add:${c.chunkId}`);
          sources = [...sources, ...pendSe];
        }
        if (budgeted && (pendX1.length || pendSe.length || pendDense.length)) {""")
rep(A, """          const { kept, dropped } = applyAppendBudget([...pendX1, ...pendDense], chars, 4 * HEADPASS_BUDGET_TOKENS);
          for (const c of kept) reasonCodes.push(x1Ids.has(c.chunkId) ? `headpass:add:${c.chunkId}` : `headpass:dense:add:${c.chunkId}`);""", """          const seIds = new Set(pendSe.map((c) => c.chunkId));
          const { kept, dropped } = applyAppendBudget([...pendX1, ...pendSe, ...pendDense], chars, 4 * HEADPASS_BUDGET_TOKENS);
          for (const c of kept) reasonCodes.push(x1Ids.has(c.chunkId) ? `headpass:add:${c.chunkId}` : seIds.has(c.chunkId) ? `headpass:selead:add:${c.chunkId}` : `headpass:dense:add:${c.chunkId}`);""")
rep(A, """const healthExtractive = health && sources.length > 0 && req.tier !== "deep";""", """const healthExtractive = health && !healthFallback && sources.length > 0 && req.tier !== "deep";""")
print("ok")
