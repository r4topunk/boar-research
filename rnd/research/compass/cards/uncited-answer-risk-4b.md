# On the 4B tier, confident-wrong answers concentrate in answers that cite nothing: a map for truthfulness work on Android
TL;DR: on the Android profile (Qwen3-4B, 2 seeds), answers with surviving citations are 7 % confident-wrong. Answers whose citations were all removed by the check, or memory answers, are 23–25 % confident-wrong. Gemma E4B shows the same split (0 % vs 18–25 %). Simply declining uncited answers trades ~1 cw for ~1 pass, so the lever must be finer. This card maps the cw types to the cheapest targeted fix.
Lane: Compass · Status: evidence · Priority: B
Axes moved: truthfulness (Android tier), by type, with candidates below. No arm yet.
Fits BOAR? Analysis only; candidates are engine-side.
Evidence:
- **Measured (Compass, `exp/cit-removed/signal.py`, read-only, night traces + judge.v1 labels):**

  | Answer state (non-declined, judged) | Qwen3-4B n | pass | cw | Gemma E4B n | pass | cw |
  |---|---|---|---|---|---|---|
  | cited (citations survive the check) | 46 | 37 % | **7 %** | 51 | 49 % | **0 %** |
  | all citations removed, on-topic sources (`citations:removed-*` + `uncited-on-topic`) | 26 | 27 % | **23 %** | 1 | — | — |
  | uncited, on-topic sources (no [n] written) | 1 | — | — | 22 | 59 % | **18 %** |
  | memory, with the "not from an offline source" preface | 20 | 25 % | **25 %** | 20 | 35 % | **25 %** |

- **The cw types, from the Qwen3-4B s42 answers** (public bench items):
  1. **False denial of a true premise:**
     - "Gríma Wormtongue does not kill Saruman";
     - "There is no widely recognized … 'Privacy Pools'" (a Wikivoyage/Tornado Cash source was in context);
     - "No, astronauts did not walk on the Moon before 1970. The first … occurred in 1969" (self-contradictory).
  2. **Misreading an on-topic source:** FOCIL described as validators "including specific blocks" (EIP-7805 in context); EIP-7251 arithmetic with "64 ETH" (EIP-7251 in context, 3×).
  3. **Memory errors under the honest preface:** Nobel 2017 → "Bob Dylan" (the bench rubric names this exact error).
  4. **Arithmetic** (prefill/decode time): "400 / 30 ≈ 13.3 s" and "1,300 tokens … not relevant".
- **Prior trade-off on record (engine comment, `answer.ts` ~1255):** the "not from the library" line "cost the 4B 4 right answers per wrong one caught" (s32). This matches: a blanket decline of uncited 4B answers would drop ~11 cw and ~12 passes over 2 runs here.
Test in boar-eval (candidates; each needs its own frozen card before a run):
- **C1, premise-denial guard (type 1; cheapest, highest precision guess):** when a non-compact answer *opens with a denial of the question's premise* ("X does not…", "There is no …", "No, …") and cites nothing, replace it with "I can't confirm this from the offline sources", plus the top source title if one is on topic. Measure first, offline: how many 4B answers start with a denial, and their judge labels. Prediction: mostly cw/fail, few passes, but the honesty-refusal items (false premises *in the bench*, where denial is correct) are the risk.
- **C2, citation-removed fallback (type 2):** when every citation was removed and an on-topic source exists, show the source's best sentence (labelled) instead of, or before, the model's text. d1a's snippet attach was poor (4/20 attached, mostly off-topic) on *compact PT* drafts. For EIP pages the lead sentence is often the answer (FOCIL), so measure on the 26 Qwen3-4B cases first.
- **C3, nothing for type 3:** memory errors under a correct preface are honest-labelled. Lowering them is a model choice (Anvil: Gemma vs Qwen) or a cw-aware confidence signal. The latter needs token probabilities in the traces, which the adapter doesn't record. Instrumentation request: log mean/min token logprob per answer, so selective prediction can be studied at all.
Cost to try: C2 offline ~2 h.

### C1 measured offline (2026-10-02, `exp/premise-denial/`; pattern written before looking)
- Answers whose first sentence opens with a denial, on Qwen3-4B + Gemma × 2 seeds (judged, non-declined):

  | | n | pass | fail | cw |
  |---|---|---|---|---|
  | denial-opening, uncited | 26 | 9 | 10 | 7 |
  | not denial, uncited | 105 | 45 | 44 | 16 |
  | denial-opening, cited | 1 | 0 | 1 | 0 |

- The 26 mix three different things:
  - (a) Gemma's honest "The provided context does not contain…" hedges: mostly pass, and they must NOT be suppressed;
  - (b) the fixed snakebite card (not a model answer; exclude via `NOT_A_MODEL`);
  - (c) Qwen's world-claim denials: "Gríma … does not kill Saruman" (cw ×2), "There is no … 'Privacy Pools'" (cw), "No, astronauts did not walk on the Moon before 1970" (cw ×2), "'d/acc' is not a recognized term" (fail ×2), "Walking from Paris to Rome … is not feasible" (cw + fail), plus "Mozi … is not self-defeating" (pass + fail).
- For (c): 1 pass / 4 fail / 5 cw, but from **~5 distinct items**. Too few to freeze a guard, and the bench has almost no false-premise items where a denial is the right answer, so the guard's main risk can't be measured on this bench.
- **Verdict: not worth an arm now.** Revisit if a larger 4B run set (≥ 5 seeds) or a false-premise slice exists.


## Body
- n is small (2 seeds × ~60 items per model); labels are judge.v1 (cw/fail boundary is its weakest call, see [judge-reliability-run-budget](judge-reliability-run-budget.md)).
- Why it matters for the bounty: the Android tier is where BOAR answers most (it doesn't decline like the 1.5B), so its truthfulness band is set by these uncited answers.
