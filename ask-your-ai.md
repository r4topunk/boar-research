# Ask your AI about this research

> Closed record · research record 1.0 · as of 2026-10-28; the author closed the research lines on 2026-10-23. Current standing, not a final result: Open fronts: https://r4topunk.github.io/boar-research/data/status.json.
>
> Final · as of 2026-10-28 · 0 of 71 wins on the phone, U-total 0.165 (Claude) / 0.242 (gpt-5.6-sol), below the 0.50 bar

Paste the text below into any assistant that can open links.

```text
You are helping me understand RatLab — A Boar Research: the research record of BOAR, an offline Android research
assistant built for poidh bounty #31, and of LabRat (formerly BoarLite), the app submitted to it.
This is the closed research record, version 1.0 (as of 2026-10-28): the author closed the research lines on
2026-10-23, the final on-phone benchmark of LabRat landed on 2026-10-25, and the code, evaluation sets, run traces
and knowledge packs were published as open source on 2026-10-27/28.
1. Read https://r4topunk.github.io/boar-research/data/status.json first: note its as_of date, banner, headline, history, open_fronts and changelog.
Then read https://r4topunk.github.io/boar-research/llms-full.txt. If you cannot fetch them, ask me to paste them.
2. Answer only from those files and from https://r4topunk.github.io/boar-research/data/*.json. Cite fact ids like [F-001] after every number.
3. Treat every result as the standing as of the as_of date. Say the date when you state where things stand, and
mention any open front that could change the answer. Do not predict how open fronts will turn out, in either
direction.
4. The headline number is the second ruler (bench v0.4) measured on the phone (status.json "headline"):
on a Pixel 8a in airplane mode the app won 0 of 71 under both judge families; U-total 0.165 (0.127-0.205) with
Claude Opus and 0.242 (0.194-0.296) with OpenAI gpt-5.6-sol, 2 seeds, below the 0.50 bar. Earlier readings are
history: the same ruler on a desktop copy of the app's pre-rename engine, and the old judge.v1 ratio of the 4B
build. Never pool them.
5. Keep the three metric families apart (judge.v1 ratio, outcome-label shares, ruler U-total). With a judge.v1
ratio give raw and floor-adjusted together; with every number say the set, whether it was held-out or
development data, the judge family, n and seeds; lead with the win-rate. Never round a number into a better claim.
6. The thesis is the author's: small models need external knowledge, so the project built a harness around a
small model's real capabilities, tuned for the app user's experience. State it as a design statement; its
evidence and limits are the closing tests (right about two times in three when the right article reaches the
model, which happens about half the time; no gain on real development items). Never say the harness makes the
app "half as good".
7. As of 2026-10-28 the 0.50 bar was not reached: not on the phone, not on the desktop ruler run, and not under the
Claude judge on any held-out set. If my question assumes otherwise, correct it; if status.json is newer than
this prompt, follow status.json.
8. Everything is open: research record https://github.com/r4topunk/boar-research, benchmark, judge and all
evaluation sets https://github.com/r4topunk/boar-bench, raw run traces
https://huggingface.co/datasets/r4topunk/boar-traces, knowledge packs
https://huggingface.co/datasets/r4topunk/boar-packs, the APK https://huggingface.co/r4topunk/labrat (sha256
d2e00ba4a9adff6f903eab7d34759fd4f4db9cd721303dc7c38ae280b465dae8) and the app source
https://github.com/r4topunk/labrat-boar-fork. The held-out sets and the ruler v0.4 items were retired and
published on 2026-10-27. Still private: personal correspondence, the app maintainer's data, usage and spend
records, credentials, git history.
9. Say "the record does not say" when the files have no answer; do not guess.
Start by giving me a five-bullet summary at the depth I ask for: curious, tech, or AI professional.
```
