#!/usr/bin/env python3
"""K1-COVERAGE: writes k1-coverage.jsonl from /tmp/k1-coverage-dossier.json (traces + judgments, tools/dossier.py) and the manual pack-presence
classification below (pack chunks read with tools/packq.py, read-only). 0 LLM. Usage: python3 -I dossier.py > /dev/null; python3 -I build.py"""
import json, os
D = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
DOS = {e["id"]: e for e in json.load(open("/tmp/k1-coverage-dossier.json"))}
# class: absent_from_both | present_simplewiki_not_retrieved | present_top100k_not_retrieved | retrieved_but_wrong | fixed_in_K1_or_K4 | unclear
#        + blocked_before_retrieval (the engine answered with a places/health refusal before any pack chunk reached the prompt; fact presence kept in `presence_class`)
# ret: did the arm's kept context contain the fact (article-level; kept chunk text is not logged, see report caveat): yes / partial / no / none (nothing retrieved)
M = {
 "lan-cmp-005": dict(fact="Saltwater crocodile is the largest living reptile; bigger than the Nile crocodile", k1="partial", k4="yes",
   sw="Present-day crocodiles range in size from African dwarf crocodiles ... to saltwater crocodiles which can approach 23 feet (7 m).",
   top="The saltwater crocodile is the largest living reptile.",
   k0="The saltwater crocodile is the largest of all living crocodilians (Wikivoyage: Nusa Tenggara)",
   cls="fixed_in_K1_or_K4", fix="grounded", note="K1 3.0 (kept Nile crocodile, Crocodile family chunks), K4 3.5 (kept Saltwater crocodile). The fact was already in K0's Wikivoyage pack but not retrieved."),
 "lan-rsn-001": dict(fact="~21,196 km (all sections); not visible from the Moon with the naked eye", k1="yes", k4="yes",
   sw="Neil Armstrong, said that on the Moon, it was very clear that the wall was not visible.",
   top="The Great Wall of China cannot be seen by the naked human eye from the Moon.",
   cls="fixed_in_K1_or_K4", fix="grounded", note="K1 2.5 (kept Great Wall of China + List of common misconceptions). K4 kept the same fact and answered 'cannot be seen from the Moon' but mislabelled 21,196 km as miles (1.5, still CE)."),
 "st-qa-cooking-se-002": dict(fact="Botulism; low oxygen under oil lets it grow; toxin is tasteless", k1="none", k4="none",
   sw="The most potent neurotoxin known is produced when the bacteria is exposed to low oxygen and body temperature.",
   top="garlic or herbs stored covered in oil without acidification", cls="blocked_before_retrieval", pcls="present_top100k_not_retrieved",
   note="All arms answer 'The offline places pack is not installed...' (places route, retrieval never runs). Packs give botulism + oil (top100k) and low oxygen (simplewiki); neither states 'tasteless' (top100k: some types 'can go undetected because there is no strong odor')."),
 "st-qa-cooking-se-003": dict(fact="Parchment 'cartouche' controls evaporation; lid drips unevenly", k1="no", k4="no", sw=None, top=None,
   cls="absent_from_both", note="'cartouche' exists only as the Egyptian hieroglyph (simplewiki) and map/Baroque ornament (top100k). K1 kept Cabbage roll/Simmering, K4 kept Passover."),
 "st-qa-cooking-se-008": dict(fact="Pineapple is non-climacteric: it softens but does not get sweeter after picking", k1="no", k4="no",
   sw=None, top="A pineapple never becomes any riper than it was when harvested since it is a non-climacteric fruit.",
   cls="present_top100k_not_retrieved", note="K1 kept simplewiki Pineapple + Ripening (neither says pineapple stops ripening; Ripening lists tomato/mango vs cherry/fig). K4 kept Biryani; the top100k Pineapple chunk was never retrieved."),
 "st-qa-cooking-se-012": dict(fact="French oven = enamelled Dutch oven; the name is marketing", k1="no", k4="yes",
   sw=None, top="Some metal varieties are enameled rather than being seasoned, and these are sometimes called French ovens.",
   cls="retrieved_but_wrong", note="K4 kept 'Dutch oven' (first title; the fact is in its lead chunk) and still invented a roasting-vs-baking difference. simplewiki has no Dutch/French oven article. Chunk-level identity not logged (article kept)."),
 "st-qa-cooking-se-013": dict(fact="Kosher salt scrub; burn off; lye last resort; re-season", k1="none", k4="none", sw=None, top=None,
   cls="blocked_before_retrieval", pcls="absent_from_both", note="All arms return the health decline ('I won't give health advice from memory...'). No cast-iron seasoning/cleaning content in either pack."),
 "st-qa-cooking-se-015": dict(fact="Breast overcooked; ~10 F carryover; brine; shield the breast", k1="none", k4="none",
   sw="Breast: These are white meat and are relatively dry. (Chicken as food; no cause or fix)", top=None,
   cls="blocked_before_retrieval", pcls="absent_from_both", note="All arms return the health decline. No carryover/brining content in either pack."),
 "st-qa-cooking-se-020": dict(fact="Warm dairy dissolves sugar; tempering keeps yolks from scrambling; cook to ~155-160 F", k1="no", k4="partial",
   sw=None, top="it begins setting at 70 °C (158 °F). (Custard; tempering/sugar not stated)",
   cls="fixed_in_K1_or_K4", fix="weak", note="K4 2.0 (kept Custard) with a generic memory answer under the warning line; borderline fix (CE threshold 1.5, judge noise ~5 % per CE item)."),
 "st-qa-money-se-004": dict(fact="It's a scam (money flipping); money may be stolen; don't share details", k1="none", k4="none",
   sw="money flipping, whereby the mark is promised a large amount of money in exchange for sending a small amount of money.", top=None,
   cls="blocked_before_retrieval", pcls="present_simplewiki_not_retrieved", note="All arms return the health decline. simplewiki 'Advance-fee scam' names the pattern; top100k has no money-flipping/overpayment text found."),
 "st-qa-money-se-007": dict(fact="12 USC 1759(b) common-bond / geographic field of membership", k1="partial", k4="no",
   sw="A credit union is a cooperative financial institution that is owned and controlled by its members. (no common bond)", top=None,
   cls="fixed_in_K1_or_K4", fix="partial", note="K1 2.5 (kept Credit union: member-owned, cited [4]); the legal common-bond rule is in neither pack. K4 kept American Express/Credit card (1.5)."),
 "st-qa-money-se-009": dict(fact="Taxable account is taxed twice; deferral ~ Roth; employer match", k1="no", k4="partial",
   sw=None, top="Periodic employee contributions come directly out of their paychecks, and may be matched by the employer.",
   cls="fixed_in_K1_or_K4", fix="partial", note="K4 2.5 (kept 401(k), Roth IRA, Capital gains tax): corrects the premise but no worked comparison; the 'apples to apples' argument is in neither pack."),
 "st-qa-money-se-010": dict(fact="Prior-year HSA contribution requires HDHP eligibility in that year (limit 0 here)", k1="no", k4="none",
   sw=None, top=None, cls="absent_from_both", note="No HSA article in either pack; top100k mentions HSAs only in passing (Debit card, Healthcare in the US). K1 kept Social Security / Form W-9."),
 "st-qa-money-se-011": dict(fact="RSUs taxed as income at vest; vest value = basis; holding period from vest", k1="no", k4="no",
   sw=None, top=None, cls="fixed_in_K1_or_K4", fix="ungrounded", note="K1 2.5 / K4 3.0 from memory under the warning line (kept Joint-stock company/Stock, Stock/Capital gains tax); no RSU text in either pack. Decoding variance, not pack content."),
 "st-qa-money-se-020": dict(fact="I bond composite rate tracks CPI-U inflation, not the Fed rate", k1="no", k4="no", sw=None, top=None,
   cls="absent_from_both", note="No Series I / savings-bond article; top100k 'Bond (finance)' only says inflation-indexed bonds are indexed to consumer prices (generic)."),
 "vit-cry-005": dict(fact="Privacy Pools: ZK withdrawal proof of membership in an association set excluding illicit deposits", k1="no", k4="no",
   sw=None, top=None, k0="Users prove their withdrawal originates from a \"clean\" deposit set using ZK proofs, with Association Set Providers (ERC-8262, crypto pack)",
   cls="absent_from_both", note="Absent from simplewiki and top100k, but present in K0's crypto pack (ERC-8262, EIP-7503) and never retrieved: all arms keep 4 Tornado Cash chunks."),
 "vit-cry-007": dict(fact="d/acc = defensive/decentralized accelerationism (Buterin, Nov 2023)", k1="no", k4="no", sw=None, top=None,
   cls="absent_from_both", note="No d/acc text in simplewiki, top100k or the crypto pack. K1 retrieval matched 'DAC' (Digital-to-analog converter) and the 1.7B answered from it."),
 "vit-hum-004": dict(fact="Book: at Bag End after the Scouring, Saruman taunts Gríma (reveals Lotho's murder); Gríma kills him, is shot by hobbits", k1="yes", k4="yes",
   sw="After the hobbit uprising, Gríma kills Saruman; Gríma is killed by hobbit archers.",
   top="Wormtongue, whom Saruman continues to taunt and physically abuse, finally snaps and murders him.",
   cls="retrieved_but_wrong", note="K1 kept Middle-earth characters (the answer reuses 'hobbit archers' from that chunk, so it was in the prompt) but placed the killing 'in Isegard' from the film sentence of the same chunk. K4 kept Saruman and gave the film setting."),
 "vit-sci-002": dict(fact="Japan ~330/km2 vs Germany ~236/km2: Japan ~40 % denser", k1="partial", k4="no",
   sw="The total area of Germany is 357,022 square kilometers ... Germany had a population of over 83 million (no Japan figures)",
   top="Density: 330/km2 (Japan infobox); Its population density stands at 236 inhabitants per square kilometre (Germany)",
   cls="present_top100k_not_retrieved", note="K4 kept only the generic 'Population density' article. K1 kept simplewiki Germany (area + population only) and reversed the verdict. simplewiki Japan has no population/density."),
 "vit-trv-003": dict(fact="Minivan from Arcade terminal, ~3 h, 135 km on Rte 1095; steep winding road, ~2 accidents/day", k1="no", k4="no",
   sw=None, top=None, k0="Rte 1095 which connects Pai with ... Chiang Mai (135 km) ... steep and winding drive, with lots of curves (Wikivoyage: Pai)",
   cls="absent_from_both", note="No Pai article in simplewiki or top100k. The full answer is in K0's Wikivoyage 'Pai' article, never retrieved (all arms keep 3 Chiang Mai chunks)."),
 # reading failures (CE taxonomy had_relevant_source = yes)
 "lan-cmp-004": dict(fact="Bison bulls (~460-990 kg) outweigh moose bulls (~380-700 kg)", k1="partial", k4="partial", sw=None, top=None,
   cls="fixed_in_K1_or_K4", fix="weak", note="K1 2.0 (kept Siberian tiger, Moose; answered from memory with the right verdict but inflated bison weights). K4 kept Bison/European bison and reversed the verdict (1.0)."),
 "lan-exp-007": dict(fact="Autonomous territory of Denmark; Nuuk; ~56,000 people; ~80 % ice", k1="partial", k4="partial",
   sw="Greenland is a self-governing territory of the kingdom of Denmark.", top=None,
   cls="fixed_in_K1_or_K4", fix="weak", note="K1 2.0 (kept simplewiki Greenland; population '50,000', still off). K4 kept Greenland and wrote 560,000 (1.5, CE): the 10x population error repeats."),
 "lan-rsn-003": dict(fact="Cheetah; top speed only for short sprints (20-30 s)", k1="yes", k4="yes",
   sw=None, top="The fastest land animal is the cheetah.", cls="fixed_in_K1_or_K4", fix="weak",
   note="K4 2.0 (kept Fastest animals; cheetah right, duration vague). K1 kept simplewiki Cheetah + Pronghorn and still named the pronghorn (1.5, CE)."),
 "vit-cry-002": dict(fact="FOCIL: validator committee inclusion lists enforced by fork choice, for censorship resistance", k1="yes", k4="yes", sw=None, top=None,
   k0="Allow a committee of validators to force-include a set of transactions in every block (EIP-7805, crypto pack)",
   cls="retrieved_but_wrong", note="EIP-7805 kept in K0/K1/K4; the 1.7B describes 'consistency of fork choices' in all three. K4 answer byte-identical to K0."),
 "vit-cry-003": dict(fact="Partial (pre-Merge) history expiry since July 2025 saves ~300-500 GB", k1="yes", k4="yes", sw=None, top=None,
   k0="Historical blocks and receipts currently occupy more than 400GB of disk space (EIP-4444 2021 draft, crypto pack)",
   cls="retrieved_but_wrong", note="Same EIP-4444 chunks kept in every arm; the source is the stale 2021 draft (CE taxonomy: outdated) and the answer drops the >400GB figure. K4 identical to K0."),
 "vit-cry-006": dict(fact="QF: (sum of sqrt contributions)^2 matching; main weakness collusion/Sybil", k1="yes", k4="no", sw=None, top=None,
   k0="Using onchain voting makes quadratic funding susceptible to collusion (ethereum.org ZK page, crypto pack)",
   cls="retrieved_but_wrong", note="K1 kept the same crypto chunks as K0 and still called QF a DeFi vote (1.0). K4 kept Referendum/Quadratic equation instead: top100k crowded the crypto chunks out and the answer confused QF with quadratic voting."),
 "vit-hum-005": dict(fact="'Invisible hand' appears once in The Wealth of Nations (Book IV ch. 2)", k1="no", k4="yes",
   sw=None, top="Smith used the term \"the invisible hand\" in \"History of Astronomy\" ... and once in each of his The Theory of Moral Sentiments",
   cls="retrieved_but_wrong", note="CE taxonomy label 'unclear'. K4 kept Adam Smith; the answer cites 'Book IV, Chapter II' (same chunk as the 'once' sentence) yet says the phrase 'appears frequently'. K1 kept Adam Smith/Wealth of Nations (simplewiki, no count) and said '~15 times'."),
}
rows = []
for i, e in DOS.items():
    m = M[i]; lab = e["ce_label"]["had_relevant_source"]
    grp = "no_source" if lab == "no" else ("reading_failure" if lab == "yes" else "unclear_label")
    arm = lambda a, r: dict(kept_titles=sorted({t for t, _ in e["arms"][a]["kept"]}), fact_in_kept=r, correctness=e["arms"][a]["corr"],
                            ce=e["arms"][a]["ce"], answer_same_as_K0=e["arms"][a]["same_as_K0"], answer_head=e["arms"][a]["answer"][:160])
    rows.append(dict(id=i, question=e["question"], group=grp, ce_taxonomy=dict(had_relevant_source=lab, error_kind=e["ce_label"]["error_kind"]),
                     key_fact=m["fact"], K0=dict(correctness=e["arms"]["K0"]["corr"], kept_titles=sorted({t for t, _ in e["arms"]["K0"]["kept"]})),
                     K1=arm("K1", m["k1"]), K4=arm("K4", m["k4"]),
                     presence=dict(simplewiki=m.get("sw"), top100k=m.get("top"), k0_packs=m.get("k0")),
                     cls=m["cls"], presence_class=m.get("pcls"), fix_grounding=m.get("fix"), note=m["note"]))
with open(D + "/k1-coverage.jsonl", "w") as f:
    for r in rows: f.write(json.dumps(r, ensure_ascii=False) + "\n")
from collections import Counter
for g in ["no_source", "reading_failure", "unclear_label"]:
    print(g, dict(Counter(r["cls"] for r in rows if r["group"] == g)))
