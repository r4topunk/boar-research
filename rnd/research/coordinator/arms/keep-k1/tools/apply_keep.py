#!/usr/bin/env python3
"""KEEP-K1 (2026-10-21): replay-only patch on a COPY of the RAG-FUNNEL tree (litepacks + apply_retfloor.py + apply_funnel.py).
Env KEEP_VARIANT (absent/base = byte-identical behaviour) changes the X2b dense pick (pickDenseAppend) before the RETFLOOR gate and the budget:
  D3    up to 3 dense picks (cap on all appends 5)           D4  up to 4 dense picks (cap 6)
  D4B   D4 with the append budget 1200 tokens (base 600)
  Q2    quota per source: a dense candidate is skipped while its article title already has 2 chunks among kept + X1 + picked (D 2, cap 4)
  R05   rescue: after the D=2 picks, add up to 2 more candidates whose cosine >= the last pick's cosine - 0.05 (cap 6)
  R05B  R05 with the append budget 1200 tokens
  E     empty-raw dense fallback: the head-pass/dense append path also runs when the lexical retrieve() list is empty but dense
        candidates were attached (base skips it: 17/100 MAIN rows have raw = [] and 12 dense candidates); D 2, cap 4, budget 600
  ED4B  E + D4B
  D8X   ceiling probe, not a candidate: D 8, cap 10, budget 2400 tokens (E path on)
Combines with RETFLOOR_VARIANT (the gate runs after the pick). Logs keep:variant:<V>:picked-<n>.
Usage: python3 -I apply_keep.py <tree copy whose name contains 'keep'>"""
import sys, pathlib
T = pathlib.Path(sys.argv[1]); assert "keep" in T.name, "refusing to patch a tree whose name lacks 'keep'"
p = T / "src/routing/answer.ts"; s = p.read_text()
def rep(old, new):
    global s; assert s.count(old) == 1, (old[:70], s.count(old)); s = s.replace(old, new)
rep("            let add = pickDenseAppend(dense.candidates, [...sources, ...pendX1], sources.length - hpBefore + pendX1.length, HEADPASS_DENSE_D, HEADPASS_MAX_APPEND);\n",
"""            const KV: string = (globalThis as any).process?.env?.KEEP_VARIANT ?? "base"; // KEEP-K1
            const kD = KV === "D3" ? 3 : KV === "D4" || KV === "D4B" || KV === "ED4B" ? 4 : KV === "D8X" ? 8 : HEADPASS_DENSE_D;
            const kCap = KV === "D3" ? 5 : KV === "D4" || KV === "D4B" || KV === "ED4B" || KV === "R05" || KV === "R05B" ? 6 : KV === "D8X" ? 10 : HEADPASS_MAX_APPEND;
            const soFar = sources.length - hpBefore + pendX1.length;
            let add: RetrievedChunk[];
            if (KV === "Q2") {
              const have = new Set([...sources, ...pendX1].map((c) => c.chunkId));
              const per = new Map<string, number>();
              for (const c of [...sources, ...pendX1]) per.set(c.title ?? "", (per.get(c.title ?? "") ?? 0) + 1);
              const room = Math.max(0, Math.min(HEADPASS_DENSE_D, HEADPASS_MAX_APPEND - soFar));
              add = [];
              for (const c of dense.candidates) {
                if (add.length >= room) break;
                if (have.has(c.chunkId) || (per.get(c.title ?? "") ?? 0) >= 2) continue;
                add.push(c); per.set(c.title ?? "", (per.get(c.title ?? "") ?? 0) + 1);
              }
            } else add = pickDenseAppend(dense.candidates, [...sources, ...pendX1], soFar, kD, kCap);
            if ((KV === "R05" || KV === "R05B") && add.length) {
              const last = add[add.length - 1].similarity ?? -1;
              const have = new Set([...sources, ...pendX1, ...add].map((c) => c.chunkId));
              const room = Math.max(0, Math.min(2, kCap - soFar - add.length));
              add = [...add, ...dense.candidates.filter((c) => !have.has(c.chunkId) && (c.similarity ?? -1) >= last - 0.05).slice(0, room)];
            }
            reasonCodes.push(`keep:variant:${KV}:picked-${add.length}`);
""")
rep("      if ((settings.packHeadPass === \"a2\" || denseAppend) && gen?.mode !== \"multipass\" && retrievedRaw.length) {\n",
    "      const kvE = /^(E|ED4B|D8X)$/.test((globalThis as any).process?.env?.KEEP_VARIANT ?? \"\"); // KEEP-K1 empty-raw dense fallback\n"
    "      if ((settings.packHeadPass === \"a2\" || denseAppend) && gen?.mode !== \"multipass\" && (retrievedRaw.length || (kvE && !!denseCandidatesOf(retrievedRaw)?.candidates.length))) {\n")
rep("applyAppendBudget(rfOrder ?? [...pendX1, ...pendDense], chars, 4 * HEADPASS_BUDGET_TOKENS);",
    "applyAppendBudget(rfOrder ?? [...pendX1, ...pendDense], chars, 4 * ((globalThis as any).process?.env?.KEEP_VARIANT === \"D8X\" ? 2400 : /B$/.test((globalThis as any).process?.env?.KEEP_VARIANT ?? \"\") ? 1200 : HEADPASS_BUDGET_TOKENS));")
p.write_text(s); print("patched", T)
