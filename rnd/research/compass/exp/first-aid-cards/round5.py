"""Round 5 (Compass, 2026-10-03): ripcurrent (someone still in the water, caught in a rip current) and scorpionadult
(adult sting; the child card `scorpion` is unchanged). Why: compass/exp/card-mismatch/README.md (dev pairs): there was
no rip-current card (the drowning card is post-rescue CPR) and the scorpion card is child-only.
Imported by build_cards.py. Sources: SOURCES.raw-5.md (all curl, 55/55 exact)."""

RLSS = "https://www.rlss.org.uk/blog/understanding-rip-currents"
ARC = "https://www.redcross.org/content/dam/redcross/uncategorized/2/2313_rip_current_safety_final.pdf"
NOAA_OT, NWS_WRN, NOS_RIP, NWS_BRO = ("https://oceantoday.noaa.gov/ripcurrent/", "https://www.weather.gov/wrn/rip-currents-sm",
    "https://oceanservice.noaa.gov/facts/ripcurrent.html", "https://www.weather.gov/bro/ripcurrentescape")
CDC_INS = "https://www.cdc.gov/niosh/outdoor-workers/about/insects-and-scorpions.html"
MEDL, MEDL_ES = "https://medlineplus.gov/ency/article/002850.htm", "https://medlineplus.gov/spanish/ency/article/002850.htm"
SESSP = ("https://www.saude.sp.gov.br/resources/cve-centro-de-vigilancia-epidemiologica/areas-de-vigilancia/doencas-de-transmissao-por-vetores-e-zoonoses/"
         "escorpiao-evento/alerta23_populacao_escorpiao.pdf")
MS_ESC = "https://www.gov.br/saude/pt-br/assuntos/saude-de-a-a-z/a/animais-peconhentos/acidentes-por-escorpioes"
CONAPRA = "https://www.gob.mx/cms/uploads/attachment/file/732476/LesionesFaunaNociva_compressed.pdf"
MORELOS = "https://www.morelos.gob.mx/ultimas-noticias/exhorta-ssm-a-prevenir-intoxicaciones-por-picadura-de-alacran"
GTO = "https://salud.guanajuato.gob.mx/programas/picadura-de-alacran"

S5 = {
 "RIP-CALM": ("NOAA Ocean Today, Break the Grip of the Rip (video transcript)", NOAA_OT, "If you do happen to be caught in a rip current, stay calm. It won't pull you under - it'll just pull you away from shore. If you try to fight the rip current and swim against it, you'll just get worn out. Instead - float!", "ok"),
 "RIP-PARALLEL": ("NOAA Ocean Today, Break the Grip of the Rip (video transcript)", NOAA_OT, "If you're a good swimmer, swim parallel to shore until you've cleared the pull of the rip current. Swim with the waves, allowing them to push you to shore.", "CONFLICT (nuance): NOAA 'swim with the waves' vs NWS 'then at an angle toward the beach'"),
 "RIP-WAVE": ("NOAA Ocean Today, Break the Grip of the Rip (video transcript)", NOAA_OT, "If you can, wave and yell to get the attention of lifeguards and people on shore to let them know you need help.", "ok"),
 "RIP-OTHER": ("NOAA Ocean Today, Break the Grip of the Rip (video transcript)", NOAA_OT, "If you're on shore and see someone in trouble in a rip current call for help! If a lifeguard is not available, throw in something that floats or extend a reaching object, but don't try to be a hero and make the rescue yourself. Even trained lifeguards only attempt a rescue using a flotation device.", "ok"),
 "RIP-OPTIONS": ("NOAA National Weather Service, Social Media: Rip Currents", NWS_WRN, "If caught in a rip current: 1) Relax, rip currents don't pull you under. 2) Don't swim against the current. 3) Swim out of the current, then to shore. 4) If you can't escape, float or tread water. 5) If you need help, yell or wave for assistance.", "ok"),
 "RIP-ANGLE": ("NOAA National Weather Service, Social Media: Rip Currents", NWS_WRN, "Stay calm and don't swim against the current. Swim in a direction following the shoreline, then at an angle toward the beach. If you need help, call or wave for assistance.", "ok (NOAA NOS agrees: 'swim back to land at an angle')"),
 "RIP-911": ("NOAA National Weather Service, Social Media: Rip Currents", NWS_WRN, "Get help from a lifeguard. If there is no lifeguard, call 9-1-1. Advise the person to swim following the shoreline to escape the current. If possible, throw the person something that floats. Never enter the water without a floatation device. Many people have died trying to rescue someone caught in a rip current.", "ok"),
 "RIP-BRO": ("NOAA NWS Brownsville/Rio Grande Valley, Rip Current Avoidance and Escape Guidelines", NWS_BRO, "A good method for escaping the rip current is to swim parallel to the beach. / If you are unable to escape the current, do not panic. Stay calm, and float or calmly tread water even as the current moves you farther away from shore. / Seek immediate assistance from the beach patrol. If they are not available...call 9–1–1. Find something that can help the rip current victim stay afloat, such as a life jacket, inflatable object, or cooler, and throw it to them. Shout out instructions on how to escape, making sure to tell them to remain calm and not fight against the current. Many people drown while trying to save someone else from a rip current. Do not let that happen to you.", "ok"),
 "RIP-RLSS": ("Royal Life Saving Society UK (RLSS UK), Understanding Rip Currents: What they are and how to stay safe", RLSS, "[quote withheld (copyright); see url]", "ok (second source, added 2026-10-03; agrees with NOAA: calm + float first, parallel only if confident, then at an angle)"),
 "RIP-ARC-ESCAPE": ("American Red Cross, Rip Current Safety presentation (2014; subject-matter experts incl. the United States Lifesaving Association)", ARC, "[quote withheld (copyright); see url]", "ok (second source, added 2026-10-03)"),
 "RIP-ARC-HELP": ("American Red Cross, Rip Current Safety presentation (2014; subject-matter experts incl. the United States Lifesaving Association)", ARC, "[quote withheld (copyright); see url]", "ok (second source, added 2026-10-03; settles the bystander decision: don't go in unless trained)"),
 "RIP-ES": ("NOAA Ocean Today, Break the Grip of the Rip (transcripción en español)", NOAA_OT, "Mantenga la calma, no luche contra la corriente. / Nade lateralmente fuera de la corriente y paralelo a la orilla, después en ángulo de regreso a la orilla. / Flote y manténgase en calma en el agua. La corriente de resaca eventualmente se desvanecerá. / Trate de ver hacia la costa, mueva los brazos y grite pidiendo ayuda. / NO TRATE de rescatarla usted mismo, en su lugar busque a una persona salvavidas o llame a emergencias. / Grítele instrucciones. / Y si es posible, láncele un salvavidas o dispositivo de flotación.", "ok"),
 "SCORPA-CDC": ("CDC/NIOSH, Insects and Scorpions at Work", CDC_INS, "If a worker is stung by a scorpion: / Contact a qualified health care provider or poison control center. / Apply ice, but do not submerge the affected area in ice water. / Remain relaxed and calm. / Do not take any sedatives.", "CONFLICT: ice (CDC, MedlinePlus) vs warm compress and NO ice (Brazil SES-SP)"),
 "SCORPA-CARE": ("MedlinePlus (US National Library of Medicine), Scorpion sting", MEDL, "[MedlinePlus encyclopedia (A.D.A.M.) quote withheld; see url]", "ok (A.D.A.M. content: facts only)"),
 "SCORPA-CARE-ES": ("MedlinePlus en español (NLM), Picadura de escorpión", MEDL_ES, "[MedlinePlus encyclopedia (A.D.A.M.) quote withheld; see url]", "ok (A.D.A.M. content: facts only)"),
 "SCORPA-ICE": ("MedlinePlus (US National Library of Medicine), Scorpion sting", MEDL, "[MedlinePlus encyclopedia (A.D.A.M.) quote withheld; see url]", "CONFLICT: Brazil SES-SP 'Não colocar gelo ou água fria'"),
 "SCORPA-US": ("MedlinePlus (US National Library of Medicine), Scorpion sting", MEDL, "[MedlinePlus encyclopedia (A.D.A.M.) quote withheld; see url]", "CONFLICT (tier): US = most stings need no treatment; Brazil/Mexico = every sting → health service quickly"),
 "SCORPA-SEVERE": ("MedlinePlus (US National Library of Medicine), Scorpion sting", MEDL, "[MedlinePlus encyclopedia (A.D.A.M.) quote withheld; see url]", "ok"),
 "SCORPA-ADULT-BR": ("Secretaria de Estado da Saúde de São Paulo (CVE), Acidentes com escorpiões (alerta à população)", SESSP, "[quote withheld (copyright); see url]", "ok"),
 "SCORPA-WARM-BR": ("Secretaria de Estado da Saúde de São Paulo (CVE), Acidentes com escorpiões (alerta à população)", SESSP, "[quote withheld (copyright); see url]", "CONFLICT with CDC/MedlinePlus (ice)"),
 "SCORPA-NOSUBST-BR": ("Secretaria de Estado da Saúde de São Paulo (CVE), Acidentes com escorpiões (alerta à população)", SESSP, "[quote withheld (copyright); see url]", "ok ('ti po' = PDF text split)"),
 "SCORPA-SIGNS-BR": ("Ministério da Saúde (BR), Acidentes por Escorpiões", MS_ESC, "[quote withheld (copyright); see url]", "ok"),
 "SCORPA-911-MX": ("Secretaría de Salud (MX), STCONAPRA, Lesiones por fauna nociva (infographic)", CONAPRA, "[quote withheld (copyright); see url]", "ok (PDF infographic; 'Dificultad' is printed with an fi ligature)"),
 "SCORPA-RISK-MX": ("Secretaría de Salud de Morelos (MX), Exhorta SSM a prevenir intoxicaciones por picadura de alacrán (press note)", MORELOS, "[quote withheld (copyright); see url]", "ok (state press note)"),
 "SCORPA-GTO": ("Secretaría de Salud de Guanajuato (MX), Programa Picadura de alacrán", GTO, "[quote withheld (copyright); see url]", "ok"),
}


def build(st, L):
    C = []
    C.append({"id": "ripcurrent", "round": 5, "condition": "Caught in a rip current (still in the water)",
     "covers": "card-mismatch dev pairs ed-es-048, ed-en-092, ed-pt-092 (an active rip current got the post-rescue drowning card; ed-en-051 is a post-rescue pool item, so the drowning card is right there)",
     "topic": {"en": "caught in a rip current, being swept out to sea", "pt": "pego por uma corrente de retorno (repuxo) no mar", "es": "atrapado en una corriente de resaca en el mar"},
     "rules": ["rip-fight-current"],
     "review_flags": ["Order: NOAA says float first and swim parallel only 'if you're a good swimmer'; NWS lists 'swim out of the current' before 'float or tread water'. The card says calm + float first, then swim parallel 'if you can swim'.",
                      "After escaping: NWS/NOS 'at an angle toward the beach'; NOAA Ocean Today 'swim with the waves'. The card says 'at an angle back toward the beach'.",
                      "CPR line: the card only says 'once they're out, if not breathing normally, start CPR' (cited to the drowning card's British Red Cross row); the steps are on the drowning card. No rip-current page has a CPR line.",
                      "PT call line names Bombeiros 193 (Brazil's water-rescue service) + SAMU 192. The only fetched official quote with 193 is the Ministério da Saúde scorpion page's general emergency line; Brazilian state fire-department rip pages were 403/JS-only. Keep 193?",
                      "Second sources added 2026-10-03: RLSS UK (calm, float, signal; parallel only if confident, then at an angle) and the American Red Cross rip-current presentation written with USLA experts (bystander: call the lifeguard or 911, throw something that floats, talk them out, do not enter the water unless trained). RNLI, USLA and Surf Life Saving Australia pages are still blocked (403/JS-only); no Brazilian official rip page could be read (Paraná/Santa Catarina pages 403 or JS-rendered), so the PT 193 line has no rip-specific official quote."],
     "langs": {
      "en": L("Caught in a rip current (still in the water)", [
          st("If you're caught: stay calm and float. The current pulls you away from shore, not under. Don't swim against the current.", "RIP-CALM", "RIP-OPTIONS", "RIP-RLSS", "RIP-ARC-ESCAPE"),
          st("If you can swim, swim parallel to the shore until you're out of the pull, then swim at an angle back toward the beach.", "RIP-PARALLEL", "RIP-ANGLE", "RIP-BRO", "RIP-RLSS", "RIP-ARC-ESCAPE"),
          st("If you can't get out, keep floating or tread water, and wave and yell for help.", "RIP-OPTIONS", "RIP-WAVE", "RIP-BRO", "RIP-RLSS"),
          st("If someone else is caught: get a lifeguard; if there is none, call emergency services. Don't swim out to rescue them yourself.", "RIP-911", "RIP-OTHER", "RIP-BRO", "RIP-ARC-HELP"),
          st("Throw them something that floats (a life jacket, float or cooler) and shout to them to stay calm and swim parallel to the shore.", "RIP-911", "RIP-BRO", "RIP-ARC-HELP")],
          st("Call a lifeguard or emergency services now if anyone can't get back to shore. Once they're out of the water, if they aren't breathing normally, start CPR.", "RIP-911", "DROWN-2b", "RIP-ARC-HELP")),
      "pt": L("Preso numa corrente de retorno (ainda na água)", [
          st("Se você for pego: mantenha a calma e flutue. A corrente puxa para longe da praia, não para o fundo. Não nade contra a corrente.", "RIP-CALM", "RIP-OPTIONS", "RIP-RLSS", "RIP-ARC-ESCAPE"),
          st("Se souber nadar, nade paralelo à praia até sair da correnteza; depois nade em diagonal de volta para a areia.", "RIP-PARALLEL", "RIP-ANGLE", "RIP-BRO", "RIP-RLSS", "RIP-ARC-ESCAPE"),
          st("Se não conseguir sair, continue flutuando ou mantenha-se à tona, e acene e grite por ajuda.", "RIP-OPTIONS", "RIP-WAVE", "RIP-BRO", "RIP-RLSS"),
          st("Se outra pessoa for pega: chame o guarda-vidas; se não houver, ligue para a emergência. Não entre na água para resgatá-la sozinho.", "RIP-911", "RIP-OTHER", "RIP-BRO", "RIP-ARC-HELP"),
          st("Jogue algo que flutue (colete salva-vidas, boia ou caixa de isopor) e grite para ela manter a calma e nadar paralelo à praia.", "RIP-911", "RIP-BRO", "RIP-ARC-HELP")],
          st("Chame o guarda-vidas ou ligue para a emergência (Bombeiros 193 ou SAMU 192) agora se alguém não conseguir voltar. Quando a pessoa sair da água, se não respirar normalmente, comece a RCP.", "RIP-911", "SCORP-CHILD-1", "DROWN-2b", "RIP-ARC-HELP")),
      "es": L("Atrapado en una corriente de resaca (aún en el agua)", [
          st("Si queda atrapado: mantenga la calma y flote. La corriente lo aleja de la orilla, no lo hunde. No nade contra la corriente.", "RIP-ES", "RIP-CALM", "RIP-OPTIONS", "RIP-RLSS", "RIP-ARC-ESCAPE"),
          st("Si sabe nadar, nade de lado, paralelo a la orilla, hasta salir de la corriente; después nade en ángulo de regreso a la orilla.", "RIP-ES", "RIP-PARALLEL", "RIP-ANGLE", "RIP-RLSS", "RIP-ARC-ESCAPE"),
          st("Si no puede salir, siga flotando o manténgase a flote, y mueva los brazos y grite pidiendo ayuda.", "RIP-ES", "RIP-OPTIONS", "RIP-RLSS"),
          st("Si otra persona está atrapada: busque a un salvavidas; si no hay, llame a emergencias. No entre al agua a rescatarla usted mismo.", "RIP-ES", "RIP-911", "RIP-OTHER", "RIP-ARC-HELP"),
          st("Láncele algo que flote (un chaleco salvavidas, un flotador o una hielera) y grítele que mantenga la calma y nade paralelo a la orilla.", "RIP-ES", "RIP-BRO", "RIP-ARC-HELP")],
          st("Llame a un salvavidas o a emergencias ahora si alguien no puede volver a la orilla. Cuando salga del agua, si no respira con normalidad, empiece la RCP.", "RIP-ES", "RIP-911", "DROWN-2b", "RIP-ARC-HELP"))}})
    C.append({"id": "scorpionadult", "round": 5, "condition": "Scorpion sting in an adult",
     "covers": "card-mismatch dev pairs ed-es-045, ed-en-018 (an adult sting got the child-emergency card); the child card `scorpion` is unchanged",
     "topic": {"en": "scorpion sting in an adult", "pt": "adulto picado por escorpião", "es": "adulto picado por un alacrán"},
     "rules": ["scorpion-cut-suck"],
     "review_flags": ["Cold vs warm (as on the child card): CDC/NIOSH and MedlinePlus say ice wrapped in a cloth (10 min on/10 off, never immerse in ice water); Brazil SES-SP says a WARM compress and 'no ice or cold water, it makes the pain worse'. The default card has neither; the ice line is an ALTERNATIVE below. Add it (EN/ES only?), or keep it out?",
                      "When to go: Brazil (SES-SP, Ministério da Saúde) and Mexico (Morelos, Guanajuato) send EVERY sting to the nearest health service quickly; MedlinePlus (US): 'most stings from North American scorpions do not need treatment'. The card follows Brazil/Mexico (stricter; dangerous Tityus/Centruroides species there).",
                      "Higher-risk groups: older adults and people with other illnesses (Morelos, Guanajuato, CONAPRA 911 list), plus children (child card). 'Allergic reaction' signs (lip/throat swelling, trouble breathing) are on CONAPRA's 911 list, so they are in the call line.",
                      "'Keep the limb still' now has a source (MedlinePlus EN/ES); the child card still lacks it ('keep calm' only). Add it to the child card in a later round?",
                      "No dosing, no antihistamine (MedlinePlus mentions diphenhydramine: left out), no antivenom advice. Mexico's 'no ice' (Michoacán) could not be fetched; CONAPRA's 'no frío local' is in its SNAKEBITE box, not used here."],
     "langs": {
      "en": L("Scorpion sting (adult)", [
          st("Stay calm, move away from the scorpion, and keep the stung arm or leg as still as you can.", "SCORP-4", "SCORPA-CDC", "SCORPA-CARE"),
          st("Wash the sting with soap and water, and take off rings or anything tight near it.", "SCORP-2", "SCORPA-CARE"),
          st("Don't cut, squeeze or suck the sting, and don't use a tourniquet. Don't put home remedies on it (alcohol, kerosene, coffee grounds, herbs).", "SCORP-5", "SCORPA-NOSUBST-BR"),
          st("Go to the nearest health service (urgent care or hospital) as soon as possible; don't wait for other symptoms.", "SCORPA-ADULT-BR", "SCORP-2", "SCORPA-RISK-MX"),
          st("Older adults, people with other illnesses and children get the most serious poisoning: for them, go straight to hospital. A stung child is an emergency.", "SCORPA-RISK-MX", "SCORPA-GTO", "SCORPA-911-MX", "SCORP-CHILD-1")],
          st("Call emergency services now if they have trouble breathing, swelling of the lips or throat, drooling, muscle spasms or jerking movements, heavy sweating or vomiting, a racing heartbeat, or feel faint or confused.", "SCORPA-911-MX", "SCORPA-SEVERE", "SCORPA-SIGNS-BR")),
      "pt": L("Picada de escorpião (adulto)", [
          st("Mantenha a calma, afaste-se do escorpião e deixe o braço ou a perna picada o mais parado possível.", "SCORP-4", "SCORPA-CARE"),
          st("Lave o local com água e sabão e tire anéis ou o que estiver apertado perto da picada.", "SCORP-2", "SCORPA-CARE"),
          st("Não corte, não esprema, não chupe o local e não faça torniquete. Não passe nada no local (álcool, querosene, pó de café, ervas).", "SCORP-5", "SCORPA-NOSUBST-BR"),
          st("Procure o serviço de saúde mais próximo (pronto atendimento, pronto-socorro ou hospital) o mais rápido possível; não espere aparecerem outros sintomas.", "SCORPA-ADULT-BR", "SCORP-2"),
          st("Idosos, pessoas com outras doenças e crianças têm o envenenamento mais grave: nesses casos, vá direto ao hospital. Criança picada é emergência.", "SCORPA-RISK-MX", "SCORPA-GTO", "SCORP-CHILD-1")],
          st("Ligue para a emergência (SAMU 192) agora se houver falta de ar, inchaço nos lábios ou na garganta, salivação excessiva (babando), tremores ou espasmos musculares, suor intenso ou vômitos, coração disparado, ou sensação de desmaio ou confusão.", "SCORPA-911-MX", "SCORPA-SEVERE", "SCORPA-SIGNS-BR", "SCORP-CHILD-1")),
      "es": L("Picadura de alacrán (adulto)", [
          st("Mantenga la calma, aléjese del alacrán y mantenga el brazo o la pierna picada lo más quieta posible.", "SCORP-4", "SCORPA-CARE-ES"),
          st("Lave la picadura con agua y jabón, y quite anillos o cualquier cosa ajustada cerca de ella.", "SCORPA-CARE-ES"),
          st("No corte, no apriete ni chupe la picadura, y no use torniquete. No ponga remedios caseros (alcohol, queroseno, café, hierbas).", "SCORP-5", "SCORPA-NOSUBST-BR", "SCORPA-GTO"),
          st("Vaya al centro de salud más cercano lo antes posible; no espere a que aparezcan otros síntomas.", "SCORPA-RISK-MX", "SCORPA-GTO", "SCORPA-ADULT-BR"),
          st("Las personas mayores, las que tienen otras enfermedades y los niños sufren el envenenamiento más grave: en esos casos, vaya directo al hospital. Un niño picado es una emergencia.", "SCORPA-RISK-MX", "SCORPA-GTO", "SCORPA-911-MX")],
          st("Llame a emergencias ahora si tiene dificultad para respirar, hinchazón de labios o garganta, babeo, espasmos o movimientos bruscos de los músculos, mucho sudor o vómitos, el corazón muy acelerado, o si la persona se siente a punto de desmayarse o está confundida.", "SCORPA-911-MX", "SCORPA-SEVERE", "SCORPA-SIGNS-BR"))},
     "alt_steps": {
      "en": [st("For pain, put ice wrapped in a cloth on the sting, 10 minutes on and 10 minutes off; don't put the limb in ice water.", "SCORPA-CDC", "SCORPA-ICE")],
      "pt": [st("Para a dor, ponha gelo enrolado num pano sobre a picada, 10 minutos sim e 10 minutos não; não mergulhe o membro em água gelada.", "SCORPA-CDC", "SCORPA-ICE")],
      "es": [st("Para el dolor, ponga hielo envuelto en un paño sobre la picadura, 10 minutos sí y 10 minutos no; no meta el brazo o la pierna en agua helada.", "SCORPA-CDC", "SCORPA-ICE")]}})
    return C
