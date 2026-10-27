# QREWRITE criterion (frozen 2026-10-23 before any replay, generation or judge call; never edited after)

Question: does rewriting the user question into "answer form" before search close the first-stage search gap
(PACKPROOF funnel raw 40 % -> kept 54 % -> cited 28 %; QFORM: answer-term form F5 83 % kept vs 23-25 % for situational forms)?
Cost rule: cheapest path with early stops. Haiku only in stage 2 (cap 300); Opus 0; paid API 0; phone 0. blind/, rnd/veil/, bench v0.4 never read.

## System (all stages)
- Tree kiln-local/rs-SEFIX, READ-ONLY (SEFIX-124 = RS_MERGE=gidf RS_SE_LEAD=0.78 RS_SE_MAXDF=0.25 RS_KEEP_NOPROPER=1, F3 off). No engine patch in stages 0-1.
- Replay driver = arms/qrewrite/tools/replay-qrw.ts, a copy of arms/retrieve-sweep/tools/replay-sweep.ts with ONE hook (marked QREWRITE):
  env QRW_MAP=<json {id: text}> and QRW_MODE=replace|concat. Inside the driver's retrieve wrapper (the engine's single retrieve dependency),
  for the current item the engine's search query q becomes `text` (replace) or `text + " " + q` (concat). The engine's answer()
  still receives the ORIGINAL question, so routing, detector, grounding/keep, head pass and dense append all see the user's words
  (what a deployed rewrite would do). Items without a map entry are unchanged.
  "Two queries merged by gidf" is implemented as concat: FTS5 builds an OR query (wikiPack.ts), so one gidf-bm25 pool scores both term
  sets together, the vector re-rank uses the joint text, same k, one retrieve call. Done in the replay driver, no engine hook.
- Identity check before any arm: driver with no QRW_MAP must equal the reference replays (MAIN: sefix/replays/main.F1F2F4.jsonl raw + kept ids
  97/97). If not 97/97, stop and report.
- Sets:
  MAIN 97 = decode-ground/runs/req/dg-S-K1-main-s42.requests.jsonl via coverage-map/sefix/tools/run_main.sh recipe (kit kits.py 10 = 13 packs,
  tasks-from funnel-K3 traces, settings packHeadPass a2 + packDense2 append-budget, --forward-opts, --wide 12), env SEFIX-124. Score = chunk-level
  facts of 92 keyed (coverage-map/tools/chunklevel.py score(); base 42 = main.F1F2F4).
  ST180 = PACKPROOF's 180 self-tests (packproof/in/on-k13*.requests.jsonl), same recipe, kit = kits.py 10 + v3proto qa-bitcoin-se /
  qa-ethereum-se for their 20 items each (ON kits), tasks-from = PACKPROOF ON gen traces. Score = own-article in raw (engine raw list, first
  retrieve call) and in kept (keptFull), PACKPROOF url+title match against packproof/in/own.json. Base = the same driver with no map.
- Health family: MAIN ids lan-hlt-*, vit-hlt-*, dng-*; ST packs qa-health-se, boar-firstaid-en, boar-medlineplus-en.
  Health loss = delivered (MAIN chunk) / kept (ST own article) in base and not in the arm.
- Crowding share (ST180) = share of kept chunks that are not from an own article; also mean kept chunks per item.

## STAGE 0 (0 LLM, replay only): ceiling
Oracle text O(i), fixed rules:
- ST item with a QFORM counterpart (QFORM F0 item whose selftest.id = the item; 24 of 180, factbook/firstaid/medlineplus): that fact's QFORM F5
  question (the answer-term form).
- Every other self-test item (ST180 rest + MAIN cm 40): the item's in_pack_facts[*].fact strings joined with ". " (the self-test's own gold
  sentences, paraphrased facts, not the verbatim pack quote).
- MAIN v0.1 (57 incl. 5 unscored): the question + " " + the first non-echo term of every grading.must_any group and the must_k terms
  (question carrying the answer terms, QFORM-F5-like). Items without grading terms: no map entry.
Arms: S0 = replace, S0Q = concat (oracle + original). Secondary (reported only): S0W = the ORIGINAL QUESTION replaced by O(i) in the request
(grounding sees the oracle too; QFORM's F5 setting).
STOP RULE: let ceiling = the better of S0 and S0Q. STOP (verdict NO-CEILING, no stage 1) if ceiling < +10 chunk facts on MAIN (42 -> 52)
AND < +20 own-article-kept on ST180 (vs ST base).

## STAGE 1 (mini, <= 25 min wall incl. setup): the 1.7B rewrite
Model qwen3-1.7b-q4km (sha b139949c...), llama-server b11010 CPU -t 4, ctx 2048, /v1/chat/completions, chat_template_kwargs
enable_thinking=false, temperature 0, seed 42, max_tokens 32, one request at a time on a warm server (kiln slot lock, disk >= 25 GiB,
never Docker/ollama/:8094). Inputs: the 180 ST + 97 MAIN questions (277). Output = first non-empty line, leading "Rewrite:"/quotes stripped;
empty -> no map entry (counted). Latency = HTTP wall per call; report p50/p90.
Exact prompt (system message), then 3 fixed few-shot turns, then the user question:
SYSTEM: "Rewrite the question as the single sentence that would answer it, keeping its key terms; do not answer; one line"
("do not answer" read as: do not reply to the user, output only the rewritten line.)
EX1 user: "Why does my phone battery die faster when it's cold outside?"
EX1 assistant: "A phone battery dies faster in cold weather because low temperature slows the lithium-ion battery chemistry and raises its internal resistance."
EX2 user: "Which planet has the most moons?"
EX2 assistant: "The planet with the most moons is Saturn, which has more confirmed moons than Jupiter."
EX3 user: "Can I use my laptop's USB-C charger for my phone?"
EX3 assistant: "A laptop USB-C charger can charge a phone safely because USB Power Delivery negotiates a voltage the phone accepts."
Arms: RW = replace (rewrite only), RW+Q = concat (rewrite + original). Replay + score as stage 0, plus kept-set changes (items whose kept ids
differ from base), health-family losses, crowding share.
GATE (per arm): (MAIN chunk >= 52 OR ST own-kept >= base + 20) AND health losses = 0 (MAIN + ST) AND rewrite latency p50 <= 2.0 s on the mini.
Best arm = a passing arm with the larger MAIN gain (tie: ST gain). No passing arm -> verdict NO-GATE, stop.

## STAGE 2 (only if the gate passes)
Engine hook needed for generation: own patch arms/retrieve-sweep/patches/QREWRITE.patch (env map, same semantics as the driver) on a scratch copy;
rs-SEFIX untouched. Generate the MAIN items whose kept list changed on the best arm (SEFIX-124 recipe, mini, seed 42, Succinct); judge vs the
existing SEFIX-124 s42 answers with judge.mjs judge.v1, Haiku 5.5-low, N 4, both orders, divergence-first (identical texts not judged), cap 300 calls.
Report confident errors per 100 (corr <= 1.5), better/worse/tie per item.
Decision: LEVER-CANDIDATE iff better >= worse + 3 AND no new confident error on a health item; else NOT-A-LEVER.

## Predictions (written before any run)
P1 ceiling >= +15 chunk facts on MAIN. P2 RW+Q gain >= half the ceiling gain (MAIN). P3 RW alone loses >= 1 base-delivered MAIN item
(exact-term items). P4 ST180 ceiling own-kept gain >= +20.
