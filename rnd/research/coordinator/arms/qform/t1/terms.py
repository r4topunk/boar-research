"""T1 TERMS (0 LLM): the search terms a "query bar" would show as editable chips, extracted without a model.
python3 -I t1/terms.py items/qform.questions.jsonl t1/terms.questions.jsonl

Rule (fixed before the run, portable to Kotlin): tokenize; drop stopwords, question words and first-person / narrative
filler; keep capitalised words (not sentence-initial), numbers and the remaining content words; entities and numbers
first, then content words in typed order; dedupe; at most MAX_TERMS. The question is replaced by the space-joined terms.
An empty extraction keeps the original question."""
import json, re, sys

MAX_TERMS = 6
STOP = set("""
a about above after again against all also am an and any are aren't as at be because been before being below between
both but by can can't could couldn't did didn't do does doesn't doing don't down during each few for from further had
has have having he her here hers herself him himself his how i i'd i'll i'm i've if in into is isn't it it's its itself
just let's me more most my myself no nor not of off on once only or other ought our ours ourselves out over own same
she should so some such than that that's the their theirs them themselves then there there's these they they're this
those through to too under until up very was wasn't we we're were what what's when where which while who whom why with
won't would you you're your yours yourself yourselves
""".split())
QUESTION = set("how what which when where who whom whose why whether".split())
FILLER = set("""
im ive id ill planning plan plans trip trips going go goes gonna want wanted wants wondering wonder know knows tell
telling need needs help please thanks thank think thinking heard hear read reading someone somebody friend friends
family mom dad mum kid kids son daughter wife husband partner boyfriend girlfriend next last week weekend month year
summer winter spring autumn today tomorrow tonight soon now currently really actually basically exactly roughly
approximately kind sort thing things stuff get gets got getting make makes way worried worry worries curious quick
question questions ok okay hey hi still maybe probably sure like likes love hate feel feeling felt bit lot lots much
many anyone anybody will shall must might may right true correct supposed also even ever well yeah yes guess say says
said told asked ask asking looking look find out explain idea mean means
""".split())

def tokens(q):
    return re.findall(r"\d[\d,\.]*\d|[A-Za-z0-9][A-Za-z0-9'\-\.]*[A-Za-z0-9]|[A-Za-z0-9]", q)

def extract(q):
    toks = tokens(q)
    ent, rest, seen = [], [], set()
    for i, t in enumerate(toks):
        low = t.lower().replace("'", "")
        if t.lower() in STOP or low in STOP or low in QUESTION or low in FILLER or (len(low) < 2 and not low.isdigit()):
            continue
        if low in seen:
            continue
        seen.add(low)
        sentence_start = i == 0 or re.search(re.escape(toks[i - 1]) + r"[\.\?\!:]\s+" + re.escape(t), q) is not None
        is_entity = any(ch.isdigit() for ch in t) or (t.isupper() and len(t) > 1) or (t[0].isupper() and not sentence_start)
        (ent if is_entity else rest).append(t)
    terms = (ent + rest)[:MAX_TERMS]
    return " ".join(terms)

if __name__ == "__main__":
    src, dst = sys.argv[1], sys.argv[2]
    n = empty = 0
    with open(dst, "w") as out:
        for line in open(src):
            if not line.strip():
                continue
            d = json.loads(line)
            t = extract(d["question"])
            if not t:
                empty += 1
                t = d["question"]
            d["original_question"] = d["question"]
            d["question"] = t
            out.write(json.dumps(d, ensure_ascii=False) + "\n")
            n += 1
    print(f"wrote {n} ({empty} empty extractions kept the original)", file=sys.stderr)
