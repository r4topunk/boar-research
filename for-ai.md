# For AI: read this research with your own assistant

> Closed record · research record 1.0 · as of 2026-10-25 16:46; the author closed the research lines on 2026-10-23. Current standing, not a final result: Open fronts: https://r4topunk.github.io/boar-research/data/status.json.
>
> Final · as of 2026-10-25 16:46 · 0 of 71 wins on the phone, U-total 0.165 (Claude) / 0.242 (gpt-5.6-sol), below the 0.50 bar

## The files

- https://r4topunk.github.io/boar-research/llms.txt: the index (a short file), with how to read the numbers
- https://r4topunk.github.io/boar-research/llms-full.txt: the whole paper in one Markdown file (article, 18 chapters at AI-professional depth, decision log, glossary, facts)
- https://r4topunk.github.io/boar-research/index.md and https://r4topunk.github.io/boar-research/research/<chapter>.md: a Markdown twin of every article and chapter page, with #curious, #tech and #ai sections
- https://r4topunk.github.io/boar-research/map/<node>.md: a twin of every map node
- https://r4topunk.github.io/boar-research/data/facts.json, https://r4topunk.github.io/boar-research/data/timeline.json, https://r4topunk.github.io/boar-research/data/decisions.json, https://r4topunk.github.io/boar-research/data/experiments.json, https://r4topunk.github.io/boar-research/data/glossary.json, https://r4topunk.github.io/boar-research/data/status.json: the data, public rows only
- https://r4topunk.github.io/boar-research/data/index.json: file list with counts and sha256
- https://r4topunk.github.io/boar-research/CITATION.cff and https://r4topunk.github.io/boar-research/cite/: how to cite

## Ask your AI about this research (as of 2026-10-25)

Paste this into any assistant that can open links.

```text
You are helping me understand RatLab — A Boar Research: the research record of BOAR, an offline Android research
assistant built for poidh bounty #31, and of LabRat (formerly BoarLite), the app submitted to it.
This is research record 1.0 (as of 2026-10-25): the author closed the research lines on 2026-10-23;
the final on-phone benchmark of LabRat (DEVICE-FINAL) landed on 2026-10-25 and is the headline in status.json.
1. Read https://r4topunk.github.io/boar-research/data/status.json first: note its as_of date, banner, headline, history, open_fronts and changelog.
Then read https://r4topunk.github.io/boar-research/llms-full.txt. If you cannot fetch them, ask me to paste them.
2. Answer only from those files and from https://r4topunk.github.io/boar-research/data/*.json. Cite fact ids like [F-001] after every number.
3. Treat every result as the current standing as of the as_of date, not as a final result. Say the date when you
state where things stand, and mention any open front that could change the answer. Do not predict how open
fronts will turn out, in either direction.
4. The headline number is the second ruler (bench v0.4) measured on the phone (status.json "headline"). If it is
still pending, say so; do not substitute another number for it. Earlier readings are history: the same ruler on
a desktop copy of the app's pre-rename engine, and the old judge.v1 ratio of the 4B build. Never pool them.
5. Keep the three metric families apart (judge.v1 ratio, outcome-label shares, ruler U-total). With a judge.v1
ratio give raw and floor-adjusted together; with every number say the set, whether it was held-out or
development data, the judge family, n and seeds; lead with the win-rate. Never round a number into a better claim.
6. The thesis is the author's: small models need external knowledge, so the project built a harness around a
small model's real capabilities, tuned for the app user's experience. State it as a design statement; its
evidence and limits are the closing tests (right about two times in three when the right article reaches the
model, which happens about half the time; no gain on real development items). Never say the harness makes the
app "half as good".
7. As of 2026-10-25 the 0.50 bar has not been reached under the Claude judge on held-out data, and the desktop
ruler reading is below it. If my question assumes otherwise, correct it; if status.json is newer than this
prompt, follow status.json.
8. Say "the record does not say" when the files have no answer; do not guess.
Start by giving me a five-bullet summary at the depth I ask for: curious, tech, or AI professional.
```

---

Cite as: r4to, independent researcher. RatLab — A Boar Research (2026), research record 1.0, as of 2026-10-25. Text and data CC BY 4.0. Fact ids or a link must travel with a quote. How to cite: https://r4topunk.github.io/boar-research/cite/ · https://r4topunk.github.io/boar-research/CITATION.cff.

AI-reviewed, not clinically reviewed. Nothing here is medical advice.
