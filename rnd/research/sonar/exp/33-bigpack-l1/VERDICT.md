# exp-33 verdict: KILL the bigger-pack line for now (Kiln, 2026-10-03 night; L1-criterion 9ed14be1 + addendum)

TL;DR (Android 4B, s42, judge.v1; Kiln's json: boar-eval/runs/kiln/bigpack-l1/bigpack-verdict.json):

| | A (kit A) | B (+ top100k, full search) | C2 (+ top100k, title tier, bounty2b) |
|---|---|---|---|
| vx-001 Japan | 1.67 | 1.33 | 1.50 |
| vx-002 PQ signatures | 2.67 | 2.67 | **1.67 (−1.0)** |
| vit-hum-001 Mozi | 2.67 | 2.67 | 2.67 |
| vit-hum-004 Gríma | 1.00 | 1.00 | 1.00 |
| v0.1 EN ratio (57) | 0.545 | 0.541 (Δ −0.005, CI90 −0.036…+0.028) | 0.529 (Δ −0.016, CI90 −0.040…+0.006) |
| unsafe (v0.8.7) | 0 | 0 | 0 |
| retrieval p50 | 179 ms | 589 ms (3.28×) | 194 ms (1.08×) |
| gold sentence in context (exp-34 L0) | 4/56 | 7/56 | 8/56 |

- **Verdict:** neither B nor C2 improves ≥ 2 V-exact knowledge items, and C2 is worse on vx-002. **KILL:** no full-EN title-tier build.
- **Caveat:** 1 seed, MDE ≈ 0.04.
- **What happens with Gríma (Sonar's read of the traces):**
  - A, with only "Wikivoyage: LOTR tourism": the 4B says "Gríma does not kill Saruman… killed by Aragorn's men at the Black Gate".
  - C2, with Saruman + LOTR passages that lack the killing: "Gríma does not kill Saruman [1]… killed by Gandalf", citing a source that doesn't say so.
  - rv2 R s42 (exp-35): the window "Saruman's murder by Gríma (seen only in the Extended Edition)" from the FILM article. The 4B reads it as "…does not kill Saruman… only in the Extended Edition, not in the original film or book [1]".
  - So the article reaching the context is not enough. The context must hold the BOOK's plot sentence, and a misleading film window makes it worse.
  - **rv2.2** (DEV, `sonar/exp/35-rv2-l1/rv22-on-rv2.DEV.patch`):
    - a named article gives its lead + its top 3 chunks by stems, any section;
    - named-article windows get +0.05 over keyword-only articles.
    - This puts "Saruman reveals crimes that Wormtongue has done, causing Wormtongue to turn on Saruman and kill him in front of Bag End" in the Gríma context.
    - Gold sentence overall 18 → 17 (+0 / −1, lan-ref-003). A candidate delta after the exp-35 L1, not before.
- The rv2 line (exp-35) is separate: it uses top100k with question-ranked windows, and its L1 is running.
