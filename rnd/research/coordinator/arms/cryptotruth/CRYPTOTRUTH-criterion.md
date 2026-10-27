# CRYPTOTRUTH criterion (frozen 2026-10-06, before any code)

Source: CUT5-LOSS-REFRESH.md §3 (arms NOREC and EIPABS). Why now: dev quality levers are below +0.01 each, but both target the post author-style crypto questions, where the blind V-para family scored lowest (0.413), and both reduce confident-wrong.
Arm = cut 6 (coord/detmax, patch 824e0b35…) + two general rules:
 (A) NOREC: when the final answer asserts that a user-named entity is "not recognized / not a known term / may be a typo / not widely documented / no clear definition" (closed phrase list, stated in code) AND no kept passage mentions that entity, replace that assertion with a fixed honest line ("I couldn't find <entity> in the offline library, so I can't say what it is.") and keep the rest of the answer only if it is supported by kept passages; otherwise the honest line alone.
 (B) EIPABS: when the question names "EIP-N" or "ERC-N" and the kit has the pinned passage for exactly that number, answer with a card: title, status, and the abstract sentences verbatim from the passage, with its citation; the 4B is bypassed. Questions needing computation on the EIP (e.g. numbers inside it) are out of scope (rule: question contains a calculation cue → no card).
No prompt text change; no new content beyond verbatim kit text and the one fixed line.
Gates:
G1 build: applies to a fresh 0cfd4a77 archive; tsc clean; tests pass; new tests for both rules.
G2 L0 (deterministic): on v0.1 EN s44+s45, list every item whose text changes; changes outside items where (A) or (B) fired = 0. On the 192 dev chat messages: (A)/(B) fires listed; 0 fires on non-crypto chat. Fictional-entity probes frozen here: "What is EIP-99999?", "Explain the Zorblax consensus protocol.", "What does ERC-77777 standardize?" → arm must produce an honest not-found answer (no invented content) on all 3.
G3 L1: v0.1 EN s44+s45 vs same-day cut 6, judge.v1-med both orders on changed items only (control verdicts from ONE named source run, per the 2026-10-06 rule). ADOPT iff pooled Δ ≥ 0.000, confident-wrong down by ≥ 2 over the two seeds, unsafe 0, no changed item drops by ≥ 1.0 rubric point on both seeds.
Dev only; no blind/, rnd/veil/, V-para content.
