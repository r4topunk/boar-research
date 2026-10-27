# Two-tier self-harm detection (EN/PT), written from safe-messaging categories, not from any eval item.
import re
# Tier 1: first-person ideation, intent, or method-seeking -> crisis card only (no retrieval, no model).
T1 = re.compile(r"\b(i|i'm|im|i am)\b[^.?!]{0,40}\b(want|going|plan(ning)?|thinking( about| of)?|feel like|wanna)\b[^.?!]{0,20}\b(to )?(die|kill myself|end (it all|my life|everything)|commit suicide|hurt myself|harm myself|not (be alive|wake up))|"
                r"\b(kill|hurt|harm|cut) myself\b|\bsuicidal\b|\bend my (own )?life\b|\bdon'?t want to (live|be alive|wake up)\b|\bno reason to live\b|"
                r"\b(how|what) (many|much)\b[^.?!]{0,40}\b(to|would) (die|kill (me|myself|a person|someone))\b|\b(lethal|fatal) dose\b|\bpainless (way|method) to die\b|\b(best|easiest|quickest) way to (die|kill myself|commit suicide)\b|"
                r"\bend(ing)? (it all|my (own )?life)\b|\bquero (morrer(?! de (rir|vergonha|fome|sono|t[ée]dio|saudade|calor|frio|inveja|amor))|me matar|sumir|acabar com (tudo|a minha vida))\b|\bme matar\b|\bpensando em (me matar|suic[íi]dio|morrer)\b|\bn[ãa]o quero mais viver\b|\btirar (a )?minha (pr[óo]pria )?vida\b|\bme (machucar|cortar)\b|\bsuicida\b|\bdose (letal|fatal)\b|\bquantos? (comprimidos|rem[ée]dios)\b[^.?!]{0,30}\bmorrer\b", re.I)
# Tier 2: topical mention -> normal answer + crisis-line footer (never suppress information).
T2 = re.compile(r"\bsuicid\w*|\bself[- ]harm\w*|\bautoles\w+|\bsuic[íi]di\w*", re.I)
EXCLUDE = re.compile(r"suicide (burn|doors?|squad|king|pact (song|film)|silence)|suicide squeeze|suicide (lane|knob|seat)", re.I)
def tier(q):
    if T1.search(q): return 1
    if T2.search(q) and not EXCLUDE.search(q): return 2
    return 0
