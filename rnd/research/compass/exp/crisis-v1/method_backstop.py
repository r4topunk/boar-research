# Deterministic backstop (both tiers): method/dose-seeking phrasing never reaches retrieval or generation; it gets the crisis card.
# Deliberately narrow (it overrides the classifier only toward safety). Accidental-ingestion questions are NOT matched.
import re
METHOD = re.compile(r"\b(lethal|fatal|deadly) (dose|amount)\b|\b(how (many|much)|quantos?|quantas?|quanto)\b[^.?!]{0,50}\b(to die|to kill (myself|me)|para morrer|pra morrer|para n[ãa]o acordar|to not wake up|would kill (me|a person|someone)|d[áa] overdose|to overdose)\b|\b(painless|easiest|quickest|best) (way|method) to (die|kill myself|commit suicide)\b|\bforma (menos dolorosa|mais f[áa]cil|mais r[áa]pida) de (morrer|se matar)\b|\bdose (letal|fatal)\b", re.I)
