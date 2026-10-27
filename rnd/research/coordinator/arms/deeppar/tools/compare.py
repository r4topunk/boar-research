#!/usr/bin/env python3
"""DEEPPAR compare: reads raw/ (copied from <runner>/kiln/deeppar/out) and writes items.csv + prints tables."""
import json, os, re, sys, hashlib, csv
R = sys.argv[1]; OUTCSV = sys.argv[2]
items = sorted(f[:-12] for f in os.listdir(R) if f.endswith(".server.json"))
rows = []
def summ(path):
    d = {}
    if not os.path.exists(path): return d
    for l in open(path, errors="replace"):
        if l.startswith("# summary"):
            for kv in l.split()[2:]:
                k, _, v = kv.partition("="); d[k] = v
    return d
def footprint(path):
    s = open(path, errors="replace").read() if os.path.exists(path) else ""
    m = re.search(r"(\d+)\s+peak memory footprint", s); return int(m.group(1)) / 2**30 if m else None
def gen_text(it, prompt):
    so = open(f"{R}/{it}.bmoe.stdout", errors="replace").read()
    if not so.startswith(prompt): return None, "stdout does not start with prompt"
    rest = so[len(prompt):]; i = rest.rfind("\n\ngeneration: ")
    if i < 0: return None, "no generation: trailer"
    return rest[:i], ""
for it in items:
    prompt = open(f"{R}/{it}.rendered.txt").read()
    sj = json.load(open(f"{R}/{it}.server.json")); tm = sj.get("timings", {})
    s_txt = sj.get("content", "").rstrip()
    sm = summ(f"{R}/{it}.csv")
    b_txt, err = (None, "missing") if not os.path.exists(f"{R}/{it}.bmoe.stdout") else gen_text(it, prompt)
    b_txt = None if b_txt is None else b_txt.rstrip()
    ident = b_txt is not None and b_txt == s_txt
    idx = ""; win = ""
    if b_txt is not None and not ident:
        n = min(len(s_txt), len(b_txt)); idx = next((k for k in range(n) if s_txt[k] != b_txt[k]), n)
        win = f"server={s_txt[max(0,idx-20):idx+20]!r} bmoe={b_txt[max(0,idx-20):idx+20]!r} shorter_len={n} pct={100*idx/max(n,1):.0f}"
    rows.append(dict(item=it, prompt_n_server=tm.get("prompt_n"), prompt_n_bmoe=sm.get("n_prompt"),
                     identical=int(ident), first_diff_idx=idx,
                     server_tok_s=round(tm.get("predicted_per_second", 0), 2),
                     bmoe_tok_s=sm.get("tok/s"), bmoe_prefill_s=sm.get("prefill_s"),
                     bmoe_footprint_gib=None if footprint(f"{R}/{it}.bmoe.stderr") is None else round(footprint(f"{R}/{it}.bmoe.stderr"), 2)))
    print(it, "sha12", hashlib.sha256(prompt.encode()).hexdigest()[:12], "tail", repr(prompt[-120:]))
    print("   server_pred_n", tm.get("predicted_n"), "server_prompt_ms", tm.get("prompt_ms"), "tokens_evaluated", sj.get("tokens_evaluated"),
          "bmoe_tokens", sm.get("tokens"), err, win)
    print("   S:", repr(s_txt[:200])); print("   B:", repr((b_txt or "")[:200]))
with open(OUTCSV, "w", newline="") as f:
    w = csv.DictWriter(f, fieldnames=list(rows[0].keys())); w.writeheader(); w.writerows(rows)
print("side:", summ(f"{R}/side-00-chatml.csv").get("n_prompt"))
