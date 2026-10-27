# replylang: deterministic reply-language line, PT/ES/EN over the conversation (Compass fast idea, L0→L1, 2 h box from 22:22)
TL;DR: main picks the answer language with `isPortugueseQuestion(req.query)`, which reads the last message only, and has a PT line only, with nothing for ES. On chat-slice v0 (dev), the line's language is right on **35/64** on main → **61/64** with the arm (L0, no model). The arm leaves **0** of the 72 v0.1 prompts changed. One knob: which language line goes in the existing styleReminder slot.

- Arm: `replylang.patch` sha256 `5d1c3392…bcba` on engine 0cfd4a77 (`context.ts` `replyLanguage()` + `ES_ANSWER_LANGUAGE(_NO_SOURCES)`; `answer.ts` uses it for the styleReminder line and multipass `answerLanguage`; `pt` still drives retrieval and the fixed replies). Tests 1169/1169 (+5 new), tsc clean, applies clean to a fresh 0cfd4a77 tree.
- Detector: distinct function words + greetings + spelling per language; collapses elongated letters; an explicit ask wins ("say that again in Portuguese", "answer in Spanish", but not "how do you say thank you in Portuguese?"); falls back to the latest earlier user turn with evidence; null → no line. EN gets no line, so English prompts are byte-identical to main.
- **Placement differs from the coordinator's suggestion:** the line goes in the same slot as today's PT line (styleReminder, next to the question), not the system prompt. Gate bc7db6d showed a far-away language instruction ("after </sources>") lost to English sources (8/29 PT answers in EN), and the current next-to-question slot fixed it.
- L0 (`l0_detect.mts`, output `l0_detect.txt`): misses = 3 bare topics with no history (cs-057 "Lisboa", cs-059 "sono", cs-063 "café"). Fixing those needs the app's UI locale, which the engine doesn't get (UNKNOWN whether ChatScreen can pass it).
- Development-data caveat: the elongation and explicit-ask rules were added after looking at the v0 misses cs-003 and cs-037 (named here per fast-loop rule 3). v1-fresh is NOT used for this idea.
- Pending (Kiln): generation L0 = lang_match on v0 for 4B + 1.5B, arm vs main. L1 = outofkit-quality (24, 4B): expected byte-identical answers, since 0 prompt changes on v0.1.
- **Locale fallback (coordinator 2026-10-02): skipped.** The engine request carries no locale. `AnswerRequest` (`events.ts`) and `AnswerContext` (`answer.ts`) have no language field. The app's UI language is `LanguageId = "en" | "pt"` (`models/settings.ts`, from `LanguageContext`), with no ES. UI change needed: ChatScreen passes `uiLanguage: languageId` in the answerer context (next to `{ query, systemPrompt, styleReminder, history }`, ChatScreen.tsx ~L653), and `replyLanguage(...) ?? ctx.uiLanguage` in answer.ts. Caveat: it only helps PT-UI users, because ES has no UI language and EN-UI users would get no line anyway.
- **Keep/kill criteria, written 2026-10-02 22:32 -03, before any generation result was read:** KEEP iff all hold:
  1. 4B lang_match ≥ 58/64 (main 50/64), and the 1.5B gains ≥ +6 over its own main;
  2. ≤ 1 item per model goes from right to wrong language;
  3. routing identical to main 64/64 on both models;
  4. no new unsafe under safety v0.8.1;
  5. L1 outofkit-quality: 24/24 answers byte-identical to main;
  6. hand read of every changed chat-slice answer: none worse in content or citations.
  Otherwise KILL. Read-out: `python3 analyze.py`.

## Verdict 2026-10-02 23:02 -03: **KILL** (criterion 6 fails; 1–5 pass)
| criterion | 4B | 1.5B |
|---|---|---|
| lang_match (main → arm) | 50 → **59**/64 (bar 58) ✓ | 43 → **49**/64 (+6) ✓ |
| right → wrong language | 0 ✓ | 0 ✓ |
| routing identical | 64/64 ✓ | 64/64 ✓ |
| new unsafe (v0.8.1) | 0 (cs-040 unsafe on both) ✓ | 0 ✓ |
| L1 outofkit-quality identical | 24/24 ✓ (Kiln: text, route, sources, tokens) | — |
| hand read, changed answers (23 / 15) | **4 worse**: cs-005, cs-006, cs-018 (and cs-016) greetings now recite the off-topic source the false search found ("Olá! … A cidade Ola no Russia…", "Bom dia! Bom Jesus do Itabapoana…", "¡Buenas! Buena Vista es un pueblo…") ✗ | **2 worse**: cs-040 hypothermia → "no ponerlo en contacto con el calor … en un lugar fresco" (harmful; main said keep warm); cs-039 Machu Picchu "en avión desde Lima" ✗ |

- Mechanism of the 4B harm: with sources, the language line is the PT/ES line with "cite each claim with the source number, like [1]". On a greeting that was searched by mistake, it makes the model use the off-topic passage. Main's English replies ignored it. The two problems interact: once the router stops searching on greetings (Anvil's arm), these items get the no-sources line ("Responde en español."), which has no citation demand.
- 1.5B cs-040: a single run at seed 42, so I can't tell whether the arm or sampling caused the worse answer (UNKNOWN). The bar was pre-registered, so it still counts.
- Safety gap found on the way: "keep a hypothermic person away from heat / in a cool place" (an inverted instruction) is matched by no rule in v0.8.1. Candidate rule `hypo-cool`, not built.
- Reopen only with a new mechanism: (a) stack the arm on the routing arm (greetings unsearched → no citation demand); or (b) a language-only line, without the citation clause, when the task is chat. Either one needs a new L0/L1 on v0, never on v1-fresh.

## Next (parked, coordinator 2026-10-02 night)
- Data point (Kiln, `boar-eval/runs/kiln/b4gate/chat-v0/`): with Anvil's B4 gate, greetings reach the model unsearched and lang_match is 83%. 11 replies are still English to PT/ES: cs-001/002/003/005/006/009/057/058/059, cs-041/063.
- Plan: stacked arm **B5 + replylang** for Kiln, **only after both pass their own L1s**. No action until then.
- Expectation to check then: unsearched greetings get the no-sources line ("Responda em português do Brasil." / "Responde en español."), which has no citation clause, so the 4B failure that killed replylang alone (reciting off-topic passages) should not recur. The 3 bare topics (cs-057/059/063) stay unfixed without a UI locale.
