# chat-slice v0 (Compass, 2026-10-02): does BOAR decide to search?
- `slice.v0.jsonl`: 64 items, PT 26 / EN 22 / ES 16, 13 multi-turn.
  - Kinds: greeting 20 (messy: emoji, elongation, vocative, typos), meta 8, follow-up 13, mixed greeting+question 7, research 8, ambiguous 8.
  - `expected_search`: no 34 / yes 23 / either 7.
  - Fields: id, lang, kind, turns [{role, text}] (the last user turn is the message; earlier turns = engine history), expected_search, expected (one-line behaviour).
  - Written from scratch by Compass (`build_slice.py`); not from any bench, blind set or competitor dataset. Development data, not held-out.
- `score_l0.py`: deterministic L0 scorer (accuracy, false-search, missed-search; per language and kind; `--traces` engine traces or `--decisions` jsonl). Self-tested: oracle decisions and synthetic traces → 100 %.
- `baseline_l0.mjs`: main's current single-turn rule (smallTalk + classify, `engine/` copied from upstream/main @ `engine/COMMIT`) → `decisions.main.jsonl`, `score.main.json`: **accuracy 44 %, false-search 94 % (32/34), missed-search 0 %**. Only "e aí boar, beleza?" and "e aí?" are caught.
- `fast-loop.md`: the L0–L3 levels and the 2 h kill rule.
- `score_l0.py` secondary metric **lang_match** (reply language == user language; `lang_of()` = deterministic en/pt/es function-word + orthography vote on the final answer, engine warning lines and [n] stripped; `REPLY_LANG` overrides cs-037 → pt). Kiln's full-engine base s42 (`boar-eval/runs/kiln/chat-slice-base-s42`): **50/64 = 78 %** (en 22/22, es 11/16, pt 17/26); all 14 misses are English replies: greeting 8 (echo the greeting, then switch), ambiguous 4, meta 1, follow-up 1 ("Boa noite [1]! How can I assist you tonight?"). Hand read of all 64 detections: agrees 64/64. `score.kiln-base-s42.json`.
