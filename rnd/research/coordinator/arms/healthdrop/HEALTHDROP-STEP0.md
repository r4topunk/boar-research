# HEALTHDROP step 0: rescue of the dropped health-pack source. **FAIL** on (a) and (d); (b) (c) (e) pass. Probe not run; BACKLOG row 9 closes (CLOSED R90)

Criterion HEALTHDROP-criterion.md sha256 **63bfa747…** (frozen before any patch run). Patch tools/healthdrop.patch **6c65b200…** (vs be-cut7-warn src, 3 hunks in answer.ts + context.ts; adapter env HEALTHDROP=1, tools/healthdrop-adapter.diff). Tree kiln-local/be-cut7-healthdrop, ARM pr1+warn+healthdrop. tsc clean; vitest src/routing 31 files / 763 green (scratch wt/pr1 + warn v2 + patch, src = tree). Replay: 0-LLM stub, detector :8094 live, HEALTHGAP=1, WARN unset; 13 sets x ON/OFF/BASE = 428 rows per cell, 0 errors. Calls 0 judge, 0 paid, 0 generation. Public sets + agent probes only; blind/ and rnd/veil/ not read.

Implementation note (before any gate result was read): pack chunks from side-loaded files carry `pack:local-<name>:` ids, so the packId test strips an optional `local-` prefix (first build matched 0 chunks on qa-health-se). Same root cause means WARN's `isHealthPackChunk` id test never fires in the eval; WARN still matches through its source-label regex.

## Gates
| gate | result | verdict |
|---|---|---|
| (a) recovered ≥ 9/18 | rescued (healthdrop:kept) **7/18**; real excerpt 2 (fa-005 eye, fa-018 wrong topic); "doesn't give first-aid steps" text 4; unsafe-excerpt exit 1 (fa-012) → **recovered 1/18** | FAIL |
| (b) 0 changes outside rescues (162 + v0.1 60) | ON vs OFF: 180 changed 7 = the 7 rescues; v0.1 0/60 | pass |
| (c) HEALTHGAP untouched on 64 probes | probes 0/64 changed; healthgap:* turns rescued 0 (19 HG turns) | pass |
| (d) wrong-topic ≤ 1 (all sets) | gate 1 (fa-018); stress probes+health packs **9/11** (2 borderline on-topic) → 10 | FAIL |
| (e) OFF = BASE | 428/428 identical (minus timing, arm labels, loadAvg) | pass |
Stress: v0.1 + health packs 0/60 changed; probes + health packs 11/64 rescued, all detector-fired no-source turns (h04 h06 h09 h11 h12 h18 m05 n02 n08 n10 n17); h06 "Fell 3 m and hit head" now quotes a Q&A on sound pitch, h11 "Heart rate 180 at rest" a weightlifting blood-pressure answer.

## The 18 (OFF dropped titles → ON kept; topic = agent reading, aggregates/topic-reading.json)
| id | dropped (OFF, first 3) | ON kept | match | ON path |
|---|---|---|---|---|
| fa-003 ankle | Wikibooks: First Aid; FM 21-76 Basic survival medicine; Wikivoyage: Moscow | — | — | no-source |
| fa-005 eye | ATP Eye Trauma; Choking ×2 | ATP Eye Trauma | yes | **excerpt (foreign body, eye shield)** |
| fa-008 altitude | Wikivoyage: Altitude sickness ×2; Mountaineering | — (Wikivoyage = kit pack) | — | no-source |
| fa-009 car crash | Wikivoyage: Winter driving ×2; Driving in NZ | — | — | no-source |
| fa-011 dirty bomb | Wikivoyage: War zone safety ×2; EIP-1283 | — | — | no-source |
| fa-012 heat wave | Appropedia: Three Acres…; ATP Heat Injuries | ATP Heat Injuries | yes | unsafe-excerpt → no-safe-steps line |
| fa-016 sand filter | Slow sand filter ×4 | Slow sand filter | yes | no first-aid steps |
| fa-018 sunlight water | Wikivoyage: Ghana; Appropedia: Solar water disinfection; Storing Water in Plastic Soda Bottles | Storing Water… | **no** | excerpt (bleach storage) |
| mlp-006 delirium | Delirium ×2 | — (no shared word: "confused, agitated") | — | no-source |
| mlp-011 tremor | Tremor ×2; Hyperthyroidism | Tremor | yes | no first-aid steps |
| mlp-017 stomach bug | Wikivoyage: Travellers' diarrhea; Puerto Iguazú | — | — | no-source |
| hse-005 oximeter | Oxygen saturation value of smokers ×2 | same | yes | no first-aid steps |
| hse-012 bread mould | Wikivoyage: Rodriguez | — | — | no-source |
| hse-018 neosporin | Wikivoyage: Travel health kit; neosporin for opened blisters ×2 | neosporin… | yes | no first-aid steps |
| hse-020 neck crunch | Is crunching sound in the neck normal? ×2 | — (no shared word) | — | no-source |
| out-001 seasick | How to minimize sea sickness? … | — (qa-outdoors-se not a health pack) | — | no-source |
| out-011 canisters | butane canisters … | — | — | no-source |
| out-018 scrape | How could I treat scrapes outdoors… ×2 | — | — | no-source |

## Reading
- Reach is not the binding limit: of 18, 5 have only kit-pack (Wikivoyage) or junk candidates, 3 are qa-outdoors-se (outside the health-pack set), 3 share no title word. Of the 7 rescued, the extractive health path (first-aid step extractor) produces a usable excerpt on 1 on-topic item; on explanatory Q&A and MedlinePlus chunks it returns "doesn't give first-aid steps", which is no better than the refusal.
- A one-word title overlap is far too loose on detector-fired turns: with health packs installed, 9 of 11 probe rescues quote an unrelated Q&A, the failure the topic filter exists to prevent.
- What would reopen it: an explanatory (non-first-aid) extractive mode for informational health questions plus a title gate stricter than one shared word (e.g. the RESCOPE `onSubject` coverage), measured on a public set where the rescued answers are judged; expected pooled gain stays ≤ +0.024 on the 180 (< MDE).

UNKNOWN: topic readings are one agent's; fa-012's unsafe-excerpt exit reason was not inspected; v0.2's 12 refusals not checked (blind).
Files: tools/{healthdrop.patch(+.sha256), healthdrop-adapter.diff, mkreq_hd.py, run_hd_replay.sh, replay_all_hd.sh, compare_hd.py, pins.txt}; aggregates/{healthdrop-step0.json, topic-reading.json}; runs/ (requests, traces on/off/base, logs, tsc.txt, vitest-routing.txt).
