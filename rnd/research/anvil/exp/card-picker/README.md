# 4B card picker: pick + verify, two one-token forwards (Anvil, 2026-10-03, DEV ONLY)

**TL;DR:** on Compass emergency-dev (180 emergencies with a gold `cond`; 103 have a card, 74 have no card; the 3 snakebite items are excluded because the WHO card fires upstream):

| Picker | Right card (of 103) | Wrong card (of 177) | Notes |
|---|---|---|---|
| Engine regex (`conversationCondition`, health11 final) | 26 | 11 | 5 of the 11 are the **altitude misfire** class (hypoglycemia, asthma, heatstroke, lost trail, overdose → altitude) |
| CP1 pick alone (30 single-token codes) | 90 | 47 | the 4B almost never abstains; confidence doesn't separate (median share 0.9999 for right and for wrong) |
| CP2 pick alone (+ "conditions with no card" list; **dev-tuned**) | 85 | 34 | |
| **CP1 + V1 verify** | **81** | **6** | **both prompts pre-registered, no tuning** |
| CP2 + V1 | 78 | 5 | |

**How it works:** `cp.mts` and `verify.mts`.
- **Pick:** system = `CP1.txt` (29 cards + NONE as codes A..DD, every code a single Qwen3 token). One forward, argmax over the 30 code probabilities.
- **Verify:** system = `V1.txt`; user = the message + "Card: <title>". One forward; keep the card iff p(YES)/(p(YES)+p(NO)) ≥ 0.5, else the generic emergency line.
- **Hashes:** `PREREG.sha256` (CP1 84fa2f36, V1 76cfbda3 pre-registered; CP2 aac09c0c dev-tuned).

**The 6 remaining wrong cards (CP1+V1):**
- arguably fine:
  - insulin double dose → hypoglycemia;
  - sting with anaphylaxis signs → beesting (the card has an anaphylaxis line);
- wrong:
  - spinal injury → headinjury;
  - spinal injury in water → drowning;
  - house fire → co;
  - aggressive animal (no bite) → animalbite.

**Lost:** verify rejects 9 right picks (heartattack ×2, stroke ×2, jellyfish ×2, headinjury, hypothermia, drowning); those get the generic line, which is safe.

**Cost:**
- Runs only on the health path: picker ~50 new tokens p50, verify ~67 p50 (p95 153); the prefixes are cacheable.
- Desktop ~1 s each.
- **g75 4B ≈ 6.5–10 s** at 12–18 tok/s prefill. Heavy, but:
  - (a) a card replaces the 4B's answer decode (30 s+ on g75) on the health path, so the total is still lower;
  - (b) the emergency-number line can show at once and the card stream in after;
  - (c) running verify as a continuation of the picker's KV (assistant code + a short user check turn) would save re-prefilling the message: ~30 instead of 67 tokens. Not built.
- The B6 route gate's KV can't be reused: different system prompt.

**Caveats:**
- Dev only. One set (Compass's, spec-aligned); its `cond` labels are the gold.
- 1.5B not tried.
- A learned picker on mmBERT embeddings (Sonar) would be ~0 ms. This is the 4B-only LLM option to compare against.
- hf1/hf2 are now dev for card picking (coordinator). Anvil keeps its no-`blind/` rule. A Kiln-run aggregate replay of `cp.mts` + `verify.mts` on them is possible: the scripts would need a gold-condition field, which the blind items may not have.

## Update: verify-as-continuation + v0.8.8 scoring (handed to Sonar, who owns the picker)
- **`cpv.mts` + `V2c.txt` (pre-registered):** the picked code is appended as the assistant turn, then a check turn runs on the same KV.
  - **Worse:** right 88/103, wrong 23/177 vs gold; v0.8.8 wrong-card 24 of 114 shown.
  - **Not cheaper:** 107 new tokens p50 vs V1's 67.
  - In the same context, the model mostly agrees with its own pick. **The verify must run in a fresh context (V1).**
- **v0.8.8 scorer for offline pickers:** `cardtexts.mts` renders the engine card text in the item's language; `score_v088.py` applies Compass's `wrong_card.jev`, same instructions, criteria, threshold and cache. DEV only.

  | picker | cards shown | v0.8.8 wrong-card | ok |
  |---|---|---|---|
  | engine regex (health12 tree) | 40 | 9 | 31 |
  | CP1 pick alone | 143 | 45 | 98 |
  | **CP1 + V1** | 90 | **9** | **81** |
  | CP1 + V2c (continuation) | 114 | 24 | 90 |

- **v0.8.8 flags some gold-condition cards** (choking-child title on an adult, child-only scorpion card on an adult, drowning card after a rescue). Those are card-text issues Compass already lists, not picker errors.
- **Not done (Sonar's call):** VERIFY behind health13's regex picks. Run `verify.mts` on a picks file where `pick` = the health13 regex condition.
