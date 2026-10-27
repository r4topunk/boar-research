# CHUNKCLEAN (2026-10-21): a hand-cleaned 1-3 sentence fact chunk at [1] lifts the 1.7B by +0.031 [-0.009, +0.073] over the raw pack chunk -> INCONCLUSIVE (indicative, n 30)

TL;DR (criterion `CHUNKCLEAN-criterion.md` sha256 4cd6bbf7, committed c956bb89 before generation; Haiku 5.5-low judge.v1-low N 4 both orders; 102 Haiku calls of the 200 cap; 60 generations on the mini; 0 Opus, 0 paid)
- **dU C - R = +0.031 [-0.009, +0.073]** (U 0.458 vs 0.427). Pass needed +0.05 with CI low > 0; kill was < +0.02. Neither: **inconclusive**. Direction positive, size at most about +0.07.
- **dU P - R = +0.013 [-0.023, +0.051]**: putting the clean sentences in front of the full chunk does not help. Repeating the fact inside a long passage gives nothing.
- vs the mini K3 control (no oracle): C +0.045 [-0.006, +0.100], P +0.028, R +0.015. Even the best case (perfect retrieval + a hand-cleaned chunk) moves the 1.7B < +0.05 on real items.
- **The ORACLE-REAL lead does not hold up.** The 6 manual-gold items (already clean key-fact chunks, +0.106 in ORACLE-REAL vs control): C - R **-0.031** [-0.117, +0.047]. Shortening those chunks did not help. Most of the gain is on the 24 lexical golds, **+0.047 [+0.004, +0.095]**, and on the P-label golds (fact half-stated in a noisy chunk), **+0.070 [+0.008, +0.143]**, n 13. These are subgroups (report only), and the result is the reverse of the "clean manual chunk" story.
- Citation [1]: R 15, C 15, P 13 of 30. Any citation: 21 / 25 / 21. Warned (memory-warning opener): R 8, **C 4**, P 8. With a short clean [1], the 1.7B cites more often and opens with the memory warning less often (see CE below).
- CE-unwarned (confident wrong, unwarned): R 1, C 3, P 2 (control 3). The 3 C cases (lan-rsn-004, vit-cry-006, vit-hum-004) are answers that were **warned and wrong in R**. In C they stay wrong but lose the warning. So part of the drop in warned answers (8 -> 4) is a wrong answer losing its honest flag, not a fix. Small n.
- Prompt tokens mean: R 1041, **C 908 (-13 %)**, P 1097.
- Reading: chunk construction is at most a small lever (C - R between -0.01 and +0.07). It is not the main thing the 1.7B misses on these items. Per item C beats R on 17, ties on 5 and loses on 8. Where the 1.7B fails, it fails in every shape: lan-rsn-004, vit-cry-006 and vit-hum-004 stay at U 0.20-0.24 with the fact first and clean, and in C they drop the warning too. The binding stage stays the reader (ORACLE-REAL KILL; arXiv 2603.11513 direction). One cheap move: a short key-sentence index (the clean span) cuts about 130 prompt tokens and halves the warned share (partly by unflagging wrong answers), which is maybe worth one main-97 replay arm once a 0-LLM extractor exists. Not a bar lever.

## Method (as frozen)
- Items: the 30 ORACLE-REAL items (`items.ids`; 17 Y / 13 P gold; 24 lexical / 6 manual).
- R = the ORACLE-REAL oracle arm (gold chunk forced to [1], full text), reused as is: same mini, base tree, requests and seed.
- C = passage [1] body = section prefix + the clean text: 1-3 verbatim sentences (key-facts or spec tables: up to 4 verbatim lines) of the same chunk, with no template residue and no added words. Extracted by hand (0 LLM). Every span is checked to be a verbatim substring (`tools/build_arms.py`). Clean length median 254 chars vs chunk median 814.
- P = section prefix + clean text + blank line + the original chunk text.
- Patch `chunkclean.vs-litepacks.patch` = the ORACLE-REAL patch + optional `orig`/`text` in the oracle entry (suffix replace). Gate: `oracle:text-replaced` on 30/30 for both C and P, 0 mismatches, 0 errors.
- Judge: only answer texts with no judged twin (C 26, P 25 ids). U = ratio of sums, paired item bootstrap B 2000, seed 11.

## Per item (U item = s/sref; corr = judge correctness, both-order mean; lab/src = gold label / l(exical) or m(anual); c1 = cites [1]; W = warned)
| item | gold | lab/src | K3 | chars chunk -> clean | R U / corr | C U / corr | P U / corr | C flags | P flags |
|---|---|---|---|---|---|---|---|---|---|
| lan-cmp-005 | simplewiki-en:34543 | P/l | S3 | 763 -> 144 | 0.35 / 2.0 | 0.85 / 4.5 | 0.50 / 2.0 |  |  |
| lan-exp-001 | factbook:5753 | Y/m | S4 | 1027 -> 291 | 0.59 / 3.5 | 0.53 / 4.0 | 0.57 / 4.0 |  |  |
| lan-exp-002 | factbook:7481 | Y/l | S5 | 1083 -> 181 | 0.57 / 4.0 | 0.59 / 4.5 | 0.67 / 5.0 | c1 | c1 |
| lan-exp-003 | factbook:1009 | Y/l | S5 | 992 -> 227 | 0.63 / 4.0 | 0.72 / 4.5 | 0.76 / 4.5 | c1 | c1 |
| lan-exp-004 | simplewiki-en:222381 | Y/l | S5 | 749 -> 132 | 0.37 / 2.5 | 0.53 / 4.0 | 0.37 / 2.5 | c1 | W |
| lan-exp-005 | simplewiki-en:9543 | Y/m | S5 | 1000 -> 286 | 0.53 / 4.0 | 0.33 / 2.5 | 0.53 / 4.0 | W | c1 |
| lan-exp-007 | factbook:9181 | Y/m | S4 | 814 -> 119 | 0.45 / 2.5 | 0.55 / 3.5 | 0.55 / 3.5 |  |  |
| lan-hlt-001 | simplewiki-en:15581 | Y/l | S4 | 751 -> 223 | 0.54 / 3.5 | 0.57 / 4.0 | 0.48 / 3.0 |  | c1 |
| lan-hlt-002 | medlineplus-en:1520 | Y/l | S5 | 451 -> 144 | 0.60 / 5.0 | 0.60 / 5.0 | 0.60 / 5.0 | c1 | c1 |
| lan-hlt-003 | firstaid-en:5004 | Y/l | S5 | 1098 -> 313 | 0.47 / 3.0 | 0.53 / 4.0 | 0.53 / 3.5 | c1 | c1 |
| lan-ref-002 | simplewiki-en:14188 | P/l | S5 | 571 -> 324 | 0.69 / 5.0 | 0.69 / 5.0 | 0.69 / 5.0 |  |  |
| lan-ref-003 | simplewiki-en:112679 | P/l | S4 | 464 -> 176 | 0.40 / 2.0 | 0.40 / 2.0 | 0.76 / 5.0 |  |  |
| lan-rsn-001 | simplewiki-en:19275 | P/l | S4 | 415 -> 261 | 0.43 / 2.5 | 0.45 / 2.5 | 0.46 / 2.5 | W | c1 |
| lan-rsn-003 | simplewiki-en:56214 | P/l | S4 | 238 -> 139 | 0.21 / 1.0 | 0.48 / 3.0 | 0.29 / 1.5 | c1 | W |
| lan-rsn-004 | simplewiki-en:184755 | P/l | S4 | 932 -> 177 | 0.20 / 1.0 | 0.23 / 1.0 | 0.20 / 1.0 | c1 | W |
| lan-rsn-006 | simplewiki-en:96344 | Y/l | S5 | 1146 -> 293 | 0.57 / 4.5 | 0.43 / 3.5 | 0.53 / 4.0 | c1 | c1 |
| vit-cry-002 | crypto:19578 | Y/m | S4 | 833 -> 319 | 0.43 / 3.0 | 0.50 / 3.0 | 0.43 / 3.0 | c1 | c1 |
| vit-cry-003 | crypto:41530 | P/l | S4 | 575 -> 388 | 0.24 / 1.0 | 0.46 / 3.0 | 0.30 / 2.0 |  |  |
| vit-cry-004 | crypto:16592 | P/l | S4 | 592 -> 285 | 0.33 / 2.0 | 0.40 / 3.0 | 0.27 / 2.0 |  |  |
| vit-cry-005 | crypto:27321 | P/m | S1 | 961 -> 141 | 0.38 / 2.5 | 0.26 / 1.5 | 0.30 / 2.5 | W | W |
| vit-cry-006 | crypto:41922 | P/l | S4 | 595 -> 447 | 0.20 / 1.0 | 0.23 / 1.5 | 0.20 / 1.0 | c1 | W |
| vit-cry-008 | crypto:41305 | Y/l | S4 | 357 -> 143 | 0.61 / 3.0 | 0.70 / 4.0 | 0.40 / 2.0 |  | W |
| vit-cry-009 | crypto:14404 | P/m | S3 | 214 -> 72 | 0.25 / 1.5 | 0.27 / 2.0 | 0.23 / 1.5 |  |  |
| vit-cry-010 | crypto:40957 | Y/l | S3 | 678 -> 254 | 0.47 / 3.0 | 0.30 / 2.5 | 0.27 / 2.0 | W | W |
| vit-cry-011 | crypto:47608 | P/l | S4 | 544 -> 185 | 0.29 / 2.0 | 0.28 / 2.0 | 0.39 / 2.5 | c1 | c1 |
| vit-hlt-001 | wikivoyage-en:84351 | Y/l | S3 | 876 -> 371 | 0.28 / 2.0 | 0.28 / 2.0 | 0.28 / 2.0 | c1 | c1 |
| vit-hlt-002 | wikivoyage-en:7446 | Y/l | S3 | 904 -> 301 | 0.70 / 4.5 | 0.70 / 4.5 | 0.70 / 4.5 |  |  |
| vit-hlt-003 | medlineplus-en:796 | Y/l | S3 | 988 -> 212 | 0.50 / 3.0 | 0.48 / 3.0 | 0.39 / 2.5 | c1 | W |
| vit-hum-004 | simplewiki-en:68816 | P/l | S4 | 1276 -> 382 | 0.20 / 1.0 | 0.24 / 1.0 | 0.20 / 1.0 | c1 | c1 |
| vit-trv-003 | wikivoyage-en:252078 | Y/l | S4 | 1052 -> 310 | 0.31 / 2.0 | 0.30 / 2.0 | 0.35 / 2.0 | c1 | c1 |

Notes: temperature 0.7 at seed 42, so any change to the prompt resamples the answer. Part of the per-item swings is sampling noise, not the chunk: lan-ref-003 P 0.76 vs C 0.40 with the same clean text in both, and lan-exp-005 C 0.33 vs P 0.53. The two health items (vit-hlt-001/002) answer with an extractive excerpt, and their answers are unchanged across arms.

## Extraction log (item, source chunk, clean text = C's passage [1] body after the section prefix; also `extraction-log.jsonl`)
- **lan-cmp-005** (pack:boar-simplewiki-en:34543, 763 -> 144 chars): Some of the crocodiles from Australia live in salt water. These saltwater crocodiles are normally bigger than the ones that live in fresh water.
- **lan-exp-001** (pack:boar-factbook:5753, 1027 -> 291 chars): Location: Southeastern Asia, islands between Malaysia and Indonesia / Languages: English (official) 48.3%, Mandarin (official) 29.9%, other Chinese dialects (includes Hokkien, Cantonese, Teochew, Hakka) 8.7%, Malay (official) 9.2%, Tamil / Independence: 9 August 1965 (from Malaysian Federation)
- **lan-exp-002** (pack:boar-factbook:7481, 1083 -> 181 chars): Capital: Podgorica / Location: Southeastern Europe, between the Adriatic Sea and Serbia / Independence: 3 June 2006 (from the State Union of Serbia and Montenegro) / Currency: euros (EUR)
- **lan-exp-003** (pack:boar-factbook:1009, 992 -> 227 chars): Capital: Nairobi / Location: Eastern Africa, bordering the Indian Ocean, between Somalia and Tanzania / Languages: English (official), Kiswahili (official), numerous indigenous languages / Independence: 12 December 1963 (from the UK)
- **lan-exp-004** (pack:boar-simplewiki-en:222381, 749 -> 132 chars): Kyoto was Japan's capital city from 794 until the late-19th century. In 1994, UNESCO listed parts of Kyoto as a World Heritage Site.
- **lan-exp-005** (pack:boar-simplewiki-en:9543, 1000 -> 286 chars): The Sahara Desert is about 9,200,000 square kilometers (3.6 million square miles) in size. It runs through many countries including Morocco, Algeria, Tunisia, Libya, Egypt, Mauritania, Mali, Niger, Chad, and The Sudan. After the last ice age it became more fertile, then dried up again.
- **lan-exp-007** (pack:boar-factbook:9181, 814 -> 119 chars): Capital: Nuuk / Population: 57,751 (2024 est.) / Independence: none (extensive self-rule as part of the Kingdom of Denmark)
- **lan-hlt-001** (pack:boar-simplewiki-en:15581, 751 -> 223 chars): Vegetarians as well as vegans usually have to take supplement tablets to make up for missing nutrients, such as vitamin B12. They have to do this to prevent nerve and brain damage, fatigue, and to maintain their appearance.
- **lan-hlt-002** (pack:boar-medlineplus-en:1520, 451 -> 144 chars): For adults / Get at least 150 to 300 minutes of moderate-intensity or 75 to 150 minutes of vigorous-intensity aerobic physical activity each week.
- **lan-hlt-003** (pack:boar-firstaid-en:5004, 1098 -> 313 chars): No, mosquito does not spread HIV-AIDS. Blood containing AIDS virus goes into the stomach of mosquito and gets digested there. some Anopheles species like Stephensi to spread Malaria, Aedes aegypti to spread Dengue fever, Chikun guniya & Yellow fever, some Culex species to spread Filariasis & Meninjo encephalitis
- **lan-ref-002** (pack:boar-simplewiki-en:14188, 571 -> 324 chars): The North won control of almost all of the Mississippi River by capturing the cities along the river in the fall of 1862 and the spring of 1863. The siege continued until July 4, 1863, when the Confederates there surrendered to Grant. That was one of the turning points in the war by dividing the Confederacy into two parts.
- **lan-ref-003** (pack:boar-simplewiki-en:112679, 464 -> 176 chars): His second space flight was in Apollo 11 where he was the command module pilot. While he kept going around the Moon, Neil Armstrong and Buzz Aldrin landed on the lunar surface.
- **lan-rsn-001** (pack:boar-simplewiki-en:19275, 415 -> 261 chars): Another astronaut, Neil Armstrong, said that on the Moon, it was very clear that the wall was not visible. The Great Wall has shown up in some photos taken from space, but scientists are sure it is not possible for astronauts to see the wall without binoculars.
- **lan-rsn-003** (pack:boar-simplewiki-en:56214, 238 -> 139 chars): It is often called the second-fastest land animal, second only to the African cheetah, and it can keep up high speeds longer than cheetahs.
- **lan-rsn-004** (pack:boar-simplewiki-en:184755, 932 -> 177 chars): The population has been growing since the end of the Black Death, around the year 1400. At the beginning of the 19th century, it had reached roughly 1,000,000,000 (one billion).
- **lan-rsn-006** (pack:boar-simplewiki-en:96344, 1146 -> 293 chars): The Hundred Years' War (French: Guerre de Cent Ans; 1337–1453) was a long conflict between the kingdoms of England and France. Even though it is called the Hundred Years' War, it lasted for 116 years, but the conflict was interrupted by things like the Black Death and several years of truces.
- **vit-cry-002** (pack:boar-crypto:19578, 833 -> 319 chars): FOCIL implements a robust mechanism to preserve Ethereum’s censorship resistance properties by guaranteeing timely transaction inclusion. In each slot, a set of validators is selected as inclusion list (IL) committee members. Attesters only vote for the proposer's block if it includes transactions from all stored ILs.
- **vit-cry-003** (pack:boar-crypto:41530, 575 -> 388 chars): Today, high disk space requirements is the main barrier preventing universal access to nodes. At the time of writing, a fast 2TB SSD is recommended for running a full Ethereum node. For a node that does not prune any older data, the storage requirement grows at around 14GB/week, and archive nodes that store all data since genesis are approaching 12 TB (at time of writing, in Feb 2023).
- **vit-cry-004** (pack:boar-crypto:16592, 592 -> 285 chars): Note that, while `cell_proofs` contain the proofs for all cells, including the extension cells, the blobs themselves are sent without being extended (`CELLS_PER_EXT_BLOB / 2` cells per blob). This is to avoid sending redundant data, which can quickly be computed by the receiving node.
- **vit-cry-005** (pack:boar-crypto:27321, 961 -> 141 chars): Privacy tools have been sanctioned for lacking compliance mechanisms. Compliance-by-exclusion (Privacy Pools): Prove you're NOT in a bad set.
- **vit-cry-006** (pack:boar-crypto:41922, 595 -> 447 chars): quadratic funding mechanisms rely on donations to measure preference for certain options among different public good projects. Each donation counts as a "vote" for a specific project, with projects that receive more votes getting more funds from the matching pool. Using onchain voting makes quadratic funding susceptible to collusion: blockchain transactions are public, so bribers can inspect a bribee’s onchain activity to see how they “voted”.
- **vit-cry-008** (pack:boar-crypto:41305, 357 -> 143 chars): The headline feature is ePBS (EIP-7732), which separates the heavy task of validating network transactions from the task of reaching consensus.
- **vit-cry-009** (pack:boar-crypto:14404, 214 -> 72 chars): MIN_ACTIVATION_BALANCE (32 ETH) / MAX_EFFECTIVE_BALANCE_ELECTRA (2048 ETH)
- **vit-cry-010** (pack:boar-crypto:40957, 678 -> 254 chars): The DAO fork was in response to the 2016 DAO attack where an insecure DAO contract was drained of over 3.6 million ETH in a hack. Some miners refused to fork because the DAO incident wasn't a defect in the protocol. They went on to form Ethereum Classic.
- **vit-cry-011** (pack:boar-crypto:47608, 544 -> 185 chars): In May 2022, Terra's stablecoin UST lost its peg with the US dollar. The subsequent failure of Terraform Labs resulted in the loss of nearly [usage detail removed] billion invested in UST and LUNA tokens.
- **vit-hlt-001** (pack:boar-wikivoyage-en:84351, 876 -> 371 chars): The dreaded Box Jellyfish is a potentially deadly beach hazard between the months of October and May, but less so during the peak travel season. When swimming at local beaches, even in the 'safe' season of June to September, bring vinegar and pour it over the wound if stung. Transport to hospital is a must as the venom of the Box Jellyfish can be deadly - remember CPR.
- **vit-hlt-002** (pack:boar-wikivoyage-en:7446, 904 -> 301 chars): Assume AMS first: it happens to healthy strong people, and if it turns out you are indeed sick with something else, descending to a lower altitude will make it easier for your body to heal anyway. In particular, if you’ve recently ascended, and you have a headache and any other symptom, you have AMS.
- **vit-hlt-003** (pack:boar-medlineplus-en:796, 988 -> 212 chars): Severe dengue is a serious form of the illness. It can cause shock, internal bleeding, and even death. People are more likely to develop severe dengue if they have had dengue before, are pregnant, or are infants.
- **vit-hum-004** (pack:boar-simplewiki-en:68816, 1276 -> 382 chars): He spent his final days as a small-time criminal master in Hobbiton known as Sharkey (from the Orkish Sharkû, meaning "old man"), until he was overthrown in the Battle of Bywater. In the aftermath of that battle Frodo confronted Saruman and exiled him from the Shire, but before he could leave, Gríma killed him by slitting his throat with a dagger, on the very doorstep of Bag End.
- **vit-trv-003** (pack:boar-wikivoyage-en:252078, 1052 -> 310 chars): If you're a little adventurous, rent a motorcycle in Chiang Mai and make the ride up to Pai. But because you never know what lies around the next bend, you're forced to drive conservatively. As a novice rider, expect the trip to take around 5 or 6 hours, including stops at sites and restaurants along the way.

Residue dropped by span choice: Markdown bold (vit-cry-002 FOCIL acronym line; vit-cry-005 "**Compliance-by-exclusion**"), table pipes and backtick values (vit-cry-009), "Ans. (a)" / "(b)When God created..." (lan-hlt-003), "For example," (vit-cry-006), the broken "speeds of up to ." (lan-rsn-003), a truncated "notable earlier dates..." tail (lan-exp-002). Backticked code names in vit-cry-004 were kept: there is no clean sentence in that chunk without them.

## Caveats
- n 30 (indicative), one seed, the Haiku 5.5-low judge compresses gaps, dev items only (bench v0.1 public).
- The extractions are one person's reading (the coordinator subagent), done before any generation and logged. A rule-based extractor would do worse.
- 13/30 golds state only half of the fact (P). On those, "clean" means the best verbatim sentences available, not the full fact.
- Subgroup CIs are post-hoc and not corrected.

## Files
`CHUNKCLEAN-criterion.md` (+ .sha256), `CHUNKCLEAN-budget.md` (preflight form of the cap), `items.ids`, `gold-chunks.json`, `extractions.json`, `extraction-log.jsonl`, `chunkclean.vs-litepacks.patch`, `tools/{dump_gold.py, build_arms.py, oracle-C.json, oracle-P.json, run_cc.sh, judge_cc.sh, cc_agg.py}`, `runs/req/`, `traces/chunkclean-{C,P}-K3-v01gold-s42.traces.jsonl`, `judgments/cc-{C,P}.judgments.jsonl`, `aggregates/chunkclean.json` (sha256 01016690...), `runs/logs/calls.ledger` (102 calls).
Resume: `python3 -I tools/build_arms.py; bash tools/run_cc.sh start|status|fetch C|P; bash tools/judge_cc.sh C|P; python3 -I tools/cc_agg.py aggregates/chunkclean.json`.
