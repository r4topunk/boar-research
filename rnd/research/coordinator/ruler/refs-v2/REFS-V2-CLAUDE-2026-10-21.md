# REFS-V2 Claude half (F1) frozen 2026-10-21

- Protocol REFS-V2-criterion.md (sha 65e84704…, rnd bdc6055b, frozen before any call). Generator 72d274c2…, prompt 5e41177d….
- Output boar-eval/bench/v0.4/refs/v2/claude.jsonl **sha d83e518688cdc636bbf7c221370deeae239b13f859830a9ee8ab337cf9f5209f**; MANIFEST.json family "claude".
- 88 Opus calls (75 items, 88 turns; cap 110), 0 retries, 0 failures, 0 discarded conversations; all claude-opus-5-5; as-of date 2026-10-21 on every turn; WebSearch + WebFetch; [usage detail removed] only, 0 paid.
- Checker: 75/75 ok, 8 multi-turn, 7 location; words median 703 (p10 335, p90 1371); sources median 6; 1 row without a parsed source URL (cx-032; reported, not regenerated, rule 4).
- Deviation (logged): the frozen checker (ed0629b4) flagged 7 rows as "mentions BOAR" by substring; the matched tokens were board ×6, sandboarding ×2, blackboard, boarding (counts only, no text read). Fixed to a word-boundary match (checker e0436c61); 0 hits. The references were not touched.
- Nobody read reference text. Next: Codex half (r4to, CODEX-KIT.md), then the contested-point errata pass (spec r3 §3.2), then the gate opens.
