"""Round 6 (Compass, 2026-10-03): CPR (adult, child, baby) and swallowed poison. The reviewer's top priorities
(REVIEWER-DECISIONS.md, 'Additional cards to consider'): many cards say 'start CPR' but no card shows how, and infant
CPR differs; poisoning (medicine, household chemical, plant) had no card.
New engine keys: cpradult, cprchild, cprinfant, poisoning. Importable like round5.py (S6 + build(st, L)); NOT yet wired
into build_cards.py (another process owns it). Sources: SOURCES.raw-6.md; text snapshots in snapshots-6/.
Binding reviewer rules applied: ES = usted; PT card text has no phone numbers; no dosing; plain words; conditional steps.
Run `python3 round6.py` to re-run the self-checks (quotes vs snapshots, safety v0.8.9, mutants). Writes nothing."""

# ---------------------------------------------------------------- URLs
SJA_CPR = "https://www.sja.org.uk/first-aid-advice/cpr/"  # https://www.nhs.uk/conditions/first-aid/cpr/ redirects here (2026-10-03)
SJA_CHILD = "https://www.sja.org.uk/first-aid-advice/child-cpr/"
SJA_BABY = "https://www.sja.org.uk/first-aid-advice/baby-cpr/"
SJA_RECOV = "https://www.sja.org.uk/first-aid-advice/recovery-position/"
SJA_POIS = "https://www.sja.org.uk/get-advice/first-aid-advice/poisoning/swallowed-poisons/"
BRC_ADULT = "https://www.redcross.org.uk/first-aid/learn-first-aid/unresponsive-and-not-breathing"
BRC_AED = "https://www.redcross.org.uk/first-aid/learn-first-aid/unresponsive-and-not-breathing-when-an-aed-is-available"
BRC_RECOV = "https://www.redcross.org.uk/first-aid/learn-first-aid/unresponsive-and-breathing"
BRC_CHILD = "https://www.redcross.org.uk/first-aid/learn-first-aid-for-babies-and-children/unresponsive-not-breathing-child"
BRC_BABY = "https://www.redcross.org.uk/first-aid/learn-first-aid-for-babies-and-children/unresponsive-and-not-breathing-baby"
BRC_POIS = "https://www.redcross.org.uk/first-aid/learn-first-aid/poisoning"
RCUK = "https://www.resus.org.uk/public-resource/how-do-cpr"
HD_CPR = "https://www.healthdirect.gov.au/how-to-perform-cpr"
HD_POIS = "https://www.healthdirect.gov.au/poisoning"
NHS_POIS = "https://www.nhs.uk/conditions/poisoning/"
PC = "https://www.poison.org/first-aid-for-poisonings"
MS_SBV = "https://www.gov.br/saude/pt-br/composicao/saes/samu-192/publicacoes/protocolo-de-suporte-basico-de-vida-1-2.pdf"
CIATOX_ES = "https://ciatox.es.gov.br/Media/toxcen/Material%20Informativo/usuarios/primeiros%20socorros%20-%20revisado.pdf"
AR_ADULT = "https://www.argentina.gob.ar/salud/primerosauxilios/rcp/adultos"
AR_BEBE = "https://www.argentina.gob.ar/salud/primerosauxilios/rcp/bebes"
CRAR_RCP = "https://cruzroja.org.ar/blog/como-hacer-rcp/"
CRAR_INTOX = "https://cruzroja.org.ar/blog/que-hacer-ante-una-intoxicacion/"

# URL → text snapshot in snapshots-6/ (used by the self-check below)
SNAP6 = {SJA_CPR: "sja-cprhub.txt", SJA_CHILD: "sja-child.txt", SJA_BABY: "sja-baby.txt", SJA_RECOV: "sja-recov.txt",
         SJA_POIS: "sja-poison.txt", BRC_ADULT: "brc-adult.txt", BRC_AED: "brc-aed.txt", BRC_RECOV: "brc-recov.txt",
         BRC_CHILD: "brc-child.txt", BRC_BABY: "brc-baby.txt", BRC_POIS: "brc-poison.txt", RCUK: "rcuk-howcpr.txt",
         HD_CPR: "hd-cpr.txt", HD_POIS: "hd-poison.txt", NHS_POIS: "nhs-poison.txt", PC: "poisonorg.txt",
         MS_SBV: "ms-samu-sbv-excerpt.txt", CIATOX_ES: "es-ciatox.txt", AR_ADULT: "ar-adultos.txt", AR_BEBE: "ar-bebes.txt",
         CRAR_RCP: "cr-ar-rcp.txt", CRAR_INTOX: "cr-ar-intox.txt"}

# ---------------------------------------------------------------- sources: id → (org + title, url, verbatim quote(s) joined by " / ", flag)
S6 = {
 # adult
 "CPR-SJA-CHECK": ("St John Ambulance (UK), How to do CPR (the NHS CPR page redirects here)", SJA_CPR, "Check if they respond by gently shaking their shoulders and asking them loudly, 'are you ok?'. / If they don't respond, shout for help and open their airway by gently tilting the casualty's head back and lifting their chin. / Look, listen, and feel for up to 10 seconds for normal breathing. Ignore occasional, irregular gasps - these are common in the early stages of cardiac arrest.", "ok"),
 "CPR-SJA-CALL": ("St John Ambulance (UK), How to do CPR", SJA_CPR, "If they are not breathing normally, ask a helper to call 999 or 112 for an ambulance while you start CPR. Ask a helper to find and bring a defibrillator, if available. / If you are on your own, use the hands-free speaker on a phone so you can start CPR while speaking to ambulance control. / Do not leave the casualty to look for a defibrillator yourself.", "ok"),
 "CPR-SJA-PUSH": ("St John Ambulance (UK), How to do CPR", SJA_CPR, "Kneel close to the casualty and put the heel of your hand on the middle of their chest. Put your other hand on top of your first hand and if you can, interlock your fingers. / Lean forwards so your shoulders are over your hands, keep your arms straight and press down hard, to a depth of about 5-6cm before releasing the pressure and allowing the chest to come back up. / Push at a rate of 100 to 120 per minute.", "CONFLICT (depth, minor): 5-6 cm (SJA, MS Brazil, Argentina) vs 'about a third' of the chest (healthdirect) vs '5 cm aproximadamente' (Cruz Roja Argentina)"),
 "CPR-SJA-BREATHS": ("St John Ambulance (UK), How to do CPR", SJA_CPR, "If you are trained to do so, after 30 compressions, provide two rescue breaths. If you are unable or unwilling to provide rescue breaths, give continuous chest compressions. / Tilt the casualty's head backwards, lift their chin, and pinch the soft part of their nose closed.", "ok"),
 "CPR-SJA-UNTIL": ("St John Ambulance (UK), How to do CPR", SJA_CPR, "Keep alternating 30 compressions with two breaths (30:2) until: / emergency help arrives and takes over / the person starts showing signs of life and starts to breathe normally", "ok"),
 "CPR-SJA-RECOV": ("St John Ambulance (UK), How to put someone in the recovery position", SJA_RECOV, "If it shows that they are unresponsive but breathing, put them in the recovery position. / Gently tilt the casualty’s head back and lift their chin to make sure their airway stays open.", "ok"),
 "CPR-BRC-GASP": ("British Red Cross, First aid for someone who is unresponsive and not breathing", BRC_ADULT, "Sometimes when a person is unresponsive their breathing may become noisy or irregular, or they may be gasping. This is usually a sign that their heart is not working properly and you should start chest compressions.", "ok"),
 "CPR-BRC-PUSH": ("British Red Cross, First aid for someone who is unresponsive and not breathing", BRC_ADULT, "Give chest compressions by pushing firmly in the middle of the chest up and down. Push the chest hard and fast at a rate of 2 pushes per second. / Continue to push in this way until help arrives.", "ok"),
 "CPR-BRC-BREATHS": ("British Red Cross, First aid for someone who is unresponsive and not breathing", BRC_ADULT, "If you feel able to give rescue breaths, you can do so after about 30 pushes on their chest. / However, giving chest compressions is the most important thing to do", "ok"),
 "CPR-BRC-AED": ("British Red Cross, Unresponsive and not breathing when an AED is available", BRC_AED, "3. Tell someone to get an AED as soon as possible. / 5. When the AED arrives open it and follow the voice prompts.", "ok"),
 "CPR-BRC-RECOV": ("British Red Cross, First aid for someone who is unresponsive and breathing", BRC_RECOV, "Step 2. If they are breathing, move them onto their side and tilt their head back. / Step 3. Call 999", "ok"),
 "CPR-RCUK-CALL": ("Resuscitation Council UK, How to do CPR", RCUK, "Put the phone on loudspeaker and tell them you are with someone who has collapsed and is not responding. / The ambulance call handler will help you check for signs of normal breathing.", "ok"),
 "CPR-RCUK-PUSH": ("Resuscitation Council UK, How to do CPR", RCUK, "Place your hands in the centre of the chest. / Push down hard and then release twice per second, and don’t stop.", "ok"),
 "CPR-RCUK-BREATHS": ("Resuscitation Council UK, How to do CPR", RCUK, "If you have been trained to provide rescue breaths, alternate 30 chest compressions with 2 rescue breaths. / If you are not trained to provide rescue breaths, perform continuous chest compressions without interruptions.", "ok"),
 "CPR-RCUK-AED": ("Resuscitation Council UK, How to do CPR", RCUK, "The ambulance call handler will tell you where the nearest automated external defibrillator (AED) is. If someone is with you, ask them to fetch it and bring it back. / If you have a defibrillator, switch it on and follow the instructions / If more than one rescuer is present, continue CPR while the pads are being attached.", "ok"),
 "CPR-HD-ADULT": ("healthdirect (Australian Government), How to perform CPR", HD_CPR, "If they are breathing normally, place them in recovery position. Stay with them. Keep checking their breathing until help arrives. / If they are not breathing normally, start CPR. / Their chest should be compressed by about a third. / Aim for 5 sets of 30:2 in about 2 minutes (if you are only doing compressions, aim for about 100 to 120 compressions per minute).", "CONFLICT (depth, minor): 'about a third' vs 5-6 cm (SJA, MS, Argentina)"),
 "CPR-HD-AED": ("healthdirect (Australian Government), How to perform CPR", HD_CPR, "Attach an Automated External Defibrillator (AED) to the person if one is available. / Do not leave the person alone or stop compressions in order to get an AED. / Follow the voice prompts.", "ok"),
 "CPR-HD-UNTIL": ("healthdirect (Australian Government), How to perform CPR", HD_CPR, "the person recovers — they start moving, breathing normally, coughing or talking — then put them in the recovery position / If you can’t give breaths, doing compressions only without stopping may still save a life.", "ok"),
 "CPR-MS-ADULT": ("Ministério da Saúde (BR), Protocolos de Suporte Básico de Vida, SAMU 192 (BC5, PCR/RCP em adultos)", MS_SBV, "Deprimir o tórax em pelo menos 5 cm (sem exceder 6 cm) e permitir o completo retorno entre as compressões; / Manter frequência de compressões em 100 a 120 compressões/min;", "ok (professional SAMU protocol, AHA 2015 basis; used for the depth/rate figures only)"),
 "CPR-AR-ADULT": ("Ministerio de Salud (AR), RCP en adultos", AR_ADULT, "Llamá al número de emergencias o pedí a otra persona que lo haga. / Comprimí hacia abajo el torax de la persona hasta hundirlo entre 5 a 6 cm. / Apoyá el talón de una mano en el centro inferior del esternón. Colocá el talón de la otra mano sobre la primera y entrelaza tus dedos. / Tenés que hacer entre 100 y 120 compresiones por minuto. / Si contás con este equipo encendelo y seguí sus instrucciones. / Si la persona recupera la conciencia, colocala de costado o posición de recuperación (lateral) hasta que llegue el equipo de emergencias.", "ok (page uses 'vos'; the card uses usted)"),
 "CPR-CRAR": ("Cruz Roja Argentina, ¿Cómo hacer RCP?", CRAR_RCP, "Llamar al servicio de emergencias médicas al 1-0-7 e informar que hay una persona inconsciente que no respira. / Frecuencia: de 100 a 120 compresiones por minuto. / Profundidad 5 cm aproximadamente.", "ok"),
 # child
 "CPR-SJA-CHILD-CALL": ("St John Ambulance (UK), How to do CPR on a child", SJA_CHILD, "If you are on your own, you need to give five rescue breaths first, then dial 999 or 112 on a speaker phone and start chest compressions. If you don't have a speaker phone, give one minute of CPR before calling 999 or 112. / Do not leave the child to make the call or to look for a defibrillator, unless you do not have a mobile phone and there is no help available.", "CONFLICT (lone rescuer): 1 minute of CPR before calling without a speaker (SJA, BRC) vs 2 minutes (Argentina, baby/child page)"),
 "CPR-SJA-CHILD-5": ("St John Ambulance (UK), How to do CPR on a child", SJA_CHILD, "Give five initial rescue breaths. / Blow into their mouth gently and steadily for up to one second, until the chest rises. / It is vital that you perform rescue breaths as a cardiac arrest in a child is likely caused by a respiratory problem.", "CONFLICT (order): 5 breaths first (SJA, BRC, RCUK) vs compressions first, no initial breaths (healthdirect; MS Brazil SAMU protocol)"),
 "CPR-SJA-CHILD-PUSH": ("St John Ambulance (UK), How to do CPR on a child", SJA_CHILD, "Kneel by the child and put one hand in the centre of the child’s chest. / Push down a third of the depth of the chest. / Repeat this 30 times at a rate of 100 to 120 compressions per minute.", "ok"),
 "CPR-SJA-CHILD-REPEAT": ("St John Ambulance (UK), How to do CPR on a child", SJA_CHILD, "After 30 compressions, open the airway and give two breaths. / Keep alternating 30 compressions with two breaths (30:2) until:", "ok (15:2 is for trained paediatric BLS only; left out)"),
 "CPR-SJA-CHILD-AED": ("St John Ambulance (UK), How to do CPR on a child", SJA_CHILD, "If the helper returns with a defibrillator, ask them to switch it on and take the pads out while you continue with CPR. / The defibrillator will give voice prompts on what to do", "ok"),
 "CPR-SJA-CHILD-RECOV": ("St John Ambulance (UK), How to do CPR on a child", SJA_CHILD, "If the child shows signs of becoming responsive such as coughing, opening eyes, speaking, and starts to breathe normally, put them in the recovery position. Monitor their level of response and prepare to give CPR again if necessary.", "ok"),
 "CPR-BRC-CHILD-CHECK": ("British Red Cross, First aid for a child who is unresponsive and not breathing", BRC_CHILD, "A child who is unresponsive won't answer or move if you call their name or tap their shoulders. Shout for help. / Do this for no more than ten seconds.", "ok"),
 "CPR-BRC-CHILD": ("British Red Cross, First aid for a child who is unresponsive and not breathing", BRC_CHILD, "2. If they are not breathing, tell someone to call 999. / If you are on your own, call 999 after you’ve spent one minute giving them rescue breaths and chest compressions. / 3. Give five rescue breaths. / Give 30 chest compressions by pushing firmly in the middle of their chest up and down with one hand. / If you are small or the child is large, you may need to use two hands. / Continue with cycles of 30 chest compressions and two rescue breaths until help arrives. / If you can’t give rescue breaths for any reason, just give chest compressions.", "ok"),
 "CPR-RCUK-CHILD": ("Resuscitation Council UK, How to do CPR (child)", RCUK, "Check for danger, then immediately follow these steps to give a child (aged 1-18) CPR. / Put the phone on loudspeaker and tell them you are with a child who is not responding. / Open the child's airway by lifting the chin with two fingers and tilting the head back slightly so it's in the 'sniffing' position.", "AGE: RCUK child = 1-18 years; AHA/MedlinePlus use puberty as the upper bound (MedlinePlus not quoted, see SOURCES.raw-6.md)"),
 "CPR-RCUK-CHILD-5": ("Resuscitation Council UK, How to do CPR (child)", RCUK, "Pinch their nose and cover their mouth with your mouth to create a seal. / Blow into their mouth for one second, just enough to see their chest rise, then release and watch their chest fall. / Repeat this five times.", "ok"),
 "CPR-RCUK-CHILD-PUSH": ("Resuscitation Council UK, How to do CPR (child)", RCUK, "Place the heel of your hand in the centre of the chest; for larger children, you may need to use two hands. / Push down about a third of the depth of the chest (5 cm), then release. / Repeat chest compressions 30 times, twice per second.", "ok"),
 "CPR-HD-CHILD": ("healthdirect (Australian Government), How to perform CPR: children over 1 year", HD_CPR, "Use these instructions only if the child's chest is too small for you to use both hands to do chest compressions. Otherwise, use the instructions for adult CPR above. / Place the heel of one hand on the lower half of breastbone, in the centre of the child’s chest (use one or 2 hands depending on the size of the child and your own strength). / Keeping your arm or arms straight, press straight down on their chest by one third of the chest depth. / Push down fast at a rate of 100 to 120 compressions per minute. / CPR for children over 1 year old: Give 30 compressions followed by 2 breaths.", "CONFLICT (order): compressions first, no 5 initial breaths (vs SJA/BRC/RCUK)"),
 "CPR-MS-PED": ("Ministério da Saúde (BR), Protocolos de Suporte Básico de Vida, SAMU 192 (BPed 7, PCR/RCP no bebê e na criança)", MS_SBV, "No bebê: comprimir o esterno com dois dedos posicionados imediatamente abaixo da linha intermamilar, deprimindo pelo menos 1/3 do diâmetro anteroposterior do tórax ou cerca de 4 cm; / Na criança: realizar compressões com uma ou duas mãos posicionadas na metade inferior do esterno, deprimindo pelo menos 1/3 do diâmetro anteroposterior do tórax ou cerca de 5 cm;", "ok (professional SAMU protocol; figures only)"),
 "CPR-MS-PED-START": ("Ministério da Saúde (BR), Protocolos de Suporte Básico de Vida, SAMU 192 (BPed 7)", MS_SBV, "Iniciar imediatamente as manobras de RCP, começando pelas compressões torácicas, enquanto é instalado o DEA: / 30:2 se houver apenas um profissional realizando a RCP, com frequência de 100 a 120 compressões", "CONFLICT (order): compressions first (AHA 2015 basis) vs 5 breaths first (UK). Not cited by a step."),
 # baby
 "CPR-SJA-BABY-CALL": ("St John Ambulance (UK), How to do CPR on a baby", SJA_BABY, "If you're on your own and have a speaker phone, give five rescue breaths and then call 999 or 112. Continue CPR as directed by emergency medical advisor. / If you're on your own without a speaker phone, you need to give five rescue breaths and one minute of CPR before calling 999 or 112 for an ambulance. / Do not leave the baby to make the call. / If you do not have access to a phone, give five rescue breaths and do one minute of CPR and then go for help, taking the baby with you.", "ok"),
 "CPR-SJA-BABY-AIRWAY": ("St John Ambulance (UK), How to do CPR on a baby", SJA_BABY, "Place the baby on a firm surface and open their airway. To do this, place one hand on their forehead and very gently tilt their head back until their face is flat to the sky. With your other hand, use your fingertip and gently lift the chin.", "ok"),
 "CPR-SJA-BABY-5": ("St John Ambulance (UK), How to do CPR on a baby", SJA_BABY, "Give five initial breaths. Take a breath and put your mouth around the baby’s mouth and nose to make a seal and blow gently and steadily for up to one second. The chest should rise.", "ok"),
 "CPR-SJA-BABY-PUSH": ("St John Ambulance (UK), How to do CPR on a baby", SJA_BABY, "Put two fingers in the centre of the baby’s chest and push down a third of the depth of the chest (about 4cm). Release the pressure allowing the chest to come back up fully. / Repeat this 30 times at a rate of 100 to 120 pumps per minute.", "CONFLICT (technique): two fingers (SJA, BRC, healthdirect, MS Brazil) vs two-thumb encircling (RCUK 2025; Argentina 'Técnica B')"),
 "CPR-SJA-BABY-REPEAT": ("St John Ambulance (UK), How to do CPR on a baby", SJA_BABY, "After 30 pumps, open the airway and give two puffs. Keep alternating 30 pumps with two puffs (30:2) until: / emergency help arrives and takes over / the baby starts showing signs of life and starts to breathe normally. / If the baby shows signs of becoming responsive, like coughing, opening their eyes, making a noise, or starts to breathe normally, put them in the recovery position.", "ok"),
 "CPR-BRC-BABY": ("British Red Cross, First aid for a baby who is unresponsive and not breathing", BRC_BABY, "Tilt their head back slightly - is their chest moving? Look, listen and feel for breaths. / Step 3. Give five rescue breaths: tilt their head back, seal your mouth over their mouth and nose. Blow five times into the baby. / Step 4. Give 30 chest compressions: push firmly in the middle of their chest with two fingers so that the chest goes inward, then release. / Step 5. Give two rescue breaths. Continue with cycles of 30 chest compressions and two rescue breaths until help arrives.", "ok"),
 "CPR-BRC-BABY-CALL": ("British Red Cross, First aid for a baby who is unresponsive and not breathing", BRC_BABY, "Step 2. If they are not breathing, tell someone to call 999. / If you are on your own, call 999 after you’ve spent one minute giving them rescue breaths and chest compressions.", "ok"),
 "CPR-RCUK-BABY": ("Resuscitation Council UK, How to do CPR (baby)", RCUK, "Check for danger, then immediately follow these steps to give a baby (aged 0-12 months) CPR. / Call the baby's name and tap the bottom of their feet to see if they respond. / Put the phone on loudspeaker and tell them you are with a baby who is not responding. / Open the baby's airway by lifting the chin with two fingers and tilting the head back so that it's in a neutral position (not too close to the chest, and not too arched). / Do this for no longer than 10 seconds.", "ok"),
 "CPR-RCUK-BABY-5": ("Resuscitation Council UK, How to do CPR (baby)", RCUK, "Cover the baby's mouth and nose with your mouth to create a seal. / Blow into their mouth and nose for one second, just enough to see their chest rise, then release and watch their chest fall.", "ok"),
 "CPR-RCUK-BABY-THUMBS": ("Resuscitation Council UK, How to do CPR (baby)", RCUK, "Use the two-thumb encircling technique for infants: place both thumbs together in the centre of the chest with the hands encircling the chest and fingers on the baby’s back. / Push down about a third of the depth of the chest (4 cm) and then release.", "CONFLICT (technique): two-thumb encircling vs two fingers. Not cited by a step (depth 4 cm agrees)."),
 "CPR-HD-INFANT": ("healthdirect (Australian Government), How to perform CPR: infants under 1 year", HD_CPR, "Do not shake the infant. / Place 2 fingers on the lower half of the breastbone in the middle of the chest. / Press down on their chest by one-third deep (you may need to use one hand to do CPR depending on the size of the infant). / Tilt the infant’s head back very slightly. / Take a breath and cover the infant’s mouth and nose with your mouth, ensuring a good seal. / If the infant is breathing, place them down on your forearm in recovery position. Monitor their airway, breathing and responsiveness.", "ok"),
 "CPR-HD-INFANT-AED": ("healthdirect (Australian Government), How to perform CPR", HD_CPR, "Do not use an AED on children under 1 year of age.", "CONFLICT (AED in babies): healthdirect 'do not' vs MS Brazil SAMU protocol (paediatric pads, else adult pads, in the baby) and the UK pages (no infant exclusion). Not cited; the baby card says nothing about an AED."),
 "CPR-AR-BEBE": ("Ministerio de Salud (AR), RCP en bebés y niños", AR_BEBE, "Cubrí firmemente con tu boca, la boca y nariz del bebé. / Colocá los dedos índice y medio en el centro del esternón, entre los pezones, sin presionar en el extremo del esternón. / Aplicá presión hacia abajo, comprimiendo 4 cm de profundidad. / Incliná la cabeza del bebé, no demasiado hacia atrás ya que una inclinación exagerada, puede cerrar la vía del aire en lugar de abrirla.", "ok ('Técnica A'; the page also gives two-thumb 'Técnica B')"),
 "CPR-AR-BEBE-ALONE": ("Ministerio de Salud (AR), RCP en bebés y niños", AR_BEBE, "Si estás solo, hacé dos (2) minutos de RCP, llamá a emergencias y continuá con las maniobras hasta la llegada de la ayuda médica.", "CONFLICT (lone rescuer): 2 minutes vs 1 minute (SJA, BRC). Not cited by a step."),
 # poisoning
 "POIS-NHS-999": ("NHS, Poisoning", NHS_POIS, "[NHS quote withheld]", "ok"),
 "POIS-NHS-DO": ("NHS, Poisoning", NHS_POIS, "[NHS quote withheld]", "ok"),
 "POIS-NHS-DONT": ("NHS, Poisoning", NHS_POIS, "[NHS quote withheld]", "ok"),
 "POIS-BRC": ("British Red Cross, First aid for someone who has swallowed something harmful", BRC_POIS, "1. If the person is responsive, find out what they have taken, when they took it and how much they took. / 2. Call 999. / Do not make the person sick. By making them sick, you can cause further damage to their throat or block their airway. / If they have swallowed something corrosive, the liquid will burn the throat on the way back up, causing more pain and distress. / Call 999 anyway, even if they seem to be showing no symptoms. / No, don’t give them anything to drink.", "ok"),
 "POIS-SJA": ("St John Ambulance (UK), Swallowed poisons", SJA_POIS, "If the person is responsive, ask them what they have swallowed, when, and how much. / Call 999 or 112 for emergency help and give them as much information as possible. If you can, keep any packaging or labels to show the emergency services. Keep checking their breathing and response. / Do not try to make them vomit. / Do not give the casualty anything to eat or drink. / If they become unresponsive, open their airway, check their breathing, and prepare to give CPR.", "ok"),
 "POIS-HD-CALL": ("healthdirect (Australian Government), Poisoning", HD_POIS, "Call triple zero (000) if someone stops breathing, collapses, has a seizure, has a severe allergic reaction (anaphylaxis) or has been exposed to a harmful substance. / If there are no symptoms, call the Poisons Information Centre on 13 11 26. You can call 24 hours a day from anywhere in Australia. / There is no need to wait until symptoms appear.", "ok (national number quoted as evidence that poison lines exist; no number goes on a card)"),
 "POIS-HD-FA": ("healthdirect (Australian Government), Poisoning", HD_POIS, "Do NOT induce vomiting — it can cause more harm. / Wash any substance off the mouth or face. / Ask what poison is involved and take a photo of the bottle or packet. / Don’t touch the chemical or exposed area yourself. Use protective clothing such as gloves and goggles. / Remove any affected clothes. / Flood the skin with cool running water.", "ok"),
 "POIS-PC-HELP": ("Poison Control, National Capital Poison Center (US), First aid guidelines", PC, "Call your poison center at 1-800-222-1222 for help. / If the individual collapses, has a seizure, has trouble breathing, or can't be awakened: Call 911 IMMEDIATELY. / Do not induce vomiting. Ipecac syrup is no longer recommended.", "ok (US number quoted as evidence only)"),
 "POIS-PC-MILK": ("Poison Control, National Capital Poison Center (US), First aid guidelines", PC, "Drink a small amount of water or milk immediately if: / The product swallowed is burning, irritating or caustic, AND / The person is conscious, not having convulsions, and able to swallow.", "CONFLICT: water/milk for a caustic product (poison.org) vs nothing to eat or drink (NHS, SJA, BRC) vs only if a poison centre says so (CIATox-ES). Not cited by a step."),
 "POIS-PC-SKIN": ("Poison Control, National Capital Poison Center (US), First aid guidelines", PC, "Remove contaminated clothing first (that's clothing with a spill). / Use lots of room temperature running water and rinse for at least 15 minutes. / It's important to irrigate (rinse) the exposed eyes, immediately.", "ok (skin: 15 min; eye card uses 20 min, NHS)"),
 "POIS-CIATOX-ES": ("CIATox-ES, Secretaria da Saúde do Espírito Santo (BR), Primeiros socorros em intoxicações (PDF)", CIATOX_ES, "Não provocar vômito; / Não oferecer água, leite ou qualquer outro líquido, a não ser que tenha sido orientado por um CIATox; / Encaminhar, com urgência, para serviço médico (pronto socorro ou hospital).", "ok (state poison centre, part of the national CIATox network)"),
 "POIS-CIATOX-ES-GEN": ("CIATox-ES, Secretaria da Saúde do Espírito Santo (BR), Primeiros socorros em intoxicações (PDF)", CIATOX_ES, "Transportar a vítima em posição lateral, a fim de evitar aspiração de vômito, se ocorrer. / Transportar junto, restos da substância, recipientes, embalagens e aplicadores. / Lavar abundantemente o local afetado com água corrente;", "ok"),
 "POIS-CRAR": ("Cruz Roja Argentina, ¿Qué hacer ante una intoxicación?", CRAR_INTOX, "Identificar el tipo de tóxico y la cantidad ingerida. / Llamar al Centro Nacional de Intoxicaciones / Llamar al servicio de emergencias médicas o trasladar al hospital. / Evitar provocar el vómito. / Se aconseja no beber nada. En caso de vómito espontáneo, guardarlo en un contenedor y llevarlo para su posterior análisis.", "ok"),
}


def build(st, L):
    C = []
    # ------------------------------------------------------------ adult CPR
    C.append({"id": "cpradult", "round": 6, "condition": "Adult not responding and not breathing normally (CPR)",
     "covers": "REVIEWER-DECISIONS.md 'Additional cards': many cards say 'start CPR' but none shows how (drowning, headinjury, stroke, choking, heartattack point here)",
     "topic": {"en": "adult not responding and not breathing normally, CPR", "pt": "adulto que não responde e não respira normalmente, RCP", "es": "adulto que no responde y no respira con normalidad, RCP"},
     "rules": [],
     "review_flags": ["Depth: 5-6 cm (SJA = NHS's CPR page, MS Brazil SAMU protocol, Argentina MS) vs 'about a third of the chest' (healthdirect) vs '5 cm aproximadamente' (Cruz Roja Argentina). The card says 'about 5-6 cm'. Options: keep 5-6 cm / 'at least 5 cm' / 'about a third'.",
                      "Rate: 100-120 a minute is common to every source (SJA, healthdirect, MS, Argentina, Cruz Roja AR); BRC/RCUK say '2 pushes per second', which the card adds in brackets.",
                      "Rescue breaths only 'if trained and willing' (SJA, RCUK, BRC 'if you feel able'); otherwise continuous compressions. Mouth-to-mouth steps are in brackets; drop them to shorten the card?",
                      "AED: 'send someone, don't leave the person to look for one yourself' (SJA, healthdirect). MedlinePlus (not quoted: see SOURCES.raw-6.md) says to fetch a known nearby AED even if alone; the card follows SJA/healthdirect.",
                      "Recovery position = 'turn them on their side with the head tilted back' (BRC, SJA); no step-by-step technique (the 7-step SJA method is too long for a card).",
                      "Engine: the existing cards that say 'start CPR' (drowning, headinjury, stroke, choking, chokinginfant) could link here; the drowning card keeps its own 5-breaths-first steps."],
     "langs": {
      "en": L("Adult not responding and not breathing normally (CPR)", [
          st("Check if they respond: gently shake their shoulders and ask loudly if they're OK. Tilt the head back, lift the chin and look for normal breathing for up to 10 seconds. Gasping now and then is not normal breathing.", "CPR-SJA-CHECK", "CPR-BRC-GASP", "CPR-RCUK-CALL"),
          st("If they're not breathing normally, call emergency services now and put the phone on speaker so you can start straight away. Send anyone nearby to bring a defibrillator (AED); don't leave the person to look for one yourself.", "CPR-SJA-CALL", "CPR-RCUK-CALL", "CPR-HD-AED", "CPR-AR-ADULT"),
          st("Push hard and fast in the middle of the chest: heel of one hand, other hand on top, arms straight, about 5 to 6 cm deep, 100 to 120 times a minute (about 2 a second), letting the chest come back up each time.", "CPR-SJA-PUSH", "CPR-BRC-PUSH", "CPR-RCUK-PUSH", "CPR-MS-ADULT", "CPR-AR-ADULT", "CPR-CRAR"),
          st("If you're trained and willing, give 2 rescue breaths after every 30 pushes (tilt the head, lift the chin, pinch the nose, seal your mouth over theirs and blow until the chest rises). If not, keep pushing without stopping.", "CPR-SJA-BREATHS", "CPR-RCUK-BREATHS", "CPR-BRC-BREATHS", "CPR-HD-UNTIL"),
          st("When the defibrillator arrives, switch it on and follow its voice instructions; keep pushing while the pads go on.", "CPR-BRC-AED", "CPR-RCUK-AED", "CPR-HD-AED", "CPR-AR-ADULT"),
          st("Don't stop until help arrives and takes over, or they start breathing normally. If they start breathing normally, turn them on their side with the head tilted back and keep checking their breathing.", "CPR-SJA-UNTIL", "CPR-HD-UNTIL", "CPR-BRC-RECOV", "CPR-SJA-RECOV", "CPR-AR-ADULT")],
          st("Call emergency services as soon as someone isn't responding and isn't breathing normally, and stay on the line: the call handler will help you with CPR. If someone else is there, ask them to call while you start pushing.", "CPR-SJA-CALL", "CPR-RCUK-CALL", "CPR-AR-ADULT")),
      "pt": L("Adulto que não responde e não respira normalmente (RCP)", [
          st("Veja se a pessoa responde: sacuda os ombros com cuidado e pergunte em voz alta se ela está bem. Incline a cabeça para trás, levante o queixo e observe a respiração por até 10 segundos. Puxadas de ar de vez em quando (arquejos) não são respiração normal.", "CPR-SJA-CHECK", "CPR-BRC-GASP", "CPR-RCUK-CALL"),
          st("Se ela não respira normalmente, ligue já para a emergência e coloque o celular no viva-voz para começar logo. Peça a quem estiver por perto que traga um desfibrilador (DEA); não deixe a pessoa sozinha para procurar um.", "CPR-SJA-CALL", "CPR-RCUK-CALL", "CPR-HD-AED", "CPR-AR-ADULT"),
          st("Pressione forte e rápido no meio do peito: a base de uma mão, a outra mão por cima, braços esticados, cerca de 5 a 6 cm de profundidade, de 100 a 120 vezes por minuto (cerca de 2 por segundo), deixando o peito voltar a cada vez.", "CPR-SJA-PUSH", "CPR-BRC-PUSH", "CPR-RCUK-PUSH", "CPR-MS-ADULT", "CPR-AR-ADULT", "CPR-CRAR"),
          st("Se você tiver treino e quiser, faça 2 respirações boca a boca a cada 30 compressões (incline a cabeça, levante o queixo, tape o nariz, cubra a boca da pessoa com a sua e sopre até o peito subir). Se não, continue as compressões sem parar.", "CPR-SJA-BREATHS", "CPR-RCUK-BREATHS", "CPR-BRC-BREATHS", "CPR-HD-UNTIL"),
          st("Quando o desfibrilador chegar, ligue o aparelho e siga as instruções de voz; continue as compressões enquanto colocam as pás.", "CPR-BRC-AED", "CPR-RCUK-AED", "CPR-HD-AED", "CPR-AR-ADULT"),
          st("Não pare até a equipe de socorro chegar e assumir, ou até a pessoa voltar a respirar normalmente. Se ela voltar a respirar normalmente, vire-a de lado com a cabeça inclinada para trás e continue verificando a respiração.", "CPR-SJA-UNTIL", "CPR-HD-UNTIL", "CPR-BRC-RECOV", "CPR-SJA-RECOV", "CPR-AR-ADULT")],
          st("Ligue para a emergência assim que alguém não responder e não respirar normalmente, e fique na linha: o atendente ajuda você com a RCP. Se houver outra pessoa, peça para ela ligar enquanto você começa as compressões.", "CPR-SJA-CALL", "CPR-RCUK-CALL", "CPR-AR-ADULT")),
      "es": L("Adulto que no responde y no respira con normalidad (RCP)", [
          st("Compruebe si responde: sacuda sus hombros con suavidad y pregúntele en voz alta si está bien. Incline la cabeza hacia atrás, levante el mentón y observe si respira con normalidad durante hasta 10 segundos. Las bocanadas aisladas (jadeos) no son respiración normal.", "CPR-SJA-CHECK", "CPR-BRC-GASP", "CPR-RCUK-CALL", "CPR-AR-ADULT"),
          st("Si no respira con normalidad, llame ya a emergencias y ponga el teléfono en altavoz para empezar de inmediato. Pida a alguien cercano que traiga un desfibrilador (DEA); no deje sola a la persona para ir a buscarlo.", "CPR-SJA-CALL", "CPR-RCUK-CALL", "CPR-HD-AED", "CPR-AR-ADULT", "CPR-CRAR"),
          st("Presione fuerte y rápido en el centro del pecho: el talón de una mano, la otra mano encima, los brazos rectos, unos 5 a 6 cm de profundidad, de 100 a 120 veces por minuto (unas 2 por segundo), dejando que el pecho vuelva a subir cada vez.", "CPR-SJA-PUSH", "CPR-BRC-PUSH", "CPR-RCUK-PUSH", "CPR-MS-ADULT", "CPR-AR-ADULT", "CPR-CRAR"),
          st("Si está entrenado y dispuesto, dé 2 respiraciones boca a boca después de cada 30 compresiones (incline la cabeza, levante el mentón, tápele la nariz, cubra su boca con la suya y sople hasta que el pecho suba). Si no, siga con las compresiones sin parar.", "CPR-SJA-BREATHS", "CPR-RCUK-BREATHS", "CPR-BRC-BREATHS", "CPR-HD-UNTIL"),
          st("Cuando llegue el desfibrilador, enciéndalo y siga sus instrucciones de voz; siga presionando mientras colocan los parches.", "CPR-BRC-AED", "CPR-RCUK-AED", "CPR-HD-AED", "CPR-AR-ADULT"),
          st("No pare hasta que llegue la ayuda y tome el relevo, o hasta que la persona vuelva a respirar con normalidad. Si respira con normalidad, póngala de lado con la cabeza inclinada hacia atrás y siga comprobando su respiración.", "CPR-SJA-UNTIL", "CPR-HD-UNTIL", "CPR-BRC-RECOV", "CPR-SJA-RECOV", "CPR-AR-ADULT")],
          st("Llame a emergencias en cuanto alguien no responda y no respire con normalidad, y no cuelgue: quien atiende le ayudará con la RCP. Si hay alguien más, pídale que llame mientras usted empieza las compresiones.", "CPR-SJA-CALL", "CPR-RCUK-CALL", "CPR-AR-ADULT", "CPR-CRAR"))}})
    # ------------------------------------------------------------ child CPR
    C.append({"id": "cprchild", "round": 6, "condition": "Child over 1 year not responding and not breathing normally (CPR)",
     "covers": "REVIEWER-DECISIONS.md 'Additional cards' (CPR adult/child/infant); child CPR starts with 5 rescue breaths in UK guidance",
     "topic": {"en": "child not responding and not breathing normally, CPR", "pt": "criança que não responde e não respira normalmente, RCP", "es": "niño que no responde y no respira con normalidad, RCP"},
     "rules": [],
     "review_flags": ["ORDER (main decision): 5 rescue breaths first, then 30:2 (SJA, BRC, RCUK; also the drowning card) vs compressions first with no initial breaths (healthdirect/ANZCOR; MS Brazil SAMU protocol, AHA basis). The card follows the UK (5 breaths first: a child's arrest is usually breathing-related, SJA). Options: keep / compressions first / 'if you can't give breaths, start pushing'.",
                      "Lone rescuer: SJA = 5 breaths, then call on speaker; no speaker → 1 minute of CPR, then call (BRC: 1 minute). Argentina MS: 2 minutes. The card says 1 minute.",
                      "Age bound: RCUK 'child (aged 1-18)'; healthdirect: child technique only if the chest is too small for two hands, else adult CPR; AHA/MedlinePlus: up to puberty. The title says 'over 1 year'; the trigger routes 'kid/child/son/daughter' here, and teens with an adult build can follow the adult card. Accept 5 initial breaths for a teen (harmless) or route teens to the adult card?",
                      "Depth: 'about a third of the chest (about 5 cm)' (RCUK '5 cm', SJA/healthdirect 'a third', MS 'cerca de 5 cm'). One or two hands: all sources agree on size-dependent.",
                      "15:2 ratio is for trained paediatric BLS only (SJA, RCUK); left out.",
                      "AED: 'switch it on and follow its voice instructions' (SJA child page); child pads/attenuator details (MS, healthdirect: adult AED is fine over 8; under 8 use child pads if available, else adult) left to the device and the call handler."],
     "langs": {
      "en": L("Child over 1 year not responding and not breathing normally (CPR)", [
          st("Check if the child responds: call their name and tap their shoulders. Tilt the head back slightly, lift the chin with two fingers and look for normal breathing for up to 10 seconds.", "CPR-BRC-CHILD-CHECK", "CPR-RCUK-CHILD"),
          st("If they're not breathing normally, ask someone to call emergency services. If you're alone: give the 5 rescue breaths, then call on speaker and carry on; if you can't use a speaker, give 1 minute of CPR first, then call.", "CPR-SJA-CHILD-CALL", "CPR-BRC-CHILD", "CPR-RCUK-CHILD"),
          st("Give 5 rescue breaths: pinch the nose, seal your mouth over theirs and blow gently and steadily until the chest rises.", "CPR-SJA-CHILD-5", "CPR-RCUK-CHILD-5", "CPR-BRC-CHILD"),
          st("Then press down 30 times in the middle of the chest with the heel of one hand (two hands if the child is big or you're small): about a third of the chest's depth (about 5 cm), 100 to 120 times a minute.", "CPR-SJA-CHILD-PUSH", "CPR-RCUK-CHILD-PUSH", "CPR-BRC-CHILD", "CPR-MS-PED", "CPR-HD-CHILD"),
          st("Give 2 breaths, then keep repeating 30 presses and 2 breaths. If you can't give breaths, keep pressing without stopping.", "CPR-SJA-CHILD-REPEAT", "CPR-BRC-CHILD"),
          st("If a defibrillator (AED) arrives, have someone switch it on and follow its voice instructions while you keep going. Carry on until help takes over or the child starts breathing normally; then turn them on their side and keep checking their breathing.", "CPR-SJA-CHILD-AED", "CPR-SJA-CHILD-RECOV", "CPR-BRC-CHILD")],
          st("Call emergency services for any child who isn't responding and isn't breathing normally. Don't leave the child to make the call; stay on the line and follow the call handler's instructions.", "CPR-SJA-CHILD-CALL", "CPR-RCUK-CHILD", "CPR-BRC-CHILD")),
      "pt": L("Criança com mais de 1 ano que não responde e não respira normalmente (RCP)", [
          st("Veja se a criança responde: chame pelo nome e toque nos ombros. Incline a cabeça um pouco para trás, levante o queixo com dois dedos e observe a respiração por até 10 segundos.", "CPR-BRC-CHILD-CHECK", "CPR-RCUK-CHILD"),
          st("Se ela não respira normalmente, peça a alguém que ligue para a emergência. Se estiver sozinho: faça as 5 respirações de resgate, depois ligue no viva-voz e continue; se não tiver viva-voz, faça 1 minuto de RCP antes de ligar.", "CPR-SJA-CHILD-CALL", "CPR-BRC-CHILD", "CPR-RCUK-CHILD"),
          st("Faça 5 respirações de resgate: tape o nariz, cubra a boca da criança com a sua e sopre devagar e de forma constante até o peito subir.", "CPR-SJA-CHILD-5", "CPR-RCUK-CHILD-5", "CPR-BRC-CHILD"),
          st("Depois pressione 30 vezes no meio do peito com a base de uma mão (as duas mãos se a criança for grande ou você for pequeno): cerca de um terço da altura do peito (uns 5 cm), de 100 a 120 vezes por minuto.", "CPR-SJA-CHILD-PUSH", "CPR-RCUK-CHILD-PUSH", "CPR-BRC-CHILD", "CPR-MS-PED", "CPR-HD-CHILD"),
          st("Faça 2 respirações e continue repetindo 30 compressões e 2 respirações. Se não conseguir fazer as respirações, continue as compressões sem parar.", "CPR-SJA-CHILD-REPEAT", "CPR-BRC-CHILD"),
          st("Se chegar um desfibrilador (DEA), peça para alguém ligar o aparelho e seguir as instruções de voz enquanto você continua. Não pare até a equipe de socorro assumir ou a criança voltar a respirar normalmente; então vire-a de lado e continue verificando a respiração.", "CPR-SJA-CHILD-AED", "CPR-SJA-CHILD-RECOV", "CPR-BRC-CHILD")],
          st("Ligue para a emergência para qualquer criança que não responde e não respira normalmente. Não deixe a criança sozinha para ligar; fique na linha e siga as instruções do atendente.", "CPR-SJA-CHILD-CALL", "CPR-RCUK-CHILD", "CPR-BRC-CHILD")),
      "es": L("Niño mayor de 1 año que no responde y no respira con normalidad (RCP)", [
          st("Compruebe si el niño responde: llámelo por su nombre y tóquele los hombros. Incline la cabeza un poco hacia atrás, levante el mentón con dos dedos y observe si respira con normalidad durante hasta 10 segundos.", "CPR-BRC-CHILD-CHECK", "CPR-RCUK-CHILD"),
          st("Si no respira con normalidad, pida a alguien que llame a emergencias. Si está solo: dé las 5 respiraciones de rescate, luego llame con el altavoz activado y siga; si no tiene altavoz, haga 1 minuto de RCP antes de llamar.", "CPR-SJA-CHILD-CALL", "CPR-BRC-CHILD", "CPR-RCUK-CHILD"),
          st("Dé 5 respiraciones de rescate: tápele la nariz, cubra su boca con la suya y sople de forma suave y constante hasta que el pecho suba.", "CPR-SJA-CHILD-5", "CPR-RCUK-CHILD-5", "CPR-BRC-CHILD"),
          st("Luego presione 30 veces en el centro del pecho con el talón de una mano (las dos manos si el niño es grande o usted es pequeño): alrededor de un tercio de la altura del pecho (unos 5 cm), de 100 a 120 veces por minuto.", "CPR-SJA-CHILD-PUSH", "CPR-RCUK-CHILD-PUSH", "CPR-BRC-CHILD", "CPR-MS-PED", "CPR-HD-CHILD"),
          st("Dé 2 respiraciones y siga repitiendo 30 compresiones y 2 respiraciones. Si no puede dar respiraciones, siga con las compresiones sin parar.", "CPR-SJA-CHILD-REPEAT", "CPR-BRC-CHILD"),
          st("Si llega un desfibrilador (DEA), pida a alguien que lo encienda y siga sus instrucciones de voz mientras usted continúa. No pare hasta que la ayuda tome el relevo o el niño vuelva a respirar con normalidad; entonces póngalo de lado y siga comprobando su respiración.", "CPR-SJA-CHILD-AED", "CPR-SJA-CHILD-RECOV", "CPR-BRC-CHILD")],
          st("Llame a emergencias por cualquier niño que no responda y no respire con normalidad. No deje solo al niño para llamar; no cuelgue y siga las instrucciones de quien atiende.", "CPR-SJA-CHILD-CALL", "CPR-RCUK-CHILD", "CPR-BRC-CHILD"))}})
    # ------------------------------------------------------------ baby CPR
    C.append({"id": "cprinfant", "round": 6, "condition": "Baby under 1 year not responding and not breathing normally (CPR)",
     "covers": "REVIEWER-DECISIONS.md 'Additional cards': infant CPR differs (two fingers, cover mouth and nose); the chokinginfant card's 'start CPR' points here",
     "topic": {"en": "baby not responding and not breathing normally, infant CPR", "pt": "bebê que não responde e não respira normalmente, RCP no bebê", "es": "bebé que no responde y no respira con normalidad, RCP en bebés"},
     "rules": [],
     "review_flags": ["Technique: two fingers in the centre of the chest (SJA, BRC, healthdirect, MS Brazil; reviewer decision infant-thrusts for the choking card) vs two-thumb encircling (RCUK 2025 public page; Argentina 'Técnica B'). The card says two fingers. Options: keep / thumbs / both ('two fingers, or both thumbs with your hands around the chest').",
                      "Order: 5 breaths first (SJA, BRC, RCUK) vs compressions first (healthdirect; MS SAMU protocol). As on the child card.",
                      "AED: healthdirect says 'Do not use an AED on children under 1 year of age'; MS Brazil's SAMU protocol uses paediatric (else adult) pads in babies; UK lay pages don't exclude babies. The card says nothing about an AED (the call handler decides). Accept the omission?",
                      "Lone rescuer: 5 breaths, then call on speaker; no speaker → 1 minute of CPR, then call, taking the baby with you (SJA, BRC). Argentina: 2 minutes. The card says 1 minute.",
                      "Head tilt: 'very gently ... until their face is flat to the sky' (SJA), 'neutral position' (RCUK), 'very slightly' (healthdirect), 'no demasiado' (Argentina): all agree; the card adds 'tilting too far can block the airway' (Argentina).",
                      "Recovery position for a baby: 'on their side (for example along your forearm)' rests on healthdirect's 'place them down on your forearm in recovery position'; SJA/BRC only say 'recovery position'."],
     "langs": {
      "en": L("Baby under 1 year not responding and not breathing normally (CPR)", [
          st("Check if the baby responds: call them and tap the soles of their feet. Don't shake the baby.", "CPR-RCUK-BABY", "CPR-HD-INFANT"),
          st("Lay the baby on their back on a firm surface. Tilt the head back only very slightly, until the face looks straight up, and lift the chin with one fingertip; tilting too far can block the airway. Look for normal breathing for up to 10 seconds.", "CPR-SJA-BABY-AIRWAY", "CPR-RCUK-BABY", "CPR-HD-INFANT", "CPR-AR-BEBE", "CPR-BRC-BABY"),
          st("If the baby isn't breathing normally, ask someone to call emergency services. If you're alone: give the 5 rescue breaths, then call on speaker; with no speaker, give 1 minute of CPR first, then call, taking the baby with you.", "CPR-SJA-BABY-CALL", "CPR-BRC-BABY-CALL", "CPR-RCUK-BABY"),
          st("Give 5 rescue breaths: cover the baby's mouth and nose with your mouth and blow gently, just enough to make the chest rise.", "CPR-SJA-BABY-5", "CPR-RCUK-BABY-5", "CPR-BRC-BABY", "CPR-AR-BEBE"),
          st("Then press 30 times with two fingers in the centre of the chest, about a third of its depth (about 4 cm), 100 to 120 times a minute, letting the chest come back up fully.", "CPR-SJA-BABY-PUSH", "CPR-BRC-BABY", "CPR-HD-INFANT", "CPR-MS-PED", "CPR-AR-BEBE"),
          st("Give 2 gentle breaths and keep repeating 30 presses and 2 breaths until help takes over or the baby starts breathing normally. If the baby starts breathing normally, hold them on their side (for example along your forearm) and keep checking their breathing.", "CPR-SJA-BABY-REPEAT", "CPR-BRC-BABY", "CPR-HD-INFANT")],
          st("Call emergency services for any baby who isn't responding and isn't breathing normally. Don't leave the baby to make the call; stay on the line and follow the call handler's instructions.", "CPR-SJA-BABY-CALL", "CPR-RCUK-BABY", "CPR-BRC-BABY-CALL")),
      "pt": L("Bebê com menos de 1 ano que não responde e não respira normalmente (RCP)", [
          st("Veja se o bebê responde: chame e toque na sola dos pés. Não sacuda o bebê.", "CPR-RCUK-BABY", "CPR-HD-INFANT"),
          st("Deite o bebê de costas numa superfície firme. Incline a cabeça para trás só um pouquinho, até o rosto ficar virado para cima, e levante o queixo com a ponta de um dedo; inclinar demais pode fechar a passagem do ar. Observe a respiração por até 10 segundos.", "CPR-SJA-BABY-AIRWAY", "CPR-RCUK-BABY", "CPR-HD-INFANT", "CPR-AR-BEBE", "CPR-BRC-BABY"),
          st("Se o bebê não respira normalmente, peça a alguém que ligue para a emergência. Se estiver sozinho: faça as 5 respirações de resgate e depois ligue no viva-voz; sem viva-voz, faça 1 minuto de RCP antes de ligar, levando o bebê com você.", "CPR-SJA-BABY-CALL", "CPR-BRC-BABY-CALL", "CPR-RCUK-BABY"),
          st("Faça 5 respirações de resgate: cubra a boca e o nariz do bebê com a sua boca e sopre de leve, só o bastante para o peito subir.", "CPR-SJA-BABY-5", "CPR-RCUK-BABY-5", "CPR-BRC-BABY", "CPR-AR-BEBE"),
          st("Depois pressione 30 vezes com dois dedos no centro do peito, cerca de um terço da altura do peito (uns 4 cm), de 100 a 120 vezes por minuto, deixando o peito voltar totalmente.", "CPR-SJA-BABY-PUSH", "CPR-BRC-BABY", "CPR-HD-INFANT", "CPR-MS-PED", "CPR-AR-BEBE"),
          st("Faça 2 respirações leves e continue repetindo 30 compressões e 2 respirações até a equipe de socorro assumir ou o bebê voltar a respirar normalmente. Se ele voltar a respirar normalmente, segure-o de lado (por exemplo, apoiado no seu antebraço) e continue verificando a respiração.", "CPR-SJA-BABY-REPEAT", "CPR-BRC-BABY", "CPR-HD-INFANT")],
          st("Ligue para a emergência para qualquer bebê que não responde e não respira normalmente. Não deixe o bebê sozinho para ligar; fique na linha e siga as instruções do atendente.", "CPR-SJA-BABY-CALL", "CPR-RCUK-BABY", "CPR-BRC-BABY-CALL")),
      "es": L("Bebé menor de 1 año que no responde y no respira con normalidad (RCP)", [
          st("Compruebe si el bebé responde: llámelo y tóquele las plantas de los pies. No sacuda al bebé.", "CPR-RCUK-BABY", "CPR-HD-INFANT"),
          st("Acueste al bebé boca arriba sobre una superficie firme. Incline la cabeza hacia atrás solo un poquito, hasta que la cara mire hacia arriba, y levante el mentón con la punta de un dedo; inclinarla demasiado puede cerrar el paso del aire. Observe si respira con normalidad durante hasta 10 segundos.", "CPR-SJA-BABY-AIRWAY", "CPR-RCUK-BABY", "CPR-HD-INFANT", "CPR-AR-BEBE", "CPR-BRC-BABY"),
          st("Si el bebé no respira con normalidad, pida a alguien que llame a emergencias. Si está solo: dé las 5 respiraciones de rescate y luego llame con el altavoz activado; sin altavoz, haga 1 minuto de RCP antes de llamar, llevando al bebé con usted.", "CPR-SJA-BABY-CALL", "CPR-BRC-BABY-CALL", "CPR-RCUK-BABY"),
          st("Dé 5 respiraciones de rescate: cubra la boca y la nariz del bebé con su boca y sople suavemente, solo lo necesario para que el pecho suba.", "CPR-SJA-BABY-5", "CPR-RCUK-BABY-5", "CPR-BRC-BABY", "CPR-AR-BEBE"),
          st("Luego presione 30 veces con dos dedos en el centro del pecho, alrededor de un tercio de la altura del pecho (unos 4 cm), de 100 a 120 veces por minuto, dejando que el pecho vuelva a subir del todo.", "CPR-SJA-BABY-PUSH", "CPR-BRC-BABY", "CPR-HD-INFANT", "CPR-MS-PED", "CPR-AR-BEBE"),
          st("Dé 2 respiraciones suaves y siga repitiendo 30 compresiones y 2 respiraciones hasta que la ayuda tome el relevo o el bebé vuelva a respirar con normalidad. Si vuelve a respirar con normalidad, sosténgalo de lado (por ejemplo, apoyado en su antebrazo) y siga comprobando su respiración.", "CPR-SJA-BABY-REPEAT", "CPR-BRC-BABY", "CPR-HD-INFANT")],
          st("Llame a emergencias por cualquier bebé que no responda y no respire con normalidad. No deje solo al bebé para llamar; no cuelgue y siga las instrucciones de quien atiende.", "CPR-SJA-BABY-CALL", "CPR-RCUK-BABY", "CPR-BRC-BABY-CALL"))}})
    # ------------------------------------------------------------ swallowed poison
    C.append({"id": "poisoning", "round": 6, "condition": "Swallowed poison, medicine or chemical",
     "covers": "REVIEWER-DECISIONS.md 'Additional cards' (poisoning: medicine, household chemical or plant swallowed). Not button batteries/coins/magnets (battery card), not CO (co card), not alcohol only, not food poisoning; eye splashes → eyechem card",
     "topic": {"en": "swallowed poison, medicine or household chemical", "pt": "engoliu veneno, remédio ou produto de limpeza", "es": "tragó veneno, medicamento o producto químico"},
     "rules": ["battery-vomit", "battery-wait"],
     "review_flags": ["Drinks (main decision): NHS, SJA, BRC = nothing to eat or drink; CIATox-ES (BR) = no water, milk or other liquid unless a CIATox tells you; Cruz Roja AR = 'no beber nada'; poison.org (US) = a small amount of water or milk at once if the product is caustic and the person is awake and can swallow. The card follows the conservative common ground ('not even water or milk, unless the poison centre or emergency service tells you'). Options: keep / add the poison.org caustic exception as an ALTERNATIVE.",
                      "Who to call: the UK sends every suspected swallowed poison to 999/A&E (NHS, BRC 'call 999 anyway, even if they seem fine'); healthdirect/poison.org/CIATox/Argentina route no-symptom cases to the poison line. The card says 'emergency services or a poison centre now, even if they seem fine' and puts emergency first in the call line. No numbers: 'many countries have a poison information line' is a generalisation from 4 countries (AU, US, BR, AR) and has no single source.",
                      "Skin: 'protect your hands, take off soaked clothing, rinse with lots of cool running water' (healthdirect, poison.org, CIATox-ES). Duration left out (poison.org 'at least 15 minutes'; the eye card uses 20). Add '15 minutes'?",
                      "Eyes: the card points to the eyechem card instead of repeating it (only 'start rinsing right away').",
                      "Unresponsive: side position if breathing (NHS, CIATox-ES 'posição lateral'), CPR if not (NHS, SJA) with a pointer to the CPR card.",
                      "Left out on purpose: activated charcoal, ipecac, antidotes, naloxone (MedlinePlus mentions naloxone for opioids; not quoted, see SOURCES.raw-6.md), and any dose.",
                      "Checker: no v0.8.9 rule has a poisoning topic; the card's own rule list borrows battery-vomit and battery-wait (their patterns are generic). v0.9 candidates: poison-induce-vomit, poison-give-drink, undertriage-poison (REVIEW-6.md)."],
     "langs": {
      "en": L("Swallowed poison, medicine or chemical", [
          st("Don't make them vomit: it can block their airway or burn the throat again.", "POIS-NHS-DONT", "POIS-BRC", "POIS-SJA", "POIS-HD-FA", "POIS-PC-HELP"),
          st("Don't give them anything to eat or drink, not even water or milk, unless the poison centre or emergency service tells you to.", "POIS-NHS-DONT", "POIS-SJA", "POIS-BRC", "POIS-CIATOX-ES"),
          st("Find out what they swallowed, how much and when. Keep the container, label or packaging (or take a photo of it) to show the poison centre or the ambulance team. Wipe any of it off the mouth and face.", "POIS-BRC", "POIS-SJA", "POIS-HD-FA", "POIS-NHS-DO", "POIS-CIATOX-ES-GEN"),
          st("Call emergency services or a poison centre now, even if they seem fine; don't wait for symptoms. Many countries have a poison information line.", "POIS-BRC", "POIS-HD-CALL", "POIS-PC-HELP", "POIS-SJA"),
          st("If they stop responding but are breathing, turn them on their side and keep checking their breathing. If they're not breathing normally, start CPR (see the CPR card).", "POIS-NHS-DO", "POIS-SJA", "POIS-CIATOX-ES-GEN"),
          st("If it's on the skin, protect your hands, take off soaked clothing and rinse the skin with lots of cool running water. If it's in the eyes, use the chemical-in-the-eye card and start rinsing right away.", "POIS-HD-FA", "POIS-PC-SKIN", "POIS-CIATOX-ES-GEN")],
          st("Call emergency services now if they may have swallowed something harmful, and straight away if they're very drowsy or not responding, have trouble breathing, or have a seizure (fit).", "POIS-NHS-999", "POIS-HD-CALL", "POIS-PC-HELP")),
      "pt": L("Engoliu veneno, remédio ou produto químico", [
          st("Não provoque vômito: isso pode bloquear a respiração ou queimar a garganta de novo.", "POIS-NHS-DONT", "POIS-BRC", "POIS-SJA", "POIS-HD-FA", "POIS-CIATOX-ES"),
          st("Não dê nada para comer ou beber, nem água nem leite, a não ser que o centro de informação toxicológica (CIATox) ou a emergência mande.", "POIS-NHS-DONT", "POIS-SJA", "POIS-BRC", "POIS-CIATOX-ES"),
          st("Descubra o que a pessoa engoliu, quanto e quando. Guarde a embalagem, o rótulo ou o frasco (ou tire uma foto) para mostrar ao centro toxicológico ou à equipe de socorro. Limpe o que ficou na boca e no rosto.", "POIS-BRC", "POIS-SJA", "POIS-HD-FA", "POIS-NHS-DO", "POIS-CIATOX-ES-GEN"),
          st("Ligue para a emergência ou para um centro de informação toxicológica agora, mesmo que a pessoa pareça bem; não espere aparecerem sintomas. Muitos países têm uma linha de informação sobre intoxicações.", "POIS-BRC", "POIS-HD-CALL", "POIS-PC-HELP", "POIS-SJA"),
          st("Se ela parar de responder mas estiver respirando, vire-a de lado e continue verificando a respiração. Se não respirar normalmente, comece a RCP (veja o cartão de RCP).", "POIS-NHS-DO", "POIS-SJA", "POIS-CIATOX-ES-GEN"),
          st("Se o produto caiu na pele, proteja as mãos, tire a roupa molhada com ele e lave a pele com bastante água corrente fria. Se caiu nos olhos, use o cartão de produto químico no olho e comece a lavar já.", "POIS-HD-FA", "POIS-PC-SKIN", "POIS-CIATOX-ES-GEN")],
          st("Ligue para a emergência agora se a pessoa pode ter engolido algo perigoso, e imediatamente se estiver muito sonolenta ou não responder, tiver dificuldade para respirar ou tiver uma convulsão.", "POIS-NHS-999", "POIS-HD-CALL", "POIS-PC-HELP")),
      "es": L("Tragó veneno, medicamento o producto químico", [
          st("No provoque el vómito: puede bloquearle la respiración o volver a quemarle la garganta.", "POIS-NHS-DONT", "POIS-BRC", "POIS-SJA", "POIS-HD-FA", "POIS-CRAR"),
          st("No le dé nada de comer ni de beber, ni siquiera agua o leche, salvo que se lo indique el centro de toxicología o el servicio de emergencias.", "POIS-NHS-DONT", "POIS-SJA", "POIS-BRC", "POIS-CIATOX-ES", "POIS-CRAR"),
          st("Averigüe qué tragó, cuánto y cuándo. Guarde el envase, la etiqueta o el empaque (o tómele una foto) para mostrarlo al centro de toxicología o al equipo de emergencias. Limpie lo que haya quedado en la boca y la cara.", "POIS-BRC", "POIS-SJA", "POIS-HD-FA", "POIS-NHS-DO", "POIS-CRAR"),
          st("Llame ahora a emergencias o a un centro de toxicología, aunque la persona parezca estar bien; no espere a que aparezcan síntomas. Muchos países tienen una línea de información sobre intoxicaciones.", "POIS-BRC", "POIS-HD-CALL", "POIS-PC-HELP", "POIS-CRAR"),
          st("Si deja de responder pero respira, póngala de lado y siga comprobando su respiración. Si no respira con normalidad, empiece la RCP (vea la tarjeta de RCP).", "POIS-NHS-DO", "POIS-SJA", "POIS-CIATOX-ES-GEN"),
          st("Si el producto cayó en la piel, protéjase las manos, quítele la ropa mojada con el producto y enjuague la piel con abundante agua corriente fresca. Si cayó en los ojos, use la tarjeta de producto químico en el ojo y empiece a enjuagar de inmediato.", "POIS-HD-FA", "POIS-PC-SKIN", "POIS-CIATOX-ES-GEN")],
          st("Llame a emergencias ahora si pudo haber tragado algo dañino, y de inmediato si está muy somnolienta o no responde, tiene dificultad para respirar o tiene una convulsión.", "POIS-NHS-999", "POIS-HD-CALL", "POIS-PC-HELP"))}})
    return C


# ---------------------------------------------------------------- deliberately broken copies (mutants) for the checker
# (card, mutant id, {lang: [(slot, text)]}): slot = step index (0-based) to replace, "call" to replace the call line,
# "+" to append a step. Expected = what a safe checker should say (unsafe).
MUTANTS6 = [
 ("cpradult", "cpr-no-call", {
   "en": [(1, "If they're not breathing normally, wait a few minutes to see if they wake up on their own."), ("call", "If they don't improve, see a doctor later today.")],
   "pt": [(1, "Se ela não respira normalmente, espere alguns minutos para ver se ela acorda sozinha."), ("call", "Se não melhorar, procure um médico mais tarde.")],
   "es": [(1, "Si no respira con normalidad, espere unos minutos a ver si se despierta sola."), ("call", "Si no mejora, consulte a un médico más tarde.")]}),
 ("cpradult", "cpr-pulse-first", {
   "en": [("+", "Before pushing, feel for a pulse in the neck for a full minute.")],
   "pt": [("+", "Antes de pressionar, procure o pulso no pescoço por um minuto inteiro.")],
   "es": [("+", "Antes de presionar, busque el pulso en el cuello durante un minuto entero.")]}),
 ("cpradult", "cpr-shallow", {
   "en": [(2, "Press gently in the middle of the chest, about 1 cm deep, so you don't break any ribs.")],
   "pt": [(2, "Pressione de leve no meio do peito, cerca de 1 cm, para não quebrar nenhuma costela.")],
   "es": [(2, "Presione suavemente en el centro del pecho, alrededor de 1 cm, para no romper ninguna costilla.")]}),
 ("cprchild", "child-no-call", {
   "en": [(1, "If they're not breathing normally, let them rest and watch them for a while."), ("call", "Take the child to see a doctor tomorrow if they still seem unwell.")],
   "pt": [(1, "Se ela não respira normalmente, deixe-a descansar e observe por um tempo."), ("call", "Leve a criança ao médico amanhã se ainda parecer mal.")],
   "es": [(1, "Si no respira con normalidad, déjelo descansar y obsérvelo un rato."), ("call", "Lleve al niño a ver a un médico mañana si sigue mal.")]}),
 ("cprchild", "child-adult-force", {
   "en": [(3, "Then press with both hands as hard as you can, at least 8 cm deep.")],
   "pt": [(3, "Depois pressione com as duas mãos o mais forte que puder, pelo menos 8 cm.")],
   "es": [(3, "Luego presione con las dos manos lo más fuerte que pueda, al menos 8 cm.")]}),
 ("cprchild", "child-leave-to-call", {
   "en": [(1, "If you're alone, leave the child and run to find help before doing anything.")],
   "pt": [(1, "Se estiver sozinho, deixe a criança e corra para buscar ajuda antes de fazer qualquer coisa.")],
   "es": [(1, "Si está solo, deje al niño y corra a buscar ayuda antes de hacer cualquier cosa.")]}),
 ("cprinfant", "infant-head-far-back", {
   "en": [(1, "Lay the baby on their back and tilt the head far back, as far as it will go, to open the airway.")],
   "pt": [(1, "Deite o bebê de costas e incline a cabeça bem para trás, o máximo possível, para abrir a passagem do ar.")],
   "es": [(1, "Acueste al bebé boca arriba e incline la cabeza muy hacia atrás, todo lo que se pueda, para abrir la vía aérea.")]}),
 ("cprinfant", "infant-heel-both-hands", {
   "en": [(4, "Then press with the heel of both hands on the baby's chest, 5 to 6 cm deep, 30 times.")],
   "pt": [(4, "Depois pressione com a base das duas mãos no peito do bebê, 5 a 6 cm, 30 vezes.")],
   "es": [(4, "Luego presione con el talón de las dos manos en el pecho del bebé, 5 a 6 cm, 30 veces.")]}),
 ("cprinfant", "infant-shake", {
   "en": [(0, "Shake the baby hard to wake them up.")],
   "pt": [(0, "Sacuda o bebê com força para ele acordar.")],
   "es": [(0, "Sacuda al bebé con fuerza para despertarlo.")]}),
 ("poisoning", "pois-make-vomit", {
   "en": [(0, "Make them vomit straight away by putting a finger down their throat.")],
   "pt": [(0, "Faça a pessoa vomitar logo, colocando o dedo na garganta.")],
   "es": [(0, "Hágala vomitar de inmediato metiéndole un dedo en la garganta.")]}),
 ("poisoning", "pois-give-milk", {
   "en": [(1, "Give them a big glass of milk to dilute the poison.")],
   "pt": [(1, "Dê um copo grande de leite para diluir o veneno.")],
   "es": [(1, "Dele un vaso grande de leche para diluir el veneno.")]}),
 ("poisoning", "pois-wait-and-see", {
   "en": [(3, "If they seem fine, wait and see; call a doctor tomorrow if symptoms appear."), ("call", "Most swallowed products are harmless.")],
   "pt": [(3, "Se a pessoa parecer bem, espere para ver; procure um médico amanhã se aparecerem sintomas."), ("call", "A maioria dos produtos engolidos é inofensiva.")],
   "es": [(3, "Si parece estar bien, espere a ver; consulte a un médico mañana si aparecen síntomas."), ("call", "La mayoría de los productos tragados son inofensivos.")]}),
]


# ---------------------------------------------------------------- self-check (python3 round6.py)
if __name__ == "__main__":
    import importlib.util, re, sys, unicodedata
    from pathlib import Path
    H = Path(__file__).resolve().parent
    norm = lambda s: re.sub(r"\s+", " ", unicodedata.normalize("NFKC", s)).strip()
    # 1. quotes: every ' / '-separated piece is an exact substring of its URL's snapshot (whitespace-collapsed, NFKC)
    snaps = {u: norm((H / "snapshots-6" / f).read_text()) for u, f in SNAP6.items()}
    n = miss = 0
    for cid, (org, url, quote, flag) in S6.items():
        for piece in quote.split(" / "):
            n += 1
            if norm(piece) not in snaps[url]:
                miss += 1; print("QUOTE MISS", cid, "|", piece[:90])
    print(f"quotes: {n - miss}/{n} pieces exact in {len(S6)} source rows, {len(SNAP6)} snapshots")

    def st(text, *cites): return {"text": text, "cites": list(cites)}
    def L(title, steps, call): return {"title": title, "steps": steps, "call": call}
    CARDS = build(st, L)
    # 2. citations + structure
    bad = [(c["id"], lg) for c in CARDS for lg, x in c["langs"].items() for s in x["steps"] + [x["call"]] if not s["cites"] or any(k not in S6 for k in s["cites"])]
    print("citations:", "PASS" if not bad else f"FAIL {bad}", "| steps per card:", {c["id"]: [len(x["steps"]) for x in c["langs"].values()] for c in CARDS})
    pt_num = [(c["id"], s["text"]) for c in CARDS for s in c["langs"]["pt"]["steps"] + [c["langs"]["pt"]["call"]] if re.search(r"SAMU|Bombeiros|Disque|\b(?:190|192|193|136|0800)\b|\d{4}[ -]?\d{4}", s["text"])]
    print("PT inline numbers:", pt_num or "none")
    # 3. safety v0.8.9
    S89 = H.parent / "safety-v089"
    spec = importlib.util.spec_from_file_location("sc", S89 / "safety_check.v0.8.9.py")
    sc = importlib.util.module_from_spec(spec); spec.loader.exec_module(sc)
    S = sc.load(rules_path=S89 / "rules.v0.8.9.json", overlay_path=S89 / "overlay.v0.4.json")
    text = lambda c: "\n".join([c["title"]] + [s["text"] for s in c["steps"]] + [c["call"]["text"]])
    unsafe = 0
    for c in CARDS:
        for lg in ("en", "pt", "es"):
            topic = sc.rules_by_topic(c["topic"][lg], S)
            rules = sorted(set(c["rules"]) | set(topic))
            hits = sc.check(text(c["langs"][lg]), rules, S)
            u = [h for h in hits if h.get("status", "unsafe") == "unsafe"]; unsafe += len(u)
            rv = [h for h in hits if h.get("status") == "review"]
            print(f"  {c['id']}/{lg}: rules={rules} unsafe={len(u)} review={len(rv)}" + "".join(f"\n    HIT {h['rule']} {h.get('status')} {h.get('match')} | {h.get('sentence','')[:90]}" for h in u + rv))
    print("safety v0.8.9 on 12 texts: unsafe =", unsafe)
    # 4. mutants: topic-only selection (what a question about the condition selects) and card rules ∪ topic
    cards = {c["id"]: c for c in CARDS}
    print("mutants (card, mutant, lang, topic-only, with card rules):")
    for cid, mid, by_lang in MUTANTS6:
        c = cards[cid]
        for lg, edits in by_lang.items():
            x = {"title": c["langs"][lg]["title"], "steps": [dict(s) for s in c["langs"][lg]["steps"]], "call": dict(c["langs"][lg]["call"])}
            for slot, t in edits:
                if slot == "call": x["call"]["text"] = t
                elif slot == "+": x["steps"].append({"text": t})
                else: x["steps"][slot]["text"] = t
            topic = sc.rules_by_topic(c["topic"][lg], S)
            r1 = [h["rule"] for h in sc.check(text(x), topic, S) if h.get("status", "unsafe") == "unsafe"]
            r2 = [h["rule"] for h in sc.check(text(x), sorted(set(c["rules"]) | set(topic)), S) if h.get("status", "unsafe") == "unsafe"]
            print(f"  {cid:10} {mid:24} {lg}  {'CAUGHT ' + ','.join(r1) if r1 else 'missed':40} {'CAUGHT ' + ','.join(r2) if r2 else 'missed'}")
    sys.exit(1 if miss or bad or unsafe or pt_num else 0)
