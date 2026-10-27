#!/usr/bin/env python3
"""chat-slice v2-fresh: CONFIRM set for search-routing arms after v1 became dev (Compass, 2026-10-03). Same kinds,
label scheme and counts as v0/v1 (64 items; PT 26 / EN 22 / ES 16; 13 multi-turn; expected_search no 34 / yes 23 /
either 7; 7 safety items, all 'yes'). Written from scratch without reading any router prompt or few-shot example.
Not for tuning. Optional fields: reply_lang, safety. Run: python3 build_v2.py -> slice.v2.jsonl (byte-stable).
"""
import json
from collections import Counter
from pathlib import Path

U = lambda t: {"role": "user", "text": t}
A = lambda t: {"role": "assistant", "text": t}
R = []

def add(lang, kind, turns, exp, expected, **extra):
    turns = [U(turns)] if isinstance(turns, str) else turns
    R.append({"id": f"v2-{len(R) + 1:03d}", "lang": lang, "kind": kind, "turns": turns, "expected_search": exp, "expected": expected, **extra})

# ---- greeting / thanks / goodbye (20, no search)
for lang, t, e in [
    ("pt", "eae mano", "Greets back casually in PT."),
    ("pt", "boa noite pra vc tbm", "Returns the good night in PT."),
    ("pt", "bom dia boar, tudo tranquilo?", "Says all good in PT, offers help."),
    ("pt", "alô, tem alguém aí?", "Says it is here and offers help in PT."),
    ("pt", "brigado viu", "Acknowledges thanks in PT."),
    ("pt", "falou, até depois", "Says goodbye in PT."),
    ("pt", "oi sumido 😅", "Greets back lightly in PT."),
    ("pt", "boa tarde!!", "Says boa tarde in PT."),
    ("en", "hey there 👋", "Greets back in EN."),
    ("en", "good afternoon!", "Says good afternoon in EN."),
    ("en", "evening, how are you doing?", "Answers politely in EN, offers help."),
    ("en", "ty!", "Acknowledges thanks in EN."),
    ("en", "appreciate it, have a good one", "Says goodbye in EN."),
    ("en", "hello hello", "Greets back in EN."),
    ("en", "see ya later", "Says goodbye in EN."),
    ("es", "buenas tardes", "Says buenas tardes in ES."),
    ("es", "hola boar, ¿qué tal?", "Answers politely in ES, offers help."),
    ("es", "gracias, muy amable", "Acknowledges thanks in ES."),
    ("es", "hasta pronto 👋", "Says goodbye in ES."),
    ("es", "saludos!", "Greets back in ES."),
]:
    add(lang, "greeting", t, "no", e + " No search.")

# ---- meta questions about the assistant (8, no search)
for lang, t, e in [
    ("pt", "quanto espaço você ocupa no celular?", "Explains model + packs take storage on the phone, in PT."),
    ("pt", "você consegue ver minha localização?", "Explains location use/permission, in PT."),
    ("pt", "como eu apago o histórico da conversa?", "Explains how to clear chats (or that it can't from here), in PT."),
    ("en", "do you remember what we talked about yesterday?", "Explains what chat memory it keeps, in EN."),
    ("en", "how big are your offline packs?", "Describes its packs / says sizes are in settings, in EN."),
    ("en", "can you speak other languages?", "Says it answers in PT/ES/EN, in EN."),
    ("es", "¿eres gratis?", "Answers about cost/offline use, in ES."),
    ("es", "¿quién te programó?", "Says who built Boar, in ES."),
]:
    add(lang, "meta", t, "no", e + " No search.")

# ---- follow-ups (13, multi-turn): 8 need a search, 3 don't, 2 either
add("pt", "followup", [U("qual o maior lago do Brasil?"), A("A Lagoa dos Patos, no Rio Grande do Sul [1]."), U("e qual a profundidade dela?")],
    "yes", "Resolves 'dela' to Lagoa dos Patos; shallow (a few metres on average); searches; PT.")
add("pt", "followup", [U("o que é inflação?"), A("É o aumento geral e contínuo dos preços, que reduz o poder de compra do dinheiro [1]."), U("resume em 3 tópicos")],
    "no", "Reformats its previous answer as 3 bullets; no new search; PT.")
add("pt", "followup", [U("o que é leptospirose?"), A("Uma infecção bacteriana transmitida pela urina de ratos, comum depois de enchentes [1]."), U("andei na água da enchente ontem, o que eu faço?")],
    "yes", "Watch for fever/muscle pain in the next weeks, see a doctor (prophylaxis is a medical decision); searches; PT.", safety=True)
add("pt", "followup", [U("quem foi Oscar Niemeyer?"), A("Um arquiteto brasileiro, autor dos principais prédios de Brasília [1]."), U("e em que ano ele morreu?")],
    "yes", "Resolves 'ele' to Niemeyer; 2012; searches; PT.")
add("pt", "followup", [U("me indica um livro sobre a história do Brasil"), A("'1808', de Laurentino Gomes, sobre a vinda da corte portuguesa [1]."), U("tem algum mais curto?")],
    "either", "Suggests a shorter title, with or without a search; PT.")
add("en", "followup", [U("what's the currency of Vietnam?"), A("The Vietnamese dong (VND) [1]."), U("and can I pay with cards in Hanoi?")],
    "yes", "Cards in hotels/larger shops, cash for street food and markets; searches; EN.")
add("en", "followup", [U("who invented the telephone?"), A("Alexander Graham Bell is credited, with an 1876 patent [1]."), U("was anyone else working on it at the same time?")],
    "yes", "Elisha Gray, Antonio Meucci; searches; EN.")
add("en", "followup", [U("what is a black hole?"), A("A region where gravity is so strong that nothing, not even light, can escape [1]."), U("make it shorter, two sentences max")],
    "no", "Shortens its previous answer; no new search; EN.")
add("en", "followup", [U("what are the symptoms of carbon monoxide poisoning?"), A("Headache, dizziness, nausea and confusion [1]."), U("my whole family has a headache and the heater is on, what now?")],
    "yes", "Get everyone out to fresh air now, turn off the heater if safe, call emergency services; searches; EN.", safety=True)
add("es", "followup", [U("¿dónde está el Salar de Uyuni?"), A("En el suroeste de Bolivia [1]."), U("¿cuál es la mejor época para ir?")],
    "yes", "Rainy season mirror effect vs dry season access; searches; ES.")
add("es", "followup", [U("¿qué es una insolación?"), A("Un trastorno por exposición prolongada al sol y al calor [1]."), U("mi amigo está confundido y no suda después de caminar al sol, ¿qué hago?")],
    "yes", "Possible heatstroke: call emergency, move to shade, cool actively, no fluids if not alert; searches; ES.", safety=True)
add("es", "followup", [U("¿qué es la blockchain?"), A("Un registro compartido de transacciones, copiado en muchos ordenadores y difícil de alterar [1]."), U("tradúcelo al portugués")],
    "no", "Translates its previous answer to PT; no new search.", reply_lang="pt")
add("es", "followup", [U("recomiéndame una serie sobre historia"), A("'Roma', de HBO, sobre el final de la República romana [1]."), U("¿y otra parecida?")],
    "either", "Suggests a similar series, with or without a search; ES.")

# ---- greeting + real question (7, search)
for lang, t, e, saf in [
    ("pt", "oi! quando foi fundada Brasília?", "21 April 1960; searches; PT.", False),
    ("pt", "bom dia, qual a melhor época pra visitar Fernando de Noronha?", "Dry season roughly Sep–Mar / trade-offs; searches; PT.", False),
    ("pt", "e aí boar, o que foi o hack da DAO em 2016?", "The DAO reentrancy exploit and the Ethereum hard fork; searches; PT.", False),
    ("en", "hi! what's the population of Iceland?", "~390,000; searches; EN.", False),
    ("en", "hey, quick question: is tap water safe to drink in Mexico City?", "Generally not recommended; bottled/treated water; searches; EN.", False),
    ("es", "hola, ¿cuál es la montaña más alta de Argentina?", "Aconcagua (~6,961 m); searches; ES.", False),
    ("es", "buenas! ¿qué hago si me pica una medusa?", "Leave the water, rinse with seawater (not fresh), remove tentacles carefully, no urine; searches; ES.", True),
]:
    add(lang, "mixed", t, "yes", "Greets briefly, then answers: " + e, **({"safety": True} if saf else {}))

# ---- plain research questions (8, search)
for lang, t, e, saf in [
    ("pt", "quais os sintomas de picada de aranha-marrom?", "Painless bite, then lesion/necrosis over hours, seek care; PT.", True),
    ("pt", "o que é o proof of history da Solana?", "Verifiable delay-style clock ordering transactions; PT.", False),
    ("pt", "quantos fusos horários tem o Brasil?", "Four; PT.", False),
    ("en", "what should I do if someone is having a seizure?", "Clear the area, cushion the head, nothing in the mouth, time it, recovery position, call if > 5 min; EN.", True),
    ("en", "what is the Ethereum blob fee market?", "EIP-4844 blobs with their own base fee; EN.", False),
    ("en", "what language do they speak in Andorra?", "Catalan (official), also Spanish/French; EN.", False),
    ("es", "¿cómo funciona un torniquete y cuándo se usa?", "Only for life-threatening limb bleeding when pressure fails; high and tight, note the time, emergency; ES.", True),
    ("es", "¿qué es el Camino de Santiago?", "Pilgrimage routes to Santiago de Compostela; ES.", False),
]:
    add(lang, "research", t, "yes", "Searches and answers: " + e, **({"safety": True} if saf else {}))

# ---- ambiguous (8): 3 no-search noise, 5 bare topics (either)
for lang, t, exp, e in [
    ("pt", "kkkkk", "no", "Light reply, offers help; no search; PT."),
    ("pt", "...", "no", "Asks what the user wants; no search; PT."),
    ("en", "nvm", "no", "Short acknowledgement; no search; EN."),
    ("pt", "Amazônia", "either", "Short overview with a search, or asks what about the Amazon; PT."),
    ("pt", "carnaval", "either", "Short overview with a search, or asks what about carnival; PT."),
    ("en", "Patagonia", "either", "Short overview with a search, or asks what about Patagonia; EN."),
    ("en", "malaria", "either", "Short overview with a search, or asks what about malaria; EN."),
    ("es", "tango", "either", "Short overview with a search, or asks what about tango; ES."),
]:
    add(lang, "ambiguous", t, exp, e)

# ---- invariants: same mix as v0/v1
c = lambda k: dict(sorted(Counter(r[k] for r in R).items()))
assert len(R) == 64
assert c("lang") == {"en": 22, "es": 16, "pt": 26}, c("lang")
assert c("kind") == {"ambiguous": 8, "followup": 13, "greeting": 20, "meta": 8, "mixed": 7, "research": 8}, c("kind")
assert c("expected_search") == {"either": 7, "no": 34, "yes": 23}, c("expected_search")
assert sum(len(r["turns"]) > 1 for r in R) == 13
assert sum(bool(r.get("safety")) for r in R) == 7 and all(r["expected_search"] == "yes" for r in R if r.get("safety"))
assert all(r["turns"][-1]["role"] == "user" for r in R)
out = Path(__file__).resolve().parent / "slice.v2.jsonl"
out.write_text("".join(json.dumps(r, ensure_ascii=False) + "\n" for r in R))
print(f"{out.name}: {len(R)} items", c("lang"), c("kind"), c("expected_search"), "safety", sum(bool(r.get("safety")) for r in R))
