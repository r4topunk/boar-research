# v1 long-tail conditions, added on top of the frozen v0.1 terms (terms.py unchanged).
import re
from terms import TERMS as V01, W
NEW = {
 # Hypoglycaemia: needs a diabetes/insulin/low-sugar cue; symptoms alone overlap heatstroke/stroke/seizure.
 # Hypoglycaemia: an explicit low-sugar term, OR a diabetes cue together with a typical symptom. Never "high blood sugar".
 "hypoglycemia": re.compile(r"^(?!.*\b(high blood sugar|hyperglyc|a[çc][úu]car alto|hiperglic))(?:.*(low (blood )?sugar|hypoglyc|hipoglic|glicose baixa|a[çc][úu]car (no sangue )?baixo)|(?=.*(diabet|diab[ée]tic|insulin))(?=.*\b(shak\w*|sweat\w*|confus\w*|faint\w*|dizzy|pale|drows\w*|tremend\w*|suad\w*|suando|confus\w*|desmai\w*|tont\w*)))", re.I | re.S),
 "altitude": W(r"altitude sickness|mountain sickness|\bams\b|hace\b|hape\b|at [0-9][0-9.,]{2,} ?m\b|high altitude|soroche|mal de altitude|doen[çc]a da altitude"),
 "beesting": W(r"\b(bee|wasp|hornet|yellow ?jacket)s?\b.{0,40}\b(sting|stung|stinger)|\bstung by an? (bee|wasp|hornet)|(abelha|vespa|marimbondo).{0,40}(picad|picou|ferr[ãa]o)|picad\w* (por|de) (uma )?(abelha|vespa|marimbondo)"),
 "scorpion": W(r"scorpion|escorpi[ãa]o"),
 "marinepuncture": W(r"sting ?ray|sea urchin|stonefish|weever|lionfish|arraia|ouri[çc]o.do.mar|peixe.pedra"),
 "tick": W(r"\bticks?\b|carrapato"),
 "animalbite": W(r"\b(dog|cat|monkey|bat|fox|raccoon|macaque)s?\b.{0,30}\b(bit|bite|bitten|scratch\w*)|\bbitten by an? (dog|cat|monkey|bat|fox|raccoon)|rabies|raiva|(cachorro|c[ãa]o|gato|macaco|morcego).{0,30}(mordeu|mordid|arranh)|mordid\w* (por|de) (um )?(cachorro|c[ãa]o|gato|macaco|morcego)"),
 "heatexhaustion": W(r"heat exhaustion|heat cramps?|cramps?.{0,40}\b(heat|sun|hot)\b|exaust[ãa]o (pelo|por) calor|c[ãa]imbras?.{0,40}\b(sol|calor)\b"),
}
TERMS = {**V01, **NEW}
def regex_condition(q):
    hits = [c for c, rx in TERMS.items() if rx.search(q)]
    return hits[0] if len(hits) == 1 else (None if not hits else "MULTI:" + "+".join(hits))
