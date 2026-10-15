# FACTS r4 (2026-10-06 22:43): FAIL on the fresh-precision gate, before the blind set. Set 3 untouched (still blind).
Criterion FACTS-r4-criterion.md sha 23e82776… (addendum 1 fixed the set-2 baseline to 26/40). Code: wt/facts on 45d5d058, the two
frozen rules (safe-lowercase multi-word names; typo-tolerant "the"), +34 −8 in src/rag/facts.ts, NOT committed; kept as
facts-r4-WIP.vs-r3.patch (sha 0d8adc47…). wt/facts restored to 45d5d058 (= r3). Scorer v2 (transliteration fold) kept in tools/.

| measure | r3 | r4 | bar |
|---|---|---|---|
| set 1 recall / precision / FP (scorer v2) | 30/40 / 88.2 % / 0/20 | **33/40 = 82.5 %** / 89.2 % / 0/20 | dev |
| set 2 recall / precision / FP (scorer v2) | 26/40 / 100 % / 0/20 | **28/40 = 70.0 %** / 93.3 % / 0/20 | dev, expected 85–90 % |
| fresh lowercase-homonym probes (22, written by the r4 agent) | 5/22 fire | **10/22 wrong fires** (11 incl. "kuala lumpur tower", a real entity) | 0 |
| G1–G5, 13 probes | not run (stop rule) | not run | — |

Wrong fires: pre-existing in r3 (one-word lowercase rule): paris hilton → Paris 48 m, paris las vegas, cuba libre → Cuba area,
london broil → London area, japan times → Japanese. New in r4: mont blanc pen, mount everest base camp, mexico city metro fare,
rio grande valley, berlin wall memorial. Cause: the r3 glue guard only looks at a CAPITALISED neighbour, so a lowercase word
right after a name ("pen", "hilton", "broil") never blocks the fire. Blind set 2's near-misses were capitalised ("Paris Hilton")
and did not expose this; the CF failure class is still open on lowercase typing.
Set-2 recall stays at 70 % because of 4 causes outside the two rules: "whats …" without "?" is not parsed as a question (uae,
philippines); Netherlands and Vietnam have no population row; "victoria" is on the risk list (lake victoria); Rhine and CN Tower
are not in the table. One new wrong value: Mekong 4,350 km vs expect (scorer MISS, not a false fire).
Verdict by the frozen rule: FAIL (gate red), no rescue, no r5 today. Reading: recall rules are easy; the binding constraint is
lowercase precision, which needs a neighbour guard on BOTH sides for ALL names (changes the r3 rule) and a fresh adversarial
lowercase near-miss set. whether to open r5 with that scope is a separate decision (set 3 remains blind for it).
UNKNOWN: r3's own lowercase-homonym rate on a larger adversarial set (5/22 here is dev, agent-written); whether the facts tier is
worth cut 7 if lowercase names must be refused entirely (recall then ≈ 60–65 %, set-2 level).
