# TOPICS27 criterion (FROZEN 2026-10-23 before any run; never edited after; addenda go to TOPICS27.md)

Question (maintainer, incoming9 2026-10-21): for the 27 RC1 "Research Topics" (q1 q2 q4 q7 q8 q9, b1..b21; EN text = the question), (1) does wiki-vital5 hold articles that support a good answer, (2) is the Qwen3-1.7B Detailed answer good and free of invented facts, (3) which topics to swap for 1.5-1.7B models.
Public set (the app maintainer's own strings), dev use only. Opus 0, paid API 0, phone 0, no pushes. Never read blind/, rnd/veil/, bench/v0.4.

## System (bench engine, not the app maintainer's native pipeline)
Tree = K1 litepacks (kiln-local/be-0cfd4a77-cut7-litepacks on the MacBook for the replay; <runner>/kiln/be-0cfd4a77-cut7-litepacks on the mini for generation, APFS clone per job, no patch). Settings = K1 (quickFirst true, alwaysComplete false, packHeadPass a2, packDense2 append-budget) + personalityId "detailed". Kit = wiki-vital5 only (sha256 d3b87d562baba3489f6878bf99783f50d504db94c347029771e53f6d1aecc666; local copy shared-data/packs/wiki-vital5.sqlite, mini <runner>/kiln/compose/packs-k13/wiki-vital5.sqlite, sha checked), corpus essential (bundled corpus.json 300 + corpus-standard 1000 + corpus-full 4000 articles). Model qwen3-1.7b-q4km, seed 42, --reasoning off, LITEDECLINE_OFF=5, llama-server b11010 CPU -t 4 (lp-screens mini_gen.sh recipe + --dump-prompts), device android ramGb 12, detector :8094 used as in every K1 run.

## Stage 1 (0 LLM)
1a Title presence: case-insensitive exact match of a title against chunks.title in wiki-vital5, and separately against the essential corpus JSON titles. Shipped = wiki-vital5 OR essential corpus.
 - q*: expect titles from in/suggestions.json (`sources[].expect`). Topic PRESENT iff >= 1 expect title is shipped.
 - b*: anchor titles frozen here (my reading before any lookup). Each topic has required groups; PRESENT iff every group has >= 1 shipped title.
   b1 [Natural selection | Charles Darwin | Alfred Russel Wallace | On the Origin of Species]
   b2 [Vaccine | Vaccination | Smallpox vaccine | MRNA vaccine | Smallpox] + [Immune system | Adaptive immune system | Immunity (medicine)]
   b3 [Photosynthesis | Calvin cycle | Light-dependent reactions]
   b4 [French Revolution] + [Industrial Revolution]
   b5 [Fall of the Western Roman Empire | Western Roman Empire | Decline of the Roman Empire]
   b6 [Black hole | Event horizon | Stellar black hole]
   b7 [Napoleon | Napoleon Bonaparte | Napoleonic Wars]
   b8 [Antimicrobial resistance | Antibiotic resistance] 
   b9 [Canberra | Australian Capital Territory]
   b10 [Great Wall of China]
   b11 [Polar bear] + [Grizzly bear | Brown bear]
   b12 [Brazil | Economy of Brazil] + [Russia | Economy of Russia]
   b13 [Mosquito | Mosquito-borne disease]
   b14 [Physical exercise | Exercise | Physical activity | Physical fitness]
   b15 [Kyoto | History of Kyoto]
   b16 [Mount Kilimanjaro | Kilimanjaro]
   b17 [Berlin Wall | Fall of the Berlin Wall]
   b18 [Cheetah]
   b19 [AC power plugs and sockets | Mains electricity by country | Emergency telephone number] (Brazil alone does not count: the topic is plugs, voltage, emergency numbers)
   b20 [Japan | Demographics of Japan | Aging of Japan] + [Germany | Demographics of Germany] + [Population density | Population ageing]
   b21 [Dengue fever | Dengue virus | Dengue]
1b Replay (retrieve-sweep/tools/replay-sweep.ts, the COMPOSE recipe: --tree K1 local, --packs wiki-vital5 local, --corpus essential, --model qwen3-1.7b-q4km --ram-gb 12 --cpu-embed --wide 12 --forward-opts --settings-json K1 settings, --gate search, no --tasks-from (no reference traces; detector absent -> lexical predicate)). Record raw titles, kept (sources) titles, keptFull.
 - q*: IN RAW / IN KEPT iff >= 1 expect title appears in raw / kept (case-insensitive exact).
 - b*: IN RAW / IN KEPT iff >= 1 anchor title (any group) appears; for comparisons also report groups covered. Plus my title reading of the top-6 raw titles (on-topic / partly / off-topic), written to TOPICS27.md BEFORE stage 2 starts.

## Stage 2
Generation: the 27 EN questions, one run, seed 42, on the mini (system above), traces + dumped prompts. Live kept titles are compared with the replay (parity count reported); the live trace is the source of truth for kept and answer.
Sentence split (0 LLM, tools/split.py, frozen with this file): answer text; drop the "Not found in this phone's offline library..." style preamble line only if it is a fixed engine banner (reported, not audited); strip markdown (#, **, leading - * or digit. bullets); split on newlines and on (?<=[.!?])\s+(?=[A-Z0-9"(]); drop units with < 4 words or with no letter; a line of <= 8 words with no terminal punctuation followed by more text is a heading and is dropped.
Support audit (Haiku 5.5-low via boar-eval eval-lib runClaude, the SUPPORT label.mjs client; tools none; JSON schema; N 1 per sentence, original chunk order only). Context = the context block of the answer's own dumped prompt (the chunk text the model saw); if the dump is missing for an item, the replay keptFull with a title-parity note.
System prompt (exact): "You are a strict support auditor. You only judge whether the source chunks contain the information a sentence states. Whether anything is true in the real world is irrelevant."
User prompt (exact; {Q}, {CHUNKS}, {S} substituted):
"QUESTION:\n{Q}\n\nSOURCE CHUNKS:\n{CHUNKS}\n\nSENTENCE FROM THE ANSWER:\n{S}\n\nLabel SUPPORTED if the source chunks state or directly entail everything the sentence claims. Label PARTIAL if the chunks support its main claim but it adds a detail they do not contain. Label UNSUPPORTED if the chunks do not contain its main claim (even if it may be true), or contradict it. Generic framing with no factual claim (an introduction, a transition, advice to see a doctor) is SUPPORTED. Then set invented_specific to true if the sentence states a specific number, date, quantity, name of a person, place, organisation, gas, disease or similar named entity that appears nowhere in the source chunks; otherwise false. Ignore your own knowledge of whether the sentence is true. Reply with the JSON {\"label\": \"SUPPORTED\" | \"PARTIAL\" | \"UNSUPPORTED\", \"invented_specific\": true | false}."
Retry an errored call once; unresolved -> counted as missing and reported. Cap: <= 300 Haiku invocations. If the split yields > 290 sentences, sentences are audited per topic in key order until 290 invocations, and each remaining topic gets ONE batched call with the same instructions over its numbered sentence list (JSON array output), flagged `batched`. Ledger arms/topics27/CALLS.md.
Also 0 LLM: numbers (digit runs, incl. decimals and %) in each sentence absent from the context text -> `num_absent` count (reported beside the Haiku flag).

## Per-topic verdict (frozen, applied mechanically; reason in one line)
unsup = UNSUPPORTED sentences / audited sentences; inv = UNSUPPORTED or PARTIAL sentences with invented_specific true.
1. SWAP if the topic is not PRESENT (stage 1a, shipped = wiki-vital5 OR essential corpus), or (unsup >= 1/3 and inv >= 1), or the answer is empty / declined.
2. else FIX-PACK if not IN KEPT in the live trace (the article ships but retrieval does not deliver it).
3. else KEEP. (A KEEP with unsup >= 1/3 but inv 0, or inv >= 1 with unsup < 1/3, gets a "watch" note.)
Aggregates: titles present x/y (q* expect titles individually; b* topics), PRESENT topics x/27, IN KEPT x/27 (live), sentences total, unsupported share (pooled sentences), invented-specific count, verdict counts.

## Prediction (frozen)
PRESENT 22-25/27 (b19 likely absent; q2/q7/q9 expect titles may sit in the corpus, not vital5); IN KEPT 17-22/27; unsupported share 0.25-0.40 for the 1.7B Detailed (3-5 paragraphs over short intro chunks invites memory filling); SWAP 3-7, FIX-PACK 3-6.

## Caveats to state
Bench engine K1 tree, not the app maintainer's native Kotlin pipeline (NATIVE-PARITY found KB-only retrieval differs); essential corpus may differ from RC1's built-in corpus; Haiku support audit, not a correctness judge (unsupported != false: the 1.7B may be right from memory); one seed; EN only (PT not run); 1.7B only (4B and 1.5B not run).
