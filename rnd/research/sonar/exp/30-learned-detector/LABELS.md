# exp-30 provisional label spec (Sonar, 2026-10-03)

Provisional until Compass's labeling spec lands; Sonar will re-map to it (the binary target should survive).

Unit = one user message, optionally with the previous user turns of the same chat (`turns[-1]` is the message being classified).

## Binary target: `emergency` (1) vs not (0)

**1 = emergency / first-aid**, the health route must handle it (never a memory answer, never pack trivia):
- someone (the user, a child, a companion, a stranger nearby) **has or may have** an acute injury, poisoning, exposure, bite/sting, allergic reaction, breathing/heart/neuro symptom, heat/cold injury, drowning, burn, electric shock, overdose, pregnancy/infant red flag, etc. — happening now or just happened;
- a **present hazard** to a person ("scorpion in the baby's room, is it dangerous?", "smell of gas in the kitchen", "tsunami siren, what do we do");
- a **first-aid how-to**, even hypothetical ("what do you do if someone is choking?", "como tratar picada de cobra?");
- a short **follow-up** in a chat whose earlier user turns are an emergency ("e agora?", "is it serious?", "should I go to the hospital?").

**0 = not emergency**, three sub-classes kept for analysis:
- `health_info`: non-acute health knowledge (nutrition, chronic disease facts, vaccine schedules, how a drug works, fitness);
- `hard_negative`: looks like danger but isn't: figurative ("this deadline is killing me", "dor no peito de saudade"), trivia/history ("what injury ended Theismann's career?"), animal facts ("biggest scorpion in the world"), cooking ("burn the garlic"), crypto/tech ("Bitcoin is a bit volatile", "kill the process"), travel planning about risks ("is it safe to visit X in monsoon season?", "should I pack a first-aid kit?"), sports, games, fiction, news;
- `other`: ordinary chat/search (greetings, facts, travel, crypto, food).

Edge rules: a planning question about a *possible future* risk with no one affected and no present hazard = 0 (`hard_negative`). Self-harm/suicide = 1 with tag `selfharm` (a separate crisis route exists; kept so it can be excluded).

## JSONL schema
`{"id": "en-p-0001", "lang": "en|pt|es", "label": 1|0, "cls": "emergency|health_info|hard_negative|other", "tag": "<condition or negative type>", "turns": ["<earlier user turn>", "...", "<message to classify>"]}`
