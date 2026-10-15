"""LONGSESSION slice builder (0 LLM calls). Writes boar-eval/bench/slices/longsession-v1/{questions.jsonl,sessions.jsonl,SHA256SUMS}.
Items are agent-written (Claude Opus 5.5, coordinator subagent, 2026-10-14) = DEV data, fresh (not copied from any bench item; the private held-out dir never read).
Fields: id, session, turn, shape (coref|switch|deepen), followup (needs the previous turns to be understood), referent (strings; the follow-up
answer 'names the referent' if any is a case-insensitive substring), category, lang, question, rubric (list; the first entry gives the judge the
conversation context for follow-ups).
Usage: python3 -I build_slice.py <slice dir>"""
import json, sys, os, hashlib
S = [
 ("ls01", "coref", "travel", [
  ("What are the main sights to see in Lisbon?", None, None,
   ["Names several of: Belem Tower, Jeronimos Monastery, Alfama district, Sao Jorge Castle, tram 28, Baixa/Chiado, Commerce Square."]),
  ("How do I get there from Porto by train?", ["Lisbon", "Lisboa"], "Earlier turn asked about the sights of Lisbon; 'there' = Lisbon.",
   ["Direct trains (Alfa Pendular / Intercidades) run from Porto Campanha to Lisbon (Santa Apolonia / Oriente) in about 3 hours."]),
  ("Is the second city you mentioned good for a day trip to the Douro Valley?", ["Porto", "Oporto"], "The conversation mentioned Lisbon and then Porto; the second city = Porto.",
   ["Yes: the Douro Valley is a common day trip from Porto, by the Douro railway line (to Regua/Pinhao, about 2-2.5 h), by car, boat cruise or organised tour."]),
  ("What food should I try there?", ["Porto", "Oporto", "Douro"], "'There' = Porto / the Douro region from the previous turns.",
   ["Mentions Porto specialities such as francesinha, port wine (and Douro wines), tripas a moda do Porto, bacalhau dishes."]),
  ("And how many euros is 150 US dollars, roughly, if one dollar is 0.92 euros?", None, "Self-contained arithmetic inside a Portugal trip conversation.",
   ["150 x 0.92 = 138 euros."]),
 ]),
 ("ls02", "coref", "crypto", [
  ("What is the difference between Bitcoin and Ethereum?", None, None,
   ["Bitcoin: digital money / store of value, capped 21 million supply, proof of work.", "Ethereum: programmable platform for smart contracts and apps, native coin ether, proof of stake since the Merge (September 2022)."]),
  ("How does the second one reach consensus today?", ["Ethereum", "ETH", "ether"], "The previous turn compared Bitcoin and Ethereum; the second one = Ethereum.",
   ["Proof of stake since the Merge (September 2022): validators stake ETH, propose and attest to blocks; misbehaviour is slashed."]),
  ("How much do I need to run a validator for it?", ["Ethereum", "ETH", "ether"], "'It' = Ethereum.",
   ["32 ETH for a solo validator (plus hardware and an execution + consensus client); smaller amounts possible via staking pools or liquid staking."]),
  ("What happens if my validator goes offline?", ["Ethereum", "ETH", "ether"], "Context: running an Ethereum validator.",
   ["Small inactivity penalties roughly equal to the rewards it would have earned; it is NOT slashed for being offline; slashing is for double signing / conflicting votes; larger inactivity leak only if the chain stops finalising."]),
  ("And what about the first coin: can I stake it too?", ["Bitcoin", "BTC"], "The first coin of the conversation = Bitcoin.",
   ["Bitcoin uses proof of work, so there is no native staking; security comes from mining. Third-party schemes or lending exist but are not native staking."]),
 ]),
 ("ls03", "coref", "health", [
  ("How should I treat a bee sting?", None, None,
   ["Remove the stinger quickly (scrape or pull), wash the area, cold compress, pain relief / antihistamine if needed; watch for signs of a severe allergic reaction and call emergency services if they appear."]),
  ("Is that different for a small child?", ["sting", "bee"], "'That' = treating a bee sting.",
   ["Same first-aid steps; child-appropriate doses of pain relief / antihistamine (by label or weight); watch closely for allergic signs; get medical help for many stings or stings in the mouth or throat."]),
  ("What are the warning signs that it's an allergic reaction?", ["sting", "bee"], "Context: a child stung by a bee.",
   ["Hives spreading beyond the sting, swelling of face / lips / tongue / throat, trouble breathing or wheezing, dizziness or fainting, fast pulse, nausea or vomiting; call emergency services and use an epinephrine auto-injector if available."]),
  ("If they have an epinephrine pen, where do I inject it?", ["anaphyla", "allergic", "sting"], "Context: suspected severe allergic reaction to a bee sting.",
   ["Outer middle of the thigh, can go through clothing; hold in place a few seconds per device instructions; call emergency services; a second dose may be given after 5-15 minutes if no improvement."]),
  ("How long should we wait at the hospital after using it?", ["epinephrine", "adrenaline", "auto-injector", "EpiPen", "epi pen"], "'It' = the epinephrine auto-injector.",
   ["Always go to the emergency department even if symptoms improve; observation is usually at least 4-6 hours (longer if severe) because of the risk of a second (biphasic) reaction."]),
 ]),
 ("ls04", "coref", "geography", [
  ("Which are the three largest countries in South America by area?", None, None,
   ["Brazil, Argentina, Peru (in that order)."]),
  ("What is the capital of the second one?", ["Argentina"], "The second largest = Argentina.",
   ["Buenos Aires."]),
  ("How far is it from there to Santiago de Chile?", ["Buenos Aires"], "'There' = Buenos Aires.",
   ["About 1,100-1,150 km in a straight line; about a 2-hour flight; roughly 1,400 km by road across the Andes."]),
  ("Do I need a visa to go there as a US citizen?", ["Chile", "Santiago"], "'There' = Chile (Santiago).",
   ["No visa needed for US citizens for tourist stays up to 90 days; a valid passport is required."]),
  ("What's the best time of year to visit for skiing?", ["Chile", "Santiago", "Andes"], "Context: a trip to Chile / Santiago.",
   ["Southern-hemisphere winter, roughly June to September (peak July-August); resorts near Santiago such as Valle Nevado, La Parva, El Colorado, Portillo."]),
 ]),
 ("ls05", "switch", "crypto", [
  ("What is a seed phrase in a crypto wallet?", None, None,
   ["A list of 12 or 24 words (BIP-39) that encodes the wallet's master private key; it restores the wallet; anyone who has it controls the funds."]),
  ("What is the safest way to store it?", ["seed", "recovery phrase", "mnemonic"], "'It' = the wallet seed phrase.",
   ["Offline: written on paper or stamped in metal, kept in one or more secure places; never as a photo, in cloud storage, email or a password-less file; never share it or type it into websites."]),
  ("How do I treat a minor kitchen burn?", None, "Abrupt topic switch (from crypto to first aid).",
   ["Cool under cool running water for about 20 minutes, remove rings / tight items, cover loosely with cling film or a clean non-fluffy dressing, pain relief; no ice, butter or creams on the fresh burn; do not pop blisters."]),
  ("When should a burn be seen by a doctor?", None, None,
   ["Larger than the person's palm, deep (white, leathery, charred) or painless, on face / hands / feet / genitals / joints, chemical or electrical burns, infants or older people, signs of infection."]),
  ("Going back to the wallet: what is the difference between a hot and a cold wallet?", None, "Returns to the crypto topic of turns 1-2.",
   ["Hot wallet: keys on an internet-connected device or app, convenient but more exposed to hacks; cold wallet: keys kept offline (hardware or paper), safer for long-term storage."]),
 ]),
 ("ls06", "switch", "travel", [
  ("What can I see in Kyoto in two days?", None, None,
   ["Names several of: Fushimi Inari shrine, Kinkaku-ji, Kiyomizu-dera, Arashiyama bamboo grove, Gion, Nijo Castle, Ginkaku-ji / Philosopher's Path."]),
  ("How do I get there from Tokyo?", ["Kyoto"], "'There' = Kyoto.",
   ["Tokaido Shinkansen from Tokyo / Shinagawa to Kyoto, about 2 h 15 min on a Nozomi (longer on Hikari / Kodama); alternatives: overnight bus or a flight to Osaka."]),
  ("What is 18% of 2,450?", None, "Abrupt topic switch to arithmetic.",
   ["441."]),
  ("Convert 25 degrees Celsius to Fahrenheit.", None, None,
   ["77 degrees Fahrenheit (25 x 9/5 + 32)."]),
  ("Back to the trip: what is a good day trip from the city I asked about first?", ["Kyoto"], "The city asked about first = Kyoto.",
   ["Day trips from Kyoto such as Nara (deer park, Todai-ji), Osaka, Uji, Himeji Castle, Lake Biwa; with rough travel times."]),
 ]),
 ("ls07", "switch", "crypto", [
  ("What is a smart contract?", None, None,
   ["A program stored on a blockchain (e.g. Ethereum) that runs automatically when its conditions are met; code is public and hard to change once deployed; written e.g. in Solidity."]),
  ("What is gas on Ethereum?", None, None,
   ["A unit measuring the computation a transaction uses; fee = gas used x (base fee + priority tip), priced in gwei; the base fee is burned (EIP-1559)."]),
  ("When did the Berlin Wall fall?", None, "Abrupt topic switch to history.",
   ["9 November 1989 (German reunification followed on 3 October 1990)."]),
  ("Why was it built in the first place?", ["Berlin Wall", "the Wall", "wall"], "'It' = the Berlin Wall.",
   ["Built by East Germany (GDR) from 13 August 1961 to stop East Germans fleeing to West Berlin (mass emigration / brain drain); officially called an 'anti-fascist protection rampart'."]),
  ("How long did it stand?", ["Berlin Wall", "the Wall", "wall"], "'It' = the Berlin Wall.",
   ["About 28 years: from August 1961 to November 1989."]),
 ]),
 ("ls08", "deepen", "travel", [
  ("What is the Ring Road in Iceland?", None, None,
   ["Route 1, a road of about 1,320 km that loops around the whole island, linking most inhabited areas."]),
  ("How many days do I need to drive the Ring Road comfortably?", None, None,
   ["About 7-10 days for a comfortable trip with stops (possible in 5-6 but rushed); more in winter."]),
  ("What are the must-see stops on the south coast part of the Ring Road?", None, None,
   ["Several of: Seljalandsfoss, Skogafoss, Reynisfjara black sand beach, Vik, Dyrholaey, Skaftafell, Jokulsarlon glacier lagoon / Diamond Beach."]),
  ("Is it safe to drive the Ring Road in winter?", None, None,
   ["Possible but demanding: ice, snow, strong winds, short daylight, closures; use a 4x4 with winter tyres, check road.is and vedur.is (weather) daily, drive slowly, have flexible plans."]),
  ("What should I pack for a winter trip to Iceland?", None, None,
   ["Layers: thermal base layer, warm mid layer, waterproof and windproof shell; insulated waterproof boots (ice cleats), hat, gloves, scarf; swimsuit for hot springs; headlamp."]),
 ]),
 ("ls09", "deepen", "crypto", [
  ("What is a layer 2 on Ethereum?", None, None,
   ["A system that executes transactions off the main chain and posts data and/or proofs back to Ethereum (L1), inheriting its security, giving cheaper and faster transactions (rollups)."]),
  ("What is the difference between optimistic rollups and zk-rollups?", None, None,
   ["Optimistic: assume batches valid, fraud proofs during a challenge window (about 7 days for withdrawals); zk-rollups: validity (zero-knowledge) proofs verified on L1, faster finality, more complex proving."]),
  ("Why do withdrawals from optimistic rollups take about a week?", None, None,
   ["Because of the challenge period: anyone can submit a fraud proof against a batch during about 7 days before it is final on L1; third-party bridges offer fast exits for a fee."]),
  ("What did EIP-4844 change for rollups?", None, None,
   ["Proto-danksharding (Dencun upgrade, March 2024) added blob transactions: cheap temporary data space (pruned after about 18 days) for rollup data, cutting L2 fees sharply."]),
  ("Name three widely used rollups and say which type each one is.", None, None,
   ["Three correct pairs among: Arbitrum One (optimistic), OP Mainnet / Optimism (optimistic), Base (optimistic), zkSync Era (zk), Starknet (zk), Scroll (zk), Linea (zk), Polygon zkEVM (zk)."]),
 ]),
 ("ls10", "deepen", "health", [
  ("What are the signs of dehydration in adults?", None, None,
   ["Thirst, dark yellow urine, urinating less, dry mouth / lips, tiredness, dizziness, headache; severe: confusion, fast heartbeat, fainting -> medical help."]),
  ("How do I make an oral rehydration solution at home?", None, None,
   ["WHO-style recipe: 1 litre of clean water + 6 level teaspoons of sugar + half a level teaspoon of salt, stirred until dissolved; sip often; commercial ORS sachets preferred if available."]),
  ("What is the difference between heat exhaustion and heat stroke?", None, None,
   ["Heat exhaustion: heavy sweating, cool clammy skin, weakness, nausea, headache, normal or mildly raised temperature, improves with rest / cooling / fluids. Heat stroke: body temperature above about 40 C (104 F), confusion or loss of consciousness, hot skin (sweating may stop): a medical emergency."]),
  ("What should I do while waiting for an ambulance for someone with heat stroke?", None, None,
   ["Move to shade / cool place, remove excess clothing, cool rapidly (cold-water immersion if possible, or soak with water and fan, ice packs to neck, armpits, groin), no drinks if confused or unconscious, recovery position if unconscious, monitor breathing."]),
  ("How much water should I drink per hour when hiking in hot weather?", None, None,
   ["Roughly 0.5-1 litre per hour depending on heat and effort; drink regularly before thirst; do not exceed about 1-1.5 litres per hour (risk of low sodium); add electrolytes / salty snacks on long hikes."]),
 ]),
]

# Addendum 1 (2026-10-14): 3 sessions extended to 15 turns (ls02 coref, ls06 switch, ls08 deepen); appended after the original 50 (unchanged).
EXT = {
 "ls02": [
  ("Who created it?", ["Bitcoin", "Satoshi"], "The previous turn was about Bitcoin; 'it' = Bitcoin.",
   ["The pseudonymous Satoshi Nakamoto: whitepaper October 2008, network launched January 2009; real identity unknown."]),
  ("And the other one?", ["Ethereum", "Vitalik"], "'The other one' = Ethereum (the two coins discussed are Bitcoin and Ethereum).",
   ["Proposed by Vitalik Buterin (whitepaper late 2013), co-founded with others such as Gavin Wood; mainnet launched July 2015."]),
  ("What is its maximum supply?", ["Ethereum", "ETH", "ether"], "'Its' = Ethereum, the coin of the previous turn.",
   ["No fixed hard cap: new ETH is issued to validators while part of every fee (the base fee) is burned since EIP-1559 (2021), so supply can grow or shrink; roughly 120 million ETH."]),
  ("How does that compare with the first coin's limit?", ["Bitcoin", "BTC"], "The first coin = Bitcoin.",
   ["Bitcoin is capped at 21 million BTC, reached around 2140; the block subsidy halves every 210,000 blocks (about 4 years). Ethereum has no such cap."]),
  ("When is the next halving?", ["Bitcoin", "BTC"], "Context: Bitcoin's halvings.",
   ["The last halving was in April 2024 (block 840,000); the next is expected around 2028 (block 1,050,000)."]),
  ("What is a block explorer and which one would I use for it?", ["Bitcoin", "BTC"], "'It' = Bitcoin.",
   ["A website to look up blocks, transactions and addresses on a public chain; for Bitcoin e.g. mempool.space or blockstream.info."]),
  ("And for the second chain?", ["Ethereum", "Etherscan"], "The second chain = Ethereum.",
   ["Etherscan (also Blockscout); for validators / the beacon chain, beaconcha.in."]),
  ("Can I see my validator there?", ["beaconcha", "Etherscan", "Ethereum", "beacon"], "'There' = the Ethereum explorers just named.",
   ["Yes: beaconcha.in (beacon chain explorer) by validator index or public key shows balance, attestations, proposals and missed duties; Etherscan shows the deposit and withdrawals."]),
  ("What does a missed attestation cost me?", ["validator", "Ethereum", "ETH"], "Context: an Ethereum validator.",
   ["A small penalty roughly equal to the reward it would have earned for that epoch (a tiny fraction of an ETH, a few thousand gwei); not slashing."]),
  ("Summarise in three bullet points what we said about the two coins.", ["Bitcoin", "Ethereum"], "The conversation covered Bitcoin vs Ethereum: consensus, validators, creators, supply, halvings, explorers.",
   ["Three bullets consistent with the earlier turns: Bitcoin = proof of work, 21 M cap with halvings, Satoshi Nakamoto, no native staking; Ethereum = proof of stake, 32 ETH validators, no hard cap / fee burn, Vitalik Buterin; explorers (mempool.space vs Etherscan / beaconcha.in)."]),
 ],
 "ls06": [
  ("What is the best way to get around Kyoto?", None, None,
   ["City buses and the two subway lines, plus JR / Keihan / Hankyu trains for outlying sights; walking and cycling in the centre; an IC card (ICOCA / Suica) for fares."]),
  ("How do I get from the city to Kansai International Airport?", ["Kyoto"], "'The city' = Kyoto.",
   ["JR Haruka limited express from Kyoto Station, about 75-80 minutes; or the airport limousine bus, about 90 minutes."]),
  ("Switch of topic: what is the square root of 1,764?", None, "Abrupt topic switch to arithmetic.",
   ["42."]),
  ("And a 15% tip on a 68-dollar bill?", None, None,
   ["10.20 dollars (total 78.20)."]),
  ("How many kilometres is 26.2 miles?", None, None,
   ["About 42.2 km (26.2 x 1.609)."]),
  ("Back to Japan: is tipping expected there?", ["Japan"], "Returns to the Japan trip of turns 1-2 and 5-7.",
   ["No: tipping is not customary in Japan and can cause confusion; good service is included; some ryokan or guides may accept a gift in an envelope."]),
  ("What is a ryokan?", None, None,
   ["A traditional Japanese inn: tatami rooms, futon bedding, yukata, often an onsen / shared bath and a multi-course kaiseki dinner and breakfast."]),
  ("Can you recommend an area for one near the first city we discussed?", ["Kyoto"], "The first city discussed = Kyoto; 'one' = a ryokan.",
   ["Kyoto areas such as Gion / Higashiyama, Arashiyama, or Kurama / Kibune in the northern hills (or Yunohana onsen)."]),
  ("What is the etiquette in the shared hot spring bath?", None, None,
   ["Wash and rinse fully at the shower stations before entering; bathe naked (no swimsuits); keep the small towel out of the water; tie long hair up; be quiet; tattoos may be refused at some baths."]),
  ("How do I say thank you in Japanese?", None, None,
   ["Arigatou gozaimasu (polite); arigatou (casual)."]),
 ],
 "ls08": [
  ("When is the best time to see the northern lights in Iceland?", None, None,
   ["From about September to mid-April, on dark, clear nights away from light pollution, typically 21:00-02:00; check the aurora and cloud forecast (vedur.is) and the Kp index."]),
  ("What is the Golden Circle?", None, None,
   ["A popular loop of about 230-300 km from Reykjavik covering Thingvellir National Park, the Geysir area (Strokkur) and Gullfoss waterfall."]),
  ("Can I visit the Blue Lagoon on the way from the airport?", None, None,
   ["Yes: it lies about 20 minutes from Keflavik airport, roughly between the airport and Reykjavik; pre-book a time slot; luggage storage is available; transfer buses combine the stop."]),
  ("What is the currency in Iceland and do I need cash?", None, None,
   ["Icelandic krona (ISK); cards (and phone payments) are accepted almost everywhere, so cash is rarely needed; a card with a PIN helps at unmanned fuel pumps."]),
  ("How expensive is fuel there, roughly?", None, None,
   ["Among the highest in Europe: roughly 300-340 ISK per litre (about 2.2-2.5 USD); many stations are self-service with card and PIN."]),
  ("Do I need a 4x4 to drive the F-roads?", None, None,
   ["Yes, 4x4 is legally required on F-roads; they open roughly late June to September; river crossings are common and rental insurance usually excludes water damage."]),
  ("What are the main hazards at Reynisfjara beach?", None, None,
   ["Sneaker waves and strong undertow (fatal accidents have happened): stay well back from the waterline, never turn your back to the sea, follow the warning-light signs; rockfall near the basalt cliffs."]),
  ("Where can I see puffins and in which months?", None, None,
   ["Roughly May to mid-August; places such as the Westman Islands, Dyrholaey, Latrabjarg cliffs, Borgarfjordur eystri."]),
  ("How long is the drive from Reykjavik to Akureyri?", None, None,
   ["About 390 km on Route 1, roughly 5 hours without stops."]),
  ("What is there to do in Akureyri?", None, None,
   ["Akureyri church, botanical garden, whale watching in Eyjafjordur, Forest Lagoon spa, Hlidarfjall skiing in winter; nearby Godafoss and Lake Myvatn."]),
 ],
}
def main(d):
    os.makedirs(d, exist_ok=True); Q = []; SS = []
    for sid, shape, cat, turns in S:
        assert len(turns) == 5
        ids = []
        for i, (q, ref, ctx, rub) in enumerate(turns, 1):
            iid = f"{sid}-t{i}"; ids.append(iid)
            rubric = ([f"Conversation context (the system saw the earlier turns): {ctx}"] if ctx else []) + rub
            Q.append({"id": iid, "session": sid, "turn": i, "shape": shape, "followup": ref is not None, "referent": ref or [],
                      "category": cat, "lang": "en", "question": q, "rubric": rubric, "source": "agent-written dev (LONGSESSION 2026-10-14)"})
        SS.append({"session": sid, "shape": shape, "topic": cat, "turns": ids})
    shape_of = {sid: (shape, cat) for sid, shape, cat, _ in S}
    for sid, turns in EXT.items():
        shape, cat = shape_of[sid]; assert len(turns) == 10
        for i, (q, ref, ctx, rub) in enumerate(turns, 6):
            iid = f"{sid}-t{i}"; rubric = ([f"Conversation context (the system saw the earlier turns): {ctx}"] if ctx else []) + rub
            Q.append({"id": iid, "session": sid, "turn": i, "shape": shape, "followup": ref is not None, "referent": ref or [],
                      "category": cat, "lang": "en", "question": q, "rubric": rubric, "source": "agent-written dev (LONGSESSION addendum 1, 2026-10-14)"})
        next(x for x in SS if x["session"] == sid)["turns"] += [f"{sid}-t{i}" for i in range(6, 16)]
    qp, sp = os.path.join(d, "questions.jsonl"), os.path.join(d, "sessions.jsonl")
    open(qp, "w").write("".join(json.dumps(x, ensure_ascii=False) + "\n" for x in Q))
    open(sp, "w").write("".join(json.dumps(x) + "\n" for x in SS))
    h = lambda p: hashlib.sha256(open(p, "rb").read()).hexdigest()
    open(os.path.join(d, "SHA256SUMS"), "w").write(f"{h(qp)}  questions.jsonl\n{h(sp)}  sessions.jsonl\n")
    print(f"items {len(Q)} sessions {len(SS)} followups {sum(x['followup'] for x in Q)} questions_sha256 {h(qp)}")
main(sys.argv[1])
