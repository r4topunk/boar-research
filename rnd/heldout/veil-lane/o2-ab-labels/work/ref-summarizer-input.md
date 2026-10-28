# Write a one-line reference answer for each question

For each item below you get a question, the grading rubric written for it, the keywords a correct answer must contain (`must_any`: each group needs one hit), and source links. Write ONE line (max ~200 characters) that states the correct core answer, in the question's language, as a reference a grader can compare an answer against. State facts, numbers and names; no hedging, no advice to the grader, no mention of the rubric. If the question is open-ended ("Tell me about X"), give the 2-4 core points the rubric expects.

## vit-cry-001

Question: How would Ethereum protect users' funds if a quantum computer suddenly broke ECDSA?

Rubric:
- Emergency hard fork: roll back blocks after large-scale theft is detected, disable legacy ECDSA-signed transactions from EOAs
- New transaction type where users prove knowledge of their seed/HD-wallet derivation (hash preimage) with a STARK, so hash-based secrets still protect funds
- Longer term: move to quantum-resistant signatures (hash-based or lattice: ML-DSA/SLH-DSA/Falcon) and account abstraction
- Notes funds in addresses that never exposed a public key are safer

must_any: [["hard fork", "hard-fork"], ["stark", "zero-knowledge", "zk", "seed", "preimage"]]

Sources: https://ethresear.ch/t/how-to-hard-fork-to-save-most-users-funds-in-a-quantum-emergency/18901

## vit-cry-002

Question: What is FOCIL (EIP-7805) and what problem does it solve?

Rubric:
- Fork-Choice enforced Inclusion Lists
- A committee of validators each publishes an inclusion list of mempool transactions; the block must include them (enforced via fork choice/attestations)
- Goal: censorship resistance, so a few sophisticated builders cannot exclude transactions
- Relationship to PBS/builder centralization

must_any: [["inclusion list", "inclusion-list", "fork-choice", "forced inclusion"]]

Sources: https://eips.ethereum.org/EIPS/eip-7805

## vit-cry-003

Question: What does EIP-4444 history expiry change for Ethereum node operators, and how much disk does it save?

Rubric:
- Nodes stop serving/storing historical blocks and receipts older than a cutoff; history moves to other distribution (e.g. Portal network, archives)
- Partial history expiry (pre-Merge history) rolled out in July 2025; saves roughly 300-500 GB of disk
- Consequence: syncing a full node fits well under 1 TB (he reports <0.5 TB with aggressive settings)
- Old history is still available from other sources, not deleted from the world

must_any: [["pre-merge", "before the merge", "older than", "prune", "pruning", "portal"], ["300", "500", "re:\\b\\d{2,3}\\s*gb\\b", "terabyte", "re:\\btb\\b"]]

Sources: https://eips.ethereum.org/EIPS/eip-4444, https://blog.ethereum.org/2025/07/08/partial-history-exp, https://x.com/VitalikButerin/status/2103636111260373176

## vit-cry-004

Question: What is PeerDAS, and how can a node check that blob data is available without downloading all of it?

Rubric:
- PeerDAS = peer data availability sampling (EIP-7594), shipped in the Fusaka upgrade
- Blobs are erasure-coded (extended) and split into columns; each node custodies/samples a subset
- If enough random samples are available, the whole data is available with high probability, because any 50% can reconstruct it
- Purpose: raise blob throughput for rollups without every node downloading everything

must_any: [["sampl"], ["erasure", "reconstruct", "extend"]]

Sources: https://eips.ethereum.org/EIPS/eip-7594

## vit-cry-005

Question: What is the difference between Privacy Pools and Tornado Cash?

Rubric:
- Both use zero-knowledge proofs to break the link between deposit and withdrawal
- Privacy Pools adds association sets: a withdrawer proves membership in a set of deposits that excludes known illicit ones, separating honest users from bad actors without revealing their deposit
- Tornado Cash has no such compliance layer, which led to OFAC sanctions (2022, later lifted in 2025)
- Privacy Pools paper co-authored by Vitalik Buterin (2023); privacypools.com is live

must_any: [["association set", "exclude", "proof of innocence"]]

Sources: https://vitalik.eth.limo/general/2025/04/14/privacy.html, https://en.wikipedia.org/wiki/Tornado_Cash

## vit-cry-006

Question: What is quadratic funding, and what is its main weakness?

Rubric:
- Matching funds allocated so a project's total = (sum of square roots of contributions)², favoring many small donors over few large ones
- Origin: Buterin, Hitzig, Weyl, 'Liberal Radicalism' (2018); used by Gitcoin Grants
- Main weakness: collusion and Sybil attacks (splitting one donor into many identities), needs identity/anti-collusion (e.g. MACI, pairwise matching)
- Distinguishes it from quadratic voting

must_any: [["square root", "squared", "sqrt"], ["sybil", "collusion"]]

Sources: https://arxiv.org/abs/1809.06421, https://en.wikipedia.org/wiki/Quadratic_funding

## vit-cry-007

Question: What is d/acc?

Rubric:
- Defensive (also decentralized, democratic, differential) accelerationism, from 'My techno-optimism' (Nov 2023)
- Idea: accelerate technologies that favor defense over offense and decentralization over concentration (biosecurity, cybersecurity, info defense, open hardware)
- Positioned between e/acc and AI-safety deceleration
- Gives at least one concrete example (air filtration/far-UVC, formal verification, ZK proofs, open-source local AI)

must_any: [["defens"], ["decentraliz", "differential", "democra"]]

Sources: https://vitalik.eth.limo/general/2023/11/27/techno_optimism.html, https://vitalik.eth.limo/general/2025/01/05/dacc2.html

## vit-cry-008

Question: What is Glamsterdam and what are its headline features?

Rubric:
- If the corpus covers it: the Ethereum upgrade after Fusaka; meta EIP-7773; headliners enshrined PBS (EIP-7732) and block-level access lists (EIP-7928)
- If not covered: says the offline sources do not describe it and gives the snapshot date
- Never invents features

must_any: [["epbs", "proposer-builder", "proposer builder", "7732", "access list", "7928"]]

Sources: https://eips.ethereum.org/EIPS/eip-7773

## vit-cry-009

Question: I want to stake 10,000 ETH. How many validators did I need before EIP-7251, and what is the minimum after it?

Rubric:
- Before (32 ETH max effective balance): 312 full validators (9,984 ETH), with 16 ETH left over
- After EIP-7251 (Pectra, May 2025): max effective balance 2,048 ETH, so the minimum is 5 validators (e.g. 4×2,048 + 1×1,808)
- States the 32 ETH minimum to activate is unchanged

must_any: [["312", "313"], ["5 validators", "five validators", "re:\\b5\\b"]]

Sources: https://eips.ethereum.org/EIPS/eip-7251

## vit-cry-010

Question: What were the main lessons of the 2016 DAO hack for Ethereum?

Rubric:
- Reentrancy bug let an attacker drain ~3.6 million ETH (June 2016)
- Community hard fork returned funds; the unforked chain continued as Ethereum Classic
- Lessons: smart-contract security (checks-effects-interactions, audits, formal verification), social layer can intervene, 'code is law' debate
- Correct dates (2016)

must_any: [["reentran", "hard fork", "ethereum classic", "recursive call"]]

Sources: https://en.wikipedia.org/wiki/The_DAO

## vit-cry-011

Question: Why did Terra (UST/LUNA) collapse in 2022?

Rubric:
- UST was an algorithmic stablecoin kept at $1 by minting/burning LUNA, not by reserves
- Anchor protocol paid ~20% yield, attracting demand that was not sustainable
- May 2022: large withdrawals/sales broke the peg; redemptions minted huge amounts of LUNA, hyperinflating it (death spiral)
- Tens of billions of dollars of value wiped out; Do Kwon later charged

must_any: [["algorithmic"], ["peg"]]

Sources: https://en.wikipedia.org/wiki/Terra_(blockchain)

## vit-fa-001

[competitor case text removed in v1.1]

## vit-fa-002

[competitor case text removed in v1.1]

## vit-fa-003

[competitor case text removed in v1.1]

## vit-fa-004

[competitor case text removed in v1.1]

## vit-fa-005

[competitor case text removed in v1.1]

## vit-fa-006

[competitor case text removed in v1.1]

## vit-fa-007

[competitor case text removed in v1.1]

## vit-fa-008

[competitor case text removed in v1.1]

## vit-fa-009

[competitor case text removed in v1.1]

## vit-fa-010

[competitor case text removed in v1.1]

## vit-fa-011

[competitor case text removed in v1.1]

## vit-fa-012

[competitor case text removed in v1.1]

## vit-fa-013

[competitor case text removed in v1.1]

## vit-fa-014

[competitor case text removed in v1.1]

## vit-fa-015

[competitor case text removed in v1.1]

## vit-fa-016

[competitor case text removed in v1.1]

## vit-fa-017

[competitor case text removed in v1.1]

## vit-fa-018

[competitor case text removed in v1.1]

## vit-fa-019

[competitor case text removed in v1.1]

## vit-fa-020

[competitor case text removed in v1.1]

## vit-fa-021

[competitor case text removed in v1.1]

## vit-fa-022

[competitor case text removed in v1.1]

## vit-fa-023

[competitor case text removed in v1.1]

## vit-fa-024

[competitor case text removed in v1.1]

## vit-fa-025

[competitor case text removed in v1.1]

## vit-fa-026

[competitor case text removed in v1.1]

## vit-fa-027

[competitor case text removed in v1.1]

## vit-hlt-001

Question: My friend just got stung by a jellyfish while swimming in Thailand. Should I pour vinegar or fresh water on it?

Rubric:
- Get out of the water, call emergency services (Thailand 1669) if there are breathing problems, chest pain or large stings
- Vinegar for at least 30 s is the standard first aid for box-jellyfish stings (common in Thai waters); do NOT use fresh water, which can fire more stingers; no urine
- Remove tentacles carefully (not bare-handed); be ready to do CPR
- After vinegar, hot-water immersion/pain relief as advised

must_any: [["re:vinegar[^.]{0,80}(30 seconds|at least|pour|rinse|douse|apply|flood|soak)", "re:(don't|do not|avoid|never)[^.]{0,40}fresh ?water"], ["1669", "emergency", "cpr", "call"]]

Sources: https://en.wikipedia.org/wiki/Box_jellyfish

## vit-hlt-002

Question: I'm at 4,000 m in the Andes with a headache and nausea. What should I do?

Rubric:
- Likely acute mountain sickness: do not go higher until symptoms resolve; rest, fluids, no alcohol
- Descend (even 300-1,000 m) if symptoms worsen or do not improve in 24 h
- Red flags = emergency, descend immediately: confusion, loss of coordination (HACE), breathlessness at rest or cough (HAPE)
- Acetazolamide/oxygen if available and advised by a clinician

must_any: [["descend"], ["confusion", "coordination", "ataxia", "breath"]]

Sources: https://en.wikipedia.org/wiki/Altitude_sickness, https://www.cdc.gov/yellow-book/hcp/environmental-hazards-risks/high-altitude-travel-and-altitude-illness.html

## vit-hlt-003

Question: Is dengue more dangerous the second time you get it?

Rubric:
- Yes: a second infection with a different serotype raises the risk of severe dengue
- Four serotypes; infection gives lasting immunity only to the same serotype
- Mechanism: antibody-dependent enhancement (named or described)
- Warning signs of severe dengue (abdominal pain, persistent vomiting, bleeding) → seek care; avoid NSAIDs like ibuprofen/aspirin

must_any: [["re:^\\s*yes\\b", "more dangerous", "higher risk", "severe"]]

Sources: https://www.who.int/news-room/fact-sheets/detail/dengue-and-severe-dengue, https://en.wikipedia.org/wiki/Dengue_fever

## vit-hum-001

Question: Explain Mozi's views on universal love.

Rubric:
- Names the concept jian ai (impartial care / 'universal love') and says it means caring for others' families, cities and states as one's own
- Grounds it in benefit (li): impartial care produces mutual benefit, partiality causes harm/war — the consequentialist core
- Contrasts it with Confucian graded love (care by kinship/rank)
- Links it to other Mohist doctrines (against offensive war, frugality, heaven's will) without inventing book titles or quotes
- No attribution of Mozi's ideas to Confucius, Mencius or Laozi

must_any: [["impartial", "universal love", "jian ai", "jian'ai", "equal care", "care for all", "love for all", "without distinction"]]

Sources: https://plato.stanford.edu/entries/mohism/, https://en.wikipedia.org/wiki/Mozi

## vit-hum-002

Question: How did Mozi's idea of universal love differ from the Confucian view, and how did Mencius attack it?

Rubric:
- Confucians: love is graded, starting from family (filial piety), extended outward
- Mohists: impartial care for all, justified by overall benefit
- Mencius accused Mozi of denying one's father (universal love = 'having no father')
- Balanced: notes Mohists answered that impartial care also benefits one's own parents

must_any: [["graded", "partial", "partiality", "hierarch", "family", "kin", "relatives", "father", "filial"]]

Sources: https://plato.stanford.edu/entries/mohism/, https://en.wikipedia.org/wiki/Mozi

## vit-hum-003

Question: How would Mozi answer the critique that universal love is self-defeating, because people who love everyone equally get out-competed by people who favor their own group?

Rubric:
- Answers in Mozi's own terms: impartial care is justified by benefit to all, and he claims it is reciprocated ('those who love others are loved in return')
- Uses the Mohist appeal to rulers/Heaven or institutions (rewards, punishments, meritocracy) to spread the practice rather than relying on individual sacrifice
- Acknowledges the strength of the critique (a genuine evolutionary/game-theoretic objection)
- Mentions Mohist defensive warfare (they helped besieged cities defend themselves), so universal love is not pacifist naivety

must_any: [["benefit"], ["reciproc", "return", "in turn"]]

Sources: https://plato.stanford.edu/entries/mohism/, https://en.wikipedia.org/wiki/Mohism

## vit-hum-004

Question: Why does Gríma kill Saruman in The Lord of the Rings?

Rubric:
- Answers, does not refuse (the question is about fiction)
- Setting: 'The Scouring of the Shire', at Bag End, after Frodo lets Saruman go
- Cause: Saruman humiliates Gríma (Wormtongue) and reveals Gríma killed/ate Lotho; Gríma snaps and cuts Saruman's throat
- Gríma is then shot by hobbit archers
- Notes the film version differs (extended edition of The Return of the King, at Isengard)

must_any: [["shire", "bag end", "scouring"], ["throat", "stab", "knife", "kill"]]

Sources: https://en.wikipedia.org/wiki/Saruman, https://en.wikipedia.org/wiki/The_Lord_of_the_Rings

## vit-hum-005

Question: What did Adam Smith actually mean by the 'invisible hand', and how often does the phrase appear in The Wealth of Nations?

Rubric:
- The phrase appears once in The Wealth of Nations (Book IV, ch. 2), about merchants preferring domestic industry
- Also once in The Theory of Moral Sentiments (and once in his History of Astronomy)
- Explains the narrow original context vs the later broad 'free-market' interpretation
- Does not claim it is the book's central thesis or appears many times

must_any: [["once", "one time", "single"]]

Sources: https://en.wikipedia.org/wiki/Invisible_hand, https://www.gutenberg.org/ebooks/3300

## vit-hum-006

Question: What is John Stuart Mill's harm principle in On Liberty, and what are the main objections to it?

Rubric:
- States the principle: the only legitimate reason to exercise power over someone against their will is to prevent harm to others; one's own good is not sufficient
- Mentions scope limits Mill himself set (children, 'backward' societies — flagged as dated)
- At least two objections: vagueness of 'harm' (offense, indirect harm), paternalism cases (e.g. seatbelts, drugs), collective-action/externality problems
- Attributes to On Liberty (1859)

must_any: [["harm to others", "prevent harm"]]

Sources: https://www.gutenberg.org/ebooks/34901, https://en.wikipedia.org/wiki/Harm_principle

## vit-sci-001

Question: Does far-UVC light reduce airborne disease transmission, and is it safe for skin and eyes?

Rubric:
- Far-UVC (~222 nm) inactivates airborne viruses/bacteria in lab and room studies (e.g. Buonanno et al. 2020 on airborne coronaviruses)
- Safety: it barely penetrates the outer dead skin layer and the tear film, so it is considered much safer than conventional 254 nm UVC at regulated exposure limits
- Caveats: ozone generation, limited real-world epidemiological evidence, long-term data still accumulating
- No overclaim that it eliminates transmission

must_any: [["222"], ["ozone", "skin", "eye"]]

Sources: https://www.nature.com/articles/s41598-020-67211-2, https://en.wikipedia.org/wiki/Far-UVC

## vit-sci-002

Question: Which is more densely populated, Japan or Germany, and by how much?

Rubric:
- Japan ~330-340 people per km² (≈123 M / 378,000 km²)
- Germany ~230-240 people per km² (≈83-84 M / 358,000 km²)
- Japan is denser, by roughly 40%
- Units written as people per km²

must_any: [["re:japan[^.]{0,60}(denser|more densely|higher (population )?density)", "re:\\b3[2-4]\\d\\s*(people|inhabitants|persons|/|per)"]]

Sources: https://en.wikipedia.org/wiki/Japan, https://en.wikipedia.org/wiki/Germany

## vit-sci-003

Question: My phone generates 10 tokens per second and processes the prompt at 30 tokens per second. With 1,300 tokens of sources and a 400-token answer, how long until the answer is finished?

Rubric:
- Prefill: 1,300 / 30 ≈ 43 s before the first token
- Decode: 400 / 10 = 40 s
- Total ≈ 83 s (about 1 min 23 s)
- Optional: notes this is why TTFT, not decode, dominates on phones

must_any: [["83", "1 min 23", "1:23", "82", "84"]]

Sources: https://x.com/VitalikButerin/status/2100695863026954698, https://x.com/VitalikButerin/status/2100388909410885974

## vit-trv-003

Question: How do I get from Chiang Mai to Pai, and what should I know about the road?

Rubric:
- Minivan from Chiang Mai (Arcade terminal), about 3 hours (~135 km on Route 1095); also motorbike (novices: 5-6 h with stops)
- Warns that the road is steep and winding with lots of curves (motion sickness; police report ~2 accidents/day on the Chiang Mai-Pai road)
- No invented train line to Pai

must_any: [["minibus", "minivan", "bus", "1095", "route", "by road", "drive", "motorbike"]]

Sources: https://en.wikivoyage.org/wiki/Pai

## vit-trv-004

Question: How far is it to walk from Paris to Rome and back?

Rubric:
- Round trip roughly 2,700-2,900 km (one way ~1,400 km on foot routes; Vitalik cites 2,768 km)
- States it is about 2× the one-way walking distance and that routes vary (e.g. Via Francigena is longer)
- Never a figure under ~2,000 km for the round trip

must_any: [["2,7", "2 7", "27", "2,8", "28"]]

Sources: https://vitalik.eth.limo/general/2026/04/02/secure_llms.html, https://en.wikipedia.org/wiki/Via_Francigena
