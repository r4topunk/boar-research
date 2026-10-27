# First-aid cards round 5: review sheet for r4to (first-aid-cards draft 2026-10-03, DRAFT, NOT FOR SHIPPING)

TL;DR: DRAFT, NOT FOR SHIPPING. Round 1: 10 cards; round 2: 4 cards (heart attack, head injury, tsunami, hypothermia); round 3: 6 cards (burn, frostbite, heatstroke, nosebleed, earthquake, animal bite); round 4: 9 cards (bleeding, stroke, anaphylaxis, chemical in the eye, electric shock, altitude, sea-creature puncture, tick, heat exhaustion); round 5: 2 cards (rip current, scorpion sting in an adult); all EN/PT/ES, every step cited to a verbatim quote from an official source (SOURCES.md). It needs r4to's sign-off on the wording, a clinical review, and native-speaker reviews (PT-BR, ES) before anything ships.

How to review: for each card, read the EN steps against the quotes below them, then PT and ES. Tick a box only if you accept the wording as is; write any change next to it. **Nothing ships without your sign-off** (and the clinical + native-speaker reviews listed at the end).

Automatic checks (check_cards.py): citations on every step = PASS; safety rules v0.8.7 = PASS (0 unsafe in all 93 card-language texts, all rounds).

## ripcurrent: Caught in a rip current (still in the water)
Covers: card-mismatch dev pairs ed-es-048, ed-en-092, ed-pt-092 (an active rip current got the post-rescue drowning card; ed-en-051 is a post-rescue pool item, so the drowning card is right there)

**Decisions for you:** (1) Order: NOAA says float first and swim parallel only 'if you're a good swimmer'; NWS lists 'swim out of the current' before 'float or tread water'. The card says calm + float first, then swim parallel 'if you can swim'. (2) After escaping: NWS/NOS 'at an angle toward the beach'; NOAA Ocean Today 'swim with the waves'. The card says 'at an angle back toward the beach'. (3) CPR line: the card only says 'once they're out, if not breathing normally, start CPR' (cited to the drowning card's British Red Cross row); the steps are on the drowning card. No rip-current page has a CPR line. (4) PT call line names Bombeiros 193 (Brazil's water-rescue service) + SAMU 192. The only fetched official quote with 193 is the Ministério da Saúde scorpion page's general emergency line; Brazilian state fire-department rip pages were 403/JS-only. Keep 193? (5) RNLI, USLA and Surf Life Saving Australia pages could not be fetched (403/404); the card rests on NOAA/NWS only (US public domain).

**EN: Caught in a rip current (still in the water)**

- [ ] 1. If you're caught: stay calm and float. The current pulls you away from shore, not under. Don't swim against the current.  <sub>[RIP-CALM, RIP-OPTIONS]</sub>
- [ ] 2. If you can swim, swim parallel to the shore until you're out of the pull, then swim at an angle back toward the beach.  <sub>[RIP-PARALLEL, RIP-ANGLE, RIP-BRO]</sub>
- [ ] 3. If you can't get out, keep floating or tread water, and wave and yell for help.  <sub>[RIP-OPTIONS, RIP-WAVE, RIP-BRO]</sub>
- [ ] 4. If someone else is caught: get a lifeguard; if there is none, call emergency services. Don't swim out to rescue them yourself.  <sub>[RIP-911, RIP-OTHER, RIP-BRO]</sub>
- [ ] 5. Throw them something that floats (a life jacket, float or cooler) and shout to them to stay calm and swim parallel to the shore.  <sub>[RIP-911, RIP-BRO]</sub>
- [ ] ☎ Call a lifeguard or emergency services now if anyone can't get back to shore. Once they're out of the water, if they aren't breathing normally, start CPR.  <sub>[RIP-911, DROWN-2b]</sub>

**PT: Preso numa corrente de retorno (ainda na água)**

- [ ] 1. Se você for pego: mantenha a calma e flutue. A corrente puxa para longe da praia, não para o fundo. Não nade contra a corrente.  <sub>[RIP-CALM, RIP-OPTIONS]</sub>
- [ ] 2. Se souber nadar, nade paralelo à praia até sair da correnteza; depois nade em diagonal de volta para a areia.  <sub>[RIP-PARALLEL, RIP-ANGLE, RIP-BRO]</sub>
- [ ] 3. Se não conseguir sair, continue flutuando ou mantenha-se à tona, e acene e grite por ajuda.  <sub>[RIP-OPTIONS, RIP-WAVE, RIP-BRO]</sub>
- [ ] 4. Se outra pessoa for pega: chame o guarda-vidas; se não houver, ligue para a emergência. Não entre na água para resgatá-la sozinho.  <sub>[RIP-911, RIP-OTHER, RIP-BRO]</sub>
- [ ] 5. Jogue algo que flutue (colete salva-vidas, boia ou caixa de isopor) e grite para ela manter a calma e nadar paralelo à praia.  <sub>[RIP-911, RIP-BRO]</sub>
- [ ] ☎ Chame o guarda-vidas ou ligue para a emergência (Bombeiros 193 ou SAMU 192) agora se alguém não conseguir voltar. Quando a pessoa sair da água, se não respirar normalmente, comece a RCP.  <sub>[RIP-911, SCORP-CHILD-1, DROWN-2b]</sub>

**ES: Atrapado en una corriente de resaca (aún en el agua)**

- [ ] 1. Si queda atrapado: mantenga la calma y flote. La corriente lo aleja de la orilla, no lo hunde. No nade contra la corriente.  <sub>[RIP-ES, RIP-CALM, RIP-OPTIONS]</sub>
- [ ] 2. Si sabe nadar, nade de lado, paralelo a la orilla, hasta salir de la corriente; después nade en ángulo de regreso a la orilla.  <sub>[RIP-ES, RIP-PARALLEL, RIP-ANGLE]</sub>
- [ ] 3. Si no puede salir, siga flotando o manténgase a flote, y mueva los brazos y grite pidiendo ayuda.  <sub>[RIP-ES, RIP-OPTIONS]</sub>
- [ ] 4. Si otra persona está atrapada: busque a un salvavidas; si no hay, llame a emergencias. No entre al agua a rescatarla usted mismo.  <sub>[RIP-ES, RIP-911, RIP-OTHER]</sub>
- [ ] 5. Láncele algo que flote (un chaleco salvavidas, un flotador o una hielera) y grítele que mantenga la calma y nade paralelo a la orilla.  <sub>[RIP-ES, RIP-BRO]</sub>
- [ ] ☎ Llame a un salvavidas o a emergencias ahora si alguien no puede volver a la orilla. Cuando salga del agua, si no respira con normalidad, empiece la RCP.  <sub>[RIP-ES, RIP-911, DROWN-2b]</sub>

<details><summary>Sources quoted</summary>

- **DROWN-2b** British Red Cross, Drowning first aid: "Step 4. Give five rescue breaths / Step 5. Give 30 chest compressions by pushing firmly in the middle of their chest up and down. / If you are on your own, call 999 after you’ve spent one minute giving them rescue breaths and chest compressions." (https://www.redcross.org.uk/first-aid/learn-first-aid/drowning)
- **RIP-911** NOAA National Weather Service, Social Media: Rip Currents: "Get help from a lifeguard. If there is no lifeguard, call 9-1-1. Advise the person to swim following the shoreline to escape the current. If possible, throw the person something that floats. Never enter the water without a floatation device. Many people have died trying to rescue someone caught in a rip current." (https://www.weather.gov/wrn/rip-currents-sm)
- **RIP-ANGLE** NOAA National Weather Service, Social Media: Rip Currents: "Stay calm and don't swim against the current. Swim in a direction following the shoreline, then at an angle toward the beach. If you need help, call or wave for assistance." (https://www.weather.gov/wrn/rip-currents-sm) ok (NOAA NOS agrees: 'swim back to land at an angle')
- **RIP-BRO** NOAA NWS Brownsville/Rio Grande Valley, Rip Current Avoidance and Escape Guidelines: "A good method for escaping the rip current is to swim parallel to the beach. / If you are unable to escape the current, do not panic. Stay calm, and float or calmly tread water even as the current moves you farther away from shore. / Seek immediate assistance from the beach patrol. If they are not available...call 9–1–1. Find something that can help the rip current victim stay afloat, such as a life jacket, inflatable object, or cooler, and throw it to them. Shout out instructions on how to escape, making sure to tell them to remain calm and not fight against the current. Many people drown while trying to save someone else from a rip current. Do not let that happen to you." (https://www.weather.gov/bro/ripcurrentescape)
- **RIP-CALM** NOAA Ocean Today, Break the Grip of the Rip (video transcript): "If you do happen to be caught in a rip current, stay calm. It won't pull you under - it'll just pull you away from shore. If you try to fight the rip current and swim against it, you'll just get worn out. Instead - float!" (https://oceantoday.noaa.gov/ripcurrent/)
- **RIP-ES** NOAA Ocean Today, Break the Grip of the Rip (transcripción en español): "Mantenga la calma, no luche contra la corriente. / Nade lateralmente fuera de la corriente y paralelo a la orilla, después en ángulo de regreso a la orilla. / Flote y manténgase en calma en el agua. La corriente de resaca eventualmente se desvanecerá. / Trate de ver hacia la costa, mueva los brazos y grite pidiendo ayuda. / NO TRATE de rescatarla usted mismo, en su lugar busque a una persona salvavidas o llame a emergencias. / Grítele instrucciones. / Y si es posible, láncele un salvavidas o dispositivo de flotación." (https://oceantoday.noaa.gov/ripcurrent/)
- **RIP-OPTIONS** NOAA National Weather Service, Social Media: Rip Currents: "If caught in a rip current: 1) Relax, rip currents don't pull you under. 2) Don't swim against the current. 3) Swim out of the current, then to shore. 4) If you can't escape, float or tread water. 5) If you need help, yell or wave for assistance." (https://www.weather.gov/wrn/rip-currents-sm)
- **RIP-OTHER** NOAA Ocean Today, Break the Grip of the Rip (video transcript): "If you're on shore and see someone in trouble in a rip current call for help! If a lifeguard is not available, throw in something that floats or extend a reaching object, but don't try to be a hero and make the rescue yourself. Even trained lifeguards only attempt a rescue using a flotation device." (https://oceantoday.noaa.gov/ripcurrent/)
- **RIP-PARALLEL** NOAA Ocean Today, Break the Grip of the Rip (video transcript): "If you're a good swimmer, swim parallel to shore until you've cleared the pull of the rip current. Swim with the waves, allowing them to push you to shore." (https://oceantoday.noaa.gov/ripcurrent/) CONFLICT (nuance): NOAA 'swim with the waves' vs NWS 'then at an angle toward the beach'
- **RIP-WAVE** NOAA Ocean Today, Break the Grip of the Rip (video transcript): "If you can, wave and yell to get the attention of lifeguards and people on shore to let them know you need help." (https://oceantoday.noaa.gov/ripcurrent/)
- **SCORP-CHILD-1** Ministério da Saúde (BR), Acidentes por Escorpiões: "Crianças constituem o grupo mais suscetível ao envenenamento sistêmico grave. / Em caso de emergência, contate imediatamente o Serviço de Atendimento Móvel de Urgência (SAMU 192) ou o Corpo de Bombeiros (193)." (https://www.gov.br/saude/pt-br/assuntos/saude-de-a-a-z/a/animais-peconhentos/acidentes-por-escorpioes)

</details>

Sign-off: [ ] EN  [ ] PT  [ ] ES  [ ] clinical review done  · notes: ____

## scorpionadult: Scorpion sting in an adult
Covers: card-mismatch dev pairs ed-es-045, ed-en-018 (an adult sting got the child-emergency card); the child card `scorpion` is unchanged

**Decisions for you:** (1) Cold vs warm (as on the child card): CDC/NIOSH and MedlinePlus say ice wrapped in a cloth (10 min on/10 off, never immerse in ice water); Brazil SES-SP says a WARM compress and 'no ice or cold water, it makes the pain worse'. The default card has neither; the ice line is an ALTERNATIVE below. Add it (EN/ES only?), or keep it out? (2) When to go: Brazil (SES-SP, Ministério da Saúde) and Mexico (Morelos, Guanajuato) send EVERY sting to the nearest health service quickly; MedlinePlus (US): 'most stings from North American scorpions do not need treatment'. The card follows Brazil/Mexico (stricter; dangerous Tityus/Centruroides species there). (3) Higher-risk groups: older adults and people with other illnesses (Morelos, Guanajuato, CONAPRA 911 list), plus children (child card). 'Allergic reaction' signs (lip/throat swelling, trouble breathing) are on CONAPRA's 911 list, so they are in the call line. (4) 'Keep the limb still' now has a source (MedlinePlus EN/ES); the child card still lacks it ('keep calm' only). Add it to the child card in a later round? (5) No dosing, no antihistamine (MedlinePlus mentions diphenhydramine: left out), no antivenom advice. Mexico's 'no ice' (Michoacán) could not be fetched; CONAPRA's 'no frío local' is in its SNAKEBITE box, not used here.

**EN: Scorpion sting (adult)**

- [ ] 1. Stay calm, move away from the scorpion, and keep the stung arm or leg as still as you can.  <sub>[SCORP-4, SCORPA-CDC, SCORPA-CARE]</sub>
- [ ] 2. Wash the sting with soap and water, and take off rings or anything tight near it.  <sub>[SCORP-2, SCORPA-CARE]</sub>
- [ ] 3. Don't cut, squeeze or suck the sting, and don't use a tourniquet. Don't put home remedies on it (alcohol, kerosene, coffee grounds, herbs).  <sub>[SCORP-5, SCORPA-NOSUBST-BR]</sub>
- [ ] 4. Go to the nearest health service (urgent care or hospital) as soon as possible; don't wait for other symptoms.  <sub>[SCORPA-ADULT-BR, SCORP-2, SCORPA-RISK-MX]</sub>
- [ ] 5. Older adults, people with other illnesses and children get the most serious poisoning: for them, go straight to hospital. A stung child is an emergency.  <sub>[SCORPA-RISK-MX, SCORPA-GTO, SCORPA-911-MX, SCORP-CHILD-1]</sub>
- [ ] ☎ Call emergency services now if they have trouble breathing, swelling of the lips or throat, drooling, muscle spasms or jerking movements, heavy sweating or vomiting, a racing heartbeat, or feel faint or confused.  <sub>[SCORPA-911-MX, SCORPA-SEVERE, SCORPA-SIGNS-BR]</sub>

- [ ] **ALTERNATIVE (decision, not in the default card):** For pain, put ice wrapped in a cloth on the sting, 10 minutes on and 10 minutes off; don't put the limb in ice water.  <sub>[SCORPA-CDC, SCORPA-ICE]</sub>

**PT: Picada de escorpião (adulto)**

- [ ] 1. Mantenha a calma, afaste-se do escorpião e deixe o braço ou a perna picada o mais parado possível.  <sub>[SCORP-4, SCORPA-CARE]</sub>
- [ ] 2. Lave o local com água e sabão e tire anéis ou o que estiver apertado perto da picada.  <sub>[SCORP-2, SCORPA-CARE]</sub>
- [ ] 3. Não corte, não esprema, não chupe o local e não faça torniquete. Não passe nada no local (álcool, querosene, pó de café, ervas).  <sub>[SCORP-5, SCORPA-NOSUBST-BR]</sub>
- [ ] 4. Procure o serviço de saúde mais próximo (pronto atendimento, pronto-socorro ou hospital) o mais rápido possível; não espere aparecerem outros sintomas.  <sub>[SCORPA-ADULT-BR, SCORP-2]</sub>
- [ ] 5. Idosos, pessoas com outras doenças e crianças têm o envenenamento mais grave: nesses casos, vá direto ao hospital. Criança picada é emergência.  <sub>[SCORPA-RISK-MX, SCORPA-GTO, SCORP-CHILD-1]</sub>
- [ ] ☎ Ligue para a emergência (SAMU 192) agora se houver falta de ar, inchaço nos lábios ou na garganta, salivação excessiva (babando), tremores ou espasmos musculares, suor intenso ou vômitos, coração disparado, ou sensação de desmaio ou confusão.  <sub>[SCORPA-911-MX, SCORPA-SEVERE, SCORPA-SIGNS-BR, SCORP-CHILD-1]</sub>

- [ ] **ALTERNATIVE (decision, not in the default card):** Para a dor, ponha gelo enrolado num pano sobre a picada, 10 minutos sim e 10 minutos não; não mergulhe o membro em água gelada.  <sub>[SCORPA-CDC, SCORPA-ICE]</sub>

**ES: Picadura de alacrán (adulto)**

- [ ] 1. Mantenga la calma, aléjese del alacrán y mantenga el brazo o la pierna picada lo más quieta posible.  <sub>[SCORP-4, SCORPA-CARE-ES]</sub>
- [ ] 2. Lave la picadura con agua y jabón, y quite anillos o cualquier cosa ajustada cerca de ella.  <sub>[SCORPA-CARE-ES]</sub>
- [ ] 3. No corte, no apriete ni chupe la picadura, y no use torniquete. No ponga remedios caseros (alcohol, queroseno, café, hierbas).  <sub>[SCORP-5, SCORPA-NOSUBST-BR, SCORPA-GTO]</sub>
- [ ] 4. Vaya al centro de salud más cercano lo antes posible; no espere a que aparezcan otros síntomas.  <sub>[SCORPA-RISK-MX, SCORPA-GTO, SCORPA-ADULT-BR]</sub>
- [ ] 5. Las personas mayores, las que tienen otras enfermedades y los niños sufren el envenenamiento más grave: en esos casos, vaya directo al hospital. Un niño picado es una emergencia.  <sub>[SCORPA-RISK-MX, SCORPA-GTO, SCORPA-911-MX]</sub>
- [ ] ☎ Llame a emergencias ahora si tiene dificultad para respirar, hinchazón de labios o garganta, babeo, espasmos o movimientos bruscos de los músculos, mucho sudor o vómitos, el corazón muy acelerado, o si la persona se siente a punto de desmayarse o está confundida.  <sub>[SCORPA-911-MX, SCORPA-SEVERE, SCORPA-SIGNS-BR]</sub>

- [ ] **ALTERNATIVE (decision, not in the default card):** Para el dolor, ponga hielo envuelto en un paño sobre la picadura, 10 minutos sí y 10 minutos no; no meta el brazo o la pierna en agua helada.  <sub>[SCORPA-CDC, SCORPA-ICE]</sub>

<details><summary>Sources quoted</summary>

- **SCORP-2** Ministério da Saúde (BR), Perguntas Frequentes, Acidentes por Escorpiões: "Deve-se limpar o local com água e sabão e a vítima deve então ser encaminhada, sem demora, para o ponto de atendimento médico de referência da região." (https://www.gov.br/saude/pt-br/assuntos/saude-de-a-a-z/a/animais-peconhentos/acidentes-por-escorpioes/faq/faq)
- **SCORP-4** Ministério da Saúde (BR), Perguntas Frequentes, Acidentes por Escorpiões: "A primeira coisa a ser feita é acalmar a pessoa e afastá-la do escorpião causador do acidente." (https://www.gov.br/saude/pt-br/assuntos/saude-de-a-a-z/a/animais-peconhentos/acidentes-por-escorpioes/faq/faq)
- **SCORP-5** Secretaria de Estado da Saúde de São Paulo (CVE), Acidentes com escorpiões (alerta à população): "Não fazer torni quete ou garrote, não furar, não cortar, não queimar, não espremer o local da picada; / Não fazer sucção no local da ferida;" (https://www.saude.sp.gov.br/resources/cve-centro-de-vigilancia-epidemiologica/areas-de-vigilancia/doencas-de-transmissao-por-vetores-e-zoonoses/escorpiao-evento/alerta23_populacao_escorpiao.pdf) ok ('torni quete' = PDF text split)
- **SCORP-CHILD-1** Ministério da Saúde (BR), Acidentes por Escorpiões: "Crianças constituem o grupo mais suscetível ao envenenamento sistêmico grave. / Em caso de emergência, contate imediatamente o Serviço de Atendimento Móvel de Urgência (SAMU 192) ou o Corpo de Bombeiros (193)." (https://www.gov.br/saude/pt-br/assuntos/saude-de-a-a-z/a/animais-peconhentos/acidentes-por-escorpioes)
- **SCORPA-911-MX** Secretaría de Salud (MX), STCONAPRA, Lesiones por fauna nociva (infographic): "La persona debe ser llevada al centro de salud más cercano o llamar al 911 si observa: / Dificultad para respirar / Hinchazón en labios, párpados o garganta / Mareos, sensación de desmayo o desorientación / Latidos del corazón rápidos / Una picadura de alacrán en niñas y niños o personas adultas mayores" (https://www.gob.mx/cms/uploads/attachment/file/732476/LesionesFaunaNociva_compressed.pdf) ok (PDF infographic; 'Dificultad' is printed with an fi ligature)
- **SCORPA-ADULT-BR** Secretaria de Estado da Saúde de São Paulo (CVE), Acidentes com escorpiões (alerta à população): "Para os demais pacientes: Deve-se procurar o mais rapidamente possível o serviço de saúde mais próximo, preferencialmente um pronto atendimento, pronto socorro ou hospital." (https://www.saude.sp.gov.br/resources/cve-centro-de-vigilancia-epidemiologica/areas-de-vigilancia/doencas-de-transmissao-por-vetores-e-zoonoses/escorpiao-evento/alerta23_populacao_escorpiao.pdf)
- **SCORPA-CARE** MedlinePlus (US National Library of Medicine), Scorpion sting: "Clean the area thoroughly with soap and water. / Keep the affected area still, if possible, to prevent the venom from spreading. / Loosen clothing and remove rings and other tight jewelry." (https://medlineplus.gov/ency/article/002850.htm) ok (A.D.A.M. content: facts only)
- **SCORPA-CARE-ES** MedlinePlus en español (NLM), Picadura de escorpión: "Lave muy bien el área con agua y jabón. / Mantenga a la persona y la zona de la picadura inmóvil, si es posible, para evitar que el veneno se extienda. / Afloje la ropa y quite los anillos y demás joyería ajustada." (https://medlineplus.gov/spanish/ency/article/002850.htm) ok (A.D.A.M. content: facts only)
- **SCORPA-CDC** CDC/NIOSH, Insects and Scorpions at Work: "If a worker is stung by a scorpion: / Contact a qualified health care provider or poison control center. / Apply ice, but do not submerge the affected area in ice water. / Remain relaxed and calm. / Do not take any sedatives." (https://www.cdc.gov/niosh/outdoor-workers/about/insects-and-scorpions.html) CONFLICT: ice (CDC, MedlinePlus) vs warm compress and NO ice (Brazil SES-SP)
- **SCORPA-GTO** Secretaría de Salud de Guanajuato (MX), Programa Picadura de alacrán: "su veneno es muy tóxico y quienes tienen mayor riesgo son los niños y los adultos mayores. / Salivación y sed intensa / lo más importante es que no utilices ningún remedio casero, acude de inmediato a tu centro de salud" (https://salud.guanajuato.gob.mx/programas/picadura-de-alacran)
- **SCORPA-ICE** MedlinePlus (US National Library of Medicine), Scorpion sting: "Place ice (wrapped in a clean cloth) on the site of the sting for 10 minutes and then off for 10 minutes. Repeat this process. If the person has problems with blood circulation, decrease the time that the ice is on the area to prevent possible skin damage." (https://medlineplus.gov/ency/article/002850.htm) CONFLICT: Brazil SES-SP 'Não colocar gelo ou água fria'
- **SCORPA-NOSUBST-BR** Secretaria de Estado da Saúde de São Paulo (CVE), Acidentes com escorpiões (alerta à população): "Não aplicar qualquer ti po de substância sobre o local da picada (fezes, álcool, querosene, fumo, ervas, urina, pó de café, terra)" (https://www.saude.sp.gov.br/resources/cve-centro-de-vigilancia-epidemiologica/areas-de-vigilancia/doencas-de-transmissao-por-vetores-e-zoonoses/escorpiao-evento/alerta23_populacao_escorpiao.pdf) ok ('ti po' = PDF text split)
- **SCORPA-RISK-MX** Secretaría de Salud de Morelos (MX), Exhorta SSM a prevenir intoxicaciones por picadura de alacrán (press note): "La prevención es fundamental para reducir el riesgo de intoxicaciones, en particular en niñas, niños, personas adultas mayores y con comorbilidades, quienes son más vulnerables a complicaciones. / La persona afectada debe acudir de inmediato a la unidad de salud más cercana, preferentemente dentro de los primeros 30 minutos posteriores al incidente, para recibir el tratamiento adecuado." (https://www.morelos.gob.mx/ultimas-noticias/exhorta-ssm-a-prevenir-intoxicaciones-por-picadura-de-alacran) ok (state press note)
- **SCORPA-SEVERE** MedlinePlus (US National Library of Medicine), Scorpion sting: "In severe cases, symptoms in different parts of the body may include: / Difficulty breathing / Drooling / Muscle spasms / Convulsions (seizures) / Random movements of the head, eye, or neck / If you or someone you are with is stung, call the local emergency number (such as 911), or the local poison control center" (https://medlineplus.gov/ency/article/002850.htm)
- **SCORPA-SIGNS-BR** Ministério da Saúde (BR), Acidentes por Escorpiões: "Sudorese profusa, agitação psicomotora, tremores, náuseas, vômitos, sialorreia / Crianças constituem o grupo mais suscetível ao envenenamento sistêmico grave." (https://www.gov.br/saude/pt-br/assuntos/saude-de-a-a-z/a/animais-peconhentos/acidentes-por-escorpioes)

</details>

Sign-off: [ ] EN  [ ] PT  [ ] ES  [ ] clinical review done  · notes: ____

## Before anything ships
- r4to signs off every card in EN, PT and ES (REVIEW.md checkboxes).
- Clinical review by a qualified person (doctor/paramedic/first-aid trainer), as for the snakebite card.
- Native PT-BR and ES review (ES uses neutral 'usted' and Latin American 'jugo'/'refresco'; Spain would differ).
- Recheck the † (summary-only) CDC quotes by eye.
- Decide the conflicts listed per card (honey, scorpion compress, rescue breaths, infant thrust technique, insulin line, vinegar; round 5: scorpion ice vs warm compress, rip-current 193).
- Engine: es text needs a one-line change (conditionCards.ts reads only en/pt) and the trigger changes in triggers.proposed.mjs; the sources line must not imply NHS endorsement.
