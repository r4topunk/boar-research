#!/usr/bin/env python3
"""KEEP-E (2026-10-21): env-gated empty-raw dense fallback on a COPY of the LITEPACKS tree (answer.ts 0d1ac07d...).
KEEP_E=1: the head-pass/dense append block also runs when the lexical retrieve() list is empty but dense candidates were attached.
KEEP_E unset = byte-identical behaviour. Usage: python3 -I apply_keepe.py <tree copy whose name contains 'keepe'>"""
import sys, pathlib, hashlib
T = pathlib.Path(sys.argv[1]); assert "keepe" in T.name, "refusing to patch a tree whose name lacks 'keepe'"
p = T / "src/routing/answer.ts"; s = p.read_text()
assert hashlib.sha256(s.encode()).hexdigest().startswith("0d1ac07d"), "answer.ts is not the LITEPACKS base"
old = "      if ((settings.packHeadPass === \"a2\" || denseAppend) && gen?.mode !== \"multipass\" && retrievedRaw.length) {\n"
new = ("      const keepE = (globalThis as any).process?.env?.KEEP_E === \"1\"; // KEEP-E empty-raw dense fallback (eval flag)\n"
       "      if ((settings.packHeadPass === \"a2\" || denseAppend) && gen?.mode !== \"multipass\" && (retrievedRaw.length || (keepE && !!denseCandidatesOf(retrievedRaw)?.candidates.length))) {\n"
       "        if (!retrievedRaw.length) reasonCodes.push(\"keep-e:empty-raw-dense\");\n")
assert s.count(old) == 1; s = s.replace(old, new); p.write_text(s); print("patched", T, hashlib.sha256(s.encode()).hexdigest()[:16])
