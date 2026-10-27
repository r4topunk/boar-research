# Fast loop: 4 levels, iterate fast first, rigor later (Compass, 2026-10-02 night; r4to's policy change)
TL;DR: every idea climbs L0 → L1 → L2 → L3 and stops at the first level it fails. Freezing (sha256) is required only at L2 and L3. Each idea gets a **2-hour time box**; at 2 h without passing L1 it's killed and logged in one line.

| Level | What runs | Time | Input | Pass to the next level when | Freeze? |
|---|---|---|---|---|---|
| **L0 mechanism** | The changed pure function(s) alone (classifier, router, prompt builder), no model or only the decision step | seconds | a slice (e.g. `chat-slice/slice.v0.jsonl`) + `score_l0.py` / unit tests | the targeted metric moves in the right direction AND the guard metric doesn't break (chat slice: false-search ↓ with missed-search ≤ 5 %) | no |
| **L1 targeted slice** | Full engine via the desktop adapter, 1 rep, ~24 items picked for the idea (affected + guard items) | ~10 min | slice subset + its deterministic scorer; spot-read every changed answer | target improves on the slice; no new unsafe; every changed answer read and none is worse | no (log commit + slice ids) |
| **L2 full dev bench** | v0.1, 2 reps (s42/s43), judged | ~1–1.5 h | bench v0.1 + judge.v1 + gate | the idea's frozen criterion (written before the run): paired Δ (or non-inferiority) + cw + unsafe + gate | **yes**: criterion + patch sha before the run |
| **L3 held-out** | v0.2 held-out, confirm only | as E3 | frozen v0.2 manifest | confirms L2 within the plan's bounds; never used to choose | **yes**: analysis plan + addendum |

Rules:
1. **Time box: 2 h of wall time per idea from its first L0 run.** No L1 pass by then → kill. Write one line in the owner's LOG (what was tried, the numbers, why it died). Reopen only with a new mechanism, not a new wording.
2. **One knob per idea.** Two changes at once = two ideas.
3. **Slices are development data.** Expect over-fitting at L0/L1: any slice item that drove a design choice is named in the card, and L2 is the first honest number.
4. **Never skip a level upward.** An L0-only "win" isn't a result; a level can be skipped downward (a pure bug fix may go straight to L1).
5. **Guard metrics at every level:** safety (rules v0.7 on danger items), confident-wrong, and the slice's opposite error (false-search vs missed-search) are reported even when they aren't the target.
6. **Blindness unchanged:** L3 sets and `blind/` are never read; slices live in researchers' folders and are not blind.

Chat-slice specifics (first user: Anvil, model-driven routing):
- L0: `score_l0.py --slice slice.v0.jsonl --decisions <your decisions.jsonl>`. Baseline main: `node baseline_l0.mjs slice.v0.jsonl` → accuracy 44 %, false-search 94 % (32/34), missed-search 0 % (0/23).
- L1 needs the adapter to pass multi-turn items: `turns[:-1]` → `req.history.turns` (engine type `ConversationTurn {role, text}`, `src/rag/pure.ts` L265). Today the desktop adapter sends `query` only. Without that, run the 51 single-turn items and report the 13 multi-turn ones as "not run".
- L1 also reads every reply against the item's `expected` line (one line each), since the decision is right but the reply can still be wrong.
