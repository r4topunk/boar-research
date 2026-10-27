# Bounty #31 ground truth: what is asked, what the post author said, how rivals measure (2026-10-19)

**Sources checked live on 2026-10-19:**
- **[P] poidh API:** `https://poidh.xyz/mainnet/bounty/31/data`, which is the JSON behind `https://poidh.xyz/mainnet/bounty/31`.
- **[V1] the OG post**, `https://x.com/VitalikButerin/status/2100695863026954698` (2026-09-17). I read it through the public mirror `api.fxtwitter.com`, because x.com returns 402. It replies to `x.com/darmandgwei/status/2100607223542251898`.
- **[V2] the follow-up post**, `https://x.com/VitalikButerin/status/2103762130554204651` (2026-09-26).
- **[V3] a privacy self-experiment post**, `https://x.com/VitalikButerin/status/2106537633056969024` (2026-10-04).
- **[B] the blog post** `https://vitalik.eth.limo/general/2026/04/02/secure_llms.html` ("My self-sovereign / local / private / secure LLM setup, April 2026").
- **Competitor READMEs** on GitHub.

**Checks:**
- The bounty text in `<workspace>/BOUNTY_31.md` matches [P] word for word.
- The local status block in that file is stale. Live values: **1.53575 ETH, 17 contributors, 7 claims** (#115, #124, #125, #132, #134, #137, #142), `deadline: None`, `acceptingClaims: true`.
- `CLAIMS_31.md` lacks #134, #137 and #142.

---

## 1. The bounty, clause by clause

Notation: **M** = must (pass/fail gate), **J** = judged against (a graded bar), **P** = proof deliverable. All quotes come from [P] / `BOUNTY_31.md`.

| # | Exact text | Type | Testable form | Ambiguity / misreading risk |
|---|---|---|---|---|
| 1 | "Build a casual info lookup and research tool that runs entirely offline on Android and is >50% as good as internet search + frontier AI models." | J | Quality ratio vs a reference system on a casual-lookup query mix | "casual", "research", ">50% as good", "internet search + frontier AI models" (see §4) |
| 2 | "People travel with their phones into offline situations all the time" | context → J | Query mix must over-represent **travel / on-the-road** needs | Easy to under-weight. the post author's own eval is a travel query (V2) |
| 3 | "His past attempts got ~10 tokens/sec from 1B models that break on anything interesting." | context | Two baselines to beat: ~10 tok/s, and 1B quality | Not a numeric requirement, but it defines "failure" |
| 4 | "~100B params, most living on disk, with <1B activated per token. That's one promising direction, not a requirement." | — | none | Do **not** score architecture |
| 5 | "run on Android and compatible GrapheneOS hardware" | M | Install and run on GrapheneOS, no Google services | Issuer: "GrapheneOS compatibility is a requirement" (comment 1201) |
| 6 | "operate within a maximum **12GB RAM environment**" | M | Device has ≤12 GB total RAM | A device ceiling, not an app-RSS target. 8 GB phones are allowed |
| 7 | "use no more than **50GB total** for the app, model weights, indexes, databases, and other offline assets (streaming weights from disk is expected)" | M | Sum of installed bytes ≤ 50 GB | Includes the app itself |
| 8 | "work completely offline once installed" / "make no API calls, remote inference requests, web searches, or other network requests during use" | M | No INTERNET permission, or a measured 0 bytes of traffic | A one-time download at install is allowed ("once installed") |
| 9 | "not require Google Play Services for core offline functionality" | M | No `com.google.android.gms` | — |
| 10 | "handle useful research questions beyond simple factual recall, including explanation, comparison, synthesis, and reasoning" | M/J | Query mix must contain these four types, and they must be answered usefully | "**beyond**" means *in addition to* recall, not *instead of* it. V2 says the goal is to "look up any facts about the world" |
| 11 | "respond at speeds that feel usable for real lookups on a phone" | J | Latency (time to first useful content, time to full answer) on a real phone | No number is given. "feel usable" is subjective; see the post author's own numbers in §2 |
| 12 | "be published in a public GitHub repository" / "include all code, assets, dependencies, and instructions needed to reproduce" / "clearly document the models, datasets, indexes" | M | Repo audit | — |
| 13 | "Architecture is open." / "There is no parameter-count limit." | — | — | — |
| 14 | "Someone with a compatible Android or GrapheneOS device should be able to visit the GitHub repo, follow the instructions, and get the app running locally within a few minutes without substantial debugging." | M | Time a fresh install by a third party | **"within a few minutes" is about SETUP, not answer latency.** Rivals already admit far longer setups (a competitor team: "Setup, about an hour and a half"). A download could arguably be excluded, but the text does not say so |
| 15 | "Any required models, databases, indexes, or other assets must either be included or have clear download and installation instructions." | M | — | — |
| 16 | "Post a public demo on **X or Farcaster** showing: the app running offline; several example queries and responses (include ones a 1B model would fail on); a link to the public GitHub repo; a brief explanation" | P | Demo includes queries a 1B model fails | "ones a 1B model would fail on" is a **proof** item. It hints that the judged bar sits *above* 1B quality, which supports a 1B floor (see §4) |
| 17 | "Submissions are judged against the requirements above and the bar described in the post author's post: a useful, fully offline research tool that's >50% as good as internet + frontier models." | J | Final bar | Here the wording drops "search" ("internet + frontier models", as in V1) and adds "**useful**" |
| 18 | "If the post author publicly confirms that a submitted build meets that bar, that submission wins" … "Otherwise … select a winner they believe best satisfies the requirements and spirit of the post author's request" | judges | Two judges: (a) the post author's own subjective confirmation; (b) "the creator and bounty contributors" | Path (b) is a relative ranking among entries ("best satisfies"), not a fixed threshold |
| 19 | "Note: … He is not affiliated with it or involved in judging unless he chooses to weigh in." | — | — | Do not claim the post author endorsed anything |
| 20 | "Submissions that are … materially different from the version reviewed … may be disqualified." | M | Freeze and tag the reviewed build | Issuer: "the best way to continue refining your app before the deadline is to update your submitted repo" (comment 1279). Updates are expected, but the reviewed version must match |

**Issuer comments on [P]** (by kenny, the bounty issuer):
- 1159/1160: "there is no specific deadline … if the post author says an app fits his requirement before October 31st, it gets the prize if he doesn't, contributors will make an executive decision"
- 1278: "we are organizing contributors to review all submitted apps before the deadline"
- 1230 (an entrant): "does ui/ux play any role or only core functionality matters". This question is **unanswered**.

---

## 2. the post author's public words (exact quotes)

### V1 — OG post, 2026-09-17
https://x.com/VitalikButerin/status/2100695863026954698

> "I agree with this and I keep trying every few months.
> My killer app is having a casual info lookup / research tool that's >50% as good as internet + frontier models that can function on a fully offline phone.
> (As people travel with their phones to situations where they're offline all the time)
> There the goal is not even just CROPS, it's utility - and the problem is that if you're literally offline, magic remote FHE inference won't help you.
> And so far I've gotten like 10 TPS with 1B models that break if you try to use them for anything interesting :(
> I think the right architecture for phone might be extreme MoE (including newer varieties like ngrams), eg. you want like 100B params most of which live on disk and only <1B get activated per token"

**Context: what V1 replies to.** It answers @darmandgwei: "My concern is that the bar for mass adoption is 'Can the frontier run on a phone?' and we're still a long way off from that tech." That post quotes the post author's own earlier post: "I think we're very close to the point where you can just use local models for a large share of tasks, and for anything more advanced, workflows like 'use your local model to orchestrate queries to powerful models…' actually become viable." So ">50% as good" is the post author **lowering the bar from "frontier on a phone" to "half as good"**.

What V1 establishes:
- The criterion is **"utility"**, not privacy (CROPS).
- The reference is **"internet + frontier models"**, which is the way the post author himself works: an LLM plus web search.

### V2 — follow-up, 2026-09-26
https://x.com/VitalikButerin/status/2103762130554204651 (1388 likes, 347k views). This is the **only public signal of how he actually evaluated entries**.

> "Testing out some of the mobile offline local knowledge apps that people have been trying to build (see here https://poidh.xyz/mainnet/bounty/31 )
> Definitely getting much better than the one I tried to build myself 2 months ago. But also still much slower and less effective at difficult questions than the models that can run on a laptop.
> It's weakest at specialized travel-related queries (eg. my eval is "Tell me the best vegan restaurants in [city I am currently in]", unfortunately none of these performed well on that)
> Looking forward to seeing these continue to improve! I hope we can soon get to the point where you can comfortably look up any facts about the world that you care about without needing to access the internet at all."

Reading of V2:
- His **comparison point in practice was laptop-runnable models**, not only internet + frontier.
- He judged on two axes, **speed ("much slower")** and **"difficult questions"**.
- He has a **named personal eval**: a location-dependent travel query in the **current city**.
- His end goal is **"look up any facts about the world that you care about"**, so factual lookup is core.
- Secondary coverage (PANews) misquotes "vegan" as "vegetarian". The original says **vegan**.

### V3 — 2026-10-04
https://x.com/VitalikButerin/status/2106537633056969024

> "Qwen 3.8 Flash Next is still too slow for comfort. It's comfortably running at 20-30 TPS, but it would only really start to feel fast at 100+"

### B — blog, 2026-04-02
https://vitalik.eth.limo/general/2026/04/02/secure_llms.html
- Speed: "For me personally, anything slower than 50 tok/sec feels too annoying to be worth it. 90 tok/sec is ideal." This is on a laptop.
- Offline knowledge: "A world_knowledge folder, where I have a dump of all Wikipedia articles and regularly throw in manuals (eg. Vyper documentation) for things I care about" … "The goal … is to reduce my reliance on internet searches, both so that I can be smarter when offline (eg. on airplanes)". This shows his own design is **retrieval over a local corpus**.
- **How he compares research tools:** "I did a side-by-side test … and I fed both outputs into an LLM to ask which is better." This is **pairwise LLM-as-judge**, which is the method he trusts.
- On quality: "Local Deep Research … responses are, in my view, pretty bland and not very high-quality". So blandness counts as a defect.
- Failure mode: "Of course, AI, especially small models … can make mistakes: the walking distance from Paris to Rome and back is 2768 km, not 312.5 km." Arithmetic and travel errors are salient to him.
- Pattern: "performs extremely well on civilization's well-trodden ground, but starts breaking down quickly on unfamiliar territory."
- Task taxonomy: "There is a set of 'bounded' tasks, eg. transcription, summarization, translation … that laptop AI can already do well … and even phones. But there is another set of tasks that will always benefit significantly from having 'even more intelligence' … intellectual work is another."

### Gaps (public data only)
- I could not read his **replies inside the V1/V2 threads**. V1 has 19 replies and V2 has 287. X returns 402, and nitter/xcancel are down (nitter's notice of 2026-10-10 cites a takedown).
- **Which apps he tested is unknown.**
- No blog post since April covers LLMs. The 2026-09-27 post is "The cryptographic world computer".

---

## 3. How the competing claims measure themselves (public)

All three entries that report a ">50%" number use the same convention: **mean rubric score (app) / mean rubric score (Claude Opus 5.5 + web search)**. This is becoming the field's default ruler.

| Claim | Exact public text | Method |
|---|---|---|
| #134 a competitor team (a competitor team) | "On 63 of my own questions, it scores 53% of Claude Opus 5.5 with web search." (poidh claim). README: "The score ratio is our mean score divided by the baseline's mean score." "The baseline wins almost every single question (61 losses, 1 tie, 1 win). a competitor team gets half the points, not half the wins." "The ratio changes by about ±[competitor score removed] between two runs of the judge." [competitor link removed] | Author's own questions; Claude grades both answers blind (correctness, completeness, grounding, usefulness); desktop run "with the phone's settings" |
| #137 Offline Research (a competitor team) | "On 61 blind-graded questions the 35B model reached 45% of Claude Opus 5.5 with web search" (claim). README: "54% … (build 0.8.4)"; "The 54% is not a safe pass. Grader instances have differed by ten points … these 61 questions were used to find and fix faults." [competitor link removed] | Score ratio; admits tuning on its own test set; phone 8 GB, "first word after a median of 247 s" |
| #125 a competitor team (a competitor team) | "We measured it on 61 the post author-style questions from Boar's evaluation set … A frontier model (Claude Opus 5.5) answered with web search. The answers were graded blind in pairs, 0-10, with the graders checking facts on the web." Result: "All (61) 6.0 / 9.3 / 64%". "The reference was better on every question." [competitor link removed] | Pairwise 0–10 score ratio on **our** public items. Reports "60-65% … depending on the graders" |
| #132 Outpost | "two measured failures from TinyLlama 1.1B under the same document questions" (claim) | Demonstrates the 1B-fail proof item only |
| #142 baby-zack | "engine tests 16/16" | No quality ratio |
| #124 Boar (the app maintainer) | "An open benchmark on the phone … load time, time to first token, tokens/s, memory and every answer" | Speed and memory only, no ratio |

**Observations:**
- Every rival reports **≈ [competitor score removed] win-rate together with a [competitor score removed] score ratio**. Under the score-ratio reading, several rivals "pass" with numbers whose noise (±[competitor score removed]–[competitor score removed], by their own admission) is as large as their margin over [competitor score removed].
- No rival corrects for the rubric floor. A blank or generic answer still earns points, so the ratio is inflated. This is the gap our floor-adjusted + win-rate protocol fills.
- a competitor team already runs on Boar's public item set, so our set is becoming a shared ruler. That raises the bar for its correctness.

---

## 4. Candidate interpretations of ">50% as good as internet + frontier models"

| ID | Interpretation | Operationalization | Text support | Problems |
|---|---|---|---|---|
| I1 | **Raw score ratio** | mean rubric(app) / mean rubric(ref) > 0.5 | Literal "50% as good" as a quantity; used by every rival | Depends on scale origin. Floor credit means a useless answer scores > 0; per CLAUDE.md our raw 0.50 is "a rubric-floor artefact". The judge family shifts it by about 0.10 (XFAM) |
| I2 | **Floor-adjusted ratio** | (app − floor) / (ref − floor) > 0.5, where floor = a useless or 1B answer | "1B models that break on anything interesting" are the failure state; the proof asks for "ones a 1B model would fail on" | Choice of floor (zero-content vs 1B) must be pre-registered |
| I3 | **Pairwise win/tie rate** | P(app ≥ ref) > 0.5 | B: the post author's own method is pairwise ("ask which is better") | Text says "50% as good", not "as good 50% of the time". Under this reading ≈0 % for every entry, so the bar becomes unreachable, which contradicts the bounty's premise that it is attainable |
| I4 | **Utility / task-success ratio** | share of queries where the user's need is met (app) ÷ same for ref | V1: "it's utility"; bounty: "a **useful** … research tool"; V2: "comfortably look up any facts … you care about" | Needs a pass/fail usefulness rubric and a definition of "met" |
| I5 | **Share-of-tasks coverage** | fraction of a realistic personal query stream (travel, local, facts, research) answered acceptably | Parent thread: "use local models for a large share of tasks"; travel framing | Needs a representative query distribution, which nobody has |
| I6 | **the post author's holistic judgment** | he tries it, including his vegan-restaurant eval, quality on "difficult questions" and speed | Winner clause: confirmation is entirely his call; V2 shows how he does it | Not reproducible; a benchmark can only predict it |

**The text supports I4 best, with I2 as its scalar form and I6 as the actual decider.**
1. V1 states the objective explicitly: "the goal is not even just CROPS, it's utility". The judged-against sentence adds "**useful**". "As good as" a lookup tool is most naturally the fraction of the reference's usefulness delivered, which is I4 per query, aggregated.
2. I1 is the literal surface reading, but its zero point is arbitrary. A 1B model that "breaks on anything interesting" would still score well above 0 on a 0–10 rubric. The bounty treats 1B output as failure (proof clause), so the scale origin must sit at "useless", which gives I2.
3. I3 matches the post author's personal comparison *method* but not the *threshold wording*. Report it as a mandatory secondary metric, not as the bar.
4. V2 reveals the operative test: the post author tries apps himself, compares them to laptop models, weights "difficult questions", speed, and a location-dependent travel query. Any ruler that omits **(a) travel/local queries using the user's current location, (b) hard multi-step questions, (c) speed** will be misaligned with I6.

---

## 5. Implications for the ruler: Decisions / Options / Tasks

**Decisions (supported by the text):**
- D1. Headline metric: a floor-adjusted utility ratio vs "internet + frontier model". Always report the win/tie rate and the raw ratio next to it, and name the judge family.
- D2. Include a **"current city" travel stratum** (vegan / restaurant / place queries using device location), mirroring V2. Otherwise we diverge from the post author's only stated eval.
- D3. The query mix must cover **factual lookup** (V2's "any facts about the world") **plus** "explanation, comparison, synthesis, and reasoning" (req. 10), plus travel arithmetic (B's Paris–Rome example).
- D4. Speed is a separate, reported axis:
  - first useful content
  - complete answer
  - long-session behaviour

  Anchor the bands to the post author's own numbers: 10 TPS = failure baseline; 20–30 TPS "too slow for comfort"; 50 tok/s minimum on a laptop; 100+ "feels fast".
- D5. Include a 1B-model baseline arm in the ruler. This doubles as the floor and as evidence for proof item 16.
- D6. "Within a few minutes" = install/setup time. Measure it separately and never present it as answer latency.

**Options:**
- O1. Weight strata by a stated usage prior (e.g. travel-heavy) vs uniform.
- O2. Reference = Claude + web (the rivals' convention) vs a panel of frontier models + web (more faithful to "frontier models", plural).
- O3. Add a "laptop-model" reference arm, since V2 compared against laptop models.

**Tasks:**
- T1. Refresh `BOUNTY_31.md` status and `CLAIMS_31.md` with #134, #137, #142 and the live amount.
- T2. Retry getting V1/V2 thread replies via a public mirror once one is available, for any the post author clarification.
- T3. Pre-register the floor definition (I2) with a sha256 before any scoring run.

**UNKNOWN:**
- the post author's in-thread replies (unreadable).
- Which apps he tested.
- Whether "few minutes" excludes the asset download.
- Whether UI/UX counts (comment 1230 unanswered).
- Language: the bounty never says "English only". That is our scope choice, and the text does not support it. a competitor team answers "in the language of the question".
- The 2026-10-25 deadline in local memory is not on any public page. [P] shows `deadline: None`, and the bounty says "by October 31st, 2026".
