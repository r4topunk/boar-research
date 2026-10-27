# BANNER-KEPT: why the 1.7B's released answers say "Not found in this phone's offline library" with on-topic chunks kept (2026-10-23, 0 LLM)

TL;DR: the banner is not the model copying the prompt, and it is not in wt/engfix. It is the CMP30OFF release line, one fixed string for all five released compact declines. It is prepended by the engine in the eval trees that carry the CMP30OFF / LITEDECLINE OFF5 patch: kiln-local/be-0cfd4a77-cut7-litepacks (TOPICS27, SEFIX MAIN) and bench-app/engine (cut7-cmp30off-batchret). Every false banner comes from rule 4 "uncited-with-sources" (often together with rule 3 "all-citations-removed"). These rules fire when passages were kept and shown but CT-1 removed every [n], or the answer cites nothing. The product decline for those rules already says "The passages found don't support this answer." The fix gives the release the same split: **bannerkept.patch** (sha256 b3cc02eb...) on the CMP30OFF code, with 2 new vitest cases and 1 updated case.

## 1. Condition (litepacks tree src/routing/answer.ts, sha 0d1ac07d; same code in bench-app/engine 4bb154a6)
- The switch is deps.compactDeclinesOff = "all" (adapter LITEDECLINE_OFF=5, set in topics27/tools/mini_gen_dump.sh) or setBenchCompactDeclinesOff(true) (BOAR Bench engineOverrides.compactDeclinesOff).
- The model must be compact: isCompactModel = answerTier "compact" or size <= 1.6e9 B. Qwen3-1.7B Q4_K_M is 1.11e9 B.
- release(rule) records grounding:compact-decline-released-<rule>. On the first release it emits a weak_sources warning with COMPACT_DECLINE_RELEASED_WARNING. If text remains, the answer becomes that line + "\n" + text.
- The five rules:
  - no-source: fromMemory, nothing kept.
  - false-claim.
  - all-citations-removed: CT-1 removed every [n], not multipass, not health.
  - uncited-with-sources: sources.length > 0, no [n] after attribution, not multipass, not health, declinesOff "all".
  - uncited.
- One string for all five rules: "Not found in this phone's offline library. From the model's memory, may be wrong:".
- Grep: the string is in 0/27 prompts (topics27/gen/prompts.jsonl). It is absent from wt/engfix src (5f46417f), wt/pr1 and boar-app.
- wt/engfix has no release path. Its compact model declines with the correct text: "The passages found don't support this answer." when sources were kept, "I didn't find this in this phone's library." when none were kept. The tests for that are gate 1724fd5 and Boar (A).

## 2. Counts (tools/count_banner.py; "on-topic" = kept, i.e. passed the engine's topic guard; also max kept similarity >= ANSWER_MIN_SIMILARITY 0.70 and a crude question-word / kept-title match)
| set | n | banner | banner, kept >= 1 | of those sim >= 0.70 | title match | banner, kept 0 | rule 4 uncited-with-sources | rule 3 all-citations-removed |
|---|---|---|---|---|---|---|---|---|
| TOPICS27 gen (1.7B Detailed) | 27 | 11 | **10** | 10 | 9 | 1 (b13, no-source) | 10 | 8 |
| SEFIX MAIN sefix124-main-s42 (1.7B Succinct) | 97 | 38 | **37** | 23 (14 lexical-only kept, similarity 0) | 32 | 1 (vit-hum-003, no-source) | 37 | 6 |

- The TOPICS27 reading's 9 are q8 b1 b3 b4 b5 b8 b11 b16 b18. The 10th is b15: Heian period / History of Japan kept, the Kyoto anchor dropped. b18's single Cheetah chunk fails the crude title match only on wording.
- Every banner with chunks kept goes through rule 4 on both sets: 10/10 and 37/37. Neither similarity nor persona explains it. Succinct shows the same thing at 37/97.

## 3. Cause
- Ruled out:
  - The similarity floor: every kept chunk passed it.
  - The Detailed persona: Succinct MAIN has it too.
  - The uncited-warning path: that one writes "No offline source backs this answer." as an event, not as text.
  - Model copying: the string is in no prompt.
- The cause is the release-line wording. The CMP30OFF patch (r4to 10-20: "answer with a warning instead of declining") replaced five declines, which had two different texts, with one text. That text is right for no-source and uncited, and false for rules 3 and 4, where passages were kept and shown.
- The release itself is right: the 1.7B's sentences are not backed by the kept chunks. The Haiku audit puts TOPICS27 at 0.468 unsupported. CITEFIX found that CT-1 removals are a support problem, not a numbering one. So only the "Not found" clause is false.

## 4. Fix (bannerkept.patch, on the CMP30OFF code)
- New COMPACT_DECLINE_RELEASED_WARNING_FOUND = "The passages found don't support this answer. From the model's memory, may be wrong:".
- Its first sentence is the product decline's own reviewed text for these rules (Quill 892c049). No new wording.
- release(rule, found) picks the line on the first release, for both the warning event and the text prefix:
  - all-citations-removed and uncited-with-sources: found = true.
  - false-claim: found = sources.length > 0.
  - no-source and uncited: keep "Not found ...". uncited is the product's "didn't find" rule.
- Not changed: English only, like the existing line. Released or not, the rules, the codes, and the declinesOff-unset path are as before.

## 5. Tests (src/routing/answer.test.ts)
- New: "BANNER-KEPT: a released decline with a kept on-topic source never says 'Not found' (CT-1 removed every [n], and no [n] at all)". It checks the FOUND line on the text and the warning event, the sources event present, and no "declined".
- New: "BANNER-KEPT: a released decline with nothing usable kept keeps the 'Not found in this phone's offline library' line". It checks retrieved [] and [WALIPINI], and the no-source code.
- Updated: CMP30OFF "uncited with sources (rule 4) and all citations removed (rules 3+4)" now expects the FOUND line.
- Without the fix (export stub only): 2 failing. With the fix: answer.test.ts 161/161.
- Full suite on the bench-app/engine tree copy, with boar-app node_modules: 1204 passed, 1 failed, 11 files failed. The baseline without the patch has the same 11 files and the same 1 test failing (1202 passed): plugins/ and scripts/ are not in an engine tree. tsc shows no answer.ts errors.
- The patch applies to the litepacks tree (offsets +94).

## 6. Commits
- wt/engfix: **no commit**. The mechanism is not there, and porting CMP30OFF onto engfix-1023 would be a product-policy change, not this fix.
- rnd: this folder, plus bannerkept.patch, its sha256 and tools/count_banner.py. Sha in the QUEUE row.
- Apply it as a new arm: bench-app via scripts/engine.sh with cmp30off+batchret+bannerkept as one patch, and the desktop litepacks tree via git apply.

## 7. What a replay must confirm on answers
- 0-LLM replay of the stored generations through the patched tree. Expected: the 10/27 and 37/97 kept-chunk banners switch to the FOUND line, b13 and vit-hum-003 keep "Not found", and no other text changes.
- Before any judged run, boar-eval/harness/judge-v2.mjs WARNING_LINES (the ruler strips that one fixed line) must list the FOUND line too. Otherwise the judge reads the warning as answer text. The ruler is frozen (v0.4), so this needs a ruler decision. It was not edited here.
- The same applies to the analysis scripts that hard-code the old line: cb17_table.py, ce-opus-check/analyze.py, chunkclean/cc_agg.py, citefix/apply.mjs and inventory.py.
- On the phone (BOAR Bench): the chat warning is the same weak_sources event with the new message. Check that the UI shows it. The native Kotlin RC1 has no warning line, so it is not affected.
