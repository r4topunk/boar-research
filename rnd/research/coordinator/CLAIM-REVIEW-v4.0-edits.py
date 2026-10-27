import sys
# Applies the 26 edits (E1-E26) of CLAIM-REVIEW-v4.0.md to CLAIM-DRAFT.md. Usage: python3 this.py [out_path]
src = "<workspace>/rnd/research/coordinator/CLAIM-DRAFT.md"
t = open(src, encoding="utf-8").read()
E = []
def e(i, old, new): E.append((i, old, new))

e(1, 'Cut 7 ran on a POCO X6 Pro (12 GB class: 10.7 GiB usable RAM, Android 16) in airplane mode, without the INTERNET permission: **72/72** answered, 0 crashes. Fast-tier answers (the 4B path) p50 30.7 s, p90 48.4 s.',
  'Cut 7 ran in our measurement app (same engine code) on a POCO X6 Pro (12 GB class: 10.7 GiB usable RAM, Android 16) in airplane mode: **72/72** answered, 0 crashes. Fast-tier answers median 30.7 s, p90 48.4 s.')
e(2, 'On 57 v0.1 development items it matched the desktop: raw 0.529 vs 0.529, paired −0.000 (−0.026…+0.028) (one run, Haiku judge). Earlier, cut 6 on an 8 GB Galaxy A15, same conditions: 73/73 answered, model answers p50 49 s, PSS max 4.41 GiB; phone 0.561 (0.507–0.617) vs desktop 0.558 and 0.560 on the same 57 items (Opus judge).',
  'On 57 v0.1 development items it matched the desktop: floor-adjusted 0.403 vs 0.402, raw 0.529 vs 0.529 (one run; Haiku triage judge, level not comparable with Opus). Earlier, cut 6 on an 8 GB Galaxy A15, same conditions: 73/73, model answers median 49 s; raw 0.561 (0.507–0.617) vs desktop 0.558 and 0.560 on the same 57 items (Opus judge; floor-adjusted not computed).')
e(3, 'three extended to 15 turns; each in-session answer paired with the same question asked standalone. **No quality drop was detected out to turn 15**: in-session/standalone ratio 1.397 (1.187–1.673) on turns 2–5, 1.136 (0.993–1.320) on turns 6–15; on self-contained questions 1.017 (0.950–1.095), parity.',
  'three extended to 15 turns, on desktop with full history; each in-session answer paired with the same question asked standalone. **No quality drop was detected out to turn 15**: in-session/standalone ratio 1.397 (1.187–1.673) on turns 2–5, 1.136 (0.993–1.320) on turns 6–15 (above 1: asked alone, a follow-up lacks context); on self-contained questions in turns 6–15, 1.017 (0.950–1.095), parity.')
e(4, 'The cost is speed: with full history, desktop p50 rose from 11 s at turn 1 to 22 s at turns 14–15 (about 8 s standalone). The app keeps the last 6 messages plus a summary, which bounds the prompt; that policy itself was not run here.',
  'The cost is speed: desktop median rose to about 22 s at turns 14–15 (about 8 s standalone). The app sends only the last 6 messages, plus a summary from turn 8, so turns 5–7 lose the oldest turns; that app policy was not run.')
e(5, 'Ten five-turn sessions (follow-ups that point back, topic switches, deepening),',
  'Ten five-turn sessions (follow-ups, topic switches, deepening),')
e(6, 'Limits: 80 development questions written by a Claude agent, one seed, Haiku judge, and the reference is',
  'Limits: 80 agent-written development questions, one seed, Haiku judge; the reference is')
e(7, "Measured on cut 3 and repeated on cut 6; cut 7's answers on both sets are identical.",
  "Measured on cut 3, re-run on cut 6 (verdicts reused for unchanged answers); cut 7's answers equal cut 6's.")
e(8, '**V-para**, 51 judged bounty-style questions written by a Claude Opus agent, held out for the 4B claim runs (2026-10-05/06), development-style since; **v0.2**, 110 questions by Claude-family agents, held out at the time, since exposed (now development data);',
  '**V-para**, 51 judged bounty-style questions written by a Claude Opus agent (plus 7 venue questions, 0/7 in the claim run), held out for the 4B claim runs (2026-10-05/06), development-style since; **v0.2**, 110 questions by Claude-family agents, held out at the time but stored in plaintext in a private repository before the claim runs; now development data;')
e(9, '**Deep tier: measured on desktop only; needs a 12 GB phone.** Qwen3.6-35B-A3B with a 512-token thinking budget, development data. V-para (two seeds): floor-adjusted **0.436** (0.387–0.486 with seed noise) vs 0.261 for the 4B,',
  '**Deep tier: measured on desktop only, never on a phone.** Qwen3.6-35B-A3B with a 512-token thinking budget, development data, best of many deep variants tried on these sets. Intervals include seed noise. V-para (two seeds): floor-adjusted **0.436** (0.387–0.486) vs 0.261 for the 4B,')
e(10, 'Desktop p50 about 79 s. Never run on any phone; not in the shipped build.',
  'Desktop median 79 s. Not in the shipped build.')
e(11, 'The pre-registered rule is a raw-ratio 95% CI above 0.50 on v0.2; we also apply it to V-para. On both sets only the deep tier with thinking meets it, on development data, on the desktop.',
  "Our own pre-registered rule, not the bounty's, is a raw-ratio 95% CI above 0.50 on v0.2; we also apply it to V-para. On both sets only the deep tier with thinking meets it: development data, desktop only, not shipped.")
e(12, 'Our stricter target, a floor-adjusted CI low end at or above 0.50 on V-para, is met by no configuration (best 0.436).',
  'Our stricter target (floor-adjusted CI low end ≥ 0.50 on V-para) is met by no configuration (best 0.436).')
e(13, 'The win rate is 0 everywhere. BOAR is not shown',
  'The win rate is 0 on both sets. BOAR is not shown')
e(14, 'answers are often right but thin, or miss knowledge the packs do not hold.',
  'answers are often thin or partly wrong, or miss knowledge the packs do not hold.')
e(15, 'Safety evidence is small (0 unsafe-rule hits on 10 danger questions).',
  'Safety evidence is small (0 unsafe-rule hits on 10 danger questions, one of which prompted a fix).')
e(16, 'We report three scales, in this order:',
  'Three scales, in this order:')
e(17, 'App memory (PSS) peaked at 5.88 GB during model load, then stayed at or below 4.23 GB;',
  'App memory peaked at 5.88 GB at model load, then stayed ≤ 4.23 GB;')
e(18, '(retrieval 60/60 identical to the measured build, desktop answers 59/60 byte-identical, 1,378/1,378 tests)',
  '(retrieval 60/60 and desktop answers 59/60 identical to the measured build; 1,378/1,378 tests)')
e(19, 'Not in PR-1: the deep tier; the knowledge-pack retrieval improvements and pack catalogue (a second PR after 2026-10-20); "answer anyway" and "deeper answer" buttons.',
  'Not in PR-1: the deep tier, the knowledge-pack improvements (a second PR after 2026-10-20), and "answer anyway" / "deeper answer" buttons.')
e(20, '(v0.1 questions with reference answers, judge harness, a trace format any app can emit, scorers)',
  '(v0.1 questions and references, judge harness, trace format, scorers)')
e(21, '(reports, frozen criteria, closed experiments, device runs)',
  '(reports, frozen criteria, closed experiments)')
e(22, 'Other teams are welcome to run the judge on their own traces and to contribute held-out questions written outside the Claude family, so every team gets an unexposed set.',
  'Other teams can run the judge on their own traces and contribute held-out questions written outside the Claude family (rules in CONTRIBUTING).')
e(23, 'history pushing a comparison onto the health extractive path, 1); 0 in turns 6–15.',
  'history pushing a comparison onto the health extractive path, 1); none of these two kinds in turns 6–15, where one follow-up resolved "it" to the wrong coin and one answer invented a penalty figure primed by earlier turns.')
e(24, 'device run still pending (needs a 12 GB phone);',
  'device run still pending (the 12 GB-class POCO X6 Pro has run only the 4B build);')
e(25, '(DRAFT v4.0; independently reviewed through v3.9, v4.0 pending review; see the changelogs; not published)',
  '(DRAFT v4.0; independently reviewed through v4.0, see CLAIM-REVIEW-v4.0.md and the changelogs; not published)')
e(26, 'No Google Play Services, Firebase or tracker classes in any of the three measurement APKs (E1).',
  'No Google Play Services, Firebase or tracker classes in any of the three measurement APKs (E1), nor in the cut 7 no-network APK (audit 2026-10-10, QUEUE.md l.897).')

out = t
for i, o, n in E:
    c = out.count(o)
    if c != 1:
        print("FAIL E%d count=%d: %s" % (i, c, o[:80])); sys.exit(1)
    out = out.replace(o, n)
open(sys.argv[1] if len(sys.argv) > 1 else src, "w", encoding="utf-8").write(out)
print("edits", len(E), "ok")
