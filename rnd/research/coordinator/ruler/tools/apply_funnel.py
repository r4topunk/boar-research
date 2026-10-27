#!/usr/bin/env python3
"""RAG-FUNNEL (2026-10-21): logging-only patch on a COPY of the RETFLOOR replay tree (kiln-local/be-0cfd4a77-cut7-litepacks + apply_retfloor.py).
Adds reason codes, no behaviour change: fun:raw:<chunk ids of the retrieve() list, before any filter>, fun:dense:<the two-stage dense candidates
attached beside it, best cosine first>, fun:compressed:<ids after compressContext, before grounding>. Usage: python3 -I apply_funnel.py <tree copy>"""
import sys, pathlib
T = pathlib.Path(sys.argv[1]); assert "funnel" in T.name, "refusing to patch a tree whose name lacks 'funnel'"
p = T / "src/routing/answer.ts"; s = p.read_text()
def rep(old, new):
    global s; assert s.count(old) == 1, (old[:60], s.count(old)); s = s.replace(old, new)
rep("      const retrievedRaw = raw;\n",
    "      const retrievedRaw = raw;\n"
    "      reasonCodes.push(`fun:raw:${raw.map((c) => c.chunkId).join(\",\")}`); // RAG-FUNNEL\n"
    "      { const fd = denseCandidatesOf(raw); if (fd) reasonCodes.push(`fun:dense:${fd.candidates.map((c) => c.chunkId).join(\",\")}`); } // RAG-FUNNEL\n")
rep("      let sources = compressed.chunks;\n",
    "      let sources = compressed.chunks;\n      reasonCodes.push(`fun:compressed:${sources.map((c) => c.chunkId).join(\",\")}`); // RAG-FUNNEL\n")
p.write_text(s); print("patched", T)
