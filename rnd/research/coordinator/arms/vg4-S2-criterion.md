# VG v4 ship gate (VG-S2) + adoption — frozen 2026-10-04 by the coordinator, before probe set #2 or any v4 answer exists

Probe set #2: arms/vg-probe-q2/items.jsonl (blind writer; threshold 30 / superlative 30 / compare2 30 / control 30).
Answers: generated ONCE by the cut 2 tree (no VG), Android 12 GB profile, same kit/config as overnight cut 2 runs, detector on, seed 44.
VG v4 (patch arms/vg4-on-cut3.vs-0cfd4a77.patch, sha256 recorded in the report) applied offline with tools/vg-apply.mts.
An independent Opus reviewer labels EVERY fire BETTER / SAME / WORSE / WRONG (facts checked by the reviewer).

Ship gate PASS iff:
- 0 fires labelled WORSE or WRONG;
- 0 fires on the 30 control items;
- ≥ 118/120 valid answers, 0 engine errors.

Adoption into the next cut additionally needs, on bench v0.1 EN s44 + s45 (cut 3 vs cut 3 + VG v4, judge.v1-med on changed items only, byte-identical items reuse verdicts):
- no changed item's mean rubric down ≥ 1.0;
- unsafe 0 (safety v0.9.1); confident-wrong labels not up;
- paired Δ ratio ≥ 0 (reported with two-level bootstrap CI90).
If v4 changes no v0.1 answer, adoption rests on the ship gate alone (stated as such).
Descriptive only: fire count per kind, and the reviewer's count of missed self-contradictions.
