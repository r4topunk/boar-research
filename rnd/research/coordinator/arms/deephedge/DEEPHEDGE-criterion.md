# DEEPHEDGE: "lead with the substantive answer, safety note last" on the deep thinking tier — does it recover the hedged items on v0.2? (frozen 2026-10-12, loop coordinator)

## Tags
Tags: none

## Question
Arm **E** = H (dt512) + `settings.deepHedge = true`: one instruction appended after the persona on the deep thinking generation only — "Lead with the substantive answer: the facts, numbers, steps or comparison the question asks for. If a safety or professional-help note is warranted, add it in one sentence at the end. Never replace the answer with a referral or a generic caution." Cap unchanged (200). Health extractive path, fast tier, multipass untouched; default-off byte-identical to dt512 (differential 6/6). Target: the 11 v0.2 items whose LOSSMAP primary bucket is *hedged* (18 % of H's v0.2 loss; 9 on the deep path) and the hedged axis (21 items). V-para has 0 hedged-primary items: this is a v0.2-only lever and cannot be a LEVER at the bounty bar; the best outcome is SMALL on v0.2 with the mechanism confirmed.
reopen: n/a (prompt family on the deep tier: DEEPFULL closed length/persona, DEEPCOVER closed key-point enumeration; this targets refusal/deferral behaviour, a different failure bucket).

## Fixed inputs
- Tree `<runner>/kiln/be-0cfd4a77-deephedge` = dt512 + `deephedge.vs-dt512.patch` (f4f775a1…; content hash 80e3d402…); runner `deephedge-remote-run.sh`; requests = H's v0.2 s42 with `config.arm` deephedge and the setting, on the union of the 11 hedged-primary ids and random20-v02 (≤ 31 ids).
- Control H = dt512 rows (v0.2 Haiku slice rows; Opus L2-H-1seed on all 110).
- Gate classifier: jev boolean "hedged" over answer text (same wording as LOSSMAP's hedged axis), 0 Claude calls.

## Power
expected_delta: +0.01…+0.02 raw on v0.2 (source: hedged items hold 0.18 of H's loss at ratio 0.29; recovering half of that bucket ≈ +0.03 on those items' share → ≈ +0.015 on the set; 0 on V-para)
n: 110 (v0.2 s42) if stages 1–2 pass; the hedged-11 subset decides the mechanism, not the verdict
seeds: 1 (v0.2 is seed-stable, r 0.90)
mde: ≈ 0.025 raw at 110 → expected_delta < mde: the arm cannot show a LEVER; it can show SMALL (CI low > 0) or close the bucket. Declared: a v0.2-only, mechanism-level arm.
slice: random20-v02.ids ∪ the 11 hedged ids (generation); L1 on random20-v02 vs H's Haiku slice rows; the 11 hedged ids judged by Haiku vs H's Haiku rows where they exist (none outside the slice) — so the hedged-11 are read by the jev gate and, if promoted, by Opus vs L2-H-1seed (22 calls)
l1_futility: stop only if Haiku delta <= 0 AND h2h <= control; any Haiku delta > 0 -> Opus N=4 on the same 20 ids
reopen: n/a

## Stages and rules
0. Generation of the ≤ 31 ids (0 calls) → **jev gate: hedged answers on the 11 hedged-primary ids drop by ≥ 50 % (H: 11/11 by construction → E ≤ 5), 0 errors, answer length ≤ 2× H's p50** → else closed at step 0.
1. L1 Haiku N=4 on random20-v02 vs H's Haiku rows (40); rules above + near-miss. Correctness clause as DEEPCOVER (−0.05 → NO).
2. Opus N=4 on the 11 hedged ids vs L2-H-1seed (22) — mechanism read-out (reported, not a verdict).
3. Only if stage 1 promotes: full 110 (generation) → Opus 220 vs L2-H-1seed (next week's budget). Verdict: SMALL (CI low > 0) / NO; LEVER impossible by declaration.

## Stop rules and budget
Mini disk ≥ 25 GiB (25.6 now; traces only), one MoE server, detector untouched. This week: Haiku ≤ 60 left (40 used here), Opus ≤ 56 left (22 + up to 34). Generation ≤ 1 h.

## Outputs and exposure
`arms/deephedge/DEEPHEDGE.md`, `aggregates/`, traces/judgments under `blind/bench-v02/runs-deephedge/`. One EXPOSURES row.
