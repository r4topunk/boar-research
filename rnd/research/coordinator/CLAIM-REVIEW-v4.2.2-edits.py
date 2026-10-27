import sys, argparse
# Applies the edits of CLAIM-REVIEW-v4.2.2.md to CLAIM-DRAFT-v4.2.2.md and writes CLAIM-DRAFT-v4.2.3.md.
# Usage: python3 this.py [out_path]   (no flags: no decision is pending)
ap = argparse.ArgumentParser()
ap.add_argument("out", nargs="?", default="<workspace>/rnd/research/coordinator/CLAIM-DRAFT-v4.2.3.md")
A = ap.parse_args()
src = "<workspace>/rnd/research/coordinator/CLAIM-DRAFT-v4.2.2.md"
t = open(src, encoding="utf-8").read()
E = []
def e(i, old, new, n=1): E.append((i, old, new, n))

# R1 must-fix: §0 Judge family. Restores the CLAIM-REVIEW-v4.2 E1 order (wins -> lower-judge rule -> ratios -> OpenAI-alone
# intervals -> not shown); offset as the measured range; "ranking does not depend on the judge" scoped to what two arms show;
# the least-sure sentence reworded to what the intervals are (no "would clear our rule": the rule's own lower-judge clause
# excludes the higher judge, and the intervals' seed-noise treatment is not in the sources); "BOAR half as good" back in Not shown.
e("R1", "Two post-hoc re-judges, not pre-registered, both after the claim results: OpenAI's gpt-5.6-sol (Codex CLI) re-scored the existing 4B and deep-tier answers on V-para and on v0.2, the set our analysis plan names (same rubric, orders, blinding). It scores ≈ 0.10 raw higher on both sets and arms. Floor-adjusted, OpenAI vs Claude: V-para 0.361 vs 0.261 (4B), 0.577 vs 0.436 (deep); v0.2 0.517 vs 0.388, 0.639 vs 0.508. The ranking does not depend on the judge (deep − 4B on v0.2: +0.097 vs +0.096 raw; Spearman 0.88–0.97). Wins: 0–1 % on V-para, 2.7 % (4B) and 6.4 % (deep) on v0.2, 0 under Claude; the bar is not met by win rate under either judge. The plan's headline is the lower judge: Claude. Under OpenAI alone the 4B's v0.2 raw CI (0.567–0.666) would clear our pre-registered rule and the deep tier our floor-adjusted target. Not shown: an unexposed set, human labels, a repeat pass.",
  "Two post-hoc re-judges, not pre-registered, both after the claim results: OpenAI's gpt-5.6-sol (Codex CLI) re-scored the existing 4B and deep-tier answers on V-para and on v0.2, the set our plan names (same rubric, orders, blinding). Wins stay low: 0–1 % on V-para, 2.7 % (4B) and 6.4 % (deep) on v0.2, 0 under Claude. The plan's headline is the lower judge: Claude. Ratios rise 0.08–0.11 raw on both sets and arms; floor-adjusted, OpenAI vs Claude: V-para 0.361 vs 0.261 (4B), 0.577 vs 0.436 (deep); v0.2 0.517 vs 0.388, 0.639 vs 0.508. Both judges put the deep tier above the 4B (v0.2: +0.097 vs +0.096 raw) and rank items similarly (Spearman 0.88–0.97). Read alone, OpenAI's intervals for the 4B's v0.2 raw ratio (0.567–0.666) and the deep tier's V-para floor-adjusted ratio (0.519–0.632) lie above 0.50; the rule excludes that reading, and neither is known to include seed noise. Not shown: BOAR half as good, an unexposed set, human labels, a repeat pass.")
# R2 should-fix: §0 submitted app. Says plainly that a number is held and why it is not published (intermediate builds; final only).
e("R2", "**It has been scored on our benchmark internally, on an intermediate build; the final build's number is published when it ships.**",
  "**We scored intermediate builds on our benchmark internally and publish only the final build's number, when it ships.**")
# R3 should-fix: A1 bar readings, same scoping as R1
e("R3", "The offset is ≈ +0.10 raw on both sets and both arms, the ranking of configurations is the same under both judges, and the win rate stays far below half under either. [v4.2.2]",
  "The raw offset is +0.08 to +0.11 on both sets and both arms, both judges put the deep tier above the 4B, and the win rate stays far below half under either. [v4.2.2]")
# R4 should-fix: §1 pre-registered-rule bullet ("the plan's own set" read as a plan-conformant run; it is burnt dev data, post hoc)
e("R4", "On v0.2, the plan's own set, the OpenAI re-judge puts",
  "On v0.2, the set the plan names (now development data), the post-hoc OpenAI re-judge puts")
# R5 nit: Changes bullet, same scoping as R1 (internal header)
e("R5", "The offset is ≈ +0.10 raw on both sets and both arms; the ranking of configurations does not depend on the judge",
  "The raw offset is +0.08 to +0.11 on both sets and both arms; both judges put the deep tier above the 4B")
# T1-T4 meaning-neutral trims (pay for R1 so that §0 keeps a margin under the 1,100 cap)
e("T1", "Ten 5-turn sessions (three extended to 15) on desktop with full history;", "Ten 5-turn sessions (three extended to 15), desktop, full history;")
e("T2", "Desktop median rose to 22 s at turns 14–15 (8 s standalone).", "Desktop median: 22 s at turns 14–15, 8 s standalone.")
e("T3", "the submitted app is scored only internally so far (below).", "the submitted app is scored internally only (below).")
e("T4", "Desktop median 79 s. Not in any submitted build. An expert", "Desktop median 79 s. An expert")  # "not submitted" is stated in Where we stand
# V1-V5: version lines
e("V1", "Draft v4.2.2 (2026-10-17) — v4.2.1 + two folds",
  "Draft v4.2.3 (2026-10-17) — v4.2.2 with the edits of CLAIM-REVIEW-v4.2.2 applied (reviewer verdict ACCEPT WITH EDITS) — Draft v4.2.2 (2026-10-17) — v4.2.1 + two folds")
e("V2", "(DRAFT v4.2.2; independently reviewed through v4.2, see CLAIM-REVIEW-v4.2.md and the changelogs; the v4.2.2 folds await review, see CLAIM-REVIEW-v4.2.2-packet.md; not published) [v4.2.2]",
  "(DRAFT v4.2.3; independently reviewed through v4.2.2, see CLAIM-REVIEW-v4.2.2.md and the changelogs; not published)")
e("V3", "## 0. Post text (v4.2.2, post-facing;", "## 0. Post text (v4.2.3, post-facing;")
e("V4", "## Changelog v4.2.1 → v4.2.2 [v4.2.2]",
  "## Changelog v4.2.2 → v4.2.3\n- v4.2.3 (2026-10-17): edits of CLAIM-REVIEW-v4.2.2.md applied by CLAIM-REVIEW-v4.2.2-edits.py.\n\n## Changelog v4.2.1 → v4.2.2 [v4.2.2]")
e("V5", "awaiting independent review (`CLAIM-REVIEW-v4.2.2-packet.md`). [v4.2.2]",
  "awaiting independent review (`CLAIM-REVIEW-v4.2.2-packet.md`). [v4.2.2]\n- v4.2.2 reviewed 2026-10-17 (independent Opus reviewer): ACCEPT WITH EDITS, see `CLAIM-REVIEW-v4.2.2.md`; applied as v4.2.3.")

out = t
for i, o, n, k in E:
    c = out.count(o)
    if c != k:
        print("FAIL %s count=%d (want %d): %s" % (i, c, k, o[:80])); sys.exit(1)
    out = out.replace(o, n)
open(A.out, "w", encoding="utf-8").write(out)
s = out.index("## 0. Post text"); x = out.index("### Appendix A.")
body = out[s:x].split("\n", 1)[1].replace("[v4.2.2]", "").replace("[v4.2]", "")
print("edits", len(E), "ok; §0 words (markers and heading excluded):", len(body.split()),
      "; caveat count:", out.count("AI-reviewed, not clinically reviewed"),
      "; 'would clear' left:", out.count("would clear"), "; 'does not depend on the judge' left:", out.count("does not depend on the judge"))
