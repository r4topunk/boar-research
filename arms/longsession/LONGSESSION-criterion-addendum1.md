# LONGSESSION addendum 1: 15-turn extension (frozen 2026-10-14, before any extension run; the base criterion sha256 710f07a6… is unchanged)

## Change
- Three sessions extended from 5 to 15 turns: ls02 (coref, crypto), ls06 (topic switch, travel + arithmetic; a second switch happens at turn 8 and a return at turn 11), ls08 (deepen, Iceland). That is 30 new agent-written dev items, ids ls0X-t6 … ls0X-t15. They are appended to `boar-eval/bench/slices/longsession-v1/questions.jsonl`; the first 50 lines are byte-identical, and the file's new sha256 is a73f1e644e5e163adf6c5c8887016706dc0606ba258d10595442356b4a466b08. 13 of the 30 are `followup: true`. SHA256SUMS and sessions.jsonl are updated. Builder: `tools/build_slice.py` (EXT block).
- References: `refs/refs.jsonl` is rebuilt over all 80 items. The original 50 rows come from `ls-standalone-s42` (same answers); the 30 new rows come from `ls-ext15-standalone-s42`. MANIFEST is updated to the new questions sha. The original 50-item judgments keep their own provenance (old questions sha f618808d…) and are not re-judged.

## Runs (same tree, seed 42, server, kit and runner as the base criterion)
- A `ls-ext15-session-s42`: waves t6..t15, one wave per turn index (3 items per wave). The history is the full set of turns 1..k-1, made of the questions plus the engine's own answers. Turns 1-5 come from the base run `ls-session-s42` and turns 6+ from earlier extension waves. The desktop adapter passes ALL previous turns: `history = {summary: null, turns}`.
- B `ls-ext15-standalone-s42`: the 30 new items alone.
- Server guard: wait while busy.sh shows another llama-server or adapter job, polling every 60 s for up to 90 min (`WAIT_MAX=90`).

## Measured (same definitions as the base criterion)
- Per turn block, 6-10 and 11-15 (15 items each): ratio A/B (item bootstrap B 2000 seed 11) and W/T/L. Also per session, and the base turns 1-5 of the same 3 sessions for context.
- Prompt-token curve to turn 15 (A promptTokens per turn, the A − B history overhead).
- App-window comparison. The app (ChatScreen, cut 7 tree) sends only the last 6 messages verbatim (VERBATIM_MESSAGE_COUNT = 6). After a turn completes with more than 6 turns in total (historyTurnThreshold 6, autoSummarize on), it summarises the older messages (nPredict 150). So turns 5-7 carry only the last 3 turns, with no summary, and turns 8+ carry the last 3 turns plus a summary of at most 150 tokens. Reported:
  - (a) the history tokens the adapter actually passed per turn;
  - (b) the history tokens the app would pass: the last 6 messages plus ≤ 150 for the summary from turn 8 on;
  - the turn and token count at which the app window first truncates (the first turn with more than 6 prior messages).
  Tokens of a message are estimated as chars × (tokens/char), with the ratio fitted on the dumped prompts (promptTokens vs prompt characters) of this arm. This is an estimate and is labelled as one.
- Coreference heuristic (referent substring) on the 13 new follow-ups. Card reuse = count of `grounding:fa-card-from-history` and of cards (`grounding:fa-card-*`) in A that B lacks. The 3 worst items (s_A − s_B).
- Reading: descriptive only (n = 15 per block, 1 seed, dev). A block whose CI lies wholly below 1 counts as "quality falls in long sessions"; a CI covering 1 counts as "no drop detected (CI width stated)".

## Budget
≤ 64 Haiku calls (2 preflight + 60), 0 Opus, 0 paid. Wall cap 2 h on the MacBook, excluding waiting for another agent's server.
