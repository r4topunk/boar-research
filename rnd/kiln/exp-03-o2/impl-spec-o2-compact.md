# Implementation spec: O2 "off-subject" early decline on the compact tier

For: modelos ai #2 (via the coordinator) · From: Kiln exp-03 ([README](README.md)) · Rule: [`rnd/lantern/o2-weak-support-spec.md`](../../lantern/o2-weak-support-spec.md) (accepted) · Base: boar-app `origin/main` `7aa67d5`.

> **Rule (r4to, 2026-09-30, at the app maintainer's request):** engine changes are lowkey and local only. No upstream PR touching routing / rag / models / llama.rn. Everything below is a spec for a **local branch, for measurement**, not a PR.

## TL;DR

- **What:** on the **compact tier only**, before prefill, decline a numeric / superlative / comparative / list question when none of the passages going into the prompt is *about* the question's subject.
- **Evidence:** in-sample on iPhone run 3: CW 8 → 2, pass −1 (17 → 16), ~7 s of generation saved per decline. It is off on the default tier (Qwen3-4B: pass −21 pp).
- **Size:**
  - **1 new pure module**, `src/routing/o2WeakSupport.ts`, ~220 lines. It is a TS port of `rnd/lantern/tools/o2_reference.py`, with no LLM and no new asset.
  - **1 hook** in `src/routing/answer.ts` (~15 lines).
  - **1 test file** (~80 lines) using Lantern's 32-case test set as fixtures.
  - 2 strings (EN/PT).
- **Must pass before merge:** the test-set gates A1 ≥ 6/7, A2 7/7 and A3 4/4 as unit tests. Then the blind iPhone A/B in exp-03 README §5.

## 1. New module `src/routing/o2WeakSupport.ts` (pure, ~220 lines)

Port `o2_reference.py` function by function. The Python file is the executable definition of the spec (§3.1–3.5), and it passes A1–A3.

| Python (reference) | TS export | Notes |
|---|---|---|
| `classify(q)` | `o2Kind(q): "list" \| "superlative" \| "comparative" \| "numeric" \| null` | Keep the step order from spec §3.1: causal first (out), then list, superlative, comparative, numeric |
| `subjects(q, kind)` | internal | `named_entities`, `comparison_sides` and `superlative_class` as in the reference |
| `title_covers`, `class_level_title`, `passage_asserts_superlative`, `dominates` | internal | Normalization: NFKD, lowercase, drop possessive, plural stem. `PREFIX` strips `Wikivoyage: `, `Ethereum EIPs/ERCs: `, … |
| `decide(question, passages)` | `o2Decide(question: string, passages: {title: string; text: string}[]): { inScope: boolean; kind?: string; action: "keep" \| "refuse"; reason: string; questionSubject?: string; passageSubject?: string }` | `passages` = the chunks going into the prompt: `title` = `chunk.title` (display title, prefix included, as the app already shows it), `text` = `chunk.body` |

Rules to preserve exactly:
- **Fail open.** No subject extracted → keep. PT subject the lexicon cannot map → keep (spec §3.2). No passages → out of scope; the existing no-source gate handles it.
- **No geographic containment.** "Kantō region" does not cover "Japan". That is the core of the rule.
- **Aliases:** the spec says "pack redirects only". There is **no redirects lookup in `src/rag` today** (checked `origin/main`). **v1 ships without aliases** (fail-closed on "USA" vs "United States"). Log `o2:no-alias-table` in `reason`, and track the false refusals this causes in the A/B (§4).
- **PT:** map subject tokens with `englishNamesIn(query, lexicon)` from `src/rag/ptLexicon.ts` (already used by retrieval). If nothing maps, keep.

## 2. Hook in `src/routing/answer.ts` (~15 lines)

**Where:** right after the extractive-health block returns and **before** the `fromMemory` / `grounding:declined-compact` block (at `origin/main` ~line 958, comment "A knowledge question with nothing retrieved…"). At that point:
- `sources` is final: compressed (`compressContext`, ~l.827), then filtered by the on-topic gate (`grounding:off-topic-dropped` / `no-good-source`, ~l.836–841).
- `genLlm` (l.663), `pt` (l.752), `health` (l.656), `req.answerAnyway` and `gen.mode` are in scope.
- Nothing has been prefilled yet (`stage("prefill", …)` is at ~l.1103).

```ts
// O2 (exp-03, rnd/lantern/o2-weak-support-spec.md): on the compact tier, a numeric/superlative/comparative
// question whose passages are all about something else (Kantō for Japan, Moose for "tallest animal") is
// declined before prefill. The default tier is left alone (it answers these from memory, right 8 of 9 times).
if (O2_COMPACT && !health && gen?.mode !== "multipass" && genLlm && isCompactModel(genLlm) && !req.answerAnyway && sources.length) {
  const o2 = o2Decide(req.query, sources.map((c) => ({ title: c.title, text: c.body })));
  if (o2.action === "refuse") {
    reasonCodes.push("grounding:o2-off-subject");
    markVisible();
    const message = o2Message(pt, o2); // §3
    emit({ type: "warning", answerId, code: "weak_sources", declined: true, message });
    finalText = message;
    return finish(genTier, "success", message, sources, receipt({ retrievalMs }));
  }
}
```

- **Return `sources`** (not `[]`), because the passages were found and shown. This matches the reasoning behind `all-citations-removed-declined-compact` (Quill 892c049: "didn't find this" would be false).
- **`O2_COMPACT`:** a module constant, default `true` after the A/B passes and `false` until then. It is the rollback switch.
- **"Answer anyway"** bypasses it, like every compact decline (`req.answerAnyway`).
- **No late (post-draft) hook in v1.** On run 3, 7/7 hits already fire on the prompt passages, so a late check adds 0 hits. Add it only if the blind A/B shows cases where the cited passages differ.

## 3. Strings

Spec §1: the message says *why*, and falls back to the generic line when either subject is missing.
- EN: `The passages found are about {passageSubject}, not {questionSubject}.`, fallback `The passages found don't support this answer.`
- PT: `Os trechos encontrados falam de {passageSubject}, não de {questionSubject}.`, fallback `Os trechos encontrados não sustentam esta resposta.` (the existing string)
- `passageSubject` = the first passage title without its prefix. `questionSubject` = the extracted subject or class.

## 4. Tests (`src/routing/o2WeakSupport.test.ts`, ~80 lines)

- **Fixtures:** copy `rnd/lantern/o2/o2-testset.jsonl` (32 cases: question, passages' titles, bucket, `expected_o2`).
  - Offline, the reference reads passage text from local packs. For the unit test, inline a short `text` excerpt for the ~6 cases whose decision depends on text. These are the dominance and unqualified-superlative cases: fa-005 Elephant, fa-015 World population, fa-013/023 class cases.
- **Gates:** A1 must_refuse recall ≥ 6/7, A2 must_keep 7/7, A3 gate_must_not_worsen 4/4. Log neutral and out-of-reach cases without asserting them.
- **Classifier:** the 20 in-scope items of the 58-item set are in scope; `vit-cry-011` "Why did Terra collapse in 2022?" is out (causal).
- **Hook test** in `answer.test.ts`:
  - compact model + Kantō passage + "What is Japan's population?" → declined, `grounding:o2-off-subject`, sources kept;
  - the same with `answerTier: "default"` → not declined;
  - with `answerAnyway` → not declined.

## 5. Acceptance and rollback

- **Merge gate:** unit tests A1–A3 green. `O2_COMPACT = false` until the blind A/B.
- **Ship gate (exp-03 README §5):** on the iPhone, compact, `wiki-vital5`, O2 off vs on, Plumb's blind labels:
  - A4 Δpass ≥ −5 pp;
  - A5 Δcw ≤ −5 pp;
  - on ≥ 20 fresh in-scope items, ≤ 1 new false refusal per 10 hits.
- **Rollback:** `O2_COMPACT = false` (one line). No data or asset migration.

## UNKNOWN

- Out-of-sample precision. Everything is in-sample (exp-03 README §5).
- Whether in-app passage `body` text (shorter than the article text the offline eval used) lets the dominance and superlative keeps fire. If not, more false refusals. That is what the A/B measures.
- The alias gap (no redirects table in `src/rag`).
