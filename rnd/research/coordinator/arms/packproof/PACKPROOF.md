# PACKPROOF: does the app answer right when the pack holds the answer, and say so honestly when it does not? (2026-10-23)

**Leitura para o r4to (PT-BR):**
1. A tese **não se sustenta como frase absoluta** no 1.7B Succinct: com o pack instalado, ele acerta 48 % das perguntas do próprio pack (86/180). Sem o pack, acerta 26 %. O pack soma +0.23 (+0.16..+0.31), mas fica longe dos 75 % previstos.
2. O que se sustenta é a versão condicional. **Quando a busca entrega o artigo certo ao modelo** (98/180 itens), ele acerta 65 %. Quando não entrega, acerta 28 %. O gargalo é a busca (artigo kept em 54 %), não o pack.
3. "Honesto quando não tem" **se sustenta pela faixa de aviso, não por recusa**. Sem o pack, só 17 % das respostas saem erradas e confiantes. Já 45 % saem erradas com o aviso "Not found…" e apenas 12 % dizem "não sei".
4. Nenhum pack PROVA pela regra congelada (correct-any ON ≥ 0.75). Dois ficam em PARCIAL: qa-bitcoin-se 0.60 e qa-health-se 0.60. Os outros 7 ficam abaixo de 0.60 e, pela regra, **não deveriam ser default-eligible**. O pior é boar-factbook 0.25 (40 % errado-confiante sem o pack), depois firstaid e outdoors com 0.35.
5. Os packs que provam a versão condicional (acerto ≥ 0.75 quando o artigo é entregue) são qa-ethereum-se, qa-health-se, boar-firstaid-en e boar-medlineplus-en. Os três de saúde são AI-reviewed, not clinically reviewed, e as amostras são pequenas (n 6 a 11).
6. Frase para a página do app: "Quando o BOAR encontra a passagem certa no pack, acerta cerca de 2 em 3 perguntas sobre ela. Quando não encontra, avisa na própria resposta que não veio da biblioteca offline: só 1 em 6 respostas sem pack sai errada sem aviso (1.7B, perguntas de teste escritas a partir dos packs, rótulos Haiku)."

Criterion: PACKPROOF-criterion.md sha256 37f74d6fa85029faaf23e65e675f45578e02a12c769230436ae5f91b3e9c9419 (frozen before any run, not edited; verified). Ledger: CALLS.md (Haiku 395 of 400, Opus 0, paid 0, phone 0).

## System and hosts
SEFIX-124 (the adopted search stack): be-0cfd4a77-cut7-litepacks + H4-MERGE + SEFIX-ALL patches, env RS_MERGE=gidf RS_SE_LEAD=0.78 RS_SE_MAXDF=0.25 RS_KEEP_NOPROPER=1, F3 off; adapter-litedecline (d53c1487), Qwen3-1.7B Q4_K_M (b139949c), seed 42, Succinct persona, 512 max tokens, llama-server b11010 CPU -t 4 (not -t 6: same as the mini recipe and UXMATRIX), detector mmBERT v3b. Kit K13 (sha-pinned; v3proto builds). ON = K13 (7 packs in K13) or K13 + pack (qa-ethereum-se, qa-bitcoin-se, v3proto c58d44eb / 012e0053). OFF = K13 minus the pack, or K13.
**Hosts differ by arm** (coordinator parallelism note 12:4x): ON on-k13 (140) and on-k13+qa-bitcoin-se (20) on the MacBook (M1 Pro). ON on-k13+qa-ethereum-se (20) on the mini: the 14:10 session restart killed the MacBook run at 6/20 and wiped the scratch tree, so the group was re-run whole on the mini. All 8 OFF groups (180) ran on the mini (M4). ON and OFF are compared per item by outcome class, not by bytes.
Host identity check (kept list title + source, in order, vs the mini sefix124-main-s42 traces; 5 items vit-hum-001, vit-hum-004, lan-exp-001, st-qa-cooking-se-001, st-qa-money-se-019): **MacBook 5/5, mini 5/5** (aggregates/ident5.json, ident5-mini.json); answer texts differ across hosts (CPU numerics).

## Commands
```
python3 -I tools/mk_req.py            # 360 requests, 11 groups (in/)
python3 -I tools/own.py               # own-article table (url + title) per item
tools/run.sh ident; tools/run.sh main # MacBook (ON groups; OFF dirs held placeholders)
tools/run_mini_off.sh start|fetch     # mini: ident5 + 8 OFF groups (job pp-off-s42)
tools/run_mini_eth.sh start|fetch     # mini: ethereum ON re-run (job pp-on-eth-s42)
python3 -I tools/ident.py [ident5-mini]
python3 -I tools/prep.py; ONLY_A=1 node tools/label.mjs judge/units.json judge/labels.jsonl; node tools/label.mjs judge/units.json judge/labels.jsonl
python3 -I tools/agg.py               # aggregates/packproof.{json,table.md}
```

## THE TABLE (Haiku 5.5-low outcome labels, UXMATRIX protocol; shares of n; funnel = own fact article in raw / kept / shown / cited, ON arm)
| pack | n | ON CWS | ON correct-any | ON refused-wrongly | OFF honest-unknown | OFF wrong-confident | OFF wrong-warned | OFF correct-any | Δ correct-any ON-OFF (CI) | ON funnel retrieved / kept / shown / cited | time p50 s ON / OFF | verdict |
|---|---|---|---|---|---|---|---|---|---|---|---|---|
| qa-travel-se | 20 | 0.55 | 0.55 | 0.00 | 0.00 | 0.25 | 0.55 | 0.20 | +0.35 (+0.10..+0.60) | 0.65 / 0.85 / 0.85 / 0.35 | 27.6 / 5.0 | DOES NOT PROVE |
| qa-ethereum-se | 20 | 0.45 | 0.55 | 0.00 | 0.00 | 0.10 | 0.70 | 0.20 | +0.35 (+0.15..+0.55) | 0.45 / 0.50 / 0.50 / 0.10 | 5.1 / 4.6 | DOES NOT PROVE |
| qa-bitcoin-se | 20 | 0.55 | 0.60 | 0.00 | 0.00 | 0.15 | 0.70 | 0.15 | +0.45 (+0.25..+0.65) | 0.20 / 0.35 / 0.35 / 0.20 | 11.0 / 5.2 | PARTIAL |
| qa-health-se (health*) | 20 | 0.45 | 0.60 | 0.00 | 0.20 | 0.00 | 0.25 | 0.55 | +0.05 (-0.15..+0.25) | 0.35 / 0.55 / 0.55 / 0.40 | 9.3 / 5.0 | PARTIAL |
| qa-outdoors-se | 20 | 0.30 | 0.35 | 0.00 | 0.15 | 0.15 | 0.50 | 0.20 | +0.15 (-0.05..+0.35) | 0.45 / 0.55 / 0.55 / 0.30 | 6.4 / 4.2 | DOES NOT PROVE |
| boar-firstaid-en (health*) | 20 | 0.30 | 0.35 | 0.00 | 0.50 | 0.15 | 0.15 | 0.20 | +0.15 (-0.10..+0.40) | 0.15 / 0.30 / 0.30 / 0.10 | 1.3 / 0.8 | DOES NOT PROVE |
| boar-medlineplus-en (health*) | 20 | 0.45 | 0.55 | 0.00 | 0.25 | 0.15 | 0.10 | 0.50 | +0.05 (-0.10..+0.25) | 0.55 / 0.45 / 0.45 / 0.20 | 6.2 / 4.6 | DOES NOT PROVE |
| boar-factbook | 20 | 0.20 | 0.25 | 0.00 | 0.00 | 0.40 | 0.40 | 0.20 | +0.05 (-0.15..+0.25) | 0.25 / 0.45 / 0.45 / 0.40 | 6.9 / 5.4 | DOES NOT PROVE |
| boar-simplewiki-en | 20 | 0.45 | 0.55 | 0.00 | 0.00 | 0.20 | 0.70 | 0.10 | +0.45 (+0.20..+0.70) | 0.55 / 0.90 / 0.90 / 0.45 | 6.9 / 5.1 | DOES NOT PROVE |
| **pooled 180** | 180 | 0.41 | 0.48 | 0.00 | 0.12 | 0.17 | 0.45 | 0.26 | +0.23 (+0.16..+0.31) | 0.40 / 0.54 / 0.54 / 0.28 | 6.9 / 4.9 | DOES NOT PROVE |
| qa-cooking-se (UXMATRIX reuse, not pooled) | 20 | 0.30 | 0.35 | 0.00 | 0.30 | 0.10 | 0.40 | 0.20 | +0.15 (+0.00..+0.30) | 0.60 / 0.45 / 0.45 / 0.30 | 7.0 / 6.7 | DOES NOT PROVE |
| qa-money-se (UXMATRIX reuse, not pooled) | 20 | 0.25 | 0.30 | 0.00 | 0.05 | 0.00 | 0.70 | 0.25 | +0.05 (-0.10..+0.25) | 0.45 / 0.50 / 0.50 / 0.15 | 10.4 / 5.8 | DOES NOT PROVE |

\* health pack: AI-reviewed, not clinically reviewed. Shown = kept in this tree (every kept passage is shown). Retrieved can be lower than kept because headpass/dense appends add chunks from outside the raw list. The time columns mix hosts (ON on the MacBook, loaded by UXMATRIX and a game; ethereum ON and all OFF on the mini), so they are not a latency comparison. Cooking/money rows are UXMATRIX Succinct labels reused by unit key (MacBook both arms, same protocol), never pooled.

Conditional on the funnel (ON, pooled): correct-any **0.65 when the own article is kept (n 98)** vs 0.28 when it is not (n 82). Per pack, kept to correct: ethereum 0.80 (10), health 0.82 (11), firstaid 0.83 (6), medlineplus 0.78 (9), bitcoin 0.71 (7), simplewiki 0.61 (18), travel 0.59 (17), outdoors 0.45 (11), factbook 0.44 (9).
UX surface (pooled): the Not-found banner appears on 42 % of ON answers and 58 % of OFF answers. bannerkept.patch is not applied, so many ON banners sit on top of kept sources (the known false banner). The health decline line appears on 11 % of ON answers. REFUSED_WRONGLY is 0.00 everywhere.
Label resolution: 300 single, 49 A = B, 11 A ≠ B with no C call (cap reached, A stands).

## Predictions
| # | prediction | result | |
|---|---|---|---|
| P1 | pooled correct-any ON ≥ 0.75 | 0.48 | MISS |
| P2 | pooled honest-unknown OFF ≥ 0.50 | 0.12 (the warned-wrong share is 0.45 instead) | MISS |
| P3 | pooled wrong-confident OFF ≤ 0.25 | 0.17 | HIT |
| P4 | weakest pack is format-1 or a Wikipedia-style topic pack | boar-factbook 0.25 (topic pack) | HIT |
| P5 | weakest is boar-firstaid-en | factbook 0.25; firstaid 0.35 ties for second with outdoors | MISS |
| P6 | Δ correct-any > 0 for every pack | all +0.05..+0.45 | HIT |

## Reads (frozen rules)
- Thesis "right when the pack holds it": **does not hold** (P1 miss, even though the pooled Δ CI is above 0). Per pack: 0 PROVES, 2 PARTIAL (bitcoin, health), 7 DOES NOT PROVE (ON correct-any < 0.60). By the frozen rule those 7 should not ship as default-eligible, and the app page must not claim the thesis for them.
- Thesis "honest when not": **holds** (OFF wrong-confident 0.17 ≤ 0.25). The mechanism is the warning line, not abstention, so the honesty surface does not need a change by the rule.
- REFUSED_WRONGLY with the pack ON is 0.00, so there is no refusal bug.
- What would change the story: the conditional reading (0.65 when delivered) says the lever is delivery (kept 54 %), plus the reader for factbook/outdoors (kept → correct < 0.5). A defensible app sentence is conditional on finding the passage, as in line 6 above.

## Caveats
One seed (42); Haiku labels (not human), blinded to arm; 1.7B Succinct only; self-tests are agent-written from the pack text (retrieval favoured, install value by construction, dev only, never claim items); K13 uses v3proto builds, not the published bytes; two hosts across arms; OFF kits still hold overlapping content (wikivoyage, vital5 and simplewiki overlap factbook and health), so some OFF correct answers are legitimate; the false Not-found banner (bannerkept.patch not applied) inflates WRONG_WARNED on ON answers; 11 labels without a tie-break.
