# First-aid cards: independent reviewer decisions (opus-reviewer, 2026-10-03)

TL;DR: all **39 decisions** made, and the **31 cards** reviewed: **6 approved, 25 changed, 0 rejected**. ES register = **usted** everywhere (8 fixed strings (plus their tests) change). This review replaces human review by r4to's decision. It was done by an AI model, so the residual-risk list at the end matters. Input: `conditionCards.v1.json` sha256 `bfdaeec4…` (re-read after Compass's rip-current source update; card text unchanged). Machine-readable twin: `REVIEWER-DECISIONS.json`. The choices are also recorded on the review artifact (collections `decisions`, `cards`).

Principles: safe across countries and for a stressed lay bystander. Where sources conflict, the more conservative or region-neutral wording wins. No drug dosing unless every source agrees. Every card says when to call. Card changes are conservative (more calling or escalation, less doing); unsourced additions are flagged.

## Top 5 changes
1. drowning: rescue-breath steps are now conditional on 'not breathing normally', with a recovery-position step for a breathing person. The trigger fires on any 'pulled from the water', so a breathing, coughing child would otherwise get rescue-breath instructions.
2. electric: the broom-handle step is limited to household electricity. For downed or high-voltage lines: don't approach, stay 10 m away, call. As written, a bystander could try it near a high-voltage line.
3. headinjury + chokinginfant (+ stroke): added the missing 'not responding and not breathing normally → call + CPR' step; head injury now treats vomiting more than once as an emergency.
4. ES register → usted everywhere. 8 fixed strings (plus their tests) change, including the ES_EMERGENCY line appended to every ES card, which made each ES card end in tú after a usted body.
5. PT: inline 'SAMU 192' / 'Bombeiros 193' removed from 8 PT cards, so Brazilians abroad aren't told to dial 192. The engine's appended line still gives 192/193 and becomes country-aware when the user names the country. Plus under-triage fixes: eyechem (any chemical → emergency), nosebleed/animalbite/tsunami/earthquake (explicit call lines), and hypoglycemia (not diet/zero drinks).

## Decisions (39)
Choice = the page's option id; `neither` = none of the page's options (the replacement is in the rationale).

| id | card | choice | rationale |
|---|---|---|---|
| `battery-honey` | battery | **keep** (Manter fora (como está)) | Leave honey out. It is a dose (10 mL every 10 min) from one source (poison.org); CAPT/NHS omit it and put getting to the ED first. Rule: no dosing unless every allowed source agrees; it must never delay transport. |
| `scorpion-compress` | scorpion | **keep** (Manter fora (como está)) | Leave both out. CDC/MedlinePlus (ice) and Brazil MS/SES-SP (warm, no ice) directly conflict; neither changes outcome, and the child card's job is getting to care fast. |
| `drowning-upside-down` | drowning | **keep** (Manter o texto com fonte) | Keep the sourced line ('don't try to get water out or press on the stomach'; Saudi MOH, St John NSW). It answers the upside-down myth without adding an unsourced claim. |
| `drowning-breaths` | drowning | **keep** (Manter 5) | Keep 5 initial rescue breaths (St John UK, British Red Cross; same as ERC/RCUK drowning guidance). Drowning is a hypoxic arrest; 5 is the more oxygen-first option and is not harmful vs 2. |
| `infant-thrusts` | chokinginfant | **keep** (Manter dois dedos) | Keep two fingers just below the nipple line (NHS + British Red Cross; 2 of 3 sources). Simpler for a lay bystander than two-thumb encircling. |
| `hypo-insulin` | hypoglycemia | **keep** (Manter a linha) | Keep 'Don't give insulin'. Single source (St John NZ) but no allowed source contradicts it; it only removes a potentially fatal action and is the exact myth in vit-hm2-021. |
| `battery-coins` | battery | **keep** (Manter como está) | Keep: coin/magnet also to the ED (NHS regional page). The conservative option; poison.org only calls home management 'controversial', it does not recommend it to lay people. |
| `jelly-vinegar` | jellyfish | **keep** (Manter a linha) | Keep the line, scoped to tropical box-jellyfish areas (healthdirect). Box-jellyfish stings can kill; the line also carries 'go to hospital'. Card change: PT/ES 'morna/tibia' contradicted 'as hot as they can bear'. |
| `heart-aspirin` | heartattack | **a-no-dose** (A: sem dose (recomendação da Compass)) | A: no dose. NHS/BHF/St John disagree on details (chew, under 16), country practice unverified, contraindications (blood thinners, bleeding, ulcer) absent from lay pages, and the metaphor trigger can fire on a sad person. Rule: no dosing unless all sources agree. |
| `hypo-walk` | hypothermia | **keep** (Manter “mova com cuidado”) | Keep 'handle them gently' (CDC). 'Don't make them walk' is in no allowed source (NHS, St John, BRC, CDC); the gentle-handling line plus the call line cover the hazard. Revisit only if an allowed source is found. |
| `head-vomit` | headinjury | **emergency-repeat** (Emergência se vomitar mais de uma vez) | Vomiting more than once moves to the emergency tier (healthdirect 'more than once', CDC 'repeatedly'; BRC: any vomiting). The more conservative common ground; a single vomit stays in urgent advice (NHS 111). |
| `neck-recovery` | headinjury | **keep** (Manter St John) | Keep St John UK: don't move a possible neck injury; turn on the side only if the airway is at risk. Card change: replace the jargon 'can't keep the airway open' with plain signs (vomiting, blocked or gurgling breathing) and add the missing 'not breathing normally → call + CPR' step. |
| `tsunami-vertical` | tsunami | **keep** (Manter como está) | Keep 'upper floors of a tall, strong building' as a last resort (NSW SES). Chile's 8-floor rule is national guidance; the card already puts horizontal evacuation first, as SENAPRED does. |
| `burn-water` | burn | **keep** (Manter “fresca”) | Keep 'cool' running water for 20 minutes (NHS, St John, healthdirect; PT says 'fria (não gelada)'). 'Cold' (BRC) adds hypothermia risk in children and ice-water misuse. |
| `burn-child` | burn | **keep** (Manter: sempre ao médico) | Keep: every burned baby or child is checked by a doctor (British Red Cross, Pregnancy Birth and Baby). The conservative tier; NHS 111 [NHS quote withheld] presumes a UK triage line that travellers don't have. |
| `frost-temp` | frostbite | **keep** (Manter sem número) | No number (most users have no thermometer). Card change: add the CDC lay test, 'comfortable to the touch of an unaffected hand', so 'warm, not hot' is usable and numb skin is not scalded. |
| `heat-fluids` | heatstroke | **keep** (Manter a regra do healthdirect) | Keep healthdirect's rule, narrowed: 'If they're fully awake and can swallow, give small sips'. Confusion is the defining heatstroke sign, and a confused person can choke on fluids. |
| `nose-time` | nosebleed | **keep** (Manter NHS (10 a 15 min)) | Keep NHS 10–15 minutes (earlier help than St John's 30). Card change: say '10 to 15 minutes of pinching' and add an explicit 'call emergency services' line (weak/faint/breathing trouble). |
| `bite-care` | animalbite | **keep** (Manter healthdirect) | Keep healthdirect: any bite that breaks the skin gets medical advice the same day. Travellers have no access to NHS 111 criteria; rabies and tetanus make the stricter rule the safer one. |
| `bleed-soaked` | bleeding | **neither** ((none of the options)) | Neither option alone. Region-neutral wording: 'If blood soaks through, put a fresh pad on and keep pressing firmly; don't stop the pressure.' Both St John/BRC (replace) and NHS (add on top) put a fresh pad on; the key lay message, unbroken firm pressure, is common to all three. |
| `bleed-tourniquet` | bleeding | **keep** (Manter a linha) | Keep. RCUK 2025 (consistent with ERC 2021): tourniquet for life-threatening limb bleeding pressure doesn't control, 5–7 cm above, not on a joint, note the time, don't release. The card already sends improvised tourniquets to the call handler (St John). |
| `stroke-fast` | stroke | **keep** (Manter sem sigla) | No mnemonic (FAST, BE FAST and RÁPIDO use different letters per language). Card change: the EN/PT/ES text has only face/arm/speech, though the sheet says it also covers balance and vision. Add 'sudden loss of balance, or sudden trouble seeing' (CDC BE FAST, verbatim in SOURCES.raw-4; add a STROKE-BEFAST row). |
| `elec-distance` | electric | **keep** (Manter “pelo menos 10 m”) | Keep 'at least 10 metres' (American Red Cross 35 ft, the stricter source). Card change: limit the broom-handle step to household electricity; for high voltage, don't approach. |
| `tick-method` | tick | **keep** (Manter: UK/EUA + linha da Austrália) | Keep one card with both methods, but put the Australia line first: in Australia, tweezers can trigger tick anaphylaxis, so the reader must see it before reaching for tweezers. Elsewhere: CDC/NHS tweezers. |
| `sea-stonefish` | marinepuncture | **keep** (Manter a separação por bicho) | Keep the split: leave stonefish spines in (healthdirect), remove other surface spines (NHS). Card change: don't pull out anything large stuck deep (stingray barb), per the bleeding card. |
| `hex-legs` | heatexhaustion | **keep** (Manter sem a linha) | Keep without 'legs raised' (St John only; not in NHS's 4 steps). Leaving it out is harmless; the call line covers collapse. |
| `r5-snake-es` | (app strings) | **change** (Pedir mudança) | Content is a faithful translation of the WHO-based card. Register: change it to usted (see register decision): 'Mordedura de serpiente, primeros auxilios: aléjese de la serpiente y no intente atraparla ni matarla. Mantenga a la persona quieta y tranquila, sin que se mueva; si puede, llévela en una camilla improvisada y trasládela a atención médica sin demora. NO use un torniquete apretado, NO corte la herida y NO chupe el veneno ni ponga productos químicos.' Also: conditionCardText returns null for ES snakebite, and the trigger has no ES words. |
| `r5-decline-es` | (app strings) | **approve** (Aprovar) | Approve. Both lines are register-neutral and correct: 'No encontré esto en la biblioteca de este teléfono.' / 'Los fragmentos encontrados no respaldan esta respuesta.' |
| `r5-preface-es` | (app strings) | **change** (Pedir mudança) | Register to usted: 'Esta respuesta no viene de una fuente offline de este teléfono; verifíquela antes de confiar en ella.' |
| `r5-health-es` | (app strings) | **change** (Pedir mudança) | Register to usted, numbers unchanged: '…En una emergencia, llame al número de emergencias local (911 en gran parte de América, 112 en Europa).' and '…Llame ahora al número de emergencias local (911 en gran parte de América, 112 en Europa) y busque atención médica lo antes posible.' Update isNoStepsAnswer and the tests. Residual: 911 is wrong for Colombia (123), Chile (131) and Peru, which are not in the country table. |
| `r5-about` | (app strings) | **honest** (Atribuição honesta (decidido)) | Concur with r4to's decision (not medical). The ES 'No menciones…' lines address the model, not the user, so they are outside the register rule. |
| `r5-register-es` | (app strings) | **usted** (Tudo em “usted”) | Usted everywhere. 31 cards × ES already use usted, as do the official ES sources the cards rest on (CDC, MedlinePlus, NOAA). Usted is neutral and respectful from Mexico to Argentina for a stranger in an emergency, and fewer strings change (only the fixed app strings). Full list in REVIEWER-DECISIONS.md. |
| `rip-order` | ripcurrent | **keep** (Manter (NOAA)) | Keep NOAA: stay calm and float first, then swim parallel if you can swim. RLSS UK (added 2026-10-03) agrees: float; swim parallel only if confident. Float-first is the safer default for weak or panicking swimmers. |
| `rip-angle` | ripcurrent | **keep** (Manter em diagonal) | Keep 'at an angle back toward the beach' (NWS, NOS, RLSS UK, American Red Cross/USLA, and NOAA's ES transcript 'después en ángulo de regreso a la orilla'). |
| `rip-bystander` | ripcurrent | **keep** (Manter) | Keep: don't go in; throw something that floats and call. Now multi-source: NOAA, NWS, and American Red Cross/USLA ('Do not enter the water to help a person who is in trouble unless you are trained to do so'). For a lay bystander the card's stricter 'don't swim out yourself' is right. |
| `rip-193` | ripcurrent | **neither** ((none of the options)) | Re-checked after the 2026-10-03 source update: still no Brazil-official rip page, so 193 has no rip-specific quote (only MS's general 'SAMU 192 ou Corpo de Bombeiros 193'). Both numbers are correct for Brazil, but inline numbers in PT card bodies conflict with the engine's country-aware appended line for Brazilians abroad, the traveller case. Remove inline numbers from all PT cards ('Ligue para a emergência'). The appended PT line already reads '192 SAMU, 193 Bombeiros no Brasil, 112 na Europa, 911 nos EUA'. |
| `scorpa-cold` | scorpionadult | **keep** (Manter sem nenhum) | Neither ice nor warm compress. Direct conflict (CDC/MedlinePlus ice vs Brazil SES-SP warm, no ice). Comfort measures are not worth a region-dependent instruction; the card's priority is getting to care. |
| `scorpa-when` | scorpionadult | **keep** (Manter (mais rígido)) | Keep the stricter rule: every sting → nearest health service fast (Brazil MS/SES-SP, Mexico). Dangerous Tityus/Centruroides species where most PT/ES users are; MedlinePlus's 'most need no treatment' is North-America-specific. |
| `scorpa-still` | scorpion | **add** (Acrescentar no cartão infantil) | Add 'keep the stung arm or leg as still as you can' to the child card (MedlinePlus EN/ES), plus the 'no home remedies' line from the adult card (SES-SP). |

## Cards (31)

| key | verdict | summary |
|---|---|---|
| `co` | **approve** | Correct against NHS/CDC; call line present; scope fine. Opening windows (HSE) is rightly left out: go outside first. |
| `drowning` | **change** | Steps 2–3 were unconditional, but the trigger fires on any 'pulled out of the water', so a person who is breathing would also be told to start rescue breaths. Made them conditional, added a breathing → side + warmth step, translated 'open the airway' into plain words, and added the phone-on-speaker option for a lone rescuer. |
| `jellyfish` | **change** | Medically correct. In PT 'água bem morna' and ES 'agua muy tibia' mean lukewarm, which contradicts 'as hot as they can bear'. Fixed, with 'without burning' added as on the marinepuncture card. |
| `seizure` | **approve** | Matches NHS/CDC; the spoon/fingers myth is covered; the 999 criteria are complete. |
| `hypoglycemia` | **change** | Omission risk: 'regular soft drink' / 'refrigerante comum' doesn't exclude diet or zero drinks, which have no sugar and won't treat the low. NHS says 'non-diet'; add an NHS row. |
| `scorpion` | **change** | Scope correct (child only). Changes: add keep-limb-still and no-home-remedies (decision scorpa-still), add Brazil MS danger signs to the call line, drop the inline PT number (rip-193 rule; the engine appends the PT line with 192/193), and add 'escorpión' to the ES title for South America. |
| `choking` | **change** | Trigger scope mismatch: the `choking` regex fires for adults too (only infants are split off), but the title says 'child'. The technique (back blows, then abdominal thrusts) is the same for adults (NHS/SJA adult pages), so retitle and make the wording neutral. Also add 'call on speaker' to the unresponsive step. Add an NHS adult-choking citation row (gap). Pregnant or very large adults (chest thrusts) are not covered: residual. |
| `chokinginfant` | **change** | Omission risk: no step for a baby who becomes unresponsive (call + CPR), which NHS gives on the same page. Added. ES 'si no se destapa' is plumbing language; replaced. |
| `battery` | **approve** | Correct and conservative (CAPT + NHS regional); honey stays out (decision). Applies to adults too ('child' wording is acceptable for this mostly-paediatric hazard). |
| `beesting` | **approve** | Matches NHS; anaphylaxis escalation correct. Swelling of the face alone is not an NHS 999 sign; the card escalates once swelling reaches the lips, mouth, tongue or throat. |
| `heartattack` | **change** | Default A (no aspirin) per decision. Drop the inline PT number (rip-193 rule). ES 'coche' is Spain/Mexico; use 'auto'. |
| `headinjury` | **change** | Omission risk: an unresponsive person who isn't breathing normally had no CPR step (the 'child fell and isn't responding' gap). 'Can't keep the airway open' is jargon. Repeated vomiting moves to the emergency tier (decision head-vomit). ES 'guisantes' is Spain-only. |
| `tsunami` | **change** | Content correct (FEMA/NWS/ARC/NSW SES/SENAPRED). The card never says when to call emergency services; added a call sentence that keeps people away from the water. The 'call for anyone hurt or missing' clause is a generic addition with no tsunami-specific source; TSU-STAY covers 'don't go back'. |
| `hypothermia` | **change** | Medically correct (NHS/CDC/SJA); 'handle gently' kept (decision hypo-walk). ES vocabulary only: 'coche' → 'auto'. |
| `burn` | **change** | Medically correct. ES vocabulary: 'grifo' and 'film plástico' are Spain usage; neutral Latin American wording used. |
| `frostbite` | **change** | Add CDC's touch test (decision frost-temp) so numb skin is not scalded. |
| `heatstroke` | **change** | The title made 'not sweating' look required, but exertional heatstroke can sweat, so a sweating, confused person might dismiss the card. Retitled. Fluids narrowed to 'fully awake and can swallow' (decision heat-fluids). |
| `nosebleed` | **change** | The card had no 'call emergency services' line, only the ED. '10 to 15 minutes' now clearly means 'of pinching'. Calling (rather than going in) for weak, faint or breathless people is the conservative reading of NHS's A&E tier. |
| `earthquake` | **change** | Content correct (FEMA/CDC/ARC). The call line only covered gas; added serious injury and trapped people. ES: 'oríllese' and 'coche' are regional. |
| `animalbite` | **change** | There was no 'call emergency services' line (ED only). 'Any animal that could have rabies' assumes the reader knows which animals carry rabies; now names the common ones, after WHO. ES 'arañazo' → 'rasguño' (Latin America). |
| `bleeding` | **change** | Soaked dressing: region-neutral wording (decision bleed-soaked). The tourniquet is kept. The call line now says to call for any heavy bleeding and to have a helper call while you press (BRC step 2 is 'Call 999'). Inline PT number dropped. |
| `stroke` | **change** | The text has no balance or vision signs, though the review sheet says it does; added from CDC BE FAST (verbatim in SOURCES.raw-4 → add a STROKE-BEFAST row to SOURCES.md). Added a CPR line. ES 'ictus' is Spain usage; Latin America says 'derrame cerebral'/'ACV'. ES 'coche' → 'auto'. Inline PT number dropped. |
| `anaphylaxis` | **change** | Medically correct. ES 'pitidos' → 'silbidos al respirar' (Latin America). Inline PT number dropped. |
| `eyechem` | **change** | Under-triage: the call line covered only strong chemicals (NHS tier) and dropped the 'still painful or blurry' escalation the review sheet says it has. Switched to St John's tier (any chemical splash → 999/ED), the conservative one, plus 'keep rinsing on the way' (NHS). ES 'lentillas' and 'lejía' are Spain usage. |
| `electric` | **change** | Hazard: the 'dry wooden broom handle' step read as general, but it is only for household (low-voltage) current. Near high voltage it can kill the rescuer. Scoped it, and added healthdirect's 'don't try to remove a live power cable'. ES 'cuadro eléctrico' → 'tablero eléctrico'; 'a al menos' fixed. Inline PT number dropped. |
| `altitude` | **approve** | Matches NHS (stricter descent rule) and the CDC Yellow Book; 'go down + get help' line present. |
| `marinepuncture` | **change** | Omission risk: a stingray barb can be large and deep (chest or abdomen wounds can kill), but the card said 'remove spines with tweezers' and sent stingray to a minor-injuries unit. Added 'don't pull out large embedded objects' (as on the bleeding card) and a deep or chest/belly wound to the call line. That trigger has no sea-creature source (conservative addition; flagged). ES title adds 'mantarraya'. |
| `tick` | **change** | The direct contradiction stays in one card (decision tick-method), but the Australia line moves to step 1 so an Australian reader sees 'no tweezers' before using them (tick anaphylaxis risk there). The old step 4 is removed. |
| `heatexhaustion` | **approve** | Matches NHS's 4 steps and 999 tier; heatstroke escalation explicit. |
| `ripcurrent` | **change** | Content approved; now multi-source (NOAA, NWS, RLSS UK, American Red Cross/USLA). Only the inline PT numbers are dropped (decision rip-193); the engine-appended PT line lists 193 and 192. |
| `scorpionadult` | **change** | Content approved (stricter Brazil/Mexico rule; no ice or warm compress). Only the inline PT number is dropped (rip-193 rule). |

### Exact edits (EN / PT / ES)
Step numbers are the current card's. `(unchanged)` = keep that language as is. 'cites' = the citation ids the new text should carry; '(+ … row)' = a source row to add to SOURCES.md.

#### drowning
- **step 2 (replace)**  <sub>cites: DROWN-1, DROWN-1b</sub>
  - EN: If they're not breathing normally, don't try to get water out of them or press on their stomach; start rescue breaths straight away.
  - PT: Se a pessoa não respira normalmente, não tente tirar água dela nem apertar a barriga; comece as respirações de resgate imediatamente.
  - ES: Si no respira con normalidad, no intente sacarle agua ni presionarle el abdomen; empiece las respiraciones de rescate de inmediato.
- **step 3 (replace)**  <sub>cites: DROWN-2, DROWN-2b</sub>
  - EN: Open the airway (tilt the head back and lift the chin) and give 5 rescue breaths, then 30 chest compressions and 2 breaths; keep repeating.
  - PT: Abra as vias aéreas (incline a cabeça para trás e levante o queixo) e faça 5 respirações de resgate; depois 30 compressões no peito e 2 respirações, repetindo sem parar.
  - ES: Abra la vía aérea (incline la cabeza hacia atrás y levante el mentón) y dé 5 respiraciones de rescate; luego 30 compresiones en el pecho y 2 respiraciones, y repita sin parar.
- **new step after 3**  <sub>cites: HEAD-RECOVERY (+ add an SJA drowning 'keep warm' row)</sub>
  - EN: If they're breathing normally, turn them on their side, keep them warm and keep checking their breathing.
  - PT: Se estiver respirando normalmente, vire a pessoa de lado, mantenha-a aquecida e continue verificando a respiração.
  - ES: Si respira con normalidad, póngala de lado, manténgala abrigada y siga comprobando su respiración.
- **call (replace)**  <sub>cites: DROWN-2b, CHOKE-CHILD-5b</sub>
  - EN: Call emergency services now. If you're alone, put the phone on speaker and start straight away; if you can't call and do CPR together, give 1 minute of rescue breaths and compressions first, then call.
  - PT: Ligue para a emergência agora. Se estiver sozinho, ligue no viva-voz e comece logo; se não der para ligar e fazer a RCP ao mesmo tempo, faça 1 minuto de respirações e compressões antes de ligar.
  - ES: Llame a emergencias ahora. Si está solo, llame con el altavoz activado y empiece de inmediato; si no puede llamar y hacer la RCP a la vez, haga 1 minuto de respiraciones y compresiones antes de llamar.

#### jellyfish
- **step 4 (replace)**  <sub>cites: FA-JELLY-HOT</sub>
  - EN: For pain, soak the area in very warm water, as hot as they can bear without burning, for at least 30 minutes.
  - PT: Para a dor, deixe o local em água bem quente, o mais quente que a pessoa aguentar sem se queimar, por pelo menos 30 minutos.
  - ES: Para el dolor, sumerja la zona en agua muy caliente, lo más caliente que tolere sin quemarse, durante al menos 30 minutos.

#### hypoglycemia
- **step 1 (replace)**  <sub>cites: FA-HYPO-15, FA-HYPO-15b (+ NHS 'non-diet' row)</sub>
  - EN: If they're awake and can swallow, give about 15 g of fast sugar now: a small glass of juice or of a regular (not diet or zero) soft drink, glucose tablets or sweets.
  - PT: Se a pessoa estiver acordada e conseguir engolir, dê cerca de 15 g de açúcar rápido agora: um copo pequeno de suco ou de refrigerante comum (não diet nem zero), tabletes de glicose ou balas.
  - ES: Si está despierta y puede tragar, dele unos 15 g de azúcar rápido ahora: un vaso pequeño de jugo o de refresco o gaseosa normal (no light ni cero), tabletas de glucosa o caramelos.

#### scorpion
- **title (ES only)**
  - ES: Niño picado por un alacrán (escorpión)
- **step 2 (replace)**  <sub>cites: SCORP-4, SCORPA-CARE, SCORPA-CARE-ES</sub>
  - EN: Keep the child calm and away from the scorpion, and keep the stung arm or leg as still as you can.
  - PT: Acalme a criança, afaste-a do escorpião e deixe o braço ou a perna picada o mais parado possível.
  - ES: Calme al niño, aléjelo del alacrán y mantenga el brazo o la pierna picada lo más quieta posible.
- **step 4 (replace)**  <sub>cites: SCORP-5, SCORPA-NOSUBST-BR</sub>
  - EN: Don't cut, squeeze or suck the sting, and don't use a tourniquet. Don't put home remedies on it (alcohol, kerosene, coffee grounds, herbs).
  - PT: Não corte, não esprema, não chupe o local e não faça torniquete. Não passe nada no local (álcool, querosene, pó de café, ervas).
  - ES: No corte, no apriete ni chupe la picadura, y no use torniquete. No ponga remedios caseros (alcohol, queroseno, café, hierbas).
- **call (replace)**  <sub>cites: SCORP-CHILD-1, SCORP-CHILD-1b, SCORPA-SIGNS-BR</sub>
  - EN: Call emergency services now if you can't get to care quickly, or if the child vomits, drools, sweats a lot, shakes or becomes agitated.
  - PT: Ligue para a emergência agora se não der para chegar rápido ao atendimento, ou se a criança vomitar, babar, suar muito, tremer ou ficar agitada.
  - ES: Llame a emergencias ahora si no puede llegar rápido a la atención, o si el niño vomita, babea, suda mucho, tiembla o se pone agitado.

#### choking
- **title (replace)**
  - EN: Choking (adult or child over 1 year)
  - PT: Engasgo (adulto ou criança com mais de 1 ano)
  - ES: Atragantamiento (adulto o niño mayor de 1 año)
- **step 1 (replace)**  <sub>cites: CHOKE-CHILD-1</sub>
  - EN: If they can cough, encourage them to keep coughing and stay with them.
  - PT: Se a pessoa consegue tossir, incentive-a a continuar tossindo e fique junto.
  - ES: Si puede toser, anímela a seguir tosiendo y no la deje sola.
- **step 3 (replace)**  <sub>cites: CHOKE-CHILD-3 (+ NHS adult row)</sub>
  - EN: If it's still stuck, give up to 5 abdominal thrusts: stand behind them, put your fist between the navel and the ribs, and pull sharply in and up.
  - PT: Se continuar engasgada, faça até 5 compressões abdominais: por trás, com o punho entre o umbigo e as costelas, puxe com força para dentro e para cima.
  - ES: Si sigue atragantada, haga hasta 5 compresiones abdominales: por detrás, con el puño entre el ombligo y las costillas, tire con fuerza hacia dentro y hacia arriba.
- **step 5 (replace)**  <sub>cites: CHOKE-CHILD-5b</sub>
  - EN: If they become unresponsive, call emergency services (on speaker) and start CPR.
  - PT: Se ela parar de responder, ligue para a emergência (no viva-voz) e comece a RCP.
  - ES: Si deja de responder, llame a emergencias (con el altavoz) y empiece la RCP.

#### chokinginfant
- **new step after 4**  <sub>cites: CHOKE-CHILD-5b</sub>
  - EN: If the baby stops responding, call emergency services (on speaker) and start CPR.
  - PT: Se o bebê parar de responder, ligue para a emergência (no viva-voz) e comece a RCP.
  - ES: Si el bebé deja de responder, llame a emergencias (con el altavoz) y empiece la RCP.
- **call (ES only)**  <sub>cites: CHOKE-INFANT-4</sub>
  - ES: Llame a emergencias si el objeto no sale, llevando al bebé con usted, y siga repitiendo golpes y compresiones. Después, el bebé debe ser revisado en el hospital.

#### heartattack
- **step 2 (ES only)**  <sub>cites: HEART-DRIVE, HEART-DRIVE-BHF</sub>
  - ES: No la lleve en auto ni la deje conducir hasta el hospital; espere a la ambulancia.
- **call (PT only)**  <sub>cites: HEART-CALL, HEART-CALL-NHS, HEART-SIGNS, HEART-SIGNS-CDC</sub>
  - PT: Ligue para a emergência agora se achar que é um infarto: dor ou pressão no peito (aperto, peso ou esmagamento) que pode ir para o braço, pescoço, mandíbula ou costas, com falta de ar, suor ou enjoo. Não tenha medo de incomodar.

#### headinjury
- **new step after 1**  <sub>cites: HEART-CPR, HEART-CPR-BHF</sub>
  - EN: If they're not responding and not breathing normally, call emergency services and start CPR.
  - PT: Se ela não responde e não respira normalmente, ligue para a emergência e comece a RCP.
  - ES: Si no responde y no respira con normalidad, llame a emergencias y empiece la RCP.
- **step 2 (replace)**  <sub>cites: HEAD-RECOVERY</sub>
  - EN: If they're not responding but breathing normally, and they're vomiting or their breathing sounds blocked or gurgling, turn them on their side, keeping the head and spine in line.
  - PT: Se ela não responde mas respira normalmente, e estiver vomitando ou com a respiração ruidosa ou obstruída, vire-a de lado, mantendo cabeça e coluna alinhadas.
  - ES: Si no responde pero respira con normalidad, y vomita o su respiración suena ruidosa u obstruida, póngala de lado, con la cabeza y la columna alineadas.
- **step 3 (ES only)**  <sub>cites: HEAD-HOME, HEAD-COLD-BRC</sub>
  - ES: Para un chichón, ponga hielo o una bolsa de verduras congeladas envuelta en un paño durante ratos cortos; nunca ponga hielo directo sobre la piel.
- **step 5 (replace)**  <sub>cites: HEAD-111</sub>
  - EN: Get urgent medical advice if they've been sick once, feel dizzy, take blood thinners, or had been drinking; if told to go to hospital, don't drive yourself.
  - PT: Procure orientação médica urgente se ela vomitou uma vez, está tonta, toma anticoagulante ou tinha bebido; se mandarem ir ao hospital, não vá dirigindo.
  - ES: Busque atención médica urgente si vomitó una vez, está mareada, toma anticoagulantes o había bebido; si le dicen que vaya al hospital, no conduzca.
- **call (replace)**  <sub>cites: HEAD-999 (+ healthdirect/CDC repeated-vomiting rows)</sub>
  - EN: Call emergency services if they were knocked out and haven't woken, can't stay awake, have a seizure, vomit more than once, fell more than 1 metre or 5 stairs, were hit at high speed, have problems seeing, hearing, speaking, walking or with balance, new weakness or numbness, clear fluid from the ears or nose, bleeding from the ears, or changed behaviour.
  - PT: Ligue para a emergência se ela desmaiou e não acordou, não consegue ficar acordada, teve convulsão, vomitou mais de uma vez, caiu de mais de 1 metro ou 5 degraus, levou uma batida em alta velocidade, tem dificuldade para ver, ouvir, falar, andar ou se equilibrar, fraqueza ou dormência nova, líquido claro saindo do ouvido ou nariz, sangue saindo do ouvido, ou mudou de comportamento.
  - ES: Llame a emergencias si perdió el conocimiento y no despierta, no puede mantenerse despierta, tiene una convulsión, vomitó más de una vez, cayó desde más de 1 metro o 5 escalones, recibió un golpe a gran velocidad, tiene problemas para ver, oír, hablar, caminar o mantener el equilibrio, debilidad o adormecimiento nuevos, líquido claro por los oídos o la nariz, sangre por los oídos, o cambió su comportamiento.

#### tsunami
- **call (replace)**  <sub>cites: TSU-STAY</sub>
  - EN: Stay away from the coast until officials say it's safe: more waves can follow, and the first is not always the biggest. Once you're on high ground, call emergency services for anyone hurt or missing; don't go back to the water to look for them.
  - PT: Fique longe da costa até as autoridades dizerem que é seguro: podem vir outras ondas, e a primeira nem sempre é a maior. Já num lugar alto, ligue para a emergência se alguém estiver ferido ou desaparecido; não volte para perto da água para procurar.
  - ES: Manténgase lejos de la costa hasta que las autoridades digan que es seguro: pueden llegar más olas, y la primera no siempre es la más grande. Ya en un lugar alto, llame a emergencias si alguien está herido o desaparecido; no vuelva cerca del agua a buscarlo.

#### hypothermia
- **call (ES only)**  <sub>cites: HYPOTH-CALL</sub>
  - ES: Llame a emergencias siempre que sospeche hipotermia; no la lleve en auto si puede venir una ambulancia.

#### burn
- **step 1 (ES only)**  <sub>cites: BURN-COOL</sub>
  - ES: Enfríela con agua corriente fresca durante 20 minutos, lo antes posible (aún ayuda hasta 3 horas después); si no hay agua corriente, use agua embotellada fresca o un paño mojado.
- **step 4 (ES only)**  <sub>cites: BURN-COVER, BURN-COVER-NHS, BURN-COVER-HD</sub>
  - ES: Una vez enfriada, cúbrala sin apretar con plástico adherente (film) o una bolsa de plástico limpia (sin envolver apretado, y sin plástico en la cara).

#### frostbite
- **step 3 (replace)**  <sub>cites: FROST-REWARM, FROST-REWARM-CDC</sub>
  - EN: Put the area in warm (not hot) water that feels comfortable to an unaffected hand, or warm it with body heat: in your lap, or hands in the armpits. Then dry it and cover it lightly.
  - PT: Coloque a área em água morna (não quente), que pareça agradável ao toque de uma mão não afetada, ou aqueça com o calor do corpo: no colo, ou as mãos nas axilas. Depois seque e cubra levemente.
  - ES: Ponga la zona en agua tibia (no caliente), que se sienta agradable al tocarla con una mano sana, o caliéntela con el calor del cuerpo: en el regazo, o las manos en las axilas. Luego séquela y cúbrala ligeramente.

#### heatstroke
- **title (replace)**
  - EN: Heatstroke (very hot and confused, or collapsed)
  - PT: Insolação grave (muito quente e confuso, ou desmaiado)
  - ES: Golpe de calor (muy caliente y confundido, o desmayado)
- **step 3 (replace)**  <sub>cites: HEAT-FLUIDS</sub>
  - EN: If they're fully awake and can swallow, give small sips of a cool drink.
  - PT: Se estiver bem acordada e conseguir engolir, dê pequenos goles de uma bebida fresca.
  - ES: Si está bien despierta y puede tragar, dele pequeños sorbos de una bebida fresca.

#### nosebleed
- **call (replace)**  <sub>cites: NOSE-CALL, NOSE-PINCH</sub>
  - EN: Go to the emergency department if it's still bleeding after 10 to 15 minutes of pinching, the bleeding is heavy, they swallow so much blood that they vomit, or it started after a blow to the head. Call emergency services if they feel weak, dizzy or faint, or have trouble breathing.
  - PT: Vá ao pronto-socorro se ainda estiver sangrando depois de 10 a 15 minutos apertando, se o sangramento for forte, se a pessoa engolir tanto sangue que vomite, ou se tiver começado depois de uma pancada na cabeça. Ligue para a emergência se ela se sentir fraca, tonta ou a ponto de desmaiar, ou tiver dificuldade para respirar.
  - ES: Vaya a urgencias si sigue sangrando después de 10 a 15 minutos de apretar, si el sangrado es abundante, si traga tanta sangre que vomita, o si empezó tras un golpe en la cabeza. Llame a emergencias si se siente débil, mareada o a punto de desmayarse, o tiene dificultad para respirar.

#### earthquake
- **step 5 (ES only)**  <sub>cites: QUAKE-CAR</sub>
  - ES: Conduciendo: deténgase a un lado del camino, lejos de postes, cables y pasos elevados, ponga el freno de mano y quédese en el auto.
- **call (replace)**  <sub>cites: QUAKE-GAS, QUAKE-AFTER</sub>
  - EN: If you smell gas, leave and call emergency services. Check yourself and others for injuries, and call emergency services for anyone badly hurt or trapped.
  - PT: Se sentir cheiro de gás, saia e ligue para a emergência. Verifique se você e os outros estão feridos, e ligue para a emergência se alguém estiver gravemente ferido ou preso.
  - ES: Si huele a gas, salga y llame a emergencias. Revise si usted y los demás están heridos, y llame a emergencias si alguien está gravemente herido o atrapado.

#### animalbite
- **title (ES only)**
  - ES: Mordedura o rasguño de animal
- **step 4 (replace)**  <sub>cites: BITE-RABIES, BITE-RABIES-THP, BITE-WASH</sub>
  - EN: If you were abroad, or it was a bat, dog, cat, monkey or any other animal that could have rabies, get medical help immediately, even if the wound looks trivial. Don't wait for symptoms or until you get home.
  - PT: Se você estava no exterior, ou foi um morcego, cachorro, gato, macaco ou qualquer outro animal que possa ter raiva, procure atendimento médico imediatamente, mesmo que o ferimento pareça pequeno. Não espere sintomas nem voltar para casa.
  - ES: Si estaba en el extranjero, o fue un murciélago, perro, gato, mono o cualquier otro animal que pueda tener rabia, busque atención médica de inmediato, aunque la herida parezca pequeña. No espere síntomas ni a volver a casa.
- **call (replace)**  <sub>cites: BITE-CALL, BITE-DRIVE, BLEED-CALL</sub>
  - EN: Call emergency services if it's bleeding heavily and won't stop. Go to the emergency department if the wound is large or deep, or the bite is on the face or head; don't drive yourself.
  - PT: Ligue para a emergência se estiver sangrando muito e não parar. Vá ao pronto-socorro se o ferimento for grande ou profundo, ou se a mordida for no rosto ou na cabeça; não vá dirigindo.
  - ES: Llame a emergencias si sangra mucho y no para. Vaya a urgencias si la herida es grande o profunda, o la mordedura es en la cara o la cabeza; no conduzca usted mismo.

#### bleeding
- **step 2 (replace)**  <sub>cites: BLEED-SOAK, BLEED-SOAK-BRC, BLEED-PRESS-BRC</sub>
  - EN: If blood soaks through, put a fresh pad on and keep pressing firmly; don't stop the pressure.
  - PT: Se o sangue atravessar, coloque um pano novo e continue apertando com firmeza; não pare de pressionar.
  - ES: Si la sangre lo empapa, ponga un paño nuevo y siga presionando con firmeza; no deje de presionar.
- **call (replace)**  <sub>cites: BLEED-CALL, BLEED-PRESS, BLEED-PRESS-BRC</sub>
  - EN: Call emergency services now for heavy bleeding, especially if it won't stop or spurts out bright red; if someone is with you, ask them to call while you keep pressing.
  - PT: Ligue para a emergência agora em caso de sangramento forte, principalmente se não parar ou sair em jatos vermelho-vivo; se houver alguém junto, peça para ligar enquanto você continua apertando.
  - ES: Llame a emergencias ahora ante un sangrado fuerte, sobre todo si no para o sale a chorros rojo brillante; si hay alguien con usted, pídale que llame mientras usted sigue presionando.

#### stroke
- **title (ES only)**
  - ES: Posible derrame cerebral (ACV)
- **step 1 (replace)**  <sub>cites: STROKE-FAST, STROKE-BEFAST (new row: CDC BE FAST)</sub>
  - EN: Check quickly: one side of the face drooping, one arm weak, slurred or strange speech, sudden loss of balance, or sudden trouble seeing.
  - PT: Confira rápido: um lado do rosto caído, um braço fraco, fala enrolada ou estranha, perda repentina de equilíbrio ou dificuldade repentina para enxergar.
  - ES: Compruebe rápido: un lado de la cara caído, un brazo débil, habla arrastrada o extraña, pérdida repentina del equilibrio o dificultad repentina para ver.
- **step 3 (ES only)**  <sub>cites: STROKE-DRIVE, STROKE-ES</sub>
  - ES: No la lleve en auto al hospital; espere a la ambulancia.
- **new step after 5**  <sub>cites: HEART-CPR, HEART-CPR-BHF</sub>
  - EN: If they stop responding and aren't breathing normally, start CPR.
  - PT: Se ela parar de responder e não respirar normalmente, comece a RCP.
  - ES: Si deja de responder y no respira con normalidad, empiece la RCP.
- **call (PT only)**  <sub>cites: STROKE-CALL</sub>
  - PT: Ligue para a emergência agora se vir qualquer um desses sinais, mesmo que passem.

#### anaphylaxis
- **step 1 (ES only)**  <sub>cites: ANA-SIGNS</sub>
  - ES: Signos: hinchazón de garganta o lengua, dificultad para respirar o silbidos al respirar, sensación de desmayo, piel pálida o fría.
- **call (PT only)**  <sub>cites: ANA-ADR, ANA-ADR-SJA</sub>
  - PT: Ligue para a emergência agora e diga que pode ser anafilaxia.

#### eyechem
- **step 3 (ES only)**  <sub>cites: EYE-LENS</sub>
  - ES: Quite los lentes de contacto si es fácil, pero no si el ojo parece muy dañado.
- **call (replace)**  <sub>cites: EYE-CALL, EYE-CALL-NHS, EYE-RINSE</sub>
  - EN: Call emergency services or go to the emergency department after any chemical in the eye, especially a strong one such as bleach or oven cleaner. Keep rinsing on the way, and don't drive yourself.
  - PT: Ligue para a emergência ou vá ao pronto-socorro depois de qualquer produto químico no olho, principalmente um produto forte como água sanitária ou limpa-forno. Continue lavando no caminho e não vá dirigindo.
  - ES: Llame a emergencias o vaya a urgencias después de cualquier producto químico en el ojo, sobre todo uno fuerte como cloro o limpiahornos. Siga enjuagando en el camino y no conduzca.

#### electric
- **step 2 (replace)**  <sub>cites: ELEC-OFF, ELEC-OFF-SJA</sub>
  - EN: For household electricity: switch off the power at the mains or unplug it first. If you can't, separate them from the source using something dry and wooden, like a broom handle, while standing on something dry.
  - PT: Em eletricidade de casa: desligue a energia no quadro de luz ou tire da tomada primeiro. Se não der, afaste a pessoa da fonte com algo seco de madeira, como um cabo de vassoura, em pé sobre algo seco.
  - ES: Con electricidad de la casa: corte la corriente en el tablero eléctrico o desenchufe primero. Si no puede, apártela de la fuente con algo seco de madera, como el palo de una escoba, de pie sobre algo seco.
- **step 3 (replace)**  <sub>cites: ELEC-HV-ARC, ELEC-HV</sub>
  - EN: If a power line is down or it's high voltage, don't try to move them or the cable: stay at least 10 metres away from it and anything it touches, and call emergency services.
  - PT: Se houver um fio de alta tensão caído ou for alta tensão, não tente mexer na pessoa nem no fio: fique a pelo menos 10 metros dele e do que ele toca, e ligue para a emergência.
  - ES: Si hay un cable de alta tensión caído o es alta tensión, no intente mover a la persona ni el cable: manténgase al menos a 10 metros de él y de lo que toque, y llame a emergencias.
- **call (PT only)**  <sub>cites: ELEC-CALL, ELEC-CALL-SJA</sub>
  - PT: Ligue para a emergência se a pessoa desmaiou, tem dificuldade para respirar, batimento acelerado ou lento, ou depois de qualquer choque de alta tensão.

#### marinepuncture
- **title (ES only)**
  - ES: Raya (mantarraya), erizo de mar, pez araña o pez piedra
- **step 2 (replace)**  <sub>cites: SEA-SPINE, SEA-STONEFISH, BLEED-OBJECT</sub>
  - EN: Remove spines near the surface with tweezers or the edge of a card (not bare hands), but leave a stonefish spine in, and don't pull out anything large stuck deep in the wound.
  - PT: Tire os espinhos superficiais com pinça ou a borda de um cartão (sem as mãos), mas deixe o espinho de peixe-pedra e não puxe nada grande cravado fundo no ferimento.
  - ES: Quite las espinas superficiales con pinzas o el borde de una tarjeta (sin las manos), pero deje la espina del pez piedra y no saque nada grande clavado en lo profundo de la herida.
- **call (replace)**  <sub>cites: SEA-CALL, SEA-STONEFISH (chest/belly: no sea-creature source)</sub>
  - EN: Call emergency services for a stonefish sting, a deep wound or one in the chest or belly, or if they have trouble breathing, chest pain, severe swelling or bleeding, or feel faint.
  - PT: Ligue para a emergência em caso de peixe-pedra, ferimento profundo ou no peito ou na barriga, ou se houver falta de ar, dor no peito, inchaço ou sangramento forte, ou sensação de desmaio.
  - ES: Llame a emergencias si es un pez piedra, una herida profunda o en el pecho o el abdomen, o si hay dificultad para respirar, dolor en el pecho, hinchazón o sangrado fuertes, o sensación de desmayo.

#### tick
- **new step 1 (insert at top)**  <sub>cites: TICK-AU</sub>
  - EN: In Australia: don't use tweezers; health services advise freezing the tick with an ether-containing spray so it drops off. If it won't drop off, get urgent medical help.
  - PT: Na Austrália: não use pinça; os serviços de saúde orientam congelar o carrapato com um spray que contenha éter para que ele caia. Se ele não cair, procure ajuda médica urgente.
  - ES: En Australia: no use pinzas; los servicios de salud aconsejan congelar la garrapata con un spray que contenga éter para que se caiga. Si no se cae, busque ayuda médica urgente.
- **old step 1 (replace; now step 2)**  <sub>cites: TICK-REMOVE, TICK-REMOVE-NHS</sub>
  - EN: Elsewhere: with fine-tipped tweezers, grab the tick as close to the skin as possible and pull straight up with steady pressure, without squeezing it.
  - PT: Em outros lugares: com uma pinça de ponta fina, segure o carrapato o mais perto possível da pele e puxe para cima com força constante, sem apertá-lo.
  - ES: En otros lugares: con una pinza de punta fina, agarre la garrapata lo más cerca posible de la piel y tire hacia arriba con presión constante, sin apretarla.
- **old step 4 (remove)**
  - EN: (removed: moved to step 1)
  - PT: (removido)
  - ES: (eliminado)

#### ripcurrent
- **call (PT only)**  <sub>cites: RIP-911, RIP-ARC-HELP, DROWN-2b</sub>
  - PT: Chame o guarda-vidas ou ligue para a emergência agora se alguém não conseguir voltar. Quando a pessoa sair da água, se não respirar normalmente, comece a RCP.

#### scorpionadult
- **call (PT only)**  <sub>cites: SCORPA-911-MX, SCORPA-SEVERE, SCORPA-SIGNS-BR</sub>
  - PT: Ligue para a emergência agora se houver falta de ar, inchaço nos lábios ou na garganta, salivação excessiva (babando), tremores ou espasmos musculares, suor intenso ou vômitos, coração disparado, ou sensação de desmaio ou confusão.

## ES register: usted
All 31 ES cards already use usted, and so do the official ES sources they rest on (CDC en español, MedlinePlus en español, NOAA Ocean Today ES). For a stranger in an emergency, usted is neutral and respectful across Latin America (Mexico to Argentina, where 'vos' is the informal form). Changing only the fixed app strings is the smaller, lower-risk diff.

Every string to change (fixed strings; the 31 ES cards already use usted):

| where | from (tú) | to (usted) |
|---|---|---|
| conditionCards.ts ES_EMERGENCY (appended to EVERY ES card) | En una emergencia, llama al número de emergencias local (911 en gran parte de América, 112 en Europa). | En una emergencia, llame al número de emergencias local (911 en gran parte de América, 112 en Europa). |
| context.ts emergencyLine(es) | En una emergencia, llama al número de emergencias local (911 en gran parte de América, 112 en Europa). | En una emergencia, llame al número de emergencias local (911 en gran parte de América, 112 en Europa). |
| healthExtract no-steps lead (with source) | La fuente offline no trae los pasos de primeros auxilios para esto. En una emergencia, llama al número de emergencias local. Lo que dice la fuente (en inglés): | La fuente offline no trae los pasos de primeros auxilios para esto. En una emergencia, llame al número de emergencias local. Lo que dice la fuente (en inglés): |
| healthExtract no-steps answer (+ isNoStepsAnswer matcher + test) | La fuente offline no trae los pasos de primeros auxilios para esto. En una emergencia, llama al número de emergencias local (911 en gran parte de América, 112 en Europa). | La fuente offline no trae los pasos de primeros auxilios para esto. En una emergencia, llame al número de emergencias local (911 en gran parte de América, 112 en Europa). |
| noSafeStepsAnswer | No encontré en la biblioteca offline instrucciones de primeros auxilios seguras para esto. Llama ahora al número de emergencias local (911 en gran parte de América, 112 en Europa) y busca atención médica lo antes posible. | No encontré en la biblioteca offline instrucciones de primeros auxilios seguras para esto. Llame ahora al número de emergencias local (911 en gran parte de América, 112 en Europa) y busque atención médica lo antes posible. |
| uncitedPreface | Esta respuesta no viene de una fuente offline de este teléfono; verifícala antes de confiar en ella. | Esta respuesta no viene de una fuente offline de este teléfono; verifíquela antes de confiar en ella. |
| emergencyNumbersAnswer (ES tail) | Si una vida está en riesgo, llama de inmediato. | Si una vida está en riesgo, llame de inmediato. |
| snakebiteFirstAidCard ES body | Mordedura de serpiente, primeros auxilios: aléjate de la serpiente y no intentes atraparla ni matarla. Mantén a la persona quieta y tranquila, sin que se mueva; si puedes, llévala en una camilla improvisada y trasládala a atención médica sin demora. NO uses un torniquete apretado, NO cortes la herida y NO chupes el veneno ni pongas productos químicos. | Mordedura de serpiente, primeros auxilios: aléjese de la serpiente y no intente atraparla ni matarla. Mantenga a la persona quieta y tranquila, sin que se mueva; si puede, llévela en una camilla improvisada y trasládela a atención médica sin demora. NO use un torniquete apretado, NO corte la herida y NO chupe el veneno ni ponga productos químicos. |
| esFixedStrings.test.ts + answer.test.ts expectations | the strings above | update them to the usted forms (the regex /Llama ahora…/ → /Llame ahora…/) |

Already neutral: decline lines ('No encontré esto…', 'Los fragmentos encontrados…'), currentEventAnswer ('Estoy sin conexión…'), situationNote, withAfterPart note, sourceLanguageLead, the country table lines. r5-about ES ('No menciones…') addresses the model, not the user: out of scope.

## Emergency numbers (checked against the sources in this folder)

| region | number | status | evidence |
|---|---|---|---|
| BR | SAMU 192, Bombeiros 193 | VERIFIED | Ministério da Saúde page quote (SCORP-CHILD-1): 'SAMU 192 ou o Corpo de Bombeiros (193)'; SES-SP 'SAMU pelo 192'. Engine table also lists police 190 (not verified here). |
| US | 911 | VERIFIED | CDC (STROKE-DRIVE 'Call 9-1-1'; CO-CALL-CDC '911'), American Red Cross (QUAKE-GAS, RIP-ARC-HELP), NWS (RIP-911). |
| MX | 911 | VERIFIED | Secretaría de Salud STCONAPRA infographic (SCORPA-911-MX: 'llamar al 911'). |
| EU | 112 | PARTIAL | Only UK pages in the folder (St John: '999 or 112'). No EU-level official source in the folder; 112 as the EU number is standard, but not verified here. |
| UK | 999 / 112 | VERIFIED | NHS, BRC, St John quotes. |
| AU | 000 | VERIFIED | healthdirect quotes (ELEC-CALL, SEA-STONEFISH: 'triple zero (000)'). |
| NZ | 111 | VERIFIED | St John NZ (HYPO-UNRESP-CALL). |
| AR | 107 (ambulance), 911 (police) | UNVERIFIED | No Argentine source in the folder. Engine table has AR. Check an official source (Ministerio de Salud / SAME); 107 is regional (CABA/provinces vary). |
| CO | 123 | UNVERIFIED + MISSING | No source in the folder, and Colombia is NOT in the engine country table. ES users there get '911 en gran parte de América'. |
| CL | 131 (SAMU) | UNVERIFIED + MISSING | No source in the folder; Chile NOT in the engine table. ES users there get the 911 hint. |
| PE etc. | — | MISSING | Peru, Ecuador, Bolivia, Venezuela, Central America, Caribbean: not in the table; not verified. |

Card bodies now carry no numbers in any language. The number comes from the engine-appended line: EN 'In an emergency, call your local emergency number (911 in the US, 112 in Europe).', PT '(192 SAMU, 193 Bombeiros no Brasil, 112 na Europa, 911 nos EUA)', ES '(911 en gran parte de América, 112 en Europa)'. For EN/PT it switches to the country table when the user names a country.

## Additional cards to consider
- CPR / unresponsive and not breathing (adult, child, infant): many cards say 'start CPR', but no card shows how, and infant CPR differs (two fingers, cover mouth and nose). Highest priority.
- Poisoning (medicine, household chemical, or plant swallowed; child): call the poison centre or emergency services, don't induce vomiting. Needs national poison-centre numbers (BR CIATox, US Poison Control, MX), to be verified.
- Asthma attack (inhaler use, when to call).
- Spider bite (Brazil: armadeira and marrom; Ministério da Saúde animais peçonhentos) and other venomous bites. The scorpion cards say 'scorpion only'.
- Dengue warning signs (BR/LatAm travellers: severe abdominal pain, persistent vomiting, bleeding → urgent care; avoid aspirin/NSAIDs). Ministério da Saúde / PAHO sources.
- Snakebite: the ES card exists (fixed string), but conditionCardText returns null for ES and the trigger has no ES words (serpiente, culebra, víbora). Fix the routing; no new card needed.
- Choking in pregnancy or obesity (chest thrusts instead of abdominal), if the retitled choking card is accepted as the adult card.
- Severe dehydration / diarrhoea in a child (oral rehydration, red flags): common for travelling families.

## Residual risks
- No human clinical or native-speaker review. This review is by an AI model; an error here ships. Strongly recommend at least one paramedic or first-aid trainer read of the 31 cards before release, ideally including the 5 most consequential (drowning, choking ×2, bleeding, headinjury).
- Some text I added has no verbatim quote in SOURCES.md yet: STROKE-BEFAST (the quote exists in SOURCES.raw-4, add the row), NHS 'non-diet' drink (hypoglycemia), NHS adult choking (choking retitle), SJA drowning 'keep warm', tsunami/earthquake 'call for anyone hurt', stingray chest/belly wounds, plain-language airway signs (head injury). Each is conservative (more calling, less doing), but check_cards.py will fail citations until rows are added.
- ES emergency numbers: every ES card gets '911 en gran parte de América, 112 en Europa'. Wrong for Colombia (123), Chile (131) and Peru (not in the table; unverified here). conditionCardText also ignores the country-aware emergencyNumbersLine for ES (it uses a constant), unlike EN/PT. Fix: emergencyNumbersLine(query, false, true) ?? ES line, and add verified CO/CL/PE/EC/BO/UY/PY/VE/Central America rows.
- AR 107, CO 123 and CL 131 could not be verified from the folder's sources (see the numbers table).
- Trigger scope: the choking regex routes adults to a card titled 'child' (fixed by the retitle), and drowning fires whether or not the person is breathing (fixed by the conditional steps). The child scorpion card still fires on 'when I was a kid I got stung' (known false positive; harmless over-triage).
- The tick-removal contradiction (Australia vs UK/US) is inherent; the card relies on the reader knowing their country.
- Jellyfish: the 'hot water, no ice' line (NHS) may differ from Australian tropical (box jellyfish/Irukandji) protocols, where vinegar plus hospital is what matters. Vinegar stays scoped to box-jellyfish areas.
- Aspirin left out (A). In the US, call handlers may advise it; the card neither forbids nor gives it. Low risk.
- Hypothermia: 'don't make them walk' is still unsourced and absent; 'handle gently' plus 'call' cover it. The dng-002/saf-002 rule hypo-exertion still guards the checker.
- CDC † (summary-only) quotes (FA-HYPO-15, FA-SEIZ-HOLD, CO-CALL-CDC) have not been re-checked by eye.
- ES vocabulary is now Latin American neutral (auto, cloro, lentes de contacto, rasguño, gaseosa/refresco, derrame cerebral), but regional variation (Rioplatense, Andean, Caribbean) has not been reviewed by a native speaker.
- PT inline numbers removed: Brazilians now depend on the engine-appended line ('192 SAMU, 193 Bombeiros no Brasil, 112 na Europa, 911 nos EUA'). If the engine ever stops appending it, PT cards would carry no number. Add a test that every card output ends with an emergency line.
- NHS OGL attribution and MedlinePlus/Mexico (A.D.A.M./copyright: facts only): the wording is original, but a legal check was not part of this review.

UNKNOWN: whether the engine's `conditionCardText` in the shipping arm already uses the country-aware ES line (R1es patch reviewed; later arms not read). The 2026-10-03 rip-current source rows (RLSS UK, ARC/USLA) were read as quoted in SOURCES.md, not re-fetched.
