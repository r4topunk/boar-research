# Model-usage audit: context assembly for Qwen3-1.7B (2026-10-20)

TL;DR
- The prompts are faithful. A stub-server capture of the LITEPACKS runs matches the real traces exactly: 302/302 prompt token counts (llama-server /tokenize of the rendered template = trace promptTokens), and kept chunks and context/headpass codes are identical on 560/560 items. The template, the context placement (system message, as Qwen-Agent does) and the `<think></think>` empty block are correct.
- **HIGH: the X2b append path bypasses the grounding check.** On K1 MAIN, 19/75 generated prompts (25 %) carry only X2b-appended chunks after grounding had already returned `grounding:no-good-source`. These chunks are off-topic: "What is d/acc?" gets Digital-to-analog converter, Mozi gets Camera obscura, garlic sauté gets Scrambled eggs, credit card gets Captain Jack Harkness. The model is told to "use the context". CE on these prompts is 10/19, mean correctness 1.74 against 2.35 on the rest. On the 180 self-tests this happens on 33/152 (K1) and 31/152 (K3) prompts. The same chunks also make the item count as "source kept", which inflates the ruler's planned retrieval coverage.
- **MEDIUM: X2b carries most of the context, and it puts the answer late.** On K1/K3, appended chunks make up 69-70 % of the context characters. On the 61 pack-matched self-tests (K3), the gold quote reaches the prompt on 43/61 items. Of 72 quote hits, 47 sit in appended chunks and 25 in compressed ones; 17 are at [1] and 19 in the last chunk. The sentence compressor alone mostly drops the fact sentence.
- **MEDIUM (pack content, not assembly): templates were stripped during the pack build, which leaves holes in facts.** In simplewiki, 1.8 % of the sampled articles have a hole ("Its height is .", "Bitcoin was invented by someone using the name ."). In Wikivoyage (the K0 default kit), 6.1 % have a hole and 17 % have nameless list items: "Cities" lists lost the {{marker}} names, so 5.2 % of all list items are empty, and 2.1 % of chunks are affected. Inside today's prompts the exposure is 20/562 simplewiki chunks and 1/117 Wikivoyage chunks. top100k: 0.4 % (noise).
- OK: mid-sentence cuts are rare (6/968 distinct chunks, mostly template holes), the quote truncation that compression causes is rare (2 partial vs 72 found), and the context fits the window (max 1388 tokens of 4096).

## Method (0 generation, 0 judge, 0 paid)
- `context-tools/stub_server.py`: fake llama-server (/health, /props, a fixed SSE reply). The real LITEPACKS adapter (`be/adapter-litedecline.ts`, tree be-0cfd4a77-cut7-litepacks, same env as `arms/litepacks/tools/run_lp.sh`) runs with `--server-url` to the stub and `--dump-prompts`. Runs: lp-K0/K1 v01+cm (MAIN 97; 75 generated prompts each), lp-K1-st, lp-K3-st (180; 152 generated each). MacBook, about 4 min total.
- Parity (`context-tools/parity.py`): kept titles, context/headpass/no-good-source codes and the generated-item set are identical to the LITEPACKS traces on all 560 items.
- Tokens (`context-tools/tok.py`): Qwen3-1.7B Q4_K_M on a tokenize-only llama-server b11010 (/apply-template + /tokenize, stopped after). Rendered totals equal the trace promptTokens on 302/302.
- Analysis: `context-tools/analyze.py` (writes `analysis.json` and `rows.json`) and `artefacts.py`, plus inline sqlite+zstd scans of the packs (150 random blocks per pack, seed 7).

## Code path (fast tier, 1.7B)
- Budget: `src/routing/depth.ts:92-95` `quickBudget`: lookup k 3 / 450 tok, other k 4 / 700 tok (approxTokens = chars/4). `answer.ts:1042-1052` caps it by ctx − maxTokens − 512 − 256 (thinking). It does not bind at ctx 4096.
- Compression: `src/rag/compress.ts:174-264` `compressContext` scores sentences by IDF term coverage and drops chunks under 0.5× the best chunk. Each kept chunk = its first sentence + the best sentences (≤ 4), restored to document order and joined with " " (no ellipsis for gaps). The ranking is by chunk relevance.
- Grounding: `answer.ts:1072-1078` `onSubject` filter on the compressed sources; `grounding:no-good-source` when none survive.
- **X2b append**: `answer.ts:1109-1168`. It reads `retrievedRaw` (before the substantive filter and grounding), appends head-pass chunks 1-2 of the first user-pack article plus up to 2 dense candidates (HEADPASS_MAX_APPEND 4, `denseCandidates.ts:40-63`), and stays within 600 tokens counted on the JSON of the messages. Appended chunks skip `onSubject` and compression (only health questions filter them, by `onHealthTopic`). It runs whether or not grounding kept anything.
- Formatting: `src/rag/pure.ts:367-399` `assembleChatMessages`. System = persona + CONTEXT_INSTRUCTION + GROUNDING_INSTRUCTION + "\n\nContext:\n" + `[n] Title\nbody` blocks joined by blank lines. User = question + "(Response style: …)". Pack chunk bodies open with "Section > Sub: ".

## Measurements

| Set (prompts) | promptTokens mean / p50 / p90 / max | system head tok (share) | chunks/prompt | appended share of ctx chars | prompts with only appended chunks (after no-good-source) |
|---|---|---|---|---|---|
| MAIN K0 (75) | 384 / 295 / 624 / 796 | 187-215 (51-68 %) | 1.0 | 0 (X2b inert: no-user-pack + nosidecar 66/66) | 0 |
| MAIN K1 (75) | 729 / 762 / 1053 / 1273 | 212-225 (28-46 %) | 3.5 | 0.689 | **19 (CE 10/19; corr 1.74 vs 2.35 rest)** |
| st180 K1 (152) | 741 / 762 / 1027 / 1388 | 222 | 3.6 | 0.695 | 33 (CE 12/33) |
| st180 K3 (152) | 782 / 795 / 1074 / 1388 | 222 (33 %) | 3.7 | 0.701 | 31 (CE 9/31) |

Gold quote placement (selftest `in_pack_facts` quotes, 61 generated pack-matched items, 158 quotes):

| Arm | items with any quote in prompt | quotes found full / partial | in compressed / appended | at [1] / in last chunk (n>1) | correctness by first-quote slot |
|---|---|---|---|---|---|
| K1 (simplewiki only) | 20/61 | 29 / 2 | 20 / 11 | 11 / 4 | absent 2.67 (40), pos1-comp 3.07 (7), later-app 2.64 (7) |
| K3 (all 4 packs) | 43/61 | 70 / 2 | 25 / 47 | 17 / 19 | absent 2.53 (17), pos1-comp 3.36 (11), later-app 3.19 (26), pos1-app 2.88 (4) |

The slot cells are small (n 3-26), so read them as leads. A late or appended quote still scores about as well as one at [1].

Fragments: 6/968 distinct chunks start mid-sentence (strict check). The loose check flagged about 10 %, but those were infobox "key: value;" rows and bullet lists, not cuts. 48/75 K1 MAIN prompts number the same article under two [n] (compressed lead plus appended neighbours).

## Findings

### F1 (high): X2b-appended chunks bypass grounding and fill "no source" prompts with off-topic text
- Where: `answer.ts:1109-1168`. The guard at 1113 is `(packHeadPass === "a2" || denseAppend) && !multipass && retrievedRaw.length`, with no condition on the grounding outcome. `packHeadPass` reads `retrievedRaw` from before the `onSubject` filter.
- Evidence: listed in the TL;DR. Paired K0 (no context) against K1 (only appended context) on the same 19 items: 1.89 vs 1.74. That is within noise and the decoding differs, but it is not positive. Examples: vit-cry-007 "What is d/acc?" → [Digital-to-analog converter, Analog-to-digital converter]; lan-rsn-005 rivers → [Gilgit-Baltistan ×2]; st-qa-cooking-se-019 garlic → [Scrambled eggs ×2]; st-qa-money-se-002 → [Captain Jack Harkness ×2, Credit card, Advance-fee scam].
- Effect on today's arms: every K1 screen (SHORTCTX, QUOTEFIRST, OCCRAG-K1) and LITEPACKS K1-K4 ran with these contexts. SHORTCTX ("first 2 sources in order") keeps mostly these chunks on such items. OCC-RAG's "faithful refusals" on K1 are partly correct refusals of irrelevant text. In the ruler (RULER-SPEC-v1), "retrieval coverage = a source kept at run time" counts these 25 % as covered unless coverage is read from the pre-append grounding code.
- Cheapest test (0 gen): recompute coverage and U-ref/U-noref splits counting `grounding:no-good-source` items as uncovered. Then 1 screen: gate X2b on grounding success (`sources.length > 0` before the append), on K1 screen 37 vs the mini control.

### F2 (medium): the answer sentence reaches the 1.7B mostly through late, uncompressed appended chunks
- On K3, 47/72 quote hits come from X2b chunks and only 17 sit at [1]. `compressContext` keeps ≤ 4 IDF-ranked sentences per chunk and often drops the fact sentence. X2b re-adds whole neighbour chunks after the compressed ones, so the fact sits at position 3-5 of 4-5 chunks, or last (19/72).
- Qwen gives no ordering rule. Small-model "lost in the middle/last" effects are plausible, but the slot-correctness table shows no clear penalty (later-app 3.19 vs pos1-comp 3.36, n 26/11).
- Test (0 gen first): on the stub capture, re-rank so the chunk with the highest query-term coverage goes first. Count how often the quote moves to [1] before spending a screen.

### F3 (medium; pack build): template stripping erased numbers and names in simplewiki and Wikivoyage
- simplewiki v3proto 99bcec30: 119/6626 sampled articles (1.8 %, narrow regex, lower bound). Examples: Manaslu "Its height is .", Zaatari "covers an area of about .", Pentane "chemical formula of .", Bitcoin "invented by someone using the name ." The Bitcoin chunk is appended to 8 bitcoin self-tests.
- wikivoyage ff8595e3 (K0 kit): 81/1336 articles with holes (6.1 %). 229/1336 (17 %) have nameless list items, and 1676/32233 list items are empty (5.2 %, e.g. Namur "## Cities" = six empty bullets). This is 2.1 % of chunks.
- Prompt exposure today is low (simplewiki 20/562 distinct prompt chunks, Wikivoyage 1/117), so this is not a likely cause of today's NOs. It does remove the facts that numeric and travel "which towns" questions need. top100k is clean (0.4 %).
- Test: grep the pack builders for {{convert}}/{{marker}}/{{nihongo}} handling, then rebuild one pack and replay retrieval (no LLM).

### F4 (low): the fixed system boilerplate is half of the K0 prompt
- The persona + citation + device/alarm GROUNDING_INSTRUCTION head is 187-225 tokens, 51-68 % of K0 prompts. With prefix KV this is no latency issue, but it is a lot of instruction text about devices and greetings for a 1.7B answering knowledge questions. B-HONEST changed this text without effect, so it is a low priority.

### F5 (low): the same article appears under several [n] in 48/75 K1 prompts
- The compressed lead plus appended neighbours each get their own number. Citation checks and "cite by number" still work, but the context is longer and repeats the title.

## Checked and OK
- Chat template: Qwen3 ChatML via `--jinja`. llama-server `--reasoning off` renders `<|im_start|>assistant\n<think>\n\n</think>\n\n` even without `chat_template_kwargs`, which is the vendor's non-thinking form.
- Context in the system message: matches Qwen-Agent (`assistant.py` `_prepend_knowledge_prompt`: "# Knowledge Base" appended to messages[0]). No Qwen-documented numbering or format requirement is violated.
- Prompt token parity: rendered = trace 302/302. No hidden truncation: max 1388 tokens of ctx 4096, budgets 450/700 + 600 X2b.
- Compression: sentence-level, so no mid-word or mid-sentence cuts (6/968, mostly F3 holes). Quote partially cut in only 2/74 found.
- K0 arms (B-HONEST, GREEDY, VENDORSAMP, LOGPROB): X2b inert (no user pack, no sidecar). Those NOs are not affected by F1/F2.
- Mini/MacBook: retrieval and context identical 37/37 and 97/97 per SCREENS.md. The capture confirms the context is deterministic.

## UNKNOWN
- Whether F1 moves U on K1: the paired 19-item comparison is confounded by decoding divergence and judge noise.
- How the Android app (llama.rn) uses X2b: whether packDense2 "append-budget" is on in the shipped settings was not checked here.
