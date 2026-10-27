# Per-condition lay + clinical terms (EN/PT), written from the condition definitions, frozen with the card.
import re
W = lambda s: re.compile(r"(?<![\w])(" + s + r")", re.I)
TERMS = {
 "co": W(r"carbon monoxide|\bco\b poison|mon[óo]xido de carbono|gas (heater|leak)|vazamento de g[áa]s|aquecedor a g[áa]s|generator (inside|indoors)"),
 "burn": W(r"burn(ed|t)? (my|his|her|their)|scald|boiling (water|oil)|hot (pan|oil|water|stove)|queim(ei|ou|ado|ada|adura)|[áa]gua fervendo|[óo]leo quente|panela quente"),
 "heatstroke": W(r"heat ?stroke|stopped sweating|collapsed in the heat|very hot and confused|insola[çc][ãa]o|golpe de calor|desmai\w* no calor|desabou no calor"),
 # Hypothermia needs cold exposure by definition: shaking/slurring alone is also hypoglycemia, stroke, seizure.
 "hypothermia": W(r"hypotherm|hipoterm|(shiver\w*|slurr\w+|stumbl\w+|confused)[^.?!]{0,80}\b(cold|snow|winter|freezing|icy|lake)\b|\b(cold|snow|winter|freezing)\b[^.?!]{0,80}(shiver\w*|slurr\w+|stumbl\w+|confus\w+)|(tremend\w*|fala enrolada|enrolando a fala|confus\w+)[^.?!]{0,80}\b(frio|neve|inverno|gelad\w*)\b|\b(frio|neve|inverno|gelad\w*)\b[^.?!]{0,80}(tremend\w*|enrolad\w*|confus\w+)"),
 "frostbite": W(r"frostbit|frostnip|frozen (toes|fingers|feet)|white,? (waxy|hard)|congelad|queimadura de frio"),
 "choking": W(r"chok(e|ing)|can'?t (breathe|speak) .{0,20}(food|stuck)|engasg"),
 "bleeding": W(r"bleeding (a lot|heavily|badly)|won'?t stop bleeding|blood (is )?(pouring|spurting)|sangrando muito|sangramento forte|n[ãa]o para de sangrar"),
 "heartattack": W(r"chest pain|pressure in (his|her|my) chest|heart attack|dor (forte )?no peito|aperto (forte )?no peito|infarto|ataque card"),
 "stroke": W(r"face (droop|drooping|drooped)|crooked (smile|face)|stroke\b|one side (of (his|her) body )?(is )?weak|boca torta|rosto (ca[íi]do|torto)|derrame|\bavc\b"),
 "seizure": W(r"seizure|convuls|fit\b|jerking|shaking on the (floor|ground)|se debatendo|ataque epil"),
 "anaphylaxis": W(r"anaphyla|throat (is )?(swelling|closing)|lips? (are |is )?swelling|garganta (inchando|fechando)|choque anafil"),
 "battery": W(r"swallow\w* (a |an )?(button |coin|watch |small )?batter|engoli\w* (uma )?(bateria|pilha)"),
 "eyechem": W(r"(bleach|chemical|cleaning product|acid|alkali)\w* .{0,25}(eye)|(eye).{0,25}(bleach|chemical)|(sanit[áa]ria|produto qu[íi]mico|produto de limpeza).{0,25}olho"),
 "electric": W(r"electric(al)? shock|electrocut|live (wire|cable)|got a shock|tomou choque|levou um choque|fio desencapado"),
 "jellyfish": W(r"jellyfish|man.o.war|blue ?bottle|[áa]gua.viva|caravela"),  # v0.1: bluebottle (FirstAidQA OOS check)
 "nosebleed": W(r"nose ?bleed|nose (is |started )?bleeding|bleeding from (my|the|his|her) nose|sangr\w* (pelo|no|do) nariz|nariz (sangrando|sangra)"),
 "earthquake": W(r"earthquake|ground is shaking|building is shaking|terremoto|tremor de terra|pr[ée]dio (est[áa] )?tremendo"),
 "drowning": W(r"drown|pulled .{0,20}out of the (water|pool|sea)|afog|tiramos .{0,20}(da|do) (piscina|mar|[áa]gua)"),
 "snakebite": W(r"snake ?bit|bitten by a (snake|viper|rattlesnake)|snake (just )?bit|cobra (me )?(picou|mordeu)|picad\w* (por|de) (uma )?(cobra|jararaca|cascavel)"),
}
def regex_condition(q):
    hits = [c for c, rx in TERMS.items() if rx.search(q)]
    return hits[0] if len(hits) == 1 else (None if not hits else "MULTI:" + "+".join(hits))
