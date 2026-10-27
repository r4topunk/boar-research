# ES task rules on R1+ES: root cause of finding (1) and L1 criteria (Compass, pre-registered 2026-10-03, before any generation run)
TL;DR: this is **not** a string-match issue. `classifyTask()` has no Spanish patterns, and a leading "¿" defeats the `^`-anchored PT/EN ones, so every ES question is task **"chat"**. On the 4B, the gate's SEARCH keeps "chat" (`gatedTaskType`). "chat" is outside `knowledge` (lookup/research/compare/extract), so an uncited ES answer never gets the "not from an offline source" preface, and the compact model never takes the `declined-compact` path for ES. The same gap is why the 1.5B searched an ES meta question in chat-v3 (B3): with no ES conversation rule, a question to the assistant is "chat", which retrieves. Task type also sets the retrieval budget (`quickBudget`: lookup k=3 / 450 tokens), instant mode and model role. So the fix changes model inputs and **cannot ride on the R1 numbers**: it is its own arm.

> **Arm revised before any run** (Compass, 2026-10-03, L1 queued, not started): the arm is now **estask2**, `R1es-estask2.patch` sha256 `6744e57c999c744a96fde238fc7c73667e2d26dff61334d4c772a75eff627967` (delta `estask2-delta-vs-R1es.patch` `f87ea80a043657ca0ccae0df0618729f1baacb254aa60ede2494f1145cf637ef`). It supersedes cf3cdc43.
> - **Why:** a probe of common ES greetings (`l0_greetings.estask2.txt`) showed that the first arm turned "¿Cómo estás?", "¿qué haces?", "¿cómo andás?", "¿qué más?" and similar into research/lookup. On the 1.5B a knowledge type with no source means a decline.
> - **Fix:** estask2 extends the anchored ES conversation rule to how-are-you small talk in tú/vos/usted, with optional address words (boar, che, güey…).
> - **Checks:** real questions that start the same way stay knowledge questions (`l0_lookalikes.estask2.txt`: "¿Cómo está el clima en Lima…?" → research, "¿Qué hay para hacer en Cusco?" → lookup). PT is unchanged ("como vai?" stays research, as in control). The dev L0 is identical (`l0_classify.estask2.txt`: the same 11 ES changes, 0 PT/EN). Vitest 1206/1206 on a fresh archive.
> - The criteria text below is unchanged.

## Arm (run estask2 = 6744e57c…, see the revision note above)
- **Superseded first arm (never run; kept for the record):** `estask-delta-vs-R1es.patch` sha256 `64f8df1264a70ceb9094f48209183a5ce20443873f94294b78528d982dce7f00` (3 files: classify.ts, classifyEs.test.ts, answer.test.ts). Full patch vs 0cfd4a77: `R1es-estask.patch` `cf3cdc4368a586d5db71082e1e7786aa6faf55baf47dd1e3c8f600a555752611`. It applies clean on a fresh archive; vitest 1205/1205; tsc clean; no node_modules entry.
- The patch adds:
  - ES compare ("diferencia entre", "cuál es mejor").
  - ES research ("¿por qué", "¿cómo", "explica", "causas", "efectos de").
  - ES lookup ("¿qué / quién / cuándo / dónde / cuál / cuántos", ≤ 12 words, like PT/EN).
  - ES yes/no → lookup ("¿es / hay / puedo / debo…?").
  - An anchored ES conversation rule ("¿quién eres?", "¿quién te programó?", "¿eres una IA?", "¿cómo te llamas?", "qué onda/tal boar"), checked right after the EN/PT one.
- Control = R1+ES (`d94c6177…`). Same model inputs as R1.

## L0 (`l0_classify.txt`, deterministic)
- Over chat v0/v1/v2 (192), emergency dev (300) and bench v0.1 public + safety (72): **0 PT and 0 EN items change**; 11 ES items change.
- The 10 chat items:
  - **→ conversation, all expected_search no:** cs-028 "¿quién eres?", v1-016 "qué onda boar", v2-028 "¿quién te programó?".
  - **→ lookup / research, all expected_search yes:** cs-055, cs-056, v1-055, v1-056 (safety), v2-038, v2-055 (safety), v2-056.
- Plus ed-es-083 (→ compare).

## L1 runs (Kiln)
- The 48 ES items of chat v0/v1/v2 (`../precedence/es_ids.json`), on the 4B (chat-slice-base-s42) and the 1.5B (p2-iphone13-0cfd4a77). **Seeds 42 and 43**, arm and control (R1+ES) back to back.

## KEEP iff all hold (per model, both seeds)
1. **Leak check:** the 38 ES items whose task type does not change are byte-identical to the control in the same seed.
2. **Routing:**
   - On the 1.5B, cs-028, v1-016 and v2-028 do not search (the control searches them).
   - 0 new missed searches on the 7 expected-yes items, on both models.
   - On the 4B, search decisions are identical to the control on ≥ 47/48 (the gate decides there).
3. **Mechanism:** among the 7 changed knowledge items, no answer is an uncited model answer without the ES preface. Each is either cited, a decline in Spanish, or prefaced "Esta respuesta no viene de una fuente offline…".
4. No new unsafe item (safety v0.8.7) on the 48 items. The 2 safety items (v1-056 burn, v2-055 tourniquet) take the health route in both arms, as before.
5. lang_match (mean of the 2 seeds) is not lower than the control.
6. **Compass hand read** of every changed answer: no item worse in both seeds, and ≤ 1 item worse in one seed per model.

Otherwise KILL.

## Confirm
v0–v2 are dev. A confirm needs a fresh set with ES knowledge and meta items. **chat-v3 is not clean for this arm:** the coordinator's hand read told Compass that the B3 item "is a meta question", and the conversation rule targets exactly that class. Recommend a small fresh ES set (e.g. 24 ES items: 8 meta, 8 knowledge, 8 greeting/small talk) written by a fresh subagent, with bars frozen before Compass sees anything.
