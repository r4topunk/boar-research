#!/bin/bash
# The only change to the engine copy: ANSWER_MIN_SIMILARITY (RagPure.kt l.41, const 0.7) becomes a getter that reads the
# system property boar.cutoff (default 0.7), so the harness can sweep the relevance gate. Nothing else is touched.
set -euo pipefail
F="$1/team/sopa/boar/engine/rag/RagPure.kt"
grep -q 'const val ANSWER_MIN_SIMILARITY = 0.7' "$F"
sed -i '' 's/const val ANSWER_MIN_SIMILARITY = 0.7/val ANSWER_MIN_SIMILARITY: Double get() = System.getProperty("boar.cutoff")?.toDouble() ?: 0.7/' "$F"
grep -n 'ANSWER_MIN_SIMILARITY' "$F" | head -3
