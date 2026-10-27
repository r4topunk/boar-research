# FACTS-R9 audit addendum criterion (frozen 2026-10-19 before any comparison is run)

Model: arms/factsaudit/FACTSAUDIT-criterion.md (9710b996). Question: are the r9 travel fields of the country table right enough to be stated as deterministic answers? Fields audited: drive (driving side, Wikidata P1622), call (telephone country code, P474), volt (mains voltage, P2884) with hz (its P2144 qualifier), plug (P2853). Time zone (P421) and official languages are not audited here (time zone is not shipped; languages are unchanged since r6). 0 judge calls, 0 generation, public data only.

Table: the r9 asset built by arms/facts/tools/build_asset.py r9 (sha256 recorded in FACTS-R9.md), 197 entities of kind country.

Second sources (on disk, read only):
- S1 CIA World Factbook pack text (shared-data/packs/wave2/boar-factbook.sqlite, CC0, data as of 2026-09-11): the calling code is the bracketed prefix of "Diplomatic representation from the US (telephone): [NN]".
- S2 English Wikivoyage pack text (shared-data/packs/boar-wikivoyage-en.sqlite, CC BY-SA), article titled as the country name or alias: driving side phrases, "NNN V" / "volts", "Type X" plug letters, "+NN" / "country code is NN".
Matching: exact case-insensitive title equal to the table name or one of its aliases; unmatched countries are listed, not scored.

Part A, full scan (script tools/audit_r9.py, all 197 countries): a row is FLAGGED when
- call: S1 code exists and no table code starts with "+" + S1 code (NANP: "+1 268" vs [1]... the S1 bracket "[1]" matches "+1 268"); or no S1 code and S2 has a "+NN" / "country code is NN" that no table code equals.
- drive: S2 states only the opposite side (side phrases: "drive on the left/right", "drives on the left/right", "driving is on the left/right", "left-hand/right-hand traffic", "keep left/right"), or S2 states neither.
- volt: no table voltage (V) appears within +/- 10 V of a voltage number in S2 ("NNN V", "NNN volts", "NNN-volt").
- hz: a table frequency and S2 states only the other of 50/60 Hz.
- plug: no table plug letter appears as "Type X" / "type X" in S2 (British-related types count as D, G and M).
Part B, sample: 48 rows (12 per field drive, call, volt incl. hz, plug), drawn with Python random.Random(919) over the sorted country QIDs having that field; each is adjudicated by reading the S1/S2 snippets.
Adjudication of every flagged and sampled row: TABLE-RIGHT, TABLE-WRONG (the table value would mislead a traveller today), DEFENSIBLE (regional split, reference stale, both defensible), NAMING, NO-REF (no usable second-source text). Wikipedia may be consulted for adjudication only.

Pass rule: 0 TABLE-WRONG rows on drive and call (Part A + Part B); TABLE-WRONG rows / rows with a reference <= 2 % on plug and on volt+hz (each). On a failure: every TABLE-WRONG row gets a builder override or the field is dropped for that country, the audit is re-run, and both results are reported.

FP check: every question of the public sets (bench v0.1 questions.public, rivalset, selftest/*, slices/*; boar-eval/bench, no blind or held-out data) is run through factsAnswer on the r8 tree (wt/pr1 b546706c) and the r9 tree. Pass rule: the r9-only templates (driving, calling) and every r8 -> r9 changed answer fire 0 times on questions that do not ask for plug/socket/voltage/frequency, driving side or calling code; each changed row is listed and classified.
