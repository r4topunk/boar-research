import sys
# Applies the 20 edits (E1-E17, E19-E21) of CLAIM-REVIEW-v4.1.md to CLAIM-DRAFT.md. Usage: python3 this.py [out_path]
src = "<workspace>/rnd/research/coordinator/CLAIM-DRAFT.md"
t = open(src, encoding="utf-8").read()
E = []
def e(i, old, new): E.append((i, old, new))

e(1, "The app's own window (last 6 messages, plus a summary from turn 8) was not run.",
  "Neither the React Native app's window (6 messages, summary from turn 8; turns 5–7 drop the oldest) nor the submitted app's was run.")
e(2, 'Ten 5-turn sessions (three to 15 turns) on desktop',
  'Ten 5-turn sessions (three extended to 15) on desktop')
e(3, 'written by a Claude Opus agent, held out for the 4B claim runs',
  'written by a Claude Opus agent (plus 7 venue questions, 0/7), held out for the 4B claim runs')
e(4, '(FACTS citation check, emergency routing, grounding and health)',
  '(emergency routing, grounding and health, citation support)')
e(5, 'Win rate: 0 on every row and seed. Deep-tier rows:',
  "Win rate: 0 on every row and seed. V-para's 7 venue questions (outside the 51): 0/7 in the claim run (no device location passed); 7/7 only with device location and the user's area tile (§4 row 15; plumbing check, not a quality score). Deep-tier rows:")
e(6, 'raw 0.561 (0.507–0.617) vs 0.558 and 0.560 |',
  'raw 0.561 (0.507–0.617) vs 0.558 and 0.560 (floor-adjusted not computed) |')
e(7, 'They are not device results. [S1] [S18] [S19]',
  "They are not device results, and they are the TypeScript engine's numbers, not the submitted native app's (its score is pending [S55]). [S1] [S18] [S19]")
e(8, '- **Not yet done:** public repos (snapshots being prepared: https://github.com/r4topunk/boar-bench, https://github.com/r4topunk/boar-research), Android UI integration (PR-1 prepared with a wiring commit not yet built or run on a device [S53]), the deep tier on any phone, public demo post.',
  '- **Not yet done:** the submitted native app\'s score on our benchmark (traces requested [S55]), Android UI integration (PR #85 open, CI green on typecheck and tests; its wiring not yet built for Android or run on a device [S53] [S56]), the deep tier on any phone, public demo post. Done 2026-10-15: public benchmark and research repos (https://github.com/r4topunk/boar-bench, https://github.com/r4topunk/boar-research; QUEUE.md row "PUBLIC REPOS LIVE (10:07)").')
e(9, '| 9 | Public GitHub repo with the functional version | **Not yet** | The code is in private repos; no public code repository exists.',
  '| 9 | Public GitHub repo with the functional version | **Partly met (code public; release not checked by us)** | The submitted native app\'s code is on a public branch (`fullnative-dev`) of the BOAR app repository, not checked by us [S55]; the measured engine is public as PR #85 [S56]; the benchmark and research record are public (https://github.com/r4topunk/boar-bench, https://github.com/r4topunk/boar-research; QUEUE.md row "PUBLIC REPOS LIVE (10:07)"). A public release of the submitted APKs is the maintainer\'s step, not checked by us.')
e(10, '| Android UI wired to the measured engine path | Makes the measured ratio apply to the app a user installs. PR-1 carries the wiring commit (tests only; no Android build or device run yet) [S53]. |',
  "| Android UI wired to the measured engine path | Makes the measured ratio apply to the React Native app's chat; it does not reach the submitted native app, a separate port whose score is pending [S55]. PR #85 carries the wiring (CI green on typecheck and tests; no Android build or device run yet) [S53] [S56]. |")
e(11, 'but no device run of that commit yet, and no UI for',
  "but no Android build or device run of that commit yet (the PR's CI runs typecheck, tests and CodeQL), and no UI for")
e(12, 'PR #85 open, CI green (reference implementation; no device run of the wiring yet) [S53] [S56].',
  'PR #85 open, CI green on typecheck and tests (reference implementation; no Android build or device run of the wiring yet) [S53] [S56].')
e(13, "- [ ] Public repo, install instructions, reproduction steps, model and dataset documentation (rows 9–11). Two curated public repos are being prepared (benchmark: https://github.com/r4topunk/boar-bench; research record: https://github.com/r4topunk/boar-research); publishing needs the owner's explicit approval.",
  '- [ ] Install instructions, reproduction steps, model and dataset documentation (rows 9–11). Done 2026-10-15: two curated public repos (benchmark: https://github.com/r4topunk/boar-bench; research record: https://github.com/r4topunk/boar-research).')
e(14, 'and will publish the result as "the submitted app".',
  'and will publish the result.')
e(15, "The official submission is the maintainer's",
  "The submission is the maintainer's")
e(16, "These are the TypeScript engine's numbers; the submitted app's score is pending.",
  "These are the TypeScript engine's numbers; the submitted app is unscored.")
e(17, '(12 GB class: 10.7 GiB usable RAM, Android 16)',
  '(12 GB class, 10.7 GiB usable, Android 16)')
e(19, 'thermal status 0 over the 29-minute run.',
  'thermal status 0 throughout.')
e(20, '(DRAFT v4.1; independently reviewed through v4.0.1, see CLAIM-REVIEW-v4.0.md and the changelogs; v4.1 awaiting review; not published)',
  '(DRAFT v4.1; independently reviewed through v4.1, see CLAIM-REVIEW-v4.1.md and the changelogs; not published)')
e(21, 'Desktop median rose to about 22 s at turns 14–15',
  'Desktop median rose to 22 s at turns 14–15')

out = t
for i, o, n in E:
    c = out.count(o)
    if c != 1:
        print("FAIL E%d count=%d: %s" % (i, c, o[:80])); sys.exit(1)
    out = out.replace(o, n)
open(sys.argv[1] if len(sys.argv) > 1 else src, "w", encoding="utf-8").write(out)
print("edits", len(E), "ok")
