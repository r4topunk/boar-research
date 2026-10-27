# NOREPACK97 criterion (frozen before any generation or judge call)

Question: is `--no-repack` (llama-server, via BOAR_SERVER_EXTRA_ARGS="--reasoning off --no-repack") a safe cross-host pairing flag on the full MAIN 97?
System: LITEPACKS K1 tree (kiln-local/be-0cfd4a77-cut7-litepacks, answer.ts 0d1ac07d, adapter-litedecline.ts d53c1487), Qwen3-1.7B Q4_K_M, seed 42, temp 0.7, -t 4, LITEDECLINE_OFF=5, llama-server b11010. Requests: runs/req/lp-K1-{cm,v01}-s42 rows restricted to lp-screens/main-97.ids, runId nr97 (norepack97/req/nr97.requests.jsonl). No engine or llama.cpp edit.

## (a) Identity
Arms: MacBook no-repack and mini no-repack on MAIN 97 (one run each, sequential on each host, hosts in parallel).
PASS if answer text is byte-identical on >= 95 of 97 ids -> adopt `--no-repack` as the cross-host pairing flag (for text pairing only; it is not the shipped phone path).

## (b) Quality
Baseline = mini default K1 (traces/mini/lp-K1-{cm,v01}-s42.mini.traces.jsonl). Arm = mini no-repack. Judge only ids whose text differs (Haiku 5.5-low judge.v1-low, N=4 shards, both orders, cap 450 calls, 0 Opus, 0 paid); identical rows reuse the baseline judgment (delta 0). Baseline judgments come from lp-screens/control lpctl-K1-main-s42 where its text equals the mini-baseline text; the other baseline rows are judged in the same run as the arm.
Metrics as LITEPACKS: U (declined -> 0), CE = non-declined with correctness <= 1.5, warned = text starts with the CMP30OFF warning line. CE-unwarned = CE among answers that are not warned.
PASS (quality-neutral) if paired dU (arm - baseline, all 97, item bootstrap B 2000, seed 11) has point estimate within +-0.02, AND CE-unwarned count rises by < 3 (i.e. <= +2 of 97; "up by >= 3/100" fails). The CI is reported; a CI excluding 0 is flagged but does not by itself change the verdict.
Verdict: (a) and (b) both pass -> `--no-repack` quality-neutral cross-host flag. Otherwise report the failing clause; no further claims.

## Outputs
arms/litepacks/NOREPACK97.md (<= 40 lines), aggregates/norepack97.json, one QUEUE row, commit to rnd (own paths only).
