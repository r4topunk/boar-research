#!/usr/bin/env python3
"""LITEDECLINE arm patch (0 LLM). Usage: python3 -I mk_patch.py <answer.ts in> <adapter-lite5.ts in> <answer.ts out> <adapter-litedecline.ts out>
Engine (src/routing/answer.ts): AnswerDeps.compactDeclinesOff?: "three" | "all" (eval-only switch, default unset = byte-identical behaviour).
  "three" -> the three compact-only declines named by the frozen criterion skip (declined-compact, false-claim-declined-compact,
             all-citations-removed-declined-compact); the 1.7B then takes the 4B's path at those three decisions only.
  "all"   -> report-only arm OFF5: also uncited-with-sources-declined-compact and uncited-declined-compact skip (= the 4B's grounding path).
Adapter (be/adapter-lite5.ts -> be/adapter-litedecline.ts): (a) the 1.7B catalog entry loses answerTier "default" (untiered, as in the
  product: sizeBytes 1.11e9 <= LOW_RAM_MAX_MODEL_BYTES 1.6e9 -> isCompactModel true); (b) LITEDECLINE_OFF=3|5 -> deps.compactDeclinesOff."""
import sys
a_in, ad_in, a_out, ad_out = sys.argv[1:5]
a = open(a_in).read(); ad = open(ad_in).read()
def sub(s, old, new, n=1):
    assert s.count(old) == n, (old, s.count(old)); return s.replace(old, new)
a = sub(a, "  facts?: boolean;\n", "  facts?: boolean;\n  /** LITEDECLINE (eval-only switch, default unset): \"three\" = the three compact-only declines named in LITEDECLINE-criterion.md\n   * skip (the compact model takes the 4B's path there); \"all\" = also the two uncited compact declines (report-only arm). */\n  compactDeclinesOff?: \"three\" | \"all\";\n")
a = sub(a, "if (fromMemory && genLlm && isCompactModel(genLlm) && !req.answerAnyway) {",
           "if (fromMemory && genLlm && isCompactModel(genLlm) && !deps.compactDeclinesOff && !req.answerAnyway) {")
a = sub(a, "        if (isCompactModel(genLlm) && !req.answerAnyway) {\n          reasonCodes.push(\"grounding:false-claim-declined-compact\");",
           "        if (isCompactModel(genLlm) && !deps.compactDeclinesOff && !req.answerAnyway) {\n          reasonCodes.push(\"grounding:false-claim-declined-compact\");")
a = sub(a, "!health && isCompactModel(genLlm) && !req.answerAnyway && gen.mode !== \"multipass\") {\n        reasonCodes.push(\"grounding:all-citations-removed-declined-compact\");",
           "!health && isCompactModel(genLlm) && !deps.compactDeclinesOff && !req.answerAnyway && gen.mode !== \"multipass\") {\n        reasonCodes.push(\"grounding:all-citations-removed-declined-compact\");")
a = sub(a, "!/\\[\\d+\\]/.test(text) && isCompactModel(genLlm) && !req.answerAnyway) {\n        reasonCodes.push(\"grounding:uncited-with-sources-declined-compact\");",
           "!/\\[\\d+\\]/.test(text) && isCompactModel(genLlm) && deps.compactDeclinesOff !== \"all\" && !req.answerAnyway) {\n        reasonCodes.push(\"grounding:uncited-with-sources-declined-compact\");")
a = sub(a, "else if (sources.length && isCompactModel(genLlm) && !req.answerAnyway) {\n          reasonCodes.push(\"grounding:uncited-declined-compact\");",
           "else if (sources.length && isCompactModel(genLlm) && deps.compactDeclinesOff !== \"all\" && !req.answerAnyway) {\n          reasonCodes.push(\"grounding:uncited-declined-compact\");")
assert a.count("isCompactModel(genLlm)") == 5
ad = sub(ad, "filename: \"models/qwen3-1.7b-q4km.gguf\", sizeBytes: 1107409472, answerTier: \"default\",",
             "filename: \"models/qwen3-1.7b-q4km.gguf\", sizeBytes: 1107409472, // LITEDECLINE: untiered = compact by size, as in the product")
ad = sub(ad, "    ...(emergencyScore ? { emergencyScore } : {}),\n  });",
             "    ...(emergencyScore ? { emergencyScore } : {}),\n    // LITEDECLINE: eval switch for the compact-only declines (unset = engine default).\n    ...(process.env.LITEDECLINE_OFF === \"3\" ? { compactDeclinesOff: \"three\" as const } : process.env.LITEDECLINE_OFF === \"5\" ? { compactDeclinesOff: \"all\" as const } : {}),\n  });")
open(a_out, "w").write(a); open(ad_out, "w").write(ad); print("ok")
