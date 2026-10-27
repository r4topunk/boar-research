# CRYPTOSEL (crypto-pack spec selection: tables/constants and EIP sections) on cut 3 — frozen 2026-10-05 by the coordinator before any code

Evidence (KNOWLEDGE-PACK-SIZING.md): vit-cry-002/003 (EIP-7805/4444) and vit-cry-009 (EIP-7251 constants table) have the needed text IN the shipped crypto pack, but question-similarity selection picks prose windows. Crypto is a the post author/V-para family.
Mechanism: for questions that already route to the crypto pack, when a retrieved EIP/spec article is selected, (1) prefer chunks containing the EIP number or a named constant/parameter from the question, (2) keep a matching constants-table chunk intact (no window cutting), (3) cap at the existing work budget. Non-crypto questions untouched.

## L0 (deterministic, stub-LLM replay, no judge)
- Gold fact in context (Sonar goldhit method) on the 3 target items: ≥ 2/3 gain it, 0 lose it;
- other v0.1 + V-exact items: contexts byte-identical except crypto-routed items; 0 crypto-routed item loses its gold sentence; retrieval p50 ≤ 1.2× cut 3.
## L1 (v0.1 EN s44 + s45, judge changed items only, judge.v1-med)
PASS iff: target items mean rubric up on average ≥ +0.5; no changed item down ≥ 1.0; unsafe 0; cw not up; paired Δ ≥ 0.
Stop rule: one revision after an L0 FAIL; no revision after L1.
