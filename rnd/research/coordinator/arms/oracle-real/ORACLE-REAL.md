# ORACLE-REAL (2026-10-21): the key-fact chunk placed first lifts the 1.7B by only +0.015 on real v0.1 items -> KILL: reading, not retrieval, binds

TL;DR (criterion `ORACLE-criterion.md` sha256 16f32030, committed f5a61d78 before generation; Haiku 5.5-low judge.v1-low N 4 both orders; 98 Haiku calls of the 250 cap; 30 generations on the mini; 0 Opus, 0 paid)
- **dU oracle - mini K3 control = +0.015 [-0.029, +0.059]** (U 0.427 vs 0.412, n 30). That is **10 % of the self-test cell-(a) gain** (+0.139). Brief's kill (dU < +0.03) is **met**. Hypothesis kill: dU < half of ORACLE-ST (+0.0475) is also met; CI high (+0.059) is not below +0.05. **n 30 < 35, so the result is indicative** (the hypothesis's own size rule).
- vs the MacBook K3 control: +0.002 [-0.045, +0.051]. Host noise mini - MacBook on the same system: -0.012 [-0.042, +0.014].
- **CE-unwarned:** 1/30 oracle vs 3/30 mini control (1/30 MacBook). Warned answers: 8 vs 10 (13 MacBook). Declined: 0 everywhere.
- **Support:** oracle answers cite [1] on 15/30 (control 5/30); any citation 21/30 vs 18/30. **8/30 oracle answers still open with the memory warning** with the gold chunk in slot [1] (e.g. Montenegro, Kyoto, cheetah, quadratic funding): the 1.7B ignored the passage and the engine flagged it uncited.
- **Reading:** with retrieval made perfect for these items, the 1.7B's answers barely move. Even with the fact first, real multi-part questions get partial answers, misreads, or uncited memory answers. For the 1.7B at 8 GB, the binding stage on real items is **reading**. Retrieval/keep levers (RAG-FUNNEL S3, 17 items) have a real-item ceiling of about +0.015 x (items reached), not the self-test +0.139.
- **Post-hoc leads (not in the verdict, small n):**
  - Manual gold (6 items whose chunk is a clean key-facts / lead passage: Singapore, Sahara, Greenland, FOCIL, EIP-7251, Privacy Pools): +0.106 [+0.054, +0.159].
  - Lexical gold (24): -0.009. Y labels +0.018, P +0.008.
  - Fact not kept in K3 before (7): +0.037 [-0.136, +0.155]. Fact already kept (23): +0.008.
  - So a clean, dense fact passage may help where a noisy lexical one does not. This is a lead on chunk quality, not retrieval; n 6.

## Method (as frozen)
- Items: 30 keyed v0.1 ids with a hand-verified gold chunk (17 Y, 13 P; 24 lexical, 6 manual) in a K3 kit pack, minus 7 that a deterministic layer answers (`gold-labels.tsv`, `items.ids`).
- Arm: LITEPACKS 1.7B K3 system on the mini, plus `oracle.vs-litepacks.patch` with env `BOAR_ORACLE_FILE`. After the engine's keep step the gold chunk becomes passage [1] (moved if already kept), and the other kept passages follow. The cap never bound (0 dropped). The prompt wording is unchanged. Trace codes are `oracle:first` on 30/30.
- Primary control: the existing mini K3 traces (ru-K3-dump-s42). Its 23 texts were judged (46 calls); 7 reuse identical judged texts.
- Arm judging: the 26 oracle texts without a judged twin (52 calls). 26/30 oracle answers differ from the mini control.
- U = ratio of sums (3 dims, both orders), paired item bootstrap B 2000, seed 11.

## Per item (U item = s/sref; corr = judge correctness, both-order mean; c1 = cites [1]; W = warned)
| item | gold | K3 funnel | control U / corr | oracle U / corr | |
|---|---|---|---|---|---|
| lan-cmp-005 | P | S3 | 0.25 / 1.0 | 0.35 / 2.0 | |
| lan-exp-001 | Y | S4 | 0.53 / 4.0 | 0.59 / 3.5 | c1 |
| lan-exp-002 | Y | S5 | 0.60 / 5.0 | 0.57 / 4.0 | W |
| lan-exp-003 | Y | S5 | 0.72 / 4.5 | 0.63 / 4.0 | c1 |
| lan-exp-004 | Y | S5 | 0.53 / 4.0 | 0.37 / 2.5 | W |
| lan-exp-005 | Y | S5 | 0.33 / 3.0 | 0.53 / 4.0 | c1 |
| lan-exp-007 | Y | S4 | 0.40 / 2.0 | 0.45 / 2.5 | |
| lan-hlt-001 | Y | S4 | 0.41 / 2.5 | 0.54 / 3.5 | c1 |
| lan-hlt-002 | Y | S5 | 0.60 / 5.0 | 0.60 / 5.0 | c1 |
| lan-hlt-003 | Y | S5 | 0.53 / 4.0 | 0.47 / 3.0 | c1 |
| lan-ref-002 | P | S5 | 0.67 / 5.0 | 0.69 / 5.0 | |
| lan-ref-003 | P | S4 | 0.50 / 3.5 | 0.40 / 2.0 | c1 |
| lan-rsn-001 | P | S4 | 0.43 / 2.5 | 0.43 / 2.5 | |
| lan-rsn-003 | P | S4 | 0.21 / 1.0 | 0.21 / 1.0 | W |
| lan-rsn-004 | P | S4 | 0.20 / 1.0 | 0.20 / 1.0 | W |
| lan-rsn-006 | Y | S5 | 0.60 / 5.0 | 0.57 / 4.5 | c1 |
| vit-cry-002 | Y | S4 | 0.23 / 1.0 | 0.43 / 3.0 | c1 |
| vit-cry-003 | P | S4 | 0.27 / 1.5 | 0.24 / 1.0 | W |
| vit-cry-004 | P | S4 | 0.23 / 1.5 | 0.33 / 2.0 | |
| vit-cry-005 | P | S1 | 0.27 / 2.0 | 0.38 / 2.5 | c1 |
| vit-cry-006 | P | S4 | 0.33 / 2.0 | 0.20 / 1.0 | W |
| vit-cry-008 | Y | S4 | 0.61 / 3.0 | 0.61 / 3.0 | c1 |
| vit-cry-009 | P | S3 | 0.21 / 1.0 | 0.25 / 1.5 | |
| vit-cry-010 | Y | S3 | 0.27 / 2.0 | 0.47 / 3.0 | c1 |
| vit-cry-011 | P | S4 | 0.27 / 2.0 | 0.29 / 2.0 | W |
| vit-hlt-001 | Y | S3 | 0.68 / 3.5 | 0.28 / 2.0 | c1 (health extractive answer quoted the travel chunk) |
| vit-hlt-002 | Y | S3 | 0.70 / 4.5 | 0.70 / 4.5 | |
| vit-hlt-003 | Y | S3 | 0.29 / 2.0 | 0.50 / 3.0 | c1 |
| vit-hum-004 | P | S4 | 0.20 / 1.0 | 0.20 / 1.0 | W |
| vit-trv-003 | Y | S4 | 0.22 / 1.0 | 0.31 / 2.0 | c1 |

## Caveats
- n 30 (indicative). One seed. The Haiku 5.5-low judge compresses gaps. Dev items only (bench v0.1 public).
- 13/30 gold chunks are P (they hold half of the key fact). The 23 'already kept' items had the fact in context before; on them the arm only moves it to [1] in full text.
- For the 2 health items (vit-hlt-001/002) the answer is an extractive excerpt, not a 1.7B generation; the oracle changes the excerpt source.
- Gold selection is by lexical rule + hand reading, not by the self-tests' chunk-id truth.

## Files
`ORACLE-criterion.md` (+ .sha256), `ORACLE-budget.md` (the frozen cap in preflight form), `gold-labels.tsv`, `items.ids`, `oracle.vs-litepacks.patch` (+ .sha256), `tools/{build_inputs.py, oracle-file.json, run_oracle.sh, oracle_agg.py}`, `traces/oracle-K3-v01gold-s42.traces.jsonl`, `judgments/{ctlmini-K3-v01, oracle-K3-v01}.judgments.jsonl`, `aggregates/oracle-real.json` (sha256 53ece0eb...), `runs/logs/calls.ledger` (98 calls).
