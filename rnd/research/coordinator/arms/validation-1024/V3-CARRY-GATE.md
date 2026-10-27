# V3-CARRY-GATE (ADDENDUM-3 job 17, 0 LLM, MacBook, 2026-10-23 19:1x): PASS -> job 17 appended

Tree kiln-local/rs-RC-STICKY = APFS clone of rs-RC + arms/retrieve-sweep/patches/R5-STICKY.patch (sha 6b172fd2, applied clean, no fuzz; touches src/rag/packs.ts, src/rag/wikiPack.ts, src/routing/answer.ts; default off). Replays: night/tools/carry_gate.sh (the rcrun.sh rc-mode commands, tree swapped, own replay cache, one at a time, load 1.9-4.5); scorer night/tools/score_carry_gate.py (U5 rules imported verbatim from uxmatrix/u5/tools/score_u5.py); data replays/RCST/ (gate.json).

## Identity (switch off vs rs-RC, replays/RC): PASS
- MAIN 97: kept chunk ids in order 97/97.
- F8 96 (48 F0 + 48 F8): 96/96.

## RS_STICKY=2 (subject carry), ENGINE-RC kit, vs U5 (SEFIX-124 ON)
| set | K1 turn 1 | survived without carry | lost | carry recovers | K2 with carry | off-subject share no carry / carry | carry off-subject mult | U5 reference |
|---|---|---|---|---|---|---|---|---|
| F8 48 | 21 | 1/21 | 20 | **16/20** | 18 | 0.99 / 0.88 | **1.20x** | K1 19, 1/19, recovers 15/18, 1.22x |
| LS 20 | 13 | 4/13 | 9 | **8/9** | 14 | 0.88 / 0.73 | **1.08x** | 4/13, 8/9, 1.08x |
LS self-contained turns: kept chunks with / without carry 1.29x (U5 1.29x). Reading: same as U5 on the RC kit (carry recovers most lost referents, at about 1.2x off-subject chunks on F8 and 1.29x more chunks on self-contained turns); measurement only, not adopted.

## Generation path (bench-only, be/ of rs-RC-STICKY)
The desktop adapter does not pass history.rsSticky. rs-RC-STICKY's be/adapter-litedecline.ts (sha 1683a033 before the second edit; final sha in the tree manifest f28d5047, identical on the mini) adds: RS_STICKY_DUMP=<jsonl> records each item's last non-empty engine `sources` event (full chunks, as replay-sticky.ts's carrier), and, read at process start, gives a turn-2 item the chunks of its turn 1 (RS_STICKY_PREV = jobs/v3-s-carry/prev.json, F8 id -> F0 id) as history.rsSticky, with an `other/rs-sticky-carry` trace event. Env rcsticky = rc.env + RS_STICKY=2 + those two paths. Not smoke-tested on the mini (one job at a time there): the morning check is `sticky:carried-N` reason codes on the 48 turn-2 traces; if they are absent, job 17 is FAIL-INFRA and is not labelled.

## Appended (mini extension queue, after job 16; read by the waiting start-ext invocation when the main queue exits)
17. v3-s-carry: 48 F0 + 48 F8 (turn 2 with history as V3L2), persona S, seed 42, tree rs-RC-STICKY, env rcsticky. Labels later by the frozen V3L2 protocol.
18. v2-p2: V2 UXMATRIX seed 42, ON/OFF (115), persona v2/personas/p2.json (file sha 3936980a, adapter persona sha 272d238c): Succinct with "Answer in two short paragraphs" replacing the length phrase in system prompt and reminder, rest unchanged. Reported next to S and S+; the S+ ADOPT rule does not apply.
- Live check (replaces the MacBook smoke, cancelled by the coordinator): the carry path was verified live on the mini at 21:53 in job 17 v3-s-carry: turn 1 48/48 rc 0, the first 13 turn-2 traces 13/13 carry sticky:carried reason codes and the rs-sticky-carry event (final count in the morning).
