# exp-35 verdict: rv2 KILLED (Kiln, 2026-10-03 night; criterion 64ede784; Sonar's verdict.py reproduces it)

TL;DR (v0.1 EN, 57 items, Android 4B, pooled s42 + s43, judge.v1):
- **A 0.538 → R 0.517, Δ −0.021 (CI90 −0.054…+0.009) → KILL** (Δ ≤ 0).
- **Safety:** unsafe 0 / 0.
- **V-exact:** vx-001 Japan +0.25; vx-002 −0.08; Mozi and Gríma unchanged. None moves ≥ 1.
- **Retrieval p50:** 3.59× on desktop (192 → 690 ms).
- **L0 vs judge:** gold sentence in context rose 4 → 18 /56 on the real traces, yet the judged score fell. The second time this happens (E1(a): vital5 4 → 11, Δ 0.000).

## Why (Sonar's read of the traces; per-item mean of 2 seeds)
- **By gold-sentence category (R vs A):**
  - gained a gold sentence: n = 15, Σ −1.83;
  - gold in neither: n = 38, Σ −4.33;
  - gold in both: n = 3, Σ +0.83.
- **The worst items show fragments overriding the 4B's own (correct) knowledge:**
  - lan-cmp-001 "Does Brazil have more people than Russia?" (−2.58). A, from memory: "Yes, 215 M vs 144 M". R, with the right numbers in context: "No… Russia has over 140 million, while Brazil has about 212 million. Therefore Brazil has a larger population". It contradicts itself.
  - lan-rsn-002 Burj Khalifa on Baikal's floor (−3.08). A: correct "no, submerged by ~814 m". R: the window says "deepest point is 1,642 m below sea level", and the 4B concludes the top "would stick out by ~830 m".
  - lan-exp-003 Kenya essentials (−1.67). A: "English and Swahili". R: the 60-word window says English only, and the 4B drops Swahili.
- **Readings:**
  1. On popular facts the 4B's memory is good. Short (45–60-word) windows give partial or ambiguous facts, which the 4B follows over memory. They also hand it numbers to compare, and it compares them wrongly.
  2. The gold-sentence metric counts presence, not harm from partial context, so it is necessary but not sufficient.
  3. rv2 differed from Anvil's Q450 in three ways: 45–60-word windows vs 120-word passages, 240 vs 340 words, and its own retrieval vs gold articles. **The judged gain of Q450 did not transfer** to engine retrieval + short windows.
- **The bigger-pack / retrieval line on v0.1 is now:** exp-33 KILL (B, C2), exp-35 KILL (rv2).
