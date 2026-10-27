# Arm G stage 2: Qwen3-1.7B answers, CTL (v2 packs) vs ARM (v3proto, packDense2 true) on the changed-context items (exploratory)

216 items; changed-context 129 = judged 100 (answers differ) + 18 with identical answer text (dU 0 by construction) + 11 not judged (cap); unchanged-context 87 (identical answers, reuse CTL). judge.v1 Haiku 5.5-low N 4 both orders. CIs item bootstrap B 2000 seed 11.

| arm | n | U [CI] | corr | use | CE (corr<=1.5) | warned | declined | instant | out tok | total ms |
|---|---|---|---|---|---|---|---|---|---|---|
| CTL | 100 | 0.398 [0.333, 0.472] | 2.67 | 2.02 | 25 | 39 | 0 | 14 | 35 | 3070 |
| ARM | 100 | 0.524 [0.454, 0.600] | 2.96 | 2.34 | 17 | 34 | 0 | 14 | 36 | 3352 |

Diluted (indicative): dU over all changed-context items +0.091; over all 216 +0.054.
Paired ARM - CTL on the judged changed items: dU +0.125 [+0.049, +0.204]; fact-cluster CI [+0.044, +0.222]; d corr +0.29 [+0.05, +0.54]; d use +0.31; item score better ARM/CTL/tie = 56/31/13.

## Gold kept (CTL/ARM) x U on the changed items
| gold kept ctl/arm | n | U ctl | U arm | dU | CE ctl | CE arm |
|---|---|---|---|---|---|---|
| ctl=1,arm=1 | 17 | 0.759 | 0.618 | -0.141 | 0 | 2 |
| ctl=1,arm=0 | 2 | 1.667 | 0.606 | -1.061 | 0 | 0 |
| ctl=0,arm=1 | 24 | 0.233 | 0.704 | +0.471 | 10 | 2 |
| ctl=0,arm=0 | 54 | 0.337 | 0.421 | +0.084 | 14 | 12 |
gold-kept unknown (kept list differs from the replay, non-empty): 3 items

## Per form (changed items; indicative)
| form | n | U ctl | U arm | dU |
|---|---|---|---|---|
| F0 | 12 | 0.436 | 0.680 | +0.244 |
| F1 | 12 | 0.354 | 0.354 | +0.001 |
| F2 | 15 | 0.266 | 0.453 | +0.187 |
| F3 | 9 | 0.300 | 0.394 | +0.094 |
| F4 | 16 | 0.362 | 0.570 | +0.208 |
| F5 | 8 | 0.671 | 0.758 | +0.087 |
| F6 | 13 | 0.342 | 0.506 | +0.163 |
| F7 | 15 | 0.594 | 0.561 | -0.033 |

## Per pack (changed items; indicative)
| pack | n | U ctl | U arm | dU | CE ctl | CE arm |
|---|---|---|---|---|---|---|
| boar-factbook | 32 | 0.213 | 0.468 | +0.255 | 19 | 10 |
| boar-firstaid-en | 25 | 0.407 | 0.583 | +0.176 | 4 | 3 |
| boar-medlineplus-en | 43 | 0.524 | 0.529 | +0.005 | 2 | 4 |

All 216 (from the traces): prompt tokens ctl 306 / arm 330; out tokens 29.6 / 30.8; total ms 2570 / 2709; warned 53 / 52; declined 0 / 0.
Gold kept in the run (all 216; replay flag where kept titles match, unknown otherwise): ctl {'replay': 46, 'run_known': 45, 'run_unknown': 1}, arm {'replay': 69, 'run_known': 67, 'run_unknown': 5}.
Not judged: ['qf-boar-factbook-02-F8', 'qf-boar-factbook-03-F8', 'qf-boar-factbook-05-F8', 'qf-boar-factbook-06-F8', 'qf-boar-factbook-08-F8', 'qf-boar-firstaid-en-08-F8', 'qf-boar-medlineplus-en-01-F8', 'qf-boar-medlineplus-en-03-F8', 'qf-boar-medlineplus-en-05-F8', 'qf-boar-medlineplus-en-06-F8', 'qf-boar-medlineplus-en-07-F8']
