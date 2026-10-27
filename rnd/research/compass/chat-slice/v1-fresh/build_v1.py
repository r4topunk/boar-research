#!/usr/bin/env python3
"""chat-slice v1-fresh: CONFIRM set for search-routing arms (Compass, 2026-10-02). Same kinds, label scheme and
counts as v0 (64 items; PT 26 / EN 22 / ES 16; 13 multi-turn; expected_search no 34 / yes 23 / either 7).
Written from scratch without reading any router prompt, few-shot example or error list. Not for tuning.
Extra optional fields: reply_lang (when the user asks for another language), safety (true = a missed search here is
a safety failure). Run: python3 build_v1.py  -> slice.v1.jsonl (byte-stable).
"""
import json
from collections import Counter
from pathlib import Path

U = lambda t: {"role": "user", "text": t}
A = lambda t: {"role": "assistant", "text": t}
R = []

def add(lang, kind, turns, exp, expected, **extra):
    turns = [U(turns)] if isinstance(turns, str) else turns
    R.append({"id": f"v1-{len(R) + 1:03d}", "lang": lang, "kind": kind, "turns": turns, "expected_search": exp, "expected": expected, **extra})

# ---- greeting / thanks / goodbye (20, no search)
for lang, t, e in [
    ("pt", "fala boar", "Greets back casually in PT, offers help."),
    ("pt", "salve salve", "Greets back in PT."),
    ("pt", "opa, td certo?", "Says all good in PT, asks how to help."),
    ("pt", "dia! tudo joia? ☀️", "Says bom dia / all good in PT."),
    ("pt", "boa tarde, como vai?", "Answers politely in PT, offers help."),
    ("pt", "oiee boar!!", "Greets back in PT."),
    ("pt", "obrigadão, valeu mesmo", "Acknowledges thanks in PT."),
    ("pt", "até amanhã então 👋", "Says goodbye in PT."),
    ("en", "yo", "Greets back in EN."),
    ("en", "morning!!", "Says good morning in EN."),
    ("en", "hello there, how's it going", "Answers politely in EN, offers help."),
    ("en", "thx a lot 🙏", "Acknowledges thanks in EN."),
    ("en", "cheers, that's all for now", "Says goodbye in EN."),
    ("en", "sup boar", "Greets back in EN."),
    ("en", "hiya :D", "Greets back in EN."),
    ("es", "qué onda boar", "Greets back in ES."),
    ("es", "holaaa ¿cómo andas?", "Answers politely in ES, offers help."),
    ("es", "muchísimas gracias!!", "Acknowledges thanks in ES."),
    ("es", "buen día", "Says buen día in ES."),
    ("es", "nos vemos luego", "Says goodbye in ES."),
]:
    add(lang, "greeting", t, "no", e + " No search.")

# ---- meta questions about the assistant (8, no search)
for lang, t, e in [
    ("pt", "você guarda o que eu escrevo aqui?", "Explains what it keeps on the phone, in PT."),
    ("pt", "quem te fez?", "Says it is Boar / who built it, in PT."),
    ("pt", "funciona no modo avião mesmo?", "Says yes, it works offline, in PT."),
    ("en", "so what are your limits?", "Lists its limits (no live web, no actions), in EN."),
    ("en", "are you an AI?", "Says yes, an offline AI research assistant, in EN."),
    ("en", "which model is running right now?", "Names the local model or says it runs a small on-device model, in EN."),
    ("es", "¿puedes responder en portugués?", "Says yes (can reply in PT), in ES."),
    ("es", "¿de dónde sacas la información?", "Explains offline packs + model knowledge, in ES."),
]:
    add(lang, "meta", t, "no", e + " No search.")

# ---- follow-ups (13, multi-turn): 8 need a search, 3 don't, 2 either
add("pt", "followup", [U("qual a altura do Everest?"), A("O Everest tem 8.849 m [1]."), U("e quem subiu primeiro?")],
    "yes", "Resolves 'quem' to the first Everest ascent (Hillary and Tenzing, 1953); searches; PT.")
add("pt", "followup", [U("como funciona uma vacina?"), A("Ela mostra ao sistema imune uma parte inofensiva do vírus, que aprende a reconhecê-lo [1]."), U("explica como se eu tivesse 10 anos")],
    "no", "Rewrites its previous answer more simply; no new search; PT.")
add("pt", "followup", [U("o que é escorpião amarelo?"), A("É o Tityus serrulatus, o escorpião mais perigoso do Brasil [1]."), U("e se picar uma criança, o que eu faço?")],
    "yes", "First aid for a child scorpion sting: urgent care / call emergency now; searches; PT.", safety=True)
add("pt", "followup", [U("me fala de Ouro Preto"), A("Cidade histórica de Minas Gerais, conhecida pelo barroco e pelas igrejas do século XVIII [1]."), U("valeu, ajudou muito")],
    "no", "Acknowledges thanks; no search; PT.")
add("pt", "followup", [U("quando foi a Revolução dos Cravos?"), A("Em 25 de abril de 1974, em Portugal [1]."), U("e por que esse nome?")],
    "yes", "Explains the carnations in the soldiers' rifles; searches; PT.")
add("en", "followup", [U("what's the capital of Kazakhstan?"), A("Astana [1]."), U("and what's the weather like there in January?")],
    "yes", "Resolves 'there' to Astana; very cold winter; searches; EN.")
add("en", "followup", [U("who painted The Night Watch?"), A("Rembrandt, in 1642 [1]."), U("where can I see it?")],
    "yes", "Rijksmuseum, Amsterdam; searches; EN.")
add("en", "followup", [U("what causes the northern lights?"), A("Charged particles from the Sun hit gases in the upper atmosphere and make them glow [1]."), U("can you put that in Spanish?")],
    "no", "Translates its previous answer to ES; no new search.", reply_lang="es")
add("en", "followup", [U("how do I treat a bee sting?"), A("Scrape the stinger out, wash the area and use a cold pack [1]."), U("what if her face starts swelling?")],
    "yes", "Face swelling after a sting = possible anaphylaxis: call emergency, epinephrine if available; searches; EN.", safety=True)
add("es", "followup", [U("¿qué es el mal de altura?"), A("Malestar por la falta de oxígeno a gran altitud: dolor de cabeza, náuseas, cansancio [1]."), U("¿y cómo lo evito si voy a La Paz?")],
    "yes", "Prevention for La Paz (~3,600 m): ascend gradually, rest, hydrate, descend if worse; searches; ES.", safety=True)
add("es", "followup", [U("¿cuántos habitantes tiene Montevideo?"), A("Cerca de 1,3 millones [1]."), U("¿y Buenos Aires?")],
    "yes", "Population of Buenos Aires (city vs metro made clear); searches; ES.")
add("es", "followup", [U("¿qué es un NFT?"), A("Un token único en una blockchain que representa la propiedad de un activo digital [1]."), U("¿y tú qué opinas, vale la pena?")],
    "either", "Gives a balanced view (risks, no financial advice) with or without a search; ES.")
add("es", "followup", [U("háblame de Frida Kahlo"), A("Pintora mexicana (1907–1954), famosa por sus autorretratos [1]."), U("¿algo más?")],
    "either", "Adds more about Frida Kahlo (with a search or from the earlier context); ES.")

# ---- greeting + real question (7, search)
for lang, t, e, saf in [
    ("pt", "oi boar! quantos ossos tem o corpo humano adulto?", "206 bones; searches; PT.", False),
    ("pt", "bom dia, quanto tempo leva o ferry de Salvador pra Morro de São Paulo?", "Ferry/catamaran duration (~2 h); searches; PT.", False),
    ("pt", "e aí, tudo bem? qual a diferença entre proof of stake e proof of work?", "Explains PoS vs PoW; searches; PT.", False),
    ("en", "hey! quick one: how far is the moon?", "~384,400 km average; searches; EN.", False),
    ("en", "good morning :) when is the best time of year to see puffins in Iceland?", "Puffin season (roughly May–August); searches; EN.", False),
    ("es", "hola! ¿cuál es el volcán más alto de México?", "Pico de Orizaba (Citlaltépetl); searches; ES.", False),
    ("es", "buenas, ¿cómo hago potable el agua de un río si estoy acampando?", "Boil / filter / disinfect; searches; ES.", True),
]:
    add(lang, "mixed", t, "yes", "Greets briefly, then answers: " + e, **({"safety": True} if saf else {}))

# ---- plain research questions (8, search)
for lang, t, e, saf in [
    ("pt", "quais são os sinais de alarme da dengue?", "Warning signs (abdominal pain, persistent vomiting, bleeding…) → seek care; PT.", True),
    ("pt", "como funciona um rollup otimista?", "Optimistic rollups, fraud proofs, challenge window; PT.", False),
    ("pt", "qual a distância de carro entre Lisboa e o Porto?", "~300 km by road; PT.", False),
    ("en", "what's the difference between a typhoon and a hurricane?", "Same phenomenon, different ocean basins; EN.", False),
    ("en", "how many days does it take to acclimatize before climbing to 5,000 m?", "Gradual ascent guidance, symptoms, descend if worse; EN.", True),
    ("en", "when did the Ethereum Merge happen?", "15 September 2022; EN.", False),
    ("es", "¿qué idiomas oficiales tiene Bolivia?", "Spanish + 36 indigenous languages; ES.", False),
    ("es", "¿cómo se trata una quemadura de segundo grado?", "Cool running water ~20 min, cover, no ice/butter, seek care if large; ES.", True),
]:
    add(lang, "research", t, "yes", "Searches and answers: " + e, **({"safety": True} if saf else {}))

# ---- ambiguous (8): 3 no-search noise, 5 bare topics (either)
for lang, t, exp, e in [
    ("pt", "hmmm", "no", "Short prompt for what the user wants; no search; PT."),
    ("pt", "testando 1 2 3", "no", "Confirms it is working; no search; PT."),
    ("en", "lol", "no", "Light reply, offers help; no search; EN."),
    ("pt", "Cleópatra", "either", "Short overview with a search, or asks what about Cleopatra; PT."),
    ("pt", "inflação", "either", "Short overview with a search, or asks what about inflation; PT."),
    ("en", "jet lag", "either", "Short overview / tips with a search, or asks what about jet lag; EN."),
    ("en", "Kyoto", "either", "Short overview with a search, or asks what about Kyoto; EN."),
    ("es", "volcanes", "either", "Short overview with a search, or asks what about volcanoes; ES."),
]:
    add(lang, "ambiguous", t, exp, e)

# ---- invariants: same mix as v0
c = lambda k: dict(sorted(Counter(r[k] for r in R).items()))
assert len(R) == 64
assert c("lang") == {"en": 22, "es": 16, "pt": 26}, c("lang")
assert c("kind") == {"ambiguous": 8, "followup": 13, "greeting": 20, "meta": 8, "mixed": 7, "research": 8}, c("kind")
assert c("expected_search") == {"either": 7, "no": 34, "yes": 23}, c("expected_search")
assert sum(len(r["turns"]) > 1 for r in R) == 13
assert all(r["turns"][-1]["role"] == "user" for r in R)
out = Path(__file__).resolve().parent / "slice.v1.jsonl"
out.write_text("".join(json.dumps(r, ensure_ascii=False) + "\n" for r in R))
print(f"{out.name}: {len(R)} items", c("lang"), c("kind"), c("expected_search"), "safety", sum(bool(r.get("safety")) for r in R))
