#!/bin/bash
# LITEPACKS tree (0 LLM): kiln-local/be-0cfd4a77-cut7-litepacks = copy of be-0cfd4a77-cut7-headpass-x2 (cut 7 + X2b, answer.ts 289607fd; be/.cache excluded)
# + answer.ts: the CMP30OFF answer hunks (arms/cmp30off/tools/cmp30off.vs-cut7.answer.diff, first file only; applies cleanly to 289607fd)
# + be/adapter-litedecline.ts from be/adapter-lite5.ts (5785ffc4) via arms/litedecline/tools/mk_patch.py (adapter part; its answer.ts output is discarded).
set -eu
A=<workspace>/rnd/research/coordinator/arms; S=<workspace>/kiln-local/be-0cfd4a77-cut7-headpass-x2; T=<workspace>/kiln-local/be-0cfd4a77-cut7-litepacks
[ -e $T ] && { echo "exists $T"; exit 1; }
[ "$(shasum -a 256 $S/src/routing/answer.ts | cut -c1-16)" = 289607fd66dc7685 ]
rsync -a --exclude be/.cache $S/ $T/
awk '/^--- \<users-dir>/{exit} {print}' $A/cmp30off/tools/cmp30off.vs-cut7.answer.diff > /tmp/litepacks-answer.diff
patch -s $T/src/routing/answer.ts /tmp/litepacks-answer.diff
python3 -I $A/litedecline/tools/mk_patch.py $S/src/routing/answer.ts $S/be/adapter-lite5.ts /tmp/litepacks-junk-answer.ts $T/be/adapter-litedecline.ts
rm -f /tmp/litepacks-junk-answer.ts $T/src/routing/answer.ts.orig
echo cut7-headpass-x2+litepacks > $T/ARM
(cd $T && shasum -a 256 src/routing/answer.ts be/adapter-litedecline.ts)
diff -u $S/src/routing/answer.ts $T/src/routing/answer.ts > $A/litepacks/tools/litepacks.answer.vs-x2.diff || true
diff -u $S/be/adapter-lite5.ts $T/be/adapter-litedecline.ts > $A/litepacks/tools/adapter-litedecline.vs-lite5.diff || true
