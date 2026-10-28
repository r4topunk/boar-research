# First-aid cards round 2: review sheet for r4to (first-aid-cards draft 2026-10-03, DRAFT, NOT FOR SHIPPING)

TL;DR: DRAFT, NOT FOR SHIPPING. Round 1: 10 cards; round 2: 4 cards (heart attack, head injury, tsunami, hypothermia); round 3: 6 cards (burn, frostbite, heatstroke, nosebleed, earthquake, animal bite); round 4: 9 cards (bleeding, stroke, anaphylaxis, chemical in the eye, electric shock, altitude, sea-creature puncture, tick, heat exhaustion); all EN/PT/ES, every step cited to a verbatim quote from an official source (SOURCES.md). It needs r4to's sign-off on the wording, a clinical review, and native-speaker reviews (PT-BR, ES) before anything ships.

How to review: for each card, read the EN steps against the quotes below them, then PT and ES. Tick a box only if you accept the wording as is; write any change next to it. **Nothing ships without your sign-off** (and the clinical + native-speaker reviews listed at the end).

Automatic checks (check_cards.py): citations on every step = PASS; safety rules v0.8.6 = PASS (0 unsafe in all 87 card-language texts, all rounds).

## heartattack: Chest pain / suspected heart attack
Covers: Sonar: the placeholder heartattack card (with aspirin dosing) fires on 5 chest-pain items; replaces it

**Decisions for you:** (1) ASPIRIN (decision): the default card (A) gives NO dose; it calls emergency first. Alternative B adds 'adult (16+) and not allergic: one 300 mg aspirin, chewed slowly' (St John UK; NHS/BHF: 300 mg + allergy only; 'chew' and 'under 16' rest on St John alone). Country variation is NOT verified (AHA blocked the fetch; US practice and Brazilian/Spanish guidance not checked). Other contraindications (bleeding disorders, blood thinners, stomach ulcer) are not on these lay pages. Recommend A, with B only after clinical review. (2) Metaphor false positive ('dor no peito de saudade'): with A, the card tells a sad person to sit down and call emergency, which is annoying but harmless. With B, it could prompt an unnecessary aspirin, one more reason for A. (3) CDC has no 'don't drive' line; NHS and BHF do.

**EN: Possible heart attack**

- [ ] 1. Help them sit on the floor with knees bent and back supported (or on a chair), and keep them calm.  <sub>[HEART-REST, HEART-CALM]</sub>
- [ ] 2. Don't drive them or let them drive to hospital; wait for the ambulance.  <sub>[HEART-DRIVE, HEART-DRIVE-BHF]</sub>
- [ ] 3. Keep checking that they're responding and breathing.  <sub>[HEART-REST]</sub>
- [ ] 4. If they stop responding and aren't breathing normally, start CPR and send someone for a defibrillator.  <sub>[HEART-CPR, HEART-CPR-BHF]</sub>
- [ ] ☎ Call emergency services now if you think it's a heart attack: chest pain or pressure (tight, crushing or squeezing) that may spread to the arm, neck, jaw or back, with shortness of breath, sweating or feeling sick. Don't worry about wasting anyone's time.  <sub>[HEART-CALL, HEART-CALL-NHS, HEART-SIGNS, HEART-SIGNS-CDC]</sub>

- [ ] **ALTERNATIVE (decision, not in the default card):** If they're an adult (16 or over) and not allergic to aspirin, give one 300 mg aspirin to chew slowly.  <sub>[HEART-ASPIRIN, HEART-ASPIRIN-NHS]</sub>

**PT: Possível infarto**

- [ ] 1. Ajude a pessoa a sentar no chão com os joelhos dobrados e as costas apoiadas (ou numa cadeira) e mantenha-a calma.  <sub>[HEART-REST, HEART-CALM]</sub>
- [ ] 2. Não leve a pessoa de carro nem deixe que ela dirija até o hospital; espere a ambulância.  <sub>[HEART-DRIVE, HEART-DRIVE-BHF]</sub>
- [ ] 3. Continue verificando se ela responde e respira.  <sub>[HEART-REST]</sub>
- [ ] 4. Se ela parar de responder e não respirar normalmente, comece a RCP e peça para alguém buscar um desfibrilador (DEA).  <sub>[HEART-CPR, HEART-CPR-BHF]</sub>
- [ ] ☎ Ligue para a emergência (SAMU 192) agora se achar que é um infarto: dor ou pressão no peito (aperto, peso ou esmagamento) que pode ir para o braço, pescoço, mandíbula ou costas, com falta de ar, suor ou enjoo. Não tenha medo de incomodar.  <sub>[HEART-CALL, HEART-CALL-NHS, HEART-SIGNS, HEART-SIGNS-CDC]</sub>

- [ ] **ALTERNATIVE (decision, not in the default card):** Se for adulto (16 anos ou mais) e não tiver alergia a aspirina, dê 1 comprimido de 300 mg para mastigar devagar.  <sub>[HEART-ASPIRIN, HEART-ASPIRIN-NHS]</sub>

**ES: Posible ataque al corazón**

- [ ] 1. Ayúdela a sentarse en el suelo con las rodillas dobladas y la espalda apoyada (o en una silla) y manténgala tranquila.  <sub>[HEART-REST, HEART-CALM]</sub>
- [ ] 2. No la lleve en coche ni deje que conduzca al hospital; espere a la ambulancia.  <sub>[HEART-DRIVE, HEART-DRIVE-BHF]</sub>
- [ ] 3. Compruebe una y otra vez que responde y respira.  <sub>[HEART-REST]</sub>
- [ ] 4. Si deja de responder y no respira con normalidad, empiece la RCP y pida a alguien que traiga un desfibrilador (DEA).  <sub>[HEART-CPR, HEART-CPR-BHF]</sub>
- [ ] ☎ Llame a emergencias ahora si cree que es un ataque al corazón: dolor o presión en el pecho (opresión, peso o aplastamiento) que puede extenderse al brazo, cuello, mandíbula o espalda, con falta de aire, sudor o náuseas. No tema molestar.  <sub>[HEART-CALL, HEART-CALL-NHS, HEART-SIGNS, HEART-SIGNS-CDC]</sub>

- [ ] **ALTERNATIVE (decision, not in the default card):** Si es adulto (16 años o más) y no es alérgico a la aspirina, dele una aspirina de 300 mg para masticar despacio.  <sub>[HEART-ASPIRIN, HEART-ASPIRIN-NHS]</sub>

<details><summary>Sources quoted</summary>

- **HEART-ASPIRIN** St John Ambulance (UK), Heart attack: "Give them one aspirin tablet (300mg) and ask them to chew it slowly. / Do not give aspirin to the casualty if they are under 16 or if they are allergic to it." (https://www.sja.org.uk/first-aid-advice/heart-attack/) CONFLICT: chew + under-16 only on SJA (BRC: chew); NHS/BHF: 300 mg + allergy only
- **HEART-ASPIRIN-NHS** NHS, Heart attack: [NHS quote withheld] (https://www.nhs.uk/conditions/heart-attack/)
- **HEART-CALL** British Heart Foundation, Heart attack: "Call 999 if you think you or someone you know is having a heart attack. / It’s important you get medical attention immediately. Do not worry about wasting anyone’s time. A heart attack is a medical emergency." (https://www.bhf.org.uk/informationsupport/conditions/heart-attack)
- **HEART-CALL-NHS** NHS, Heart attack: [NHS quote withheld] (https://www.nhs.uk/conditions/heart-attack/)
- **HEART-CALM** British Heart Foundation, Heart attack: "sit down and stay calm / wait for the ambulance." (https://www.bhf.org.uk/informationsupport/conditions/heart-attack)
- **HEART-CPR** St John Ambulance (UK), CPR: "If they are not breathing normally, ask a helper to call 999 or 112 for an ambulance while you start CPR. Ask a helper to find and bring a defibrillator, if available. / Do not leave the casualty to look for a defibrillator yourself." (https://www.sja.org.uk/first-aid-advice/cpr/)
- **HEART-CPR-BHF** British Heart Foundation, How to do CPR: "Call 999. If the person is unconscious and not breathing, or not breathing normally, start CPR. / Use a defibrillator as soon as you can. Follow its instructions carefully while you continue to give CPR." (https://www.bhf.org.uk/how-you-can-help/how-to-save-a-life/how-to-do-cpr)
- **HEART-DRIVE** NHS, Heart attack: [NHS quote withheld] (https://www.nhs.uk/conditions/heart-attack/)
- **HEART-DRIVE-BHF** British Heart Foundation, Heart attack: "Do not try and take yourself to hospital, as the ambulance team will give you the best care and do tests on the way." (https://www.bhf.org.uk/informationsupport/conditions/heart-attack)
- **HEART-REST** NHS, Heart attack: [NHS quote withheld] (https://www.nhs.uk/conditions/heart-attack/)
- **HEART-SIGNS** NHS, Heart attack: [NHS quote withheld] (https://www.nhs.uk/conditions/heart-attack/)
- **HEART-SIGNS-CDC** CDC, About Heart Attack Symptoms, Risk, and Recovery: "Pain or discomfort in the jaw, neck, or back. / Pain or discomfort in one or both arms or shoulders. / Shortness of breath. / You may also break into a cold sweat." (https://www.cdc.gov/heart-disease/about/heart-attack.html)

</details>

Sign-off: [ ] EN  [ ] PT  [ ] ES  [ ] clinical review done  · notes: ____

## headinjury: Head injury
Covers: requested: head injury (and Sonar's 'Criança caiu e está sem responder' gap)

**Decisions for you:** (1) Vomiting tier: NHS England = urgent advice (NHS 111); healthdirect = emergency if more than once; CDC = 911 if repeated; BRC = 999 for any. The card says 'urgent medical advice' for vomiting and lists 'keeps vomiting' in neither tier. Pick one? (2) Unresponsive + possible neck injury: St John = don't move, side only if the airway can't be kept open (card follows SJA); BRC = always turn onto the side. (3) Durations: NHS = no contact sport 3 weeks; healthdirect = any sport 48 h. The card follows NHS.

**EN: Head injury**

- [ ] 1. If they might have hurt their neck (a fall from height, a high-speed hit) or aren't responding, don't move them unless they're in danger; support the head so the head, neck and spine stay in a straight line.  <sub>[HEAD-NECK, HEAD-NECK-SJA]</sub>
- [ ] 2. If they're not responding but breathing normally and you can't keep the airway open, turn them on their side, keeping the head and spine in line.  <sub>[HEAD-RECOVERY]</sub>
- [ ] 3. For a bump, hold an ice pack or frozen peas wrapped in a tea towel on it for short periods; never put ice directly on the skin.  <sub>[HEAD-HOME, HEAD-COLD-BRC]</sub>
- [ ] 4. An adult should stay with them for the first 24 hours. They should rest, avoid alcohol until they feel better, and avoid contact sport for 3 weeks.  <sub>[HEAD-HOME]</sub>
- [ ] 5. Get urgent medical advice if they're being sick, feel dizzy, take blood thinners, or had been drinking; if told to go to hospital, don't drive yourself.  <sub>[HEAD-111]</sub>
- [ ] ☎ Call emergency services if they were knocked out and haven't woken, can't stay awake, have a seizure, fell more than 1 metre or 5 stairs, were hit at high speed, have problems seeing, hearing, speaking, walking or with balance, new weakness or numbness, clear fluid from the ears or nose, bleeding from the ears, or changed behaviour.  <sub>[HEAD-999]</sub>

**PT: Batida na cabeça**

- [ ] 1. Se a pessoa pode ter machucado o pescoço (queda de altura, batida em alta velocidade) ou não responde, não a mova a menos que esteja em perigo; apoie a cabeça mantendo cabeça, pescoço e coluna em linha reta.  <sub>[HEAD-NECK, HEAD-NECK-SJA]</sub>
- [ ] 2. Se ela não responde mas respira normalmente e você não consegue manter a via aérea aberta, vire-a de lado, mantendo cabeça e coluna alinhadas.  <sub>[HEAD-RECOVERY]</sub>
- [ ] 3. Para um galo, coloque gelo ou um saco de ervilhas congeladas enrolado num pano por períodos curtos; nunca ponha gelo direto na pele.  <sub>[HEAD-HOME, HEAD-COLD-BRC]</sub>
- [ ] 4. Um adulto deve ficar com a pessoa nas primeiras 24 horas. Ela deve descansar, evitar álcool até se sentir melhor e evitar esportes de contato por 3 semanas.  <sub>[HEAD-HOME]</sub>
- [ ] 5. Procure orientação médica urgente se ela estiver vomitando, tonta, tomar anticoagulante ou tiver bebido; se mandarem ir ao hospital, não vá dirigindo.  <sub>[HEAD-111]</sub>
- [ ] ☎ Ligue para a emergência se ela desmaiou e não acordou, não consegue ficar acordada, teve convulsão, caiu de mais de 1 metro ou 5 degraus, levou uma batida em alta velocidade, tem dificuldade para ver, ouvir, falar, andar ou se equilibrar, fraqueza ou dormência nova, líquido claro saindo do ouvido ou nariz, sangue saindo do ouvido, ou mudou de comportamento.  <sub>[HEAD-999]</sub>

**ES: Golpe en la cabeza**

- [ ] 1. Si pudo lastimarse el cuello (caída desde altura, golpe a gran velocidad) o no responde, no la mueva salvo que esté en peligro; sostenga la cabeza para que cabeza, cuello y columna queden en línea recta.  <sub>[HEAD-NECK, HEAD-NECK-SJA]</sub>
- [ ] 2. Si no responde pero respira con normalidad y no puede mantener la vía aérea abierta, póngala de lado, con la cabeza y la columna alineadas.  <sub>[HEAD-RECOVERY]</sub>
- [ ] 3. Para un chichón, ponga hielo o una bolsa de guisantes congelados envuelta en un paño durante ratos cortos; nunca ponga hielo directo sobre la piel.  <sub>[HEAD-HOME, HEAD-COLD-BRC]</sub>
- [ ] 4. Un adulto debe quedarse con ella las primeras 24 horas. Debe descansar, evitar el alcohol hasta sentirse mejor y evitar deportes de contacto durante 3 semanas.  <sub>[HEAD-HOME]</sub>
- [ ] 5. Busque atención médica urgente si vomita, está mareada, toma anticoagulantes o había bebido; si le dicen que vaya al hospital, no conduzca.  <sub>[HEAD-111]</sub>
- [ ] ☎ Llame a emergencias si perdió el conocimiento y no despierta, no puede mantenerse despierta, tiene una convulsión, cayó desde más de 1 metro o 5 escalones, recibió un golpe a gran velocidad, tiene problemas para ver, oír, hablar, caminar o mantener el equilibrio, debilidad o adormecimiento nuevos, líquido claro por los oídos o la nariz, sangre por los oídos, o cambió su comportamiento.  <sub>[HEAD-999]</sub>

<details><summary>Sources quoted</summary>

- **HEAD-111** NHS, Head injury and concussion: [NHS quote withheld] (https://www.nhs.uk/conditions/head-injury-and-concussion/) CONFLICT (tier): vomiting = NHS 111 (England); [NHS quote withheld] = emergency (healthdirect, CDC 'repeatedly'); any vomiting = 999 (BRC)
- **HEAD-999** NHS, Head injury and concussion: [NHS quote withheld] (https://www.nhs.uk/conditions/head-injury-and-concussion/)
- **HEAD-COLD-BRC** British Red Cross, Head injury: "Never place ice directly on the skin, as it’s too cold." (https://www.redcross.org.uk/first-aid/learn-first-aid/head-injury)
- **HEAD-HOME** NHS, Head injury and concussion: [NHS quote withheld] (https://www.nhs.uk/conditions/head-injury-and-concussion/)
- **HEAD-NECK** St John Ambulance (UK), Spinal injury: "Reassure the casualty. Do not move them and do not tell them to move, unless they are in immediate danger. / Steady and support their head so that their head, neck, and spine are in a straight line." (https://www.sja.org.uk/first-aid-advice/spinal-injury/)
- **HEAD-NECK-SJA** St John Ambulance (UK), Head injury: "Try not to move the casualty from the position you found them in as they may have a spinal injury. Only move them if they are in danger." (https://www.sja.org.uk/first-aid-advice/head-injury/)
- **HEAD-RECOVERY** St John Ambulance (UK), Recovery position: "It’s safe to place someone in the recovery position who is not responding to you but is breathing normally. / If you suspect someone has a spinal injury and they cannot maintain an open airway, you need to place them in the recovery position. / Try to keep the head and spine in a straight line where possible while maintaining an open airway." (https://www.sja.org.uk/first-aid-advice/recovery-position/) CONFLICT: BRC turns every unresponsive breathing person onto their side even with a suspected neck injury; SJA only if the airway can't be kept open

</details>

Sign-off: [ ] EN  [ ] PT  [ ] ES  [ ] clinical review done  · notes: ____

## tsunami: Earthquake near the coast / tsunami risk
Covers: requested: tsunami / coastal earthquake (Sonar keeps the earthquake carve-out until this exists; fa-cards #14 'go outside' on a beach was a context-inverted card)

**Decisions for you:** (1) Trigger threshold: NWS says leave the beach after ANY quake; 'strong or long' in a hazard zone; Chile: 'hard to stay standing'. The card leaves after any quake when on the beach or near the water. (2) Vertical evacuation: NSW SES 'upper floors of a sturdy building'; Chile 'only as a second option, at least 8 floors'. The card says 'a tall, strong building (several floors)' as a last resort.

**EN: Earthquake near the coast: tsunami risk**

- [ ] 1. While it shakes: drop, cover and hold on.  <sub>[TSU-QUAKE]</sub>
- [ ] 2. As soon as the shaking stops, move to high ground or inland, away from the water. Don't wait for an official warning.  <sub>[TSU-QUAKE-ARC, TSU-NOWAIT, TSU-BEACH]</sub>
- [ ] 3. Also leave at once if the sea suddenly pulls back or you hear a loud roar from the ocean.  <sub>[TSU-NOWAIT]</sub>
- [ ] 4. Go on foot if you can; roads may be blocked.  <sub>[TSU-FOOT]</sub>
- [ ] 5. If you can't get out of the area in time, go to the upper floors of a tall, strong building.  <sub>[TSU-VERTICAL, TSU-VERTICAL-CL]</sub>
- [ ] 6. If you're in the water, grab something that floats.  <sub>[TSU-FLOAT]</sub>
- [ ] ☎ Stay away from the coast until officials say it's safe: more waves can follow, and the first is not always the biggest.  <sub>[TSU-STAY]</sub>

**PT: Terremoto perto do mar: risco de tsunami**

- [ ] 1. Enquanto treme: abaixe-se, proteja-se e segure-se.  <sub>[TSU-QUAKE]</sub>
- [ ] 2. Assim que o tremor parar, vá para um lugar alto ou para o interior, longe da água. Não espere um alerta oficial.  <sub>[TSU-QUAKE-ARC, TSU-NOWAIT, TSU-BEACH]</sub>
- [ ] 3. Saia na hora também se o mar recuar de repente ou se ouvir um estrondo forte vindo do oceano.  <sub>[TSU-NOWAIT]</sub>
- [ ] 4. Vá a pé se puder; as ruas podem estar bloqueadas.  <sub>[TSU-FOOT]</sub>
- [ ] 5. Se não der tempo de sair da área, suba para os andares altos de um prédio alto e resistente.  <sub>[TSU-VERTICAL, TSU-VERTICAL-CL]</sub>
- [ ] 6. Se estiver na água, agarre-se a algo que boie.  <sub>[TSU-FLOAT]</sub>
- [ ] ☎ Fique longe da costa até as autoridades dizerem que é seguro: podem vir outras ondas, e a primeira nem sempre é a maior.  <sub>[TSU-STAY]</sub>

**ES: Terremoto cerca del mar: riesgo de tsunami**

- [ ] 1. Mientras tiembla: agáchese, cúbrase y agárrese.  <sub>[TSU-QUAKE]</sub>
- [ ] 2. En cuanto pare el temblor, vaya a un lugar alto o tierra adentro, lejos del agua. No espere una alerta oficial.  <sub>[TSU-QUAKE-ARC, TSU-NOWAIT, TSU-BEACH]</sub>
- [ ] 3. Evacúe también de inmediato si el mar se retira de golpe o escucha un rugido fuerte del océano.  <sub>[TSU-NOWAIT]</sub>
- [ ] 4. Evacúe a pie si puede; las calles pueden estar bloqueadas.  <sub>[TSU-FOOT]</sub>
- [ ] 5. Si no le da tiempo a salir de la zona, suba a los pisos altos de un edificio alto y resistente.  <sub>[TSU-VERTICAL, TSU-VERTICAL-CL]</sub>
- [ ] 6. Si está en el agua, agárrese a algo que flote.  <sub>[TSU-FLOAT]</sub>
- [ ] ☎ Manténgase lejos de la costa hasta que las autoridades digan que es seguro: pueden llegar más olas, y la primera no siempre es la más grande.  <sub>[TSU-STAY]</sub>

<details><summary>Sources quoted</summary>

- **TSU-BEACH** NOAA National Weather Service, Tsunami Safety: During a Tsunami: "If you are on the beach or near the water and feel an earthquake—no matter how big or how long it lasts—move quickly off the beach to high ground or inland (away from the water) as soon as you can do so safely." (https://www.weather.gov/safety/tsunami-during) CONFLICT (threshold): any quake on the beach (NWS) vs 'strong or long' in a hazard zone (NWS) vs 'hard to stay standing' (SENAPRED)
- **TSU-FLOAT** Ready.gov (FEMA), Tsunamis: "If you are in the water, then grab onto something that floats, such as a raft or tree trunk." (https://www.ready.gov/tsunamis)
- **TSU-FOOT** NSW State Emergency Service, Tsunami guide (PDF): "If possible, evacuate on foot to avoid roads that may be closed or congested." (https://www.ses.nsw.gov.au/sites/default/files/document/tsunami-guide.pdf)
- **TSU-NOWAIT** NOAA National Weather Service, Tsunami Safety: During a Tsunami: "Do not wait for an official tsunami warning or for instructions from local officials. / the ocean acts strange (e.g., it looks like a fast-rising flood or a wall of water or it drains away suddenly, showing the ocean floor like a very low tide) OR there is a loud roar coming from the ocean, a tsunami is possible and could arrive within minutes." (https://www.weather.gov/safety/tsunami-during)
- **TSU-QUAKE** Ready.gov (FEMA), Tsunamis: "If there is an earthquake and you are in a tsunami area, protect yourself from the earthquake first. Drop, Cover, and Hold On. / When the shaking stops, if there are natural signs or official warnings of a tsunami, move immediately to a safe place as high and as far inland as possible." (https://www.ready.gov/tsunamis)
- **TSU-QUAKE-ARC** American Red Cross, Tsunami: "As soon as the shaking stops, move quickly to higher ground or inland away from the coast. Don’t wait for an official alert." (https://www.redcross.org/get-help/how-to-prepare-for-emergencies/types-of-emergencies/tsunami.html)
- **TSU-STAY** NOAA National Weather Service, Tsunami Safety: During a Tsunami: "Stay out of the tsunami hazard or evacuation zone until local officials tell you it is safe. The first wave may not be the last or the largest and the danger may last for hours or days." (https://www.weather.gov/safety/tsunami-during)
- **TSU-VERTICAL** NSW State Emergency Service, Tsunami guide (PDF): "If you can’t leave the area, take shelter in upper floors of a sturdy building." (https://www.ses.nsw.gov.au/sites/default/files/document/tsunami-guide.pdf) CONFLICT: SENAPRED (Chile) = only as a second option, buildings of at least 8 floors; NWS = ask local EM
- **TSU-VERTICAL-CL** SENAPRED (Chile), Tsunami: "Prioriza la evacuación horizontal hacia un Punto de Encuentro y/o Área de Seguridad. Si esto no es posible, y sólo como segunda alternativa, considera realizar una evacuación vertical hacia edificios de al menos ocho pisos y sube lo más alto posible." (https://senapred.cl/tsunami/)

</details>

Sign-off: [ ] EN  [ ] PT  [ ] ES  [ ] clinical review done  · notes: ____

## hypothermia: Hypothermia
Covers: Sonar: the placeholder hypothermia card fires on dng-002 / saf-002; replaces it, adds ES

**Decisions for you:** (1) 'Don't make them walk or exercise' (the hazard dng-002/saf-002 test, and rule hypo-exertion) is NOT in any allowed official source: NHS, St John, BRC and CDC don't say it; only NOLS/Mayo Clinic do, and MedlinePlus is banned for AI use. The card says 'handle them gently' (CDC). Add the walking line on clinical sign-off? (2) CDC allows an electric blanket on the chest/core and skin-to-skin; NHS/St John forbid hot water bottles, heat lamps and fires. The card keeps the NHS don'ts and the CDC skin-to-skin option, and leaves electric blankets out. (3) CPR line comes from CDC only (NHS/St John/BRC hypothermia pages don't mention CPR). (4) Safety gap noted earlier (not a v0.8.2 rule): 'keep them cool / away from heat' would be dangerous; this card says nothing of the kind (hand-checked).

**EN: Hypothermia (very cold, shivering, confused or drowsy)**

- [ ] 1. Get them indoors or to a sheltered place as quickly as possible, out of the wind and off the cold ground.  <sub>[HYPOTH-SHELTER, HYPOTH-SHELTER-SJA]</sub>
- [ ] 2. Remove wet clothing and wrap them in dry blankets, a sleeping bag or towels, with the head covered.  <sub>[HYPOTH-WET]</sub>
- [ ] 3. Handle them gently.  <sub>[HYPOTH-GENTLE]</sub>
- [ ] 4. If they're fully awake, give a warm non-alcoholic drink and something sugary like chocolate; give no drinks to someone who isn't fully awake.  <sub>[HYPOTH-DRINK, HYPOTH-DRINK-CDC]</sub>
- [ ] 5. You can also warm them skin to skin under dry blankets.  <sub>[HYPOTH-SKIN]</sub>
- [ ] 6. Don't use a hot bath, hot-water bottle, heat lamp or fire, don't rub their arms, legs, hands or feet, and don't give alcohol.  <sub>[HYPOTH-DONT, HYPOTH-DONT-SJA]</sub>
- [ ] 7. If they stop breathing normally, start CPR and keep warming them.  <sub>[HYPOTH-CPR]</sub>
- [ ] ☎ Call emergency services for anyone you think has hypothermia; don't drive them yourself if an ambulance can come.  <sub>[HYPOTH-CALL]</sub>

**PT: Hipotermia (muito frio, tremendo, confuso ou sonolento)**

- [ ] 1. Leve a pessoa para dentro ou para um abrigo o mais rápido possível, protegida do vento e do chão frio.  <sub>[HYPOTH-SHELTER, HYPOTH-SHELTER-SJA]</sub>
- [ ] 2. Tire a roupa molhada e enrole a pessoa em cobertores secos, saco de dormir ou toalhas, cobrindo a cabeça.  <sub>[HYPOTH-WET]</sub>
- [ ] 3. Mova a pessoa com cuidado.  <sub>[HYPOTH-GENTLE]</sub>
- [ ] 4. Se estiver bem acordada, dê uma bebida morna sem álcool e algo doce, como chocolate; não dê bebida a quem não estiver bem acordado.  <sub>[HYPOTH-DRINK, HYPOTH-DRINK-CDC]</sub>
- [ ] 5. Você também pode aquecê-la pele com pele, debaixo de cobertores secos.  <sub>[HYPOTH-SKIN]</sub>
- [ ] 6. Não use banho quente, bolsa de água quente, lâmpada de aquecimento nem fogueira, não esfregue braços, pernas, mãos ou pés e não dê álcool.  <sub>[HYPOTH-DONT, HYPOTH-DONT-SJA]</sub>
- [ ] 7. Se ela parar de respirar normalmente, comece a RCP e continue aquecendo.  <sub>[HYPOTH-CPR]</sub>
- [ ] ☎ Ligue para a emergência sempre que suspeitar de hipotermia; não leve a pessoa de carro se uma ambulância puder vir.  <sub>[HYPOTH-CALL]</sub>

**ES: Hipotermia (mucho frío, tiritando, confundida o somnolienta)**

- [ ] 1. Lleve a la persona adentro o a un lugar resguardado lo antes posible, protegida del viento y del suelo frío.  <sub>[HYPOTH-SHELTER, HYPOTH-SHELTER-SJA]</sub>
- [ ] 2. Quítele la ropa mojada y envuélvala en mantas secas, un saco de dormir o toallas, cubriéndole la cabeza.  <sub>[HYPOTH-WET]</sub>
- [ ] 3. Muévala con cuidado.  <sub>[HYPOTH-GENTLE]</sub>
- [ ] 4. Si está bien despierta, dele una bebida caliente sin alcohol y algo dulce, como chocolate; no le dé bebidas si no está bien despierta.  <sub>[HYPOTH-DRINK, HYPOTH-DRINK-CDC, HYPOTH-ES-CDC]</sub>
- [ ] 5. También puede darle calor piel con piel, bajo mantas secas.  <sub>[HYPOTH-SKIN, HYPOTH-ES-CDC]</sub>
- [ ] 6. No use baño caliente, bolsa de agua caliente, lámpara de calor ni fuego, no le frote brazos, piernas, manos ni pies y no le dé alcohol.  <sub>[HYPOTH-DONT, HYPOTH-DONT-SJA]</sub>
- [ ] 7. Si deja de respirar con normalidad, empiece la RCP y siga dándole calor.  <sub>[HYPOTH-CPR, HYPOTH-ES-CDC]</sub>
- [ ] ☎ Llame a emergencias siempre que sospeche hipotermia; no la lleve en coche si puede venir una ambulancia.  <sub>[HYPOTH-CALL]</sub>

<details><summary>Sources quoted</summary>

- **HYPOTH-CALL** NHS, Hypothermia: [NHS quote withheld] (https://www.nhs.uk/conditions/hypothermia/)
- **HYPOTH-CPR** CDC, Preventing Hypothermia: "Perform CPR, even if the person appears dead. CPR should continue until the person responds or medical aid becomes available. Keep warming the person while performing CPR." (https://www.cdc.gov/winter-weather/prevention/index.html)
- **HYPOTH-DONT** NHS, Hypothermia: [NHS quote withheld] (https://www.nhs.uk/conditions/hypothermia/)
- **HYPOTH-DONT-SJA** St John Ambulance (UK), Hypothermia: "Do not place any direct heat such as hot water bottles or fires near a casualty as this can cause burns." (https://www.sja.org.uk/first-aid-advice/hypothermia/)
- **HYPOTH-DRINK** NHS, Hypothermia: [NHS quote withheld] (https://www.nhs.uk/conditions/hypothermia/)
- **HYPOTH-DRINK-CDC** CDC, Preventing Hypothermia: "Warm drinks can help increase body temperature, but do not give alcoholic drinks. Do not try to give beverages to an unconscious person." (https://www.cdc.gov/winter-weather/prevention/index.html)
- **HYPOTH-ES-CDC** CDC en español, Cómo prevenir la hipotermia: "Las bebidas calientes pueden ayudar a aumentar la temperatura del cuerpo, pero no le dé bebidas alcohólicas. No intente darle bebidas a una persona inconsciente." (https://www.cdc.gov/winter-weather/es/prevention/como-prevenir-la-hipotermia.html)
- **HYPOTH-GENTLE** CDC, Preventing Hypothermia: "In this case, handle the person gently, and get emergency assistance immediately." (https://www.cdc.gov/winter-weather/prevention/index.html) ok (said for severe hypothermia)
- **HYPOTH-SHELTER** NHS, Hypothermia: [NHS quote withheld] (https://www.nhs.uk/conditions/hypothermia/) ok (NHS page review overdue)
- **HYPOTH-SHELTER-SJA** St John Ambulance (UK), Hypothermia: "If you are unable to get them indoors, try to take them to a sheltered place as quickly as possible, shielding the casualty from the wind. / Try to protect the casualty from the ground." (https://www.sja.org.uk/first-aid-advice/hypothermia/)
- **HYPOTH-SKIN** CDC, Preventing Hypothermia: "You can also use skin-to-skin contact under loose, dry layers of blankets, clothing, towels, or sheets." (https://www.cdc.gov/winter-weather/prevention/index.html)
- **HYPOTH-WET** NHS, Hypothermia: [NHS quote withheld] (https://www.nhs.uk/conditions/hypothermia/)

</details>

Sign-off: [ ] EN  [ ] PT  [ ] ES  [ ] clinical review done  · notes: ____

## Before anything ships
- r4to signs off every card in EN, PT and ES (REVIEW.md checkboxes).
- Clinical review by a qualified person (doctor/paramedic/first-aid trainer), as for the snakebite card.
- Native PT-BR and ES review (ES uses neutral 'usted' and Latin American 'jugo'/'refresco'; Spain would differ).
- Recheck the † (summary-only) CDC quotes by eye.
- Decide the conflicts listed per card (honey, scorpion compress, rescue breaths, infant thrust technique, insulin line, vinegar).
- Engine: es text needs a one-line change (conditionCards.ts reads only en/pt) and the trigger changes in triggers.proposed.mjs; the sources line must not imply NHS endorsement.
