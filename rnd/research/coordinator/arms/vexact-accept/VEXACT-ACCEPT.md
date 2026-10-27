# VEXACT-ACCEPT: acceptance test on the 11 public bounty questions (2026-10-19/20)

TL;DR: `tools/run.sh` runs a one-command acceptance test. It sends the 11 public V-exact questions through the claim engine (cut 7 + HEADPASS-X2b, Qwen3-4B-2507, prompt D4, claim kit, device location + area tile), has Haiku judge the 5 judged items, and scores the 6 venue items against OSM gold. **Baseline (2 seeds): judged ratio 0.475 (item CI 0.280-0.786), venues 6/6 on both seeds, all 3 GPS answers name the right city.** The same traces would have scored 0.491 under the cut 2 Haiku judge; cut 2's published figure was 0.510 under Opus. The criterion was frozen before the baseline: `VEXACT-ACCEPT-criterion.md`, sha256 **93a7b8ca**3958b45f7207a06c2e989bc76ec83f943a2d866258d38fde6c763f45, committed in 815420b2 before any generation. Generation is deterministic: a second run of the identical config reproduced all 22 answers byte-for-byte, so delta = 0.000 and the verdict is ACCEPT. That run validates the reuse and verdict path.

```fish
# baseline (done) / a candidate pack / a candidate facts table / the engine's own Succinct prompt instead of D4
bash tools/run.sh --label baseline --wait-chainwhen
bash tools/run.sh --label cand-foo --pack boar-foo-en=<runner>/shared-data/packs/wave3/boar-foo-en.sqlite --baseline baseline --own-gate PASS
bash tools/run.sh --label facts-r9 --facts <runner>/kiln/facts-r9/facts.v1.json --baseline baseline --own-gate PASS
bash tools/run.sh --label eng --prompt engine --baseline baseline
```
Run time is about 2 min of generation per seed on the mini (4 model answers per seed, each about 20-30 s at 23-25 tok/s, plus 7 instant answers), then about 30 s of judging per seed. Haiku calls: 20 for a full run, and 0 for any answer identical to the baseline's.

## Acceptance rule (frozen, 93a7b8ca)
A candidate is accepted only if all three hold on a valid run (11 traces per seed, 0 errors, and under D4 every model answer's prompt rewritten):
- **A1:** judged ratio ≥ baseline − 0.03.
- **A2:** venues 6/6 on each seed.
- **A3:** the asset's own frozen gate passes. `--own-gate` takes PASS, FAIL or NA, and NA means not accepted.

A judged answer that is byte-identical to the baseline's reuses the baseline's judgment rows, so the delta comes only from items the asset changed.

## How the harness is built (no change to the engine tree)
| piece | what |
|---|---|
| `tools/mkreq.py` | Builds requests in the X2b request shape: arm cut7-headpass-x2, packHeadPass a2 + packDense2 append-budget, kit boar-crypto + boar-wikivoyage-en (+ `--pack id=sha256`), android 12 GB. GPS items keep their lat/lon. |
| `tools/mini_gen.sh` | Runs on the mini. It checks the tree, adapter, X2b and kit-vexact sha256s, that the detector on :8094 is up (it never starts or stops it), that disk is ≥ 25 GiB and that port 8193 is free. It then starts its own llama-server b11010 on **:8193** with the adapter's own args and runs the adapter with `--server-url` and `--places` (kit-vexact, 5 files). The server is killed on exit. |
| `tools/vxa-hook.mjs` | Loaded with `NODE_OPTIONS=--import` into the adapter process. (1) D4: it rewrites each answer request exactly as PACKREAD's build.py did. The system text before " You are BOAR, an offline AI research app" becomes D4 sys + D4 context instruction (when a context is present), the "(Response style: …)" reminder becomes D4 rem, and max_tokens becomes 1024. Context, identity text and question stay byte-identical. Each rewrite is logged to `*.rewrites.jsonl`. (2) `--facts`: the engine's `./facts.v1.json` import resolves to the given file through `module.registerHooks`. |
| `tools/d4.json` | D4 strings exported from honestprompt/tools/prompts_lib.py. They are identical to the mini's prompt3m copy used by PACKREAD (checked field by field). |
| `tools/reuse.py`, `tools/agg.py` | Judgment reuse, then the aggregate: pooled raw ratio Σboar/Σref over both orders, items and seeds, which reproduces cut 2's 0.510 from its Opus rows. Also item-bootstrap CI, paired delta and the verdict, written to `runs/<label>/{result.json,RESULT.md}`. |
| `tools/fake_server.mjs` | A stub llama-server for plumbing smoke tests while another arm owns the CPU. |

Smoke test with the stub, run before the baseline (it used no CPU while CHAINWHEN was running). 12 requests, 0 errors. The 4 model-routed answer requests were all rewritten to D4 with max_tokens 1024. The venue path returned 6/6, with the same counts as cut 2 (9/9/9/8/9/7). The facts override worked: with a stub table where Japan's capital was changed, "What is the capital of Japan?" was answered "Stubtown" instead of "Tokyo". The smoke files were then deleted from the mini.

## Baseline results (runs/baseline/, judge Haiku 5.5-low)
| item | cut 2 Opus (published) | cut 2 Haiku re-judge | **baseline s42** | **s43** | **pooled** | route |
|---|---|---|---|---|---|---|
| vx-001 Tell me about Japan | 0.36 | 0.345 | 0.333 | 0.333 | **0.333** | fast, model |
| vx-002 quantum-resistant signatures | 0.53 | 0.517 | 0.433 | 0.467 | **0.450** | fast, model |
| vit-hum-001 Mozi universal love | 0.56 | 0.473 | 0.464 | 0.483 | **0.474** | fast, model, no good source (caution line) |
| vit-hum-004 why Gríma kills Saruman | 0.20 | 0.200 | 0.200 | 0.200 | **0.200** | fast, model: wrongly says Gríma does not kill Saruman |
| vit-trv-004 Paris-Rome walk and back | 0.94 | 1.043 | 1.091 | 1.043 | **1.067** | instant estimate (2,900 km) |
| **judged ratio** | **0.510** | **0.491** | 0.471 | 0.479 | **0.475** (CI 0.280-0.786) | |

| venues (OSM gold, ≥ 3 real) | cut 2 | baseline s42 | s43 |
|---|---|---|---|
| pass | 6/6 | **6/6** | **6/6** |
| GPS answers naming the right city | 2/3 | **3/3** | **3/3** |
| real vegan venues per item (vx-003/4/5, food-001/002/006) | 9/9/9/8/9/7 | 9/9/9/8/9/7 | 9/9/9/8/9/7 |

How to read this: against the cut 2 traces under the same Haiku judge, the current claim engine with D4 scores −0.016 (0.475 vs 0.491). That is within one item's noise at n = 5. Most of the gap is vx-002 (−0.067; I did not audit why). The Paris-Rome answer is now an instant estimate and scores slightly higher. The Gríma item is wrong in every version and is the biggest single target on this set. The venue path is unchanged and LLM-free, so A2 can only fail if an asset changes routing or places. Speed on the mini CPU: first token 3.0-8.0 s, full answer 21-29 s for model answers, and under 30 ms for instant and venue answers.

## Deviations
1. The task asked for the engine to run with D4. The cut 7 tree has no prompt switch, so D4 is swapped in at the request level by an in-process fetch hook (`vxa-hook.mjs`). This is the same transformation PACKREAD applied to the dumped prompts, and the engine tree was not changed. `--prompt engine` turns the hook off.
2. The task said to compare with cut 2's 0.510, which was judged by Opus. I also re-judged the cut 2 traces with Haiku (20 calls; `runs/cut2-haiku/`) so the comparison uses the same judge. Both numbers are reported.
3. I added judge reuse for byte-identical answers to the frozen criterion. It was frozen before the baseline. It removes judge noise from items an asset does not touch.
4. One extra run (`runs/selfcheck/`, 8 model generations, 0 judge calls) re-ran the baseline config to test determinism and the verdict path. Result: 22/22 identical, delta 0.000, ACCEPT.
5. The CHAINWHEN wait took 50 min (135 → 236 lines). Generation started at 23:56, after its 236th line. Its :8191 server was already gone at that point.

UNKNOWN: whether the Haiku judge's ±0.03 noise on a changed item is small enough for A1 on its own. If a candidate lands within 0.03 of the line, run it on seeds 44/45 as well before deciding. Whether a candidate pack whose kit sidecar lacks chunk_vecs gets the X2b dense half. It does not on the claim kit (KIT-X2B), so a pack's X2b behaviour depends on its file.
