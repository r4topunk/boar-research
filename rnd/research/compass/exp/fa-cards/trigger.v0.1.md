# First-aid condition cards v0.1: trigger (supersedes trigger.md v0 before QUEUE #14 runs)
Changes vs v0, from an independent out-of-sample check on 400 FirstAidQA questions (exp/firstaidqa/, CC BY 4.0 synthetic; blind sets untouched):
- REMOVED the embedding-centroid fallback (step 3 of v0): it fired 4 times and was wrong on 3 (incl. a diabetic, i.e. hypoglycemia, given the heatstroke card).
- terms.py: jellyfish terms add "blue bottle|bluebottle" (a bluebottle sting with "hot water" matched burn alone; now burn + jellyfish = MULTI → no specific card).
Trigger v0.1:
1. Gate unchanged: only where A1 or the health path would show the generic no-source card.
2. terms.regex_condition(query) returns exactly one condition → that card; MULTI or none → generic card.
3. Snakebite unchanged. Card texts unchanged (cards.v0.json).
