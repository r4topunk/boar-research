# exp-38: a citation marker inside a decimal number ("9 [2].4 million") (Sonar, 2026-10-03 night; found by Anvil in the exp-35 traces)

TL;DR:
- **Bug:** `attributeCitations` (src/routing/citations.ts) splits the answer on every ".". So "covering about 9.4 million square kilometres." becomes the "sentence" "…about 9." and gets "9 [2].4 million".
  - It is in the shipping stack: arm A (bounty1) and both cut 2 variants.
  - It hit 1/65 answers per run in exp-33/35 (lan-exp-005, the Sahara, every seed and arm). A demo answer with a number like "9.4" can show it.
- **Fix:** a "." between two digits doesn't end a sentence: `/(?:[^.!?\n]|(?<=\d)\.(?=\d))+[.!?]*/g`. One line plus a comment.
- **Tests:** 2 new (`citations.decimal.test.ts`): the Sahara sentence is cited after the sentence, and a real sentence end after a number still splits. `src` suite 1157/1157; tsc clean on the file.
- **Patch:** `citefix-on-cut2.patch` (delta on cut2-norv2 aa28cf3c; applies cleanly on cut2-rv2 too).
