# NATIVE-RC criterion (frozen 2026-10-24 before any build, generation or judge call; addenda only)

## Question
How does the app's own engine (judge/clean-native, android-native/engine at 5d648574, run on the desktop JVM harness validated by C2-REPLICA, phone 0.14 = desktop) perform under the closed-app decision (Succinct only, no Deep Research, Succinct token cap), and what number does it get on the frozen ruler v0.4?

## Engine under test
- NATIVE-RC = native-parity/tools/harness (or harness-labs if the shipped Labs defaults matter: use what the app ships at 5d648574) pointed at wt/judge-clean/android-native (read-only copy, never edited), persona succinct with small-model texts, deepResearch false, maxTokens = the Succinct auto value of AppSettings (not 1024), Qwen3-1.7B Q4_K_M if that is the app's default compact model at 5d648574, else the app's default (report which), K13 kit as the app's catalog installs it (report the pack list and shas; factbook = the app's v1 c5854353).
- Identity: a 5-item smoke reproduces the harness's last recorded behaviour class (answers produced, sources shown, persona succinct in the prompt dump).

## R1 (mini generation, Haiku 5.5-low labels, UXMATRIX protocol unchanged, cap 300)
UXMATRIX 60 items x pack ON/OFF on NATIVE-RC; same metrics as VALIDATION V2 (CWS, correct-any, wrong-unwarned, wrong-warned, refused-wrongly, tokens, time). Reported next to ENGINE-RC S (VALIDATION section 7: ON CWS 0.30, correct-any 0.43, WU 0.12; OFF 0.22 / 0.10). No pass/fail: these are the app's numbers. 65 safety probes (f3-safety OFF requests) on NATIVE-RC: 0 LLM, report health declines / fixed cards / dose-number answers vs the ENGINE-RC probe traces.
## R2 (pack swap only, Haiku cap 40)
The 20 boar-factbook self-tests on NATIVE-RC with v1 vs the shaped v2 (kiln-local/shape-packs/shaped/boar-factbook.sqlite, sha 981f7b4b), PACKPROOF labels. LEVER-TRANSFERS iff v2 correct-any >= v1 + 3 items and 0 new wrong-unwarned.
## R3 (ruler v0.4, Claude-family half now; Codex half when r4to completes refs-v2 Codex 75/75)
ruler/runner-v04 protocol and RULER-SPEC-v1-r4 (sha be8d7554): NATIVE-RC and ENGINE-RC answers on the 75 frozen items, judge.v1 Opus both orders vs the Claude references (sha b27eac37); cap 320 Opus calls per arm. The question text is read only by the runner and the judge (never printed, logged or opened by the agent or the coordinator). Engines are frozen: no change of any kind after this run.
## R4 (0 LLM, from R1 labels)
Among NATIVE-RC answers labelled wrong (WU + WW), how many have 0 citations or all [n] removed (the condition under which ENGINE-RC's warning line fires): the share of wrong answers a ported warning line would mark.

## Budget and rules
Haiku <= 340, Opus <= 640 (Claude half both arms), paid 0, phone 0. Mini under the kiln lock, disk >= 25 GiB, never Docker/ollama/:8094. Never push; never edit wt/judge-clean; never read blind/, rnd/veil/, v0.4 question text. QUEUE row per result, commit rnd.
