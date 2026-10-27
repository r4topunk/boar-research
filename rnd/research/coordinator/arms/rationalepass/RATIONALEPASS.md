# RATIONALEPASS (T1): what the Opus rationales say is wrong or missing in H (2026-10-12)
Arm H (cut 6 + Qwen3.6-35B + think 512, s42), jev p >= 0.6, criterion sha 7ab8b3812c17…013 (frozen before the run). V-para n=51, v0.2 n=110. Cost [usage detail removed] jev, 0 Claude. Shares = loss-weighted share of total loss (as LOSSMAP). Primary bucket loss: V-para absent 0.587 / wrong 0.397 / thin 0.016; v0.2 absent 0.551 / wrong 0.214 / hedged 0.178 / off_q 0.057.

| Axis | V-para n | loss share | of wrong loss (n wrong) | v0.2 n | loss share | of wrong loss (n wrong) |
|---|---|---|---|---|---|---|
| stale | 2 | 0.048 | 0.120 (2) | 2 | 0.019 | 0.062 (1) |
| numeric | 11 | 0.248 | 0.451 (7) | 25 | 0.244 | 0.533 (9) |
| date | 3 | 0.061 | 0.105 (2) | 22 | 0.211 | 0.518 (9) |
| entity_swap | 0 | 0 | 0 | 0 | 0 | 0 |
| overgeneralised | 24 | 0.466 | 0.407 (7) | 35 | 0.311 | 0.059 (1) |
| fabricated | 8 | 0.196 | 0.495 (8) | 4 | 0.051 | 0.188 (3) |
| recent_event (2024+) | 8 | 0.153 | 0.127 (2) | 4 | 0.032 | 0.062 (1) |
| rationale_names_correction | 49 | 0.964 | 1.0 (16) | 110 | 1.0 | 1.0 (17) |

Cross-tab by LOSSMAP primary (axis loss share in bucket; V-para absent/wrong, v0.2 absent/wrong/hedged): numeric 0.069/0.179, 0.112/0.114/0.019; date 0.019/0.042, 0.100/0.111/0; overgeneralised 0.304/0.162, 0.237/0.013/0.061; fabricated 0/0.196, 0.011/0.040/0; stale 0/0.048, 0.005/0.013/0; recent 0.102/0.051, 0.019/0.013/0. (Full table per bucket in the JSON.)
Combos on wrong loss: numeric+date 0.505 (8 of 16 items) / 0.699 (12 of 17); entity+fabricated 0.495 / 0.188 (entity alone 0); any of the six 0.931 / 0.882. Axes overlap, so shares do not add.

Fact type of comparison+synthesis losses (V-para 14 items, v0.2 19): infobox_attribute 0 / 0.205; country_number 0 / 0; practical 0.123 / 0; mechanism 0.182 / 0.356; other 0.695 / 0.439.

(a) Decline oracle (no item declined in either set, so floor 1/1/1 = ratio 3/ref points; mean ratio of the wrong-primary items 0.410 vs floor 0.206 on V-para, 0.462 vs 0.202 on v0.2): replacing every wrong item by a decline changes the mean judge ratio by -0.064 (V-para 0.533 -> 0.469) and -0.040 (v0.2 0.608 -> 0.568); decline is better on 0/16 and 0/17 items. The judge pays a wrong answer about twice what a decline earns, because wrong answers still score on completeness and usefulness.
(b) CITEMAP-REF (items citing a domain; both sets store reference_sources as URL strings, 167 and 197 URLs): V-para en.wikipedia.org 49/51, en.wikivoyage.org 14, csrc.nist.gov 6, ethereum.org 3, ethresear.ch 2, then single items (cp.pt, iec.ch, evisa.imigrasi.go.id, newscenter.lbl.gov, pq.ethereum.org, pmc.ncbi.nlm.nih.gov, nejm.org, who.int). v0.2 en.wikipedia.org 85/110, nhs.uk 10, cdc.gov 8, ready.gov 6, ethereum.org 4, weather.gov 3, bitcoin.org 3, en.wikivoyage.org 3, usgs.gov 2, eips.ethereum.org 2, then singles (developer.bitcoin.org, wwwnc.cdc.gov, oceanservice.noaa.gov, rnli.org, keishicho.metro.tokyo.lg.jp).

Reading against DEEP-RESEARCH §3 (single seed; V-para shares about +-0.05; wrong bucket is 16 and 17 items):
- O-4 stale >= 40 % of wrong loss: NOT met (0.12 / 0.06; 2 and 1 items). Freshness is not what the wrong bucket is made of; recent_event is 0.13 / 0.06 of wrong loss and 0.15 / 0.03 of all loss (V-para absent items carry most of that 0.15).
- O-5 numeric+date >= 40 %: MET on both (0.505 / 0.699), so NUMCHECK goes ahead; on v0.2 it is 12 of 17 wrong items. Caveat: the axis is read from judge wording, and the V-para half is 8 items.
- Entity+fabricated >= 50 %: borderline V-para (0.495, all fabricated, entity_swap never fires) and clearly not v0.2 (0.188).
- O-8 abstention oracle >= +0.03: NOT met, the opposite sign (-0.064 / -0.040). Replacing wrong with decline only pays if the judge scored a decline above the floor; no decline exists in these runs, so the number is a floor-based bound, not a measurement. A selective abstain line is dead on this judge unless declines are scored above 1/1/1 (open: score a real decline once).
- T3 comparison fact types >= 30 % infobox+country: NOT met (0 / 0.205; n = 14 and 19; `other` and `mechanism` dominate). CMPCARD / O-7 not triggered by this pass.
- rationale_names_correction is saturated (1.0 on wrong items, 0.96–1.0 overall): the rationales nearly always state the correct content, so the axis does not discriminate and stale cannot be called a lower bound only; stale is simply rare in the rationales.
Outputs: aggregates/rationalepass-H-{vpara,v02}.json (ids, labels, probs, summaries), tools/rationalepass.py, RATIONALEPASS-criterion.md(.sha256). Cache: blind/V-para/runs-dt512/rationalepass-cache/, blind/bench-v02/runs-dt512v02/rationalepass-cache/. EXPOSURES row not yet written.
