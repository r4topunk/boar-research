# REFS-V2 protocol (frozen 2026-10-21 before any call): references v2 on bench v0.4, both families

Governs RULER-SPEC-v1 r3 §3.2 / §10.5. Frozen before the first generation call; any change = new version, logged.

## Inputs (pinned)
- Items: boar-eval/bench/v0.4/items.jsonl sha f9ad2f2f0fc367811ea03690bc9b05e52d85b1ee5fb662600efa818587d33594 (75 items, 88 user turns; 8 multi-turn, 7 with a device location).
- Prompt: prompts/reference.v2.md sha 5e41177dfa1badcff297d14f477c94393c626da76db75797841f18ce920754f1 = reference.r3-pilot (REFVAR) + three lines: answer as of the current date, treat a stated location as the user's, answer only the last turn of a conversation. Reasons per instruction: search + authoritative sources (frontier AI + internet, B31:7); as-of date (REFVAR rule 3: uncapped web picks up dated facts, the archive must say when); location (V2 "city I am currently in", RV4); multi-turn (blueprint multi-turn shapes); same language; no length cap (REFVAR rule 2: uncapped does not lower U); safety steps + seek care (health items, harm gate); false premise (items with over-refusal / premise shapes); sources with dates (REFVAR rule 5, "date not shown" compliant). No mention of BOAR, the app, packs or the benchmark.
- Generator: tools/gen_refs_v2.mjs sha 72d274c2070ed33538011cd0bef95307d3d1e515b9111df3430b1850d88f0edf. Checker: tools/check_refs_v2.py sha ed0629b4abbc000a83a8e3d299edabef514987f26bb413000daddc4e4690a12b.
- Message frame: "Current date: YYYY-MM-DD" (call's date, GMT-3); for location items "The user is currently in <city> (coordinates <lat>, <lon>)."; for turn k > 1 the conversation so far (user turns + this family's own earlier answers) then the latest user message.

## Families
- F1 Claude: `claude -p`, model opus (claude-opus-5-5 expected; the actual model id is recorded per turn), tools WebSearch + WebFetch, [usage detail removed] only (cleanEnv, no API key). Run by the ruler session on the MacBook.

## Rules
1. One draw per item per family. An ok row is never regenerated or replaced. A failed turn gets one retry (2 attempts). An item still failing gets no row; a later run retries only items without an ok row; discarded partial conversations are logged (<family>.discarded.jsonl).
2. Cap per family: 110 calls (88 turns + 22 retries). Rate limit = stop; rerun resumes.
3. Nobody reads reference text before both families are complete and checked, except the checker (counts only). No app arm answers any v0.4 item before both families are frozen.
4. Freeze per family: check_refs_v2.py exits 0 (75/75 ok, turn counts match, shas constant, no BOAR mention); then MANIFEST.json gets the family's file sha; one QUEUE row; one EXPOSURES row. Rows without any source URL are reported (not regenerated).
5. After both families are frozen: contested-point pass (spec §3.2) produces the errata file, hashed before any judgment.
6. Outputs: boar-eval/bench/v0.4/refs/v2/{claude,codex}.jsonl (+ .calls.jsonl, MANIFEST.json). Rows: id, family, ok, multiTurn, nTurns, hasLocation, answer (multi-turn = "[Turn k]" blocks), sources (url|title|date, union over turns), words, turns[] (per-turn answer, sources, rawResult, asOfDate, messageSha256, model, usage, searches, fetches, wall), prompt/items/generator shas, cliVersion, generatedAt.

## Exposure
v0.4 question text (and location) goes to the two reference families (Claude Opus and Codex, live web search). Items stay a held-out ruler: no answering system sees them; no engine work uses them.
