# U5 FOLLOWUP-PACKS: does a source found on turn 1 survive the follow-up in OUR engine, with the pack on? (2026-10-23, 0 LLM)
Criterion U5-criterion.md, sha256 a87f8877d1996cbec9e16edee49b566ebd44be8eb54d3a9c31deae9d27ef2aff, frozen before any replay and not edited. 0 LLM, 0 judge, 0 paid, 0 phone, MacBook only (mini not used), blind not read. Data: u5.json (aggregates + per-pair rows), u5/ls_off_plan.json; replays in u5/replays (gitignored).

## Verdict
**NO, the source does not survive in our engine: F8 1/19 with the pack on (his FollowUp rule 17/18); LONGSESSION 4/13 (his 12/16).** Subject carry (RS_STICKY=2) recovers 15 of the 18 lost F8 pairs, but at 1.22x off-subject chunks (line 1.20x), and on LONGSESSION it recovers 8/9 at 1.08x but adds 1.29x chunks on self-contained turns (line 1.20x). **By the frozen line, no follow-up fix is proposed from this test** (F8 misses the junk line by 0.02; read it as borderline, not as "carry is clean").

## Table (turn 1 = F0 / previous turn, turn 2 = the follow-up; K13 kit; hit rule F8 = gold quote in a kept chunk, LS = referent string in a kept chunk)
| set | arm | n | K1 turn 1 | K2 turn 2 | **survived S/K1** | lost | R: carry recovers | found only on turn 2 | junk t2 (off-subject share) | junk t2 with carry | carry off-subject mult | K2 with carry |
|---|---|---|---|---|---|---|---|---|---|---|---|---|
| F8 48 | BASE | 48 | 17 | 1 | **0/17** | 17 | 14 | 1 | 1.00 | 0.92 | 1.26x | 15 |
| F8 48 | **ON (SEFIX-124)** | 48 | 19 | 2 | **1/19 = 0.05** | 18 | **15** | 1 | 0.99 | 0.90 | **1.22x** | 17 |
| F8 48 | OFF (gold pack removed) | 48 | 0 | 0 | – | 0 | 0 | 0 | 1.00 | 1.00 | 1.26x | 0 |
| LS 20 | BASE | 20 | 14 | 7 | 5/14 = 0.36 | 9 | 5 | 2 | 0.84 | 0.72 | 1.10x | 12 |
| LS 20 | **ON** | 20 | 13 | 6 | **4/13 = 0.31** | 9 | **8** | 2 | 0.88 | 0.73 | **1.08x** | 14 |
| LS 20 | OFF (referent pack removed) | 20 | 11 | 6 | 3/11 = 0.27 | 8 | 6 | 3 | 0.88 | 0.73 | 1.04x | 13 |
| LS his 16 | BASE | 16 | 13 | 6 | 5/13 | 8 | 5 | 1 | 0.80 | 0.67 | 1.13x | 11 |
| LS his 16 | ON | 16 | 12 | 5 | 4/12 = 0.33 | 8 | 7 | 1 | 0.86 | 0.69 | 1.10x | 12 |
| LS his 16 | OFF | 16 | 10 | 4 | 3/10 | 7 | 6 | 1 | 0.89 | 0.71 | 1.03x | 11 |
LS self-contained turns 2-5 (20, not 30 as the criterion text says; the chain has 20 of each), mean kept without / with carry: BASE 4.90 / 6.65 (1.36x), ON 5.05 / 6.50 (**1.29x**).
F8 per pack, ON (K1, survived, lost, R): crypto 6/1/5/4, wikivoyage 8/0/8/8, firstaid 2/0/2/1, medlineplus 2/0/2/1, visa 1/0/1/1, factbook 0 (the F0 turn never keeps the factbook gold).
Comparison (UXT-24, his engine, KB + Vital + 6 packs): F8 K1 18, survived 17/18, R 1; LS 12/16, R 2, carry 1.19x / 1.37x. Our R5 (other recipe): base 2/48 on turn 2, carry 19/48 at 1.42x.

Reading:
- The pack is what finds the source on turn 1 (F8: 19 with it, 0 without; LS 13 vs 11). SEFIX-124 over BASE changes almost nothing across turns (K1 17 -> 19, survival 0 -> 1).
- The loss is the engine, not the pack: turn 2 searches the fragment alone ("and when was that vulnerability found?"), and on F8 0.99 of the kept chunks are off the article turn 1 found. Survival is the same with and without the pack.
- The gap to his rule is all on F8-shaped fragments (1/19 vs 17/18). On LONGSESSION both engines lose about a quarter to two thirds, and ours loses more (4/13 vs 12/16).
- Carry works mechanically (F8 17/48 kept on turn 2, close to R5's 19/48 and his 17/48), but it costs extra off-subject chunks. His rule gets the same reach by searching with the previous question, at 1.19x.

## Commands
- Tree kiln-local/rs-U5 = cp -cR rs-SEFIX + patch -p1 retrieve-sweep/patches/R5-STICKY.patch (sha 6b172fd2); rs-SEFIX untouched. Identity rs-U5 vs rs-SEFIX (LS ON, no carry): kept ids + reason codes 50/50.
- u5/tools/run_u5.sh <qform|longsession> <label> <BASE|ON> <0|2> [drop-pack] (r5 replay-sticky.ts, kits.py 10, packHeadPass a2, packDense2 append-budget, gate search, cpu embed, wide 0; ON = RS_MERGE=gidf RS_SE_LEAD=0.78 RS_SE_MAXDF=0.25 RS_KEEP_NOPROPER=1).
- u5/tools/queue.sh (BASE/ON x carry on both sets + identity + F8 OFF per gold pack x carry); u5/tools/plan_ls_off.py -> ls_off_plan.json (13 pairs by the previous turn's referent pack, 7 by the follow-up's first kept pack, 0 full kit) -> u5/tools/queue2.sh; u5/tools/score_u5.py -> u5.json.
- Wall: about 30 min of replays. A first attempt that ran two queues in parallel died on a SQLite lock in the shared appdir cache (0 rows used; logs in u5/replays/failed-lock); everything was rerun sequentially.

## Caveats
- Kept is not answered. History (the previous answer text) still reaches the prompt, so the 1.7B can repeat turn 1's fact from history even when turn 2 keeps no source. This test measures sources and the "Not found" path, not answer text.
- The F8 off-subject share counts any chunk outside the gold article as off-subject (strict), so 0.99 also counts on-topic neighbours. The carry multiplier compares like with like.
- LS is a referent-string proxy on agent-written dev data. F8 items are agent-written dev data. "K1 kit" in the task was read as K13, the adopted 13-pack kit (stated in the criterion). The OFF LS pack choice depends on the ON replay, following the frozen rule.
- His numbers come from his engine and corpus (KB + Vital + 6 packs, retrieve 4). The comparison is about direction, not a paired one.

## Para r4to (PT-BR)
- Com o pack ligado, a referência NÃO sobrevive à pergunta seguinte no nosso motor: 1 de 19 nas F8 ("e quando foi isso?") e 4 de 13 no LONGSESSION. A regra FollowUp do the app maintainer mantém 17 de 18 e 12 de 16.
- O pack acha a fonte no turno 1 (19 com ele, 0 sem). Quem perde a fonte é o motor: o turno 2 busca só o fragmento, e 99 % do que volta é de outro artigo.
- Para o usuário, a segunda pergunta vem com passagens erradas, ou com "Não encontrado", ou o modelo responde de cabeça usando o histórico, sem fonte nova.
- Carregar o assunto recupera 15 das 18 fontes perdidas, mas traz 1,22x de lixo (linha 1,20x). A régua congelada diz que não há fix aqui: no app que vai ser entregue, a regra dele já resolve o caso.
