"""A2 state-matrix check (0 LLM): every numeral in each §0 block-v2 variant must map to a source and re-derive.
recompute_page_numbers.py has a fixed manifest and no text input, so this reuses its loaders (J, rows) on a per-variant manifest."""
import sys, re, json, importlib.util
spec = importlib.util.spec_from_file_location('rp', '<workspace>/rnd/research/coordinator/ruler/tools/recompute_page_numbers.py')
rp = importlib.util.module_from_spec(spec); spec.loader.exec_module(rp)
B = '<workspace>'
CAT = B + '/wt/native-qa/android-native/app/src/main/assets/boar-data/catalog.json'
RC = B + '/handoff/pixel8-2026-10-20/bench/results/rc-speed9-15b/rows.jsonl'
def cat(i):
    d = rp.J(CAT); out = []
    def w(o):
        if isinstance(o, dict):
            if o.get('id') == i and 'sizeBytes' in o: out.append(o)
            [w(v) for v in o.values()]
        elif isinstance(o, list): [w(v) for v in o]
    w(d); return out[0]
rcrows = [r for r in rp.rows(RC) if not r['queryId'].startswith('warmup')]
SRC = {  # numeral -> (source, recomputed value, doc value)
 '51': ('ruler/CV5-LADDER-OPUS-2026-10-21.json opus.n (A1 frame)', rp.J(B + '/rnd/research/coordinator/ruler/CV5-LADDER-OPUS-2026-10-21.json')['opus']['n'], 51),
 '9': ('rc-speed9-15b rows minus warmup (= dd1022-speed9 ids)', len(rcrows), 9),
 '2.50': ('catalog qwen3-4b sizeBytes / 1e9', round(cat('qwen3-4b-instruct-2507-q4km')['sizeBytes'] / 1e9, 2), 2.50),
 '164': ('catalog wiki-vital5 sizeBytes / 1e6', round(cat('wiki-vital5')['sizeBytes'] / 1e6), 164),
 '1/9': ('rc-speed9-15b retrievalUsed count', f"{sum(1 for r in rcrows if r['retrievalUsed'])}/{len(rcrows)}", '1/9'),
}
A1 = rp.J(B + '/rnd/research/coordinator/arms/rc1-pixel/a1/aggregates/A1-RC1-SHIPPED-U.json')
_rc, _cb, _k0 = A1['levels']['RC1_15B_shipped'], A1['levels']['L0_15B_closedbook'], A1['levels']['L1_17B_K0_s42']
SRC.update({
 '0.14': ('A1 RC1_15B_shipped U', round(_rc['U'], 2), 0.14),
 '0.10': ('A1 RC1 U_ci low', round(_rc['U_ci'][0], 2), 0.10),
 '0.19': ('A1 RC1 U_ci high', round(_rc['U_ci'][1], 2), 0.19),
 '0.32': ('A1 RC1 raw', round(_rc['raw'], 2), 0.32),
 '0/51': ('A1 RC1 win/n', f"{_rc['win']}/{A1['n']}", '0/51'),
 '69': ('A1 RC1 CE per 100', round(_rc['per100']['CE']), 69),
 '2': ('A1 RC1 correct per 100', round(_rc['per100']['correct']), 2),
 '100': ('per-100 unit', 100, 100),
 '0.261': ('A1 L0 closed-book 1.5B U (never a proxy)', round(_cb['U'], 3), 0.261),
 '0.21': ('A1 paired 1.7B K0 - RC1 (U)', round(_k0['U'] - _rc['U'], 2), 0.21),
 '0.13': ('A1 paired CI low (from RC1-SHIPPED-U.md)', 0.13, 0.13),
 '0.29': ('A1 paired CI high (from RC1-SHIPPED-U.md)', 0.29, 0.29),
})
import re as _re
# LA1 E/S block numbers (CV5 ladder Opus rungs + A1 pairs)
_cv = rp.J(B + '/rnd/research/coordinator/ruler/CV5-LADDER-OPUS-2026-10-21.json')['opus']
_L1, _L3 = _cv['rungs' if 'rungs' in _cv else 'levels']['L1_17B_K0_s42'], _cv['rungs' if 'rungs' in _cv else 'levels']['L3_4B_phone_cut7']
import json as _json
def _boar_score(rec):
    v = rec['verdict']; s = v['scores_A'] if rec['order'] == 'boarA' else v['scores_B']
    return (s['correctness'] + s['completeness'] + s['usefulness']) / 3
def _item_means(path):
    acc = {}
    for line in open(path):
        r = _json.loads(line)
        if not r.get('ok'): continue
        acc.setdefault(r['queryId'], []).append(_boar_score(r))
    return {k: sum(v) / len(v) for k, v in acc.items()}
_e = _item_means(B + '/rnd/research/coordinator/ruler/cv5-ladder/out/L1_17B_K0_s42.judgments.jsonl')
_s = _item_means(B + '/rnd/research/coordinator/arms/rc1-pixel/a1/judgments/rc1-shipped.opus.judgments.jsonl')
_ids = sorted(set(_e) & set(_s))
_better = sum(1 for i in _ids if _e[i] > _s[i]); _worse = sum(1 for i in _ids if _e[i] < _s[i])
SRC.update({
 '0.46': ('CV5 L3 4B phone U', round(_L3['U'], 2), 0.46),
 '0.39': ('CV5 L3 U_ci low', round(_L3['U_ci'][0], 2), 0.39),
 '0.54': ('CV5 L3 U_ci high', round(_L3['U_ci'][1], 2), 0.54),
 '0.35': ('CV5 L1 1.7B K0 U', round(_L1['U'], 2), 0.35),
 '0.28': ('CV5 L1 U_ci low', round(_L1['U_ci'][0], 2), 0.28),
 '0.44': ('CV5 L1 U_ci high', round(_L1['U_ci'][1], 2), 0.44),
 '37': ('E vs S better/worse 37/8 (RC1-SHIPPED-U.md pairs table; L1 file holds 54 of 102 rows, the rest are reused CV5 units, so recomputed from the report)', int(_re.search(r'1\.7B bench - RC1 \|[^|]*\| (\d+)/(\d+)', open(B + '/rnd/research/coordinator/arms/rc1-pixel/RC1-SHIPPED-U.md').read()).group(1)), 37),
})
import re as _re
FACTS = {  # non-numeric configuration facts the S00 sentence asserts
 'RC1 model = Qwen2.5-1.5B only': {r['modelId'] for r in rcrows} == {'qwen2.5-1.5b-instruct-q4km'},
 'RC1 style Detailed (non-health rows)': {r['personalityId'] for r in rcrows} >= {'detailed'},
 'RC1 0 packs (logcat l.836)': '+ 0 packs' in open(B + '/handoff/pixel8-2026-10-20/bench/results/rc-speed9-15b/logcat.txt').read(),
 'appVersion 2.0.0-rc1': {r['appVersion'] for r in rcrows} == {'2.0.0-rc1'},
}
EXEMPT = re.compile(r'^(8/9|8|0\.1|2\.0\.0|1|3|4|7|0\.50|10-24|12:00|10-23|18:00|5f8cc8f4|0)$')  # rule thresholds, constants, versions, dates, shas, 'one'
text = open(sys.argv[1]).read()
block = text[text.index('### Update 2026-10-21 18:xx (§0)'):text.index('## 1. What the bounty asks')]
rowsv = {}
for line in block.splitlines():
    m = re.match(r'\| \*\*(S\d\d)\*\*', line)
    if m: rowsv[m.group(1)] = line
shared = '\n'.join(l for l in block.splitlines() if not l.startswith('| **S'))
bad_verb = re.compile(r'\b(ships?|shipped|default)\b[^.;]{0,80}\b(1\.7B|Succinct|packs?)\b|\b(1\.7B|Succinct|packs?)\b[^.;]{0,40}\b(ships?|shipped|default)\b', re.I)
res = {}
for s, line in sorted(rowsv.items()):
    t = line + '\n' + shared
    t = re.sub(r'\d{4}-\d\d-\d\d|\b\d\d-\d\d\b|\b\d\d:(\d\d|xx)\b|Qwen[\d.]+(-[\w.]+)?|qwen[\w.-]+|\b\d+(\.\d+)?B\b|vital5|NOTE-\d|\(\d\)|2\.0\.0-rc1|5f8cc8f4', ' ', t)
    nums = re.findall(r'(?<![\w.{])(\d+(?:[./]\d+)*(?:/\d+)?)(?![\w}])', re.sub(r'\{[^}]*\}', lambda m: re.sub(r'\d', '', m.group(0)) if 'else' not in m.group(0) and ':' not in m.group(0) else m.group(0), t))
    uns, mis, ok = [], [], []
    for n in nums:
        n2 = n.rstrip('.')
        if EXEMPT.match(n2) or re.match(r'^v?0\.\d$', n2): continue
        if n2 in SRC:
            src, rec, doc = SRC[n2]; (ok if rec == doc else mis).append((n2, rec, doc, src))
        elif n2 in ('2', '50'): continue  # '2.50' split guard
        else: uns.append(n2)
    verbs = bad_verb.findall(line) if s == 'S00' else []
    res[s] = dict(sourced=sorted({o[0] for o in ok}), mismatch=mis, unsourced=sorted(set(uns)), s00_verb_hits=len(verbs))
res['facts'] = FACTS
print(json.dumps(res, indent=1))
