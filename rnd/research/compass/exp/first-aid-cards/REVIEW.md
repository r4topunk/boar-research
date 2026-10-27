# First-aid cards: review sheet for r4to (first-aid-cards draft 2026-10-03, DRAFT, NOT FOR SHIPPING)

TL;DR: DRAFT, NOT FOR SHIPPING. Round 1: 10 cards; round 2: 4 cards (heart attack, head injury, tsunami, hypothermia); round 3: 6 cards (burn, frostbite, heatstroke, nosebleed, earthquake, animal bite); round 4: 9 cards (bleeding, stroke, anaphylaxis, chemical in the eye, electric shock, altitude, sea-creature puncture, tick, heat exhaustion); round 5: 2 cards (rip current, scorpion sting in an adult); round 6: 4 cards (CPR adult, child, infant; swallowed poison), reviewed by a second Opus reviewer (REVIEWER-DECISIONS-6); MedlinePlus rows removed (terms forbid automated/AI use); all EN/PT/ES, every step cited to a verbatim quote from an official source (SOURCES.md). Reviewed 2026-10-03 by an independent Opus reviewer (REVIEWER-DECISIONS.md/.json; r4to chose no human review): 25 cards changed, 6 approved, 0 rejected; ES register usted; PT card text without inline phone numbers. Residual risk: no clinician or native-speaker review (see REVIEWER-DECISIONS residual_risks).

How to review: for each card, read the EN steps against the quotes below them, then PT and ES. Tick a box only if you accept the wording as is; write any change next to it. **Nothing ships without your sign-off** (and the clinical + native-speaker reviews listed at the end).

Automatic checks (check_cards.py): citations on every step = PASS; safety rules v0.9.1 = PASS (0 unsafe in all 105 card-language texts, all rounds).

## co: Carbon monoxide exposure
Covers: saf-011 (CO at home, PT; the 4B lost 'leave + call' under the health widening); requested CO card

**Decisions for you:** (1) NHS says 'go outside'; opening windows (HSE) was left out to keep the card minimal.

**EN: Possible carbon monoxide poisoning**

- [ ] 1. Get everyone out into fresh air now. Switch off the heater, boiler or stove on your way out only if you can do it quickly.  <sub>[CO-OUT]</sub>
- [ ] 2. Don't go back inside until the place has been checked.  <sub>[CO-OUT]</sub>
- [ ] 3. Don't drive yourself to hospital.  <sub>[CO-CALL]</sub>
- [ ] ☎ Call emergency services now if anyone is struggling to breathe, confused, weak, has chest pain or has passed out; otherwise get medical advice straight away.  <sub>[CO-CALL, CO-CALL-CDC]</sub>

**PT: Possível intoxicação por monóxido de carbono**

- [ ] 1. Leve todos para o ar livre agora. Desligue o aquecedor ou o fogão na saída só se der para fazer isso rápido.  <sub>[CO-OUT]</sub>
- [ ] 2. Não volte para dentro até o local ser verificado.  <sub>[CO-OUT]</sub>
- [ ] 3. Não dirija até o hospital.  <sub>[CO-CALL]</sub>
- [ ] ☎ Ligue para a emergência agora se alguém estiver com falta de ar, confuso, fraco, com dor no peito ou desmaiado; se não, procure atendimento médico imediatamente.  <sub>[CO-CALL, CO-CALL-CDC]</sub>

**ES: Posible intoxicación por monóxido de carbono**

- [ ] 1. Saque a todos al aire libre ahora. Apague el calentador o la estufa al salir solo si puede hacerlo rápido.  <sub>[CO-OUT]</sub>
- [ ] 2. No vuelva a entrar hasta que revisen el lugar.  <sub>[CO-OUT]</sub>
- [ ] 3. No conduzca usted mismo al hospital.  <sub>[CO-CALL]</sub>
- [ ] ☎ Llame a emergencias ahora si alguien tiene dificultad para respirar, está confundido, débil, con dolor en el pecho o se desmayó; si no, busque atención médica de inmediato.  <sub>[CO-CALL, CO-CALL-CDC]</sub>

<details><summary>Sources quoted</summary>

- **CO-CALL** NHS, Carbon monoxide poisoning: "Immediate action required: Call 999 or go to A&E if: / You think you or someone else has been exposed to carbon monoxide and: / are finding it hard to breathe / have suddenly become confused / have lost consciousness / are feeling weak / have chest or muscle pain / Urgent advice: Call NHS 111 if: / you think you might have symptoms of carbon monoxide poisoning / Do not drive to A&E." (https://www.nhs.uk/conditions/carbon-monoxide-poisoning/)
- **CO-CALL-CDC** CDC NIOSH, Carbon Monoxide Hazards at Work: "Call 911 or another local emergency number for medical attention or assistance if symptoms occur" (https://www.cdc.gov/niosh/carbon-monoxide/about/index.html) † summary-only
- **CO-OUT** NHS, Carbon monoxide poisoning: "stop using appliances you think might be making carbon monoxide (such as a boiler, cooker or heater) if you can / go outside / get medical advice as soon as possible – do not go back into the affected building until you have got advice" (https://www.nhs.uk/conditions/carbon-monoxide-poisoning/)

</details>

Sign-off: [ ] EN  [ ] PT  [ ] ES  [ ] clinical review done  · notes: ____

## drowning: Pulled from the water, not breathing normally
Covers: vit-loc1-026, vit-hm2-017 (rescued child not breathing; myth: drain water first)

**Decisions for you:** (1) 'Don't hold them upside down' (the myth the items ask about) is in NO official drowning page; the card says 'don't try to get water out', which is sourced. (2) 5 initial rescue breaths (St John UK, British Red Cross) vs 2 (Saudi MOH): the card follows the UK sources. (3) Hospital: required for anyone who needed rescue breaths or CPR (AAP); otherwise 'get medical advice even if they seem fine' (St John UK).

**EN: Pulled from the water and not breathing normally**

- [ ] 1. Don't put yourself in danger getting them out.  <sub>[FA-DROWN-SAFE]</sub>
- [ ] 2. If they're not breathing normally, don't try to get water out of them or press on their stomach; start rescue breaths straight away.  <sub>[DROWN-1, DROWN-1b]</sub>
- [ ] 3. Open the airway (tilt the head back and lift the chin) and give 5 rescue breaths, then 30 chest compressions and 2 breaths; keep repeating.  <sub>[DROWN-2, DROWN-2b]</sub>
- [ ] 4. If they're breathing normally, turn them on their side, keep them warm and keep checking their breathing.  <sub>[HEAD-RECOVERY, DROWN-WARM-SJA]</sub>
- [ ] 5. Anyone who needed rescue breaths or CPR must go to hospital, and anyone rescued should get medical advice even if they seem fine.  <sub>[DROWN-3, DROWN-3b]</sub>
- [ ] ☎ Call emergency services now. If you're alone, put the phone on speaker and start straight away; if you can't call and do CPR together, give 1 minute of rescue breaths and compressions first, then call.  <sub>[DROWN-2b, CHOKE-CHILD-5b]</sub>

**PT: Tirado da água e sem respirar normalmente**

- [ ] 1. Não se coloque em perigo para tirar a pessoa da água.  <sub>[FA-DROWN-SAFE]</sub>
- [ ] 2. Se a pessoa não respira normalmente, não tente tirar água dela nem apertar a barriga; comece as respirações de resgate imediatamente.  <sub>[DROWN-1, DROWN-1b]</sub>
- [ ] 3. Abra as vias aéreas (incline a cabeça para trás e levante o queixo) e faça 5 respirações de resgate; depois 30 compressões no peito e 2 respirações, repetindo sem parar.  <sub>[DROWN-2, DROWN-2b]</sub>
- [ ] 4. Se estiver respirando normalmente, vire a pessoa de lado, mantenha-a aquecida e continue verificando a respiração.  <sub>[HEAD-RECOVERY, DROWN-WARM-SJA]</sub>
- [ ] 5. Quem precisou de respirações ou RCP deve ir ao hospital, e todo resgatado deve procurar atendimento médico mesmo que pareça bem.  <sub>[DROWN-3, DROWN-3b]</sub>
- [ ] ☎ Ligue para a emergência agora. Se estiver sozinho, ligue no viva-voz e comece logo; se não der para ligar e fazer a RCP ao mesmo tempo, faça 1 minuto de respirações e compressões antes de ligar.  <sub>[DROWN-2b, CHOKE-CHILD-5b]</sub>

**ES: Sacado del agua y sin respirar con normalidad**

- [ ] 1. No se ponga en peligro para sacar a la persona del agua.  <sub>[FA-DROWN-SAFE]</sub>
- [ ] 2. Si no respira con normalidad, no intente sacarle agua ni presionarle el abdomen; empiece las respiraciones de rescate de inmediato.  <sub>[DROWN-1, DROWN-1b]</sub>
- [ ] 3. Abra la vía aérea (incline la cabeza hacia atrás y levante el mentón) y dé 5 respiraciones de rescate; luego 30 compresiones en el pecho y 2 respiraciones, y repita sin parar.  <sub>[DROWN-2, DROWN-2b]</sub>
- [ ] 4. Si respira con normalidad, póngala de lado, manténgala abrigada y siga comprobando su respiración.  <sub>[HEAD-RECOVERY, DROWN-WARM-SJA]</sub>
- [ ] 5. Quien necesitó respiraciones o RCP debe ir al hospital, y toda persona rescatada debe recibir atención médica aunque parezca estar bien.  <sub>[DROWN-3, DROWN-3b]</sub>
- [ ] ☎ Llame a emergencias ahora. Si está solo, llame con el altavoz activado y empiece de inmediato; si no puede llamar y hacer la RCP a la vez, haga 1 minuto de respiraciones y compresiones antes de llamar.  <sub>[DROWN-2b, CHOKE-CHILD-5b]</sub>

<details><summary>Sources quoted</summary>

- **CHOKE-CHILD-5b** NHS, How to stop a child from choking: "If a choking child is, or becomes, unconscious: / call 999, putting the phone on speakerphone so your hands are free / start cardiopulmonary resuscitation (CPR)" (https://www.nhs.uk/conditions/baby/first-aid-and-safety/first-aid/how-to-stop-a-child-from-choking/)
- **DROWN-1** Saudi Ministry of Health, Drowning First Aid Steps: "Do not try to remove water from the mouth or press on the chest/abdomen—this is ineffective and can cause injury. / CPR takes priority over attempts to “expel water.”" (https://www.moh.gov.sa/en/awarenessplateform/FirstAid/Pages/Drowning.aspx)
- **DROWN-1b** St John Ambulance NSW, Rescuing a drowning person: "Avoid delays or interruptions to CPR. Do not empty a distended stomach by applying external pressure. It is not necessary to drain clear water or frothy fluid that can build up in the upper airway during CPR." (https://stjohnnsw.com.au/first-aid-guides/rescuing-a-drowning-person/)
- **DROWN-2** St John Ambulance (UK), Drowning: "Check the airway is open before giving five initial rescue breaths. / After 30 chest compressions, give two rescue breaths." (https://www.sja.org.uk/get-advice/first-aid-advice/breathing-difficulties/drowning/) CONFLICT: 5 initial breaths (SJA, British Red Cross) vs 2 (Saudi MOH)
- **DROWN-2b** British Red Cross, Drowning first aid: "Step 4. Give five rescue breaths / Step 5. Give 30 chest compressions by pushing firmly in the middle of their chest up and down. / If you are on your own, call 999 after you’ve spent one minute giving them rescue breaths and chest compressions." (https://www.redcross.org.uk/first-aid/learn-first-aid/drowning)
- **DROWN-3** AAP (HealthyChildren.org), CPR for drowning: updated guidance: "Anyone who needs any level of resuscitation following drowning, including those who only need rescue breaths, should be transported to a hospital for evaluation, monitoring and treatment." (https://www.healthychildren.org/English/news/Pages/cpr-for-drowning-updated-guidance.aspx)
- **DROWN-3b** St John Ambulance (UK), Drowning: "People who have experienced near-drowning (they have been successfully rescued, with or without the need for resuscitation) may need to be observed for a short period in hospital. Medical advice should be sought, even if they appear well in the immediate aftermath." (https://www.sja.org.uk/get-advice/first-aid-advice/breathing-difficulties/drowning/)
- **DROWN-WARM-SJA** St John Ambulance (UK), Drowning: "put them in the recovery position. You may also need to treat them for hypothermia by covering them with warm clothes and blankets." (https://www.sja.org.uk/get-advice/first-aid-advice/breathing-difficulties/drowning/) ok (curl)
- **FA-DROWN-SAFE** St John Ambulance (UK), Drowning: "Do not put yourself in danger…" (https://www.sja.org.uk/first-aid-advice/drowning/) ok (2026-10-02)
- **HEAD-RECOVERY** St John Ambulance (UK), Recovery position: "It’s safe to place someone in the recovery position who is not responding to you but is breathing normally. / If you suspect someone has a spinal injury and they cannot maintain an open airway, you need to place them in the recovery position. / Try to keep the head and spine in a straight line where possible while maintaining an open airway." (https://www.sja.org.uk/first-aid-advice/recovery-position/) CONFLICT: BRC turns every unresponsive breathing person onto their side even with a suspected neck injury; SJA only if the airway can't be kept open

</details>

Sign-off: [ ] EN  [ ] PT  [ ] ES  [ ] clinical review done  · notes: ____

## jellyfish: Jellyfish sting
Covers: vit-hm2-011, vit-hm3-014 (myth: pee on it)

**Decisions for you:** (1) Vinegar is ONLY for box-jellyfish areas (tropical Australia/Indo-Pacific); healthdirect says no vinegar on bluebottles. Keep or drop the vinegar line? (2) NHS sends mouth/throat/eye stings to a minor injuries unit (lower tier), not 999; not on the card.

**EN: Jellyfish sting**

- [ ] 1. Get out of the water. Don't touch the tentacles with bare hands; remove any with tweezers or the edge of a card.  <sub>[JELLY-TENT, FA-JELLY-VINEGAR]</sub>
- [ ] 2. Rinse the sting with seawater, not fresh water.  <sub>[JELLY-TENT]</sub>
- [ ] 3. In tropical box-jellyfish areas, pour vinegar on the sting and go to hospital.  <sub>[FA-JELLY-VINEGAR]</sub>
- [ ] 4. For pain, soak the area in very warm water, as hot as they can bear without burning, for at least 30 minutes.  <sub>[FA-JELLY-HOT]</sub>
- [ ] 5. Don't pee on it and don't put ice on it.  <sub>[FA-JELLY-HOT]</sub>
- [ ] ☎ Call emergency services if they have trouble breathing, chest pain, a seizure, severe swelling, vomiting, or feel faint.  <sub>[JELLY-CALL]</sub>

**PT: Queimadura de água-viva**

- [ ] 1. Saia da água. Não toque nos tentáculos com as mãos; tire os que estiverem na pele com pinça ou a borda de um cartão.  <sub>[JELLY-TENT, FA-JELLY-VINEGAR]</sub>
- [ ] 2. Lave o local com água do mar, não com água doce.  <sub>[JELLY-TENT]</sub>
- [ ] 3. Em áreas tropicais com cubomedusa (água-viva-de-caixa), jogue vinagre no local e vá ao hospital.  <sub>[FA-JELLY-VINEGAR]</sub>
- [ ] 4. Para a dor, deixe o local em água bem quente, o mais quente que a pessoa aguentar sem se queimar, por pelo menos 30 minutos.  <sub>[FA-JELLY-HOT]</sub>
- [ ] 5. Não faça xixi no local e não ponha gelo.  <sub>[FA-JELLY-HOT]</sub>
- [ ] ☎ Ligue para a emergência se houver falta de ar, dor no peito, convulsão, inchaço forte, vômito ou sensação de desmaio.  <sub>[JELLY-CALL]</sub>

**ES: Picadura de medusa**

- [ ] 1. Salga del agua. No toque los tentáculos con las manos; retire los que queden en la piel con pinzas o el borde de una tarjeta.  <sub>[JELLY-TENT, FA-JELLY-VINEGAR]</sub>
- [ ] 2. Enjuague la zona con agua de mar, no con agua dulce.  <sub>[JELLY-TENT]</sub>
- [ ] 3. En zonas tropicales con cubomedusas, eche vinagre sobre la picadura y vaya al hospital.  <sub>[FA-JELLY-VINEGAR]</sub>
- [ ] 4. Para el dolor, sumerja la zona en agua muy caliente, lo más caliente que tolere sin quemarse, durante al menos 30 minutos.  <sub>[FA-JELLY-HOT]</sub>
- [ ] 5. No orine sobre la picadura y no ponga hielo.  <sub>[FA-JELLY-HOT]</sub>
- [ ] ☎ Llame a emergencias si hay dificultad para respirar, dolor en el pecho, convulsiones, hinchazón fuerte, vómitos o sensación de desmayo.  <sub>[JELLY-CALL]</sub>

<details><summary>Sources quoted</summary>

- **FA-JELLY-HOT** NHS, Jellyfish and other sea creature stings: "soak the area in very warm water (as hot as can be tolerated) for at least 30 minutes / do not pee on the sting / do not apply ice or a cold pack" (https://www.nhs.uk/conditions/jellyfish-and-other-sea-creature-stings/) ok (2026-10-02; re-seen 2026-10-03)
- **FA-JELLY-VINEGAR** healthdirect (AU), Jellyfish stings: "remove any tentacles… pour vinegar on the sting site and go to hospital (tropical) / Do not put vinegar on the sting. (bluebottle)" (https://www.healthdirect.gov.au/jellyfish-stings) ok (2026-10-02)
- **JELLY-CALL** NHS, Jellyfish and other sea creature stings: "Immediate action required: Go to A&E or call 999 if: / you've been stung by a sea creature and have: / difficulty breathing / chest pain / fits or seizures / severe swelling around the affected area / severe bleeding / vomiting / lightheadedness or loss of consciousness" (https://www.nhs.uk/conditions/jellyfish-and-other-sea-creature-stings/)
- **JELLY-TENT** NHS, Jellyfish and other sea creature stings: "remove any spines from the skin using tweezers or the edge of a bank card / do not touch any tentacles or spines with your bare hands / rinse the affected area with seawater (not fresh water)" (https://www.nhs.uk/conditions/jellyfish-and-other-sea-creature-stings/)

</details>

Sign-off: [ ] EN  [ ] PT  [ ] ES  [ ] clinical review done  · notes: ____

## seizure: Seizure (fit)
Covers: vit-hm3-049 (myth: spoon in the mouth)

**EN: Seizure**

- [ ] 1. Move anything that could hurt them out of the way and cushion their head.  <sub>[FA-SEIZ]</sub>
- [ ] 2. Don't hold them down and don't put anything in their mouth, not even your fingers.  <sub>[FA-SEIZ-HOLD, FA-SEIZ]</sub>
- [ ] 3. Note the time it starts and stops.  <sub>[SEIZ-TIME]</sub>
- [ ] 4. When the jerking stops, turn them on their side.  <sub>[FA-SEIZ]</sub>
- [ ] ☎ Call emergency services if it's their first seizure, it lasts more than 5 minutes, they're badly hurt, they don't wake up fully, or they have trouble breathing.  <sub>[SEIZ-CALL]</sub>

**PT: Convulsão**

- [ ] 1. Afaste o que possa machucar a pessoa e apoie a cabeça dela em algo macio.  <sub>[FA-SEIZ]</sub>
- [ ] 2. Não segure a pessoa e não coloque nada na boca dela, nem os dedos.  <sub>[FA-SEIZ-HOLD, FA-SEIZ]</sub>
- [ ] 3. Marque a hora em que começou e terminou.  <sub>[SEIZ-TIME]</sub>
- [ ] 4. Quando os tremores pararem, vire a pessoa de lado.  <sub>[FA-SEIZ]</sub>
- [ ] ☎ Ligue para a emergência se for a primeira convulsão, durar mais de 5 minutos, a pessoa se machucar, não acordar totalmente ou tiver dificuldade para respirar.  <sub>[SEIZ-CALL]</sub>

**ES: Convulsión**

- [ ] 1. Aparte lo que pueda lastimar a la persona y apoye su cabeza en algo blando.  <sub>[FA-SEIZ]</sub>
- [ ] 2. No la sujete y no le ponga nada en la boca, ni siquiera los dedos.  <sub>[FA-SEIZ-HOLD, FA-SEIZ]</sub>
- [ ] 3. Anote la hora en que empieza y termina.  <sub>[SEIZ-TIME]</sub>
- [ ] 4. Cuando paren las sacudidas, póngala de lado.  <sub>[FA-SEIZ]</sub>
- [ ] ☎ Llame a emergencias si es su primera convulsión, dura más de 5 minutos, se lastima, no despierta del todo o tiene dificultad para respirar.  <sub>[SEIZ-CALL]</sub>

<details><summary>Sources quoted</summary>

- **FA-SEIZ** NHS, What to do if someone has a seizure (fit): "cushion their head if they're on the ground / turn them on to their side after their convulsions stop / Do not put anything in their mouth, including your fingers." (https://www.nhs.uk/symptoms/what-to-do-if-someone-has-a-seizure-fit/) ok (2026-10-02; mouth line re-seen 2026-10-03)
- **FA-SEIZ-HOLD** CDC, First aid for seizures: "Don't hold the person down or stop their movements." (https://www.cdc.gov/epilepsy/first-aid-for-seizures/index.html) † summary-only (2026-10-02)
- **SEIZ-CALL** NHS, What to do if someone has a seizure (fit): "Call 999 and ask for an ambulance if: / it's the first time someone has had a seizure / … / the seizure lasts more than 5 minutes, if you do not know how long their seizures usually last / the person does not regain full consciousness, or has several seizures without regaining consciousness / the person is seriously injured during the seizure / the person has difficulty breathing after the seizure" (https://www.nhs.uk/symptoms/what-to-do-if-someone-has-a-seizure-fit/)
- **SEIZ-TIME** NHS, What to do if someone has a seizure (fit): "note the time the seizure starts and finishes" (https://www.nhs.uk/symptoms/what-to-do-if-someone-has-a-seizure-fit/)

</details>

Sign-off: [ ] EN  [ ] PT  [ ] ES  [ ] clinical review done  · notes: ____

## hypoglycemia: Low blood sugar (person with diabetes)
Covers: vit-hm2-021 (type 1, shaky and sweaty, can swallow; myth: give insulin)

**Decisions for you:** (1) 'Don't give insulin' has ONE source (St John New Zealand); NHS/CDC/Diabetes UK don't say it. Keep it? (It is the exact myth vit-hm2-021 asks about.) (2) NHS calls 999 for an unconscious person only if glucagon isn't available/fails; St John NZ calls an ambulance for any unresponsive person. The card follows St John NZ (stricter).

**EN: Low blood sugar (diabetes)**

- [ ] 1. If they're awake and can swallow, give about 15 g of fast sugar now: a small glass of juice or of a regular (not diet or zero) soft drink, glucose tablets or sweets.  <sub>[FA-HYPO-15, FA-HYPO-15b, HYPO-SUGARY-NHS]</sub>
- [ ] 2. Wait 15 minutes; if they still feel unwell, give fast sugar again.  <sub>[FA-HYPO-15]</sub>
- [ ] 3. Once they feel better, give a snack or meal, such as a sandwich or biscuits.  <sub>[HYPO-AFTER]</sub>
- [ ] 4. Don't give insulin.  <sub>[HYPO-INSULIN]</sub>
- [ ] 5. If they're unconscious or can't swallow safely, give nothing by mouth and put them in the recovery position; use a glucagon injection only if one is there and you know how.  <sub>[HYPO-GLUCAGON]</sub>
- [ ] ☎ Call emergency services if they're unconscious, can't swallow, or don't improve.  <sub>[HYPO-UNRESP-CALL, HYPO-GLUCAGON]</sub>

**PT: Hipoglicemia (diabetes)**

- [ ] 1. Se a pessoa estiver acordada e conseguir engolir, dê cerca de 15 g de açúcar rápido agora: um copo pequeno de suco ou de refrigerante comum (não diet nem zero), tabletes de glicose ou balas.  <sub>[FA-HYPO-15, FA-HYPO-15b, HYPO-SUGARY-NHS]</sub>
- [ ] 2. Espere 15 minutos; se ainda estiver mal, dê açúcar rápido de novo.  <sub>[FA-HYPO-15]</sub>
- [ ] 3. Quando melhorar, ofereça um lanche ou refeição, como um sanduíche ou biscoitos.  <sub>[HYPO-AFTER]</sub>
- [ ] 4. Não dê insulina.  <sub>[HYPO-INSULIN]</sub>
- [ ] 5. Se estiver inconsciente ou não conseguir engolir com segurança, não dê nada pela boca e coloque-a em posição lateral de segurança; use glucagon injetável só se houver e você souber aplicar.  <sub>[HYPO-GLUCAGON]</sub>
- [ ] ☎ Ligue para a emergência se a pessoa estiver inconsciente, não conseguir engolir ou não melhorar.  <sub>[HYPO-UNRESP-CALL, HYPO-GLUCAGON]</sub>

**ES: Hipoglucemia (diabetes)**

- [ ] 1. Si está despierta y puede tragar, dele unos 15 g de azúcar rápido ahora: un vaso pequeño de jugo o de refresco o gaseosa normal (no light ni cero), tabletas de glucosa o caramelos.  <sub>[FA-HYPO-15, FA-HYPO-15b, HYPO-SUGARY-NHS]</sub>
- [ ] 2. Espere 15 minutos; si sigue mal, dele azúcar rápido otra vez.  <sub>[FA-HYPO-15]</sub>
- [ ] 3. Cuando se sienta mejor, dele un refrigerio o comida, como un sándwich o galletas.  <sub>[HYPO-AFTER]</sub>
- [ ] 4. No le dé insulina.  <sub>[HYPO-INSULIN]</sub>
- [ ] 5. Si está inconsciente o no puede tragar con seguridad, no le dé nada por la boca y póngala en posición lateral de seguridad; use glucagón inyectable solo si lo hay y sabe aplicarlo.  <sub>[HYPO-GLUCAGON]</sub>
- [ ] ☎ Llame a emergencias si está inconsciente, no puede tragar o no mejora.  <sub>[HYPO-UNRESP-CALL, HYPO-GLUCAGON]</sub>

<details><summary>Sources quoted</summary>

- **FA-HYPO-15** CDC, Treatment of Low Blood Sugar (Hypoglycemia): "Have 15 grams of carbs, then wait 15 minutes. Check your blood sugar again." (https://www.cdc.gov/diabetes/treatment/treatment-low-blood-sugar-hypoglycemia.html) † summary-only (2026-10-02)
- **FA-HYPO-15b** healthdirect (AU), Hypoglycaemia: "Have about 15g of fast-acting carbohydrate." (https://www.healthdirect.gov.au/hypoglycaemia) ok (2026-10-02)
- **HYPO-AFTER** NHS, Low blood sugar (hypoglycaemia): "Once your symptoms have improved and your blood sugar is above 4mmol/L, eat something that will keep your blood sugar up for longer, such as some biscuits, a sandwich, or your next meal if it's due." (https://www.nhs.uk/conditions/low-blood-sugar-hypoglycaemia/) ok (NHS page review overdue)
- **HYPO-GLUCAGON** NHS, Low blood sugar (hypoglycaemia): "Do not give them any food or drink as they will not be able to swallow safely. / Put them into the recovery position. / Give them a glucagon injection straight away, if one is available and you know how to use it. / Call 999 if: / a glucagon injection is not available or you do not know how to use it / you've given a glucagon injection and they have not recovered within 10 minutes" (https://www.nhs.uk/conditions/low-blood-sugar-hypoglycaemia/)
- **HYPO-INSULIN** St John New Zealand, Diabetes (first aid library): "DO NOT try to give the person insulin – that can be dangerous." (https://www.stjohn.org.nz/first-aid/first-aid-library/diabetes/) single source
- **HYPO-SUGARY-NHS** NHS, Low blood sugar (hypoglycaemia): "Eat or drink something that will raise your blood sugar quickly, such as a small glass of fruit juice or sugary fizzy drink, 5 glucose or dextrose tablets, 4 large jelly babies, or 2 tubes of glucose gel." (https://www.nhs.uk/conditions/low-blood-sugar-hypoglycaemia/) ok (curl); supports 'regular (not diet or zero)' only indirectly, via 'sugary'
- **HYPO-UNRESP-CALL** St John New Zealand, Diabetes (first aid library): "Call 111 for an ambulance if: / The person is unresponsive or unconscious" (https://www.stjohn.org.nz/first-aid/first-aid-library/diabetes/) ok (via SOURCES.raw.md HYPO-GLUCAGON note)

</details>

Sign-off: [ ] EN  [ ] PT  [ ] ES  [ ] clinical review done  · notes: ____

## scorpion: Scorpion sting in a child
Covers: requested: scorpion/venomous sting in a child (Sonar repro ×5 PT; chat-slice v1-031)

**Decisions for you:** (1) Cold vs warm compress: CDC says ice; Brazil (SES-SP, federal protocol) says warm compress and NO ice. Left out of the card. Add the Brazilian line for PT? (2) 'Keep still' has no official source; only 'keep calm' is on the card. (3) Scope: scorpion only. Other venomous stings (spiders, etc.) have no sourced card here.

**EN: Scorpion sting in a child**

- [ ] 1. Treat it as an emergency: children get the most serious poisoning. Go to the nearest hospital or health service now.  <sub>[SCORP-CHILD-1, SCORP-CHILD-1b]</sub>
- [ ] 2. Keep the child calm and away from the scorpion.  <sub>[SCORP-4]</sub>
- [ ] 3. Wash the sting with soap and water, without delaying the trip.  <sub>[SCORP-2]</sub>
- [ ] 4. Don't cut, squeeze or suck the sting, and don't use a tourniquet. Don't put home remedies on it (alcohol, kerosene, coffee grounds, herbs).  <sub>[SCORP-5, SCORPA-NOSUBST-BR]</sub>
- [ ] ☎ Call emergency services now if you can't get to care quickly, or if the child vomits, drools, sweats a lot, shakes or becomes agitated.  <sub>[SCORP-CHILD-1, SCORP-CHILD-1b, SCORPA-SIGNS-BR]</sub>

**PT: Criança picada por escorpião**

- [ ] 1. É emergência: crianças têm o envenenamento mais grave. Vá agora ao hospital ou à unidade de saúde mais próxima.  <sub>[SCORP-CHILD-1, SCORP-CHILD-1b]</sub>
- [ ] 2. Acalme a criança e afaste-a do escorpião.  <sub>[SCORP-4]</sub>
- [ ] 3. Lave o local com água e sabão, sem atrasar a ida ao atendimento.  <sub>[SCORP-2]</sub>
- [ ] 4. Não corte, não esprema, não chupe o local e não faça torniquete. Não passe nada no local (álcool, querosene, pó de café, ervas).  <sub>[SCORP-5, SCORPA-NOSUBST-BR]</sub>
- [ ] ☎ Ligue para a emergência agora se não der para chegar rápido ao atendimento, ou se a criança vomitar, babar, suar muito, tremer ou ficar agitada.  <sub>[SCORP-CHILD-1, SCORP-CHILD-1b, SCORPA-SIGNS-BR]</sub>

**ES: Niño picado por un alacrán (escorpión)**

- [ ] 1. Es una emergencia: los niños sufren el envenenamiento más grave. Vaya ahora al hospital o centro de salud más cercano.  <sub>[SCORP-CHILD-1, SCORP-CHILD-1b]</sub>
- [ ] 2. Calme al niño y aléjelo del alacrán.  <sub>[SCORP-4]</sub>
- [ ] 3. Lave la picadura con agua y jabón, sin retrasar el traslado.  <sub>[SCORP-2]</sub>
- [ ] 4. No corte, no apriete ni chupe la picadura, y no use torniquete. No ponga remedios caseros (alcohol, queroseno, café, hierbas).  <sub>[SCORP-5, SCORPA-NOSUBST-BR]</sub>
- [ ] ☎ Llame a emergencias ahora si no puede llegar rápido a la atención, o si el niño vomita, babea, suda mucho, tiembla o se pone agitado.  <sub>[SCORP-CHILD-1, SCORP-CHILD-1b, SCORPA-SIGNS-BR]</sub>

<details><summary>Sources quoted</summary>

- **SCORP-2** Ministério da Saúde (BR), Perguntas Frequentes, Acidentes por Escorpiões: "Deve-se limpar o local com água e sabão e a vítima deve então ser encaminhada, sem demora, para o ponto de atendimento médico de referência da região." (https://www.gov.br/saude/pt-br/assuntos/saude-de-a-a-z/a/animais-peconhentos/acidentes-por-escorpioes/faq/faq)
- **SCORP-4** Ministério da Saúde (BR), Perguntas Frequentes, Acidentes por Escorpiões: "A primeira coisa a ser feita é acalmar a pessoa e afastá-la do escorpião causador do acidente." (https://www.gov.br/saude/pt-br/assuntos/saude-de-a-a-z/a/animais-peconhentos/acidentes-por-escorpioes/faq/faq)
- **SCORP-5** Secretaria de Estado da Saúde de São Paulo (CVE), Acidentes com escorpiões (alerta à população): "Não fazer torni quete ou garrote, não furar, não cortar, não queimar, não espremer o local da picada; / Não fazer sucção no local da ferida;" (https://www.saude.sp.gov.br/resources/cve-centro-de-vigilancia-epidemiologica/areas-de-vigilancia/doencas-de-transmissao-por-vetores-e-zoonoses/escorpiao-evento/alerta23_populacao_escorpiao.pdf) ok ('torni quete' = PDF text split)
- **SCORP-CHILD-1** Ministério da Saúde (BR), Acidentes por Escorpiões: "Crianças constituem o grupo mais suscetível ao envenenamento sistêmico grave. / Em caso de emergência, contate imediatamente o Serviço de Atendimento Móvel de Urgência (SAMU 192) ou o Corpo de Bombeiros (193)." (https://www.gov.br/saude/pt-br/assuntos/saude-de-a-a-z/a/animais-peconhentos/acidentes-por-escorpioes)
- **SCORP-CHILD-1b** Secretaria de Estado da Saúde de São Paulo (CVE), Acidentes com escorpiões (alerta à população): "Para crianças até 10 anos: Deve-se procurar o mais rapidamente possível a unidade de saúde / OBS: Se necessário, ligue para o SAMU pelo 192, pois há urgência no atendimento à criança picada." (https://www.saude.sp.gov.br/resources/cve-centro-de-vigilancia-epidemiologica/areas-de-vigilancia/doencas-de-transmissao-por-vetores-e-zoonoses/escorpiao-evento/alerta23_populacao_escorpiao.pdf)
- **SCORPA-NOSUBST-BR** Secretaria de Estado da Saúde de São Paulo (CVE), Acidentes com escorpiões (alerta à população): "Não aplicar qualquer ti po de substância sobre o local da picada (fezes, álcool, querosene, fumo, ervas, urina, pó de café, terra)" (https://www.saude.sp.gov.br/resources/cve-centro-de-vigilancia-epidemiologica/areas-de-vigilancia/doencas-de-transmissao-por-vetores-e-zoonoses/escorpiao-evento/alerta23_populacao_escorpiao.pdf) ok ('ti po' = PDF text split)
- **SCORPA-SIGNS-BR** Ministério da Saúde (BR), Acidentes por Escorpiões: "Sudorese profusa, agitação psicomotora, tremores, náuseas, vômitos, sialorreia / Crianças constituem o grupo mais suscetível ao envenenamento sistêmico grave." (https://www.gov.br/saude/pt-br/assuntos/saude-de-a-a-z/a/animais-peconhentos/acidentes-por-escorpioes)

</details>

Sign-off: [ ] EN  [ ] PT  [ ] ES  [ ] clinical review done  · notes: ____

## choking: Choking child (over 1 year)
Covers: requested: choking child (Sonar repro 'Criança engasgada')

**Decisions for you:** (1) Order: NHS says back blows and thrusts in either order; British Red Cross and St John give back blows first. The card gives back blows first.

**EN: Choking (adult or child over 1 year)**

- [ ] 1. If they can cough, encourage them to keep coughing and stay with them.  <sub>[CHOKE-CHILD-1]</sub>
- [ ] 2. If they can't cough, breathe or speak, give up to 5 firm back blows between the shoulder blades.  <sub>[CHOKE-CHILD-2]</sub>
- [ ] 3. If it's still stuck, give up to 5 abdominal thrusts: stand behind them, put your fist between the navel and the ribs, and pull sharply in and up.  <sub>[CHOKE-CHILD-3, CHOKE-ADULT-SJA]</sub>
- [ ] 4. Only take out an object you can see; don't poke blindly with your fingers.  <sub>[CHOKE-CHILD-5a]</sub>
- [ ] 5. If they become unresponsive, call emergency services (on speaker) and start CPR.  <sub>[CHOKE-CHILD-5b]</sub>
- [ ] ☎ Call emergency services if it hasn't come out after back blows and thrusts, and keep repeating them until help arrives. Get medical help even if it comes out.  <sub>[CHOKE-CHILD-4]</sub>

**PT: Engasgo (adulto ou criança com mais de 1 ano)**

- [ ] 1. Se a pessoa consegue tossir, incentive-a a continuar tossindo e fique junto.  <sub>[CHOKE-CHILD-1]</sub>
- [ ] 2. Se não consegue tossir, respirar ou falar, dê até 5 tapas firmes nas costas, entre as escápulas.  <sub>[CHOKE-CHILD-2]</sub>
- [ ] 3. Se continuar engasgada, faça até 5 compressões abdominais: por trás, com o punho entre o umbigo e as costelas, puxe com força para dentro e para cima.  <sub>[CHOKE-CHILD-3, CHOKE-ADULT-SJA]</sub>
- [ ] 4. Só retire o objeto se conseguir vê-lo; não enfie os dedos às cegas.  <sub>[CHOKE-CHILD-5a]</sub>
- [ ] 5. Se ela parar de responder, ligue para a emergência (no viva-voz) e comece a RCP.  <sub>[CHOKE-CHILD-5b]</sub>
- [ ] ☎ Ligue para a emergência se não sair depois dos tapas e das compressões, e continue repetindo até a ajuda chegar. Procure atendimento médico mesmo que saia.  <sub>[CHOKE-CHILD-4]</sub>

**ES: Atragantamiento (adulto o niño mayor de 1 año)**

- [ ] 1. Si puede toser, anímela a seguir tosiendo y no la deje sola.  <sub>[CHOKE-CHILD-1]</sub>
- [ ] 2. Si no puede toser, respirar ni hablar, dele hasta 5 golpes firmes en la espalda, entre los omóplatos.  <sub>[CHOKE-CHILD-2]</sub>
- [ ] 3. Si sigue atragantada, haga hasta 5 compresiones abdominales: por detrás, con el puño entre el ombligo y las costillas, tire con fuerza hacia dentro y hacia arriba.  <sub>[CHOKE-CHILD-3, CHOKE-ADULT-SJA]</sub>
- [ ] 4. Saque el objeto solo si lo ve; no meta los dedos a ciegas.  <sub>[CHOKE-CHILD-5a]</sub>
- [ ] 5. Si deja de responder, llame a emergencias (con el altavoz) y empiece la RCP.  <sub>[CHOKE-CHILD-5b]</sub>
- [ ] ☎ Llame a emergencias si no sale después de los golpes y las compresiones, y siga repitiéndolos hasta que llegue ayuda. Busque atención médica aunque salga.  <sub>[CHOKE-CHILD-4]</sub>

<details><summary>Sources quoted</summary>

- **CHOKE-ADULT-SJA** St John Ambulance (UK), Adult choking: "give five abdominal thrusts. To do this, stand behind them and put your arms around their waist. Place one hand in a clenched fist between their belly button and the bottom of their chest. With your other hand, grasp your fist and pull sharply inwards and upwards up to five times." (https://www.sja.org.uk/get-advice/first-aid-advice/choking/adult-choking/) ok (curl); NHS has no adult choking page (404), SJA used instead
- **CHOKE-CHILD-1** NHS, How to stop a child from choking: "If your child's coughing loudly, encourage them to carry on coughing to bring up what they're choking on and don't leave them." (https://www.nhs.uk/conditions/baby/first-aid-and-safety/first-aid/how-to-stop-a-child-from-choking/)
- **CHOKE-CHILD-2** British Red Cross, Choking child: "1. Give up to five back blows. / Hit them firmly on their back between the shoulder blades." (https://www.redcross.org.uk/first-aid/learn-first-aid-for-babies-and-children/choking-child)
- **CHOKE-CHILD-3** NHS, How to stop a child from choking: "stand or kneel behind your child, place your arms under the child's arms and around their upper abdomen / clench your fist and place it between the navel and ribs / grasp this hand with your other hand and pull sharply inwards and upwards / repeat up to 5 times" (https://www.nhs.uk/conditions/baby/first-aid-and-safety/first-aid/how-to-stop-a-child-from-choking/)
- **CHOKE-CHILD-4** NHS, How to stop a child from choking: "Call 999 if the blockage doesn't come out after trying back blows and either chest or abdominal thrusts. Keep trying this cycle until help arrives. / Even if the object has come out, get medical help." (https://www.nhs.uk/conditions/baby/first-aid-and-safety/first-aid/how-to-stop-a-child-from-choking/)
- **CHOKE-CHILD-5a** NHS, How to stop a child from choking: "If you can see the object, try to remove it. Don't poke blindly or repeatedly with your fingers." (https://www.nhs.uk/conditions/baby/first-aid-and-safety/first-aid/how-to-stop-a-child-from-choking/)
- **CHOKE-CHILD-5b** NHS, How to stop a child from choking: "If a choking child is, or becomes, unconscious: / call 999, putting the phone on speakerphone so your hands are free / start cardiopulmonary resuscitation (CPR)" (https://www.nhs.uk/conditions/baby/first-aid-and-safety/first-aid/how-to-stop-a-child-from-choking/)

</details>

Sign-off: [ ] EN  [ ] PT  [ ] ES  [ ] clinical review done  · notes: ____

## chokinginfant: Choking baby (under 1 year)
Covers: requested: choking infant (new engine key; needs the trigger split in triggers.proposed.mjs)

**Decisions for you:** (1) Chest thrusts: two fingers just below the nipple line (NHS, British Red Cross) vs two-thumb encircling (St John UK). The card follows NHS/BRC.

**EN: Choking baby (under 1 year)**

- [ ] 1. Lay the baby face down along your thigh or forearm, supporting the head, and give up to 5 sharp back blows between the shoulder blades.  <sub>[CHOKE-INFANT-1]</sub>
- [ ] 2. If it's still stuck, turn the baby face up and give up to 5 chest thrusts with two fingers in the middle of the chest, just below the nipple line.  <sub>[CHOKE-INFANT-2]</sub>
- [ ] 3. Never use abdominal thrusts on a baby.  <sub>[CHOKE-INFANT-3]</sub>
- [ ] 4. Only take out an object you can see; don't poke blindly with your fingers.  <sub>[CHOKE-CHILD-5a]</sub>
- [ ] 5. If the baby stops responding, call emergency services (on speaker) and start CPR.  <sub>[CHOKE-CHILD-5b]</sub>
- [ ] ☎ Call emergency services if it hasn't cleared, taking the baby with you, and keep repeating back blows and chest thrusts. The baby should be seen in hospital afterwards.  <sub>[CHOKE-INFANT-4]</sub>

**PT: Bebê engasgado (menos de 1 ano)**

- [ ] 1. Deite o bebê de bruços ao longo da sua coxa ou antebraço, apoiando a cabeça, e dê até 5 tapas firmes nas costas, entre as escápulas.  <sub>[CHOKE-INFANT-1]</sub>
- [ ] 2. Se continuar engasgado, vire o bebê de barriga para cima e faça até 5 compressões no peito com dois dedos no meio do peito, logo abaixo da linha dos mamilos.  <sub>[CHOKE-INFANT-2]</sub>
- [ ] 3. Nunca faça compressões abdominais em bebê.  <sub>[CHOKE-INFANT-3]</sub>
- [ ] 4. Só retire o objeto se conseguir vê-lo; não enfie os dedos às cegas.  <sub>[CHOKE-CHILD-5a]</sub>
- [ ] 5. Se o bebê parar de responder, ligue para a emergência (no viva-voz) e comece a RCP.  <sub>[CHOKE-CHILD-5b]</sub>
- [ ] ☎ Ligue para a emergência se não desengasgar, levando o bebê com você, e continue repetindo tapas e compressões. Depois, o bebê deve ser avaliado no hospital.  <sub>[CHOKE-INFANT-4]</sub>

**ES: Bebé atragantado (menor de 1 año)**

- [ ] 1. Acueste al bebé boca abajo sobre su muslo o antebrazo, sosteniendo la cabeza, y dele hasta 5 golpes firmes en la espalda, entre los omóplatos.  <sub>[CHOKE-INFANT-1]</sub>
- [ ] 2. Si sigue atragantado, póngalo boca arriba y haga hasta 5 compresiones en el pecho con dos dedos en el centro del pecho, justo debajo de la línea de los pezones.  <sub>[CHOKE-INFANT-2]</sub>
- [ ] 3. Nunca haga compresiones abdominales a un bebé.  <sub>[CHOKE-INFANT-3]</sub>
- [ ] 4. Saque el objeto solo si lo ve; no meta los dedos a ciegas.  <sub>[CHOKE-CHILD-5a]</sub>
- [ ] 5. Si el bebé deja de responder, llame a emergencias (con el altavoz) y empiece la RCP.  <sub>[CHOKE-CHILD-5b]</sub>
- [ ] ☎ Llame a emergencias si el objeto no sale, llevando al bebé con usted, y siga repitiendo golpes y compresiones. Después, el bebé debe ser revisado en el hospital.  <sub>[CHOKE-INFANT-4]</sub>

<details><summary>Sources quoted</summary>

- **CHOKE-CHILD-5a** NHS, How to stop a child from choking: "If you can see the object, try to remove it. Don't poke blindly or repeatedly with your fingers." (https://www.nhs.uk/conditions/baby/first-aid-and-safety/first-aid/how-to-stop-a-child-from-choking/)
- **CHOKE-CHILD-5b** NHS, How to stop a child from choking: "If a choking child is, or becomes, unconscious: / call 999, putting the phone on speakerphone so your hands are free / start cardiopulmonary resuscitation (CPR)" (https://www.nhs.uk/conditions/baby/first-aid-and-safety/first-aid/how-to-stop-a-child-from-choking/)
- **CHOKE-INFANT-1** NHS, How to stop a child from choking: "sit down and lay your baby face down along your thigh or forearm, supporting their head and neck with your hand / give up to 5 sharp back blows with the heel of your hand in the middle of your baby's back between their shoulder blades" (https://www.nhs.uk/conditions/baby/first-aid-and-safety/first-aid/how-to-stop-a-child-from-choking/)
- **CHOKE-INFANT-2** British Red Cross, Choking baby: "Place two fingers in the middle of their chest just below the nipples. Push sharply downwards up to five times." (https://www.redcross.org.uk/first-aid/learn-first-aid-for-babies-and-children/choking-baby) CONFLICT: two fingers (NHS, BRC) vs two-thumb encircling (SJA)
- **CHOKE-INFANT-3** British Red Cross, Choking baby: "Abdominal thrusts are used to help choking children and adults only. Using abdominal thrusts on a baby could damage their internal organs, which are fragile and still developing." (https://www.redcross.org.uk/first-aid/learn-first-aid-for-babies-and-children/choking-baby)
- **CHOKE-INFANT-4** St John Ambulance (UK), Baby choking: "Call 999 or 112 for emergency help if the obstruction hasn't cleared. / Take the baby with you to make the call. / All babies who have received chest thrusts should be seen in hospital." (https://www.sja.org.uk/get-advice/first-aid-advice/choking/baby-choking/)

</details>

Sign-off: [ ] EN  [ ] PT  [ ] ES  [ ] clinical review done  · notes: ____

## battery: Swallowed button battery, coin or magnet
Covers: requested: swallowed battery/coin (Sonar repro 'Minha filha engoliu uma bateria')

**Decisions for you:** (1) Honey: poison.org (US) says 10 mL every 10 min (≥ 1 year, within 12 h) on the way to the ER; UK (CAPT, NHS) puts getting to A&E first and omits it. Left OUT. Add for US/ES users? (2) Coins: the regional NHS page sends EVERY swallowed coin/magnet/battery to A&E; poison.org calls managing symptom-free coins 'controversial'. The card follows the NHS (go to A&E).

**EN: Swallowed button battery, coin or magnet**

- [ ] 1. A button battery is an emergency: go to the emergency department now or call an ambulance. Don't wait for symptoms.  <sub>[BATT-1]</sub>
- [ ] 2. A coin or magnet: also take the child to the emergency department.  <sub>[COIN-1]</sub>
- [ ] 3. Don't make them vomit and don't let them eat or drink.  <sub>[BATT-2]</sub>
- [ ] ☎ Call emergency services now if they're choking, drooling, retching or vomiting, or working hard to breathe.  <sub>[COIN-1b, BATT-1]</sub>

**PT: Engoliu bateria de botão, moeda ou ímã**

- [ ] 1. Bateria de botão é emergência: vá agora ao pronto-socorro ou chame uma ambulância. Não espere aparecer sintoma.  <sub>[BATT-1]</sub>
- [ ] 2. Moeda ou ímã: leve a criança ao pronto-socorro também.  <sub>[COIN-1]</sub>
- [ ] 3. Não provoque vômito e não deixe comer nem beber.  <sub>[BATT-2]</sub>
- [ ] ☎ Ligue para a emergência agora se a criança estiver engasgada, babando, com ânsia ou vômito, ou com esforço para respirar.  <sub>[COIN-1b, BATT-1]</sub>

**ES: Se tragó una pila de botón, una moneda o un imán**

- [ ] 1. Una pila de botón es una emergencia: vaya ahora a urgencias o llame a una ambulancia. No espere a que haya síntomas.  <sub>[BATT-1]</sub>
- [ ] 2. Una moneda o un imán: lleve también al niño a urgencias.  <sub>[COIN-1]</sub>
- [ ] 3. No le provoque el vómito y no le deje comer ni beber.  <sub>[BATT-2]</sub>
- [ ] ☎ Llame a emergencias ahora si se está atragantando, babea, tiene arcadas o vómitos, o le cuesta respirar.  <sub>[COIN-1b, BATT-1]</sub>

<details><summary>Sources quoted</summary>

- **BATT-1** CAPT (Child Accident Prevention Trust), Button Batteries: In an emergency: "Take them straight to the A&E department at your local hospital or dial 999 for an ambulance. / Trust your instincts and act fast – do not wait to see if any symptoms develop." (https://capt.org.uk/button-batteries-in-an-emergency/)
- **BATT-2** CAPT (Child Accident Prevention Trust), Button Batteries: In an emergency: "Do not let your child eat or drink. / Do not make them sick." (https://capt.org.uk/button-batteries-in-an-emergency/)
- **COIN-1** NHS West Yorkshire Healthier Together, Swallowed an object: "If you are concerned your child has swallowed an object such as a coin, toy, magnet or battery you should take them to the nearest Accident and Emergency Department." (https://wyhealthiertogether.nhs.uk/parentscarers/keeping-your-child-safe/swallowed-foreign-object) ok (regional NHS; no national page)
- **COIN-1b** NHS West Yorkshire Healthier Together, Swallowed an object: "Go to the nearest Accident and Emergency Department or phone 999: Is choking / Drooling more than normal / Starts gagging, vomiting or retching / Working hard to breathe" (https://wyhealthiertogether.nhs.uk/parentscarers/keeping-your-child-safe/swallowed-foreign-object)

</details>

Sign-off: [ ] EN  [ ] PT  [ ] ES  [ ] clinical review done  · notes: ____

## beesting: Bee or wasp sting (with anaphylaxis escalation)
Covers: Sonar (b): 'criança picada por abelha e o rosto está inchando' fires beesting; needs the anaphylaxis line

**Decisions for you:** (1) NHS names lips, mouth, tongue or throat swelling (not 'face') as the 999 sign. The card uses the NHS list; a swollen face alone is not on it. (2) Stings in the mouth/throat or several stings: NHS says urgent GP/111 (not on the card, which is kept minimal).

**EN: Bee or wasp sting**

- [ ] 1. Scrape the stinger out sideways with a fingernail or the edge of a card; don't use tweezers.  <sub>[BEE-SCRAPE]</sub>
- [ ] 2. Wash the area with soap and water and hold a cold cloth or wrapped ice pack on it for 20 minutes.  <sub>[BEE-WASH-COLD]</sub>
- [ ] 3. Watch for an allergic reaction: swelling of the lips, mouth, tongue or throat, trouble breathing or swallowing, sudden confusion, dizziness or fainting.  <sub>[BEE-ANAPH-SIGNS]</sub>
- [ ] 4. If that happens, use their adrenaline auto-injector if they have one, and a second one after 5 minutes if they're not better.  <sub>[ANAPH-ADR]</sub>
- [ ] 5. Have them lie down (sit up slowly if breathing is hard) and don't let them stand or walk.  <sub>[ANAPH-LIE]</sub>
- [ ] ☎ Call emergency services now if any sign of an allergic reaction appears, and say it may be anaphylaxis.  <sub>[BEE-ANAPH-SIGNS, ANAPH-ADR]</sub>

**PT: Picada de abelha ou vespa**

- [ ] 1. Raspe o ferrão de lado com a unha ou a borda de um cartão; não use pinça.  <sub>[BEE-SCRAPE]</sub>
- [ ] 2. Lave com água e sabão e coloque um pano frio ou gelo enrolado num pano por 20 minutos.  <sub>[BEE-WASH-COLD]</sub>
- [ ] 3. Observe sinais de alergia: inchaço nos lábios, boca, língua ou garganta, dificuldade para respirar ou engolir, confusão repentina, tontura ou desmaio.  <sub>[BEE-ANAPH-SIGNS]</sub>
- [ ] 4. Se isso acontecer, use a caneta de adrenalina se a pessoa tiver, e uma segunda após 5 minutos se não melhorar.  <sub>[ANAPH-ADR]</sub>
- [ ] 5. Deite a pessoa (sentada devagar se respirar for difícil) e não deixe ficar em pé nem caminhar.  <sub>[ANAPH-LIE]</sub>
- [ ] ☎ Ligue para a emergência agora se aparecer qualquer sinal de alergia, e diga que pode ser anafilaxia.  <sub>[BEE-ANAPH-SIGNS, ANAPH-ADR]</sub>

**ES: Picadura de abeja o avispa**

- [ ] 1. Raspe el aguijón de lado con la uña o el borde de una tarjeta; no use pinzas.  <sub>[BEE-SCRAPE]</sub>
- [ ] 2. Lave con agua y jabón y ponga un paño frío o hielo envuelto en un paño durante 20 minutos.  <sub>[BEE-WASH-COLD]</sub>
- [ ] 3. Vigile signos de alergia: hinchazón de labios, boca, lengua o garganta, dificultad para respirar o tragar, confusión repentina, mareo o desmayo.  <sub>[BEE-ANAPH-SIGNS]</sub>
- [ ] 4. Si ocurre, use su autoinyector de adrenalina si lo tiene, y un segundo a los 5 minutos si no mejora.  <sub>[ANAPH-ADR]</sub>
- [ ] 5. Acuéstela (que se siente despacio si le cuesta respirar) y no la deje ponerse de pie ni caminar.  <sub>[ANAPH-LIE]</sub>
- [ ] ☎ Llame a emergencias ahora si aparece cualquier signo de alergia, y diga que puede ser anafilaxia.  <sub>[BEE-ANAPH-SIGNS, ANAPH-ADR]</sub>

<details><summary>Sources quoted</summary>

- **ANAPH-ADR** NHS, Anaphylaxis: "Use an adrenaline auto-injector (such as an EpiPen) if you have one … / If your symptoms have not improved after 5 minutes, use a 2nd adrenaline auto-injector." (https://www.nhs.uk/conditions/anaphylaxis/)
- **ANAPH-LIE** NHS, Anaphylaxis: "Lie down – you can raise your legs, and if you're struggling to breathe, raise your shoulders or sit up slowly … / Do not stand or walk at any time, even if you feel better." (https://www.nhs.uk/conditions/anaphylaxis/)
- **BEE-ANAPH-SIGNS** NHS, Insect bites and stings: "Immediate action required: Call 999 if: / your lips, mouth, throat or tongue suddenly become swollen / you're breathing very fast or struggling to breathe … / your throat feels tight or you're struggling to swallow / you suddenly become very confused, drowsy or dizzy / someone faints and cannot be woken up" (https://www.nhs.uk/conditions/insect-bites-and-stings/)
- **BEE-SCRAPE** NHS, Insect bites and stings: "Brush or scrape the stinger sideways with your fingernail or the edge of a bank card. / Do not use tweezers to pull out a stinger as you could squeeze poison out of it." (https://www.nhs.uk/conditions/insect-bites-and-stings/) ok (NHS page review overdue)
- **BEE-WASH-COLD** NHS, Insect bites and stings: "Wash the area with soap and water. / put an ice pack wrapped in a cloth, or a clean cloth soaked in cold water, on the bite or sting for at least 20 minutes, if it's swollen" (https://www.nhs.uk/conditions/insect-bites-and-stings/)

</details>

Sign-off: [ ] EN  [ ] PT  [ ] ES  [ ] clinical review done  · notes: ____

## Before anything ships
- r4to signs off every card in EN, PT and ES (REVIEW.md checkboxes).
- Clinical review by a qualified person (doctor/paramedic/first-aid trainer), as for the snakebite card.
- Native PT-BR and ES review (ES uses neutral 'usted' and Latin American 'jugo'/'refresco'; Spain would differ).
- Recheck the † (summary-only) CDC quotes by eye.
- Decide the conflicts listed per card (honey, scorpion compress, rescue breaths, infant thrust technique, insulin line, vinegar; round 5: scorpion ice vs warm compress, rip-current 193).
- Engine: es text needs a one-line change (conditionCards.ts reads only en/pt) and the trigger changes in triggers.proposed.mjs; the sources line must not imply NHS endorsement.

## Checker notes
- hypoglycemia/en/step2: only summary-only (†) sources
- hypoglycemia/pt/step2: only summary-only (†) sources
- hypoglycemia/es/step2: only summary-only (†) sources
