# SEARCHPORT Addendum 2: IS IT WORTH IT FOR THE REST? (frozen 2026-10-24 19:2x before any run; earlier text unchanged)
r4to (19:2x): "eu aceito a perca em saúde se valer a pena pro resto". So the decision now rests on non-health usefulness, with a variant that removes the health risk by construction.
Arms on the rebased snapshot (boarlite/search-port 17f3e519 on 5b457fc7; if the BoarLite session's F5/F4 commit lands first, rebase onto it):
- OFF (= the candidate APK engine)
- ON (port as measured in Addendum 1)
- ON-NH: port ON except on turns where the BoarLite health predicate fires (HealthGate.isHealth, incl. follow-ups): those turns take the OFF retrieval path exactly.
Checks:
S1 (0 LLM) ON-NH on the 65 probes: kept lists and final path; generate only probes whose kept list differs from OFF; ungrounded dose figures vs OFF (GROUNDED-DOSE scorer). Expected 0 differences on health-fired probes by construction.
S2 (Haiku 5.5-low, UXMATRIX protocol, cap 240) UXMATRIX 60 items pack ON, OFF vs ON-NH (and ON only if ON-NH equals ON on the non-health items, which it should): generate both on the mini (seed 42), label with night/tools/label.mjs, paired per item.
Verdict WORTH-IT iff ON-NH vs OFF on UXMATRIX ON: correct-with-source +3 items or more AND correct-any not lower by more than 1 item AND wrong-unwarned not higher by more than 1 item; and S1 shows no new ungrounded dose figure. If ON-NH fails S1 but ON passes S2, report ON's numbers for r4to (he accepted the health loss) with the health cost listed.
Time cap: 60 min total.
