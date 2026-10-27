# PACK-BUILD criterion (FROZEN 2026-10-22 16:5x, before any build or shard replay is read)

Question: which packs, installed or built from permitted corpora, put more of the dev facts into the context the 1.7B reads, without crowding out the facts the current kit already delivers?
Sets (dev only): MAIN 92 keyed items (v0.1 52 + cooking/money 40) and v0.1 52 alone; fact check = the FACTPRESENT lexical rule (noisy: upper bound on S1); baseline = K3 kit funnel from COVERAGE-MAP (S1 52 / kept 23 on MAIN 92; S1 12 on v0.1 52).
Builds / installs under test, each its own 0-LLM funnel replay (K1 tree, stock settings and, where chunk vectors exist, head pass a2 + packDense2 extra):
B1 install qa-cooking-se + qa-money-se (built, CC BY-SA).
B2 Wikipedia top100k behind an additive quota q = 1 (one slot reserved, never a peer pack; engine patch with a switch; default off byte-identical).
B3 full English Wikipedia, shard by shard from hf.co/datasets/r4topunk/boar-packs wiki/en (15 shards, CC BY-SA; the mini downloads one shard, replays, deletes it; union of fact-present per item).
B4 (web W85–W87) travel.state.gov per-country pages (PD) as boar-travelinfo-us: only if the 0-LLM check finds ≥ 3 dev travel facts in those pages.
Rules: a build PASSES iff on MAIN 92 kept facts ≥ baseline + 3 AND on v0.1 52 kept facts ≥ baseline (no net loss) AND S1 drops by ≥ 3 on the set it targets; a build that gains S1 but not kept is COVERAGE-ONLY (the next lever is retrieval, not content). PASS builds go to the Haiku answer screen (1.7B on the mini, changed-context items only, judge.v1 N 4 both orders, cap 300 per build); LEVER iff ΔU ≥ +0.02 with CI low > −0.01 on the changed items and CE-unwarned not up.
Licences: PD / CC0 / CC BY / CC BY-SA only without asking; WTFPL (the post author blog pack) and MIT (ethereum.org inside boar-crypto) are flagged for r4to, not used in new builds until he answers.
Prediction: B1 PASS on MAIN (kept 23 → 29), neutral on v0.1; B2 PASS on v0.1 only if the quota holds (kept +3…+5, 0 lost); B3 adds ≤ 2 kept facts on dev beyond top100k (its value is for the the post author-style sets: WIKIFULL 37/78 on v0.2); B4 ≤ 3 facts.
Caps: 0 LLM for funnels; Haiku ≤ 300 per PASS build; Opus 0; paid 0; phone 0. Mini disk ≥ 25 GiB (one shard at a time).
