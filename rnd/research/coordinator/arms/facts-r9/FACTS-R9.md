# FACTS-R9: travel fields in the facts table (2026-10-19)

## TL;DR
- New country fields from Wikidata (CC0, fetched 2026-10-19): driving side (P1622) on 197/197, international calling code (P474) on 196/197, mains frequency (P2144 qualifier of P2884) on 191. Plug (P2853) and voltage (P2884) were already in the table since r6; r9 cleans both. Time zone not shipped (not clean, see Deviations); official languages unchanged (P37 since r6).
- Engine: two new templates (driving, calling) + wider electricity wording. "What plug do I need in Japan", "do they drive on the left in X", "voltage in X", "country code for X" all fire (probes-r9.out.txt).
- Audit (criterion a4fd8b92, frozen and committed before any comparison, rnd 55947e92): final r9 asset 0 TABLE-WRONG on driving side and calling code, 0 on plug and voltage. The first r9 build had 2 wrong voltage rows (1.0 %) and 3 wrong plug rows (1.6 %), both under the 2 % bar; all were fixed anyway.
- FP check: 675 public bench questions, the new templates fire 0 times; 1 answer changes (trv-002, the Brazil plug question, gains "60 Hz").
- Tests: engine suite 124 files / 1,590 tests green (r8 base 1,586, +4 r9 tests), same with HEALTHGAP=1; tsc clean; the new test block fails 3/4 on the r8 tree. Patch applies on wt/pr1 b546706c.

## Artefacts
| What | Where | sha256 |
|---|---|---|
| Asset r9 | arms/facts/data/facts.v1.r9.json = handoff/facts-r9-2026-10-20/facts.v1.json (4,233 entities, 784,561 bytes, rebuilt byte-identical twice) | 0c167a8f… |
| Builder r9 | arms/facts/tools/build_asset.py (r8 kept as build_asset.r8.py; it rebuilds r8 byte-identical, 08079bc0) | |
| Fetcher | arms/facts/tools/fetch_wikidata_r9.py -> data/raw/{drive,call,volt,plug,tz}_r9.{rq,json} | |
| Engine patch | facts-r9.patch (commit 4d8428c9 on a scratch worktree wt/facts-r9 of wt/pr1 b546706c; wt/pr1 itself untouched) | d121e03c… |
| Audit | tools/audit_r9.py, tools/wpcheck_r9.py, tools/plugrule_r9.py, tools/extract_wp_r9.py; audit-r9{,-prefix}.json, wpcheck-r9{,-prefix}.json | |
| FP check | tools/fpcheck.mts -> fpcheck-r9.jsonl, fpcheck-r9.out.txt | |
| Handoff | handoff/facts-r9-2026-10-20/ (facts.v1.json, facts-r9.patch, CHANGES.md, LICENSE-DATA.txt, SHA256SUMS) | |

Property ids verified with wbgetentities before use: P1622 driving side, P474 telephone country code, P2884 mains voltage, P2853 electrical plug type, P421 located in time zone, P37 official language. P2885 does not exist (r8 read it for hz, so r8 never had a frequency); the frequency is qualifier P2144 on P2884.

## Builder rules (r9)
- drive: current statements (no P582), preferred rank first, exactly one value left/right. Sweden, Iceland, Myanmar, Argentina, Samoa resolve to the current side through the end-time rule.
- call: current, preferred first; NANP "+1876" -> "+1 876"; parts from P518 (Kingdom of Denmark: Denmark +45, Faroe Islands +298, Greenland +299); Vatican City dropped (+379 unused); San Marino +390549 and Turkey +36 dropped (old).
- volt/hz: from volt_r9 (fresh), ended rows dropped, preferred first, 100-240 V only; hz in {50, 60} only, and only when every frequency of the kept rows is valid (Liberia, North Korea 55 Hz -> none).
- Audit fixes: VOLT_DROP Indonesia 127, Libya 127; plug umbrella item "AC power plugs and sockets: British and related types" dropped; Saint Vincent and the Grenadines no plug; PLUG_DROP_PAIR Solomon Islands G, Oman C, UAE C.
- r8 -> r9 field changes: drive 197, call 196, hz 191, plug 38, volt 7; nothing else changes.

## Audit (criterion FACTS-R9-criterion.md, a4fd8b92)
Sources: S1 Factbook pack (wave2, CC0, 2026-09-11), S2 Wikivoyage pack (CC BY-SA); Wikipedia (enwiki top-100k pack: "Mains electricity by country", "Left- and right-hand traffic") for adjudication only. S2 matched 193/197 countries (missing: Ivory Coast, People's Republic of China, Palestine, Vatican City).

Part A (full scan, final asset): rows drive 197, call 196, volt 193, plug 192. Flags drive 137, call 39, volt 151, plug 176. Almost all are NO-REF in S2 (the country article has no electricity/driving sentence the regex finds): drive 137/137, call 31/39, volt 147/151, plug 174/176. Every flagged row was then compared with the Wikipedia tables (wpcheck-r9.json) and adjudicated:
- drive: Wikipedia agrees on 195/197; the 2 disagreements are table-parse artefacts (United Kingdom row read "Yes", Chile "Unknown"; both table values right). TABLE-WRONG 0.
- call: S1/S2 agree on 157/196. 8 contradictions are reference artefacts, table right: S1 is the US embassy's phone, so Libya [216] (embassy in Tunis), Somalia [254] (Nairobi), Maldives [94] (Colombo), Haiti [011] and Kuwait [00] (exit prefixes); S2 picked up other numbers (Guinea-Bissau 33, Kiribati 692, Iran 00). 31 NO-REF rows adjudicated by hand against the ITU E.164 assignments: all right (Ivory Coast +225, Cape Verde +238, Eswatini +268, China +86, Palestine +970, Monaco +377, San Marino +378, Belize +501, US +1, Liechtenstein +423, Tonga +676, Nauru +674, Venezuela +58, the NANP islands, Dominican Republic +1 809/829/849, Egypt +20, Iraq +964, Yemen +967, Syria +963, Afghanistan +93, Bhutan +975, Brunei +673, Mexico +52, Burkina Faso +226, Comoros +269). TABLE-WRONG 0.
- volt+hz: Wikipedia agrees on 191/193 (all within 10 V, frequency included); 1 no Wikipedia row (Micronesia 120 V 60 Hz, right); Afghanistan 240 V vs Wikipedia 220 V: DEFENSIBLE (same 220-240 V class for any device; S2 also mentions 220). S2 contradictions (Tuvalu 220 vs 240, Kuwait 240 vs 220, Vietnam 200 regex artefact, Afghanistan) all DEFENSIBLE or right. hz flags 0. First build: Indonesia and Libya listed an obsolete 127 V next to 230 V ("differs by region" would mislead) = 2 TABLE-WRONG / 193 = 1.0 %; fixed, final 0.
- plug: hand rule fixed before re-running (tools/plugrule_r9.py; same rule on both builds): TABLE-WRONG when no reference letter (Wikipedia + S2) is in the table, or at least half of the listed types are in no reference. First build 3/192 (1.6 %: Solomon Islands G+I vs I; Saint Vincent and the Grenadines A,C,E,G,I,K vs A,B,G; Oman C+G vs G); after the umbrella item was dropped, the UAE (C+G vs G) crossed the half line, so the fix list is Solomon Islands, Oman, UAE, Saint Vincent. Final 0/191. The 18 remaining rows with one extra minor type (e.g. Thailand F, China C, Israel D/M) are DEFENSIBLE: the main types are listed.
- Part B sample (48 rows, 12 per field, random.Random(919)): drive 12/12 agree with Wikipedia; call 9 agree with S1/S2, 3 NO-REF right by hand (Eswatini, Monaco, Syria; South Sudan S2 249 = Sudan, table +211 right); volt 11 agree, 1 DEFENSIBLE (Afghanistan); plug 11 agree, 1 no Wikipedia row (Micronesia A/B, right). TABLE-WRONG 0.

Verdict per criterion: PASS (drive 0, call 0, volt+hz 0/193 final (2/193 = 1.0 % first build), plug 0/191 final (3/192 = 1.6 % first build)).

## FP check (criterion part 3)
675 unique questions (bench v0.1 public 60, rivalset, selftest x12, slices chainwhen/longsession/mathroute/packread/chat-fu/citation-pt; no blind or held-out data): factsAnswer fires 11 times on r8 and 11 on r9; driving/calling fire 0 times; 1 changed answer, trv-002 "What plug type and voltage does Brazil use?" (an electricity question; adds "60 Hz" and the note wording). PASS.

## Engine tests (wt/facts-r9 = wt/pr1 b546706c + facts-r9.patch)
- New describe block "FACTS asset r9" (4 tests, 27 expectations): plug/voltage travel wording with Hz, Indonesia 230 V only, no British umbrella; driving Yes/No and neutral; calling incl. NANP, Denmark parts, Turkey +90, Vatican null; 12 stay-out questions (licence, permit, safe to drive, ISO/internet/area code, city, time zone).
- vitest: 124 files / 1,590 passed (base 1,586), same with HEALTHGAP=1; tsc --noEmit clean; on the r8 tree the r9 block fails 3 of 4.

## Deviations
- Time zone not added: Wikidata P421 has 630 mixed statements for 197 countries (IANA ids, UTC offsets, named zones, DST zones, overseas parts; only 4 countries have one statement). Conservative option per the brief ("only if clean"); the engine keeps "time zone" on its veto list.
- Official languages: already shipped (P37, r6); no change.
- Plug and voltage already existed (r6); r9 corrects them (ended/three-phase/obsolete voltages, umbrella plug item, 4 plug lists) instead of adding them.
- Calling-code audit has no Wikipedia table in the local pack; 31 NO-REF rows were adjudicated by hand against the ITU assignments (named above), not against an on-disk source.
- Plug TABLE-WRONG needed a concrete rule the criterion left open ("would mislead a traveller"); it was written as a script and applied identically to both builds; under it the first build already passed (1.6 %).
- The engine change also edits the existing electricity answer: the regional note ("Where two values are listed ...") now appears only when two voltages or frequencies are listed (r8 printed it always).
- 0 judge calls, 0 generation, no mini usage (port 8194 unused, 0 GiB mini disk); Wikidata fetched from the MacBook (9 public WDQS/API requests, generic UA). The patch keeps r8's commit author line; nothing pushed, wt/pr1 untouched.
