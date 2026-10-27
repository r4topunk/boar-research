# ORACLE-REAL criterion (frozen 2026-10-21 before any generation; coordinator subagent)

Question: on real v0.1 dev items whose key fact sits in an installed K3 pack chunk, does putting that chunk first in the 1.7B's kept context lift the answer? This is the 1.7B's reading ceiling when retrieval is perfect (ORACLE-ST measured +0.095 for the 4B on the self-tests; FACTPRESENT self-test cell (a) +0.139 for the 1.7B).

## Items (frozen)
- 30 v0.1 ids, `items.ids` (sha256 29e2bceccc22048c...): lan-cmp-005 lan-exp-001 lan-exp-002 lan-exp-003 lan-exp-004 lan-exp-005 lan-exp-007 lan-hlt-001 lan-hlt-002 lan-hlt-003 lan-ref-002 lan-ref-003 lan-rsn-001 lan-rsn-003 lan-rsn-004 lan-rsn-006 vit-cry-002 vit-cry-003 vit-cry-004 vit-cry-005 vit-cry-006 vit-cry-008 vit-cry-009 vit-cry-010 vit-cry-011 vit-hlt-001 vit-hlt-002 vit-hlt-003 vit-hum-004 vit-trv-003.
- Rule: keyed v0.1 items (FACTPRESENT) with a gold chunk labelled Y or P in `gold-labels.tsv` (sha256 223ac510c45ce1b9...), minus the 7 whose LITEPACKS K3 trace is answered by a deterministic layer (Wikidata facts; the 1.7B never runs). Gold = ruler/RAG-FUNNEL rule v3 (lexical) read and labelled by hand (29/39 Y/P), plus 6 hand-found chunks for items whose lexical gold was N or absent (all read). 17 Y, 13 P. No cooking/money self-test qualifies (their facts are in qa-* packs no K-set installs).
- n 30 < 35: the hypothesis's own rule labels the result **indicative**. MDE at n 30 is about 0.05-0.06.

## Arm (frozen)
- System = the LITEPACKS 1.7B K3 system (adapter be/adapter-litedecline.ts, LITEDECLINE_OFF=5, Qwen3-1.7B Q4_K_M, --reasoning off, seed 42, kit K3 = crypto + wikivoyage + simplewiki + factbook + medlineplus + firstaid), generated on the Mac mini (lp-screens mini_gen.sh, slot lock, base tree <runner>/kiln/be-0cfd4a77-cut7-litepacks, answer.ts 0d1ac07d...).
- Change = `oracle.vs-litepacks.patch` (sha256 5b4d204a25707eaf...), env `BOAR_ORACLE_FILE=tools/oracle-file.json` (sha256 ff3eba76a02be5f6...; item -> {question, pack, chunk_id}). After the engine has built its kept list (compress, grounding, X2b appends), the gold chunk (full chunk text, as the append path formats it) becomes passage [1]; if it was already kept it is moved there; the engine's other kept passages follow in order; while the kept passages exceed the context cap (compress budget + HEADPASS_BUDGET_TOKENS, ceil(chars/4) each) the last non-oracle passage is dropped. Prompt wording is untouched. Absent env = byte-identical shipped path.
- Requests `runs/req/oracle-K3-v01gold-s42.requests.jsonl` (sha256 6698bda5f2b20c94...) = the LITEPACKS lp-K3-v01-s42 requests of the 30 ids, runId/arm renamed.
- MacBook stub replay (0 generation) before freezing: oracle off reproduces the LITEPACKS K3 kept titles 30/30; oracle on puts the gold chunk at [1] on 28/28 items that reach a generate call (2 health items, vit-hlt-001/002, answer extractively from the sources; the oracle changes their sources only); the cap dropped 0 passages.

## Controls
- **Primary: the existing mini K3 traces** `arms/refuse-unsupported/traces/ru-K3-dump-s42.traces.jsonl` (sha256 3ee6cceffd19a235...; same host, same base tree and requests; the mini decodes deterministically run to run, LP-SCREENS 37/37). Same host as the arm, per the LP-SCREENS rule (arms compare against the mini control).
- **Secondary (report only): the MacBook LITEPACKS K3 traces** `arms/litepacks/traces/lp-K3-v01-s42.traces.jsonl` (sha256 2567e0895a46d21b...) with their existing judgments (mini vs MacBook sampling differs at temperature 0.7: byte-identical texts on 7/30 items).

## Judge
- Haiku 5.5-low (judge.v1-low via deepthink/tools/shard_judge.sh, N = 4 shards, both orders, seed 7). An answer text byte-identical to an already judged text (LITEPACKS K0/K3 v0.1 judgments) reuses those rows; every other text of the arm and of the primary control is judged. Expected: control 23 texts (46 calls), arm <= 30 texts (<= 60 calls). **Cap 250 Haiku calls**; 0 Opus, 0 paid.

## Readings (all on the 30; U per item = mean of the 3 judge dims, mean of both orders; declined = 0; U = ratio of sums vs the reference; paired item bootstrap B 2000, seed 11, 2.5/97.5 pct)
1. **dU = U(oracle) - U(mini K3 control)**, 95 % CI = the 1.7B's reading ceiling with perfect retrieval on real items. Also vs the MacBook K3 control.
2. CE-unwarned: share of non-declined answers with judge correctness <= 1.5 that do not start with the warning line ("Not found in this phone's offline library"), oracle vs control.
3. Support share: share of oracle answers that cite [1]; share citing any [n].
4. Fraction of the self-test gain reproduced = dU / 0.139 (FACTPRESENT self-test cell (a), 1.7B K3-K0, oracle rule).
5. Subgroups (report only, no verdict): fact already kept in K3 (RAG-FUNNEL S4/S5) vs not kept (S1-S3); Y vs P; lexical vs manual gold.

## Verdict rules
- **Kill (brief): dU < +0.03 -> reading, not retrieval, is the binding stage for the 1.7B on real items** (perfect retrieval does not lift it).
- Hypothesis kill (reported next to it): CI high < +0.05, or dU < +0.0475 (half of ORACLE-ST's +0.095).
- dU >= +0.03 with CI low > 0 -> retrieval is the binding stage on these items; the ceiling for retrieval/keep levers on real items is the dU.
- Otherwise: inconclusive at n 30 (indicative).

## Rules
Dev sets only (bench v0.1 public ids). No v0.4, no blind/, no rnd/veil, no Opus, no paid API, no phone, no maintainer contact. Generation on the mini only (>= 25 GiB free; Docker, ollama and :8094 untouched). Outputs: `ORACLE-REAL.md`, `traces/`, `judgments/`, `aggregates/`, `PLAN.md` (resume commands).
