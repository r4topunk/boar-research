# PIN2-SCREEN criterion (frozen 2026-10-23 before any generation or judge call; never edited after)
Task: re-gate PIN2 (pin2/PIN2.md; PIN2-criterion.md sha d026c9bb, NO on the context clause only) with a context clause that measures what the compressor controls, then an answer screen on the changed items. Coordinator-directed re-gate written AFTER the PIN2 replay numbers were known (PIN2.md reports total tokens +0.9 % / +3.3 % and compressor tokensAfter over budget 0 / 0): the context clause below is therefore a confirmation of known numbers, not a prediction; the answer screen is the open part. Caps: Haiku 5.5-low <= 60 calls, Opus 0, paid 0, phone 0. Never read blind/, rnd/veil/, boar-eval/bench/v0.4.

## Inputs (sha256 prefix)
- PIN2 tree = kiln-local/rs-PIN2 = SEFIX-124 tree + arms/retrieve-sweep/patches/PIN2.patch (d6c0533c), switch RS_PIN2=1. Base = SEFIX-124 (same chain without PIN2.patch, RS_PIN2 unset). Env both arms: RS_MERGE=gidf RS_SE_LEAD=0.78 RS_SE_MAXDF=0.25 RS_KEEP_NOPROPER=1 (F3 unset).
- Replays (existing, MacBook, 0 LLM): pin2/replays/main.off.jsonl 9aaed475 (= SEFIX-124 base, identity 97/97), main.PIN2.jsonl a34a9d8f, t27.off.jsonl de5a2cce (identity 27/27), t27.PIN2.jsonl 55c1df92.
- Requests: MAIN = sefix/ans-req/sefix124-main-s42.requests.jsonl (d793abd8; 13-pack kit as pinned there, default persona = succinct, seed 42), rows for the 5 MAIN changed ids only; 27 topics = arms/topics27/in/t27-succinct-s42.requests.jsonl (404888d0; kit wiki-vital5 only, persona succinct, seed 42), rows b15 b18 only. Only runId and config.arm change.

## 1. Context clause (0 LLM, on the replays above)
- Total kept tokens per set = sum over items of sum over keptFull of ceil(len(title + "\n" + body) / 4). PASS iff arm/base <= 1.10 on MAIN 97 AND on the 27 topics.
- Compressor budget = the compressor's OWN count: for every arm item with a compressContext reason code context:A->B and a budget code context:pin2-budget-N, B <= N. PASS iff 0 items with B > N on both sets. Items without a compressor call (no context:A->B code) are counted and reported, not failures. Head-pass / dense appends (keptFull outside compressContext) are not part of this check.

## 2. Answer screen (only if section 1 PASSES)
- Items: the 7 PIN2 changed items = MAIN vit-hum-002 vit-cry-008 lan-exp-005 trv-004 st-qa-cooking-se-004 + 27-topic b15 b18.
- Generation: base (SEFIX-124) and PIN2 answers for the 7 items on the mini, Qwen3-1.7B Q4_K_M, lp-screens/tools/mini_gen.sh (2-slot guard, disk >= 25 GiB, detector :8094 used, never started/stopped), BOAR_EVAL_PACK_DIRS=<runner>/kiln/compose/packs-k13 (the SEFIX-124 screen recipe = sefix/ans-tools/run_124_gen.sh; tree = be-0cfd4a77-cut7-litepacks + H4-MERGE.patch + SEFIX-ALL.patch [+ PIN2.patch]). One job per arm, both arms freshly generated. Validity (reported, no verdict change): base MAIN texts vs sefix/ans-traces/sefix124-main-s42.traces.jsonl; live kept chunk titles vs replay keptFull titles per item; 0 errors / empty / loops, else no verdict.
- Divergence-first: an item whose base and PIN2 answer texts are byte-identical is a TIE with 0 calls.
- Judge (divergent items only): Haiku 5.5-low (claude-haiku-5-5 --effort low), judge.v1, both orders, seed 7, sharded N 4 (deepthink/tools/shard_judge.sh ... 4 haiku). Fresh rows for both arms (no cache reuse).
  - MAIN items: each arm judged vs the bench reference (v0.1 / selftest qa-cooking-se refs). Per item s = mean over the 2 orders of the mean of the 3 boar dims (0 if declined), sref likewise, corr = mean boar correctness over orders. Delta s = s_PIN2 - s_base.
  - b15 b18 (no bench reference exists): head-to-head, judge.v1 with the PIN2 answer in the boar slot and the base answer in the reference slot (a local bench dir pin2/judge/h2h-bench with the 2 questions and the base texts as refs), blinded, both orders. Delta s = mean boar score - mean ref score over the 2 orders; corr per side from the same rows.
  - Calls: <= 5 x 2 arms x 2 orders + 2 x 2 = 24 planned; hard cap 60; any judge failure -> rerun only the failed unit within the cap, else no verdict.
- Metrics: paired raw U on the MAIN changed items (U = sum s / sum sref per arm, ratio of sums, Delta U = U_PIN2 - U_base; bootstrap 95 % CI over items reported, n 5, uninformative); b15 b18 enter only better/worse/tie (and their H2H scores are reported). Per item: better iff Delta s >= +1/3, worse iff Delta s <= -1/3, else tie (identical text = tie).
- Health: MAIN items with grounding:health-strict in base reason codes (main.off.jsonl) and 27-topic health items q2 q4 b2 b8 b13 b14 b21 among the 7; any such item worse -> health loss.
- New confident error (LITEPACKS rule: CE = not declined and correctness <= 1.5): an item where the PIN2 answer is CE and the base answer is not (declined or corr > 1.5), warned or not (warned count reported).

## Decision
LEVER-CANDIDATE iff section 1 PASS AND better >= worse + 2 AND 0 health losses AND 0 new confident errors. Else NO. If section 1 fails: NO, no generation, no judge.
Caveats to report: 7 items, one seed (42), Haiku L1 judge (compresses gaps), H2H on 2 items has no reference, dev items, bench engine (not the native Kotlin app), re-gate written after the replay numbers were known.

## Deliverables
pin2/PIN2-SCREEN.md, pin2/screen.json, pin2/judge/ (rows), pin2/traces/ (gitignored), pin2/tools/screen_*; one QUEUE row; BACKLOG PIN2-SCREEN [x] with the verdict; commit rnd, no push.
