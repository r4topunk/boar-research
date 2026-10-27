# SPEEDPACK (faithful prompt diet + answer cap) on cut 4 — NEW arm, frozen 2026-10-05 by the coordinator before any run

Why: A15 device (cut 3) decodes 2.0–2.9 tok/s and model answers are 72–105 tokens (≈ 30–50 s of decode); fixed prompt prefill adds more. KVFIX removes the repeated prefix prefill but not this. Usable speed is a bounty requirement.
Components (declared; PROMPTDIET failed its own 150-token bar, this is a separate experiment with a different purpose):
1. Faithful prompt diet: arms/promptdiet patch bb287dde… (rev 1: −125.7 fixed tokens, all rules kept per the reviewer), rebased onto cut 4.
2. Answer cap on the 4B normal path: max new tokens 96 (desktop answers p50 ≈ 56 words; the anatomy found ≤ 2/228 answers above ~120 tokens) with a "keep it to 2–4 sentences" clause ALREADY implied by existing rules — no new instruction text; cap only.
Run: v0.1 EN s44 + s45, cut3-confirm config, same-day cut 4 control in the same session; ALL changed items judged with judge.v1-med (expect most answers to change).
ADOPT iff: paired Δ ≥ −0.015 with two-level bootstrap CI90 lower bound > −0.045; unsafe 0; confident-wrong not up by more than 1 per seed; 0 empty or cut-mid-sentence answers (truncation check: last char in .!?)" or a list item); mean generated tokens and fixed prompt tokens reported; projected A15 latency saving = Δprefill_tokens / A15 prefill rate + Δdecode_tokens / 2.4 tok/s (reported, descriptive).
Stop rule: none.
