# Builds chat-slice v0 (written by Compass 2026-10-02; original items, not from any bench or competitor set).
# Item: id, lang, kind, turns [{role,text}] (last = the user message under test; earlier = engine history),
# expected_search yes|no|either, expected (one line).
import json
U = lambda t: {"role": "user", "text": t}
A = lambda t: {"role": "assistant", "text": t}
I = []
def add(lang, kind, turns, es, exp): I.append({"lang": lang, "kind": kind, "turns": turns, "expected_search": es, "expected": exp})
# --- greetings / small talk, messy variants (no search)
for lang, t, e in [
    ("pt", "boa noite 🙂", "Greets back (boa noite), offers help in PT; no search."),
    ("pt", "boa noite boar", "Greets back by name-free reply in PT; no search."),
    ("pt", "boaa noitee", "Reads the elongated greeting as 'boa noite'; greets back in PT; no search."),
    ("pt", "oi tudo bem?", "Says it's fine and asks what the user wants to know, in PT; no search."),
    ("pt", "olá!! 😄", "Greets back in PT; no search."),
    ("pt", "bom diaaa", "Greets back (bom dia) in PT; no search."),
    ("pt", "e aí boar, beleza?", "Casual greeting back in PT; no search."),
    ("pt", "obrigado, ajudou muito", "Says you're welcome in PT; no search."),
    ("pt", "kkkk valeu", "Short friendly acknowledgement in PT; no search."),
    ("en", "good evening :)", "Greets back in EN; no search."),
    ("en", "heyyy", "Greets back in EN; no search."),
    ("en", "hi there boar!", "Greets back in EN; no search."),
    ("en", "hows it going", "Says it's doing fine, offers help, EN; no search."),
    ("en", "thanks a ton 🙏", "You're welcome, EN; no search."),
    ("en", "gm", "Reads 'gm' as good morning; greets back; no search."),
    ("es", "buenas noches", "Greets back in ES (buenas noches); no search."),
    ("es", "holaaa qué tal", "Greets back in ES and offers help; no search."),
    ("es", "buenas!", "Greets back in ES; no search."),
    ("es", "muchas gracias amigo", "De nada, in ES; no search."),
    ("es", "chau, hasta mañana", "Says goodbye in ES; no search."),
]: add(lang, "greeting", [U(t)], "no", e)
# --- meta questions about the app (no search)
for lang, t, e in [
    ("pt", "você funciona sem internet mesmo?", "Explains it runs offline on the phone with installed libraries; no search."),
    ("pt", "quais assuntos você sabe?", "Describes its installed libraries/kits in general terms; no search."),
    ("pt", "vc é o chatgpt?", "Says it's BOAR, an offline assistant on the phone; no search."),
    ("en", "what can you do offline?", "Describes offline answering from installed libraries; no search."),
    ("en", "where do your answers come from?", "Explains: installed offline sources, cited by number, else model memory with a label; no search."),
    ("en", "can you set an alarm for 7?", "Says it can't control the device; no search."),
    ("es", "¿necesitas internet para funcionar?", "Explains it works offline; no search."),
    ("es", "¿quién eres?", "Introduces itself as BOAR; no search."),
]: add(lang, "meta", [U(t)], "no", e)
# --- follow-ups that need the previous turn
add("pt", "followup", [U("me fala de Lisboa"), A("Lisboa é a capital de Portugal, à beira do rio Tejo, conhecida pelos bairros históricos como Alfama [1]."), U("e o clima de lá?")], "yes", "Resolves 'lá' = Lisboa; searches Lisbon climate; answers in PT.")
add("pt", "followup", [U("o que é a dengue?"), A("A dengue é uma doença viral transmitida pelo mosquito Aedes aegypti [1]."), U("e como previne?")], "yes", "Resolves to dengue prevention; searches; PT.")
add("pt", "followup", [U("qual a diferença entre ethereum e bitcoin?"), A("O Bitcoin é focado em transferência de valor; o Ethereum roda contratos inteligentes [1]."), U("resume em uma frase")], "no", "Shortens its previous answer; no new search needed.")
add("pt", "followup", [U("quem pintou a Guernica?"), A("Pablo Picasso, em 1937 [1]."), U("e onde ela está hoje?")], "yes", "Resolves 'ela' = Guernica; searches its current location (Reina Sofía); PT.")
add("pt", "followup", [U("me explica o que é staking"), A("Staking é travar ETH para ajudar a validar a rede e receber recompensas [1]."), U("não entendi, explica mais simples")], "either", "Re-explains simply; may reuse prior sources; no fresh topic.")
add("en", "followup", [U("tell me about the Atacama desert"), A("The Atacama in northern Chile is one of the driest non-polar places on Earth [1]."), U("compare with the other one")], "either", "'the other one' is unresolved: asks which desert, or assumes the Sahara and says so.")
add("en", "followup", [U("what's the capital of Australia?"), A("Canberra [1]."), U("how many people live there?")], "yes", "Resolves 'there' = Canberra; searches population; EN.")
add("en", "followup", [U("explain how vaccines train the immune system"), A("Vaccines show the immune system a harmless piece or version of a germ so it builds memory cells [1]."), U("thanks! and what about mRNA ones?")], "yes", "Thanks + follow-up: searches mRNA vaccines; EN.")
add("en", "followup", [U("what is PeerDAS?"), A("PeerDAS lets Ethereum nodes check blob availability by sampling pieces instead of downloading everything [1]."), U("can you say that again in Portuguese?")], "no", "Translates its previous answer to PT; no new search.")
add("en", "followup", [U("who wrote One Hundred Years of Solitude?"), A("Gabriel García Márquez, published in 1967 [1]."), U("what else did he write?")], "yes", "Resolves 'he'; searches other works; EN.")
add("es", "followup", [U("háblame de Machu Picchu"), A("Machu Picchu es una ciudadela inca en los Andes de Perú, del siglo XV [1]."), U("¿y cómo se llega?")], "yes", "Resolves to getting to Machu Picchu; searches; ES.")
add("es", "followup", [U("¿qué es la hipotermia?"), A("Es cuando la temperatura del cuerpo baja de 35 °C [1]."), U("¿y qué hago si le pasa a alguien?")], "yes", "Resolves to hypothermia first aid; searches; ES; safety-relevant.")
add("es", "followup", [U("¿quién fue Simón Bolívar?"), A("Un líder militar y político que encabezó la independencia de varios países sudamericanos [1]."), U("ok gracias")], "no", "Acknowledges; no search.")
# --- mixed greeting + question (search)
for lang, t, e in [
    ("pt", "boa noite! o que causa as marés?", "Greets briefly and answers about tides with a search; PT."),
    ("pt", "oi boar, quanto tempo dura a gestação de um elefante?", "Greets and answers (≈22 months) with a search; PT."),
    ("pt", "olá tudo bem? como purificar água sem fervura?", "Greets and answers with search; safety-relevant; PT."),
    ("en", "hey! why is the sky blue?", "Greets and explains Rayleigh scattering with a search; EN."),
    ("en", "good morning, what's the tallest mountain in Africa?", "Greets and answers Kilimanjaro with a search; EN."),
    ("es", "hola! ¿qué es un eclipse lunar?", "Saluda y explica con búsqueda; ES."),
    ("es", "buenas, ¿cuál es el río más largo de Sudamérica?", "Saluda y responde (Amazonas) con búsqueda; ES."),
]: add(lang, "mixed", [U(t)], "yes", e)
# --- plain research questions (search)
for lang, t, e in [
    ("pt", "por que o mar é salgado?", "Explains with search; PT."),
    ("pt", "quem foi Santos Dumont?", "Answers with search; PT."),
    ("pt", "como funciona uma usina hidrelétrica", "Explains with search; PT (no question mark)."),
    ("en", "what does a mitochondrion do", "Answers with search; EN (no question mark)."),
    ("en", "how do I treat a jellyfish sting?", "First-aid answer with search; safety-relevant; EN."),
    ("en", "when did the Berlin Wall fall?", "1989, with search; EN."),
    ("es", "¿por qué los flamencos son rosados?", "Explains (diet/carotenoids) with search; ES."),
    ("es", "qué es la fotosíntesis", "Explains with search; ES."),
]: add(lang, "research", [U(t)], "yes", e)
# --- ambiguous short ones
for lang, t, es, e in [
    ("pt", "Lisboa", "either", "A bare topic: a short overview with a search, or asks what about Lisbon; both fine."),
    ("pt", "e aí?", "no", "Casual greeting; no search."),
    ("pt", "sono", "either", "Unclear (sleep? sleepy?): asks what the user means, or gives a short sleep overview."),
    ("en", "bitcoin", "either", "A bare topic: overview with a search, or asks what about bitcoin."),
    ("en", "help", "no", "Explains what it can do and how to ask; no search."),
    ("en", "tell me something interesting", "either", "May share a fact (with or without search); should not refuse."),
    ("es", "café", "either", "A bare topic: overview with a search, or asks what about coffee."),
    ("es", "¿y tú?", "no", "Reply to small talk ('and you?'); no search."),
]: add(lang, "ambiguous", [U(t)], es, e)
for n, it in enumerate(I, 1): it["id"] = f"cs-{n:03d}"
with open("slice.v0.jsonl", "w") as f:
    for it in I: f.write(json.dumps({k: it[k] for k in ("id", "lang", "kind", "turns", "expected_search", "expected")}, ensure_ascii=False) + "\n")
import collections
print(len(I), "items;", dict(collections.Counter(i["lang"] for i in I)), dict(collections.Counter(i["kind"] for i in I)), dict(collections.Counter(i["expected_search"] for i in I)), "multi-turn", sum(len(i["turns"]) > 1 for i in I))
