# RatLab — A Boar Research, read as: Curious

> Closed record · research record 1.0 · as of 2026-10-28; the author closed the research lines on 2026-10-23. Current standing, not a final result: Open fronts: https://r4topunk.github.io/boar-research/data/status.json.
>
> Final · as of 2026-10-28 · 0 of 71 wins on the phone, U-total 0.165 (Claude) / 0.242 (gpt-5.6-sol), below the 0.50 bar

The story and the headline numbers, no jargon.

## 1 · The question {#question}

##### A phone in airplane mode

Imagine you are on a mountain, on a long flight, or somewhere the network is down. You still have questions: what is this plant, how far is the next town, what does this error mean. BOAR keeps a small AI model and a few downloaded libraries on your phone and answers from them, with sources.

##### The bounty's rules

The challenge had strict limits: an Android phone with at most 12 GB of memory, at most 50 GB of downloaded files, fully offline, open source. And one target: "more than 50 % as good as internet search plus a frontier AI." Winning is decided by a public confirmation, not by a score.

##### Half as good as what, exactly?

That sentence hides a research problem. Half of what? Measured how, on which questions, on which phone? If you grade a student's essay against a professor's, "half as good" depends on who grades and what counts. Before improving anything, we had to build a way to measure that we could trust.

##### Where we started

When the author joined the project, the app ran a small 1.5-billion-parameter model over about 1,300 Wikipedia paragraphs. A review called it "solid engineering, weak research": good code, but nobody knew how good the answers were.

**In one sentence card:** "The goal was simple to say and hard to measure, so the first job was building the ruler." No number.

*Facts: [F-682] [D-014] [E-003]*

Whole chapter: https://r4topunk.github.io/boar-research/research/question.md

## 2 · Building a ruler {#ruler}

##### A frozen answer key

For every test question, a top AI model with web search wrote one reference answer. We froze those answers and fingerprinted them, so every later test is compared with exactly the same text. That reference is our stand-in for "the internet plus a frontier AI".

##### A judge that can't peek

A strong AI model acts as the judge. It sees the question, BOAR's answer and the reference side by side, with links and source lists removed so it cannot tell which answer had the web. It scores both from 1 to 5 on correctness, completeness and usefulness, and picks a winner.

##### Then we swap them

Judges, human or AI, tend to favour whichever answer they read first. So every pair is judged twice, once in each order. If the judge changes its mind when the order flips, the question counts as a tie.

##### Rules written before the experiment

Every experiment got a pass/fail rule written down before it ran, and the rule file was fingerprinted (a sha256 hash), so nobody could quietly move the goalposts after seeing the result. Over the month there were dozens of these, and an outside reviewer later re-checked 16 of 17 sampled fingerprints as matching.

##### Practice questions and a sealed exam

Some question sets were public practice. Others were sealed: the people and agents building the app were never allowed to read them, and every time a script touched one, it was written in a ledger. When a sealed set leaked, we said so and demoted it to practice. (That happened; chapter 5.)

**In one sentence card:** "Every answer is graded twice, blind, against a frozen frontier answer, under rules written before the test." Badge: v0.1 public practice set, 60 questions (57 graded).

*Facts: [F-067] [D-002] [F-125] [F-649] [F-235] [D-019] [D-009] [F-1169] [D-006] [D-015] [D-037]*

Whole chapter: https://r4topunk.github.io/boar-research/research/ruler.md

## 3 · The floor trap {#floor-trap}

##### A blank answer still gets points

The judge's scale runs from 1 to 5, not 0 to 5. So even an answer that says nothing earns a 1. If you divide BOAR's points by the reference's points, a version of BOAR that politely declines every single question already scores about 0.31.

##### So 0.50 was 61 % free

That means the bounty's 0.50 line was more than halfway reached by doing nothing. A number that rewards silence is not a fair ruler.

##### Subtract the free point

The fix: subtract the free point from both sides before dividing. On this "floor-adjusted" scale, silence scores 0 and matching the reference scores 1. A floor-adjusted 0.50 means "half of the frontier answer's value above nothing". It is a stricter scale, and we made it our headline. We still print the flattering one next to it, so you can see both.

##### And we count wins

A third, plainer number: on how many questions did the judge prefer BOAR's answer over the frontier answer, in both orders? We report it everywhere. You will see a lot of zeros.

##### Our real starting point

Here is the small model the phone runs, on the bounty-style questions it had never seen: 0.413 on the flattering scale, 0.261 on the honest one, and 0 wins out of 51.

*Badge:* V-para (bounty-style, sealed at the time) · Claude Opus judge · 51 questions · 2 runs.

**In one sentence card:** "We grade on the scale where a blank answer scores zero, and still show the flattering scale beside it." Number: 0.261 floor-adjusted / 0.413 raw, 0 of 51 wins (badge as above).

*Facts: [F-263] [F-341] [D-036]*

Whole chapter: https://r4topunk.github.io/boar-research/research/floor-trap.md

## 4 · Seven frozen builds {#builds}

##### Snapshots, not tweaks

Every idea that passed its rule went into a numbered snapshot of the app, a frozen build (cut). There were seven. Cut 7 is the one we stand behind today.

##### What actually got better

Safety got better: a small detector spots emergencies and shows a short reviewed first-aid card instead of letting the model improvise. Instant answers got better: a calculator, a travel-distance estimator and a table of 4,233 facts answer in a blink. Phones got faster after we found our own bugs.

*AI-reviewed, not clinically reviewed. Nothing here is medical advice.*

##### What did not move

On the sealed questions, the small model's quality barely moved through all seven builds: from 0.506 to 0.512 on the flattering scale, a difference smaller than the noise between two identical runs.

*Badge:* v0.2 (sealed at the time, later demoted to practice) · Claude Opus · 110 questions · 2 runs.

**In one sentence card:** "Seven builds made the app safer and quicker, not smarter."

*Facts: [F-701] [F-358] [F-312] [F-313] [F-346]*

Whole chapter: https://r4topunk.github.io/boar-research/research/builds.md

## 5 · The walls {#walls}

##### Hand it the right page

We tried cheating on purpose: give the small model the exact passage that holds the answer. Its score rose from 0.507 to 0.606 on the practice set. So the reader can read. The question is whether the right page ever reaches it.

*Badge:* v0.1 practice · Claude Opus · 57 questions · 1 run.

##### The library doesn't have the book

Often it doesn't, because the downloaded libraries simply don't contain the fact. A smarter search that pulled the right sentence into the prompt more than twice as often still did not raise the score.

##### Bigger small models, longer answers: no

Swapping in other models of similar size did not help. Asking for longer answers made the model invent more.

##### An audit, and a burnt exam

On 6 October an internal audit said the process was rigorous but going in circles. The same day we found that one sealed exam's questions had sat in a private code history the builders could have seen. We declared it burnt: from then on it counts as practice.

**In one sentence card:** "The small model reads well enough; what it lacks is knowledge the phone doesn't hold."

*Facts: [F-314] [F-443] [F-992] [F-450] [F-433]*

Whole chapter: https://r4topunk.github.io/boar-research/research/walls.md

## 6 · The deep tier {#deep-tier}

##### A much bigger brain that mostly sleeps

The one idea that clearly beat the noise was a much bigger model: 35 billion parameters, built as a "mixture of experts". Think of a hospital with many specialists where each patient only sees a few. Only about 3 billion parameters work on each word, so it can run on strong hardware without needing all of its weights at once.

##### Scratch paper with a page limit

Then we let it think before answering: it writes hidden notes, up to a budget, and only then the answer. Thinking was the biggest single step we measured. And the budget had a sweet spot: 512 tokens of notes (a token is roughly a word piece) were as good as 1,024, in about half the time.

##### Climbing the ladder

On the bounty-style questions, the honest score climbs: 0.261 for the phone's small model, 0.329 for the big model, 0.436 for the big model with thinking. The line is 0.50.

*Badge:* V-para · practice-style for the big model (used for decisions after 6 Oct) · Claude Opus · 51 questions · 2 runs.

##### Still zero wins

Even at its best, the big model did not beat the frontier answer on a single one of the 51 questions. It would also need a phone with 12 GB of memory and, by our estimate, two to three minutes per answer. It only ever ran on a desktop: on 21 October the author decided not to ship it, and it stays in this record as a possible future, with its desktop numbers.

##### What's still missing

When we looked at where its remaining points were lost, most of it was knowledge the phone does not hold and the model does not know, and the rest was confident wrong facts.

**In one sentence card:** "A bigger model that thinks first got closest, 0.436, on a desktop, with no wins, and it was never shipped." Badge as in 6.3.

*Facts: [F-650] [F-033] [F-008] [F-010] [F-593] [F-009] [F-766] [F-1532] [F-1184]*

Whole chapter: https://r4topunk.github.io/boar-research/research/deep-tier.md

## 7 · A phone on a desk, and in a hand {#phone}

##### Testing on a desk

Running a test on a phone takes hours. Running the exact same code on a desktop takes minutes. We did most of the work on the desktop, and then checked it was telling the truth.

##### The phone fights back

A phone gets hot, runs short of memory and hides different bugs. On one 8 GB phone the model was killed while loading because a speed trick quietly made a second copy of its weights. On another, every question re-read the whole prompt because of a bug in our own code that the desktop could not show.

##### Same answers, slower

On a real phone, the frozen build on a 12 GB-class phone in airplane mode answered all 72 test questions and scored exactly what the desktop scored: 0.529 and 0.529. A typical answer took about 31 seconds.

*Badge:* v0.1 public practice set · Claude Haiku triage judge · 57 graded questions · 1 run.

##### The big model has not been on a phone

The 35-billion-parameter model never ran on a phone. A technique that streams the model's experts from storage kept its working memory under 3 GB on a desktop, and was even built for Android, but nobody measured it on a phone before the big model was dropped from the plan.

**In one sentence card:** "The phone matches the desktop on quality; it is just slower, and the big model never left the desktop."

*Facts: [F-686] [F-710] [F-023] [F-771] [F-036] [F-793] [F-2118] [F-1532]*

Whole chapter: https://r4topunk.github.io/boar-research/research/phone.md

## 8 · The agent lab {#agent-lab}

##### A lab made of AI agents

There was no university and no team of humans. The author set the direction and the limits; AI agents did the rest in roles: a coordinator that wrote the rules and kept the log, researchers in separate lanes who proposed ideas but never graded their own, and independent reviewers who checked every public sentence.

##### Most ideas died for free

Of 101 ideas that were closed, 54 were killed by cheap checks before any AI judge looked at them.

##### Four days on autopilot

For four days the coordinator ran by itself, waking up on a timer: 133 wake-ups, about 10,500 judge calls, 62 machine-hours of answer generation. The result: one improvement, and only on practice questions.

##### Rules grew out of mistakes

A ten-hour run produced 45 empty answers out of 120 because nobody ran a ten-question test first. The same large model file got deleted twice by housekeeping. The loop sat idle for hours. Each mistake became a written rule: 29 of them in 12 days.

**In one sentence card:** "An AI-agent lab can run real research, if every rule is written down and every mistake becomes a new rule."

*Facts: [D-008] [D-027] [F-915] [F-900] [F-903] [F-028] [F-641] [F-756] [F-899]*

Whole chapter: https://r4topunk.github.io/boar-research/research/agent-lab.md

## 9 · Knowledge packs {#packs}

##### Libraries you choose

If the phone lacks knowledge, give it the right library. We built and published 11 free, openly licensed offline libraries: question-and-answer archives, first aid, health references, a world factbook, simple-English Wikipedia. Each comes with a card, a licence and 20 public test questions.

##### One helps a little

With the matching library installed, the small model does a bit better on that library's own test questions.

*Badge:* 180 library test questions (written from the libraries' own text; practice) · Claude Opus · +0.042.

##### Many crowd each other out

Install all of them at once and a big general library takes the few reading slots that the small, right library needed. Quality goes down.

##### Get the right paragraph in

The biggest headroom was simple to state: get the one paragraph that holds the fact into the prompt. A fix that also pulls in the neighbouring paragraphs of the article it found nearly tripled how often that happens, and gave the pack line's only real improvement. It helps on library questions, not on the bounty-style ones.

**In one sentence card:** "Pick the one library you need; more is not better." (The libraries come back in chapters 13 and 14, with a sharper question: does the right page actually reach the model?)

*Facts: [F-1028] [F-1030] [F-025] [F-026] [F-027] [F-028] [F-095]*

Whole chapter: https://r4topunk.github.io/boar-research/research/packs.md

## 10 · Measuring the measurer {#measurer}

##### Claude graded Claude

One AI family wrote the test questions, wrote the reference answers and did the grading. That is a known risk: a judge may prefer answers that sound like itself.

##### A judge from another company

So we re-graded the same answers with a judge from another AI company, using the same rules. It scored everything about 0.10 higher. It kept the same order of who is better. And it still almost never preferred our answer over the frontier one.

*Badge:* V-para and v0.2 · cross-family judge (an OpenAI model) · graded after the fact, not planned in advance.

##### We keep the stricter one

Under the other judge, the big model with thinking crosses 0.50 on the honest scale. We do not headline that. Our rule, written before we had the number, says that when two judges disagree, the lower one is the headline.

##### Luck of the draw

Re-grading identical answers barely changes anything. Re-generating answers with a different random seed changes the score by about 0.02, sometimes 0.04. That is why important numbers use two runs.

**In one sentence card:** "A different judge changes the level, not the ranking, and not the wins."

*Facts: [F-017] [F-018] [F-490] [F-1208] [F-232] [D-122] [F-019] [F-020]*

Whole chapter: https://r4topunk.github.io/boar-research/research/measurer.md

## 11 · A smaller engine for 8 GB phones {#small-engine}

##### The ordinary phone said no

On a common 8 GB phone the model we had used all along needed half a minute or more per answer, and once the phone simply shut it down for lack of memory. A smaller model, with 1.7 billion parameters, answered in a quarter of a minute or less.

*Badge:* Pixel 8a · our measurement app (not the submitted app) · 9 public practice questions · timing only.

##### Faster, and it reads worse

On 20 October the author made the small model the main engine for 8 GB phones. Not because it is better: on 51 practice questions the bigger model stays clearly ahead. Because a phone that answers in seconds, without crashing, is a phone people can use.

*Badge:* v0.1 practice · Claude Opus judge · 51 questions · 1 run per model · 4B ahead by 0.109 (old scale).

##### Nothing closed the gap

Over two days dozens of tricks were tried on the small model: other small models, new prompts, different ways of picking words, confidence checks. None made it read as well as the bigger one at the same speed on the phone.

##### No source, no answer (by default)

The product rule changed too: when the phone's libraries hold nothing on the question, the app says so instead of guessing, and a button shows the model's unsourced guess under a warning. We counted what that button reveals: more wrong answers than right ones, so it sits behind a second tap and never appears for health questions.

*AI-reviewed, not clinically reviewed. Nothing here is medical advice.*

**In one sentence card:** "For an 8 GB phone, speed and memory picked the small model; it reads worse, and we say so."

*Facts: [F-1418] [F-1386] [F-2077] [F-2072] [F-2076] [F-1933] [D-187] [D-149] [F-2084] [F-1633]*

Whole chapter: https://r4topunk.github.io/boar-research/research/small-engine.md

## 12 · A second ruler (bench v0.4) {#new-ruler}

##### Our first exam graded the wrong thing

The first ruler compared our desktop engine with answers written by one AI family, on questions written by that family, graded by that family. The bounty asks about an app on a phone. So we wrote a second ruler.

##### 75 new questions, sealed before anyone answered

75 new questions, written half by Claude and half by an OpenAI model, fact-checked by both, and frozen on 20 October before any system had seen them. It is not written outside the Claude family; we say so.

*Badge:* bench v0.4 · 75 questions (71 scored + 4 anchors) · frozen 2026-10-20.

##### A blank answer now scores zero

On the old scale a polite refusal still earned a few points. The new ruler first asks "did this even try to answer?"; if not, it scores zero. Then both AI families grade it, and the lower grade counts.

##### Graded, then published

By the evening of 24 October both AI families had written their answer keys, and the submitted app's engine had sat the exam on a desktop copy of the phone app, graded by both families. The grade was published as history. A test on the phone itself ran on 25 October and is the headline. On 27 October the questions, both answer keys and the drafts were published too, so anyone can check them against the fingerprints recorded before the exam.

**In one sentence card:** "A fairer exam was written and sealed; the submitted app sat it on a phone and scored below the bar, and the exam itself is now public (as of 28 October 2026)."

*Facts: [D-131] [F-2070] [F-1416] [F-2081] [F-1529] [G-u-total] [F-2110] [F-2212] [F-2214]*

Whole chapter: https://r4topunk.github.io/boar-research/research/new-ruler.md

## 13 · Delivery, not coverage {#delivery}

##### Big gains on the library's own questions

On test questions written from a library's own pages, installing that library makes a big difference. On real practice questions, the same library made no measurable difference.

*Badge:* practice data · Claude Haiku judge · old scale · 27 vs 10 questions.

##### How you ask decides what it finds

Ask a yes/no question and the right page is found 83 % of the time; ask a bare follow-up like "and how long does it take?" and it is found 8 % of the time.

*Badge:* 48 facts × 9 phrasings · practice questions written by agents · search replay, no judge.

##### The book is on the shelf

Of 50 facts the app failed to bring to the model, 44 were already in a library on the phone. The problem was not missing knowledge; it was fetching it.

##### Better fetching, one fix withdrawn

Search fixes doubled how often the right passage arrived (21 → 42 of 92 facts). One more fix did better still, but it let unsafe health answers through on test prompts, so we withdrew it. Answers did not measurably improve.

*AI-reviewed, not clinically reviewed.*

**In one sentence card:** "The phone usually has the book; the hard part is opening it at the right page."

*Facts: [F-2080] [F-2092] [F-2100] [F-2095] [F-2097] [F-2025]*

Whole chapter: https://r4topunk.github.io/boar-research/research/delivery.md

## 14 · Closing the research: what a small model needs {#closure}

##### Research closed, a sentence tested

On 23 October the author closed the research and wrote down what he expected: "the app is right whenever the answer is in one of its libraries". Then we tested that sentence.

##### Right two times in three, when the page arrives

On each library's own questions, the small model was right 48 % of the time with the library installed and 26 % without. When search delivered the right article, it was right 65 % of the time, but search delivered it only about half the time. No library reached the 75 % mark we had fixed in advance.

*Badge:* 180 questions written from 9 libraries · practice · Claude Haiku answer labels (not the old ratio) · 1 run · desktop.

##### What we learned, and what we built

The tests support that first sentence only in a narrower form: right about two times in three when the right page reaches the model. On real questions, the libraries did not help in a measurable way. What the author takes from it, and states as the thesis (25 October 2026): small models need outside knowledge, so the app is a harness built around what a small model can really do: a safe text instead of a guess on health, sums done by code, a search that brings the right page, one short answer style, a line asking you to check the source, and a fixed refusal text where it should not guess. The numbers above are its evidence and its limits; they do not make the app half as good as the frontier.

*Badge:* the author's statement, not a measurement.

##### Short answers win

Longer answer styles were right just as often as the short one, but shown wrong without a warning about twice as often. The short style stayed.

*Badge:* 60 practice questions · Claude Haiku labels · 1 run.

**In one sentence card:** "A small model needs a library: right about two times in three when the page arrives; the page arrives about half the time."

*Facts: [F-1653] [F-1690] [F-1704] [F-1705] [F-1706] [F-1707] [F-2236] [D-215] [G-conditional-thesis] [F-2080] [F-1727] [F-1728]*

Whole chapter: https://r4topunk.github.io/boar-research/research/closure.md

## 15 · One simple app: LabRat {#submission}

##### Which app is the entry?

For most of the project the entry was going to be the app maintainer's own app. On 24 October the author decided instead on a simple app of his own, BoarLite. On 25 October, at the app maintainer's request, it got its own name: LabRat, whose assistant is called Rat.

##### One way to use it

One chat, one short answer style, sources shown, every library inside one download, and no permission to touch the internet. No deep mode, no long mode. Under every answer, one short line: "May contain errors; check the source."

##### A safe text instead of a guess

Ask the app how much of a medicine to give a child and it does not guess: unless it has found a trusted health source, it shows a fixed safe text with the emergency number. On 65 test questions written to probe exactly this, it shows that text on 41, including every question where the small model had made up a dose. The price: some health questions whose only source is a Wikipedia article also get the safe text instead of an answer. That limitation ships; fixing it is planned for after the submission.

*Badge:* 65 safety test questions · practice data · counted by code, no AI grader · AI-reviewed, not clinically reviewed.

##### A better search, and the rule it broke

Porting the research engine's better search into the app got the right passage to the model more often (40 key facts instead of 26). But on the health test questions it also let a few more numbers into answers that no shown source backed up (6 instead of 4), even with the new search switched off for health questions. The rule written before the test said that is a fail. The author had said in advance he would accept a small health cost if the rest got better, and it did; so it shipped. We show both.

##### On a real phone, in airplane mode

On a Pixel 8a with airplane mode on, the app unpacks its 3 GB library in 14 seconds, sends and receives 0 bytes, and gives its first answer about 12 seconds after you ask.

*Badge:* one phone · hand-checked · Pixel 8a.

##### Less app, on purpose

In one night the author took things out: the long-chat summary (on the phone the small model only used the last three exchanges anyway), the PIN lock, Portuguese (the bounty is in English), and every screen and setting the closed app could not reach. The licences now ship inside the app.

##### A new name, and one new line

Renaming the app also changed one line of the instructions the model reads: it now introduces itself as Rat. That line came after the app's engine was graded on the new exam on a desktop copy (0 wins in 71, below the bar), so that grade belongs to the engine before the rename and is kept as history. The phone test running now measures LabRat as it ships, and its grade is the headline.

##### Where to get it

The download is too big for GitHub's file limit (3 GB), so it is hosted on Hugging Face with an install page. One open risk: Android's new developer checks may add a warning and a wait for apps installed from a browser; a test on an ordinary certified phone is still to be done.

**In one sentence card:** "The entry is a deliberately simple app, LabRat, that runs offline on a phone; as of 25 October 2026 its desktop dry run is below the bar and its final test on the phone, the one that counts, is below the bar too."

*Facts: [D-152] [D-183] [D-211] [F-2224] [D-181] [F-1703] [F-2189] [G-fixed-line] [F-2210] [F-2192] [F-2193] [F-2206] [F-2207] [F-2209] [G-grounded-dose-rule] [G-on-no-health] [F-2198] [F-2201] [F-2220] [F-2221] [D-206] [F-2222] [D-207] [D-208] [D-209] [D-210] [F-2225] [F-2223] [F-2230] [D-214] [F-2231]*

Whole chapter: https://r4topunk.github.io/boar-research/research/submission.md

## 16 · Where it stands (live) {#honest-number}

##### Not shown, as of 25 October

As of 25 October 2026, the research is closed and the bar has not been shown to be reached. The number that will count is the new exam measured on the phone, running now. The same exam on a desktop copy of the app's earlier engine won none of 71 head-to-heads and stayed below the bar. On the earlier sealed bounty-style questions the frozen 4B build delivered about a quarter of the frontier answer's value above nothing (0.261) and won none of 51.

*Badge:* new exam · desktop copy · 2 judge families · 71 · 1 run (history) | V-para · sealed at the time · Claude Opus · 51 · 2 runs · old scale (history).

##### Three numbers that are not the same kind

You will see three kinds of number on this site: the old ratio against the frontier answer, answer labels from the closing tests ("right", "wrong without a warning"), and the new exam's score (on the phone: running; on a desktop copy: below the bar). We never put them on one scale.

##### Our claim, in our words

The prepared sentence: "BOAR is not shown to be half as good as frontier AI with web." It was written for the research engine; it will be revised for LabRat (formerly BoarLite) and posted with a link to this article, and the change log will say so.

[sentence withheld in this file; see https://r4topunk.github.io/boar-research/data/ or the chapter record]

*Facts: [F-2215] [F-001] [F-1245]*

Whole chapter: https://r4topunk.github.io/boar-research/research/honest-number.md

## 17 · Open fronts and hand-off {#handoff}

##### Everything is public

The exams, the judge and the research record are on GitHub; the run traces, the app and the libraries are on Hugging Face. Since 27 October the sealed exams are public too, so anyone can run their own assistant against the same answer keys and check the results.

##### What is still open

Posting the revised claim with a link to this article. The final build is on Hugging Face and the final test of the app on the phone landed on 25 October: 0 wins in 71, below the bar. The reshaped factbook library stays unpublished. Each card says what changes if it works and what changes if it doesn't.

##### What we stopped testing, and why

The big model on a phone (dropped when the author ruled out a deep mode), streaming it from storage on Android (built, never measured), and a sealed exam written entirely outside the Claude family (never written).

**In one sentence card:** "The research is closed and the app is hosted; what remains is posting the claim."

*Facts: [F-1316] [F-1532] [F-2118]*

Whole chapter: https://r4topunk.github.io/boar-research/research/handoff.md

## 18 · Reproduce it (appendix) {#reproduce}

Yes, almost all of it. The benchmark questions, reference answers, judge prompt and scoring code are public, and you can run them on your own app with a few commands. Since 27 October that includes the sealed question sets and the new exam, with the run traces behind every number. What you cannot rerun exactly: the judge outputs (the judge is a closed model, so reruns agree closely but not bit for bit). Still private: personal correspondence, the app maintainer's data, spend records and the git history.

*Facts: [D-195]*

Whole chapter: https://r4topunk.github.io/boar-research/research/reproduce.md

---

AI-reviewed, not clinically reviewed. Nothing here is medical advice.
