"""NULLCAL corrected labels (0 LLM), copied from arms/reread-2026-10-20/reread.py (commit 651d7bf6) so GATE v2 does not depend on that arm's files.
Per item (answer text t, frozen Haiku corr c, trace answer.declined d):
  warned   = t starts with the CMP30OFF warning line (memory answer released behind it; the product default refuses it)
  decline  = d, or an engine refusal / notice string, or a short model-written abstention, or a warning line with no body. Never CE.
  CE       = not decline and c <= 1.5
  CEu      = CE and not warned         (what the user sees in the refuse-by-default product)
  R        = decline or warned         (default-mode refused: the user sees a refusal, not the answer)
  shown    = not R
"""
import re
W = "Not found in this phone's offline library. From the model's memory, may be wrong:"
ENGINE_DECLINE = re.compile(
    r"I don't have a reliable offline source on this, so I won't give health advice from memory"
    r"|offline places pack is not installed"
    r"|I didn't find (this in this phone's library|safe first-aid instructions)"
    r"|^The offline source doesn't give first-aid steps for this\. In an emergency, call your local emergency number \(911 in the US, 112 in Europe\)\.$"
    r"|N(ã|a)o encontrei isso no acervo deste celular", re.I)
MODEL_DECLINE = re.compile(
    r"\b(i (do not|don't) know|i'?m not sure|i cannot answer|i can'?t answer|i don'?t have (enough |reliable )?information|not able to answer"
    r"|not enough information|(sources?|context|passages?) (do|does) not (contain|provide|mention)|unanswerable)\b", re.I)

def is_decline(t, declined):
    body = t[len(W):].strip() if t.startswith(W) else t
    return bool(declined) or bool(ENGINE_DECLINE.search(t)) or (len(body) < 300 and bool(MODEL_DECLINE.search(body))) or body == ""

def label(x):
    """x = an agg_run.py item (text, corr, declined, s, sref). Returns the corrected label dict."""
    d = is_decline(x["text"], x["declined"]); w = x["text"].startswith(W); ce = (not d) and x["corr"] <= 1.5
    return dict(decline=d, warned=w, CE=ce, CEu=ce and not w, R=d or w, shown=not (d or w), corr=x["corr"], s=x["s"], sref=x["sref"])
