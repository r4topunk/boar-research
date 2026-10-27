# First-aid cards round 4: review sheet for r4to (first-aid-cards draft 2026-10-03, DRAFT, NOT FOR SHIPPING)

TL;DR: DRAFT, NOT FOR SHIPPING. Round 1: 10 cards; round 2: 4 cards (heart attack, head injury, tsunami, hypothermia); round 3: 6 cards (burn, frostbite, heatstroke, nosebleed, earthquake, animal bite); round 4: 9 cards (bleeding, stroke, anaphylaxis, chemical in the eye, electric shock, altitude, sea-creature puncture, tick, heat exhaustion); all EN/PT/ES, every step cited to a verbatim quote from an official source (SOURCES.md). It needs r4to's sign-off on the wording, a clinical review, and native-speaker reviews (PT-BR, ES) before anything ships.

How to review: for each card, read the EN steps against the quotes below them, then PT and ES. Tick a box only if you accept the wording as is; write any change next to it. **Nothing ships without your sign-off** (and the clinical + native-speaker reviews listed at the end).

Automatic checks (check_cards.py): citations on every step = PASS; safety rules v0.8.6 = PASS (0 unsafe in all 87 card-language texts, all rounds).

## bleeding: Severe bleeding
Covers: placeholder bleeding card

**Decisions for you:** (1) Soaked dressing: St John + BRC 'remove and replace with a fresh one, keep firm pressure' vs NHS 'add another on top'. The card follows SJA/BRC. (2) Raising the wound: NHS only; SJA/BRC raise the legs only for shock. Left out (shock line kept). (3) Tourniquet: RCUK 2025 (life-threatening limb bleeding pressure can't control; 5–7 cm above, not on a joint, write the time, don't release). SJA: an improvised one only if the 999 call handler asks. Keep?

**EN: Severe bleeding**

- [ ] 1. Press firmly and directly on the wound with a clean cloth or dressing, and keep pressing.  <sub>[BLEED-PRESS, BLEED-PRESS-BRC]</sub>
- [ ] 2. If blood soaks through, replace it with a fresh pad and keep firm pressure.  <sub>[BLEED-SOAK, BLEED-SOAK-BRC]</sub>
- [ ] 3. If something is stuck in the wound, don't pull it out; press on either side of it instead.  <sub>[BLEED-OBJECT]</sub>
- [ ] 4. For life-threatening bleeding from an arm or leg that pressure doesn't stop, a tourniquet 5–7 cm above the wound (not on a joint) may be needed: note the time and don't loosen it. If you have none, the emergency call handler will tell you what to do.  <sub>[BLEED-TQ, BLEED-TQ-SJA]</sub>
- [ ] 5. If they feel faint or look pale, help them lie down and raise their legs.  <sub>[BLEED-SHOCK]</sub>
- [ ] ☎ Call emergency services now if the bleeding won't stop or spurts out bright red.  <sub>[BLEED-CALL, BLEED-PRESS-BRC]</sub>

**PT: Sangramento forte**

- [ ] 1. Aperte com firmeza diretamente sobre o ferimento com um pano limpo ou curativo, e continue apertando.  <sub>[BLEED-PRESS, BLEED-PRESS-BRC]</sub>
- [ ] 2. Se o sangue atravessar, troque por um pano novo e mantenha a pressão firme.  <sub>[BLEED-SOAK, BLEED-SOAK-BRC]</sub>
- [ ] 3. Se houver algo cravado no ferimento, não retire; aperte dos dois lados do objeto.  <sub>[BLEED-OBJECT]</sub>
- [ ] 4. Para sangramento grave de braço ou perna que a pressão não controla, pode ser preciso um torniquete 5–7 cm acima do ferimento (não sobre uma articulação): anote a hora e não afrouxe. Se não tiver um, o atendente da emergência vai orientar.  <sub>[BLEED-TQ, BLEED-TQ-SJA]</sub>
- [ ] 5. Se a pessoa ficar pálida ou fraca, deite-a e eleve as pernas.  <sub>[BLEED-SHOCK]</sub>
- [ ] ☎ Ligue para a emergência (SAMU 192) agora se o sangramento não parar ou sair em jatos vermelho-vivo.  <sub>[BLEED-CALL, BLEED-PRESS-BRC]</sub>

**ES: Sangrado fuerte**

- [ ] 1. Presione con firmeza directamente sobre la herida con un paño limpio o un apósito, y siga presionando.  <sub>[BLEED-PRESS, BLEED-PRESS-BRC]</sub>
- [ ] 2. Si la sangre lo empapa, cámbielo por uno nuevo y mantenga la presión firme.  <sub>[BLEED-SOAK, BLEED-SOAK-BRC]</sub>
- [ ] 3. Si hay algo clavado en la herida, no lo saque; presione a ambos lados del objeto.  <sub>[BLEED-OBJECT]</sub>
- [ ] 4. Ante un sangrado grave de brazo o pierna que la presión no detiene, puede hacer falta un torniquete 5–7 cm por encima de la herida (no sobre una articulación): anote la hora y no lo afloje. Si no tiene uno, el operador de emergencias le indicará qué hacer.  <sub>[BLEED-TQ, BLEED-TQ-SJA]</sub>
- [ ] 5. Si se marea o se pone pálida, acuéstela y levántele las piernas.  <sub>[BLEED-SHOCK]</sub>
- [ ] ☎ Llame a emergencias ahora si el sangrado no para o sale a chorros rojo brillante.  <sub>[BLEED-CALL, BLEED-PRESS-BRC]</sub>

<details><summary>Sources quoted</summary>

- **BLEED-CALL** NHS, Cuts and grazes: "Immediate action required: Call 999 or go to A&E if: / you have a cut and cannot stop the bleeding / the blood comes out in spurts and is bright red and hard to control" (https://www.nhs.uk/conditions/cuts-and-grazes/)
- **BLEED-OBJECT** NHS, Cuts and grazes: "If there's something stuck in the wound, do not try to take it out. Make sure not to press down on the object. Press firmly either side of it to push the edges of the wound together." (https://www.nhs.uk/conditions/cuts-and-grazes/)
- **BLEED-PRESS** St John Ambulance (UK), Severe bleeding: "Apply direct firm pressure to the wound using a sterile dressing if possible or a clean non-fluffy cloth to stop the bleeding. / Ask a helper to call 999 or 112 for emergency help." (https://www.sja.org.uk/first-aid-advice/severe-bleeding/)
- **BLEED-PRESS-BRC** British Red Cross, Bleeding heavily: "Step 1. Put pressure on the wound with whatever is available to stop or slow down the flow of blood. / Step 2. Call 999. / Step 3. Keep pressure on the wound until help arrives." (https://www.redcross.org.uk/first-aid/learn-first-aid/bleeding-heavily)
- **BLEED-SHOCK** St John Ambulance (UK), Severe bleeding: "Treat them for this by helping them to lie down on a rug or blanket. Raise and support their legs, so that they are above the level of their heart." (https://www.sja.org.uk/first-aid-advice/severe-bleeding/)
- **BLEED-SOAK** St John Ambulance (UK), Severe bleeding: "If blood comes through the dressing, remove it and reapply pressure with a new dressing or pad to control the bleeding." (https://www.sja.org.uk/first-aid-advice/severe-bleeding/) CONFLICT: NHS = add another cloth on top
- **BLEED-SOAK-BRC** British Red Cross, Bleeding heavily: "Remove the item and replace with a fresh one, make sure that firm pressure is applied to the wound." (https://www.redcross.org.uk/first-aid/learn-first-aid/bleeding-heavily)
- **BLEED-TQ** Resuscitation Council UK, First aid guidelines (2025): "Apply a tourniquet as soon as possible for life-threatening extremity bleeding that is not controlled by direct manual pressure: / Place the tourniquet around the traumatised limb 5-7cm above the injury, but not over a joint. / Write the time the tourniquet was applied. / Do not release the tourniquet. It should only be released by a healthcare professional." (https://www.resus.org.uk/professional-library/2025-resuscitation-guidelines/first-aid-guidelines)
- **BLEED-TQ-SJA** St John Ambulance (UK), Severe bleeding: "If the bleed is not controlled with pressure, it is possible that the emergency call handler will ask you to improvise a tourniquet if you do not have one or are not trained." (https://www.sja.org.uk/first-aid-advice/severe-bleeding/)

</details>

Sign-off: [ ] EN  [ ] PT  [ ] ES  [ ] clinical review done  · notes: ____

## stroke: Stroke
Covers: placeholder stroke card

**Decisions for you:** (1) FAST (UK) vs BE FAST (CDC: balance, eyes) vs RÁPIDO (CDC ES). The card lists the FAST signs plus balance/vision in plain words, no mnemonic. (2) Signs that went away: NHS = still call 999; CDC = a TIA, tell a health care team right away. The card follows NHS. (3) 'No food or drink' is St John only; 'no aspirin' is in no source (left out).

**EN: Possible stroke**

- [ ] 1. Check quickly: one side of the face drooping, one arm weak, slurred or strange speech.  <sub>[STROKE-FAST]</sub>
- [ ] 2. Note the time the signs started.  <sub>[STROKE-TIME]</sub>
- [ ] 3. Don't drive them to hospital; wait for the ambulance.  <sub>[STROKE-DRIVE]</sub>
- [ ] 4. Don't give them anything to eat or drink.  <sub>[STROKE-FOOD]</sub>
- [ ] 5. Help them sit or lie down comfortably and reassure them.  <sub>[STROKE-COMFORT]</sub>
- [ ] ☎ Call emergency services now if you see any of these signs, even if they go away.  <sub>[STROKE-CALL, STROKE-FAST]</sub>

**PT: Possível AVC**

- [ ] 1. Confira rápido: um lado do rosto caído, um braço fraco, fala enrolada ou estranha.  <sub>[STROKE-FAST]</sub>
- [ ] 2. Anote a hora em que os sinais começaram.  <sub>[STROKE-TIME]</sub>
- [ ] 3. Não leve a pessoa de carro ao hospital; espere a ambulância.  <sub>[STROKE-DRIVE]</sub>
- [ ] 4. Não dê nada para comer ou beber.  <sub>[STROKE-FOOD]</sub>
- [ ] 5. Ajude a pessoa a sentar ou deitar confortável e tranquilize-a.  <sub>[STROKE-COMFORT]</sub>
- [ ] ☎ Ligue para a emergência (SAMU 192) agora se vir qualquer um desses sinais, mesmo que passem.  <sub>[STROKE-CALL, STROKE-FAST]</sub>

**ES: Posible ictus**

- [ ] 1. Compruebe rápido: un lado de la cara caído, un brazo débil, habla arrastrada o extraña.  <sub>[STROKE-FAST, STROKE-ES]</sub>
- [ ] 2. Anote la hora en que empezaron los signos.  <sub>[STROKE-TIME, STROKE-ES]</sub>
- [ ] 3. No la lleve en coche al hospital; espere a la ambulancia.  <sub>[STROKE-DRIVE, STROKE-ES]</sub>
- [ ] 4. No le dé nada de comer ni de beber.  <sub>[STROKE-FOOD]</sub>
- [ ] 5. Ayúdela a sentarse o acostarse cómoda y tranquilícela.  <sub>[STROKE-COMFORT]</sub>
- [ ] ☎ Llame a emergencias ahora si ve cualquiera de estos signos, aunque desaparezcan.  <sub>[STROKE-CALL, STROKE-ES]</sub>

<details><summary>Sources quoted</summary>

- **STROKE-CALL** NHS, Symptoms of a stroke: "Immediate action required: Call 999 now if: / you've had signs of a stroke within the last 24 hours even if they've now stopped" (https://www.nhs.uk/conditions/stroke/symptoms/) CONFLICT: CDC calls stopped symptoms a TIA → tell a health care team right away
- **STROKE-COMFORT** British Red Cross, Stroke: "Stay calm and let them know that help is on the way. Help them sit or lie down and reassure them while you wait for the ambulance." (https://www.redcross.org.uk/first-aid/learn-first-aid/stroke)
- **STROKE-DRIVE** CDC, Signs and Symptoms of Stroke: "Do not drive to the hospital or let someone else drive you. Call 9-1-1 for an ambulance so that medical personnel can begin life-saving treatment on the way to the emergency room." (https://www.cdc.gov/stroke/signs-symptoms/index.html)
- **STROKE-ES** CDC en español, Signos y síntomas de accidente cerebrovascular: "O: Obtenga ayuda RÁPIDO, ¡llame a emergencias! Si ve alguno de estos signos, llame al 911 de inmediato. / Tome nota de cuándo se presentó por primera vez cualquiera de los síntomas. / No conduzca hacia el hospital ni deje que otra persona lo lleve." (https://www.cdc.gov/stroke/es/signs-symptoms/signos-y-sintomas-de-accidente-cerebrovascular.html)
- **STROKE-FAST** NHS, Symptoms of a stroke: "face weakness – one side of your face may droop (fall) and it might be hard to smile / arm weakness – you may not be able to fully lift both arms and keep them there because of weakness or numbness in 1 arm / speech problems – you may slur your words or sound confused / The easiest way to remember these symptoms is the word FAST. This stands for: face, arms, speech and time to call 999." (https://www.nhs.uk/conditions/stroke/symptoms/) CONFLICT: CDC uses BE FAST (balance, eyes); CDC ES uses RÁPIDO
- **STROKE-FOOD** St John Ambulance (UK), Stroke: "Do not give them anything to eat or drink because it may be hard for them to swallow." (https://www.sja.org.uk/first-aid-advice/stroke/) ok (single source)
- **STROKE-TIME** CDC, Signs and Symptoms of Stroke: "Note the time when any symptoms first appear. This information helps health care providers determine the best treatment." (https://www.cdc.gov/stroke/signs-symptoms/index.html)

</details>

Sign-off: [ ] EN  [ ] PT  [ ] ES  [ ] clinical review done  · notes: ____

## anaphylaxis: Anaphylaxis (severe allergic reaction)
Covers: placeholder anaphylaxis card

**Decisions for you:** (1) Legs: NHS 'you can raise your legs' (optional), SJA legs raised. The card says lie down, legs raised if they can. (2) CPR line only on healthdirect (NHS/RCUK anaphylaxis pages have none).

**EN: Severe allergic reaction (anaphylaxis)**

- [ ] 1. Signs: swelling of the throat or tongue, trouble breathing or wheezing, feeling faint, pale or cold skin.  <sub>[ANA-SIGNS]</sub>
- [ ] 2. Use their adrenaline auto-injector (EpiPen) right away; use a second one after 5 minutes if they're not better.  <sub>[ANA-ADR]</sub>
- [ ] 3. Have them lie down (legs raised if they can; sit up slowly if breathing is hard), and don't let them stand or walk, even if they feel better.  <sub>[ANA-LIE]</sub>
- [ ] 4. If they stop responding and aren't breathing normally, start CPR.  <sub>[ANA-CPR]</sub>
- [ ] ☎ Call emergency services now and say you think it's anaphylaxis.  <sub>[ANA-ADR, ANA-ADR-SJA]</sub>

**PT: Reação alérgica grave (anafilaxia)**

- [ ] 1. Sinais: inchaço na garganta ou na língua, dificuldade para respirar ou chiado, sensação de desmaio, pele pálida ou fria.  <sub>[ANA-SIGNS]</sub>
- [ ] 2. Use a caneta de adrenalina da pessoa na hora; use uma segunda após 5 minutos se não melhorar.  <sub>[ANA-ADR]</sub>
- [ ] 3. Deite a pessoa (pernas elevadas se possível; sentada devagar se respirar for difícil) e não deixe ficar em pé nem caminhar, mesmo que melhore.  <sub>[ANA-LIE]</sub>
- [ ] 4. Se ela parar de responder e não respirar normalmente, comece a RCP.  <sub>[ANA-CPR]</sub>
- [ ] ☎ Ligue para a emergência (SAMU 192) agora e diga que pode ser anafilaxia.  <sub>[ANA-ADR, ANA-ADR-SJA]</sub>

**ES: Reacción alérgica grave (anafilaxia)**

- [ ] 1. Signos: hinchazón de garganta o lengua, dificultad para respirar o pitidos, sensación de desmayo, piel pálida o fría.  <sub>[ANA-SIGNS]</sub>
- [ ] 2. Use su autoinyector de adrenalina de inmediato; use un segundo a los 5 minutos si no mejora.  <sub>[ANA-ADR]</sub>
- [ ] 3. Acuéstela (con las piernas en alto si puede; sentada despacio si le cuesta respirar) y no la deje ponerse de pie ni caminar, aunque se sienta mejor.  <sub>[ANA-LIE]</sub>
- [ ] 4. Si deja de responder y no respira con normalidad, empiece la RCP.  <sub>[ANA-CPR]</sub>
- [ ] ☎ Llame a emergencias ahora y diga que cree que es anafilaxia.  <sub>[ANA-ADR, ANA-ADR-SJA]</sub>

<details><summary>Sources quoted</summary>

- **ANA-ADR** NHS, Anaphylaxis: "Use an adrenaline auto-injector (such as an EpiPen) if you have one – instructions are included on the side of the injector. / Call 999 for an ambulance and say that you think you're having an anaphylactic reaction. / If your symptoms have not improved after 5 minutes, use a 2nd adrenaline auto-injector." (https://www.nhs.uk/conditions/anaphylaxis/) ok (NHS page review overdue)
- **ANA-ADR-SJA** St John Ambulance (UK), Anaphylaxis: "Call 999 or 112 and tell ambulance control that you suspect anaphylaxis." (https://www.sja.org.uk/first-aid-advice/anaphylaxis/)
- **ANA-CPR** healthdirect (AU), Anaphylaxis: "If the person is unresponsive and not breathing normally, start CPR." (https://www.healthdirect.gov.au/anaphylaxis) ok (single source)
- **ANA-LIE** NHS, Anaphylaxis: "Lie down – you can raise your legs, and if you're struggling to breathe, raise your shoulders or sit up slowly (if you're pregnant, lie on your left side). / Do not stand or walk at any time, even if you feel better." (https://www.nhs.uk/conditions/anaphylaxis/)
- **ANA-SIGNS** NHS, Anaphylaxis: "swelling of your throat and tongue / difficulty breathing or breathing very fast / wheezing, coughing or noisy breathing / feeling faint, dizzy or fainting / skin that feels cold to the touch / blue, grey or pale skin, lips or tongue" (https://www.nhs.uk/conditions/anaphylaxis/)

</details>

Sign-off: [ ] EN  [ ] PT  [ ] ES  [ ] clinical review done  · notes: ____

## eyechem: Chemical in the eye
Covers: placeholder eyechem card

**Decisions for you:** (1) Tier: NHS sends only strong chemicals (oven cleaner, bleach) to A&E/999; SJA any chemical splash. The card says 'strong chemical (bleach, oven cleaner) or the eye stays painful/red/blurry' → emergency. (2) Contact lenses: healthdirect 'try to take them out, but not if the eye surface is badly damaged'; SJA 'if they can'.

**EN: Chemical in the eye**

- [ ] 1. Rinse the eye right away with lots of clean, cool (not hot) water for at least 20 minutes, washing inside the eyelids, and keep going while you wait for help.  <sub>[EYE-RINSE, EYE-RINSE-SJA]</sub>
- [ ] 2. Don't let the water run into the other eye.  <sub>[EYE-RINSE-SJA]</sub>
- [ ] 3. Take out contact lenses if you easily can, but not if the eye looks badly damaged.  <sub>[EYE-LENS]</sub>
- [ ] 4. Don't rub the eye.  <sub>[EYE-DONT]</sub>
- [ ] 5. Take the product's container with you.  <sub>[EYE-RINSE]</sub>
- [ ] ☎ Call emergency services or go to the emergency department for a strong chemical such as bleach or oven cleaner; don't drive yourself.  <sub>[EYE-CALL-NHS, EYE-CALL]</sub>

**PT: Produto químico no olho**

- [ ] 1. Lave o olho na hora com muita água limpa e fria (não quente) por pelo menos 20 minutos, por dentro das pálpebras, e continue enquanto espera ajuda.  <sub>[EYE-RINSE, EYE-RINSE-SJA]</sub>
- [ ] 2. Não deixe a água escorrer para o outro olho.  <sub>[EYE-RINSE-SJA]</sub>
- [ ] 3. Tire as lentes de contato se for fácil, mas não se o olho parecer muito machucado.  <sub>[EYE-LENS]</sub>
- [ ] 4. Não esfregue o olho.  <sub>[EYE-DONT]</sub>
- [ ] 5. Leve a embalagem do produto.  <sub>[EYE-RINSE]</sub>
- [ ] ☎ Ligue para a emergência ou vá ao pronto-socorro em caso de produto forte, como água sanitária ou limpa-forno; não vá dirigindo.  <sub>[EYE-CALL-NHS, EYE-CALL]</sub>

**ES: Producto químico en el ojo**

- [ ] 1. Enjuague el ojo de inmediato con mucha agua limpia y fresca (no caliente) durante al menos 20 minutos, por dentro de los párpados, y siga mientras espera ayuda.  <sub>[EYE-RINSE, EYE-RINSE-SJA]</sub>
- [ ] 2. Que el agua no caiga en el otro ojo.  <sub>[EYE-RINSE-SJA]</sub>
- [ ] 3. Quite las lentillas si es fácil, pero no si el ojo parece muy dañado.  <sub>[EYE-LENS]</sub>
- [ ] 4. No se frote el ojo.  <sub>[EYE-DONT]</sub>
- [ ] 5. Lleve el envase del producto.  <sub>[EYE-RINSE]</sub>
- [ ] ☎ Llame a emergencias o vaya a urgencias si es un producto fuerte como lejía o limpiahornos; no conduzca.  <sub>[EYE-CALL-NHS, EYE-CALL]</sub>

<details><summary>Sources quoted</summary>

- **EYE-CALL** St John Ambulance (UK), Eye injury: "For major eye injuries, like a wound, embedded object, or chemical splashes, call 999 or 112 or go to an Emergency Department or Eye Casualty Department." (https://www.sja.org.uk/first-aid-advice/eye-injury/) CONFLICT (tier): NHS = strong chemicals (oven cleaner, bleach) only
- **EYE-CALL-NHS** NHS, Eye injuries: "Immediate action required: Go to A&E or call 999 if: / a strong chemical, such as oven cleaner or bleach, is in your eye / Do not drive to A&E. Ask someone to drive you or call 999 and ask for an ambulance." (https://www.nhs.uk/conditions/eye-injuries/)
- **EYE-DONT** NHS, Eye injuries: "do not touch or rub your eye until it's better" (https://www.nhs.uk/conditions/eye-injuries/)
- **EYE-LENS** healthdirect (AU), Objects or chemicals in the eye: "If you're wearing contact lenses, try to take out your contact lenses. If the surface of your eye is badly damaged do not remove the contact lenses." (https://www.healthdirect.gov.au/objects-or-chemicals-in-eye) CONFLICT (nuance): SJA 'remove them if they can'; NHS no step
- **EYE-RINSE** NHS, Eye injuries: "use clean water (not hot) – this can be from a tap or shower, or bottled water if you're not at home / run lots of water over your eyeball for at least 20 minutes / keep rinsing your eye with water while waiting for medical help, and take the container with you as the information on it may help with treatment" (https://www.nhs.uk/conditions/eye-injuries/)
- **EYE-RINSE-SJA** St John Ambulance (UK), Eye injury: "If it is a chemical splash, hold the casualty’s eye under gently running water for at least 20 minutes and make sure the outside and inside of the eyelid is washed. / Make sure the contaminated water does not splash the uninjured eye, you, or the casualty." (https://www.sja.org.uk/first-aid-advice/eye-injury/)

</details>

Sign-off: [ ] EN  [ ] PT  [ ] ES  [ ] clinical review done  · notes: ____

## electric: Electric shock
Covers: placeholder electric card

**Decisions for you:** (1) Downed power line distance: healthdirect 6 m vs American Red Cross 35 ft (~10.7 m); the old 18 m is in no source. The card says 'at least 10 metres' (the stricter source, rounded). OK? (2) St John's page is low-voltage only; no NHS/BRC electric-shock page exists.

**EN: Electric shock**

- [ ] 1. Don't touch them while they may still be in contact with the electricity.  <sub>[ELEC-OFF, ELEC-OFF-SJA]</sub>
- [ ] 2. Switch off the power at the mains or unplug it first. If you can't, separate them from the source using something dry and wooden, like a broom handle, while standing on something dry.  <sub>[ELEC-OFF, ELEC-OFF-SJA]</sub>
- [ ] 3. If a power line is down, stay at least 10 metres away from it and anything it touches, and call emergency services.  <sub>[ELEC-HV-ARC, ELEC-HV]</sub>
- [ ] 4. If they're not breathing normally, start CPR. Treat burns like any other burn.  <sub>[ELEC-CALL]</sub>
- [ ] 5. Anyone who had an electric shock should get their heart checked.  <sub>[ELEC-CALL]</sub>
- [ ] ☎ Call emergency services if they lost consciousness, have trouble breathing or a fast or slow heartbeat, or after any high-voltage shock.  <sub>[ELEC-CALL, ELEC-CALL-SJA]</sub>

**PT: Choque elétrico**

- [ ] 1. Não toque na pessoa enquanto ela puder estar em contato com a eletricidade.  <sub>[ELEC-OFF, ELEC-OFF-SJA]</sub>
- [ ] 2. Desligue a energia no quadro de luz ou tire da tomada primeiro. Se não der, afaste-a da fonte com algo seco de madeira, como um cabo de vassoura, em pé sobre algo seco.  <sub>[ELEC-OFF, ELEC-OFF-SJA]</sub>
- [ ] 3. Se houver um fio de alta tensão caído, fique a pelo menos 10 metros dele e do que ele toca, e ligue para a emergência.  <sub>[ELEC-HV-ARC, ELEC-HV]</sub>
- [ ] 4. Se ela não respirar normalmente, comece a RCP. Trate queimaduras como qualquer outra queimadura.  <sub>[ELEC-CALL]</sub>
- [ ] 5. Quem levou um choque deve fazer uma avaliação do coração.  <sub>[ELEC-CALL]</sub>
- [ ] ☎ Ligue para a emergência (SAMU 192) se a pessoa desmaiou, tem dificuldade para respirar, batimento acelerado ou lento, ou depois de qualquer choque de alta tensão.  <sub>[ELEC-CALL, ELEC-CALL-SJA]</sub>

**ES: Descarga eléctrica**

- [ ] 1. No toque a la persona mientras pueda seguir en contacto con la electricidad.  <sub>[ELEC-OFF, ELEC-OFF-SJA]</sub>
- [ ] 2. Corte la corriente en el cuadro eléctrico o desenchufe primero. Si no puede, apártela de la fuente con algo seco de madera, como el palo de una escoba, de pie sobre algo seco.  <sub>[ELEC-OFF, ELEC-OFF-SJA]</sub>
- [ ] 3. Si hay un cable de alta tensión caído, manténgase a al menos 10 metros de él y de lo que toque, y llame a emergencias.  <sub>[ELEC-HV-ARC, ELEC-HV]</sub>
- [ ] 4. Si no respira con normalidad, empiece la RCP. Trate las quemaduras como cualquier otra quemadura.  <sub>[ELEC-CALL]</sub>
- [ ] 5. Toda persona que recibió una descarga debe hacerse revisar el corazón.  <sub>[ELEC-CALL]</sub>
- [ ] ☎ Llame a emergencias si perdió el conocimiento, tiene dificultad para respirar, el pulso muy rápido o lento, o tras cualquier descarga de alta tensión.  <sub>[ELEC-CALL, ELEC-CALL-SJA]</sub>

<details><summary>Sources quoted</summary>

- **ELEC-CALL** healthdirect (AU), Electric shocks and burns: "Call an ambulance on triple zero (000) if someone has had an electric shock and has lost consciousness, has difficulty breathing or has a slow or fast heartbeat. / If they are not breathing normally, you should start CPR. / If there is an electrical burn, you can treat it in the same way as you would any other burn. / It's important to get your heart checked after any electric shock." (https://www.healthdirect.gov.au/electric-shocks-and-burns)
- **ELEC-CALL-SJA** St John Ambulance (UK), Electrocution: "Call 999 or 112 for emergency help." (https://www.sja.org.uk/first-aid-advice/electrocution/)
- **ELEC-HV** healthdirect (AU), Electric shocks and burns: "If there is a power line down, stay at least 6 metres away. Do not try to remove a live power cable yourself. Ask the person not to move." (https://www.healthdirect.gov.au/electric-shocks-and-burns) CONFLICT (distance): American Red Cross 35 ft (~10.7 m); the old 18 m is in no source
- **ELEC-HV-ARC** American Red Cross, Power Outage: "Keep away from power lines. Stay at least 35 feet away from fallen power lines and anything they are touching. Call 911 and let them know." (https://www.redcross.org/get-help/how-to-prepare-for-emergencies/types-of-emergencies/power-outage.html)
- **ELEC-OFF** healthdirect (AU), Electric shocks and burns: "Look first, don't touch — the person may still be in contact with the electric current and if you touch them, you can get an electric shock. / Switch off the electricity at the mains, remove fuses, turn off all power points and unplug cords before approaching the person. / If you can't turn off the electricity, use something like a dry wooden broom handle, to separate the person from the electricity source." (https://www.healthdirect.gov.au/electric-shocks-and-burns)
- **ELEC-OFF-SJA** St John Ambulance (UK), Electrocution: "Do not touch the casualty if they’re still in contact with the electrical source as you are at risk of electrocution. / Turn off the source of electricity to break the contact between the electrical supply and the casualty." (https://www.sja.org.uk/first-aid-advice/electrocution/) ok (low-voltage page)

</details>

Sign-off: [ ] EN  [ ] PT  [ ] ES  [ ] clinical review done  · notes: ____

## altitude: Altitude sickness
Covers: placeholder altitude card (vit-hlt-002-type questions)

**Decisions for you:** (1) When to descend: NHS = worse or not better after 1 day; CDC = worse despite rest. The card follows NHS (stricter). (2) CDC source is the Yellow Book clinician chapter (no CDC traveller page exists).

**EN: Altitude sickness (headache, nausea, dizziness, tiredness at altitude)**

- [ ] 1. Stop and rest at the same altitude until you feel better; don't go higher, and never go up to sleep higher with symptoms.  <sub>[ALT-STOP, ALT-NEVER]</sub>
- [ ] 2. Don't use alcohol or sleeping pills to help you sleep at altitude.  <sub>[ALT-ALCOHOL]</sub>
- [ ] 3. If symptoms get worse or don't improve after a day, go down about 300 to 1,000 metres.  <sub>[ALT-STOP]</sub>
- [ ] ☎ Go down straight away and get medical help immediately (call emergency services if you can) if they are confused, unsteady, breathless at rest, coughing up frothy or bloody spit, or very sleepy.  <sub>[ALT-SEVERE]</sub>

**PT: Mal da altitude (dor de cabeça, enjoo, tontura, cansaço na altitude)**

- [ ] 1. Pare e descanse na mesma altitude até melhorar; não suba mais, e nunca suba para dormir mais alto com sintomas.  <sub>[ALT-STOP, ALT-NEVER]</sub>
- [ ] 2. Não use álcool nem remédio para dormir na altitude.  <sub>[ALT-ALCOHOL]</sub>
- [ ] 3. Se os sintomas piorarem ou não melhorarem em um dia, desça cerca de 300 a 1.000 metros.  <sub>[ALT-STOP]</sub>
- [ ] ☎ Desça imediatamente e procure ajuda médica na hora (ligue para a emergência se puder) se a pessoa estiver confusa, cambaleando, com falta de ar em repouso, tossindo espuma ou sangue, ou muito sonolenta.  <sub>[ALT-SEVERE]</sub>

**ES: Mal de altura (dolor de cabeza, náuseas, mareo, cansancio en altura)**

- [ ] 1. Pare y descanse a la misma altura hasta sentirse mejor; no suba más, y nunca suba a dormir más alto con síntomas.  <sub>[ALT-STOP, ALT-NEVER]</sub>
- [ ] 2. No use alcohol ni pastillas para dormir en altura.  <sub>[ALT-ALCOHOL]</sub>
- [ ] 3. Si los síntomas empeoran o no mejoran en un día, baje unos 300 a 1.000 metros.  <sub>[ALT-STOP]</sub>
- [ ] ☎ Baje de inmediato y busque ayuda médica enseguida (llame a emergencias si puede) si está confundida, se tambalea, le falta el aire en reposo, tose espuma o sangre, o está muy somnolienta.  <sub>[ALT-SEVERE]</sub>

<details><summary>Sources quoted</summary>

- **ALT-ALCOHOL** CDC Yellow Book, High-Altitude Travel and Altitude Illness: "Respiratory depressants such as alcohol and opiates should not be used to aid sleep at high altitude." (https://www.cdc.gov/yellow-book/hcp/environmental-hazards-risks/high-altitude-travel-and-altitude-illness.html)
- **ALT-NEVER** CDC Yellow Book, High-Altitude Travel and Altitude Illness: "Never ascend to sleep at a higher altitude when experiencing symptoms of altitude illness, no matter how minor the symptoms seem." (https://www.cdc.gov/yellow-book/hcp/environmental-hazards-risks/high-altitude-travel-and-altitude-illness.html) ok (clinician chapter)
- **ALT-SEVERE** NHS, Altitude sickness: "Urgent advice: Get medical help immediately if: / are confused / have problems with balance or coordination / feel short of breath, even when resting / have a cough or are coughing up frothy or bloody spit / are very sleepy or difficult to wake / Go to a lower altitude straight away (around 300 to 1,000 metres lower) if you can." (https://www.nhs.uk/conditions/altitude-sickness/)
- **ALT-STOP** NHS, Altitude sickness: "rest at the same altitude until you feel better – do not travel or climb to a higher altitude / If your symptoms get worse or do not improve after 1 day, go to a lower altitude if you can. Try to go around 300 to 1,000 metres lower." (https://www.nhs.uk/conditions/altitude-sickness/) CONFLICT: CDC = descend if worse despite rest (no day count)

</details>

Sign-off: [ ] EN  [ ] PT  [ ] ES  [ ] clinical review done  · notes: ____

## marinepuncture: Stingray, sea urchin, weever or stonefish
Covers: placeholder marinepuncture card

**Decisions for you:** (1) Hot water: NHS 'as hot as can be tolerated, at least 30 minutes'; healthdirect 45 °C up to 90 min for fish/stingray. The card says 30–90 minutes, as hot as tolerated. (2) Spines: NHS remove; healthdirect leave STONEFISH spines in. The card splits by creature. (3) Stingray alone: NHS minor injuries unit (not 999); stonefish: emergency (healthdirect).

**EN: Stingray, sea urchin, weever or stonefish**

- [ ] 1. Soak the area in very hot water, as hot as they can bear without burning, for 30 to 90 minutes.  <sub>[SEA-HOT]</sub>
- [ ] 2. Remove spines near the surface with tweezers or the edge of a card (not bare hands), but leave a stonefish spine in.  <sub>[SEA-SPINE, SEA-STONEFISH]</sub>
- [ ] 3. Don't put ice on it, don't cover or close the wound, and don't pee on it.  <sub>[SEA-DONT]</sub>
- [ ] 4. A stingray wound should be checked at a clinic or minor injuries unit.  <sub>[SEA-CALL]</sub>
- [ ] ☎ Call emergency services for a stonefish sting, or if they have trouble breathing, chest pain, severe swelling or bleeding, or feel faint.  <sub>[SEA-CALL, SEA-STONEFISH]</sub>

**PT: Arraia, ouriço-do-mar, peixe-aranha ou peixe-pedra**

- [ ] 1. Deixe a área em água bem quente, o mais quente que a pessoa aguentar sem se queimar, por 30 a 90 minutos.  <sub>[SEA-HOT]</sub>
- [ ] 2. Tire os espinhos superficiais com pinça ou a borda de um cartão (sem as mãos), mas deixe o espinho de peixe-pedra.  <sub>[SEA-SPINE, SEA-STONEFISH]</sub>
- [ ] 3. Não ponha gelo, não cubra nem feche o ferimento e não faça xixi no local.  <sub>[SEA-DONT]</sub>
- [ ] 4. Ferimento de arraia deve ser avaliado num posto de saúde ou pronto atendimento.  <sub>[SEA-CALL]</sub>
- [ ] ☎ Ligue para a emergência em caso de peixe-pedra, ou se houver falta de ar, dor no peito, inchaço ou sangramento forte, ou sensação de desmaio.  <sub>[SEA-CALL, SEA-STONEFISH]</sub>

**ES: Raya, erizo de mar, pez araña o pez piedra**

- [ ] 1. Sumerja la zona en agua muy caliente, lo más caliente que tolere sin quemarse, durante 30 a 90 minutos.  <sub>[SEA-HOT]</sub>
- [ ] 2. Quite las espinas superficiales con pinzas o el borde de una tarjeta (sin las manos), pero deje la espina del pez piedra.  <sub>[SEA-SPINE, SEA-STONEFISH]</sub>
- [ ] 3. No ponga hielo, no cubra ni cierre la herida y no orine sobre ella.  <sub>[SEA-DONT]</sub>
- [ ] 4. Una herida de raya debe revisarse en un centro de salud.  <sub>[SEA-CALL]</sub>
- [ ] ☎ Llame a emergencias si es un pez piedra, o si hay dificultad para respirar, dolor en el pecho, hinchazón o sangrado fuertes, o sensación de desmayo.  <sub>[SEA-CALL, SEA-STONEFISH]</sub>

<details><summary>Sources quoted</summary>

- **SEA-CALL** NHS, Jellyfish and other sea creature stings: "Non-urgent advice: Go to a minor injuries unit if: / you've been stung by a stingray / Immediate action required: Go to A&E or call 999 if: / difficulty breathing / chest pain / severe swelling around the affected area / severe bleeding / lightheadedness or loss of consciousness" (https://www.nhs.uk/conditions/jellyfish-and-other-sea-creature-stings/)
- **SEA-DONT** NHS, Jellyfish and other sea creature stings: "do not apply ice or a cold pack / do not cover or close the wound / do not pee on the sting" (https://www.nhs.uk/conditions/jellyfish-and-other-sea-creature-stings/)
- **SEA-HOT** NHS, Jellyfish and other sea creature stings: "soak the area in very warm water (as hot as can be tolerated) for at least 30 minutes – use hot flannels or towels if you cannot soak it" (https://www.nhs.uk/conditions/jellyfish-and-other-sea-creature-stings/) CONFLICT (time/°C): healthdirect fish/stingray 45 °C up to 90 min; stonefish up to 30 min; urchin 20 min
- **SEA-SPINE** NHS, Jellyfish and other sea creature stings: "remove any spines from the skin using tweezers or the edge of a bank card / do not touch any tentacles or spines with your bare hands" (https://www.nhs.uk/conditions/jellyfish-and-other-sea-creature-stings/) CONFLICT: healthdirect = leave stonefish spines in
- **SEA-STONEFISH** healthdirect (AU), Sea creature bites and stings: "Leave the spine in the skin — unless the ambulance operator tells you to remove it. / are stung by a stonefish or other stinging fish / Call triple zero (000) and ask for an ambulance." (https://www.healthdirect.gov.au/sea-creature-stings)

</details>

Sign-off: [ ] EN  [ ] PT  [ ] ES  [ ] clinical review done  · notes: ____

## tick: Tick bite
Covers: placeholder tick card

**Decisions for you:** (1) DIRECT CONTRADICTION by region: UK/US (CDC, NHS, St John) = fine-tipped tweezers, never burn or freeze; Australia (healthdirect, ASCIA) = freeze with an ether spray, never tweezers. The card gives the UK/US method and an Australia line. OK, or region-split the card?

**EN: Tick bite**

- [ ] 1. With fine-tipped tweezers, grab the tick as close to the skin as possible and pull straight up with steady pressure, without squeezing it.  <sub>[TICK-REMOVE, TICK-REMOVE-NHS]</sub>
- [ ] 2. Don't twist or jerk it. Don't use heat, petroleum jelly or nail polish.  <sub>[TICK-REMOVE, TICK-DONT]</sub>
- [ ] 3. Clean the bite and your hands with soap and water.  <sub>[TICK-REMOVE]</sub>
- [ ] 4. In Australia, health services advise freezing the tick with an ether spray instead of tweezers; if it won't drop off, get urgent medical help.  <sub>[TICK-AU]</sub>
- [ ] 5. Watch the bite for up to 3 months: a growing round or bullseye rash, fever or flu-like symptoms mean you should see a doctor soon.  <sub>[TICK-WATCH, TICK-WATCH-CDC]</sub>
- [ ] ☎ Call emergency services if signs of a severe allergic reaction appear (swelling of the throat or tongue, trouble breathing).  <sub>[ANA-SIGNS, ANA-ADR]</sub>

**PT: Picada de carrapato**

- [ ] 1. Com uma pinça de ponta fina, segure o carrapato o mais perto possível da pele e puxe para cima com força constante, sem apertá-lo.  <sub>[TICK-REMOVE, TICK-REMOVE-NHS]</sub>
- [ ] 2. Não torça nem puxe de uma vez, e não use vaselina, esmalte nem calor.  <sub>[TICK-REMOVE, TICK-DONT]</sub>
- [ ] 3. Lave a picada e as mãos com água e sabão.  <sub>[TICK-REMOVE]</sub>
- [ ] 4. Na Austrália, os serviços de saúde orientam congelar o carrapato com spray de éter em vez de usar pinça; se ele não cair, procure ajuda médica urgente.  <sub>[TICK-AU]</sub>
- [ ] 5. Observe a picada por até 3 meses: mancha redonda que cresce ou em forma de alvo, febre ou sintomas de gripe pedem uma consulta médica logo.  <sub>[TICK-WATCH, TICK-WATCH-CDC]</sub>
- [ ] ☎ Ligue para a emergência se surgirem sinais de alergia grave (inchaço na garganta ou na língua, falta de ar).  <sub>[ANA-SIGNS, ANA-ADR]</sub>

**ES: Picadura de garrapata**

- [ ] 1. Con una pinza de punta fina, agarre la garrapata lo más cerca posible de la piel y tire hacia arriba con presión constante, sin apretarla.  <sub>[TICK-REMOVE, TICK-REMOVE-NHS]</sub>
- [ ] 2. No la tuerza ni la arranque de un tirón, y no use vaselina, esmalte ni calor.  <sub>[TICK-REMOVE, TICK-DONT]</sub>
- [ ] 3. Lave la picadura y las manos con agua y jabón.  <sub>[TICK-REMOVE]</sub>
- [ ] 4. En Australia, los servicios de salud aconsejan congelar la garrapata con un spray de éter en lugar de usar pinzas; si no se cae, busque ayuda médica urgente.  <sub>[TICK-AU]</sub>
- [ ] 5. Vigile la picadura hasta 3 meses: un sarpullido redondo que crece o en forma de diana, fiebre o síntomas de gripe indican que debe ver a un médico pronto.  <sub>[TICK-WATCH, TICK-WATCH-CDC]</sub>
- [ ] ☎ Llame a emergencias si aparecen signos de alergia grave (hinchazón de garganta o lengua, dificultad para respirar).  <sub>[ANA-SIGNS, ANA-ADR]</sub>

<details><summary>Sources quoted</summary>

- **ANA-ADR** NHS, Anaphylaxis: "Use an adrenaline auto-injector (such as an EpiPen) if you have one – instructions are included on the side of the injector. / Call 999 for an ambulance and say that you think you're having an anaphylactic reaction. / If your symptoms have not improved after 5 minutes, use a 2nd adrenaline auto-injector." (https://www.nhs.uk/conditions/anaphylaxis/) ok (NHS page review overdue)
- **ANA-SIGNS** NHS, Anaphylaxis: "swelling of your throat and tongue / difficulty breathing or breathing very fast / wheezing, coughing or noisy breathing / feeling faint, dizzy or fainting / skin that feels cold to the touch / blue, grey or pale skin, lips or tongue" (https://www.nhs.uk/conditions/anaphylaxis/)
- **TICK-AU** healthdirect (AU), Tick bites: "If you have a tick, you should kill it as soon as possible by freezing it with an ether-containing product. / Do not try to remove ticks with tweezers. / If the tick does not drop off, or can't be frozen, leave it in place and get urgent medical help." (https://www.healthdirect.gov.au/tick-bites) CONFLICT with UK/US: region-specific
- **TICK-DONT** CDC, What to Do After a Tick Bite: "Do not use petroleum jelly, heat, nail polish, or other substances to try and make the tick detach from the skin." (https://www.cdc.gov/ticks/after-a-tick-bite/index.html)
- **TICK-REMOVE** CDC, What to Do After a Tick Bite: "Grasp the tick as close to the skin's surface as possible using clean fine-tipped tweezers. / Pull tick away from the skin with steady, even pressure. Don't twist or jerk the tick. / After removing the tick, thoroughly clean the bite area and your hands with soap and water, rubbing alcohol, or hand sanitizer." (https://www.cdc.gov/ticks/after-a-tick-bite/index.html) CONFLICT: Australia (healthdirect, ASCIA) = freeze, no tweezers
- **TICK-REMOVE-NHS** NHS, Lyme disease: "Slowly pull upwards, taking care not to squeeze or crush the tick." (https://www.nhs.uk/conditions/lyme-disease/)
- **TICK-WATCH** NHS, Lyme disease: "The rash can appear up to 3 months after being bitten by an infected tick, but usually appears within 1 to 4 weeks. / The rash may look like a bullseye on a dartboard. / Urgent advice: Ask for an urgent GP appointment or get help from NHS 111 if: / feel unwell with flu-like symptoms" (https://www.nhs.uk/conditions/lyme-disease/)
- **TICK-WATCH-CDC** CDC, What to Do After a Tick Bite: "If you develop a rash or fever within several weeks of removing a tick, see your doctor:" (https://www.cdc.gov/ticks/after-a-tick-bite/index.html)

</details>

Sign-off: [ ] EN  [ ] PT  [ ] ES  [ ] clinical review done  · notes: ____

## heatexhaustion: Heat exhaustion
Covers: placeholder heatexhaustion card

**Decisions for you:** (1) 'Lie down with legs raised' is St John only (NHS's 4 steps don't have it). Left out. (2) Confusion or no sweating = heatstroke → the heatstroke card (no plain-water advice there).

**EN: Heat exhaustion**

- [ ] 1. Move them to a cool place and take off extra clothing.  <sub>[HEX-STEPS]</sub>
- [ ] 2. Give plenty of water to drink, or a sports drink or rehydration solution.  <sub>[HEX-STEPS]</sub>
- [ ] 3. Cool their skin: spray or sponge with cool water and fan them; cold packs wrapped in a cloth in the armpits or on the neck.  <sub>[HEX-STEPS]</sub>
- [ ] 4. They should feel better within 30 minutes.  <sub>[HEX-STEPS]</sub>
- [ ] ☎ Call emergency services if they're still unwell after 30 minutes, or if they become confused, stop sweating, have a seizure or pass out (that's heatstroke).  <sub>[HEX-CALL]</sub>

**PT: Exaustão pelo calor**

- [ ] 1. Leve a pessoa para um lugar fresco e tire o excesso de roupa.  <sub>[HEX-STEPS]</sub>
- [ ] 2. Dê bastante água para beber, ou bebida isotônica ou soro de reidratação.  <sub>[HEX-STEPS]</sub>
- [ ] 3. Resfrie a pele: borrife ou passe água fresca e abane; bolsas frias enroladas num pano nas axilas ou no pescoço.  <sub>[HEX-STEPS]</sub>
- [ ] 4. Ela deve melhorar em até 30 minutos.  <sub>[HEX-STEPS]</sub>
- [ ] ☎ Ligue para a emergência se ainda estiver mal depois de 30 minutos, ou se ficar confusa, parar de suar, tiver convulsão ou desmaiar (isso é insolação grave).  <sub>[HEX-CALL]</sub>

**ES: Agotamiento por calor**

- [ ] 1. Lleve a la persona a un lugar fresco y quítele la ropa de más.  <sub>[HEX-STEPS]</sub>
- [ ] 2. Dele mucha agua para beber, o una bebida isotónica o suero de rehidratación.  <sub>[HEX-STEPS]</sub>
- [ ] 3. Enfríe la piel: rocíe o pase agua fresca y abaníquela; bolsas frías envueltas en un paño en las axilas o el cuello.  <sub>[HEX-STEPS]</sub>
- [ ] 4. Debería sentirse mejor en 30 minutos.  <sub>[HEX-STEPS]</sub>
- [ ] ☎ Llame a emergencias si sigue mal después de 30 minutos, o si se confunde, deja de sudar, tiene una convulsión o se desmaya (eso es un golpe de calor).  <sub>[HEX-CALL]</sub>

<details><summary>Sources quoted</summary>

- **HEX-CALL** NHS, Heat exhaustion and heatstroke: "Immediate action required: Call 999 now if: / still being unwell after 30 minutes of resting in a cool place, being cooled and drinking fluids / hot skin that's not sweating and might look red / confusion and lack of coordination / a seizure or fit / loss of consciousness" (https://www.nhs.uk/conditions/heat-exhaustion-heatstroke/)
- **HEX-STEPS** NHS, Heat exhaustion and heatstroke: "Move them to a cool place. / Remove all unnecessary clothing like a jacket or socks. / Give them plenty of water to drink – you can also give them an isotonic sports drink or oral rehydration powder that you mix with water, which will help replace salt lost through sweating. / Cool their skin – spray or sponge them with cool water and fan them. Cold packs, wrapped in a cloth and put under the armpits or on the neck are good too. / They should start to cool down and feel better within 30 minutes." (https://www.nhs.uk/conditions/heat-exhaustion-heatstroke/)

</details>

Sign-off: [ ] EN  [ ] PT  [ ] ES  [ ] clinical review done  · notes: ____

## Before anything ships
- r4to signs off every card in EN, PT and ES (REVIEW.md checkboxes).
- Clinical review by a qualified person (doctor/paramedic/first-aid trainer), as for the snakebite card.
- Native PT-BR and ES review (ES uses neutral 'usted' and Latin American 'jugo'/'refresco'; Spain would differ).
- Recheck the † (summary-only) CDC quotes by eye.
- Decide the conflicts listed per card (honey, scorpion compress, rescue breaths, infant thrust technique, insulin line, vinegar).
- Engine: es text needs a one-line change (conditionCards.ts reads only en/pt) and the trigger changes in triggers.proposed.mjs; the sources line must not imply NHS endorsement.
