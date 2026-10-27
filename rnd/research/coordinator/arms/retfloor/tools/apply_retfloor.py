#!/usr/bin/env python3
"""RETFLOOR: patch a COPY of kiln-local/be-0cfd4a77-cut7-litepacks (never the original). Usage: python3 -I apply_retfloor.py <tree copy>
Env-gated (RETFLOOR_VARIANT; absent = base = byte-identical behaviour, plus retfloor:* reason codes for logging).
Variants act on the X2b pending appends (X1 neighbours + dense picks) before the 600-work budget:
  V1    onSubject (the grounding check) on X1 and dense appends (health questions keep the existing onHealthTopic rule)
  V2    dense appends need cosine >= 0.70 (= DENSE2_FLOOR 0.70; candidates are cosine-sorted, so filter-after-pick is identical)
  V2b   cosine >= 0.70 on X1 and dense appends
  V3    top-1-minus-margin: keep appends with cosine >= (best cosine among the item's pending X1 U dense) - 0.05
  V4    cosine-ordered budget fill over X1 U dense (same chunks, order by cosine desc instead of X1 first)
  V1orC onSubject OR cosine >= 0.70;  V1V4 = V1 then cosine order
X1 cosine = question vector (first embed of the item's retrieve) vs the pack's chunk_vecs row (int8), as the dense path scores."""
import sys, pathlib
T = pathlib.Path(sys.argv[1]); assert "retfloor" in T.name, "refusing to patch a tree whose name lacks 'retfloor'"
def rep(rel, old, new):
    p = T / rel; s = p.read_text(); assert s.count(old) == 1, (rel, old[:60], s.count(old)); p.write_text(s.replace(old, new))
rep("src/rag/retrieve.ts", "  const queryVec = opts.queryVec ?? (await embeddingEngine.embed(query));\n",
    "  const queryVec = opts.queryVec ?? (await embeddingEngine.embed(query));\n"
    "  if ((globalThis as any).__rfQvec === undefined) (globalThis as any).__rfQvec = queryVec; // RETFLOOR\n")
rep("src/rag/packs.ts", "/** HEADPASS-ST: kit packs (shipped with the app) never get a head pass; only user-installed format-2 packs do. */\n",
    "/** RETFLOOR: cosine of the question vector to a format-2 pack chunk's chunk_vecs row; null without a sidecar. */\n"
    "export async function packChunkCosine(chunkId: string, qv: Float32Array): Promise<number | null> {\n"
    "  const m = /^pack:([^:]+):(\\d+)$/.exec(chunkId);\n  if (!m) return null;\n  const wp = wikiPacks.get(m[1]);\n"
    "  return wp ? wp.chunkCosine(Number(m[2]), qv) : null;\n}\n\n"
    "/** HEADPASS-ST: kit packs (shipped with the app) never get a head pass; only user-installed format-2 packs do. */\n")
rep("src/rag/wikiPack.ts", "  async headChunksOf(chunkId: number, from: number, to: number): Promise<PackHit[]> {\n",
    "  /** RETFLOOR: cosine of `qv` to chunk `id`'s sidecar vector (null without chunk_vecs). */\n"
    "  async chunkCosine(id: number, qv: Float32Array): Promise<number | null> {\n"
    "    if (!this.hasChunkVecs) return null;\n"
    "    const r = await this.db.getFirstAsync<{ vec: Uint8Array }>(\"SELECT vec FROM chunk_vecs WHERE chunk_id = ?\", [id]);\n"
    "    return r ? cosineSimilarityInt8(qv, new Uint8Array(r.vec)) : null;\n  }\n\n"
    "  async headChunksOf(chunkId: number, from: number, to: number): Promise<PackHit[]> {\n")
A = "src/routing/answer.ts"
rep(A, "        raw = await (settings.packDense2 === true ||",
    "        (globalThis as any).__rfQvec = undefined; // RETFLOOR\n        raw = await (settings.packDense2 === true ||")
rep(A, "        if (budgeted && (pendX1.length || pendDense.length)) {\n          let template = true;",
    """        // RETFLOOR (replay-only; env RETFLOOR_VARIANT, absent = base): log every pending append, then gate/reorder.
        let rfOrder: RetrievedChunk[] | undefined;
        if (budgeted && (pendX1.length || pendDense.length)) {
          const RF: string = (globalThis as any).process?.env?.RETFLOOR_VARIANT ?? "base";
          const qv: Float32Array | undefined = (globalThis as any).__rfQvec;
          const { packChunkCosine } = await import("../rag/packs");
          const cos = new Map<string, number | null>();
          for (const c of pendX1) cos.set(c.chunkId, qv ? await packChunkCosine(c.chunkId, qv) : null);
          for (const c of pendDense) cos.set(c.chunkId, c.similarity ?? null);
          const subj = (c: RetrievedChunk) => (health || !guarded ? true : onSubject(c));
          const cv = (c: RetrievedChunk) => cos.get(c.chunkId) ?? -1;
          for (const c of pendX1) reasonCodes.push(`retfloor:cand:x1:${c.chunkId}:${cos.get(c.chunkId)?.toFixed(4) ?? "na"}:${subj(c) ? 1 : 0}`);
          for (const c of pendDense) reasonCodes.push(`retfloor:cand:dense:${c.chunkId}:${cos.get(c.chunkId)?.toFixed(4) ?? "na"}:${subj(c) ? 1 : 0}`);
          const n0 = pendX1.length + pendDense.length;
          if (RF === "V1") { pendX1 = pendX1.filter(subj); pendDense = pendDense.filter(subj); }
          else if (RF === "V2") pendDense = pendDense.filter((c) => cv(c) >= 0.7);
          else if (RF === "V2b") { pendX1 = pendX1.filter((c) => cv(c) >= 0.7); pendDense = pendDense.filter((c) => cv(c) >= 0.7); }
          else if (RF === "V3") {
            const top = Math.max(...[...pendX1, ...pendDense].map(cv));
            pendX1 = pendX1.filter((c) => cv(c) >= top - 0.05); pendDense = pendDense.filter((c) => cv(c) >= top - 0.05);
          } else if (RF === "V1orC") { const ok = (c: RetrievedChunk) => subj(c) || cv(c) >= 0.7; pendX1 = pendX1.filter(ok); pendDense = pendDense.filter(ok); }
          else if (RF === "V1V4") { pendX1 = pendX1.filter(subj); pendDense = pendDense.filter(subj); }
          if (RF === "V4" || RF === "V1V4") rfOrder = [...pendX1, ...pendDense].map((c, i) => ({ c, i })).sort((a, b) => cv(b.c) - cv(a.c) || a.i - b.i).map((x) => x.c);
          reasonCodes.push(`retfloor:variant:${RF}:removed-${n0 - pendX1.length - pendDense.length}`);
        }
        if (budgeted && (pendX1.length || pendDense.length)) {
          let template = true;""")
rep(A, "applyAppendBudget([...pendX1, ...pendDense], chars,", "applyAppendBudget(rfOrder ?? [...pendX1, ...pendDense], chars,")
rep(A, "      if (sources.length && gen?.mode !== \"multipass\") {\n        emit({ type: \"sources\", answerId,",
    "      reasonCodes.push(`retfloor:kept:${hpBefore}:${sources.map((c) => c.chunkId).join(\",\")}`); // RETFLOOR: grounded count + final ids\n"
    "      if (sources.length && gen?.mode !== \"multipass\") {\n        emit({ type: \"sources\", answerId,")
print("patched", T)
