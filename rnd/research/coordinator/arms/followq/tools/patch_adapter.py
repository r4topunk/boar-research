#!/usr/bin/env python3
"""patch_adapter.py <in adapter.ts> <out adapter.ts>: retrieval-only variant of the committed desktop-node runner.
Two overrides, nothing else: (1) the route gate always answers SEARCH (the diagnostic asks what retrieval returns once a search is chosen;
skip-rules and rule-routed items behave as in the engine), (2) generate() throws, so no answer is ever produced (sources events are emitted before generation)."""
import sys
s = open(sys.argv[1]).read()
anchor = "  const records: any[] = [];\n  const answerer = A.createAnswerer({"
assert s.count(anchor) == 1
patch = '''  // FOLLOWQ (retrieval-only): forced SEARCH verdict, no generation.
  (engine as any).nextTokenProbs = async () => [{ token: "SEARCH", prob: 0.98 }, { token: "ANS", prob: 0.02 }];
  engine.generate = (async () => { throw new Error("followq: retrieval-only, generation disabled"); }) as any;
'''
open(sys.argv[2], "w").write(s.replace(anchor, patch + anchor))
