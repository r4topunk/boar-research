# DEVICE-FINAL: the final benchmark matrix on the phone (frozen 2026-10-25 03:3x, before any matrix generation)
Ask (r4to 10-25 03:0x): run the final benchmarks with the app running the engine inside the Pixel 8, for publication; full matrix overnight.

System: LabRat = boar-lite main 7788924a (engine = b4ef94f3 + the Rat persona line in the grounding prompt; health gate B+FU, QuickMath, exposure answer,
SearchPort ON_NO_HEALTH, Succinct, Qwen3-1.7B Q4_K_M, 512 tokens, thinking off). Device eval runner patched for this run only (branch eval/device-history):
optional follow-up turns answered in order with the chat's history (last 6 messages, HistoryBudget, stripThinking) and the streamed text recorded as
shownText (what the chat shows). Engine logic untouched. Installed as the unbundled release over the installed bundle data (same key); the bundled
LabRat-7788924a-7a95e0a5 APK is reinstalled after the matrix. Phone: Pixel 8a 8 GB (GrapheneOS, Android 17), AC power, airplane mode, screen on.
The app has no INTERNET permission; netstats for the app uid recorded before/after.

Matrix (phone order: M1 s42, M2, M4, M1 s43, M3, M1 s44, M5):
- M1 RULER-DEVICE: v0.4, 75 items (71 headline + 4 anchors), 88 turns, seeds 42, 43, 44. Judges as RULER-FINAL (rf_judge.sh logic, judge.v1 both orders):
  G1 Opus vs Claude refs (b27eac37) on all three seeds (cap 160 calls per seed); G2 Codex vs Codex refs (047cb199) on seed 42 (cap 160), seeds 43/44 if
  the [usage detail removed] allows. Report per family: U-total H (health weight 0.5) with CI (B 2000, seed 11), win-rate, refusals, min over families,
  three-seed mean (G1), and the paired delta vs the RULER-FINAL desktop twin b4ef94f3 seed 42 (G1 0.164, G2 0.245): a phone-vs-desktop parity
  read, not a verdict (engines differ by the Rat line; sampling differs by platform).
- M2 PROBES: the 65 F3 safety probes (8 with prior user turns, which the phone answers as a real chat), seed 42, 0 LLM: fixed health text count,
  exposure, model answers, new dose figures (probes.py DOSE). Reference: desktop b4ef94f3 41 fixed + 1 exposure + 23 model.
- M3 PACKPROOF-ON: the 140 on-k13 self-tests (the shipped K13 kit), seed 42, Haiku 5.5-low labels with packproof/tools/label.mjs unchanged:
  correct-any, correct-with-source, wrong-unwarned (WU). Desktop reference = PACKPROOF ON (other engine, TS stack): context only.
- M4 UXMATRIX-ON: the 60 UXMATRIX items, seed 42, Haiku labels with the UXMATRIX labeller unchanged: CWS, correct-any, WU.
  Reference NATIVE-RC/SEARCHPORT desktop numbers: context only.
- M5 PERF: from every row: total latency, user TTFT, decode tok/s, prompt tokens, peak RSS, battery temperature (p50/p90/max); cold start x3
  (force-stop, first question, model load included); netstats rx/tx of the app uid over the whole night.
Claim numbers = M1 (both families named, seeds stated, win-rate first), M5 speed/memory/offline. M2-M4 are product numbers.
Rules: never print or open v0.4 question/reference text; no tuning; no engine change; one QUEUE row + EXPOSURES row; commit rnd; never push.
Caps: Opus 3 x 160, Codex 2 x 160, Haiku 600, paid API 0.
