# Label spec: does this message need BOAR's emergency/health path?
BOAR is an offline phone assistant for travellers. For each item (last user message `msg`, optional earlier `history` turns), assign ONE label:

- **EMERGENCY** — someone (the user, a companion, a child, anyone present) is hurt, sick, poisoned, bitten/stung, injured, having a medical event, or in immediate physical danger (fire, flood, earthquake, tsunami, extreme cold/heat, drowning, electricity, carbon monoxide, unsafe water, lost in dangerous terrain) NOW or imminently; OR the message asks what to do / first aid / safety steps for such a situation, even phrased hypothetically ("what do I do if a scorpion stings my kid?", "should I suck out snake venom?"). Includes follow-ups in a conversation whose earlier turns describe such a situation ("e agora?", "is it serious?", "should I go to hospital?"). Includes a phrase the user wants translated if its content is an emergency ("how do I say 'my son is allergic and can't breathe' in Thai").
- **HEALTH_INFO** — health/medical information with no one in danger and no first-aid ask: vaccines for a trip, what dengue is, how altitude sickness works in general, pharmacies opening hours, "is tap water safe in Lima" for planning. (Borderline: if it describes current symptoms in a person → EMERGENCY.)
- **NOT** — everything else: greetings, chit-chat, trivia, history (incl. historical disasters/epidemics/deaths), geography, fiction, crypto, food, travel logistics, metaphors ("my heart is broken", "dor no peito de saudade", "this traffic is killing me"), sports injuries of famous people, animals as facts ("are box jellyfish venomous?" with no one stung = NOT unless asking safety steps for an encounter).

Also give `hard_neg: true` for NOT items that contain health/danger vocabulary (disease, venom, death, hospital, burn, chest, etc.) a keyword detector might confuse.
Decide from the text only. Be consistent; when truly ambiguous add `"unsure": true` and a 5-word reason.

Output: one JSON line per item, same order, to `labels.jsonl`: {"id": ..., "label": "EMERGENCY|HEALTH_INFO|NOT", "hard_neg": bool, "unsure": bool, "why": "<=8 words"}
