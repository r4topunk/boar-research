# SAMPLE2-GATE criterion (frozen 2026-10-21 before any generation or gate run)

## Question
If the 1.7B writes two samples (seeds 42 and 43, same prompt) and the GATE17 groundedness gate keeps, per item, the one it scores as more supported (lower P(FAIL)), does U rise on the divergence-first stage-1 pool (pack set K0)? No refusal is added (unlike RU): the gate only chooses between two answers.

## System
- S42 = the mini K0 control answer (null-cal/control/pool-K0.json, sha256 fc98ad5c...; traces lp-screens/control lpctl-K0-main-s42 + null-cal/control poolctl-K0-st180-s42). The mini regenerates it byte-identically at seed 42 (GATE17: 97/97 + 37/37), so it is the seed-42 sample.
- S43 = the same requests (null-cal/tools/mkreq_pool.py, K0, ruler/ids/stage1-pool.ids sha256 151851bf...) with null-cal/null-s43.patch (sha256 428d9f36e54b785950dad18b3daccc67dd53aa1d0a0c188b2a328c38435ea83a; be/server.ts sends seed 43), run on the mini with --dump-prompts (tools/gen_dump.sh -> refuse-unsupported/tools/mini_gen_dump.sh unchanged, sha256 93590b26...).
- Gate = GATE17 build unchanged: Qwen3-1.7B Q4_K_M (b139949c) + gate17-lora-f16.gguf (d022352e) on llama-server b11010 CPU on the mini, card RUBRIC via gate17/tools/build_items.py render() (sha256 b1c12f8b...), gate17/tools/mini_gate.py (sha256 61f1133d...), P(FAIL) = pF / (pP + pF); tools/run_gate.sh = refuse-unsupported/tools/run_gate.sh with paths changed.
- Context = the S43 run's last dumped generate prompt's system text after "Context:"; used for S42 only when S43 retrieval.kept equals the control's (title, section, source).
- ELIGIBLE item = texts differ, both LLM answers (outputTokens > 0), neither a decline (null-cal/tools/labels.py is_decline), kept parity, context present. Response = answer minus the warning first line.
- Selection (tools/s2g.py select): eligible -> S43 iff round(P_FAIL(S43), 4) < round(P_FAIL(S42), 4), else S42 (ties keep seed 42). Not eligible -> S42.
- Tools sha256: s2g.py 81e5d137..., gen_dump.sh 1a8b0525..., run_gate.sh ad814aee..., judge_agg.sh 5fd59452....

## Judge
Haiku 5.5-low judge.v1-low, N = 4 shards, both orders, only on the composite answers that differ from the control (= the S43 picks; tools/judge_agg.sh, the run_pool.sh judge step). Cap 150 calls. Composite U via lp-screens/tools/agg_run.py --control (paired item bootstrap B 2000 seed 11).

## Reading rule (screen; GATE v2 bars do not apply: no null exists on this pool)
- PRIMARY: paired U delta (selected - S42 control) on the 87. **GO iff dU >= +0.03 AND CI low > 0** -> stage 2 on MAIN 97 under its own criterion. Otherwise NO-GO.
- Reported: CE-unwarned (labels.py) and refusals (R = decline or warned) selected vs control; share of shown LLM answers with a [n]; S43 picks / eligible; prompt tokens (unchanged by construction; the gate prompt tokens reported); decode cost = generated tokens S42 + S43 vs S42 (x2 nominal, measured); gate cost = gate prompt tokens and prefill ms per call (2 calls per eligible item); wall (mini job times).
- Not a null: the S43 sample alone is judged only where picked, so no s43-alone U is computed (cap).
- RD-1 conversion (fact present -> correct, judge correctness >= 4) on pool items with ruler/FACTPRESENT-2026-10-21.json K0 present (7 ids, as FEWSHOT-criterion), control vs selected. Report only.

## Rules
Dev ids only (no blind/, rnd/veil/, boar-eval/bench/v0.4). 0 Opus, 0 paid API, no phone, no llama.cpp change (the LoRA runs through the existing --lora path).

## Budget
calls_cap: Haiku 150
(Added 2026-10-21 after generation, before any judge call: the judge preflight needs this block; the cap of 150 was already frozen above. Previous sha256 in the commit history.)
