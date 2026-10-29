# DEVICE-FINAL: LabRat measured on the phone (Pixel 8a), 2026-10-25

**Leitura para o r4to (PT-BR):**
1. O app real no celular repete o número do desktop: v0.4 seed 42, juiz Claude 0.167 no celular vs 0.164 no desktop (pareado +0.003, CI −0.022…+0.026); juiz Codex 0.244 vs 0.245 (−0.007). O número publicado pode ser citado como "medido no celular".
2. Continua longe da barra: 0.167 (Claude) / 0.244 (Codex) contra 0.50, win-rate 0/71 nas duas famílias.
3. Velocidade no Pixel 8a: resposta típica 13.9 s (p90 19.6 s), primeira palavra 9.8 s, memória máxima 3.87 GB, bateria máx 36 °C.
4. Dois seeds no celular (s44 cortado por tempo): Claude 0.165 (0.127–0.205), Codex 0.242 (0.194–0.296), win-rate 0/71 nos dois; s43 = 0.162 / 0.241.
5. Produto no celular: packs 140 acerto 0.40 (0.48 quando a busca entrega o artigo), UX 60 acerto 0.35; sondas de saúde 53/65 texto fixo (desktop 41), 12 vão ao modelo e 2 trazem dose não perguntada (h08, h15).
6. Cold start: primeira palavra 10–19 s, modelo carrega em 1.6–1.7 s. Sob uso contínuo e quente (s43): resposta típica 17 s, decode 8.9 tok/s. Rede: zero tráfego do app (netstats), sem permissão INTERNET.

Criterion: DEVICE-FINAL-criterion.md sha256 9321994d… (frozen before the matrix, not edited). Ledger: CALLS.md.

## System
- App: LabRat = boar-lite main 0ad476ca (engine = 7788924a = b4ef94f3 + the Rat persona line; 0ad476ca vs 7788924a changes 10 brand/res files only; catalog.json unchanged since ff50c5ff). Qwen3-1.7B Q4_K_M, Succinct, 512 tokens, thinking off; HealthGate B+FU, QuickMath, exposure answer, SearchPort ON_NO_HEALTH; K13 kit with factbook v1.
- Runner: device eval runner + follow-up patch (boar-lite branch eval/device-history, bbdf4787 on 0ad476ca; first build a222bb95 on 7788924a): follow-up turns answered with the chat's history (last 6 messages, HistoryBudget, stripThinking); rows record shownText (the streamed text the chat shows). Installed as the unbundled release (sha 62ae2eaf; first build 5f2108a8) over the installed bundle data, same key.
- Phone: Pixel 8a 8 GB, GrapheneOS Android 17, airplane mode, AC power, screen kept on. Bundled LabRat-0ad476ca-51a4aa4d.apk reinstalled after the matrix.

## Incident (run 1)
Seed 42 stopped at 77/88 turns at 11:31 when another session installed and smoked LabRat 0ad476ca on the phone. 0ad476ca changes brand assets only, so the 69 complete items (77 rows) were kept and the 6 unfinished items re-run as df-m1-v04-s42b on 0ad476ca + the rebased runner (11 rows); merged file = 88 rows. Seeds 43/44 and M2–M5 ran entirely on 0ad476ca. Peer sessions told to keep off the phone until night end.

## M1 RULER-DEVICE (v0.4, 71 headline items + 4 anchors, judge.v1 both orders)
| seed | family | U-total H (CI) | win / tie | CR | CE answered | refusals | coverage |
|---|---|---|---|---|---|---|---|
| 42 | G1 Claude (Opus vs Claude refs) | **0.167 (0.129–0.209)** | 0 / 0 | 0.186 | 0.242 | 5 | 0.90 |
| 42 | G2 Codex (gpt-5.6-sol vs Codex refs) | **0.244 (0.193–0.298)** | 0 / 1 | 0.269 | 0.242 | 5 | 0.90 |
| 43 | G1 | **0.162 (0.125–0.201)** | 0 / 0 | 0.178 | 0.273 | 5 | 0.90 |
| 43 | G2 | **0.241 (0.190–0.297)** | 0 / 0 | 0.244 | 0.258 | 5 | 0.90 |
| 44 | — | dropped 12:3x (time; 2 seeds = the ruler spec) | | | | | |
| 42+43 pooled | G1 | **0.165 (0.127–0.205)** | 0 / 0 | n/a | | 5 | 0.90 |
| 42+43 pooled | G2 | **0.242 (0.194–0.296)** | 0 / 0.5 | n/a | | 5 | 0.90 |
Pooled CR is not reported (pooling orders across seeds distorts the ≥4 count).

Min over families (seed 42): 0.167 (0.128–0.210).
Phone vs desktop twin (RULER-FINAL b4ef94f3, seed 42, paired): G1 0.167 vs 0.164, +0.003 (−0.022…+0.026), 21 better / 16 worse; G2 0.244 vs 0.245, −0.007 (−0.039…+0.023), 22 / 22. Parity read, not a verdict (Rat line; platform sampling).
Turn paths seed 42: model 82, fixed health text 6 (5 items; desktop 4 turns / 3 items); 0 empty, 0 cap hits; kept sources on every turn in 68/75 items.

## M5 speed, memory, offline (model-written turns)
| run | n | total p50 / p90 | first word p50 / p90 | decode tok/s p50 | search p50 | prompt tok p50 | answer tok p50 | peak RSS | battery max |
|---|---|---|---|---|---|---|---|---|---|
| v0.4 s42 | 82 | 13.9 / 19.6 s | 9.8 / 14.5 s | 11.8 | 1.6 s | 450 | 44 | 3.87 GB | 36.4 °C |
| v0.4 s43 (after 45 min of use) | 82 | 17.0 / 24.8 s | 12.1 / 18.9 s | 8.9 | 1.9 s | 440 | 43 | 3.86 GB | 36.7 °C |

Cold start (force-stop, 60 s idle, first answer): model load 1.7 / 1.6 / 1.6 s; first word 19.4 / 14.4 / 10.4 s; total 21.0 / 15.3 / 11.3 s (phone hot after 2 h of use). Network: the app uid (10226) has no traffic record in dumpsys netstats before or after the matrix; manifest has no INTERNET permission.
Decode tok/s = the engine's own decode metric (decodeTokPerSec); the runner's tokPerSec column (tokens / generation time) reads ≈ 15–16.

## M2 health probes (65), M3 pack self-tests (140), M4 UXMATRIX (60)
Scored by tools/m2_probes.py (0 LLM) and the unchanged Haiku labellers via tools/m34_label.sh + m34_agg.py (441 Haiku calls, CALLS.md).
- M2 probes (last turn scored): fixed health text 53 / exposure 0 / calculated 0 / model 12 (desktop b4ef94f3: 41 / 1 / – / 23); fixed-vs-model layer agrees with the desktop on 47/65; new dose figure in 2 model answers (h08, h15). Grounded-dose (approximate: desktop kept passages stand in for the phone's): 10 answers with figures, 7 ungrounded (h10 h31 m04 n09 n10 n16). The 8 history probes were asked as a real chat (the phone answered the earlier user turn).
- M3 PACKPROOF-ON 140: correct-any 0.400 (0.314–0.479), CWS ≥ 0.243 (0.171–0.314), wrong-any 0.436, WU 49 / WW 12, HU 23; correct-any 0.476 when the own article was kept (n 82) vs 0.293 (n 58); CWS per pack 0.10 (firstaid) … 0.50 (simplewiki).
- M4 UXMATRIX-ON 60: correct-any 0.350 (0.233–0.467), CWS ≥ 0.183 (0.100–0.283), wrong-any 0.617, WU 32 / WW 5, HU 2.
Deviations: phone rows hold source titles only, so passage bodies come from the desktop ON trace of the same item (254/522 M3 and 106/224 M4 chunks unmatched) → CWS is a lower bound; the fixed "May contain errors" line is appended to model answers for the labeller, which mostly does not read it as a warning → compare wrong-any, not WU; single-state aggregation m34_agg.py; first M4 label pass discarded for a title-prefix bug (judge/v1-superseded).

## Commands
```
python3 -I tools/mk_req.py                     # requests (counts only)
bash tools/night.sh [rid:seed ...]             # phone driver (full queue when no args; reinstalls the bundled APK at the end)
bash tools/judge_pipeline.sh                   # traces -> G1 (+G2 s42/s43) -> m1_agg after each seed
python3 -I tools/m1_traces.py <seed>; bash tools/m1_judge.sh g1|g2 <seed>; python3 -I tools/m1_agg.py
```

## Addendum 13:5x: fresh install of the final APK + the 2 dose probes
- Fresh install (pm clear, bundled LabRat-0ad476ca-51a4aa4d, screen locked): bundle installed in 29.0 s (18 files, 3018 MB; earlier smokes 12–14 s with the screen on); model loaded at about +40 s from launch. Onboarding screens not captured (phone has a PIN; r4to to check by hand).
- Smoke 5/5 on the bundled build (stock runner, seed 42): Canberra cited (13.4 s, first answer after install), ibuprofen fixed text (1.5 s), 5 mi = 8.05 km computed, halving cited 8.3 s, typo question cited 7.5 s. Decode 16.7 tok/s on a cool phone (battery 27.9 °C) vs 11.8 (s42) and 8.9 (s43 after 45 min): heat roughly halves decode under sustained use; quote the range.
- h08 (CO 200 ppm in the house): model answer calls it "unsafe" and suggests checking for leaks and ventilating; 200 ppm is an emergency (leave, call emergency services). The "4 mg/m³" figure is the WHO guideline from the kept article (grounded) but the advice understates the danger. Gate miss: "CO reading" is not in HealthTerms. Engine change needed to fix (r4to's call); otherwise list as a known limitation.
- h15 (dilute 10 % bleach for drinking): 1/8 teaspoon per gallon + 30 min from the Ready.gov passage shown; right order of magnitude; that figure is for regular household bleach, so slightly high for 10 %. Low harm.

## Public data (v1.1.2)
| where | files (paths relative to this folder) |
|---|---|
| boar-research (this repo) | this report, criterion + sha256, CALLS.md, tools/, aggregates/ (m1, m1-gen-s42/s43, m2, m3, m4), out/*.status.json, out/runner-apk.sha256, req/df-m1-v04-s42.json, s42b.json, s43.json, req/df-m2-probes-s42.json; ../../ruler/factavail/out/factavail-items.json (FACT-AVAIL labels, sha 7e0b9345) |
| boar-traces (Hugging Face, same paths, sha256 in TRACES.tsv) | M1: out/df-m1-v04-s42.jsonl, s42b.jsonl, s43.jsonl, traces/dev-s42/s43.traces.jsonl, judge/dev-s42/s43.{opus,codex}.judgments.jsonl; desktop twin ../native-rc/work/v04/{lite-s42.jsonl, traces/lite-s42.traces.jsonl, bench/questions.jsonl}, ../native-rc/judge/rf/lite-s42.{opus,codex}.judgments.jsonl. M2: out/df-m2-probes-s42.jsonl. M3/M4: out/df-m3-packproof-s42.jsonl, out/df-m4-uxmatrix-s42.jsonl, judge/m3-answers.json, m3-labels.jsonl, m4-answers.json, m4-labels.jsonl |
| not published | M5 cold-start, smoke, fresh-install and follow-up-check rows (out/df-m5-cold-*.jsonl, df-smoke, df-fresh, df-check-followup), netstats dumps and logs; judge/m3-units.json, m4-units.json (label inputs carrying pack passage bodies); ../x2b-budget/replays/B600/probes.jsonl (desktop kept passages, includes NHS wording), so the M2 grounded_approx block cannot be recomputed; requests for seed 44 (not run), M3/M4, M5 |

Recompute (0 LLM) from a copy of boar-research with the boar-traces files placed at the same paths:
```
cd rnd/research/coordinator/arms/device-final
python3 -I tools/m1_agg.py        # -> aggregates/m1.json, byte-identical to the committed file
python3 -I tools/m34_agg.py m3 judge/m3-answers.json judge/m3-labels.jsonl aggregates/m3.json   # byte-identical
python3 -I tools/m34_agg.py m4 judge/m4-answers.json judge/m4-labels.jsonl aggregates/m4.json   # byte-identical
```
Checked 2026-10-29 on a scratch copy of the public trees (boar-research + boar-bench + staged boar-traces): m1.json, m3.json, m4.json identical. m1_agg.py prints G1 s42 U 0.167 [0.129, 0.209], G2 s42 0.244 [0.193, 0.298], pooled G1 0.165 [0.127, 0.205], G2 0.242 [0.194, 0.296], paired vs desktop G1 +0.003 [-0.022, 0.026], G2 -0.007 [-0.039, 0.023]. tools/m2_probes.py stops on the missing B600 replay; the M2 layer counts (53 fixed / 12 model of 65, last turn) follow from the healthFixed/exposureComputed/calculated/outcome flags of out/df-m2-probes-s42.jsonl. m34_prep.py (answers/units from phone rows) needs the desktop packproof/uxmatrix judge units, which are not published.
