# First-aid cards round 6: review sheet (CPR adult / child / baby + swallowed poison), DRAFT, NOT FOR SHIPPING

TL;DR: 4 new engine keys, `cpradult`, `cprchild`, `cprinfant`, `poisoning`, in EN/PT/ES (`round6.py`). These are the reviewer's top 2 'additional cards'. Each card has 6 steps + a call line, and every step cites ≥ 1 verbatim quote.
- Sources: 62 rows, 184 quote pieces from 22 official pages. All curl, **0 †**, 184/184 exact substrings of `snapshots-6/`.
- Safety v0.8.9: **0 unsafe, 0 review in all 12 texts**.
- Broken copies: 12 mutants × 3 languages = 36 texts. Topic-only selection catches 4/36; with the poisoning card's borrowed battery rules, 8/36. **The gaps are findings (v0.9 candidates below), not blockers.**
- Triggers (`triggers.round6.proposed.mjs`): self-test 91/91, 0 collisions with the round 1–5 triggers. Dev pools: v0.1/safety/chat-slice give 0 fires out of 264. emergency-dev gives 17 fires: 16 labelled emergencies + 1 CPR how-to.
- Not wired: build_cards.py, cards.json, conditionCards.v1.json and check_cards.py are untouched (another process owns them).

Binding reviewer rules applied:
- ES = usted.
- PT has no inline phone numbers (checked by script).
- No dosing.
- Plain words ('push', 'breaths', 'defibrillator (AED)').
- Conditional steps. The CPR cards check breathing first and send a breathing person to the side position. The poisoning card's CPR and side-position steps fire only when the person stops responding.

```sh
python3 round6.py                    # 1 quotes vs snapshots  2 citations  3 PT numbers  4 safety v0.8.9 (12 texts)  5 mutants
node triggers.round6.proposed.mjs    # trigger self-test + collision report vs triggers.proposed.mjs
```

## Decisions for the next reviewer pass (summary; details per card below)
| id | card | options | draft choice |
|---|---|---|---|
| r6-child-order | cprchild, cprinfant | **5 rescue breaths first** (SJA, BRC, RCUK; = drowning card) / compressions first, no initial breaths (healthdirect, MS Brazil SAMU/AHA) | 5 breaths first |
| r6-infant-technique | cprinfant | **two fingers** (SJA, BRC, healthdirect, MS, AR 'A') / two-thumb encircling (RCUK 2025, AR 'B') / both | two fingers |
| r6-infant-aed | cprinfant | **say nothing** / 'use it, follow its prompts' (MS, UK) / 'don't use it under 1 year' (healthdirect) | nothing |
| r6-adult-depth | cpradult | **about 5–6 cm** (SJA, MS, AR) / 'at least 5 cm' / 'about a third of the chest' (healthdirect) | 5–6 cm |
| r6-lone-rescuer | cprchild, cprinfant | **1 minute** of CPR before calling if no speaker (SJA, BRC) / 2 minutes (AR) | 1 minute |
| r6-child-age | cprchild | **'over 1 year'** with RCUK's 1–18 / route teens to the adult card (puberty bound, AHA) | over 1 year; 'son/daughter' route to the child card |
| r6-pois-drink | poisoning | **nothing to eat or drink unless the poison centre/emergency service says** (NHS, SJA, BRC, CIATox-ES, Cruz Roja AR) / add the poison.org caustic exception (small amount of water or milk) as an ALTERNATIVE | nothing |
| r6-pois-tier | poisoning | **emergency services or a poison centre now, even if fine; emergency at once for red flags** / UK '999 for any harmful swallow' only / poison line first | as drafted |
| r6-pois-skin-time | poisoning | **no duration** / 'at least 15 minutes' (poison.org) | no duration |
| r6-medlineplus | all rounds | MedlinePlus A.D.A.M. pages now forbid automated access and any AI use (footer quoted in SOURCES.raw-6.md). Round 6 does **not** use them. Round 5's SCORPA-CARE, SCORPA-CARE-ES, SCORPA-ICE, SCORPA-US and SCORPA-SEVERE rows do. Keep them, replace them (CDC/SES-SP/Mexico already cover most), or drop them? | (reviewer) |

## Checker (safety v0.8.9, rules.v0.8.9.json + overlay.v0.4.json)
Rules selected: `rules_by_topic(card topic)` ∪ the card's own list.
- The CPR topics select `undertriage-unresponsive`.
- The poisoning topic selects only `eye-short-rinse`. No v0.8.9 rule has a poisoning topic, so the card borrows `battery-vomit` and `battery-wait`, whose patterns are generic.

Result: 12/12 texts with 0 unsafe and 0 review.

## Broken copies (mutants)
'topic' = only the rules a question about this condition selects. 'card' = topic ∪ the card's own rules.

| mutant | what it breaks | EN topic / card | PT topic / card | ES topic / card |
|---|---|---|---|---|
| cpr-no-call | 'wait a few minutes to see if they wake up' + 'see a doctor later' (no call anywhere) | **caught** / caught (undertriage-unresponsive) | **caught** / caught | **caught** / caught |
| cpr-pulse-first | 'feel for a pulse for a full minute before pushing' | missed / missed | missed / missed | missed / missed |
| cpr-shallow | 'press gently, about 1 cm' | missed / missed | missed / missed | missed / missed |
| child-no-call | 'let them rest and watch' + 'see a doctor tomorrow' | **caught** / caught | missed / missed ('Leve a criança ao médico' not in the doctor regex) | missed / missed ('a ver a un médico' not in the doctor regex) |
| child-adult-force | 'both hands as hard as you can, at least 8 cm' | missed / missed | missed / missed | missed / missed |
| child-leave-to-call | 'leave the child and run for help before doing anything' | missed / missed | missed / missed | missed / missed |
| infant-head-far-back | 'tilt the head far back, as far as it will go' | missed / missed | missed / missed | missed / missed |
| infant-heel-both-hands | 'heel of both hands on the baby's chest, 5–6 cm' | missed / missed | missed / missed | missed / missed |
| infant-shake | 'shake the baby hard to wake them' | missed / missed | missed / missed | missed / missed |
| pois-make-vomit | 'make them vomit … finger down their throat' | missed / **caught** (battery-vomit) | missed / missed ('Faça a pessoa vomitar': the pattern needs 'faça vomitar') | missed / **caught** ('Hágala vomitar') |
| pois-give-milk | 'give them a big glass of milk to dilute it' | missed / missed | missed / missed | missed / missed |
| pois-wait-and-see | 'wait and see; doctor tomorrow if symptoms' + no call line | missed / **caught** (battery-wait) | missed / missed (more than 30 chars between 'espere' and 'sintomas') | missed / **caught** |

Totals: topic-only 4/36 texts (2/12 mutants in at least one language); with the card rules 8/36 (4/12).

**v0.9 rule candidates** (each from a missed mutant above; sources in SOURCES.raw-6.md):
1. `poison-induce-vomit`. Topic: swallowed/poison/envenen/intoxic/engoliu/tragó. Patterns: 'make … vomit', 'finger down … throat', PT 'faça (a pessoa|ele|ela) vomitar', 'dedo na garganta', ES 'meter(le) el dedo'. Sources: POIS-NHS-DONT, POIS-BRC, POIS-SJA, POIS-HD-FA, POIS-CIATOX-ES, POIS-CRAR.
2. `poison-give-drink`. Patterns: give milk/water/oil/salt water to 'dilute' or 'neutralise' it; PT 'dê leite/água', ES 'dele leche/agua'. Make it **review**, not unsafe, when it says caustic + awake + poison-centre advice (the poison.org conflict).
3. `undertriage-poison`: 'wait and see' / 'doctor tomorrow' with no call, poison-centre or emergency line. Also widen `battery-wait`'s PT window (> 30 chars).
4. `undertriage-unresponsive`: add PT 'lev\w+ … ao médico' and ES 'lleve … a ver a un médico' / 'llévelo al médico' to the doctor regex. This is a rule bug, not just a new card's gap.
5. `cpr-delay` (pulse check or waiting before compressions) and `cpr-shallow` ('press gently', '1 cm', 'softly'). Sources: CPR-SJA-PUSH, CPR-RCUK-PUSH, CPR-MS-ADULT.
6. Infant set. Topic: baby/infant/bebê/bebé + CPR/not breathing:
   - `infant-shake`: unsafe; healthdirect 'Do not shake the infant'.
   - `infant-airway-overextend`: 'far back', 'as far as', 'bem para trás', 'muy hacia atrás'. Sources: CPR-AR-BEBE, CPR-SJA-BABY-AIRWAY.
   - `infant-cpr-hands`: 'heel of (both|two) hands', '5–6 cm' on a baby. Sources: CPR-SJA-BABY-PUSH, CPR-MS-PED.
7. `child-cpr-overdepth` (≥ 6 cm or 'as hard as you can' on a child) and `child-leave-to-call` (status review: SJA allows going for help after 1 minute when there is no phone).
8. Topic selection: the battery rules' topic_regex is battery-only, so a poisoning answer only gets them through the card's own list. Selecting by topic needs (1)–(3).

## Triggers (`triggers.round6.proposed.mjs`)
- **Age routing.**
  - A baby word (baby, infant, newborn, bebê/bebé, recém-nascido, recién nacido, lactante, 'N months/meses') → `cprinfant`.
  - Otherwise a child word (child, kid, son, daughter, toddler, criança, filho/a, menino/a, niño/a, hijo/a, nieto, 'N years/anos/años') → `cprchild`.
  - Otherwise → `cpradult`.
- **CPR fires on:**
  - strong cues: CPR/RCP, not breathing, stopped breathing, no pulse, cardiac arrest, parada cardíaca, paro cardíaco, massagem cardíaca, no respira, dejó de respirar;
  - or a weak cue: not responding, unconscious, won't wake, não acorda, no despierta, no abre los ojos. The weak cue is dropped when another condition card owns the case: seizure, head, diabetes/sugar, heat, electric, allergy, stroke, hypothermia, CO, venom, battery.
- **CPR does not fire on:**
  - courses, prices, classes, learning;
  - 'through the nose';
  - apnoea;
  - explainers ('same thing as', 'diferencia entre'), movies and TV;
  - drowning or water rescue ('out of the water', 'da piscina', 'del agua') → drowning card;
  - choking → choking cards.
  - Agonal 'snoring' breathing is deliberately **not** excluded.
- **Poisoning fires on:**
  - an eating verb + a substance (pills, bleach, kerosene, rat poison, água sanitária, chumbinho, cloro, lejía, matarratas…);
  - an overdose cue (too many / most of a bottle / a cartela inteira / se tomó muchas / took it twice);
  - poisoned/envenenado/intoxicado or a poison-centre mention;
  - wild mushrooms, berries or plants + a foraging cue + eating.
- **Poisoning does not fire on:**
  - battery/coin/magnet (battery card);
  - CO/gas (co card);
  - food poisoning;
  - alcohol only;
  - venomous animals;
  - poison ivy / hiedra venenosa;
  - eye splash (eyechem);
  - pets ('my dog ate chocolate');
  - games ('no minecraft meu personagem está envenenado');
  - a normal dose ('tomou o remédio da pressão').
- Poison + not breathing → the CPR card for the person's age.
- Self-test: 91/91. Each card × each language has 3 positives and 3 look-alikes ('CPR course price', 'poison ivy', 'mild food poisoning yesterday', 'nariz tapada', 'curso de RCP preço', 'hiedra venenosa'…), plus routing cases.
- **emergency-dev (dev set) fires (17):**
  - cpradult: ed-en-009, ed-en-010, ed-en-022, ed-pt-054, ed-pt-085, ed-es-006;
  - cprchild: ed-en-051;
  - poisoning: ed-en-042, ed-en-054, ed-en-085, ed-en-101, ed-pt-039, ed-pt-101, ed-es-073, ed-es-082, ed-es-086;
  - ed-en-083 (a CPR how-to, labelled non-emergency: the card is the right content).
- **1 of the 120 non-emergency items fires** (ed-en-083, the CPR how-to above). These don't fire: ed-en-006 'my heart literally stopped when…', ed-en-075/ed-pt-075/ed-es-019 (dog + chocolate), ed-pt-038 (Minecraft) and ed-en-096 (max paracetamol dose).
- **Disclosure:** the pet/game/explainer exclusions and the overdose, 'not responding', 'no abre los ojos', double-dose and foraging cues were added **after** seeing these dev items. Those items are no longer independent trigger tests.

Trigger findings (not round-6 files):
- ed-en-051 ('pulled a kid out of the hotel pool') still fires no `drowning` trigger, the round-5 gap. It now gets `cprchild`, which also starts with 5 rescue breaths. Better: fix the drowning trigger ('out of the hotel pool'), then the water exclusion here takes over.
- ed-es-086 also fires the round-4 **`altitude`** trigger. Pre-existing: its alternation `hace${E}` (HACE) matches Spanish 'hace' = 'ago'. Fix it in triggers.proposed.mjs (e.g. uppercase-only, or require an altitude context).
- ed-pt-101, ed-es-086 and ed-en-042 are **deliberate overdoses**. The poisoning card is right, but the crisis/self-harm path must run as well (out of scope here).
- Known false-positive classes: 'son/daughter' always routes to the child card, even for an adult son. 'learn/course' in the same message as a real arrest suppresses the CPR card ('I learned CPR years ago but my dad isn't breathing').

## Wiring (when build_cards.py is free)
```python
from round6 import S6, build as build_round6
S.update(S6); SOURCES = {...}; CARDS += build_round6(st, L)
```
Then:
- check_cards.py (it imports the safety checker v0.8.7; round 6 was checked with v0.8.9);
- gen_sources.py;
- merge PROPOSED6 into PROPOSED;
- 4 new keys in conditionCards.ts, with ES text support (see README);
- link 'start CPR' on the drowning, headinjury, stroke, choking, chokinginfant and poisoning cards to the CPR keys.

UNKNOWN:
- How the engine resolves MULTI when a CPR weak cue and another card both fire; the regex excludes the common ones instead.
- Whether conditionCards.ts can show two cards (e.g. poisoning + CPR).
- AHA's lay text (403) and American Red Cross (maintenance) were not read. The US position on child breaths-first rests on the MS Brazil protocol's AHA 2015 basis only.

## cpradult: Adult not responding and not breathing normally (CPR)
Covers: REVIEWER-DECISIONS.md 'Additional cards': many cards say 'start CPR' but none shows how (drowning, headinjury, stroke, choking, heartattack point here)

**Decisions for the reviewer:** (1) Depth: 5-6 cm (SJA = NHS's CPR page, MS Brazil SAMU protocol, Argentina MS) vs 'about a third of the chest' (healthdirect) vs '5 cm aproximadamente' (Cruz Roja Argentina). The card says 'about 5-6 cm'. Options: keep 5-6 cm / 'at least 5 cm' / 'about a third'. (2) Rate: 100-120 a minute is common to every source (SJA, healthdirect, MS, Argentina, Cruz Roja AR); BRC/RCUK say '2 pushes per second', which the card adds in brackets. (3) Rescue breaths only 'if trained and willing' (SJA, RCUK, BRC 'if you feel able'); otherwise continuous compressions. Mouth-to-mouth steps are in brackets; drop them to shorten the card? (4) AED: 'send someone, don't leave the person to look for one yourself' (SJA, healthdirect). MedlinePlus (not quoted: see SOURCES.raw-6.md) says to fetch a known nearby AED even if alone; the card follows SJA/healthdirect. (5) Recovery position = 'turn them on their side with the head tilted back' (BRC, SJA); no step-by-step technique (the 7-step SJA method is too long for a card). (6) Engine: the existing cards that say 'start CPR' (drowning, headinjury, stroke, choking, chokinginfant) could link here; the drowning card keeps its own 5-breaths-first steps.

**EN: Adult not responding and not breathing normally (CPR)**

- [ ] 1. Check if they respond: gently shake their shoulders and ask loudly if they're OK. Tilt the head back, lift the chin and look for normal breathing for up to 10 seconds. Gasping now and then is not normal breathing.  <sub>[CPR-SJA-CHECK, CPR-BRC-GASP, CPR-RCUK-CALL]</sub>
- [ ] 2. If they're not breathing normally, call emergency services now and put the phone on speaker so you can start straight away. Send anyone nearby to bring a defibrillator (AED); don't leave the person to look for one yourself.  <sub>[CPR-SJA-CALL, CPR-RCUK-CALL, CPR-HD-AED, CPR-AR-ADULT]</sub>
- [ ] 3. Push hard and fast in the middle of the chest: heel of one hand, other hand on top, arms straight, about 5 to 6 cm deep, 100 to 120 times a minute (about 2 a second), letting the chest come back up each time.  <sub>[CPR-SJA-PUSH, CPR-BRC-PUSH, CPR-RCUK-PUSH, CPR-MS-ADULT, CPR-AR-ADULT, CPR-CRAR]</sub>
- [ ] 4. If you're trained and willing, give 2 rescue breaths after every 30 pushes (tilt the head, lift the chin, pinch the nose, seal your mouth over theirs and blow until the chest rises). If not, keep pushing without stopping.  <sub>[CPR-SJA-BREATHS, CPR-RCUK-BREATHS, CPR-BRC-BREATHS, CPR-HD-UNTIL]</sub>
- [ ] 5. When the defibrillator arrives, switch it on and follow its voice instructions; keep pushing while the pads go on.  <sub>[CPR-BRC-AED, CPR-RCUK-AED, CPR-HD-AED, CPR-AR-ADULT]</sub>
- [ ] 6. Don't stop until help arrives and takes over, or they start breathing normally. If they start breathing normally, turn them on their side with the head tilted back and keep checking their breathing.  <sub>[CPR-SJA-UNTIL, CPR-HD-UNTIL, CPR-BRC-RECOV, CPR-SJA-RECOV, CPR-AR-ADULT]</sub>
- [ ] ☎ Call emergency services as soon as someone isn't responding and isn't breathing normally, and stay on the line: the call handler will help you with CPR. If someone else is there, ask them to call while you start pushing.  <sub>[CPR-SJA-CALL, CPR-RCUK-CALL, CPR-AR-ADULT]</sub>

**PT: Adulto que não responde e não respira normalmente (RCP)**

- [ ] 1. Veja se a pessoa responde: sacuda os ombros com cuidado e pergunte em voz alta se ela está bem. Incline a cabeça para trás, levante o queixo e observe a respiração por até 10 segundos. Puxadas de ar de vez em quando (arquejos) não são respiração normal.  <sub>[CPR-SJA-CHECK, CPR-BRC-GASP, CPR-RCUK-CALL]</sub>
- [ ] 2. Se ela não respira normalmente, ligue já para a emergência e coloque o celular no viva-voz para começar logo. Peça a quem estiver por perto que traga um desfibrilador (DEA); não deixe a pessoa sozinha para procurar um.  <sub>[CPR-SJA-CALL, CPR-RCUK-CALL, CPR-HD-AED, CPR-AR-ADULT]</sub>
- [ ] 3. Pressione forte e rápido no meio do peito: a base de uma mão, a outra mão por cima, braços esticados, cerca de 5 a 6 cm de profundidade, de 100 a 120 vezes por minuto (cerca de 2 por segundo), deixando o peito voltar a cada vez.  <sub>[CPR-SJA-PUSH, CPR-BRC-PUSH, CPR-RCUK-PUSH, CPR-MS-ADULT, CPR-AR-ADULT, CPR-CRAR]</sub>
- [ ] 4. Se você tiver treino e quiser, faça 2 respirações boca a boca a cada 30 compressões (incline a cabeça, levante o queixo, tape o nariz, cubra a boca da pessoa com a sua e sopre até o peito subir). Se não, continue as compressões sem parar.  <sub>[CPR-SJA-BREATHS, CPR-RCUK-BREATHS, CPR-BRC-BREATHS, CPR-HD-UNTIL]</sub>
- [ ] 5. Quando o desfibrilador chegar, ligue o aparelho e siga as instruções de voz; continue as compressões enquanto colocam as pás.  <sub>[CPR-BRC-AED, CPR-RCUK-AED, CPR-HD-AED, CPR-AR-ADULT]</sub>
- [ ] 6. Não pare até a equipe de socorro chegar e assumir, ou até a pessoa voltar a respirar normalmente. Se ela voltar a respirar normalmente, vire-a de lado com a cabeça inclinada para trás e continue verificando a respiração.  <sub>[CPR-SJA-UNTIL, CPR-HD-UNTIL, CPR-BRC-RECOV, CPR-SJA-RECOV, CPR-AR-ADULT]</sub>
- [ ] ☎ Ligue para a emergência assim que alguém não responder e não respirar normalmente, e fique na linha: o atendente ajuda você com a RCP. Se houver outra pessoa, peça para ela ligar enquanto você começa as compressões.  <sub>[CPR-SJA-CALL, CPR-RCUK-CALL, CPR-AR-ADULT]</sub>

**ES: Adulto que no responde y no respira con normalidad (RCP)**

- [ ] 1. Compruebe si responde: sacuda sus hombros con suavidad y pregúntele en voz alta si está bien. Incline la cabeza hacia atrás, levante el mentón y observe si respira con normalidad durante hasta 10 segundos. Las bocanadas aisladas (jadeos) no son respiración normal.  <sub>[CPR-SJA-CHECK, CPR-BRC-GASP, CPR-RCUK-CALL, CPR-AR-ADULT]</sub>
- [ ] 2. Si no respira con normalidad, llame ya a emergencias y ponga el teléfono en altavoz para empezar de inmediato. Pida a alguien cercano que traiga un desfibrilador (DEA); no deje sola a la persona para ir a buscarlo.  <sub>[CPR-SJA-CALL, CPR-RCUK-CALL, CPR-HD-AED, CPR-AR-ADULT, CPR-CRAR]</sub>
- [ ] 3. Presione fuerte y rápido en el centro del pecho: el talón de una mano, la otra mano encima, los brazos rectos, unos 5 a 6 cm de profundidad, de 100 a 120 veces por minuto (unas 2 por segundo), dejando que el pecho vuelva a subir cada vez.  <sub>[CPR-SJA-PUSH, CPR-BRC-PUSH, CPR-RCUK-PUSH, CPR-MS-ADULT, CPR-AR-ADULT, CPR-CRAR]</sub>
- [ ] 4. Si está entrenado y dispuesto, dé 2 respiraciones boca a boca después de cada 30 compresiones (incline la cabeza, levante el mentón, tápele la nariz, cubra su boca con la suya y sople hasta que el pecho suba). Si no, siga con las compresiones sin parar.  <sub>[CPR-SJA-BREATHS, CPR-RCUK-BREATHS, CPR-BRC-BREATHS, CPR-HD-UNTIL]</sub>
- [ ] 5. Cuando llegue el desfibrilador, enciéndalo y siga sus instrucciones de voz; siga presionando mientras colocan los parches.  <sub>[CPR-BRC-AED, CPR-RCUK-AED, CPR-HD-AED, CPR-AR-ADULT]</sub>
- [ ] 6. No pare hasta que llegue la ayuda y tome el relevo, o hasta que la persona vuelva a respirar con normalidad. Si respira con normalidad, póngala de lado con la cabeza inclinada hacia atrás y siga comprobando su respiración.  <sub>[CPR-SJA-UNTIL, CPR-HD-UNTIL, CPR-BRC-RECOV, CPR-SJA-RECOV, CPR-AR-ADULT]</sub>
- [ ] ☎ Llame a emergencias en cuanto alguien no responda y no respire con normalidad, y no cuelgue: quien atiende le ayudará con la RCP. Si hay alguien más, pídale que llame mientras usted empieza las compresiones.  <sub>[CPR-SJA-CALL, CPR-RCUK-CALL, CPR-AR-ADULT, CPR-CRAR]</sub>

<details><summary>Sources quoted</summary>

- **CPR-AR-ADULT** Ministerio de Salud (AR), RCP en adultos: "Llamá al número de emergencias o pedí a otra persona que lo haga. / Comprimí hacia abajo el torax de la persona hasta hundirlo entre 5 a 6 cm. / Apoyá el talón de una mano en el centro inferior del esternón. Colocá el talón de la otra mano sobre la primera y entrelaza tus dedos. / Tenés que hacer entre 100 y 120 compresiones por minuto. / Si contás con este equipo encendelo y seguí sus instrucciones. / Si la persona recupera la conciencia, colocala de costado o posición de recuperación (lateral) hasta que llegue el equipo de emergencias." (https://www.argentina.gob.ar/salud/primerosauxilios/rcp/adultos) ok (page uses 'vos'; the card uses usted)
- **CPR-BRC-AED** British Red Cross, Unresponsive and not breathing when an AED is available: "3. Tell someone to get an AED as soon as possible. / 5. When the AED arrives open it and follow the voice prompts." (https://www.redcross.org.uk/first-aid/learn-first-aid/unresponsive-and-not-breathing-when-an-aed-is-available)
- **CPR-BRC-BREATHS** British Red Cross, First aid for someone who is unresponsive and not breathing: "If you feel able to give rescue breaths, you can do so after about 30 pushes on their chest. / However, giving chest compressions is the most important thing to do" (https://www.redcross.org.uk/first-aid/learn-first-aid/unresponsive-and-not-breathing)
- **CPR-BRC-GASP** British Red Cross, First aid for someone who is unresponsive and not breathing: "Sometimes when a person is unresponsive their breathing may become noisy or irregular, or they may be gasping. This is usually a sign that their heart is not working properly and you should start chest compressions." (https://www.redcross.org.uk/first-aid/learn-first-aid/unresponsive-and-not-breathing)
- **CPR-BRC-PUSH** British Red Cross, First aid for someone who is unresponsive and not breathing: "Give chest compressions by pushing firmly in the middle of the chest up and down. Push the chest hard and fast at a rate of 2 pushes per second. / Continue to push in this way until help arrives." (https://www.redcross.org.uk/first-aid/learn-first-aid/unresponsive-and-not-breathing)
- **CPR-BRC-RECOV** British Red Cross, First aid for someone who is unresponsive and breathing: "Step 2. If they are breathing, move them onto their side and tilt their head back. / Step 3. Call 999" (https://www.redcross.org.uk/first-aid/learn-first-aid/unresponsive-and-breathing)
- **CPR-CRAR** Cruz Roja Argentina, ¿Cómo hacer RCP?: "Llamar al servicio de emergencias médicas al 1-0-7 e informar que hay una persona inconsciente que no respira. / Frecuencia: de 100 a 120 compresiones por minuto. / Profundidad 5 cm aproximadamente." (https://cruzroja.org.ar/blog/como-hacer-rcp/)
- **CPR-HD-AED** healthdirect (Australian Government), How to perform CPR: "Attach an Automated External Defibrillator (AED) to the person if one is available. / Do not leave the person alone or stop compressions in order to get an AED. / Follow the voice prompts." (https://www.healthdirect.gov.au/how-to-perform-cpr)
- **CPR-HD-UNTIL** healthdirect (Australian Government), How to perform CPR: "the person recovers — they start moving, breathing normally, coughing or talking — then put them in the recovery position / If you can’t give breaths, doing compressions only without stopping may still save a life." (https://www.healthdirect.gov.au/how-to-perform-cpr)
- **CPR-MS-ADULT** Ministério da Saúde (BR), Protocolos de Suporte Básico de Vida, SAMU 192 (BC5, PCR/RCP em adultos): "Deprimir o tórax em pelo menos 5 cm (sem exceder 6 cm) e permitir o completo retorno entre as compressões; / Manter frequência de compressões em 100 a 120 compressões/min;" (https://www.gov.br/saude/pt-br/composicao/saes/samu-192/publicacoes/protocolo-de-suporte-basico-de-vida-1-2.pdf) ok (professional SAMU protocol, AHA 2015 basis; used for the depth/rate figures only)
- **CPR-RCUK-AED** Resuscitation Council UK, How to do CPR: "The ambulance call handler will tell you where the nearest automated external defibrillator (AED) is. If someone is with you, ask them to fetch it and bring it back. / If you have a defibrillator, switch it on and follow the instructions / If more than one rescuer is present, continue CPR while the pads are being attached." (https://www.resus.org.uk/public-resource/how-do-cpr)
- **CPR-RCUK-BREATHS** Resuscitation Council UK, How to do CPR: "If you have been trained to provide rescue breaths, alternate 30 chest compressions with 2 rescue breaths. / If you are not trained to provide rescue breaths, perform continuous chest compressions without interruptions." (https://www.resus.org.uk/public-resource/how-do-cpr)
- **CPR-RCUK-CALL** Resuscitation Council UK, How to do CPR: "Put the phone on loudspeaker and tell them you are with someone who has collapsed and is not responding. / The ambulance call handler will help you check for signs of normal breathing." (https://www.resus.org.uk/public-resource/how-do-cpr)
- **CPR-RCUK-PUSH** Resuscitation Council UK, How to do CPR: "Place your hands in the centre of the chest. / Push down hard and then release twice per second, and don’t stop." (https://www.resus.org.uk/public-resource/how-do-cpr)
- **CPR-SJA-BREATHS** St John Ambulance (UK), How to do CPR: "If you are trained to do so, after 30 compressions, provide two rescue breaths. If you are unable or unwilling to provide rescue breaths, give continuous chest compressions. / Tilt the casualty's head backwards, lift their chin, and pinch the soft part of their nose closed." (https://www.sja.org.uk/first-aid-advice/cpr/)
- **CPR-SJA-CALL** St John Ambulance (UK), How to do CPR: "If they are not breathing normally, ask a helper to call 999 or 112 for an ambulance while you start CPR. Ask a helper to find and bring a defibrillator, if available. / If you are on your own, use the hands-free speaker on a phone so you can start CPR while speaking to ambulance control. / Do not leave the casualty to look for a defibrillator yourself." (https://www.sja.org.uk/first-aid-advice/cpr/)
- **CPR-SJA-CHECK** St John Ambulance (UK), How to do CPR (the NHS CPR page redirects here): "Check if they respond by gently shaking their shoulders and asking them loudly, 'are you ok?'. / If they don't respond, shout for help and open their airway by gently tilting the casualty's head back and lifting their chin. / Look, listen, and feel for up to 10 seconds for normal breathing. Ignore occasional, irregular gasps - these are common in the early stages of cardiac arrest." (https://www.sja.org.uk/first-aid-advice/cpr/)
- **CPR-SJA-PUSH** St John Ambulance (UK), How to do CPR: "Kneel close to the casualty and put the heel of your hand on the middle of their chest. Put your other hand on top of your first hand and if you can, interlock your fingers. / Lean forwards so your shoulders are over your hands, keep your arms straight and press down hard, to a depth of about 5-6cm before releasing the pressure and allowing the chest to come back up. / Push at a rate of 100 to 120 per minute." (https://www.sja.org.uk/first-aid-advice/cpr/) CONFLICT (depth, minor): 5-6 cm (SJA, MS Brazil, Argentina) vs 'about a third' of the chest (healthdirect) vs '5 cm aproximadamente' (Cruz Roja Argentina)
- **CPR-SJA-RECOV** St John Ambulance (UK), How to put someone in the recovery position: "If it shows that they are unresponsive but breathing, put them in the recovery position. / Gently tilt the casualty’s head back and lift their chin to make sure their airway stays open." (https://www.sja.org.uk/first-aid-advice/recovery-position/)
- **CPR-SJA-UNTIL** St John Ambulance (UK), How to do CPR: "Keep alternating 30 compressions with two breaths (30:2) until: / emergency help arrives and takes over / the person starts showing signs of life and starts to breathe normally" (https://www.sja.org.uk/first-aid-advice/cpr/)

</details>

Sign-off: [ ] EN  [ ] PT  [ ] ES  [ ] clinical review done  · notes: ____

## cprchild: Child over 1 year not responding and not breathing normally (CPR)
Covers: REVIEWER-DECISIONS.md 'Additional cards' (CPR adult/child/infant); child CPR starts with 5 rescue breaths in UK guidance

**Decisions for the reviewer:** (1) ORDER (main decision): 5 rescue breaths first, then 30:2 (SJA, BRC, RCUK; also the drowning card) vs compressions first with no initial breaths (healthdirect/ANZCOR; MS Brazil SAMU protocol, AHA basis). The card follows the UK (5 breaths first: a child's arrest is usually breathing-related, SJA). Options: keep / compressions first / 'if you can't give breaths, start pushing'. (2) Lone rescuer: SJA = 5 breaths, then call on speaker; no speaker → 1 minute of CPR, then call (BRC: 1 minute). Argentina MS: 2 minutes. The card says 1 minute. (3) Age bound: RCUK 'child (aged 1-18)'; healthdirect: child technique only if the chest is too small for two hands, else adult CPR; AHA/MedlinePlus: up to puberty. The title says 'over 1 year'; the trigger routes 'kid/child/son/daughter' here, and teens with an adult build can follow the adult card. Accept 5 initial breaths for a teen (harmless) or route teens to the adult card? (4) Depth: 'about a third of the chest (about 5 cm)' (RCUK '5 cm', SJA/healthdirect 'a third', MS 'cerca de 5 cm'). One or two hands: all sources agree on size-dependent. (5) 15:2 ratio is for trained paediatric BLS only (SJA, RCUK); left out. (6) AED: 'switch it on and follow its voice instructions' (SJA child page); child pads/attenuator details (MS, healthdirect: adult AED is fine over 8; under 8 use child pads if available, else adult) left to the device and the call handler.

**EN: Child over 1 year not responding and not breathing normally (CPR)**

- [ ] 1. Check if the child responds: call their name and tap their shoulders. Tilt the head back slightly, lift the chin with two fingers and look for normal breathing for up to 10 seconds.  <sub>[CPR-BRC-CHILD-CHECK, CPR-RCUK-CHILD]</sub>
- [ ] 2. If they're not breathing normally, ask someone to call emergency services. If you're alone: give the 5 rescue breaths, then call on speaker and carry on; if you can't use a speaker, give 1 minute of CPR first, then call.  <sub>[CPR-SJA-CHILD-CALL, CPR-BRC-CHILD, CPR-RCUK-CHILD]</sub>
- [ ] 3. Give 5 rescue breaths: pinch the nose, seal your mouth over theirs and blow gently and steadily until the chest rises.  <sub>[CPR-SJA-CHILD-5, CPR-RCUK-CHILD-5, CPR-BRC-CHILD]</sub>
- [ ] 4. Then press down 30 times in the middle of the chest with the heel of one hand (two hands if the child is big or you're small): about a third of the chest's depth (about 5 cm), 100 to 120 times a minute.  <sub>[CPR-SJA-CHILD-PUSH, CPR-RCUK-CHILD-PUSH, CPR-BRC-CHILD, CPR-MS-PED, CPR-HD-CHILD]</sub>
- [ ] 5. Give 2 breaths, then keep repeating 30 presses and 2 breaths. If you can't give breaths, keep pressing without stopping.  <sub>[CPR-SJA-CHILD-REPEAT, CPR-BRC-CHILD]</sub>
- [ ] 6. If a defibrillator (AED) arrives, have someone switch it on and follow its voice instructions while you keep going. Carry on until help takes over or the child starts breathing normally; then turn them on their side and keep checking their breathing.  <sub>[CPR-SJA-CHILD-AED, CPR-SJA-CHILD-RECOV, CPR-BRC-CHILD]</sub>
- [ ] ☎ Call emergency services for any child who isn't responding and isn't breathing normally. Don't leave the child to make the call; stay on the line and follow the call handler's instructions.  <sub>[CPR-SJA-CHILD-CALL, CPR-RCUK-CHILD, CPR-BRC-CHILD]</sub>

**PT: Criança com mais de 1 ano que não responde e não respira normalmente (RCP)**

- [ ] 1. Veja se a criança responde: chame pelo nome e toque nos ombros. Incline a cabeça um pouco para trás, levante o queixo com dois dedos e observe a respiração por até 10 segundos.  <sub>[CPR-BRC-CHILD-CHECK, CPR-RCUK-CHILD]</sub>
- [ ] 2. Se ela não respira normalmente, peça a alguém que ligue para a emergência. Se estiver sozinho: faça as 5 respirações de resgate, depois ligue no viva-voz e continue; se não tiver viva-voz, faça 1 minuto de RCP antes de ligar.  <sub>[CPR-SJA-CHILD-CALL, CPR-BRC-CHILD, CPR-RCUK-CHILD]</sub>
- [ ] 3. Faça 5 respirações de resgate: tape o nariz, cubra a boca da criança com a sua e sopre devagar e de forma constante até o peito subir.  <sub>[CPR-SJA-CHILD-5, CPR-RCUK-CHILD-5, CPR-BRC-CHILD]</sub>
- [ ] 4. Depois pressione 30 vezes no meio do peito com a base de uma mão (as duas mãos se a criança for grande ou você for pequeno): cerca de um terço da altura do peito (uns 5 cm), de 100 a 120 vezes por minuto.  <sub>[CPR-SJA-CHILD-PUSH, CPR-RCUK-CHILD-PUSH, CPR-BRC-CHILD, CPR-MS-PED, CPR-HD-CHILD]</sub>
- [ ] 5. Faça 2 respirações e continue repetindo 30 compressões e 2 respirações. Se não conseguir fazer as respirações, continue as compressões sem parar.  <sub>[CPR-SJA-CHILD-REPEAT, CPR-BRC-CHILD]</sub>
- [ ] 6. Se chegar um desfibrilador (DEA), peça para alguém ligar o aparelho e seguir as instruções de voz enquanto você continua. Não pare até a equipe de socorro assumir ou a criança voltar a respirar normalmente; então vire-a de lado e continue verificando a respiração.  <sub>[CPR-SJA-CHILD-AED, CPR-SJA-CHILD-RECOV, CPR-BRC-CHILD]</sub>
- [ ] ☎ Ligue para a emergência para qualquer criança que não responde e não respira normalmente. Não deixe a criança sozinha para ligar; fique na linha e siga as instruções do atendente.  <sub>[CPR-SJA-CHILD-CALL, CPR-RCUK-CHILD, CPR-BRC-CHILD]</sub>

**ES: Niño mayor de 1 año que no responde y no respira con normalidad (RCP)**

- [ ] 1. Compruebe si el niño responde: llámelo por su nombre y tóquele los hombros. Incline la cabeza un poco hacia atrás, levante el mentón con dos dedos y observe si respira con normalidad durante hasta 10 segundos.  <sub>[CPR-BRC-CHILD-CHECK, CPR-RCUK-CHILD]</sub>
- [ ] 2. Si no respira con normalidad, pida a alguien que llame a emergencias. Si está solo: dé las 5 respiraciones de rescate, luego llame con el altavoz activado y siga; si no tiene altavoz, haga 1 minuto de RCP antes de llamar.  <sub>[CPR-SJA-CHILD-CALL, CPR-BRC-CHILD, CPR-RCUK-CHILD]</sub>
- [ ] 3. Dé 5 respiraciones de rescate: tápele la nariz, cubra su boca con la suya y sople de forma suave y constante hasta que el pecho suba.  <sub>[CPR-SJA-CHILD-5, CPR-RCUK-CHILD-5, CPR-BRC-CHILD]</sub>
- [ ] 4. Luego presione 30 veces en el centro del pecho con el talón de una mano (las dos manos si el niño es grande o usted es pequeño): alrededor de un tercio de la altura del pecho (unos 5 cm), de 100 a 120 veces por minuto.  <sub>[CPR-SJA-CHILD-PUSH, CPR-RCUK-CHILD-PUSH, CPR-BRC-CHILD, CPR-MS-PED, CPR-HD-CHILD]</sub>
- [ ] 5. Dé 2 respiraciones y siga repitiendo 30 compresiones y 2 respiraciones. Si no puede dar respiraciones, siga con las compresiones sin parar.  <sub>[CPR-SJA-CHILD-REPEAT, CPR-BRC-CHILD]</sub>
- [ ] 6. Si llega un desfibrilador (DEA), pida a alguien que lo encienda y siga sus instrucciones de voz mientras usted continúa. No pare hasta que la ayuda tome el relevo o el niño vuelva a respirar con normalidad; entonces póngalo de lado y siga comprobando su respiración.  <sub>[CPR-SJA-CHILD-AED, CPR-SJA-CHILD-RECOV, CPR-BRC-CHILD]</sub>
- [ ] ☎ Llame a emergencias por cualquier niño que no responda y no respire con normalidad. No deje solo al niño para llamar; no cuelgue y siga las instrucciones de quien atiende.  <sub>[CPR-SJA-CHILD-CALL, CPR-RCUK-CHILD, CPR-BRC-CHILD]</sub>

<details><summary>Sources quoted</summary>

- **CPR-BRC-CHILD** British Red Cross, First aid for a child who is unresponsive and not breathing: "2. If they are not breathing, tell someone to call 999. / If you are on your own, call 999 after you’ve spent one minute giving them rescue breaths and chest compressions. / 3. Give five rescue breaths. / Give 30 chest compressions by pushing firmly in the middle of their chest up and down with one hand. / If you are small or the child is large, you may need to use two hands. / Continue with cycles of 30 chest compressions and two rescue breaths until help arrives. / If you can’t give rescue breaths for any reason, just give chest compressions." (https://www.redcross.org.uk/first-aid/learn-first-aid-for-babies-and-children/unresponsive-not-breathing-child)
- **CPR-BRC-CHILD-CHECK** British Red Cross, First aid for a child who is unresponsive and not breathing: "A child who is unresponsive won't answer or move if you call their name or tap their shoulders. Shout for help. / Do this for no more than ten seconds." (https://www.redcross.org.uk/first-aid/learn-first-aid-for-babies-and-children/unresponsive-not-breathing-child)
- **CPR-HD-CHILD** healthdirect (Australian Government), How to perform CPR: children over 1 year: "Use these instructions only if the child's chest is too small for you to use both hands to do chest compressions. Otherwise, use the instructions for adult CPR above. / Place the heel of one hand on the lower half of breastbone, in the centre of the child’s chest (use one or 2 hands depending on the size of the child and your own strength). / Keeping your arm or arms straight, press straight down on their chest by one third of the chest depth. / Push down fast at a rate of 100 to 120 compressions per minute. / CPR for children over 1 year old: Give 30 compressions followed by 2 breaths." (https://www.healthdirect.gov.au/how-to-perform-cpr) CONFLICT (order): compressions first, no 5 initial breaths (vs SJA/BRC/RCUK)
- **CPR-MS-PED** Ministério da Saúde (BR), Protocolos de Suporte Básico de Vida, SAMU 192 (BPed 7, PCR/RCP no bebê e na criança): "No bebê: comprimir o esterno com dois dedos posicionados imediatamente abaixo da linha intermamilar, deprimindo pelo menos 1/3 do diâmetro anteroposterior do tórax ou cerca de 4 cm; / Na criança: realizar compressões com uma ou duas mãos posicionadas na metade inferior do esterno, deprimindo pelo menos 1/3 do diâmetro anteroposterior do tórax ou cerca de 5 cm;" (https://www.gov.br/saude/pt-br/composicao/saes/samu-192/publicacoes/protocolo-de-suporte-basico-de-vida-1-2.pdf) ok (professional SAMU protocol; figures only)
- **CPR-RCUK-CHILD** Resuscitation Council UK, How to do CPR (child): "Check for danger, then immediately follow these steps to give a child (aged 1-18) CPR. / Put the phone on loudspeaker and tell them you are with a child who is not responding. / Open the child's airway by lifting the chin with two fingers and tilting the head back slightly so it's in the 'sniffing' position." (https://www.resus.org.uk/public-resource/how-do-cpr) AGE: RCUK child = 1-18 years; AHA/MedlinePlus use puberty as the upper bound (MedlinePlus not quoted, see SOURCES.raw-6.md)
- **CPR-RCUK-CHILD-5** Resuscitation Council UK, How to do CPR (child): "Pinch their nose and cover their mouth with your mouth to create a seal. / Blow into their mouth for one second, just enough to see their chest rise, then release and watch their chest fall. / Repeat this five times." (https://www.resus.org.uk/public-resource/how-do-cpr)
- **CPR-RCUK-CHILD-PUSH** Resuscitation Council UK, How to do CPR (child): "Place the heel of your hand in the centre of the chest; for larger children, you may need to use two hands. / Push down about a third of the depth of the chest (5 cm), then release. / Repeat chest compressions 30 times, twice per second." (https://www.resus.org.uk/public-resource/how-do-cpr)
- **CPR-SJA-CHILD-5** St John Ambulance (UK), How to do CPR on a child: "Give five initial rescue breaths. / Blow into their mouth gently and steadily for up to one second, until the chest rises. / It is vital that you perform rescue breaths as a cardiac arrest in a child is likely caused by a respiratory problem." (https://www.sja.org.uk/first-aid-advice/child-cpr/) CONFLICT (order): 5 breaths first (SJA, BRC, RCUK) vs compressions first, no initial breaths (healthdirect; MS Brazil SAMU protocol)
- **CPR-SJA-CHILD-AED** St John Ambulance (UK), How to do CPR on a child: "If the helper returns with a defibrillator, ask them to switch it on and take the pads out while you continue with CPR. / The defibrillator will give voice prompts on what to do" (https://www.sja.org.uk/first-aid-advice/child-cpr/)
- **CPR-SJA-CHILD-CALL** St John Ambulance (UK), How to do CPR on a child: "If you are on your own, you need to give five rescue breaths first, then dial 999 or 112 on a speaker phone and start chest compressions. If you don't have a speaker phone, give one minute of CPR before calling 999 or 112. / Do not leave the child to make the call or to look for a defibrillator, unless you do not have a mobile phone and there is no help available." (https://www.sja.org.uk/first-aid-advice/child-cpr/) CONFLICT (lone rescuer): 1 minute of CPR before calling without a speaker (SJA, BRC) vs 2 minutes (Argentina, baby/child page)
- **CPR-SJA-CHILD-PUSH** St John Ambulance (UK), How to do CPR on a child: "Kneel by the child and put one hand in the centre of the child’s chest. / Push down a third of the depth of the chest. / Repeat this 30 times at a rate of 100 to 120 compressions per minute." (https://www.sja.org.uk/first-aid-advice/child-cpr/)
- **CPR-SJA-CHILD-RECOV** St John Ambulance (UK), How to do CPR on a child: "If the child shows signs of becoming responsive such as coughing, opening eyes, speaking, and starts to breathe normally, put them in the recovery position. Monitor their level of response and prepare to give CPR again if necessary." (https://www.sja.org.uk/first-aid-advice/child-cpr/)
- **CPR-SJA-CHILD-REPEAT** St John Ambulance (UK), How to do CPR on a child: "After 30 compressions, open the airway and give two breaths. / Keep alternating 30 compressions with two breaths (30:2) until:" (https://www.sja.org.uk/first-aid-advice/child-cpr/) ok (15:2 is for trained paediatric BLS only; left out)

</details>

Sign-off: [ ] EN  [ ] PT  [ ] ES  [ ] clinical review done  · notes: ____

## cprinfant: Baby under 1 year not responding and not breathing normally (CPR)
Covers: REVIEWER-DECISIONS.md 'Additional cards': infant CPR differs (two fingers, cover mouth and nose); the chokinginfant card's 'start CPR' points here

**Decisions for the reviewer:** (1) Technique: two fingers in the centre of the chest (SJA, BRC, healthdirect, MS Brazil; reviewer decision infant-thrusts for the choking card) vs two-thumb encircling (RCUK 2025 public page; Argentina 'Técnica B'). The card says two fingers. Options: keep / thumbs / both ('two fingers, or both thumbs with your hands around the chest'). (2) Order: 5 breaths first (SJA, BRC, RCUK) vs compressions first (healthdirect; MS SAMU protocol). As on the child card. (3) AED: healthdirect says 'Do not use an AED on children under 1 year of age'; MS Brazil's SAMU protocol uses paediatric (else adult) pads in babies; UK lay pages don't exclude babies. The card says nothing about an AED (the call handler decides). Accept the omission? (4) Lone rescuer: 5 breaths, then call on speaker; no speaker → 1 minute of CPR, then call, taking the baby with you (SJA, BRC). Argentina: 2 minutes. The card says 1 minute. (5) Head tilt: 'very gently ... until their face is flat to the sky' (SJA), 'neutral position' (RCUK), 'very slightly' (healthdirect), 'no demasiado' (Argentina): all agree; the card adds 'tilting too far can block the airway' (Argentina). (6) Recovery position for a baby: 'on their side (for example along your forearm)' rests on healthdirect's 'place them down on your forearm in recovery position'; SJA/BRC only say 'recovery position'.

**EN: Baby under 1 year not responding and not breathing normally (CPR)**

- [ ] 1. Check if the baby responds: call them and tap the soles of their feet. Don't shake the baby.  <sub>[CPR-RCUK-BABY, CPR-HD-INFANT]</sub>
- [ ] 2. Lay the baby on their back on a firm surface. Tilt the head back only very slightly, until the face looks straight up, and lift the chin with one fingertip; tilting too far can block the airway. Look for normal breathing for up to 10 seconds.  <sub>[CPR-SJA-BABY-AIRWAY, CPR-RCUK-BABY, CPR-HD-INFANT, CPR-AR-BEBE, CPR-BRC-BABY]</sub>
- [ ] 3. If the baby isn't breathing normally, ask someone to call emergency services. If you're alone: give the 5 rescue breaths, then call on speaker; with no speaker, give 1 minute of CPR first, then call, taking the baby with you.  <sub>[CPR-SJA-BABY-CALL, CPR-BRC-BABY-CALL, CPR-RCUK-BABY]</sub>
- [ ] 4. Give 5 rescue breaths: cover the baby's mouth and nose with your mouth and blow gently, just enough to make the chest rise.  <sub>[CPR-SJA-BABY-5, CPR-RCUK-BABY-5, CPR-BRC-BABY, CPR-AR-BEBE]</sub>
- [ ] 5. Then press 30 times with two fingers in the centre of the chest, about a third of its depth (about 4 cm), 100 to 120 times a minute, letting the chest come back up fully.  <sub>[CPR-SJA-BABY-PUSH, CPR-BRC-BABY, CPR-HD-INFANT, CPR-MS-PED, CPR-AR-BEBE]</sub>
- [ ] 6. Give 2 gentle breaths and keep repeating 30 presses and 2 breaths until help takes over or the baby starts breathing normally. If the baby starts breathing normally, hold them on their side (for example along your forearm) and keep checking their breathing.  <sub>[CPR-SJA-BABY-REPEAT, CPR-BRC-BABY, CPR-HD-INFANT]</sub>
- [ ] ☎ Call emergency services for any baby who isn't responding and isn't breathing normally. Don't leave the baby to make the call; stay on the line and follow the call handler's instructions.  <sub>[CPR-SJA-BABY-CALL, CPR-RCUK-BABY, CPR-BRC-BABY-CALL]</sub>

**PT: Bebê com menos de 1 ano que não responde e não respira normalmente (RCP)**

- [ ] 1. Veja se o bebê responde: chame e toque na sola dos pés. Não sacuda o bebê.  <sub>[CPR-RCUK-BABY, CPR-HD-INFANT]</sub>
- [ ] 2. Deite o bebê de costas numa superfície firme. Incline a cabeça para trás só um pouquinho, até o rosto ficar virado para cima, e levante o queixo com a ponta de um dedo; inclinar demais pode fechar a passagem do ar. Observe a respiração por até 10 segundos.  <sub>[CPR-SJA-BABY-AIRWAY, CPR-RCUK-BABY, CPR-HD-INFANT, CPR-AR-BEBE, CPR-BRC-BABY]</sub>
- [ ] 3. Se o bebê não respira normalmente, peça a alguém que ligue para a emergência. Se estiver sozinho: faça as 5 respirações de resgate e depois ligue no viva-voz; sem viva-voz, faça 1 minuto de RCP antes de ligar, levando o bebê com você.  <sub>[CPR-SJA-BABY-CALL, CPR-BRC-BABY-CALL, CPR-RCUK-BABY]</sub>
- [ ] 4. Faça 5 respirações de resgate: cubra a boca e o nariz do bebê com a sua boca e sopre de leve, só o bastante para o peito subir.  <sub>[CPR-SJA-BABY-5, CPR-RCUK-BABY-5, CPR-BRC-BABY, CPR-AR-BEBE]</sub>
- [ ] 5. Depois pressione 30 vezes com dois dedos no centro do peito, cerca de um terço da altura do peito (uns 4 cm), de 100 a 120 vezes por minuto, deixando o peito voltar totalmente.  <sub>[CPR-SJA-BABY-PUSH, CPR-BRC-BABY, CPR-HD-INFANT, CPR-MS-PED, CPR-AR-BEBE]</sub>
- [ ] 6. Faça 2 respirações leves e continue repetindo 30 compressões e 2 respirações até a equipe de socorro assumir ou o bebê voltar a respirar normalmente. Se ele voltar a respirar normalmente, segure-o de lado (por exemplo, apoiado no seu antebraço) e continue verificando a respiração.  <sub>[CPR-SJA-BABY-REPEAT, CPR-BRC-BABY, CPR-HD-INFANT]</sub>
- [ ] ☎ Ligue para a emergência para qualquer bebê que não responde e não respira normalmente. Não deixe o bebê sozinho para ligar; fique na linha e siga as instruções do atendente.  <sub>[CPR-SJA-BABY-CALL, CPR-RCUK-BABY, CPR-BRC-BABY-CALL]</sub>

**ES: Bebé menor de 1 año que no responde y no respira con normalidad (RCP)**

- [ ] 1. Compruebe si el bebé responde: llámelo y tóquele las plantas de los pies. No sacuda al bebé.  <sub>[CPR-RCUK-BABY, CPR-HD-INFANT]</sub>
- [ ] 2. Acueste al bebé boca arriba sobre una superficie firme. Incline la cabeza hacia atrás solo un poquito, hasta que la cara mire hacia arriba, y levante el mentón con la punta de un dedo; inclinarla demasiado puede cerrar el paso del aire. Observe si respira con normalidad durante hasta 10 segundos.  <sub>[CPR-SJA-BABY-AIRWAY, CPR-RCUK-BABY, CPR-HD-INFANT, CPR-AR-BEBE, CPR-BRC-BABY]</sub>
- [ ] 3. Si el bebé no respira con normalidad, pida a alguien que llame a emergencias. Si está solo: dé las 5 respiraciones de rescate y luego llame con el altavoz activado; sin altavoz, haga 1 minuto de RCP antes de llamar, llevando al bebé con usted.  <sub>[CPR-SJA-BABY-CALL, CPR-BRC-BABY-CALL, CPR-RCUK-BABY]</sub>
- [ ] 4. Dé 5 respiraciones de rescate: cubra la boca y la nariz del bebé con su boca y sople suavemente, solo lo necesario para que el pecho suba.  <sub>[CPR-SJA-BABY-5, CPR-RCUK-BABY-5, CPR-BRC-BABY, CPR-AR-BEBE]</sub>
- [ ] 5. Luego presione 30 veces con dos dedos en el centro del pecho, alrededor de un tercio de la altura del pecho (unos 4 cm), de 100 a 120 veces por minuto, dejando que el pecho vuelva a subir del todo.  <sub>[CPR-SJA-BABY-PUSH, CPR-BRC-BABY, CPR-HD-INFANT, CPR-MS-PED, CPR-AR-BEBE]</sub>
- [ ] 6. Dé 2 respiraciones suaves y siga repitiendo 30 compresiones y 2 respiraciones hasta que la ayuda tome el relevo o el bebé vuelva a respirar con normalidad. Si vuelve a respirar con normalidad, sosténgalo de lado (por ejemplo, apoyado en su antebrazo) y siga comprobando su respiración.  <sub>[CPR-SJA-BABY-REPEAT, CPR-BRC-BABY, CPR-HD-INFANT]</sub>
- [ ] ☎ Llame a emergencias por cualquier bebé que no responda y no respire con normalidad. No deje solo al bebé para llamar; no cuelgue y siga las instrucciones de quien atiende.  <sub>[CPR-SJA-BABY-CALL, CPR-RCUK-BABY, CPR-BRC-BABY-CALL]</sub>

<details><summary>Sources quoted</summary>

- **CPR-AR-BEBE** Ministerio de Salud (AR), RCP en bebés y niños: "Cubrí firmemente con tu boca, la boca y nariz del bebé. / Colocá los dedos índice y medio en el centro del esternón, entre los pezones, sin presionar en el extremo del esternón. / Aplicá presión hacia abajo, comprimiendo 4 cm de profundidad. / Incliná la cabeza del bebé, no demasiado hacia atrás ya que una inclinación exagerada, puede cerrar la vía del aire en lugar de abrirla." (https://www.argentina.gob.ar/salud/primerosauxilios/rcp/bebes) ok ('Técnica A'; the page also gives two-thumb 'Técnica B')
- **CPR-BRC-BABY** British Red Cross, First aid for a baby who is unresponsive and not breathing: "Tilt their head back slightly - is their chest moving? Look, listen and feel for breaths. / Step 3. Give five rescue breaths: tilt their head back, seal your mouth over their mouth and nose. Blow five times into the baby. / Step 4. Give 30 chest compressions: push firmly in the middle of their chest with two fingers so that the chest goes inward, then release. / Step 5. Give two rescue breaths. Continue with cycles of 30 chest compressions and two rescue breaths until help arrives." (https://www.redcross.org.uk/first-aid/learn-first-aid-for-babies-and-children/unresponsive-and-not-breathing-baby)
- **CPR-BRC-BABY-CALL** British Red Cross, First aid for a baby who is unresponsive and not breathing: "Step 2. If they are not breathing, tell someone to call 999. / If you are on your own, call 999 after you’ve spent one minute giving them rescue breaths and chest compressions." (https://www.redcross.org.uk/first-aid/learn-first-aid-for-babies-and-children/unresponsive-and-not-breathing-baby)
- **CPR-HD-INFANT** healthdirect (Australian Government), How to perform CPR: infants under 1 year: "Do not shake the infant. / Place 2 fingers on the lower half of the breastbone in the middle of the chest. / Press down on their chest by one-third deep (you may need to use one hand to do CPR depending on the size of the infant). / Tilt the infant’s head back very slightly. / Take a breath and cover the infant’s mouth and nose with your mouth, ensuring a good seal. / If the infant is breathing, place them down on your forearm in recovery position. Monitor their airway, breathing and responsiveness." (https://www.healthdirect.gov.au/how-to-perform-cpr)
- **CPR-MS-PED** Ministério da Saúde (BR), Protocolos de Suporte Básico de Vida, SAMU 192 (BPed 7, PCR/RCP no bebê e na criança): "No bebê: comprimir o esterno com dois dedos posicionados imediatamente abaixo da linha intermamilar, deprimindo pelo menos 1/3 do diâmetro anteroposterior do tórax ou cerca de 4 cm; / Na criança: realizar compressões com uma ou duas mãos posicionadas na metade inferior do esterno, deprimindo pelo menos 1/3 do diâmetro anteroposterior do tórax ou cerca de 5 cm;" (https://www.gov.br/saude/pt-br/composicao/saes/samu-192/publicacoes/protocolo-de-suporte-basico-de-vida-1-2.pdf) ok (professional SAMU protocol; figures only)
- **CPR-RCUK-BABY** Resuscitation Council UK, How to do CPR (baby): "Check for danger, then immediately follow these steps to give a baby (aged 0-12 months) CPR. / Call the baby's name and tap the bottom of their feet to see if they respond. / Put the phone on loudspeaker and tell them you are with a baby who is not responding. / Open the baby's airway by lifting the chin with two fingers and tilting the head back so that it's in a neutral position (not too close to the chest, and not too arched). / Do this for no longer than 10 seconds." (https://www.resus.org.uk/public-resource/how-do-cpr)
- **CPR-RCUK-BABY-5** Resuscitation Council UK, How to do CPR (baby): "Cover the baby's mouth and nose with your mouth to create a seal. / Blow into their mouth and nose for one second, just enough to see their chest rise, then release and watch their chest fall." (https://www.resus.org.uk/public-resource/how-do-cpr)
- **CPR-SJA-BABY-5** St John Ambulance (UK), How to do CPR on a baby: "Give five initial breaths. Take a breath and put your mouth around the baby’s mouth and nose to make a seal and blow gently and steadily for up to one second. The chest should rise." (https://www.sja.org.uk/first-aid-advice/baby-cpr/)
- **CPR-SJA-BABY-AIRWAY** St John Ambulance (UK), How to do CPR on a baby: "Place the baby on a firm surface and open their airway. To do this, place one hand on their forehead and very gently tilt their head back until their face is flat to the sky. With your other hand, use your fingertip and gently lift the chin." (https://www.sja.org.uk/first-aid-advice/baby-cpr/)
- **CPR-SJA-BABY-CALL** St John Ambulance (UK), How to do CPR on a baby: "If you're on your own and have a speaker phone, give five rescue breaths and then call 999 or 112. Continue CPR as directed by emergency medical advisor. / If you're on your own without a speaker phone, you need to give five rescue breaths and one minute of CPR before calling 999 or 112 for an ambulance. / Do not leave the baby to make the call. / If you do not have access to a phone, give five rescue breaths and do one minute of CPR and then go for help, taking the baby with you." (https://www.sja.org.uk/first-aid-advice/baby-cpr/)
- **CPR-SJA-BABY-PUSH** St John Ambulance (UK), How to do CPR on a baby: "Put two fingers in the centre of the baby’s chest and push down a third of the depth of the chest (about 4cm). Release the pressure allowing the chest to come back up fully. / Repeat this 30 times at a rate of 100 to 120 pumps per minute." (https://www.sja.org.uk/first-aid-advice/baby-cpr/) CONFLICT (technique): two fingers (SJA, BRC, healthdirect, MS Brazil) vs two-thumb encircling (RCUK 2025; Argentina 'Técnica B')
- **CPR-SJA-BABY-REPEAT** St John Ambulance (UK), How to do CPR on a baby: "After 30 pumps, open the airway and give two puffs. Keep alternating 30 pumps with two puffs (30:2) until: / emergency help arrives and takes over / the baby starts showing signs of life and starts to breathe normally. / If the baby shows signs of becoming responsive, like coughing, opening their eyes, making a noise, or starts to breathe normally, put them in the recovery position." (https://www.sja.org.uk/first-aid-advice/baby-cpr/)

</details>

Sign-off: [ ] EN  [ ] PT  [ ] ES  [ ] clinical review done  · notes: ____

## poisoning: Swallowed poison, medicine or chemical
Covers: REVIEWER-DECISIONS.md 'Additional cards' (poisoning: medicine, household chemical or plant swallowed). Not button batteries/coins/magnets (battery card), not CO (co card), not alcohol only, not food poisoning; eye splashes → eyechem card

**Decisions for the reviewer:** (1) Drinks (main decision): NHS, SJA, BRC = nothing to eat or drink; CIATox-ES (BR) = no water, milk or other liquid unless a CIATox tells you; Cruz Roja AR = 'no beber nada'; poison.org (US) = a small amount of water or milk at once if the product is caustic and the person is awake and can swallow. The card follows the conservative common ground ('not even water or milk, unless the poison centre or emergency service tells you'). Options: keep / add the poison.org caustic exception as an ALTERNATIVE. (2) Who to call: the UK sends every suspected swallowed poison to 999/A&E (NHS, BRC 'call 999 anyway, even if they seem fine'); healthdirect/poison.org/CIATox/Argentina route no-symptom cases to the poison line. The card says 'emergency services or a poison centre now, even if they seem fine' and puts emergency first in the call line. No numbers: 'many countries have a poison information line' is a generalisation from 4 countries (AU, US, BR, AR) and has no single source. (3) Skin: 'protect your hands, take off soaked clothing, rinse with lots of cool running water' (healthdirect, poison.org, CIATox-ES). Duration left out (poison.org 'at least 15 minutes'; the eye card uses 20). Add '15 minutes'? (4) Eyes: the card points to the eyechem card instead of repeating it (only 'start rinsing right away'). (5) Unresponsive: side position if breathing (NHS, CIATox-ES 'posição lateral'), CPR if not (NHS, SJA) with a pointer to the CPR card. (6) Left out on purpose: activated charcoal, ipecac, antidotes, naloxone (MedlinePlus mentions naloxone for opioids; not quoted, see SOURCES.raw-6.md), and any dose. (7) Checker: no v0.8.9 rule has a poisoning topic; the card's own rule list borrows battery-vomit and battery-wait (their patterns are generic). v0.9 candidates: poison-induce-vomit, poison-give-drink, undertriage-poison (REVIEW-6.md).

**EN: Swallowed poison, medicine or chemical**

- [ ] 1. Don't make them vomit: it can block their airway or burn the throat again.  <sub>[POIS-NHS-DONT, POIS-BRC, POIS-SJA, POIS-HD-FA, POIS-PC-HELP]</sub>
- [ ] 2. Don't give them anything to eat or drink, not even water or milk, unless the poison centre or emergency service tells you to.  <sub>[POIS-NHS-DONT, POIS-SJA, POIS-BRC, POIS-CIATOX-ES]</sub>
- [ ] 3. Find out what they swallowed, how much and when. Keep the container, label or packaging (or take a photo of it) to show the poison centre or the ambulance team. Wipe any of it off the mouth and face.  <sub>[POIS-BRC, POIS-SJA, POIS-HD-FA, POIS-NHS-DO, POIS-CIATOX-ES-GEN]</sub>
- [ ] 4. Call emergency services or a poison centre now, even if they seem fine; don't wait for symptoms. Many countries have a poison information line.  <sub>[POIS-BRC, POIS-HD-CALL, POIS-PC-HELP, POIS-SJA]</sub>
- [ ] 5. If they stop responding but are breathing, turn them on their side and keep checking their breathing. If they're not breathing normally, start CPR (see the CPR card).  <sub>[POIS-NHS-DO, POIS-SJA, POIS-CIATOX-ES-GEN]</sub>
- [ ] 6. If it's on the skin, protect your hands, take off soaked clothing and rinse the skin with lots of cool running water. If it's in the eyes, use the chemical-in-the-eye card and start rinsing right away.  <sub>[POIS-HD-FA, POIS-PC-SKIN, POIS-CIATOX-ES-GEN]</sub>
- [ ] ☎ Call emergency services now if they may have swallowed something harmful, and straight away if they're very drowsy or not responding, have trouble breathing, or have a seizure (fit).  <sub>[POIS-NHS-999, POIS-HD-CALL, POIS-PC-HELP]</sub>

**PT: Engoliu veneno, remédio ou produto químico**

- [ ] 1. Não provoque vômito: isso pode bloquear a respiração ou queimar a garganta de novo.  <sub>[POIS-NHS-DONT, POIS-BRC, POIS-SJA, POIS-HD-FA, POIS-CIATOX-ES]</sub>
- [ ] 2. Não dê nada para comer ou beber, nem água nem leite, a não ser que o centro de informação toxicológica (CIATox) ou a emergência mande.  <sub>[POIS-NHS-DONT, POIS-SJA, POIS-BRC, POIS-CIATOX-ES]</sub>
- [ ] 3. Descubra o que a pessoa engoliu, quanto e quando. Guarde a embalagem, o rótulo ou o frasco (ou tire uma foto) para mostrar ao centro toxicológico ou à equipe de socorro. Limpe o que ficou na boca e no rosto.  <sub>[POIS-BRC, POIS-SJA, POIS-HD-FA, POIS-NHS-DO, POIS-CIATOX-ES-GEN]</sub>
- [ ] 4. Ligue para a emergência ou para um centro de informação toxicológica agora, mesmo que a pessoa pareça bem; não espere aparecerem sintomas. Muitos países têm uma linha de informação sobre intoxicações.  <sub>[POIS-BRC, POIS-HD-CALL, POIS-PC-HELP, POIS-SJA]</sub>
- [ ] 5. Se ela parar de responder mas estiver respirando, vire-a de lado e continue verificando a respiração. Se não respirar normalmente, comece a RCP (veja o cartão de RCP).  <sub>[POIS-NHS-DO, POIS-SJA, POIS-CIATOX-ES-GEN]</sub>
- [ ] 6. Se o produto caiu na pele, proteja as mãos, tire a roupa molhada com ele e lave a pele com bastante água corrente fria. Se caiu nos olhos, use o cartão de produto químico no olho e comece a lavar já.  <sub>[POIS-HD-FA, POIS-PC-SKIN, POIS-CIATOX-ES-GEN]</sub>
- [ ] ☎ Ligue para a emergência agora se a pessoa pode ter engolido algo perigoso, e imediatamente se estiver muito sonolenta ou não responder, tiver dificuldade para respirar ou tiver uma convulsão.  <sub>[POIS-NHS-999, POIS-HD-CALL, POIS-PC-HELP]</sub>

**ES: Tragó veneno, medicamento o producto químico**

- [ ] 1. No provoque el vómito: puede bloquearle la respiración o volver a quemarle la garganta.  <sub>[POIS-NHS-DONT, POIS-BRC, POIS-SJA, POIS-HD-FA, POIS-CRAR]</sub>
- [ ] 2. No le dé nada de comer ni de beber, ni siquiera agua o leche, salvo que se lo indique el centro de toxicología o el servicio de emergencias.  <sub>[POIS-NHS-DONT, POIS-SJA, POIS-BRC, POIS-CIATOX-ES, POIS-CRAR]</sub>
- [ ] 3. Averigüe qué tragó, cuánto y cuándo. Guarde el envase, la etiqueta o el empaque (o tómele una foto) para mostrarlo al centro de toxicología o al equipo de emergencias. Limpie lo que haya quedado en la boca y la cara.  <sub>[POIS-BRC, POIS-SJA, POIS-HD-FA, POIS-NHS-DO, POIS-CRAR]</sub>
- [ ] 4. Llame ahora a emergencias o a un centro de toxicología, aunque la persona parezca estar bien; no espere a que aparezcan síntomas. Muchos países tienen una línea de información sobre intoxicaciones.  <sub>[POIS-BRC, POIS-HD-CALL, POIS-PC-HELP, POIS-CRAR]</sub>
- [ ] 5. Si deja de responder pero respira, póngala de lado y siga comprobando su respiración. Si no respira con normalidad, empiece la RCP (vea la tarjeta de RCP).  <sub>[POIS-NHS-DO, POIS-SJA, POIS-CIATOX-ES-GEN]</sub>
- [ ] 6. Si el producto cayó en la piel, protéjase las manos, quítele la ropa mojada con el producto y enjuague la piel con abundante agua corriente fresca. Si cayó en los ojos, use la tarjeta de producto químico en el ojo y empiece a enjuagar de inmediato.  <sub>[POIS-HD-FA, POIS-PC-SKIN, POIS-CIATOX-ES-GEN]</sub>
- [ ] ☎ Llame a emergencias ahora si pudo haber tragado algo dañino, y de inmediato si está muy somnolienta o no responde, tiene dificultad para respirar o tiene una convulsión.  <sub>[POIS-NHS-999, POIS-HD-CALL, POIS-PC-HELP]</sub>

<details><summary>Sources quoted</summary>

- **POIS-BRC** British Red Cross, First aid for someone who has swallowed something harmful: "1. If the person is responsive, find out what they have taken, when they took it and how much they took. / 2. Call 999. / Do not make the person sick. By making them sick, you can cause further damage to their throat or block their airway. / If they have swallowed something corrosive, the liquid will burn the throat on the way back up, causing more pain and distress. / Call 999 anyway, even if they seem to be showing no symptoms. / No, don’t give them anything to drink." (https://www.redcross.org.uk/first-aid/learn-first-aid/poisoning)
- **POIS-CIATOX-ES** CIATox-ES, Secretaria da Saúde do Espírito Santo (BR), Primeiros socorros em intoxicações (PDF): "Não provocar vômito; / Não oferecer água, leite ou qualquer outro líquido, a não ser que tenha sido orientado por um CIATox; / Encaminhar, com urgência, para serviço médico (pronto socorro ou hospital)." (https://ciatox.es.gov.br/Media/toxcen/Material%20Informativo/usuarios/primeiros%20socorros%20-%20revisado.pdf) ok (state poison centre, part of the national CIATox network)
- **POIS-CIATOX-ES-GEN** CIATox-ES, Secretaria da Saúde do Espírito Santo (BR), Primeiros socorros em intoxicações (PDF): "Transportar a vítima em posição lateral, a fim de evitar aspiração de vômito, se ocorrer. / Transportar junto, restos da substância, recipientes, embalagens e aplicadores. / Lavar abundantemente o local afetado com água corrente;" (https://ciatox.es.gov.br/Media/toxcen/Material%20Informativo/usuarios/primeiros%20socorros%20-%20revisado.pdf)
- **POIS-CRAR** Cruz Roja Argentina, ¿Qué hacer ante una intoxicación?: "Identificar el tipo de tóxico y la cantidad ingerida. / Llamar al Centro Nacional de Intoxicaciones / Llamar al servicio de emergencias médicas o trasladar al hospital. / Evitar provocar el vómito. / Se aconseja no beber nada. En caso de vómito espontáneo, guardarlo en un contenedor y llevarlo para su posterior análisis." (https://cruzroja.org.ar/blog/que-hacer-ante-una-intoxicacion/)
- **POIS-HD-CALL** healthdirect (Australian Government), Poisoning: "Call triple zero (000) if someone stops breathing, collapses, has a seizure, has a severe allergic reaction (anaphylaxis) or has been exposed to a harmful substance. / If there are no symptoms, call the Poisons Information Centre on 13 11 26. You can call 24 hours a day from anywhere in Australia. / There is no need to wait until symptoms appear." (https://www.healthdirect.gov.au/poisoning) ok (national number quoted as evidence that poison lines exist; no number goes on a card)
- **POIS-HD-FA** healthdirect (Australian Government), Poisoning: "Do NOT induce vomiting — it can cause more harm. / Wash any substance off the mouth or face. / Ask what poison is involved and take a photo of the bottle or packet. / Don’t touch the chemical or exposed area yourself. Use protective clothing such as gloves and goggles. / Remove any affected clothes. / Flood the skin with cool running water." (https://www.healthdirect.gov.au/poisoning)
- **POIS-NHS-999** NHS, Poisoning: [NHS quote withheld] (https://www.nhs.uk/conditions/poisoning/)
- **POIS-NHS-DO** NHS, Poisoning: [NHS quote withheld] (https://www.nhs.uk/conditions/poisoning/)
- **POIS-NHS-DONT** NHS, Poisoning: [NHS quote withheld] (https://www.nhs.uk/conditions/poisoning/)
- **POIS-PC-HELP** Poison Control, National Capital Poison Center (US), First aid guidelines: "Call your poison center at 1-800-222-1222 for help. / If the individual collapses, has a seizure, has trouble breathing, or can't be awakened: Call 911 IMMEDIATELY. / Do not induce vomiting. Ipecac syrup is no longer recommended." (https://www.poison.org/first-aid-for-poisonings) ok (US number quoted as evidence only)
- **POIS-PC-SKIN** Poison Control, National Capital Poison Center (US), First aid guidelines: "Remove contaminated clothing first (that's clothing with a spill). / Use lots of room temperature running water and rinse for at least 15 minutes. / It's important to irrigate (rinse) the exposed eyes, immediately." (https://www.poison.org/first-aid-for-poisonings) ok (skin: 15 min; eye card uses 20 min, NHS)
- **POIS-SJA** St John Ambulance (UK), Swallowed poisons: "If the person is responsive, ask them what they have swallowed, when, and how much. / Call 999 or 112 for emergency help and give them as much information as possible. If you can, keep any packaging or labels to show the emergency services. Keep checking their breathing and response. / Do not try to make them vomit. / Do not give the casualty anything to eat or drink. / If they become unresponsive, open their airway, check their breathing, and prepare to give CPR." (https://www.sja.org.uk/get-advice/first-aid-advice/poisoning/swallowed-poisons/)

</details>

Sign-off: [ ] EN  [ ] PT  [ ] ES  [ ] clinical review done  · notes: ____

## Before anything ships
- Reviewer decisions above (r6-*), then a clinical review: **these are the highest-stakes cards in the set**. A first-aid trainer should read the 3 CPR cards against current ERC/AHA lay guidance.
- Native PT-BR and ES review (ES = usted, Latin-American neutral: 'altavoz', 'talón de la mano', 'no cuelgue').
- Licence: NHS rows under OGL attribution; SJA/BRC/RCUK/healthdirect/poison.org/Cruz Roja = facts only; MedlinePlus question (r6-medlineplus).
