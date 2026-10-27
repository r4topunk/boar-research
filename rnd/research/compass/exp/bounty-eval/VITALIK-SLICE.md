# the post author slice (Compass, 2026-10-03; bounty eval #1)
TL;DR: two parts, always **reported separately** from the main bench ratio.
- **V-exact (public):** the post author's own test questions, verbatim from his posts. These are the four he typed into the three apps on 2026-09-26, two more from his other posts, and his literal vegan eval in its named-city and GPS forms.
- **V-para (blind):** about 54 close paraphrases and same-family questions, written by a fresh agent the coordinator commissions. Nobody on the team reads them before the claim run.

V-exact shows how BOAR does on exactly what he will type. V-para shows it isn't overfit to those strings. References are frontier + web with the frozen recipe; venue items are graded against OSM gold, not an LLM reference.

## V-exact: 11 items (`vslice-exact.ids.txt`; new items in `vslice-exact.new.jsonl`, the rest reused from bench v0.1)
| id | question (verbatim) | where he asked it | grading | ref |
|---|---|---|---|---|
| vx-001 | Tell me about Japan | 2026-09-26 post, screenshot 1 (a competitor team) | precheck (Tokyo, islands; forbid the "330 km²" magnitude error his test exposed) + judge | **to generate** (frontier + web) |
| vx-002 | Which signature algorithms are quantum resistant? | 2026-09-26 post, screenshot 2 (BOAR, with RSA sources) | precheck (ML-DSA/Dilithium; SLH-DSA/SPHINCS+/Falcon/XMSS/LMS) + judge | **to generate** |
| vit-hum-001 | Explain Mozi's views on universal love. | 2026-09-26 post, screenshot 3 (a competitor team) | precheck + judge | v0.1 frozen |
| vit-hum-004 | Why does Gríma kill Saruman in The Lord of the Rings? | Farcaster 2026-09-02 (over-refusal case) | precheck + judge | v0.1 frozen |
| vit-trv-004 | How far is it to walk from Paris to Rome and back? | close paraphrase of his secure_llms example (the 312.5 km error) | precheck + judge | v0.1 frozen |
| food-001/002/006 | Tell me the best vegan restaurants in Berlin / Lisbon / Tokyo | his literal eval, city named | venue-list vs OSM gold (≥ 3 real venues) | OSM gold, v0.1 |
| vx-003/004/005 | Tell me the best vegan restaurants in the city I am currently in | his literal eval, "[city I am currently in]", with a **GPS fix** (`context.lat/lon`) in Berlin, Lisbon, Tokyo | venue-list vs the same OSM gold; the city must come from the location, not the text | OSM gold, v0.1 |

- **Not included (team decision 2026-10-01, no competitor test cases):** the 31 test cases in a competitor repo `tools/e2e*.json`, even though they sit on his account. "Tell me about Japan" is included because it is his own query in his own post.
- **Coordinator decision:** do you want those 31 items as a separate, clearly labelled "his fork's tests" slice, given that the repo is on his account? Recommendation: no, keep the 2026-10-01 rule.

## V-para: blind paraphrase set (brief for the writer the coordinator commissions)
Path: `blind/V-para/items.jsonl`, written by a fresh agent with no access to BOAR's repos, dev sets or this folder (except this brief), and hashed before any run. **About 54 items, EN** (the post author writes in English), in the bench v0.1 schema (`questions.schema.json`): id, category, question, lang, danger, rubric (3–5 points), grading (precheck must_any/forbid/refuse_ok, or venue-list with OSM gold), reference_sources (Wikipedia or official), origin `vitalik-para`.
1. **Close paraphrases of the 4 screenshot/post questions (5 each = 20).** Same intent, different wording or register.
   - Short, lowercase, typos, "give me a quick rundown of…", "what's the deal with…", follow-up style.
   - Topics: Japan overview; quantum-resistant signatures; Mozi's universal love; vegan restaurants in the city I'm in (GPS context, 3 cities not in v0.1, each with an OSM gold snapshot).
2. **Same families × the bounty's four task types (24).** Country/place overview, post-quantum or Ethereum research, Chinese or Western philosophy, his science and health interests. 6 each of explanation, comparison, synthesis and reasoning. Hard enough that a 1B model fails ("include ones a 1B model would fail on").
3. **Specialized travel, his self-declared weakest area (10).**
   - Diet + attribute + time at the current location: vegan with outdoor seating, open now.
   - Transport between towns, local practicalities (plugs, SIM, tipping, visas on arrival), "near me" with a GPS fix.
   - Gold: OSM for venues, Wikivoyage or official pages for the rest.
- Rules: no item copies a v0.1 / v0.2 / dev-set question (the coordinator checks similarity ≤ 0.6); no personal data; facts checked against the cited pages on the writing date; a gold `answer` per item that passes its own precheck.

## References (frontier + web, frozen recipe)
- `boar-eval/bench/v0.1/refs/gen_refs.mjs`: `claude -p` with `--model opus`, system prompt `reference.v1`, tools WebSearch + WebFetch, one call at a time, [usage detail removed] only (no API keys), manifest of sha256 per answer.
- Run it on vx-001, vx-002 and all V-para judge items. Venue items use OSM gold instead.
- Reference texts stay gitignored (provider terms); hashes go in `MANIFEST.json`.

## Scoring and reporting
- Same judge (`judge.v1`, opus, both orders) and the same frozen metric (`floor_metrics.py`, D = 0.306) as the main bench.
- Venue items are reported as venues found / ≥ 3 real (OSM).
- **Reported separately** by `claim_report.py` (a `slices` entry): V-exact with a per-item table for every system and the ladder (his questions are public, so per-item rows are fine); V-para as aggregates only, with plain bootstrap CIs.
- Seeds 42, 43 (and 44 if the main claim runs 3). Devices: the Android 12 GB tier is the headline; the iPhone 1.5B is the 1B-class context.
- Neither slice changes the main bench verdict. The bar is still judged on the main set (analysis plan §3).
