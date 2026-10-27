# GROUND-ST criterion — addendum 1: declared variant X3 after the step-0 FAIL on G1 (frozen 2026-10-13 13:5x, coordinator; base criterion sha 895d1ebb… unchanged)

reopen: GROUND-ST step 0 (GATE.md, D0.md): packGround 51 / keepTop1 53 fact chunks kept vs the bar 55 (articles 89 / 92 ≥ 85; G2/G3 pass). D0: of the 9 chunk losses top1 does not recover, all have the fact chunk at raw position 1–3 behind another pack passage at position 0 (often a kit-pack passage, since "pack:" includes crypto/wikivoyage), so keepTop1 protects the wrong passage; the ceiling inside the gates is 63.

## Variant X3 = packGround + perPackTop1 (settings.packGround: "perpack")
As packGround (full-text onTopic, pin back one compression cut, top-2 fallback), plus: for EACH installed pack (kit packs included), its best-ranked passage in the raw list is never dropped by grounding when its full text shares ≥ 1 query term (stemmed/lowercased as onTopic does); same gates as P4 (not health, not history, no lexicon names, not multipass); the compression budget is unchanged (a protected passage is pinned, so another may be cut — report how many OFF-kept chunks are cut). Nothing else changes; default absent = byte-identical.

## Gates (unchanged, applied to X3)
G1 fact chunk kept ≥ 55 and fact article kept ≥ 85, raw unchanged (67); G2 RULE 26 (lost-context 0; empty-kept over OFF-retrieving not up; v0.1 gold kept ≥ 12; v0.2 resolvable gold kept ≥ 4; tokens ≤ cap; kit kept-list changes reported add-only vs other); G3 p50 ≤ 1.2× (the keep step's extra compression call is now timed inside the replay, since G3 of step 0 timed retrieval only).

## Stage 1 amendment (applies to whichever variant passes)
Because the keep rules change the context on 29–36 % of kit dev items (add-only), stage 1 adds a quality no-harm run on the v0.1 public 60: OFF and ON generations on the stage-1 tree (4B cut 7), Haiku 5.5-low N=4 both orders (240 calls), paired Δ; rule: CI high of (ON − OFF) ≥ −0.03 → no harm; else the variant does not enter the STACK even if the 180 look good.
Variant entering stage 1 = the one with the highest fact-chunk kept among those passing G1–G3 (X3 expected). No further variants without a new addendum.
