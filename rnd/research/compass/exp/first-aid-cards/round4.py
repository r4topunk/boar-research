"""Round 4 (Compass, 2026-10-03): the last 9 placeholders: bleeding, stroke, anaphylaxis, eyechem, electric, altitude,
marinepuncture, tick, heatexhaustion. Imported by build_cards.py. Sources: SOURCES.raw-4.md (all curl, 233/233 exact)."""

NHS_CUT, SJA_BLEED, BRC_BLEED, RCUK = ("https://www.nhs.uk/conditions/cuts-and-grazes/", "https://www.sja.org.uk/first-aid-advice/severe-bleeding/",
    "[quote withheld (copyright); see url]", "https://www.resus.org.uk/professional-library/2025-resuscitation-guidelines/first-aid-guidelines")
SJA_LTB = "https://www.sja.org.uk/first-aid-advice/life-threatening-bleed/"
NHS_STROKE, CDC_STROKE, SJA_STROKE, BRC_STROKE = ("https://www.nhs.uk/conditions/stroke/symptoms/", "https://www.cdc.gov/stroke/signs-symptoms/index.html",
    "https://www.sja.org.uk/first-aid-advice/stroke/", "https://www.redcross.org.uk/first-aid/learn-first-aid/stroke")
CDC_STROKE_ES = "https://www.cdc.gov/stroke/es/signs-symptoms/signos-y-sintomas-de-accidente-cerebrovascular.html"
NHS_ANA, SJA_ANA, HD_ANA = "https://www.nhs.uk/conditions/anaphylaxis/", "https://www.sja.org.uk/first-aid-advice/anaphylaxis/", "[quote withheld (copyright); see url]"
NHS_EYE, SJA_EYE, HD_EYE = "https://www.nhs.uk/conditions/eye-injuries/", "https://www.sja.org.uk/first-aid-advice/eye-injury/", "[quote withheld (copyright); see url]"
SJA_ELEC, HD_ELEC, ARC_PO = ("https://www.sja.org.uk/first-aid-advice/electrocution/", "https://www.healthdirect.gov.au/electric-shocks-and-burns",
    "[quote withheld (copyright); see url]")
NHS_ALT, CDC_ALT = "https://www.nhs.uk/conditions/altitude-sickness/", "https://www.cdc.gov/yellow-book/hcp/environmental-hazards-risks/high-altitude-travel-and-altitude-illness.html"
NHS_SEA, HD_SEA = "https://www.nhs.uk/conditions/jellyfish-and-other-sea-creature-stings/", "https://www.healthdirect.gov.au/sea-creature-stings"
CDC_TICK, NHS_LYME, SJA_TICK, HD_TICK = ("https://www.cdc.gov/ticks/after-a-tick-bite/index.html", "https://www.nhs.uk/conditions/lyme-disease/",
    "[NHS quote withheld; see url]", "https://www.healthdirect.gov.au/tick-bites")
NHS_HEAT, SJA_HEX = "https://www.nhs.uk/conditions/heat-exhaustion-heatstroke/", "https://www.sja.org.uk/first-aid-advice/heat-exhaustion/"

S4 = {
 "BLEED-PRESS": ("St John Ambulance (UK), Severe bleeding", SJA_BLEED, "[quote withheld (copyright); see url]", "ok"),
 "BLEED-PRESS-BRC": ("British Red Cross, Bleeding heavily", BRC_BLEED, "[quote withheld (copyright); see url]", "ok"),
 "BLEED-SOAK": ("St John Ambulance (UK), Severe bleeding", SJA_BLEED, "[quote withheld (copyright); see url]", "CONFLICT: NHS = add another cloth on top"),
 "BLEED-SOAK-BRC": ("British Red Cross, Bleeding heavily", BRC_BLEED, "[quote withheld (copyright); see url]", "ok"),
 "BLEED-OBJECT": ("NHS, Cuts and grazes", NHS_CUT, "[NHS quote withheld]", "ok"),
 "BLEED-TQ": ("Resuscitation Council UK, First aid guidelines (2025)", RCUK, "[quote withheld (copyright); see url]", "ok"),
 "BLEED-TQ-SJA": ("St John Ambulance (UK), Severe bleeding", SJA_BLEED, "[quote withheld (copyright); see url]", "ok"),
 "BLEED-SHOCK": ("St John Ambulance (UK), Severe bleeding", SJA_BLEED, "[quote withheld (copyright); see url]", "ok"),
 "BLEED-CALL": ("NHS, Cuts and grazes", NHS_CUT, "[NHS quote withheld]", "ok"),
 "STROKE-FAST": ("NHS, Symptoms of a stroke", NHS_STROKE, "[NHS quote withheld]", "CONFLICT: CDC uses BE FAST (balance, eyes); CDC ES uses RÁPIDO"),
 "STROKE-CALL": ("NHS, Symptoms of a stroke", NHS_STROKE, "[NHS quote withheld]", "CONFLICT: CDC calls stopped symptoms a TIA → tell a health care team right away"),
 "STROKE-TIME": ("CDC, Signs and Symptoms of Stroke", CDC_STROKE, "Note the time when any symptoms first appear. This information helps health care providers determine the best treatment.", "ok"),
 "STROKE-DRIVE": ("CDC, Signs and Symptoms of Stroke", CDC_STROKE, "Do not drive to the hospital or let someone else drive you. Call 9-1-1 for an ambulance so that medical personnel can begin life-saving treatment on the way to the emergency room.", "ok"),
 "STROKE-FOOD": ("St John Ambulance (UK), Stroke", SJA_STROKE, "[quote withheld (copyright); see url]", "ok (single source)"),
 "STROKE-COMFORT": ("British Red Cross, Stroke", BRC_STROKE, "[quote withheld (copyright); see url]", "ok"),
 "STROKE-ES": ("CDC en español, Signos y síntomas de accidente cerebrovascular", CDC_STROKE_ES, "O: Obtenga ayuda RÁPIDO, ¡llame a emergencias! Si ve alguno de estos signos, llame al 911 de inmediato. / Tome nota de cuándo se presentó por primera vez cualquiera de los síntomas. / No conduzca hacia el hospital ni deje que otra persona lo lleve.", "ok"),
 "ANA-ADR": ("NHS, Anaphylaxis", NHS_ANA, "[NHS quote withheld]", "ok (NHS page review overdue)"),
 "ANA-ADR-SJA": ("St John Ambulance (UK), Anaphylaxis", SJA_ANA, "[quote withheld (copyright); see url]", "ok"),
 "ANA-LIE": ("NHS, Anaphylaxis", NHS_ANA, "[NHS quote withheld]", "ok"),
 "ANA-SIGNS": ("NHS, Anaphylaxis", NHS_ANA, "[NHS quote withheld]", "ok"),
 "ANA-CPR": ("healthdirect (AU), Anaphylaxis", HD_ANA, "[quote withheld (copyright); see url]", "ok (single source)"),
 "EYE-RINSE": ("NHS, Eye injuries", NHS_EYE, "[NHS quote withheld]", "ok"),
 "EYE-RINSE-SJA": ("St John Ambulance (UK), Eye injury", SJA_EYE, "[quote withheld (copyright); see url]", "ok"),
 "EYE-LENS": ("healthdirect (AU), Objects or chemicals in the eye", HD_EYE, "[quote withheld (copyright); see url]", "CONFLICT (nuance): SJA 'remove them if they can'; NHS no step"),
 "EYE-DONT": ("NHS, Eye injuries", NHS_EYE, "[NHS quote withheld]", "ok"),
 "EYE-CALL": ("St John Ambulance (UK), Eye injury", SJA_EYE, "[quote withheld (copyright); see url]", "CONFLICT (tier): NHS = strong chemicals (oven cleaner, bleach) only"),
 "EYE-CALL-NHS": ("NHS, Eye injuries", NHS_EYE, "[NHS quote withheld]", "ok"),
 "ELEC-OFF": ("healthdirect (AU), Electric shocks and burns", HD_ELEC, "[quote withheld (copyright); see url]", "ok"),
 "ELEC-OFF-SJA": ("St John Ambulance (UK), Electrocution", SJA_ELEC, "[quote withheld (copyright); see url]", "ok (low-voltage page)"),
 "ELEC-HV": ("healthdirect (AU), Electric shocks and burns", HD_ELEC, "[quote withheld (copyright); see url]", "CONFLICT (distance): American Red Cross 35 ft (~10.7 m); the old 18 m is in no source"),
 "ELEC-HV-ARC": ("American Red Cross, Power Outage", ARC_PO, "[quote withheld (copyright); see url]", "ok"),
 "ELEC-CALL": ("healthdirect (AU), Electric shocks and burns", HD_ELEC, "[quote withheld (copyright); see url]", "ok"),
 "ELEC-CALL-SJA": ("St John Ambulance (UK), Electrocution", SJA_ELEC, "[quote withheld (copyright); see url]", "ok"),
 "ALT-STOP": ("NHS, Altitude sickness", NHS_ALT, "[NHS quote withheld]", "CONFLICT: CDC = descend if worse despite rest (no day count)"),
 "ALT-NEVER": ("CDC Yellow Book, High-Altitude Travel and Altitude Illness", CDC_ALT, "Never ascend to sleep at a higher altitude when experiencing symptoms of altitude illness, no matter how minor the symptoms seem.", "ok (clinician chapter)"),
 "ALT-SEVERE": ("NHS, Altitude sickness", NHS_ALT, "[NHS quote withheld]", "ok"),
 "ALT-ALCOHOL": ("CDC Yellow Book, High-Altitude Travel and Altitude Illness", CDC_ALT, "Respiratory depressants such as alcohol and opiates should not be used to aid sleep at high altitude.", "ok"),
 "SEA-HOT": ("NHS, Jellyfish and other sea creature stings", NHS_SEA, "[NHS quote withheld]", "CONFLICT (time/°C): healthdirect fish/stingray 45 °C up to 90 min; stonefish up to 30 min; urchin 20 min"),
 "SEA-SPINE": ("NHS, Jellyfish and other sea creature stings", NHS_SEA, "[NHS quote withheld]", "CONFLICT: healthdirect = leave stonefish spines in"),
 "SEA-STONEFISH": ("healthdirect (AU), Sea creature bites and stings", HD_SEA, "[quote withheld (copyright); see url]", "ok"),
 "SEA-DONT": ("NHS, Jellyfish and other sea creature stings", NHS_SEA, "[NHS quote withheld]", "ok"),
 "SEA-CALL": ("NHS, Jellyfish and other sea creature stings", NHS_SEA, "[NHS quote withheld]", "ok"),
 "TICK-REMOVE": ("CDC, What to Do After a Tick Bite", CDC_TICK, "Grasp the tick as close to the skin's surface as possible using clean fine-tipped tweezers. / Pull tick away from the skin with steady, even pressure. Don't twist or jerk the tick. / After removing the tick, thoroughly clean the bite area and your hands with soap and water, rubbing alcohol, or hand sanitizer.", "CONFLICT: Australia (healthdirect, ASCIA) = freeze, no tweezers"),
 "TICK-REMOVE-NHS": ("NHS, Lyme disease", NHS_LYME, "[NHS quote withheld]", "ok"),
 "TICK-DONT": ("CDC, What to Do After a Tick Bite", CDC_TICK, "Do not use petroleum jelly, heat, nail polish, or other substances to try and make the tick detach from the skin.", "ok"),
 "TICK-AU": ("healthdirect (AU), Tick bites", HD_TICK, "[quote withheld (copyright); see url]", "CONFLICT with UK/US: region-specific"),
 "TICK-WATCH": ("NHS, Lyme disease", NHS_LYME, "[NHS quote withheld]", "ok"),
 "TICK-WATCH-CDC": ("CDC, What to Do After a Tick Bite", CDC_TICK, "If you develop a rash or fever within several weeks of removing a tick, see your doctor:", "ok"),
 "HEX-STEPS": ("NHS, Heat exhaustion and heatstroke", NHS_HEAT, "[NHS quote withheld]", "ok"),
 "HEX-LIE": ("St John Ambulance (UK), Heat exhaustion", SJA_HEX, "[quote withheld (copyright); see url]", "CONFLICT: not on NHS"),
 "HEX-CALL": ("NHS, Heat exhaustion and heatstroke", NHS_HEAT, "[NHS quote withheld]", "ok"),
}


def build(st, L):
    C = []
    C.append({"id": "bleeding", "round": 4, "condition": "Severe bleeding", "covers": "placeholder bleeding card",
     "topic": {"en": "severe bleeding, won't stop bleeding", "pt": "sangramento forte, não para de sangrar", "es": "sangrado fuerte, no para de sangrar"},
     "rules": ["bleed-remove-object"],
     "review_flags": ["Soaked dressing: St John + BRC [quote withheld; replace the soaked dressing and keep pressing] vs NHS [NHS quote withheld]. The card follows SJA/BRC.",
                      "Raising the wound: NHS only; SJA/BRC raise the legs only for shock. Left out (shock line kept).",
                      "Tourniquet: RCUK 2025 (life-threatening limb bleeding pressure can't control; 5–7 cm above, not on a joint, write the time, don't release). SJA: an improvised one only if the 999 call handler asks. Keep?"],
     "langs": {
      "en": L("Severe bleeding", [
          st("Press firmly and directly on the wound with a clean cloth or dressing, and keep pressing.", "BLEED-PRESS", "BLEED-PRESS-BRC"),
          st("If blood soaks through, replace it with a fresh pad and keep firm pressure.", "BLEED-SOAK", "BLEED-SOAK-BRC"),
          st("If something is stuck in the wound, don't pull it out; press on either side of it instead.", "BLEED-OBJECT"),
          st("For life-threatening bleeding from an arm or leg that pressure doesn't stop, a tourniquet 5–7 cm above the wound (not on a joint) may be needed: note the time and don't loosen it. If you have none, the emergency call handler will tell you what to do.", "BLEED-TQ", "BLEED-TQ-SJA"),
          st("If they feel faint or look pale, help them lie down and raise their legs.", "BLEED-SHOCK")],
          st("Call emergency services now if the bleeding won't stop or spurts out bright red.", "BLEED-CALL", "BLEED-PRESS-BRC")),
      "pt": L("Sangramento forte", [
          st("Aperte com firmeza diretamente sobre o ferimento com um pano limpo ou curativo, e continue apertando.", "BLEED-PRESS", "BLEED-PRESS-BRC"),
          st("Se o sangue atravessar, troque por um pano novo e mantenha a pressão firme.", "BLEED-SOAK", "BLEED-SOAK-BRC"),
          st("Se houver algo cravado no ferimento, não retire; aperte dos dois lados do objeto.", "BLEED-OBJECT"),
          st("Para sangramento grave de braço ou perna que a pressão não controla, pode ser preciso um torniquete 5–7 cm acima do ferimento (não sobre uma articulação): anote a hora e não afrouxe. Se não tiver um, o atendente da emergência vai orientar.", "BLEED-TQ", "BLEED-TQ-SJA"),
          st("Se a pessoa ficar pálida ou fraca, deite-a e eleve as pernas.", "BLEED-SHOCK")],
          st("Ligue para a emergência (SAMU 192) agora se o sangramento não parar ou sair em jatos vermelho-vivo.", "BLEED-CALL", "BLEED-PRESS-BRC")),
      "es": L("Sangrado fuerte", [
          st("Presione con firmeza directamente sobre la herida con un paño limpio o un apósito, y siga presionando.", "BLEED-PRESS", "BLEED-PRESS-BRC"),
          st("Si la sangre lo empapa, cámbielo por uno nuevo y mantenga la presión firme.", "BLEED-SOAK", "BLEED-SOAK-BRC"),
          st("Si hay algo clavado en la herida, no lo saque; presione a ambos lados del objeto.", "BLEED-OBJECT"),
          st("Ante un sangrado grave de brazo o pierna que la presión no detiene, puede hacer falta un torniquete 5–7 cm por encima de la herida (no sobre una articulación): anote la hora y no lo afloje. Si no tiene uno, el operador de emergencias le indicará qué hacer.", "BLEED-TQ", "BLEED-TQ-SJA"),
          st("Si se marea o se pone pálida, acuéstela y levántele las piernas.", "BLEED-SHOCK")],
          st("Llame a emergencias ahora si el sangrado no para o sale a chorros rojo brillante.", "BLEED-CALL", "BLEED-PRESS-BRC"))}})
    C.append({"id": "stroke", "round": 4, "condition": "Stroke", "covers": "placeholder stroke card",
     "topic": {"en": "stroke, face drooping, slurred speech", "pt": "AVC, rosto caído, fala enrolada", "es": "ictus, cara caída, habla arrastrada"},
     "rules": ["stroke-wait"],
     "review_flags": ["FAST (UK) vs BE FAST (CDC: balance, eyes) vs RÁPIDO (CDC ES). The card lists the FAST signs plus balance/vision in plain words, no mnemonic.",
                      "Signs that went away: NHS = still call 999; CDC = a TIA, tell a health care team right away. The card follows NHS.",
                      "'No food or drink' is St John only; 'no aspirin' is in no source (left out)."],
     "langs": {
      "en": L("Possible stroke", [
          st("Check quickly: one side of the face drooping, one arm weak, slurred or strange speech.", "STROKE-FAST"),
          st("Note the time the signs started.", "STROKE-TIME"),
          st("Don't drive them to hospital; wait for the ambulance.", "STROKE-DRIVE"),
          st("Don't give them anything to eat or drink.", "STROKE-FOOD"),
          st("Help them sit or lie down comfortably and reassure them.", "STROKE-COMFORT")],
          st("Call emergency services now if you see any of these signs, even if they go away.", "STROKE-CALL", "STROKE-FAST")),
      "pt": L("Possível AVC", [
          st("Confira rápido: um lado do rosto caído, um braço fraco, fala enrolada ou estranha.", "STROKE-FAST"),
          st("Anote a hora em que os sinais começaram.", "STROKE-TIME"),
          st("Não leve a pessoa de carro ao hospital; espere a ambulância.", "STROKE-DRIVE"),
          st("Não dê nada para comer ou beber.", "STROKE-FOOD"),
          st("Ajude a pessoa a sentar ou deitar confortável e tranquilize-a.", "STROKE-COMFORT")],
          st("Ligue para a emergência (SAMU 192) agora se vir qualquer um desses sinais, mesmo que passem.", "STROKE-CALL", "STROKE-FAST")),
      "es": L("Posible ictus", [
          st("Compruebe rápido: un lado de la cara caído, un brazo débil, habla arrastrada o extraña.", "STROKE-FAST", "STROKE-ES"),
          st("Anote la hora en que empezaron los signos.", "STROKE-TIME", "STROKE-ES"),
          st("No la lleve en coche al hospital; espere a la ambulancia.", "STROKE-DRIVE", "STROKE-ES"),
          st("No le dé nada de comer ni de beber.", "STROKE-FOOD"),
          st("Ayúdela a sentarse o acostarse cómoda y tranquilícela.", "STROKE-COMFORT")],
          st("Llame a emergencias ahora si ve cualquiera de estos signos, aunque desaparezcan.", "STROKE-CALL", "STROKE-ES"))}})
    C.append({"id": "anaphylaxis", "round": 4, "condition": "Anaphylaxis (severe allergic reaction)", "covers": "placeholder anaphylaxis card",
     "topic": {"en": "anaphylaxis, throat swelling, can't breathe", "pt": "anafilaxia, garganta fechando", "es": "anafilaxia, se le cierra la garganta"},
     "rules": ["anaph-stand-walk"],
     "review_flags": ["Legs: NHS 'you can raise your legs' (optional), SJA legs raised. The card says lie down, legs raised if they can.", "CPR line only on healthdirect (NHS/RCUK anaphylaxis pages have none)."],
     "langs": {
      "en": L("Severe allergic reaction (anaphylaxis)", [
          st("Signs: swelling of the throat or tongue, trouble breathing or wheezing, feeling faint, pale or cold skin.", "ANA-SIGNS"),
          st("Use their adrenaline auto-injector (EpiPen) right away; use a second one after 5 minutes if they're not better.", "ANA-ADR"),
          st("Have them lie down (legs raised if they can; sit up slowly if breathing is hard), and don't let them stand or walk, even if they feel better.", "ANA-LIE"),
          st("If they stop responding and aren't breathing normally, start CPR.", "ANA-CPR")],
          st("Call emergency services now and say you think it's anaphylaxis.", "ANA-ADR", "ANA-ADR-SJA")),
      "pt": L("Reação alérgica grave (anafilaxia)", [
          st("Sinais: inchaço na garganta ou na língua, dificuldade para respirar ou chiado, sensação de desmaio, pele pálida ou fria.", "ANA-SIGNS"),
          st("Use a caneta de adrenalina da pessoa na hora; use uma segunda após 5 minutos se não melhorar.", "ANA-ADR"),
          st("Deite a pessoa (pernas elevadas se possível; sentada devagar se respirar for difícil) e não deixe ficar em pé nem caminhar, mesmo que melhore.", "ANA-LIE"),
          st("Se ela parar de responder e não respirar normalmente, comece a RCP.", "ANA-CPR")],
          st("Ligue para a emergência (SAMU 192) agora e diga que pode ser anafilaxia.", "ANA-ADR", "ANA-ADR-SJA")),
      "es": L("Reacción alérgica grave (anafilaxia)", [
          st("Signos: hinchazón de garganta o lengua, dificultad para respirar o pitidos, sensación de desmayo, piel pálida o fría.", "ANA-SIGNS"),
          st("Use su autoinyector de adrenalina de inmediato; use un segundo a los 5 minutos si no mejora.", "ANA-ADR"),
          st("Acuéstela (con las piernas en alto si puede; sentada despacio si le cuesta respirar) y no la deje ponerse de pie ni caminar, aunque se sienta mejor.", "ANA-LIE"),
          st("Si deja de responder y no respira con normalidad, empiece la RCP.", "ANA-CPR")],
          st("Llame a emergencias ahora y diga que cree que es anafilaxia.", "ANA-ADR", "ANA-ADR-SJA"))}})
    C.append({"id": "eyechem", "round": 4, "condition": "Chemical in the eye", "covers": "placeholder eyechem card",
     "topic": {"en": "bleach splashed in the eye, chemical", "pt": "água sanitária caiu no olho, produto químico", "es": "lejía en el ojo, producto químico"},
     "rules": ["eye-rub", "eye-short-rinse"],
     "review_flags": ["Tier: NHS sends only strong chemicals (oven cleaner, bleach) to A&E/999; SJA any chemical splash. The card says 'strong chemical (bleach, oven cleaner) or the eye stays painful/red/blurry' → emergency.",
                      "Contact lenses: healthdirect 'try to take them out, but not if the eye surface is badly damaged'; SJA 'if they can'."],
     "langs": {
      "en": L("Chemical in the eye", [
          st("Rinse the eye right away with lots of clean, cool (not hot) water for at least 20 minutes, washing inside the eyelids, and keep going while you wait for help.", "EYE-RINSE", "EYE-RINSE-SJA"),
          st("Don't let the water run into the other eye.", "EYE-RINSE-SJA"),
          st("Take out contact lenses if you easily can, but not if the eye looks badly damaged.", "EYE-LENS"),
          st("Don't rub the eye.", "EYE-DONT"),
          st("Take the product's container with you.", "EYE-RINSE")],
          st("Call emergency services or go to the emergency department for a strong chemical such as bleach or oven cleaner; don't drive yourself.", "EYE-CALL-NHS", "EYE-CALL")),
      "pt": L("Produto químico no olho", [
          st("Lave o olho na hora com muita água limpa e fria (não quente) por pelo menos 20 minutos, por dentro das pálpebras, e continue enquanto espera ajuda.", "EYE-RINSE", "EYE-RINSE-SJA"),
          st("Não deixe a água escorrer para o outro olho.", "EYE-RINSE-SJA"),
          st("Tire as lentes de contato se for fácil, mas não se o olho parecer muito machucado.", "EYE-LENS"),
          st("Não esfregue o olho.", "EYE-DONT"),
          st("Leve a embalagem do produto.", "EYE-RINSE")],
          st("Ligue para a emergência ou vá ao pronto-socorro em caso de produto forte, como água sanitária ou limpa-forno; não vá dirigindo.", "EYE-CALL-NHS", "EYE-CALL")),
      "es": L("Producto químico en el ojo", [
          st("Enjuague el ojo de inmediato con mucha agua limpia y fresca (no caliente) durante al menos 20 minutos, por dentro de los párpados, y siga mientras espera ayuda.", "EYE-RINSE", "EYE-RINSE-SJA"),
          st("Que el agua no caiga en el otro ojo.", "EYE-RINSE-SJA"),
          st("Quite las lentillas si es fácil, pero no si el ojo parece muy dañado.", "EYE-LENS"),
          st("No se frote el ojo.", "EYE-DONT"),
          st("Lleve el envase del producto.", "EYE-RINSE")],
          st("Llame a emergencias o vaya a urgencias si es un producto fuerte como lejía o limpiahornos; no conduzca.", "EYE-CALL-NHS", "EYE-CALL"))}})
    C.append({"id": "electric", "round": 4, "condition": "Electric shock", "covers": "placeholder electric card",
     "topic": {"en": "electric shock, touched a live wire", "pt": "choque elétrico, encostou num fio", "es": "descarga eléctrica, tocó un cable"},
     "rules": ["electric-touch"],
     "review_flags": ["Downed power line distance: healthdirect 6 m vs American Red Cross 35 ft (~10.7 m); the old 18 m is in no source. The card says 'at least 10 metres' (the stricter source, rounded). OK?",
                      "St John's page is low-voltage only; no NHS/BRC electric-shock page exists."],
     "langs": {
      "en": L("Electric shock", [
          st("Don't touch them while they may still be in contact with the electricity.", "ELEC-OFF", "ELEC-OFF-SJA"),
          st("Switch off the power at the mains or unplug it first. If you can't, separate them from the source using something dry and wooden, like a broom handle, while standing on something dry.", "ELEC-OFF", "ELEC-OFF-SJA"),
          st("If a power line is down, stay at least 10 metres away from it and anything it touches, and call emergency services.", "ELEC-HV-ARC", "ELEC-HV"),
          st("If they're not breathing normally, start CPR. Treat burns like any other burn.", "ELEC-CALL"),
          st("Anyone who had an electric shock should get their heart checked.", "ELEC-CALL")],
          st("Call emergency services if they lost consciousness, have trouble breathing or a fast or slow heartbeat, or after any high-voltage shock.", "ELEC-CALL", "ELEC-CALL-SJA")),
      "pt": L("Choque elétrico", [
          st("Não toque na pessoa enquanto ela puder estar em contato com a eletricidade.", "ELEC-OFF", "ELEC-OFF-SJA"),
          st("Desligue a energia no quadro de luz ou tire da tomada primeiro. Se não der, afaste-a da fonte com algo seco de madeira, como um cabo de vassoura, em pé sobre algo seco.", "ELEC-OFF", "ELEC-OFF-SJA"),
          st("Se houver um fio de alta tensão caído, fique a pelo menos 10 metros dele e do que ele toca, e ligue para a emergência.", "ELEC-HV-ARC", "ELEC-HV"),
          st("Se ela não respirar normalmente, comece a RCP. Trate queimaduras como qualquer outra queimadura.", "ELEC-CALL"),
          st("Quem levou um choque deve fazer uma avaliação do coração.", "ELEC-CALL")],
          st("Ligue para a emergência (SAMU 192) se a pessoa desmaiou, tem dificuldade para respirar, batimento acelerado ou lento, ou depois de qualquer choque de alta tensão.", "ELEC-CALL", "ELEC-CALL-SJA")),
      "es": L("Descarga eléctrica", [
          st("No toque a la persona mientras pueda seguir en contacto con la electricidad.", "ELEC-OFF", "ELEC-OFF-SJA"),
          st("Corte la corriente en el cuadro eléctrico o desenchufe primero. Si no puede, apártela de la fuente con algo seco de madera, como el palo de una escoba, de pie sobre algo seco.", "ELEC-OFF", "ELEC-OFF-SJA"),
          st("Si hay un cable de alta tensión caído, manténgase a al menos 10 metros de él y de lo que toque, y llame a emergencias.", "ELEC-HV-ARC", "ELEC-HV"),
          st("Si no respira con normalidad, empiece la RCP. Trate las quemaduras como cualquier otra quemadura.", "ELEC-CALL"),
          st("Toda persona que recibió una descarga debe hacerse revisar el corazón.", "ELEC-CALL")],
          st("Llame a emergencias si perdió el conocimiento, tiene dificultad para respirar, el pulso muy rápido o lento, o tras cualquier descarga de alta tensión.", "ELEC-CALL", "ELEC-CALL-SJA"))}})
    C.append({"id": "altitude", "round": 4, "condition": "Altitude sickness", "covers": "placeholder altitude card (vit-hlt-002-type questions)",
     "topic": {"en": "altitude sickness at 4,000 m, headache and nausea", "pt": "mal da altitude a 4.000 m, dor de cabeça", "es": "mal de altura a 4.000 m, dolor de cabeza"},
     "rules": ["altitude-ascend", "altitude-push-on", "altitude-fast-ascent"],
     "review_flags": ["When to descend: NHS = worse or not better after 1 day; CDC = worse despite rest. The card follows NHS (stricter).", "CDC source is the Yellow Book clinician chapter (no CDC traveller page exists)."],
     "langs": {
      "en": L("Altitude sickness (headache, nausea, dizziness, tiredness at altitude)", [
          st("Stop and rest at the same altitude until you feel better; don't go higher, and never go up to sleep higher with symptoms.", "ALT-STOP", "ALT-NEVER"),
          st("Don't use alcohol or sleeping pills to help you sleep at altitude.", "ALT-ALCOHOL"),
          st("If symptoms get worse or don't improve after a day, go down about 300 to 1,000 metres.", "ALT-STOP")],
          st("Go down straight away and get medical help immediately (call emergency services if you can) if they are confused, unsteady, breathless at rest, coughing up frothy or bloody spit, or very sleepy.", "ALT-SEVERE")),
      "pt": L("Mal da altitude (dor de cabeça, enjoo, tontura, cansaço na altitude)", [
          st("Pare e descanse na mesma altitude até melhorar; não suba mais, e nunca suba para dormir mais alto com sintomas.", "ALT-STOP", "ALT-NEVER"),
          st("Não use álcool nem remédio para dormir na altitude.", "ALT-ALCOHOL"),
          st("Se os sintomas piorarem ou não melhorarem em um dia, desça cerca de 300 a 1.000 metros.", "ALT-STOP")],
          st("Desça imediatamente e procure ajuda médica na hora (ligue para a emergência se puder) se a pessoa estiver confusa, cambaleando, com falta de ar em repouso, tossindo espuma ou sangue, ou muito sonolenta.", "ALT-SEVERE")),
      "es": L("Mal de altura (dolor de cabeza, náuseas, mareo, cansancio en altura)", [
          st("Pare y descanse a la misma altura hasta sentirse mejor; no suba más, y nunca suba a dormir más alto con síntomas.", "ALT-STOP", "ALT-NEVER"),
          st("No use alcohol ni pastillas para dormir en altura.", "ALT-ALCOHOL"),
          st("Si los síntomas empeoran o no mejoran en un día, baje unos 300 a 1.000 metros.", "ALT-STOP")],
          st("Baje de inmediato y busque ayuda médica enseguida (llame a emergencias si puede) si está confundida, se tambalea, le falta el aire en reposo, tose espuma o sangre, o está muy somnolienta.", "ALT-SEVERE"))}})
    C.append({"id": "marinepuncture", "round": 4, "condition": "Stingray, sea urchin, weever or stonefish", "covers": "placeholder marinepuncture card",
     "topic": {"en": "stepped on a sea urchin, stingray sting", "pt": "pisei num ouriço-do-mar, arraia", "es": "pisé un erizo de mar, raya"},
     "rules": ["marine-ice"],
     "review_flags": ["Hot water: NHS 'as hot as can be tolerated, at least 30 minutes'; healthdirect 45 °C up to 90 min for fish/stingray. The card says 30–90 minutes, as hot as tolerated.",
                      "Spines: NHS remove; healthdirect leave STONEFISH spines in. The card splits by creature.",
                      "Stingray alone: NHS minor injuries unit (not 999); stonefish: emergency (healthdirect)."],
     "langs": {
      "en": L("Stingray, sea urchin, weever or stonefish", [
          st("Soak the area in very hot water, as hot as they can bear without burning, for 30 to 90 minutes.", "SEA-HOT"),
          st("Remove spines near the surface with tweezers or the edge of a card (not bare hands), but leave a stonefish spine in.", "SEA-SPINE", "SEA-STONEFISH"),
          st("Don't put ice on it, don't cover or close the wound, and don't pee on it.", "SEA-DONT"),
          st("A stingray wound should be checked at a clinic or minor injuries unit.", "SEA-CALL")],
          st("Call emergency services for a stonefish sting, or if they have trouble breathing, chest pain, severe swelling or bleeding, or feel faint.", "SEA-CALL", "SEA-STONEFISH")),
      "pt": L("Arraia, ouriço-do-mar, peixe-aranha ou peixe-pedra", [
          st("Deixe a área em água bem quente, o mais quente que a pessoa aguentar sem se queimar, por 30 a 90 minutos.", "SEA-HOT"),
          st("Tire os espinhos superficiais com pinça ou a borda de um cartão (sem as mãos), mas deixe o espinho de peixe-pedra.", "SEA-SPINE", "SEA-STONEFISH"),
          st("Não ponha gelo, não cubra nem feche o ferimento e não faça xixi no local.", "SEA-DONT"),
          st("Ferimento de arraia deve ser avaliado num posto de saúde ou pronto atendimento.", "SEA-CALL")],
          st("Ligue para a emergência em caso de peixe-pedra, ou se houver falta de ar, dor no peito, inchaço ou sangramento forte, ou sensação de desmaio.", "SEA-CALL", "SEA-STONEFISH")),
      "es": L("Raya, erizo de mar, pez araña o pez piedra", [
          st("Sumerja la zona en agua muy caliente, lo más caliente que tolere sin quemarse, durante 30 a 90 minutos.", "SEA-HOT"),
          st("Quite las espinas superficiales con pinzas o el borde de una tarjeta (sin las manos), pero deje la espina del pez piedra.", "SEA-SPINE", "SEA-STONEFISH"),
          st("No ponga hielo, no cubra ni cierre la herida y no orine sobre ella.", "SEA-DONT"),
          st("Una herida de raya debe revisarse en un centro de salud.", "SEA-CALL")],
          st("Llame a emergencias si es un pez piedra, o si hay dificultad para respirar, dolor en el pecho, hinchazón o sangrado fuertes, o sensación de desmayo.", "SEA-CALL", "SEA-STONEFISH"))}})
    C.append({"id": "tick", "round": 4, "condition": "Tick bite", "covers": "placeholder tick card",
     "topic": {"en": "a tick is stuck in my leg", "pt": "carrapato preso na perna", "es": "una garrapata pegada en la pierna"},
     "rules": ["tick-burn-smother"],
     "review_flags": ["DIRECT CONTRADICTION by region: UK/US (CDC, NHS, St John) = fine-tipped tweezers, never burn or freeze; Australia (healthdirect, ASCIA) = freeze with an ether spray, never tweezers. The card gives the UK/US method and an Australia line. OK, or region-split the card?"],
     "langs": {
      "en": L("Tick bite", [
          st("With fine-tipped tweezers, grab the tick as close to the skin as possible and pull straight up with steady pressure, without squeezing it.", "TICK-REMOVE", "TICK-REMOVE-NHS"),
          st("Don't twist or jerk it. Don't use heat, petroleum jelly or nail polish.", "TICK-REMOVE", "TICK-DONT"),
          st("Clean the bite and your hands with soap and water.", "TICK-REMOVE"),
          st("In Australia, health services advise freezing the tick with an ether spray instead of tweezers; if it won't drop off, get urgent medical help.", "TICK-AU"),
          st("Watch the bite for up to 3 months: a growing round or bullseye rash, fever or flu-like symptoms mean you should see a doctor soon.", "TICK-WATCH", "TICK-WATCH-CDC")],
          st("Call emergency services if signs of a severe allergic reaction appear (swelling of the throat or tongue, trouble breathing).", "ANA-SIGNS", "ANA-ADR")),
      "pt": L("Picada de carrapato", [
          st("Com uma pinça de ponta fina, segure o carrapato o mais perto possível da pele e puxe para cima com força constante, sem apertá-lo.", "TICK-REMOVE", "TICK-REMOVE-NHS"),
          st("Não torça nem puxe de uma vez, e não use vaselina, esmalte nem calor.", "TICK-REMOVE", "TICK-DONT"),
          st("Lave a picada e as mãos com água e sabão.", "TICK-REMOVE"),
          st("Na Austrália, os serviços de saúde orientam congelar o carrapato com spray de éter em vez de usar pinça; se ele não cair, procure ajuda médica urgente.", "TICK-AU"),
          st("Observe a picada por até 3 meses: mancha redonda que cresce ou em forma de alvo, febre ou sintomas de gripe pedem uma consulta médica logo.", "TICK-WATCH", "TICK-WATCH-CDC")],
          st("Ligue para a emergência se surgirem sinais de alergia grave (inchaço na garganta ou na língua, falta de ar).", "ANA-SIGNS", "ANA-ADR")),
      "es": L("Picadura de garrapata", [
          st("Con una pinza de punta fina, agarre la garrapata lo más cerca posible de la piel y tire hacia arriba con presión constante, sin apretarla.", "TICK-REMOVE", "TICK-REMOVE-NHS"),
          st("No la tuerza ni la arranque de un tirón, y no use vaselina, esmalte ni calor.", "TICK-REMOVE", "TICK-DONT"),
          st("Lave la picadura y las manos con agua y jabón.", "TICK-REMOVE"),
          st("En Australia, los servicios de salud aconsejan congelar la garrapata con un spray de éter en lugar de usar pinzas; si no se cae, busque ayuda médica urgente.", "TICK-AU"),
          st("Vigile la picadura hasta 3 meses: un sarpullido redondo que crece o en forma de diana, fiebre o síntomas de gripe indican que debe ver a un médico pronto.", "TICK-WATCH", "TICK-WATCH-CDC")],
          st("Llame a emergencias si aparecen signos de alergia grave (hinchazón de garganta o lengua, dificultad para respirar).", "ANA-SIGNS", "ANA-ADR"))}})
    C.append({"id": "heatexhaustion", "round": 4, "condition": "Heat exhaustion", "covers": "placeholder heatexhaustion card",
     "topic": {"en": "heat exhaustion, dizzy and sweating a lot in the heat", "pt": "exaustão pelo calor, tontura e muito suor", "es": "agotamiento por calor, mareo y mucho sudor"},
     "rules": [],
     "review_flags": ["'Lie down with legs raised' is St John only (NHS's 4 steps don't have it). Left out.", "Confusion or no sweating = heatstroke → the heatstroke card (no plain-water advice there)."],
     "langs": {
      "en": L("Heat exhaustion", [
          st("Move them to a cool place and take off extra clothing.", "HEX-STEPS"),
          st("Give plenty of water to drink, or a sports drink or rehydration solution.", "HEX-STEPS"),
          st("Cool their skin: spray or sponge with cool water and fan them; cold packs wrapped in a cloth in the armpits or on the neck.", "HEX-STEPS"),
          st("They should feel better within 30 minutes.", "HEX-STEPS")],
          st("Call emergency services if they're still unwell after 30 minutes, or if they become confused, stop sweating, have a seizure or pass out (that's heatstroke).", "HEX-CALL")),
      "pt": L("Exaustão pelo calor", [
          st("Leve a pessoa para um lugar fresco e tire o excesso de roupa.", "HEX-STEPS"),
          st("Dê bastante água para beber, ou bebida isotônica ou soro de reidratação.", "HEX-STEPS"),
          st("Resfrie a pele: borrife ou passe água fresca e abane; bolsas frias enroladas num pano nas axilas ou no pescoço.", "HEX-STEPS"),
          st("Ela deve melhorar em até 30 minutos.", "HEX-STEPS")],
          st("Ligue para a emergência se ainda estiver mal depois de 30 minutos, ou se ficar confusa, parar de suar, tiver convulsão ou desmaiar (isso é insolação grave).", "HEX-CALL")),
      "es": L("Agotamiento por calor", [
          st("Lleve a la persona a un lugar fresco y quítele la ropa de más.", "HEX-STEPS"),
          st("Dele mucha agua para beber, o una bebida isotónica o suero de rehidratación.", "HEX-STEPS"),
          st("Enfríe la piel: rocíe o pase agua fresca y abaníquela; bolsas frías envueltas en un paño en las axilas o el cuello.", "HEX-STEPS"),
          st("Debería sentirse mejor en 30 minutos.", "HEX-STEPS")],
          st("Llame a emergencias si sigue mal después de 30 minutos, o si se confunde, deja de sudar, tiene una convulsión o se desmaya (eso es un golpe de calor).", "HEX-CALL"))}})
    return C
