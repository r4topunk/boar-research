# First-aid cards round 3: review sheet for r4to (first-aid-cards draft 2026-10-03, DRAFT, NOT FOR SHIPPING)

TL;DR: DRAFT, NOT FOR SHIPPING. Round 1: 10 cards; round 2: 4 cards (heart attack, head injury, tsunami, hypothermia); round 3: 6 cards (burn, frostbite, heatstroke, nosebleed, earthquake, animal bite); round 4: 9 cards (bleeding, stroke, anaphylaxis, chemical in the eye, electric shock, altitude, sea-creature puncture, tick, heat exhaustion); all EN/PT/ES, every step cited to a verbatim quote from an official source (SOURCES.md). It needs r4to's sign-off on the wording, a clinical review, and native-speaker reviews (PT-BR, ES) before anything ships.

How to review: for each card, read the EN steps against the quotes below them, then PT and ES. Tick a box only if you accept the wording as is; write any change next to it. **Nothing ships without your sign-off** (and the clinical + native-speaker reviews listed at the end).

Automatic checks (check_cards.py): citations on every step = PASS; safety rules v0.8.6 = PASS (0 unsafe in all 87 card-language texts, all rounds).

## burn: Burn or scald
Covers: saf-004, saf-010, rep-08 (placeholder burn card, shown more often under health6)

**Decisions for you:** (1) Water: 'cool' (NHS, St John, healthdirect) vs 'cold' (British Red Cross). The card says cool. (2) Children: BRC and Pregnancy Birth and Baby say every burned baby or child needs a doctor; NHS says call 111 'if not sure'. The card follows BRC. (3) No cling film on the face (healthdirect only). Kept.

**EN: Burn or scald**

- [ ] 1. Cool it under cool running water for 20 minutes, as soon as possible (it still helps up to 3 hours later); cool bottled water or a wet towel if there's no tap.  <sub>[BURN-COOL]</sub>
- [ ] 2. Take off clothing or jewellery near the burn, but not anything stuck to it.  <sub>[BURN-REMOVE]</sub>
- [ ] 3. Keep the rest of the body warm; don't put a child in a cold bath or shower.  <sub>[BURN-WARM, BURN-WARM-BRC]</sub>
- [ ] 4. Once cooled, cover it loosely with cling film or a clean plastic bag (not wrapped tight, and no cling film on the face).  <sub>[BURN-COVER, BURN-COVER-NHS, BURN-COVER-HD]</sub>
- [ ] 5. Don't use ice. Don't put butter, toothpaste, oil or creams on it. Don't burst blisters.  <sub>[BURN-DONT-SJA, BURN-DONT, BURN-DONT-BRC]</sub>
- [ ] 6. Any burn on a baby or child should be checked by a doctor.  <sub>[BURN-CHILD, BURN-CHILD-PBB]</sub>
- [ ] ☎ Call emergency services or go to the emergency department if the burn is large or deep, on the face, hands, genitals or bottom, caused by chemicals or electricity, leaves white, brown or black skin, or if they have trouble breathing.  <sub>[BURN-CALL, BURN-CALL-HD, BURN-CALL-PBB]</sub>

**PT: Queimadura**

- [ ] 1. Resfrie em água corrente fria (não gelada) por 20 minutos, o quanto antes (ainda ajuda até 3 horas depois); use água engarrafada fria ou um pano molhado se não houver torneira.  <sub>[BURN-COOL]</sub>
- [ ] 2. Tire roupas ou joias perto da queimadura, mas não o que estiver grudado nela.  <sub>[BURN-REMOVE]</sub>
- [ ] 3. Mantenha o resto do corpo aquecido; não coloque uma criança em banho ou chuveiro frio.  <sub>[BURN-WARM, BURN-WARM-BRC]</sub>
- [ ] 4. Depois de resfriar, cubra sem apertar com filme plástico ou um saco plástico limpo (sem enrolar apertado, e sem filme plástico no rosto).  <sub>[BURN-COVER, BURN-COVER-NHS, BURN-COVER-HD]</sub>
- [ ] 5. Não use gelo. Não passe manteiga, pasta de dente, óleo nem cremes. Não estoure bolhas.  <sub>[BURN-DONT-SJA, BURN-DONT, BURN-DONT-BRC]</sub>
- [ ] 6. Toda queimadura em bebê ou criança deve ser avaliada por um médico.  <sub>[BURN-CHILD, BURN-CHILD-PBB]</sub>
- [ ] ☎ Ligue para a emergência ou vá ao pronto-socorro se a queimadura for grande ou profunda, no rosto, mãos, genitais ou nádegas, causada por produto químico ou eletricidade, deixar a pele branca, marrom ou preta, ou se houver dificuldade para respirar.  <sub>[BURN-CALL, BURN-CALL-HD, BURN-CALL-PBB]</sub>

**ES: Quemadura**

- [ ] 1. Enfríela con agua corriente fresca durante 20 minutos, lo antes posible (aún ayuda hasta 3 horas después); use agua embotellada fresca o un paño mojado si no hay grifo.  <sub>[BURN-COOL]</sub>
- [ ] 2. Quite la ropa o las joyas cerca de la quemadura, pero no lo que esté pegado a ella.  <sub>[BURN-REMOVE]</sub>
- [ ] 3. Mantenga abrigado el resto del cuerpo; no meta a un niño en un baño o ducha fría.  <sub>[BURN-WARM, BURN-WARM-BRC]</sub>
- [ ] 4. Una vez enfriada, cúbrala sin apretar con film plástico o una bolsa de plástico limpia (sin envolver apretado, y sin film plástico en la cara).  <sub>[BURN-COVER, BURN-COVER-NHS, BURN-COVER-HD]</sub>
- [ ] 5. No use hielo. No ponga mantequilla, pasta de dientes, aceite ni cremas. No reviente las ampollas.  <sub>[BURN-DONT-SJA, BURN-DONT, BURN-DONT-BRC]</sub>
- [ ] 6. Toda quemadura en un bebé o un niño debe revisarla un médico.  <sub>[BURN-CHILD, BURN-CHILD-PBB]</sub>
- [ ] ☎ Llame a emergencias o vaya a urgencias si la quemadura es grande o profunda, en la cara, manos, genitales o nalgas, causada por químicos o electricidad, deja la piel blanca, marrón o negra, o si hay dificultad para respirar.  <sub>[BURN-CALL, BURN-CALL-HD, BURN-CALL-PBB]</sub>

<details><summary>Sources quoted</summary>

- **BURN-CALL** NHS, Burns and scalds: "Immediate action required: Call 999 or go to A&E if: / is very large or deep / is on your face, genitals or bottom / has been caused by an acid or chemical, or by electricity" (https://www.nhs.uk/conditions/burns-and-scalds/)
- **BURN-CALL-HD** healthdirect (AU), Burns and scalds: "Call an ambulance or go straight to your nearest emergency department if the burn: / is deep, even if it isn't painful / involves your face, hands or genitals / has caused your skin to have patches of brown, black or white / was caused by chemicals or electricity" (https://www.healthdirect.gov.au/burns-and-scalds)
- **BURN-CALL-PBB** Pregnancy, Birth and Baby (healthdirect), Treating burns and scalds in children: "your child has burns to their throat or airways, or is having trouble breathing" (https://www.pregnancybirthbaby.org.au/parenting-and-family/family-safety/treating-burns-and-scalds-in-children)
- **BURN-CHILD** British Red Cross, Burns: "Always seek medical advice for a baby or child who has been burned. / Even small burns can be potentially life-threatening to a baby or child, so always seek medical advice." (https://www.redcross.org.uk/first-aid/learn-first-aid/burns) CONFLICT: NHS uses 111 'if not sure'
- **BURN-CHILD-PBB** Pregnancy, Birth and Baby (healthdirect), Treating burns and scalds in children: "All infants and children who have been burnt will need to be checked by a doctor." (https://www.pregnancybirthbaby.org.au/parenting-and-family/family-safety/treating-burns-and-scalds-in-children)
- **BURN-COOL** NHS, Burns and scalds: "Hold the burn or scald under cool running water for 20 minutes. Do this as soon as possible, within 3 hours of it happening. If there's no running water available, you can use cool bottled water or a wet towel." (https://www.nhs.uk/conditions/burns-and-scalds/)
- **BURN-COVER** British Red Cross, Burns: "Step 2. After the burn has been cooled, loosely cover it with cling film or a clean plastic bag." (https://www.redcross.org.uk/first-aid/learn-first-aid/burns)
- **BURN-COVER-HD** healthdirect (AU), Burns and scalds: "Cover the burn with a light, loose, non-stick dressing. Plastic cling film is a good choice. Do not use plastic cling film if the burn is to the face." (https://www.healthdirect.gov.au/burns-and-scalds) CONFLICT: face exception only here
- **BURN-COVER-NHS** NHS, Burns and scalds: "When the burn or scald has cooled, lay cling film over it if you can. Do not wrap the cling film around it." (https://www.nhs.uk/conditions/burns-and-scalds/)
- **BURN-DONT** NHS, Burns and scalds: "do not put any creams, oils or butter on burns or scalds / do not use plasters or sticky dressings to cover a burn or scald / do not burst any blisters" (https://www.nhs.uk/conditions/burns-and-scalds/)
- **BURN-DONT-BRC** British Red Cross, Burns: "No. Butter, cream or toothpaste will not cool the area." (https://www.redcross.org.uk/first-aid/learn-first-aid/burns)
- **BURN-DONT-SJA** St John Ambulance (UK), Burns and scalds: "Do not use ice, creams or gels. They may cause damage and increase the risk of infection. / Do not break any blisters that may appear as this may cause infection." (https://www.sja.org.uk/first-aid-advice/burns-and-scalds/)
- **BURN-REMOVE** NHS, Burns and scalds: "Remove any clothing or jewellery that's near the affected area – but do not remove anything that is stuck to the affected area." (https://www.nhs.uk/conditions/burns-and-scalds/)
- **BURN-WARM** Pregnancy, Birth and Baby (healthdirect), Treating burns and scalds in children: "While cooling the burn, it's important to keep the rest of the body warm. Small children can become too cold (hypothermia)." (https://www.pregnancybirthbaby.org.au/parenting-and-family/family-safety/treating-burns-and-scalds-in-children)
- **BURN-WARM-BRC** British Red Cross, Burns: "Avoid putting their whole body under a cold shower or in a cold bath as it could induce hypothermia." (https://www.redcross.org.uk/first-aid/learn-first-aid/burns)

</details>

Sign-off: [ ] EN  [ ] PT  [ ] ES  [ ] clinical review done  · notes: ____

## frostbite: Frostbite
Covers: placeholder frostbite card (unvetted)

**Decisions for you:** (1) Water temperature: the card says 'warm, not hot' (NHS, CDC). Figures differ: St John ~40 °C, healthdirect 40–42 °C, the old placeholder 37–39 °C (WMS, which couldn't be fetched). Add a figure? (2) Refreezing: only healthdirect ('only rewarm when you are in a warm dry place'). Kept. (3) Signs of hypothermia too → the hypothermia card (CDC: more serious).

**EN: Frostbite**

- [ ] 1. Get indoors or to a sheltered place, remove wet clothing and rings or boots from the area, and wrap up warm.  <sub>[FROST-SHELTER, FROST-SHELTER-CDC]</sub>
- [ ] 2. Rewarm only once you're somewhere warm and dry where it can't freeze again.  <sub>[FROST-REFREEZE]</sub>
- [ ] 3. Put the area in warm (not hot) water, or warm it with body heat: in your lap, or hands in the armpits. Then dry it and cover it lightly.  <sub>[FROST-REWARM, FROST-REWARM-CDC]</sub>
- [ ] 4. Don't rub or massage it.  <sub>[FROST-DONT, FROST-DONT-CDC]</sub>
- [ ] 5. Don't warm it at a fire or radiator. Don't use a hot-water bottle or heat lamp.  <sub>[FROST-DONT]</sub>
- [ ] 6. Don't walk on frostbitten feet unless you have to.  <sub>[FROST-WALK]</sub>
- [ ] ☎ Get medical care for any frostbite; call emergency services if the skin is hard and frozen, swollen and numb, or has blisters, or if they also shiver constantly, slur, or are confused.  <sub>[FROST-CALL, FROST-CALL-CDC]</sub>

**PT: Congelamento**

- [ ] 1. Vá para dentro ou para um abrigo, tire roupas molhadas e anéis ou botas da área e se agasalhe.  <sub>[FROST-SHELTER, FROST-SHELTER-CDC]</sub>
- [ ] 2. Só reaqueça quando estiver num lugar quente e seco, onde não possa congelar de novo.  <sub>[FROST-REFREEZE]</sub>
- [ ] 3. Coloque a área em água morna (não quente), ou aqueça com o calor do corpo: no colo, ou as mãos nas axilas. Depois seque e cubra levemente.  <sub>[FROST-REWARM, FROST-REWARM-CDC]</sub>
- [ ] 4. Não esfregue nem massageie.  <sub>[FROST-DONT, FROST-DONT-CDC]</sub>
- [ ] 5. Não aqueça no fogo nem no aquecedor. Não use bolsa de água quente nem lâmpada de calor.  <sub>[FROST-DONT]</sub>
- [ ] 6. Não caminhe com os pés congelados a menos que seja necessário.  <sub>[FROST-WALK]</sub>
- [ ] ☎ Procure atendimento médico em qualquer congelamento; ligue para a emergência se a pele estiver dura e congelada, inchada e dormente, com bolhas, ou se a pessoa também tremer sem parar, enrolar a fala ou estiver confusa.  <sub>[FROST-CALL, FROST-CALL-CDC]</sub>

**ES: Congelación**

- [ ] 1. Vaya adentro o a un refugio, quite la ropa mojada y los anillos o botas de la zona, y abríguese.  <sub>[FROST-SHELTER, FROST-SHELTER-CDC]</sub>
- [ ] 2. Recaliente solo cuando esté en un lugar cálido y seco, donde no pueda volver a congelarse.  <sub>[FROST-REFREEZE]</sub>
- [ ] 3. Ponga la zona en agua tibia (no caliente), o caliéntela con el calor del cuerpo: en el regazo, o las manos en las axilas. Luego séquela y cúbrala ligeramente.  <sub>[FROST-REWARM, FROST-REWARM-CDC]</sub>
- [ ] 4. No la frote ni la masajee.  <sub>[FROST-DONT, FROST-DONT-CDC]</sub>
- [ ] 5. No la caliente al fuego ni en un radiador. No use bolsa de agua caliente ni lámpara de calor.  <sub>[FROST-DONT]</sub>
- [ ] 6. No camine con los pies congelados salvo que sea necesario.  <sub>[FROST-WALK]</sub>
- [ ] ☎ Busque atención médica ante cualquier congelación; llame a emergencias si la piel está dura y congelada, hinchada y sin sensibilidad, con ampollas, o si además tiembla sin parar, arrastra las palabras o está confundida.  <sub>[FROST-CALL, FROST-CALL-CDC]</sub>

<details><summary>Sources quoted</summary>

- **FROST-CALL** NHS, Frostbite: "Immediate action required: Call 999 or go to A&E if: / have hard, frozen skin / have swelling and loss of feeling in the affected area / have blisters filled with blood or a clear or milky fluid / you're constantly shivering, have slurred speech, slow breathing and are tired and confused" (https://www.nhs.uk/conditions/frostbite/)
- **FROST-CALL-CDC** CDC, Preventing Frostbite: "If you notice signs of frostbite on yourself or someone else, seek medical care." (https://www.cdc.gov/winter-weather/prevention/preventing-frostbite.html)
- **FROST-DONT** NHS, Frostbite: "do not rub the affected area / do not use things like a fire, radiator, hot water bottle or heat lamp to warm the affected area / do not have a hot bath to warm yourself up" (https://www.nhs.uk/conditions/frostbite/)
- **FROST-DONT-CDC** CDC, Preventing Frostbite: "Do not rub the frostbitten area with snow or massage it at all. This can cause more damage." (https://www.cdc.gov/winter-weather/prevention/preventing-frostbite.html)
- **FROST-REFREEZE** healthdirect (AU), Frostbite: "If a frostbitten area refreezes, this can cause more damage. Only rewarm the area when you are in a warm dry place." (https://www.healthdirect.gov.au/frostbite) ok (single source)
- **FROST-REWARM** NHS, Frostbite: "place the affected body part in warm (not hot) water, dry it and put on a light dressing, such as a gauze bandage, if you have one / if you're with someone who has frostbite, place the affected body part in your lap and gently warm it with your hands / put your hands in your armpits (if your hands are affected)" (https://www.nhs.uk/conditions/frostbite/)
- **FROST-REWARM-CDC** CDC, Preventing Frostbite: "Put the areas affected by frostbite in warm—not hot—water (the temperature should be comfortable to the touch for unaffected parts of the body)." (https://www.cdc.gov/winter-weather/prevention/preventing-frostbite.html) CONFLICT (figure): SJA ~40 °C, healthdirect 40–42 °C; WMS 37–39 °C not fetchable
- **FROST-SHELTER** NHS, Frostbite: "go indoors or somewhere sheltered as quickly as possible / remove clothing and jewellery, such as gloves, rings and boots from the affected area / wrap yourself in something warm like a blanket, sleeping bag or dry towel" (https://www.nhs.uk/conditions/frostbite/)
- **FROST-SHELTER-CDC** CDC, Preventing Frostbite: "2) Get them into a warm room or shelter. / 3) Remove any wet clothing." (https://www.cdc.gov/winter-weather/prevention/preventing-frostbite.html)
- **FROST-WALK** CDC, Preventing Frostbite: "Unless absolutely necessary, do not walk on feet or toes that show signs of frostbite—this increases the damage." (https://www.cdc.gov/winter-weather/prevention/preventing-frostbite.html)

</details>

Sign-off: [ ] EN  [ ] PT  [ ] ES  [ ] clinical review done  · notes: ____

## heatstroke: Heatstroke
Covers: placeholder heatstroke card (unvetted)

**Decisions for you:** (1) Fluids: only healthdirect gives a rule ('sips of cool fluid if they are conscious'); 'nothing by mouth unless fully alert' is in no source. The card follows healthdirect. (2) Cold packs: armpits and neck (NHS, St John) vs cheeks, palms and soles (healthdirect). The card follows NHS/St John. (3) Heat exhaustion (milder, no confusion) is a separate placeholder card; the old 'feet raised' step is no longer on NHS (St John only).

**EN: Heatstroke (very hot, confused, not sweating)**

- [ ] 1. Move them somewhere cool and shaded.  <sub>[HEAT-COOL]</sub>
- [ ] 2. Cool them fast while you wait: wrap them in a cool, wet sheet, or sponge them with cold water and fan them; cold packs wrapped in cloth in the armpits and on the neck.  <sub>[HEAT-COOL, HEAT-COOL-SJA]</sub>
- [ ] 3. If they're conscious, give small sips of a cool drink.  <sub>[HEAT-FLUIDS]</sub>
- [ ] 4. If they become unconscious, put them on their side in the recovery position; start CPR if they show no sign of life.  <sub>[HEAT-UNCONSC, HEAT-FLUIDS]</sub>
- [ ] ☎ Call emergency services now: heatstroke is an emergency (hot skin that isn't sweating, confusion, a seizure, or still unwell after 30 minutes of cooling).  <sub>[HEAT-CALL, HEAT-CALL-NHS]</sub>

**PT: Insolação grave (muito quente, confuso, sem suar)**

- [ ] 1. Leve a pessoa para um lugar fresco e à sombra.  <sub>[HEAT-COOL]</sub>
- [ ] 2. Resfrie rápido enquanto espera: enrole num lençol molhado e fresco, ou passe água fria com uma esponja e abane; bolsas frias enroladas num pano nas axilas e no pescoço.  <sub>[HEAT-COOL, HEAT-COOL-SJA]</sub>
- [ ] 3. Se estiver consciente, dê pequenos goles de uma bebida fresca.  <sub>[HEAT-FLUIDS]</sub>
- [ ] 4. Se desmaiar, coloque-a de lado em posição lateral de segurança; comece a RCP se não houver sinais de vida.  <sub>[HEAT-UNCONSC, HEAT-FLUIDS]</sub>
- [ ] ☎ Ligue para a emergência agora: insolação grave é emergência (pele quente sem suor, confusão, convulsão, ou ainda mal depois de 30 minutos de resfriamento).  <sub>[HEAT-CALL, HEAT-CALL-NHS]</sub>

**ES: Golpe de calor (muy caliente, confundido, sin sudar)**

- [ ] 1. Lleve a la persona a un lugar fresco y a la sombra.  <sub>[HEAT-COOL]</sub>
- [ ] 2. Enfríela rápido mientras espera: envuélvala en una sábana mojada y fresca, o pásele agua fría con una esponja y abaníquela; bolsas frías envueltas en un paño en las axilas y el cuello.  <sub>[HEAT-COOL, HEAT-COOL-SJA]</sub>
- [ ] 3. Si está consciente, dele pequeños sorbos de una bebida fresca.  <sub>[HEAT-FLUIDS]</sub>
- [ ] 4. Si pierde el conocimiento, póngala de lado en posición lateral de seguridad; empiece la RCP si no hay signos de vida.  <sub>[HEAT-UNCONSC, HEAT-FLUIDS]</sub>
- [ ] ☎ Llame a emergencias ahora: el golpe de calor es una emergencia (piel caliente sin sudor, confusión, convulsión, o sigue mal tras 30 minutos de enfriamiento).  <sub>[HEAT-CALL, HEAT-CALL-NHS]</sub>

<details><summary>Sources quoted</summary>

- **HEAT-CALL** British Red Cross, Heatstroke: "If someone has heatstroke, call 999 immediately. Heatstroke is a medical emergency and can quickly become life-threatening." (https://www.redcross.org.uk/first-aid/learn-first-aid/heatstroke)
- **HEAT-CALL-NHS** NHS, Heat exhaustion and heatstroke: "Immediate action required: Call 999 now if: / still being unwell after 30 minutes of resting in a cool place, being cooled and drinking fluids / hot skin that's not sweating and might look red (this can be harder to see on brown or black skin) / confusion and lack of coordination / a seizure or fit" (https://www.nhs.uk/conditions/heat-exhaustion-heatstroke/)
- **HEAT-COOL** NHS, Heat exhaustion and heatstroke: "Wrap the person in a cool, wet sheet, or fan them or sponge them down with cold water while you wait for help to arrive. / Move them to a cool place." (https://www.nhs.uk/conditions/heat-exhaustion-heatstroke/)
- **HEAT-COOL-SJA** St John Ambulance (UK), Heatstroke: "If available, use cold packs placed in the armpits and around the neck." (https://www.sja.org.uk/first-aid-advice/heatstroke/) CONFLICT (placement): healthdirect 'cheeks, palms and soles'
- **HEAT-FLUIDS** healthdirect (AU), Heatstroke: "Give them sips of cool fluid if they are conscious. / If they are unconscious, place them on their side with their mouth down and their chin up. You may need to do CPR." (https://www.healthdirect.gov.au/heatstroke) ok (single source for the fluid rule)
- **HEAT-UNCONSC** NHS, Heat exhaustion and heatstroke: "If they lose consciousness while you're waiting for help, put them in the recovery position and tell the ambulance service. Check their breathing and pulse and carry out CPR if they show no sign of life." (https://www.nhs.uk/conditions/heat-exhaustion-heatstroke/)

</details>

Sign-off: [ ] EN  [ ] PT  [ ] ES  [ ] clinical review done  · notes: ____

## nosebleed: Nosebleed
Covers: placeholder nosebleed card (unvetted)

**Decisions for you:** (1) When to get help: NHS says A&E after 10–15 minutes; St John says 999 after 30 minutes. The card follows NHS. (2) Blood thinners: NHS puts them in the 'see a GP' tier, not A&E. Not on the card. (3) Ice pack on the top of the nose: NHS says the evidence is weak. Left out.

**EN: Nosebleed**

- [ ] 1. Sit down and lean forward, with the head tilted forward and the mouth open.  <sub>[NOSE-POSITION]</sub>
- [ ] 2. Pinch the soft part of the nose, just above the nostrils, for 10 to 15 minutes, and breathe through the mouth.  <sub>[NOSE-PINCH, NOSE-PINCH-SJA]</sub>
- [ ] 3. Don't tilt the head back: blood can run down the throat.  <sub>[NOSE-BACK]</sub>
- [ ] 4. For the next 24 hours, don't lie down flat, and try not to blow or pick the nose, lift heavy things, or have hot drinks or alcohol.  <sub>[NOSE-AFTER]</sub>
- [ ] ☎ Go to the emergency department if it lasts longer than 10 to 15 minutes, the bleeding is heavy, they swallow so much blood that they vomit, it started after a blow to the head, or they feel weak, dizzy or short of breath.  <sub>[NOSE-CALL]</sub>

**PT: Sangramento no nariz**

- [ ] 1. Sente-se e incline o corpo para a frente, com a cabeça inclinada para a frente e a boca aberta.  <sub>[NOSE-POSITION]</sub>
- [ ] 2. Aperte a parte mole do nariz, logo acima das narinas, por 10 a 15 minutos, e respire pela boca.  <sub>[NOSE-PINCH, NOSE-PINCH-SJA]</sub>
- [ ] 3. Não incline a cabeça para trás: o sangue pode descer pela garganta.  <sub>[NOSE-BACK]</sub>
- [ ] 4. Nas 24 horas seguintes, evite assoar ou cutucar o nariz, carregar peso, bebidas quentes ou álcool, e evite ficar deitado reto.  <sub>[NOSE-AFTER]</sub>
- [ ] ☎ Vá ao pronto-socorro se durar mais de 10 a 15 minutos, o sangramento for forte, a pessoa engolir tanto sangue que vomite, tiver começado depois de uma pancada na cabeça, ou se ela se sentir fraca, tonta ou com falta de ar.  <sub>[NOSE-CALL]</sub>

**ES: Sangrado de nariz**

- [ ] 1. Siéntese e inclínese hacia delante, con la cabeza inclinada hacia delante y la boca abierta.  <sub>[NOSE-POSITION]</sub>
- [ ] 2. Apriete la parte blanda de la nariz, justo encima de las fosas nasales, durante 10 a 15 minutos, y respire por la boca.  <sub>[NOSE-PINCH, NOSE-PINCH-SJA]</sub>
- [ ] 3. No incline la cabeza hacia atrás: la sangre puede bajar por la garganta.  <sub>[NOSE-BACK]</sub>
- [ ] 4. Durante las 24 horas siguientes, evite sonarse o hurgarse la nariz, levantar peso, tomar bebidas calientes o alcohol, y evite estar acostado del todo.  <sub>[NOSE-AFTER]</sub>
- [ ] ☎ Vaya a urgencias si dura más de 10 a 15 minutos, el sangrado es abundante, traga tanta sangre que vomita, empezó tras un golpe en la cabeza, o se siente débil, mareada o con falta de aire.  <sub>[NOSE-CALL]</sub>

<details><summary>Sources quoted</summary>

- **NOSE-AFTER** NHS, Nosebleed: "After a nosebleed, to reduce the chance of another nosebleed, try not to do the following for 24 hours: / blow your nose / pick your nose / drink hot drinks or alcohol / do any heavy lifting or strenuous exercise / lie down flat" (https://www.nhs.uk/conditions/nosebleed/)
- **NOSE-BACK** St John Ambulance (UK), Nosebleed: "Do not tell them to lean their head back as this could cause the blood to trickle down the back of their throat and block the airway." (https://www.sja.org.uk/first-aid-advice/nosebleed/)
- **NOSE-CALL** NHS, Nosebleed: "Immediate action required: Go to A&E if: / your nosebleed lasts longer than 10 to 15 minutes / the bleeding seems excessive / you're swallowing a large amount of blood that makes you vomit / the bleeding started after a blow to your head / you're feeling weak or dizzy / you're having difficulty breathing" (https://www.nhs.uk/conditions/nosebleed/) CONFLICT: SJA = 999 after 30 min
- **NOSE-PINCH** NHS, Nosebleed: "pinch your nose just above your nostrils for 10 to 15 minutes / breathe through your mouth" (https://www.nhs.uk/conditions/nosebleed/)
- **NOSE-PINCH-SJA** St John Ambulance (UK), Nosebleed: "Ask them to breathe through their mouth and pinch the soft part of their nose." (https://www.sja.org.uk/first-aid-advice/nosebleed/)
- **NOSE-POSITION** NHS, Nosebleed: "sit down and lean forward, with your head tilted forward and your mouth open" (https://www.nhs.uk/conditions/nosebleed/)

</details>

Sign-off: [ ] EN  [ ] PT  [ ] ES  [ ] clinical review done  · notes: ____

## earthquake: Earthquake (inland)
Covers: placeholder earthquake card (unvetted); coastal quakes go to the tsunami card (round 2)

**Decisions for you:** (1) Car: 'stay in the car' is from CDC and the American Red Cross; Ready.gov only says pull over and stop. (2) 'Don't move about if trapped' is in no source. Left out. (3) Near the coast, the tsunami card applies instead (move to high ground after the shaking).

**EN: Earthquake**

- [ ] 1. Drop to your hands and knees, cover your head and neck (under a sturdy table if one is close), and hold on until the shaking stops.  <sub>[QUAKE-DCH]</sub>
- [ ] 2. If you're inside, stay inside. Don't run outside or to other rooms, and avoid doorways.  <sub>[QUAKE-INSIDE, QUAKE-INSIDE-CDC]</sub>
- [ ] 3. In bed: stay there and cover your head and neck with a pillow.  <sub>[QUAKE-BED]</sub>
- [ ] 4. Outdoors: stay there, in an open area away from buildings, trees, streetlights and power lines.  <sub>[QUAKE-OUTSIDE]</sub>
- [ ] 5. Driving: pull over away from poles, wires and overpasses, set the parking brake and stay in the car.  <sub>[QUAKE-CAR]</sub>
- [ ] 6. Afterwards: expect aftershocks (drop, cover, hold on again). Leave a damaged building and don't go back in. Don't use matches, lighters or light switches until you're sure there's no gas leak.  <sub>[QUAKE-AFTER, QUAKE-GAS-CDC]</sub>
- [ ] 7. If you're trapped, cover your mouth, and bang on a pipe or wall, send a text or use a whistle instead of shouting.  <sub>[QUAKE-TRAPPED]</sub>
- [ ] ☎ If you smell gas, leave and call emergency services. Check yourself and others for injuries.  <sub>[QUAKE-GAS, QUAKE-AFTER]</sub>

**PT: Terremoto**

- [ ] 1. Abaixe-se apoiando mãos e joelhos, proteja a cabeça e o pescoço (debaixo de uma mesa firme, se houver uma perto) e segure-se até o tremor parar.  <sub>[QUAKE-DCH]</sub>
- [ ] 2. Se estiver dentro de casa, fique dentro. Não corra para a rua nem para outros cômodos, e não fique no vão da porta.  <sub>[QUAKE-INSIDE, QUAKE-INSIDE-CDC]</sub>
- [ ] 3. Na cama: fique nela e proteja a cabeça e o pescoço com um travesseiro.  <sub>[QUAKE-BED]</sub>
- [ ] 4. Ao ar livre: fique onde está, num lugar aberto, longe de prédios, árvores, postes e fios elétricos.  <sub>[QUAKE-OUTSIDE]</sub>
- [ ] 5. Dirigindo: encoste longe de postes, fios e viadutos, puxe o freio de mão e fique no carro.  <sub>[QUAKE-CAR]</sub>
- [ ] 6. Depois: espere réplicas (abaixe-se, proteja-se e segure-se de novo). Saia de um prédio danificado e não volte para dentro. Não use fósforos, isqueiros nem interruptores até ter certeza de que não há vazamento de gás.  <sub>[QUAKE-AFTER, QUAKE-GAS-CDC]</sub>
- [ ] 7. Se ficar preso, cubra a boca e bata num cano ou parede, mande uma mensagem ou use um apito em vez de gritar.  <sub>[QUAKE-TRAPPED]</sub>
- [ ] ☎ Se sentir cheiro de gás, saia e ligue para a emergência. Verifique se você e os outros estão feridos.  <sub>[QUAKE-GAS, QUAKE-AFTER]</sub>

**ES: Terremoto**

- [ ] 1. Agáchese apoyando manos y rodillas, cúbrase la cabeza y el cuello (debajo de una mesa firme si hay una cerca) y agárrese hasta que pare el temblor.  <sub>[QUAKE-DCH]</sub>
- [ ] 2. Si está adentro, quédese adentro. No salga a la calle ni corra a otras habitaciones, y no se ponga bajo el marco de una puerta.  <sub>[QUAKE-INSIDE, QUAKE-INSIDE-CDC]</sub>
- [ ] 3. En la cama: quédese en ella y cúbrase la cabeza y el cuello con una almohada.  <sub>[QUAKE-BED]</sub>
- [ ] 4. Al aire libre: quédese ahí, en un lugar abierto, lejos de edificios, árboles, postes de luz y cables eléctricos.  <sub>[QUAKE-OUTSIDE]</sub>
- [ ] 5. Conduciendo: oríllese lejos de postes, cables y pasos elevados, ponga el freno de mano y quédese en el coche.  <sub>[QUAKE-CAR]</sub>
- [ ] 6. Después: espere réplicas (agáchese, cúbrase y agárrese otra vez). Salga de un edificio dañado y no vuelva a entrar. No use fósforos, encendedores ni interruptores hasta estar seguro de que no hay fuga de gas.  <sub>[QUAKE-AFTER, QUAKE-GAS-CDC]</sub>
- [ ] 7. Si queda atrapado, cúbrase la boca y golpee una tubería o pared, envíe un mensaje o use un silbato en lugar de gritar.  <sub>[QUAKE-TRAPPED]</sub>
- [ ] ☎ Si huele a gas, salga y llame a emergencias. Revise si usted y los demás están heridos.  <sub>[QUAKE-GAS, QUAKE-AFTER]</sub>

<details><summary>Sources quoted</summary>

- **QUAKE-AFTER** Ready.gov (FEMA), Earthquakes: "Expect aftershocks to follow the main shock of an earthquake. Be ready to Drop, Cover and Hold On if you feel an aftershock. / If you are in a damaged building, go outside and quickly move away from the building. Do not enter damaged buildings. / Check yourself to see if you are hurt and help others if you have training." (https://www.ready.gov/earthquakes)
- **QUAKE-BED** American Red Cross, Earthquake Safety: "If you are in bed, STAY there and COVER your head and neck with a pillow." (https://www.redcross.org/get-help/how-to-prepare-for-emergencies/types-of-emergencies/earthquake.html)
- **QUAKE-CAR** CDC, Stay Safe During an Earthquake: "Move your car to the shoulder or curb, away from utility poles, overhead wires, and under- or overpasses. / Stay in the car and set the parking brake." (https://www.cdc.gov/earthquakes/safety/stay-safe-during-an-earthquake.html)
- **QUAKE-DCH** Ready.gov (FEMA), Earthquakes: "Drop where you are onto hands and knees. / Cover your head and neck with one arm and hand. If a sturdy table or desk is nearby, crawl underneath it for shelter. / Hold until the shaking stops." (https://www.ready.gov/earthquakes)
- **QUAKE-GAS** American Red Cross, Earthquake Safety: "If you suspect a gas leak, leave your home, and call 911." (https://www.redcross.org/get-help/how-to-prepare-for-emergencies/types-of-emergencies/earthquake.html)
- **QUAKE-GAS-CDC** CDC, Stay Safe After an Earthquake: "Do not use matches, lighters, appliances, or light switches until you are sure there are no gas leaks. Sparks from electrical switches could ignite gas, causing an explosion." (https://www.cdc.gov/earthquakes/safety/stay-safe-after-an-earthquake.html)
- **QUAKE-INSIDE** Ready.gov (FEMA), Earthquakes: "If you are inside, stay and do not run outside; avoid doorways." (https://www.ready.gov/earthquakes)
- **QUAKE-INSIDE-CDC** CDC, Stay Safe During an Earthquake: "DO NOT run outside or to other rooms during an earthquake. You are less likely to be injured if you stay where you are. / DO NOT stand in a doorway. You are safer under a table." (https://www.cdc.gov/earthquakes/safety/stay-safe-during-an-earthquake.html)
- **QUAKE-OUTSIDE** Ready.gov (FEMA), Earthquakes: "If you're outside, stay there. Move to an open area away from buildings, trees, streetlights and power lines." (https://www.ready.gov/earthquakes)
- **QUAKE-TRAPPED** Ready.gov (FEMA), Earthquakes: "If you are trapped, send a text or bang on a pipe or wall. Cover your mouth with your shirt for protection and instead of shouting, use a whistle." (https://www.ready.gov/earthquakes)

</details>

Sign-off: [ ] EN  [ ] PT  [ ] ES  [ ] clinical review done  · notes: ____

## animalbite: Animal bite or scratch
Covers: placeholder animalbite card (unvetted)

**Decisions for you:** (1) When to get care: healthdirect says ANY bite that breaks the skin needs medical advice (tetanus); NHS lists criteria for 111. The card follows healthdirect. (2) Face/head bites: emergency department (healthdirect) vs 111 (NHS). The card follows healthdirect. (3) Monkeys: only the CDC Yellow Book (clinician text) covers them; the card says 'any animal that could have rabies, or a bat', following WHO/NHS.

**EN: Animal bite or scratch**

- [ ] 1. Wash the wound right away with soap and running water for at least 15 minutes.  <sub>[BITE-WASH, BITE-WASH-CDC]</sub>
- [ ] 2. If it's bleeding heavily, press a dry dressing or clean cloth firmly on it; then cover it with a clean dressing.  <sub>[BITE-BLEED]</sub>
- [ ] 3. If the skin is broken, get medical advice the same day (infection and tetanus).  <sub>[BITE-CARE]</sub>
- [ ] 4. If you were abroad, or it was a bat or any animal that could have rabies, get medical help immediately, even if the wound looks trivial. Don't wait for symptoms or until you get home.  <sub>[BITE-RABIES, BITE-RABIES-THP, BITE-WASH]</sub>
- [ ] ☎ Go to the emergency department if the wound is large or deep, it won't stop bleeding, or the bite is on the face or head. Don't drive yourself.  <sub>[BITE-CALL, BITE-DRIVE]</sub>

**PT: Mordida ou arranhão de animal**

- [ ] 1. Lave o ferimento na hora com água corrente e sabão por pelo menos 15 minutos.  <sub>[BITE-WASH, BITE-WASH-CDC]</sub>
- [ ] 2. Se estiver sangrando muito, pressione com firmeza um curativo seco ou pano limpo; depois cubra com um curativo limpo.  <sub>[BITE-BLEED]</sub>
- [ ] 3. Se a pele rompeu, procure orientação médica no mesmo dia (infecção e tétano).  <sub>[BITE-CARE]</sub>
- [ ] 4. Se você estava no exterior, ou foi um morcego ou qualquer animal que possa ter raiva, procure atendimento médico imediatamente, mesmo que o ferimento pareça pequeno. Não espere sintomas nem voltar para casa.  <sub>[BITE-RABIES, BITE-RABIES-THP, BITE-WASH]</sub>
- [ ] ☎ Vá ao pronto-socorro se o ferimento for grande ou profundo, não parar de sangrar, ou se a mordida for no rosto ou na cabeça. Não vá dirigindo.  <sub>[BITE-CALL, BITE-DRIVE]</sub>

**ES: Mordedura o arañazo de animal**

- [ ] 1. Lave la herida de inmediato con agua corriente y jabón durante al menos 15 minutos.  <sub>[BITE-WASH, BITE-WASH-CDC]</sub>
- [ ] 2. Si sangra mucho, presione con firmeza un apósito seco o un paño limpio; luego cúbrala con un apósito limpio.  <sub>[BITE-BLEED]</sub>
- [ ] 3. Si la piel se rompió, busque atención médica el mismo día (infección y tétanos).  <sub>[BITE-CARE]</sub>
- [ ] 4. Si estaba en el extranjero, o fue un murciélago o cualquier animal que pueda tener rabia, busque atención médica de inmediato, aunque la herida parezca pequeña. No espere síntomas ni a volver a casa.  <sub>[BITE-RABIES, BITE-RABIES-THP, BITE-WASH]</sub>
- [ ] ☎ Vaya a urgencias si la herida es grande o profunda, no deja de sangrar, o la mordedura es en la cara o la cabeza. No conduzca usted mismo.  <sub>[BITE-CALL, BITE-DRIVE]</sub>

<details><summary>Sources quoted</summary>

- **BITE-BLEED** NHS, Animal and human bites: "press a dry dressing or clean cloth firmly onto the wound to stop the bleeding if it's bleeding heavily / after cleaning the wound, gently pat it dry and cover it with a clean dressing" (https://www.nhs.uk/conditions/animal-and-human-bites/)
- **BITE-CALL** healthdirect (AU), Dog, cat, bat and human bites: "Go to the emergency department of your nearest hospital if: / your wound is large or deep / you were bitten on your face or head / you can't stop the bleeding" (https://www.healthdirect.gov.au/dog-cat-bat-and-human-bites) CONFLICT: NHS puts a face bite in the 111 tier
- **BITE-CARE** healthdirect (AU), Dog, cat, bat and human bites: "If you are bitten and the skin is broken, get medical advice immediately to avoid developing tetanus." (https://www.healthdirect.gov.au/dog-cat-bat-and-human-bites) CONFLICT (tier): NHS lists criteria (hands, feet, face, head, tetanus > 10 y, hot/swollen) for 111
- **BITE-DRIVE** NHS, Animal and human bites: "Do not drive to A&E. Ask someone to drive you or call 999 and ask for an ambulance." (https://www.nhs.uk/conditions/animal-and-human-bites/)
- **BITE-RABIES** NHS, Rabies: "Urgent advice: Get medical help immediately if: / you've been bitten or scratched by an animal while you're abroad / you've been bitten or scratched by a bat in the UK / If you're abroad, get medical help as soon as possible. Do not wait until you get back to the UK." (https://www.nhs.uk/conditions/rabies/)
- **BITE-RABIES-THP** TravelHealthPro (NaTHNaC, UKHSA-funded), Rabies: "Get urgent medical help, even if the wound or incident seems very trivial. Seek medical attention locally, do not wait until you return to the UK." (https://travelhealthpro.org.uk/factsheets/rabies)
- **BITE-WASH** WHO, Rabies (fact sheet): "If a person is bitten or scratched by a potentially rabid animal, they should immediately and always wash the wound with water and soap for at least 15 minutes and seek medical attention." (https://www.who.int/news-room/fact-sheets/detail/rabies)
- **BITE-WASH-CDC** CDC, Preventing Rabies: "Wash any wounds immediately with soap and water for 15 minutes to flush out any virus." (https://www.cdc.gov/rabies/prevention/index.html)

</details>

Sign-off: [ ] EN  [ ] PT  [ ] ES  [ ] clinical review done  · notes: ____

## Before anything ships
- r4to signs off every card in EN, PT and ES (REVIEW.md checkboxes).
- Clinical review by a qualified person (doctor/paramedic/first-aid trainer), as for the snakebite card.
- Native PT-BR and ES review (ES uses neutral 'usted' and Latin American 'jugo'/'refresco'; Spain would differ).
- Recheck the † (summary-only) CDC quotes by eye.
- Decide the conflicts listed per card (honey, scorpion compress, rescue breaths, infant thrust technique, insulin line, vinegar).
- Engine: es text needs a one-line change (conditionCards.ts reads only en/pt) and the trigger changes in triggers.proposed.mjs; the sources line must not imply NHS endorsement.
