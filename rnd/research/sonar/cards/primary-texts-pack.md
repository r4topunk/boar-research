# Curated public-domain primary-texts pack (Project Gutenberg subset)
TL;DR: the post author's stack names Wikipedia + Gutenberg + science articles (thesis R12). Two bench items cite Gutenberg books as references: vit-hum-005, "invisible hand" and how often the phrase appears, → *Wealth of Nations* (#3300); vit-hum-006, Mill's harm principle → *On Liberty* (#34901). A small curated pack of public-domain classics in BOAR's format-2 builder would cover primary-text questions, including exact phrase counts that only a full text can answer.
Lane: Sonar · Status: idea · Priority: C
Axes moved: quality on humanities items, small. By the lane's exchange rate (≈ +0.003 ratio per item whose key enters the prompt), 2 items ≈ +0.006, so it is not measurable on the bench. Truthfulness ↑ for "what did X actually write" (quotes from the source instead of memory). Resources: tens to hundreds of MB.
Fits BOAR? Yes for the format: plain text → `build-wiki-pack.mjs`-style blocks + FTS. Long books need chapter-level chunking and titles ("Wealth of Nations, Book IV, ch. 2"). The phrase-count question needs an exact-phrase FTS query over one book (`"invisible hand"`, count rows). That is cheap and deterministic, but it is a new answer route (Anvil/engine).
Evidence:
- Bench v0.1 references: `https://www.gutenberg.org/ebooks/3300` and `https://www.gutenberg.org/ebooks/34901` (`boar-eval/bench/v0.1/questions.public.jsonl`).
- vit-hum-006 is a "not-in-pack" miss in exp-06. vit-hum-005 (Adam Smith) gets only "Wikivoyage: Kirkcaldy" today.
- License: PG texts not under US copyright can be redistributed freely in the US. The PG license allows stripping all PG references and trademark, which leaves "a text unrestricted by U.S. intellectual property law" (https://www.gutenberg.org/policy/license.html, accessed 2026-10-02). Outside the US, copyright term varies per country: UNKNOWN per work (Veil).
- The full `Invisible hand` Wikipedia article already states the phrase counts. The full-enwiki pack would answer vit-hum-005 too, so this pack's marginal value over `full-enwiki-pack-arm` is smaller.
Test in boar-eval: not worth an arm alone. If built, add it to the full-enwiki arm's kit and report the 2 items' key-in-context separately.
Cost to try: ~1 day (curation list, PG mirror fetch via their robot-access mirrors, chapter chunker, license strip). Risk: low.

## Details
Curation idea: books cited by Wikipedia's humanities vital articles plus the bench/eval references. PG's own "top 1000 downloads" list is a cheap proxy. Prefer a curated subset over all of PG (~70k books): retrieval noise grows with corpus size (exp-11: BM25 distractors in the big corpus).
