#!/usr/bin/env python3
"""CV5-RECOMPUTE: re-derive every quoted number in RESEARCH-PAGE-OUTLINE-2026-10-21 §0-§2
(incl. 05:xx updates) and PLAN-2026-10-21-TO-25 §1 (table + 05:xx update) from its
machine-readable source. 0 LLM, 0 judge. Criterion: ruler/CV5-criterion.md (sha in .sha256).

Each manifest row: (id, doc, tag, quote, doc value, source, recompute fn | None, judge, n, seeds, note).
fn=None means UNSOURCED (prose-only, external, or blind/-only source).
Status: MATCH if |round(recomputed, doc decimals) - doc| <= 0.001, else MISMATCH.
Never reads blind/ or rnd/veil; for bench v0.4 nothing is read here.

Usage: python3 recompute_page_numbers.py [--json OUT.json] [--md OUT.md]
"""
import glob, json, math, os, statistics, sys

ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), '../../../../..'))
C = os.path.join(ROOT, 'rnd/research/coordinator')
A = os.path.join(C, 'arms')
R = os.path.join(C, 'ruler')
_cache = {}


def J(path):
    p = path if os.path.isabs(path) else os.path.join(ROOT, path)
    if p not in _cache:
        _cache[p] = json.load(open(p))
    return _cache[p]


def g(path, *keys):
    o = J(path)
    for k in keys:
        o = o[k]
    return o


def rows(path):
    p = path if os.path.isabs(path) else os.path.join(ROOT, path)
    if p not in _cache:
        _cache[p] = [json.loads(l) for l in open(p) if l.strip()]
    return _cache[p]


def p_nr(v, q):  # nearest-rank percentile
    v = sorted(v)
    return v[max(0, math.ceil(q * len(v)) - 1)]


def phone(path, field, stat='p50', filt=None, scale=1e-3):
    rs = [r for r in rows(path) if (filt is None or filt(r))]
    v = [r[field] * scale for r in rs if isinstance(r.get(field), (int, float)) and r.get(field)]
    if stat == 'p50':
        return statistics.median(v)
    if stat == 'p90':
        return p_nr(v, 0.9)
    if stat == 'max':
        return max(v)
    if stat == 'n':
        return len(rs)
    raise ValueError(stat)


def count_rows(pattern):
    n = 0
    for f in glob.glob(os.path.join(ROOT, pattern)):
        n += sum(1 for l in open(f) if l.strip())
    return n


def speed(run, *keys):
    for r in g('rnd/research/coordinator/ruler/SPEED-PRECHECK-2026-10-21.json', 'runs'):
        if r['run'] == run:
            o = r
            for k in keys:
                o = o[k]
            return o
    raise KeyError(run)


def lossmap():
    d = J('rnd/research/coordinator/arms/lossmap/aggregates/lossmap-K-vpara-s42.json')
    it = d['items']
    gap = 1 - sum(i['ratio'] for i in it) / len(it)
    tot = sum(i['loss'] for i in it)
    out = {'gap': gap, 'n': len(it)}
    groups = {}
    for i in it:
        p = i['primary']
        if p == 'wrong':
            p = 'wrong_src' if i['labels'].get('source_on_topic') else 'wrong_nosrc'
        gr = groups.setdefault(p, [0, 0.0])
        gr[0] += 1
        gr[1] += i['loss'] / tot * gap
    out['groups'] = groups
    nk = [i for i in it if i.get('n_kept', 0) == 0]
    out['nokept_n'] = len(nk)
    out['nokept_share'] = sum(i['loss'] for i in nk) / tot
    out['floor'] = 3 * len(it) / sum(sum(i['ref'].values()) for i in it)
    return out


LP = 'rnd/research/coordinator/arms/litepacks/aggregates/litepacks.json'
GP = 'rnd/research/coordinator/arms/gemma4-e2b/packs/packs-report.json'
VS = 'rnd/research/coordinator/arms/gemma4-e2b/vs4b/vs4b-report.json'
MX = 'rnd/research/coordinator/arms/coverage-matrix/matrix-report.json'
FD = 'rnd/research/coordinator/arms/floor-anchors/aggregates/floor-decline.json'
FL = 'rnd/research/coordinator/arms/floor-anchors/aggregates/floor.json'
W1 = 'rnd/research/coordinator/arms/floor-anchors/v1_1/aggregates/W1.json'
W1S = 'rnd/research/coordinator/arms/floor-anchors/v1_1/aggregates/W1-sep.json'
W3 = 'rnd/research/coordinator/arms/floor-anchors/v1_1/aggregates/W3.json'
WO = 'rnd/research/coordinator/ruler/warn-opus/warn-opus-opus.json'
RV2 = 'rnd/research/coordinator/ruler/RV2-SEP-LADDER-2026-10-21.json'
RV4 = 'rnd/research/coordinator/ruler/RV4-CITY-BOUND-2026-10-21.json'
RF = 'rnd/research/coordinator/ruler/refvar/refvar-results.json'
FP = 'rnd/research/coordinator/ruler/FACTPRESENT-2026-10-21.json'
IS = 'rnd/research/coordinator/ruler/inpack-split.json'
OR = 'rnd/research/coordinator/arms/oracle-real/aggregates/oracle-real.json'
PK3 = 'rnd/research/coordinator/ruler/PK3-OVERLAP-2026-10-21.json'
RAG = 'rnd/research/coordinator/ruler/RAG-FUNNEL-2026-10-21.json'
SS = 'rnd/research/coordinator/arms/packs/aggregates/selftest-scores.json'
L2S = 'rnd/research/coordinator/arms/packs-l2/aggregates/s_off.json'
L2W = 'rnd/research/coordinator/arms/packs-l2/aggregates/wave3_s_off.json'
L2P = 'rnd/research/coordinator/arms/packs-l2/aggregates/p_s.json'
SD = 'rnd/research/coordinator/arms/packs/aggregates/selftest-deep.json'
PR0 = 'rnd/research/coordinator/arms/packroute/aggregates/step0.json'
GK1 = 'rnd/research/coordinator/arms/gemma4-e2b-confirm-gk1/aggregates/gemma4-e2b-confirm-gk1-K1-main-s42.json'
AU = 'rnd/research/coordinator/arms/aunion-pixel/%s/aunion-summary.json'
PK5 = 'rnd/research/coordinator/arms/aunion-pixel/pk5/aggregates/pk5-M-diff16-s42.json'
RU = 'rnd/research/coordinator/arms/refuse-unsupported/ce-opus-ru/ceopusru-opus.json'
DV = 'rnd/research/coordinator/arms/deepvpara/aggregates/dv-vpara-2seed.L2.json'
DT = 'rnd/research/coordinator/arms/dt512/aggregates/L2-H-2seed.opus.json'
WF = 'rnd/research/coordinator/arms/wikifull/aggregates/stageAB-pooled.json'
PH = 'rnd/research/coordinator/arms/gemma4-e2b/phone/%s/rows.jsonl'
PH4 = 'handoff/pixel8-2026-10-20/bench/results/final-cut7-v01/rows.jsonl'
X6 = 'boar-eval/runs/device-poco-x6pro/final-cut7-v01/rows.jsonl'
AUR = 'rnd/research/coordinator/arms/aunion-pixel/%s/rows.jsonl'

O, P = 'OUTLINE', 'PLAN'
HK, OP, NA = 'Haiku 5.5-low', 'Opus', '-'


def K14(sl, *keys):
    vals = []
    for k in ('K1', 'K2', 'K3', 'K4'):
        o = g(LP, 'deltas', k, sl)
        for kk in keys:
            o = o[kk]
        vals.append(o)
    return vals


def rng(lo_hi, vals):
    return min(vals) if lo_hi == 'lo' else max(vals)


# fmt: (id, doc, section, tag(H=headline|-), quote, value, src, fn, judge, n, seeds, note)
M = [
 # ---------- OUTLINE §0 ----------
 ('O0-01', O, '§0', '-', 'V-para 1/1/1 floor = 0.206 raw', 0.206, 'arms/lossmap/aggregates/lossmap-K-vpara-s42.json (items ref scores)', lambda: lossmap()['floor'], 'Opus (judge.v1 rows)', 51, 's42', 'recomputed 3*51/sum(ref)'),
 ('O0-02', O, '§0u', 'H', 'decline floor D', 0.058, FD, lambda: g(FD, 'decline', 'a', 'U'), HK, 30, '1', ''),
 ('O0-03', O, '§0u', 'H', 'D CI low', 0.037, FD, lambda: g(FD, 'decline', 'a', 'U_ci')[0], HK, 30, '1', ''),
 ('O0-04', O, '§0u', 'H', 'D CI high', 0.081, FD, lambda: g(FD, 'decline', 'a', 'U_ci')[1], HK, 30, '1', ''),
 ('O0-05', O, '§0u', '-', 'D calls (180 Haiku)', 180, 'arms/floor-anchors/judgments/fa-decline-*.judgments.jsonl', lambda: count_rows('rnd/research/coordinator/arms/floor-anchors/judgments/fa-decline-*.judgments.jsonl'), HK, 30, '1', 'row count'),
 ('O0-06', O, '§0u', '-', 'v1.1 decline U 0.000', '0.000', W1, lambda: g(W1, 'validity', 'a', 'U'), HK, 30, '1', ''),
 ('O0-07', O, '§0u', '-', 'v1.1 CE flips 7/40', 7, W1, lambda: g(W1, 'consistency', 'n_flips'), HK, 40, '1', ''),
 ('O0-08', O, '§0u', '-', 'v1.1 CE flips denominator 40', 40, W1, lambda: g(W1, 'consistency', 'n'), HK, 40, '1', ''),
 ('O0-09', O, '§0u', '-', 'v1.1 retest SD 0.0265', 0.0265, W1, lambda: g(W1, 'retest', 'mean_item_sd'), HK, 20, '2 repeats', ''),
 ('O0-10', O, '§0u', '-', 'v1 retest SD 0.0206', 0.0206, W1, lambda: g(W1, 'retest', 'need'), HK, 20, '2 repeats', 'stored as the bar "need"'),
 ('O0-11', O, '§0u', '-', 'v1.1 calls 528 Haiku', 528, 'arms/floor-anchors/v1_1/judgments/W1-*.judgments.jsonl', lambda: count_rows('rnd/research/coordinator/arms/floor-anchors/v1_1/judgments/W1-*.judgments.jsonl'), HK, NA, NA, 'row count'),
 ('O0-12', O, '§0u', '-', 'v1.1b CE flips 5/40', 5, W3, lambda: g(W3, 'consistency', 'n_flips'), HK, 40, '1', ''),
 ('O0-13', O, '§0u', '-', 'v1.1b retest SD 0.0295', 0.0295, W3, lambda: g(W3, 'retest', 'mean_item_sd'), HK, 20, '2 repeats', ''),
 ('O0-14', O, '§0u', '-', 'v1.1b calls 300 Haiku', 300, 'arms/floor-anchors/v1_1/judgments/W3-*.judgments.jsonl', lambda: count_rows('rnd/research/coordinator/arms/floor-anchors/v1_1/judgments/W3-*.judgments.jsonl'), HK, NA, NA, 'row count'),
 ('O0-15', O, '§0u', '-', 'same-family judge lift 3.4-8.4 pp', 3.4, 'arXiv 2609.17857 (web/WEB-LOG-2026-10-21.md)', None, NA, NA, NA, 'external paper'),
 ('O0-16', O, '§0u', '-', 'WARN-OPUS CE kappa 0.81', 0.81, WO, lambda: g(WO, 'agreement', 'CE', 'kappa'), 'Opus vs Haiku', 111, '1', ''),
 ('O0-17', O, '§0u', '-', 'WARN-OPUS correct kappa 0.29', 0.29, WO, lambda: g(WO, 'agreement', 'correct', 'kappa'), 'Opus vs Haiku', 111, '1', ''),
 ('O0-18', O, '§0u', '-', 'WARN-OPUS n 111', 111, WO, lambda: g(WO, 'agreement', 'CE', 'n'), 'Opus vs Haiku', 111, '1', ''),
 # ---------- OUTLINE §1 speed (bench app, phone rows) ----------
 ('O1-01', O, '§1', '-', '1.7B TTFT p50 4.9 s (10 q)', 4.9, PH % 'q17b10-a', lambda: phone(PH % 'q17b10-a', 'ttftMs'), NA, 10, '1', 'rows.jsonl median ttftMs'),
 ('O1-02', O, '§1', '-', '1.7B answer p50 8.3 s', 8.3, PH % 'q17b10-a', lambda: phone(PH % 'q17b10-a', 'totalLatencyMs'), NA, 10, '1', ''),
 ('O1-03', O, '§1', '-', '1.7B 13.9 tok/s', 13.9, PH % 'q17b10-a', lambda: phone(PH % 'q17b10-a', 'tokPerSec', scale=1), NA, 10, '1', 'median tokPerSec'),
 ('O1-04', O, '§1', '-', '1.7B PSS 3.25 GB', 3.25, 'ruler/SPEED-PRECHECK-2026-10-21.json', lambda: speed('q17b10-a', 'pss_peak_gb'), NA, 10, '1', ''),
 ('O1-05', O, '§1', '-', 'TTFT 9.1 s before BATCHRET (litelat-9)', 9.1, 'QUEUE l.1428 (litelat-9 not in arms/litelat/compare.json)', None, NA, NA, NA, 'compare.json holds litelat-00..07 only (base ttft 9.18 s)'),
 ('O1-06', O, '§1', '-', 'TTFT 5.5 s after BATCHRET', 5.5, 'QUEUE l.1428', None, NA, NA, NA, ''),
 ('O1-07', O, '§1', '-', 'Gemma answer p50 11.8 s', 11.8, PH % 'gemma73-a', lambda: phone(PH % 'gemma73-a', 'totalLatencyMs'), NA, 73, '1', ''),
 ('O1-08', O, '§1', '-', 'Gemma answer p90 24.3 s', 24.3, PH % 'gemma73-a', lambda: phone(PH % 'gemma73-a', 'totalLatencyMs', 'p90'), NA, 73, '1', 'nearest-rank p90'),
 ('O1-09', O, '§1', '-', 'Gemma 7.0 tok/s', '7.0', PH % 'gemma73-a', lambda: phone(PH % 'gemma73-a', 'tokPerSec', scale=1), NA, 73, '1', ''),
 ('O1-10', O, '§1', '-', 'Gemma PSS peak 4.52 GB', 4.52, 'ruler/SPEED-PRECHECK-2026-10-21.json', lambda: speed('gemma73-a', 'pss_peak_gb'), NA, 73, '1', ''),
 ('O1-11', O, '§1', '-', 'Gemma 73/73', 73, PH % 'gemma73-a', lambda: sum(1 for r in rows(PH % 'gemma73-a') if r.get('outcome') == 'success'), NA, 73, '1', 'success rows'),
 ('O1-12', O, '§1', '-', '4B 4.2 tok/s (Pixel, cut 7)', 4.2, PH4, lambda: phone(PH4, 'tokPerSec', scale=1), NA, 73, '1', ''),
 ('O1-13', O, '§1', '-', '4B answer p50 25.5 s (Pixel)', 25.5, PH4, lambda: phone(PH4, 'wallMs'), NA, 73, '1', 'median wallMs over 73 rows (GEMMA4-PHONE definition); totalLatencyMs median = 25.42 -> 25.4'),
 ('O1-14', O, '§1', '-', '4B low-memory kill at 4.4 GB RSS', 4.4, 'QUEUE l.1415 / GEMMA4-PHONE.md (logcat)', None, NA, NA, NA, 'prose only'),
 ('O1-15', O, '§1', '-', 'X6 4B 72/72', 72, X6, lambda: sum(1 for r in rows(X6) if r.get('outcome') == 'success'), NA, 73, '1', 'boar-eval copy has 73 rows, 73 success; DEVICE-X6.md says 72/72 (CLAUDE.md says 72/73): denominator unresolved'),
 ('O1-16', O, '§1', '-', 'X6 fast p50 30.7 s', 30.7, X6, lambda: phone(X6, 'totalLatencyMs', filt=lambda r: r.get('tier') == 'fast'), NA, 51, '1', 'fast tier rows only (DEVICE-X6 definition)'),
 ('O1-17', O, '§1', '-', 'X6 fast p90 48.4 s', 48.4, X6, lambda: phone(X6, 'totalLatencyMs', 'p90', filt=lambda r: r.get('tier') == 'fast'), NA, 51, '1', 'nearest-rank; DEVICE-X6.md definition unresolved'),
 ('O1-18', O, '§1', '-', 'X6 PSS <= 4.23 GB after load', 4.23, 'arms/device-x6/DEVICE-X6.md (meminfo prose)', None, NA, NA, NA, 'no JSON field'),
]
# SPEED-PRECHECK table rows
for tid, run in (('a', 'aunion73-a'), ('b', 'q17b73-a'), ('c', 'gemma73-a'), ('d', 'final-cut7-v01')):
    docv = {'a': (4.4, 11.7, 4.4, 13.7, 11.3, 3.41), 'b': (2.9, 9.9, 2.9, 11.7, 12.4, 3.39),
            'c': (9.4, 18.1, 11.8, 23.9, '7.0', 4.52), 'd': (20.2, 39.2, '26.0', '52.0', 4.2, 4.92)}[tid]
    for j, (lab, keys) in enumerate((('T30 p50', ('sets', 'S1_answered', 't30_p50')), ('T30 p90', ('sets', 'S1_answered', 't30_p90')),
                                     ('complete p50', ('sets', 'S1_answered', 'complete_p50')), ('complete p90', ('sets', 'S1_answered', 'complete_p90')),
                                     ('decode tok/s', ('decode_tps_p50',)), ('PSS peak GB', ('pss_peak_gb',)))):
        M.append(('O1-S%s%d' % (tid, j), O, '§1u', '-', 'SPEED-PRECHECK %s %s' % (run, lab), docv[j], 'ruler/SPEED-PRECHECK-2026-10-21.json',
                  (lambda run=run, keys=keys: speed(run, *keys)), NA, NA, '1', 'answered set S1'))
M += [
 ('O1-19', O, '§1u', '-', '1.7B declines 35 % of v0.1', 0.35, 'ruler/SPEED-PRECHECK-2026-10-21.json', lambda: speed('q17b73-a', 'classes', 'declined') / speed('q17b73-a', 'n_rows'), NA, 72, '1', '25/72 claim kit; A-union run 26/72'),
 ('O1-20', O, '§1u', '-', 'Gemma declines 0 %', 0.0, 'ruler/SPEED-PRECHECK-2026-10-21.json', lambda: speed('gemma73-a', 'classes', 'declined') / speed('gemma73-a', 'n_rows'), NA, 72, '1', ''),
 ('O1-21', O, '§1u', '-', '4B declines 0 %', 0.0, 'ruler/SPEED-PRECHECK-2026-10-21.json', lambda: speed('final-cut7-v01', 'classes', 'declined') / speed('final-cut7-v01', 'n_rows'), NA, 72, '1', ''),
 ('O1-22', O, '§1u', '-', 'model-path-only 1.7B+A-union T30 p50 11.2', 11.2, 'ruler/SPEED-PRECHECK-2026-10-21.json', lambda: speed('aunion73-a', 'sets', 'S1_llm_only', 't30_p50'), NA, NA, '1', ''),
 ('O1-23', O, '§1u', '-', 'model-path-only T30 p90 13.0', '13.0', 'ruler/SPEED-PRECHECK-2026-10-21.json', lambda: speed('aunion73-a', 'sets', 'S1_llm_only', 't30_p90'), NA, NA, '1', ''),
 ('O1-24', O, '§1u', '-', 'model-path-only complete p50 12.1', 12.1, 'ruler/SPEED-PRECHECK-2026-10-21.json', lambda: speed('aunion73-a', 'sets', 'S1_llm_only', 'complete_p50'), NA, NA, '1', ''),
 ('O1-25', O, '§1u', '-', '4B + A-union answer p50 19.4 s', 19.4, AU % 'q4ba73-a', lambda: g(AU % 'q4ba73-a', 'answer_p50_s'), NA, 73, '1', ''),
 ('O1-26', O, '§1u', '-', '4B + A-union PSS peak 4.76 GB', 4.76, AU % 'q4ba73-a', lambda: g(AU % 'q4ba73-a', 'pss_peak_gb'), NA, 73, '1', ''),
 ('O1-27', O, '§1u', '-', '4B + A-union 0 LMK', 0, AU % 'q4ba73-a', lambda: g(AU % 'q4ba73-a', 'lmk_kills'), NA, 73, '1', ''),
 ('O1-28', O, '§1u', '-', '8,374 world tiles hosted', 8374, 'ruler/TILE-PATH-2026-10-21.md', None, NA, NA, NA, 'prose only (tilepath.py writes no JSON)'),
 ('O1-29', O, '§1u', '-', 'RV4 7 has_location items', 7, RV4, lambda: len(g(RV4, 'loc_ids')), NA, 7, NA, 'ids only (v0.4 metadata)'),
 ('O1-30', O, '§1u', '-', 'RV4 headline weight 65.5', 65.5, RV4, lambda: g(RV4, 'sum_w_H'), NA, 71, NA, ''),
 ('O1-31', O, '§1u', 'H', 'RV4 share 10.7 %', 0.107, RV4, lambda: g(RV4, 'phi_nominal'), NA, 71, NA, ''),
 ('O1-32', O, '§1u', '-', 'RV4 swing >= 0.107', 0.107, RV4, lambda: g(RV4, 'max_swing_all0_vs_all1_lower_bound'), NA, 71, NA, ''),
 ('O1-33', O, '§1u', '-', 'RV4 tile ceiling 0.098', 0.098, RV4, lambda: g(RV4, 'proxy', 'phi_proxy'), HK, NA, NA, 'dev proxy'),
 ('O1-34', O, '§1u', '-', 'RV4 tile ceiling CI low 0.089', 0.089, RV4, lambda: g(RV4, 'proxy', 'phi_ci')[0], HK, NA, NA, ''),
 ('O1-35', O, '§1u', '-', 'RV4 tile ceiling CI high 0.106', 0.106, RV4, lambda: g(RV4, 'proxy', 'phi_ci')[1], HK, NA, NA, ''),
 ('O1-36', O, '§1u', '-', 'decline bare 0.058', 0.058, FD, lambda: g(FD, 'decline', 'a', 'U'), HK, 30, '1', ''),
 ('O1-37', O, '§1u', '-', 'decline hedged 0.053', 0.053, FD, lambda: g(FD, 'decline', 'b', 'U'), HK, 30, '1', ''),
 ('O1-38', O, '§1u', '-', 'decline fluent no-content 0.016', 0.016, FD, lambda: g(FD, 'decline', 'c', 'U'), HK, 30, '1', ''),
 ('O1-39', O, '§1u', '-', '1.5B anchor judge.v1 +0.035', 0.035, FL, lambda: g(FL, 'separability', 'dU'), HK, 57, '1', ''),
 ('O1-40', O, '§1u', '-', '1.5B anchor judge.v1 CI low', -0.019, FL, lambda: g(FL, 'separability', 'dU_ci')[0], HK, 57, '1', ''),
 ('O1-41', O, '§1u', '-', '1.5B anchor judge.v1 CI high', 0.089, FL, lambda: g(FL, 'separability', 'dU_ci')[1], HK, 57, '1', ''),
 ('O1-42', O, '§1u', '-', '1.5B anchor v1.1 +0.047', 0.047, W1S, lambda: g(W1S, 'v1_1', 'dU'), HK, 57, '1', ''),
 ('O1-43', O, '§1u', '-', '1.5B anchor v1.1 CI low', -0.0005, W1S, lambda: g(W1S, 'v1_1', 'dU_ci')[0], HK, 57, '1', ''),
 ('O1-44', O, '§1u', '-', '1.5B anchor v1.1 CI high', 0.097, W1S, lambda: g(W1S, 'v1_1', 'dU_ci')[1], HK, 57, '1', ''),
 ('O1-45', O, '§1u', 'H', 'RV2 1.7B-1.5B +0.040', 0.040, RV2, lambda: g(RV2, 'primary_51', 'pairs', 'L1-L0', 'dU'), HK, 51, '2 (1.7B)', ''),
 ('O1-46', O, '§1u', 'H', 'RV2 1.7B-1.5B CI low', -0.019, RV2, lambda: g(RV2, 'primary_51', 'pairs', 'L1-L0', 'dU_ci')[0], HK, 51, '2', ''),
 ('O1-47', O, '§1u', 'H', 'RV2 1.7B-1.5B CI high', 0.096, RV2, lambda: g(RV2, 'primary_51', 'pairs', 'L1-L0', 'dU_ci')[1], HK, 51, '2', ''),
 ('O1-48', O, '§1u', '-', 'REFVAR draw A-B 1.7B |dU| 0.015', 0.015, RF, lambda: abs(g(RF, 'dU', 's17|A-B', 'dU')), HK, 20, '1', 'sign: A-B = -0.015'),
 ('O1-49', O, '§1u', '-', 'REFVAR draw A-B 4B 0.008', 0.008, RF, lambda: g(RF, 'dU', 's4b|A-B', 'dU'), HK, 20, '1', ''),
 ('O1-50', O, '§1u', '-', 'REFVAR uncapped - v1 1.7B +0.013', 0.013, RF, lambda: g(RF, 'dU', 's17|AB-v1', 'dU'), HK, 20, '1', ''),
 ('O1-51', O, '§1u', '-', 'REFVAR uncapped - v1 4B +0.001', 0.001, RF, lambda: g(RF, 'dU', 's4b|AB-v1', 'dU'), HK, 20, '1', ''),
 ('O1-52', O, '§1u', '-', 'REFVAR 4B-1.7B gap v1 0.084', 0.084, RF, lambda: g(RF, 'gap_4b_minus_17', 'v1'), HK, 20, '1', ''),
 ('O1-53', O, '§1u', '-', 'REFVAR 4B-1.7B gap draws 0.072', 0.072, RF, lambda: g(RF, 'gap_4b_minus_17', 'AB'), HK, 20, '1', ''),
 ('O1-54', O, '§1u', '-', 'REFVAR Opus+web reference draws 40', 40, 'ruler/refvar/refs', lambda: count_rows('rnd/research/coordinator/ruler/refvar/refs/draw[AB].jsonl'), OP, 20, NA, 'rows in drawA + drawB'),
 # ---------- OUTLINE §2 table ----------
 ('O2-01', O, '§2', '-', '1.7B K0 U on 80 self-tests 0.393', 0.393, LP, lambda: g(LP, 'arms', 'K0', 'st_cand', 'U'), HK, 80, '1', ''),
 ('O2-02', O, '§2', '-', '1.7B K3 U 0.462', 0.462, LP, lambda: g(LP, 'arms', 'K3', 'st_cand', 'U'), HK, 80, '1', ''),
 ('O2-03', O, '§2', '-', '1.7B K3-K0 +0.069', 0.069, LP, lambda: g(LP, 'deltas', 'K3', 'st_cand', 'U', 'd'), HK, 80, '1', ''),
 ('O2-04', O, '§2', '-', 'CI low +0.038', 0.038, LP, lambda: g(LP, 'deltas', 'K3', 'st_cand', 'U', 'ci')[0], HK, 80, '1', ''),
 ('O2-05', O, '§2', '-', 'CI high +0.099', 0.099, LP, lambda: g(LP, 'deltas', 'K3', 'st_cand', 'U', 'ci')[1], HK, 80, '1', ''),
 ('O2-06', O, '§2', '-', 'simplewiki +0.104 (low end K1-K3)', 0.104, LP, lambda: min(g(LP, 'deltas', k, 'st:boar-simplewiki-en', 'U', 'd') for k in ('K1', 'K2', 'K3')), HK, 20, '1', ''),
 ('O2-07', O, '§2', '-', 'simplewiki +0.106 (high end)', 0.106, LP, lambda: max(g(LP, 'deltas', k, 'st:boar-simplewiki-en', 'U', 'd') for k in ('K1', 'K2', 'K3')), HK, 20, '1', ''),
 ('O2-08', O, '§2', '-', 'factbook +0.104 (K3)', 0.104, LP, lambda: g(LP, 'deltas', 'K3', 'st:boar-factbook', 'U', 'd'), HK, 20, '1', ''),
 ('O2-09', O, '§2', '-', 'medlineplus +0.057 (K3)', 0.057, LP, lambda: g(LP, 'deltas', 'K3', 'st:boar-medlineplus-en', 'U', 'd'), HK, 20, '1', ''),
 ('O2-10', O, '§2', '-', 'firstaid +0.007 (K3)', 0.007, LP, lambda: g(LP, 'deltas', 'K3', 'st:boar-firstaid-en', 'U', 'd'), HK, 20, '1', ''),
 ('O2-11', O, '§2', '-', 'MAIN off-pack dU high end -0.004 (K1-K4)', -0.004, LP, lambda: rng('hi', K14('MAIN', 'U', 'd')), HK, 97, '1', ''),
 ('O2-12', O, '§2', '-', 'MAIN off-pack dU low end -0.012', -0.012, LP, lambda: rng('lo', K14('MAIN', 'U', 'd')), HK, 97, '1', ''),
 ('O2-13', O, '§2', '-', 'MAIN all CIs straddle 0 (1 = yes)', 1, LP, lambda: int(all(c[0] < 0 < c[1] for c in K14('MAIN', 'U', 'ci'))), HK, 97, '1', 'boolean'),
 ('O2-14', O, '§2', '-', 'SE off-pack dU high end -0.003', -0.003, LP, lambda: rng('hi', K14('st_se', 'U', 'd')), HK, 100, '1', ''),
 ('O2-15', O, '§2', '-', 'SE off-pack dU low end -0.011', -0.011, LP, lambda: rng('lo', K14('st_se', 'U', 'd')), HK, 100, '1', ''),
 ('O2-16', O, '§2', '-', 'Gemma K0 U 0.395', 0.395, GP, lambda: g(GP, 'all80', 'U', 'G0'), HK, 80, '1', ''),
 ('O2-17', O, '§2', '-', 'Gemma K3 U 0.497', 0.497, GP, lambda: g(GP, 'all80', 'U', 'G3'), HK, 80, '1', ''),
 ('O2-18', O, '§2', '-', 'Gemma dU +0.102', 0.102, GP, lambda: g(GP, 'all80', 'dU_G'), HK, 80, '1', ''),
 ('O2-19', O, '§2', '-', 'Gemma dU CI low 0.061', 0.061, GP, lambda: g(GP, 'all80', 'dU_G_ci')[0], HK, 80, '1', ''),
 ('O2-20', O, '§2', '-', 'Gemma dU CI high 0.144', 0.144, GP, lambda: g(GP, 'all80', 'dU_G_ci')[1], HK, 80, '1', ''),
 ('O2-21', O, '§2', '-', 'DiD vs 1.7B +0.034', 0.034, GP, lambda: g(GP, 'all80', 'DiD'), HK, 80, '1', ''),
 ('O2-22', O, '§2', '-', 'DiD CI low +0.001', 0.001, GP, lambda: g(GP, 'all80', 'DiD_ci')[0], HK, 80, '1', ''),
 ('O2-23', O, '§2', '-', 'DiD CI high +0.066', 0.066, GP, lambda: g(GP, 'all80', 'DiD_ci')[1], HK, 80, '1', ''),
 ('O2-24', O, '§2', '-', 'Gemma MAIN K0 U 0.434', 0.434, VS, lambda: g(VS, 'gemma_vs_q17_s42_ref', 'U_cand'), HK, 97, '1', ''),
 ('O2-25', O, '§2', '-', '1.7B MAIN K0 U 0.406', 0.406, VS, lambda: g(VS, 'gemma_vs_q17_s42_ref', 'U_ctl'), HK, 97, '1', ''),
 ('O2-26', O, '§2', '-', 'Gemma-1.7B MAIN +0.028', 0.028, VS, lambda: g(VS, 'gemma_vs_q17_s42_ref', 'dU'), HK, 97, '1', ''),
 ('O2-27', O, '§2', '-', 'Gemma K1 MAIN dU +0.017', 0.017, GK1, lambda: g(GK1, 'vs_control', 'deltas', 'U', 'd'), HK, 97, '1', ''),
 ('O2-28', O, '§2', '-', 'Gemma K1 MAIN CI low -0.008', -0.008, GK1, lambda: g(GK1, 'vs_control', 'deltas', 'U', 'ci')[0], HK, 97, '1', ''),
 ('O2-29', O, '§2', '-', 'Gemma K1 MAIN CI high +0.040', 0.040, GK1, lambda: g(GK1, 'vs_control', 'deltas', 'U', 'ci')[1], HK, 97, '1', ''),
 ('O2-30', O, '§2', '-', 'MATRIX 1.7B KA MAIN dU -0.007', -0.007, MX, lambda: g(MX, 'MAIN97_noharm', 'dU', 'd'), HK, 97, '1', ''),
 ('O2-31', O, '§2', '-', 'MATRIX KA MAIN CI low -0.026', -0.026, MX, lambda: g(MX, 'MAIN97_noharm', 'dU', 'ci')[0], HK, 97, '1', ''),
 ('O2-32', O, '§2', '-', 'MATRIX KA MAIN CI high +0.012', 0.012, MX, lambda: g(MX, 'MAIN97_noharm', 'dU', 'ci')[1], HK, 97, '1', ''),
 ('O2-33', O, '§2', '-', 'CE-unwarned K0 7', 7, MX, lambda: g(MX, 'MAIN97_noharm', 'cells', 'main-q17-K0', 'CEu'), HK, 97, '1', ''),
 ('O2-34', O, '§2', '-', 'CE-unwarned KA 12', 12, MX, lambda: g(MX, 'MAIN97_noharm', 'cells', 'main-q17-KA', 'CEu'), HK, 97, '1', ''),
 ('O2-35', O, '§2', '-', 'PACKREAD 4B D4 0.650', 0.650, 'QUEUE l.1387-1390 (arms/packread has judgments, no aggregate)', None, HK, 54, '1', 'judgment rows exist; definition of the scale not in a JSON'),
 ('O2-36', O, '§2', '-', 'PACKREAD 1.7B D4 0.529', 0.529, 'QUEUE l.1387-1390', None, HK, 54, '1', ''),
 ('O2-37', O, '§2', '-', 'PACKREAD LFM2.5 0.554', 0.554, 'QUEUE l.1387-1390', None, HK, 54, '1', ''),
 ('O2-38', O, '§2', '-', '4B single pack raw +0.032 (Haiku)', 0.032, SS, lambda: g(SS, 'pooled', 'paired', 'd_raw'), HK, 180, '1', ''),
 ('O2-39', O, '§2', '-', 'raw CI low +0.016', 0.016, SS, lambda: g(SS, 'pooled', 'paired', 'd_raw_ci')[0], HK, 180, '1', ''),
 ('O2-40', O, '§2', '-', 'raw CI high +0.050', 0.050, SS, lambda: g(SS, 'pooled', 'paired', 'd_raw_ci')[1], HK, 180, '1', ''),
 ('O2-41', O, '§2', 'H', '"above_min +0.042 Opus L2"', 0.042, L2S, lambda: g(L2S, 'judges', 'opus', 'pooled', 'paired', 'd_above_min'), OP, 180, '1', 'LABEL: 0.042 (0.024-0.062) is the Opus RAW delta; Opus above_min = 0.053'),
 ('O2-42', O, '§2', 'H', '"above_min" CI low 0.024', 0.024, L2S, lambda: g(L2S, 'judges', 'opus', 'pooled', 'paired', 'd_above_min_ci')[0], OP, 180, '1', 'raw CI low = 0.024'),
 ('O2-43', O, '§2', 'H', '"above_min" CI high 0.062', 0.062, L2S, lambda: g(L2S, 'judges', 'opus', 'pooled', 'paired', 'd_above_min_ci')[1], OP, 180, '1', 'raw CI high = 0.062'),
 ('O2-44', O, '§2', '-', 'wave 3 +0.045 Opus', 0.045, L2W, lambda: g(L2W, 'judges', 'opus', 'pooled', 'paired', 'd_raw'), OP, 40, '1', 'raw scale'),
 ('O2-45', O, '§2', '-', 'wave 3 CI low +0.007', 0.007, L2W, lambda: g(L2W, 'judges', 'opus', 'pooled', 'paired', 'd_raw_ci')[0], OP, 40, '1', ''),
 ('O2-46', O, '§2', '-', 'wave 3 CI high +0.087', 0.087, L2W, lambda: g(L2W, 'judges', 'opus', 'pooled', 'paired', 'd_raw_ci')[1], OP, 40, '1', ''),
 ('O2-47', O, '§2', '-', 'deep + think: packs add -0.002', -0.002, SD, lambda: g(SD, 'pooled', 'H_with_vs_without', 'd_raw'), HK, 180, '1', ''),
 ('O2-48', O, '§2', '-', 'deep packs CI low -0.020', -0.020, SD, lambda: g(SD, 'pooled', 'H_with_vs_without', 'd_raw_ci')[0], HK, 180, '1', ''),
 ('O2-49', O, '§2', '-', 'deep packs CI high +0.016', 0.016, SD, lambda: g(SD, 'pooled', 'H_with_vs_without', 'd_raw_ci')[1], HK, 180, '1', ''),
 ('O2-50', O, '§2', '-', 'deep reads +0.054 over 4B', 0.054, SD, lambda: g(SD, 'pooled', 'Hwith_vs_4Bwith', 'd_raw'), HK, 180, '1', ''),
 ('O2-51', O, '§2', '-', 'venues P5 0/7 -> 7/7', 7, 'arms/venuegps/VENUEGPS-2.md (blind-side venue scorer output)', None, '0 judge', 7, '2', 'prose only; scorer outputs under blind/'),
 ('O2-52', O, '§2', '-', 'area tile +3.65 MB', 3.65, 'arms/venuegps/VENUEGPS-2.md', None, NA, NA, NA, 'tiles.json has fetch metadata, not the kit delta'),
 ('O2-53', O, '§2', '-', 'warned share SE +0.12 (low end K1-K4)', 0.12, LP, lambda: rng('lo', K14('st_se', 'warned', 'd')), HK, 100, '1', ''),
 ('O2-54', O, '§2', '-', 'warned share SE +0.19 (high end)', 0.19, LP, lambda: rng('hi', K14('st_se', 'warned', 'd')), HK, 100, '1', ''),
 ('O2-55', O, '§2', '-', '4B fact article kept 68/180 (one pack)', 68, PR0, lambda: g(PR0, 'selftest180', 'all', 'S', 'art_kept'), '0 judge', 180, NA, ''),
 ('O2-56', O, '§2', '-', '4B fact article kept 46/180 (9 peers)', 46, PR0, lambda: g(PR0, 'selftest180', 'all', 'P', 'art_kept'), '0 judge', 180, NA, ''),
 ('O2-57', O, '§2', '-', '4B crowding -0.019 Opus L2', -0.019, L2P, lambda: g(L2P, 'judges', 'opus', 'pooled', 'paired', 'd_raw'), OP, 180, '1', ''),
 ('O2-58', O, '§2', '-', 'crowding CI low -0.035', -0.035, L2P, lambda: g(L2P, 'judges', 'opus', 'pooled', 'paired', 'd_raw_ci')[0], OP, 180, '1', ''),
 ('O2-59', O, '§2', '-', 'crowding CI high -0.003', -0.003, L2P, lambda: g(L2P, 'judges', 'opus', 'pooled', 'paired', 'd_raw_ci')[1], OP, 180, '1', ''),
 ('O2-60', O, '§2', '-', 'prompt tokens K0 384', 384, LP, lambda: g(LP, 'retrieval', 'K0', 'MAIN', 'prompt_tokens_mean'), NA, 97, '1', ''),
 ('O2-61', O, '§2', '-', 'prompt tokens K1-K4 low 729', 729, LP, lambda: min(g(LP, 'retrieval', k, 'MAIN', 'prompt_tokens_mean') for k in ('K1', 'K2', 'K3', 'K4')), NA, 97, '1', ''),
 ('O2-62', O, '§2', '-', 'prompt tokens K1-K4 high 792', 792, LP, lambda: max(g(LP, 'retrieval', k, 'MAIN', 'prompt_tokens_mean') for k in ('K1', 'K2', 'K3', 'K4')), NA, 97, '1', ''),
 ('O2-63', O, '§2', '-', 'desktop TTFT K0 1.6 s', 1.6, LP, lambda: g(LP, 'retrieval', 'K0', 'MAIN', 'ttft_ms_p50') / 1e3, NA, 97, '1', ''),
 ('O2-64', O, '§2', '-', 'desktop TTFT K1-K4 low 3.9 s', 3.9, LP, lambda: min(g(LP, 'retrieval', k, 'MAIN', 'ttft_ms_p50') for k in ('K1', 'K2', 'K3', 'K4')) / 1e3, NA, 97, '1', ''),
 ('O2-65', O, '§2', '-', 'desktop TTFT K1-K4 high 4.4 s', 4.4, LP, lambda: max(g(LP, 'retrieval', k, 'MAIN', 'ttft_ms_p50') for k in ('K1', 'K2', 'K3', 'K4')) / 1e3, NA, 97, '1', ''),
 ('O2-66', O, '§2', '-', 'disk +0.74 GB (K1)', 0.74, LP, lambda: (g(LP, 'sizes_bytes', 'K1') - g(LP, 'sizes_bytes', 'K0')) / 1e9, NA, NA, NA, 'decimal GB'),
 ('O2-67', O, '§2', '-', 'disk +2.5 GB (K4)', 2.5, LP, lambda: (g(LP, 'sizes_bytes', 'K4') - g(LP, 'sizes_bytes', 'K0')) / 1e9, NA, NA, NA, 'decimal GB'),
 ('O2-68', O, '§2', 'H', 'A-union +2.4 s retrieval p50 (1.7B)', 2.4, 'arms/aunion-pixel (A-union side only)', None, NA, 73, '1', 'A-union side 3.99 s in aunion-summary.json; the 1.5-1.6 s baseline has no JSON field (rows firstSourcesMs p50 = 1.70 s, a different stamp)'),
 ('O2-69', O, '§2', '-', 'A-union answer p50 +3.4 s (1.7B)', 3.4, AUR % 'aunion73-a', lambda: phone(AUR % 'aunion73-a', 'totalLatencyMs') - phone(PH % 'q17b73-a', 'totalLatencyMs'), NA, 73, '1', 'rows medians 7.57 - 4.16'),
 ('O2-70', O, '§2', '-', 'V-para kit holds the fact 6/51', 6, 'VPARA-DIAGNOSIS §1 / PACKCOND-P1 (no count field in packcond-K-vpara.json)', None, 'jev', 51, NA, ''),
 ('O2-71', O, '§2', '-', 'V-para all packs 10/51', 10, 'VPARA-DIAGNOSIS §1 / PACKCOND-P2', None, 'jev', 51, NA, ''),
 # ---------- OUTLINE §2 05:xx update ----------
 ('O2u-01', O, '§2u', 'H', 'FACTPRESENT self-test cell a +0.139', 0.139, FP, lambda: g(FP, 'contrasts', 'oracle (self-tests, fact chunk id kept)', '1.7B K3-K0 | self-tests topical 60', 'a: present in K3 only', 'd'), HK, 27, '1', ''),
 ('O2u-02', O, '§2u', 'H', 'cell a CI low +0.075', 0.075, FP, lambda: g(FP, 'contrasts', 'oracle (self-tests, fact chunk id kept)', '1.7B K3-K0 | self-tests topical 60', 'a: present in K3 only', 'ci')[0], HK, 27, '1', ''),
 ('O2u-03', O, '§2u', 'H', 'cell a CI high +0.201', 0.201, FP, lambda: g(FP, 'contrasts', 'oracle (self-tests, fact chunk id kept)', '1.7B K3-K0 | self-tests topical 60', 'a: present in K3 only', 'ci')[1], HK, 27, '1', ''),
 ('O2u-04', O, '§2u', '-', 'cell a n 27', 27, FP, lambda: g(FP, 'contrasts', 'oracle (self-tests, fact chunk id kept)', '1.7B K3-K0 | self-tests topical 60', 'a: present in K3 only', 'n'), HK, 27, '1', ''),
 ('O2u-05', O, '§2u', '-', 'Gemma cell a +0.168', 0.168, FP, lambda: g(FP, 'contrasts', 'oracle (self-tests, fact chunk id kept)', 'Gemma K3-K0 | self-tests topical 60', 'a: present in K3 only', 'd'), HK, 27, '1', ''),
 ('O2u-06', O, '§2u', 'H', 'real MAIN cell a K3-K0 -0.010', -0.010, FP, lambda: g(FP, 'contrasts', 'present', '1.7B K3-K0 | MAIN 97', 'a: present in K3 only', 'd'), HK, 10, '1', ''),
 ('O2u-07', O, '§2u', 'H', 'real cell a CI low -0.077', -0.077, FP, lambda: g(FP, 'contrasts', 'present', '1.7B K3-K0 | MAIN 97', 'a: present in K3 only', 'ci')[0], HK, 10, '1', ''),
 ('O2u-08', O, '§2u', 'H', 'real cell a CI high +0.050', 0.050, FP, lambda: g(FP, 'contrasts', 'present', '1.7B K3-K0 | MAIN 97', 'a: present in K3 only', 'ci')[1], HK, 10, '1', ''),
 ('O2u-09', O, '§2u', '-', 'real cell a n 10', 10, FP, lambda: g(FP, 'contrasts', 'present', '1.7B K3-K0 | MAIN 97', 'a: present in K3 only', 'n'), HK, 10, '1', ''),
 ('O2u-10', O, '§2u', '-', 'strict +0.005', 0.005, FP, lambda: g(FP, 'contrasts', 'strict', '1.7B K3-K0 | MAIN 97', 'a: present in K3 only', 'd'), HK, 7, '1', ''),
 ('O2u-11', O, '§2u', '-', 'strict n 7', 7, FP, lambda: g(FP, 'contrasts', 'strict', '1.7B K3-K0 | MAIN 97', 'a: present in K3 only', 'n'), HK, 7, '1', ''),
 ('O2u-12', O, '§2u', '-', 'K1-K0 -0.015', -0.015, FP, lambda: g(FP, 'contrasts', 'present', '1.7B K1-K0 | MAIN 97', 'a: present in K1 only', 'd'), HK, NA, '1', ''),
 ('O2u-13', O, '§2u', '-', 'cell b +0.059', 0.059, FP, lambda: g(FP, 'contrasts', 'present', '1.7B K3-K0 | MAIN 97', 'b: present in both', 'd'), HK, 13, '1', ''),
 ('O2u-14', O, '§2u', '-', 'cell b CI low +0.022', 0.022, FP, lambda: g(FP, 'contrasts', 'present', '1.7B K3-K0 | MAIN 97', 'b: present in both', 'ci')[0], HK, 13, '1', ''),
 ('O2u-15', O, '§2u', '-', 'cell b CI high +0.093', 0.093, FP, lambda: g(FP, 'contrasts', 'present', '1.7B K3-K0 | MAIN 97', 'b: present in both', 'ci')[1], HK, 13, '1', ''),
 ('O2u-16', O, '§2u', '-', 'cell b n 13', 13, FP, lambda: g(FP, 'contrasts', 'present', '1.7B K3-K0 | MAIN 97', 'b: present in both', 'n'), HK, 13, '1', ''),
 ('O2u-17', O, '§2u', '-', 'MAIN 92 keyed', 92, FP, lambda: g(FP, 'keyed', 'MAIN'), NA, 92, NA, ''),
 ('O2u-18', O, '§2u', 'H', 'INPACK K3-K0 -0.023', -0.023, IS, lambda: g(IS, 'matching_pack_MAIN', 'K3-K0 on health+firstaid+country (pack added by K3)', 'd'), HK, 17, '1', ''),
 ('O2u-19', O, '§2u', 'H', 'INPACK CI low -0.081', -0.081, IS, lambda: g(IS, 'matching_pack_MAIN', 'K3-K0 on health+firstaid+country (pack added by K3)', 'ci')[0], HK, 17, '1', ''),
 ('O2u-20', O, '§2u', 'H', 'INPACK CI high +0.027', 0.027, IS, lambda: g(IS, 'matching_pack_MAIN', 'K3-K0 on health+firstaid+country (pack added by K3)', 'ci')[1], HK, 17, '1', ''),
 ('O2u-21', O, '§2u', '-', 'INPACK n 17', 17, IS, lambda: g(IS, 'matching_pack_MAIN', 'K3-K0 on health+firstaid+country (pack added by K3)', 'n'), HK, 17, '1', ''),
 ('O2u-22', O, '§2u', '-', '4B in-pack minus off-pack -0.081', -0.081, IS, lambda: g(IS, 'sets', 'MAIN 97', '4B K0 s42', 'gap'), HK, 97, '1', ''),
 ('O2u-23', O, '§2u', '-', 'ORACLE U 0.427', 0.427, OR, lambda: g(OR, 'U', 'oracle'), HK, 30, '1', ''),
 ('O2u-24', O, '§2u', '-', 'ORACLE control U 0.412', 0.412, OR, lambda: g(OR, 'U', 'ctl_mini'), HK, 30, '1', ''),
 ('O2u-25', O, '§2u', 'H', 'ORACLE +0.015', 0.015, OR, lambda: g(OR, 'dU_oracle_minus_ctl_mini', 'd'), HK, 30, '1', ''),
 ('O2u-26', O, '§2u', 'H', 'ORACLE CI low -0.029', -0.029, OR, lambda: g(OR, 'dU_oracle_minus_ctl_mini', 'ci')[0], HK, 30, '1', ''),
 ('O2u-27', O, '§2u', 'H', 'ORACLE CI high +0.059', 0.059, OR, lambda: g(OR, 'dU_oracle_minus_ctl_mini', 'ci')[1], HK, 30, '1', ''),
 ('O2u-28', O, '§2u', '-', '= 10 % of the self-test gain', 0.10, OR + ' / ' + FP, lambda: g(OR, 'dU_oracle_minus_ctl_mini', 'd') / g(FP, 'contrasts', 'oracle (self-tests, fact chunk id kept)', '1.7B K3-K0 | self-tests topical 60', 'a: present in K3 only', 'd'), HK, NA, NA, 'derived 0.015/0.139 = 0.108 (11 %); vs LITEPACKS +0.069 it is 22 %'),
 ('O2u-29', O, '§2u', '-', 'ORACLE n 30', 30, OR, lambda: g(OR, 'n'), HK, 30, '1', ''),
 ('O2u-30', O, '§2u', '-', 'ORACLE 98 Haiku calls', 98, 'arms/oracle-real/judgments', lambda: count_rows('rnd/research/coordinator/arms/oracle-real/judgments/*.judgments.jsonl'), HK, NA, NA, 'row count'),
 ('O2u-31', O, '§2u', '-', 'clean key-fact chunks +0.106', 0.106, OR, lambda: g(OR, 'subgroups', 'gold manual', 'd'), HK, 6, '1', 'post-hoc'),
 ('O2u-32', O, '§2u', '-', 'clean chunks CI low +0.054', 0.054, OR, lambda: g(OR, 'subgroups', 'gold manual', 'ci')[0], HK, 6, '1', ''),
 ('O2u-33', O, '§2u', '-', 'clean chunks CI high +0.159', 0.159, OR, lambda: g(OR, 'subgroups', 'gold manual', 'ci')[1], HK, 6, '1', ''),
 ('O2u-34', O, '§2u', '-', 'lexical golds -0.009', -0.009, OR, lambda: g(OR, 'subgroups', 'gold lexical', 'd'), HK, NA, '1', ''),
 ('O2u-35', O, '§2u', '-', 'Jaccard median real 0.053', 0.053, PK3, lambda: g(PK3, 'overlap', 'J', 'real', 'median'), NA, 37, NA, ''),
 ('O2u-36', O, '§2u', '-', 'Jaccard median self-tests 0.045', 0.045, PK3, lambda: g(PK3, 'overlap', 'J', 'cand80', 'median'), NA, 80, NA, ''),
 ('O2u-37', O, '§2u', '-', 'reweighted 1.7B gain +0.064', 0.064, PK3, lambda: g(PK3, 'primary', 'reweighted', 'd'), HK, 80, '1', ''),
 ('O2u-38', O, '§2u', '-', 'reweighted CI low +0.035', 0.035, PK3, lambda: g(PK3, 'primary', 'reweighted', 'ci')[0], HK, 80, '1', ''),
 ('O2u-39', O, '§2u', '-', 'reweighted CI high +0.095', 0.095, PK3, lambda: g(PK3, 'primary', 'reweighted', 'ci')[1], HK, 80, '1', ''),
 ('O2u-40', O, '§2u', '-', 'Gemma reweighted +0.101', 0.101, PK3, lambda: g(PK3, 'secondary', 'Gemma cand80 J', 'reweighted', 'd'), HK, 80, '1', ''),
 ('O2u-41', O, '§2u', '-', '37 real golds', 37, PK3, lambda: g(PK3, 'n_real'), NA, 37, NA, ''),
]
for st, v in (('S1', 45), ('S2', 7), ('S3', 17), ('S4', 15), ('S5', 8)):
    M.append(('O2u-RF' + st, O, '§2u', '-', 'RAG-FUNNEL K3 MAIN keyed 92 ' + st, v, RAG, (lambda st=st: g(RAG, 'funnel', 'K3', 'MAIN keyed 92', 'stages', st)), HK + ' labels', 92, '1', ''))
M += [
 ('O2u-42', O, '§2u', '-', 'S1 of which cooking/money 39', 39, RAG, lambda: g(RAG, 'funnel', 'K3', 'cm 40', 'stages', 'S1'), HK, 40, '1', ''),
]
for tier, cells in (('q17', (('K0', 0.381), ('K3mb', 0.462), ('KA', 0.435))), ('gem', (('K0', 0.395), ('K3', 0.497), ('KA', 0.450))), ('q4b', (('K0', 0.461), ('K3', 0.545), ('KA', 0.513)))):
    for cell, v in cells:
        M.append(('O2u-MX-%s-%s' % (tier, cell), O, '§2u', '-', 'MATRIX U %s-%s on 80' % (tier, cell), v, MX, (lambda tier=tier, cell=cell: g(MX, 'slices', 'all80', 'cells', '%s-%s' % (tier, cell), 'U')), HK, 80, '1', ''))
_KA = lambda: [g(MX, 'slices', 'all80', 'dU_vs_K0', k) for k in ('q17-KA (mini pair)', 'gem-KA', 'q4b-KA')]
M += [
 ('O2u-43', O, '§2u', '-', 'KA-K0 low end +0.052', 0.052, MX, lambda: min(x['d'] for x in _KA()), HK, 80, '1', ''),
 ('O2u-44', O, '§2u', '-', 'KA-K0 high end +0.055', 0.055, MX, lambda: max(x['d'] for x in _KA()), HK, 80, '1', ''),
 ('O2u-45', O, '§2u', '-', 'KA-K0 all CI low > 0 (1 = yes)', 1, MX, lambda: int(all(x['ci'][0] > 0 for x in _KA())), HK, 80, '1', 'boolean'),
 ('O2u-46', O, '§2u', '-', '4B-1.7B ~ +0.08 at every pack set (mean of K0/K3/KA)', 0.08, MX, lambda: statistics.mean([g(MX, 'slices', 'all80', 'cells', 'q4b-K0', 'U') - g(MX, 'slices', 'all80', 'cells', 'q17-K0', 'U'), g(MX, 'slices', 'all80', 'cells', 'q4b-K3', 'U') - g(MX, 'slices', 'all80', 'cells', 'q17-K3mb', 'U'), g(MX, 'slices', 'all80', 'cells', 'q4b-KA', 'U') - g(MX, 'slices', 'all80', 'cells', 'q17-KA', 'U')]), HK, 80, '1', 'cells: +0.080 / +0.083 / +0.078'),
 ('O2u-47', O, '§2u', '-', 'MATRIX 652 Haiku calls', 652, 'arms/coverage-matrix/*/judgments', lambda: count_rows('rnd/research/coordinator/arms/coverage-matrix/*/judgments/*.judgments.jsonl'), HK, NA, NA, 'row count of judgments.jsonl files (MATRIX.md l.43 itemises 652)'),
 ('O2u-48', O, '§2u', '-', 'A-union MAIN CE-unwarned rate diff +0.052', 0.052, MX, lambda: g(MX, 'MAIN97_noharm', 'dCEu_rate', 'd'), HK, 97, '1', ''),
 ('O2u-49', O, '§2u', '-', 'CE rate diff CI low -0.010', -0.010, MX, lambda: g(MX, 'MAIN97_noharm', 'dCEu_rate', 'ci')[0], HK, 97, '1', ''),
 ('O2u-50', O, '§2u', '-', 'CE rate diff CI high +0.113', 0.113, MX, lambda: g(MX, 'MAIN97_noharm', 'dCEu_rate', 'ci')[1], HK, 97, '1', ''),
 ('O2u-51', O, '§2u', 'H', 'A-union retrieval +2.4 s p50 (dup of O2-68)', 2.4, 'arms/aunion-pixel', None, NA, 73, '1', 'baseline side has no JSON field'),
 ('O2u-52', O, '§2u', '-', 'baseline retrieval p50 1.5-1.6 s', 1.5, 'arms/aunion-pixel/AUNION-PIXEL.md', None, NA, 73, '1', 'prose only'),
 ('O2u-53', O, '§2u', '-', 'A-union retrieval p50 low end 3.9 s', 3.9, AU, lambda: min(g(AU % r, 'retrieval_ms_p50') for r in ('aunion10-a', 'aunion73-a')) / 1e3, NA, 73, '1', '1.7B runs (aunion10-a 3.90, aunion73-a 3.99); Gemma and 4B A-union runs are 4.2-4.3 s, outside the quoted range'),
 ('O2u-54', O, '§2u', '-', 'A-union retrieval p50 high end 4.0 s', '4.0', AU, lambda: max(g(AU % r, 'retrieval_ms_p50') for r in ('aunion10-a', 'aunion73-a')) / 1e3, NA, 73, '1', '1.7B runs'),
 ('O2u-54b', O, '§2u', '-', 'A-union retrieval p50 on the other tiers (implied 3.9-4.0)', '4.0', AU, lambda: max(g(AU % r, 'retrieval_ms_p50') for r in ('gemmaa73-a', 'q4ba73-a')) / 1e3, NA, 73, '1', 'Gemma 4.41 s / 4B 4.25 s A-union runs; the outline range 3.9-4.0 is 1.7B-only'),
 ('O2u-55', O, '§2u', '-', 'A-union retrieval max 10.7 s', 10.7, AU % 'aunion73-a', lambda: g(AU % 'aunion73-a', 'retrieval_ms_max') / 1e3, NA, 73, '1', '1.7B run; 4B run max 11.1 s'),
 ('O2u-56', O, '§2u', '-', 'A-union answer p50 +3.4 s (dup)', 3.4, AUR % 'aunion73-a', lambda: phone(AUR % 'aunion73-a', 'totalLatencyMs') - phone(PH % 'q17b73-a', 'totalLatencyMs'), NA, 73, '1', ''),
 ('O2u-57', O, '§2u', '-', '1.7B PSS A-union 3.41', 3.41, AU % 'aunion73-a', lambda: g(AU % 'aunion73-a', 'pss_peak_gb'), NA, 73, '1', ''),
 ('O2u-58', O, '§2u', '-', '1.7B PSS base 3.39', 3.39, 'ruler/SPEED-PRECHECK-2026-10-21.json', lambda: speed('q17b73-a', 'pss_peak_gb'), NA, 73, '1', ''),
 ('O2u-59', O, '§2u', '-', 'Gemma PSS A-union 4.38', 4.38, AU % 'gemmaa73-a', lambda: g(AU % 'gemmaa73-a', 'pss_peak_gb'), NA, 73, '1', ''),
 ('O2u-60', O, '§2u', '-', 'Gemma PSS base 4.52', 4.52, 'ruler/SPEED-PRECHECK-2026-10-21.json', lambda: speed('gemma73-a', 'pss_peak_gb'), NA, 73, '1', ''),
 ('O2u-61', O, '§2u', '-', '4B PSS A-union 4.76', 4.76, AU % 'q4ba73-a', lambda: g(AU % 'q4ba73-a', 'pss_peak_gb'), NA, 73, '1', ''),
 ('O2u-62', O, '§2u', '-', '4B PSS base 4.92', 4.92, 'ruler/SPEED-PRECHECK-2026-10-21.json', lambda: speed('final-cut7-v01', 'pss_peak_gb'), NA, 72, '1', ''),
 ('O2u-63', O, '§2u', '-', '0 LMK on all three tiers', 0, AU, lambda: sum(g(AU % r, 'lmk_kills') for r in ('aunion73-a', 'gemmaa73-a', 'q4ba73-a')), NA, 73, '1', ''),
 ('O2u-64', O, '§2u', '-', '~0.15 s per small pack', 0.15, 'arms/aunion-pixel/AUNION-PIXEL.md', None, NA, NA, NA, 'prose only (sql_ms_by_db is a sum, not per query)'),
 ('O2u-65', O, '§2u', '-', 'PK-5 kept-source identity 81/97', 81, 'arms/aunion-pixel/AUNION-PIXEL.md (replay)', None, NA, 97, NA, 'no JSON field'),
 ('O2u-66', O, '§2u', '-', 'PK-5 identity 83.5 %', 0.835, 'derived 81/97', lambda: 81 / 97, NA, 97, NA, 'arithmetic only'),
 ('O2u-67', O, '§2u', '-', 'PK-5 merged U 0.365', 0.365, PK5, lambda: g(PK5, 'summary', 'U'), HK, 16, '1', ''),
 ('O2u-68', O, '§2u', '-', 'PK-5 control U 0.399', 0.399, PK5, lambda: g(PK5, 'summary', 'U') - g(PK5, 'vs_control', 'deltas', 'U', 'd'), HK, 16, '1', 'derived merged - delta'),
 ('O2u-69', O, '§2u', '-', 'PK-5 -0.034', -0.034, PK5, lambda: g(PK5, 'vs_control', 'deltas', 'U', 'd'), HK, 16, '1', ''),
 ('O2u-70', O, '§2u', '-', 'PK-5 16 items', 16, PK5, lambda: g(PK5, 'n'), HK, 16, '1', ''),
 ('O2u-71', O, '§2u', '-', 'PK-5 38 Haiku', 38, 'arms/aunion-pixel/pk5/judgments', lambda: count_rows('rnd/research/coordinator/arms/aunion-pixel/pk5/judgments/*.judgments.jsonl'), HK, NA, NA, 'row count'),
 # ---------- PLAN §1 ----------
 ('P1-01', P, '§1', 'H', 'gap 0.586', 0.586, 'arms/lossmap/aggregates/lossmap-K-vpara-s42.json', lambda: lossmap()['gap'], 'Opus rows + jev labels', 51, 's42', '1 - mean item ratio'),
 ('P1-02', P, '§1', 'H', 'wrong from memory share 0.167', 0.167, 'lossmap-K-vpara-s42.json', lambda: lossmap()['groups']['wrong_nosrc'][1], 'Opus + jev', 51, 's42', 'wrong & labels.source_on_topic false'),
 ('P1-03', P, '§1', '-', 'wrong from memory items 12', 12, 'lossmap-K-vpara-s42.json', lambda: lossmap()['groups']['wrong_nosrc'][0], 'Opus + jev', 51, 's42', ''),
 ('P1-04', P, '§1', 'H', 'absent knowledge share 0.239', 0.239, 'lossmap-K-vpara-s42.json', lambda: lossmap()['groups']['absent_knowledge'][1], 'Opus + jev', 51, 's42', ''),
 ('P1-05', P, '§1', '-', 'absent knowledge items 24', 24, 'lossmap-K-vpara-s42.json', lambda: lossmap()['groups']['absent_knowledge'][0], 'Opus + jev', 51, 's42', ''),
 ('P1-06', P, '§1', 'H', 'misread (on-topic source) share 0.142', 0.142, 'lossmap-K-vpara-s42.json', lambda: lossmap()['groups']['wrong_src'][1], 'Opus + jev', 51, 's42', ''),
 ('P1-07', P, '§1', '-', 'misread items 11', 11, 'lossmap-K-vpara-s42.json', lambda: lossmap()['groups']['wrong_src'][0], 'Opus + jev', 51, 's42', ''),
 ('P1-08', P, '§1', '-', 'thin share 0.038', 0.038, 'lossmap-K-vpara-s42.json', lambda: lossmap()['groups']['thin'][1], 'Opus + jev', 51, 's42', ''),
 ('P1-09', P, '§1', '-', 'thin items 4', 4, 'lossmap-K-vpara-s42.json', lambda: lossmap()['groups']['thin'][0], 'Opus + jev', 51, 's42', ''),
 ('P1-10', P, '§1', '-', 'refusals/truncation 0', 0, 'lossmap-K-vpara-s42.json', lambda: sum(1 for i in J('rnd/research/coordinator/arms/lossmap/aggregates/lossmap-K-vpara-s42.json')['items'] if i.get('declined')), 'Opus + jev', 51, 's42', 'declined items'),
 ('P1-11', P, '§1', '-', 'kit 6/51 (dup O2-70)', 6, 'VPARA-DIAGNOSIS / PACKCOND-P1', None, 'jev', 51, NA, ''),
 ('P1-12', P, '§1', '-', 'all packs 10/51 (dup O2-71)', 10, 'VPARA-DIAGNOSIS / PACKCOND-P2', None, 'jev', 51, NA, ''),
 ('P1-13', P, '§1', '-', 'full Wikipedia 9/34', 9, WF, lambda: g(WF, 'vpara', 'by_group', 'ALL', 'verified'), 'jev', 34, NA, ''),
 ('P1-14', P, '§1', '-', 'absent items 34', 34, WF, lambda: g(WF, 'vpara', 'by_group', 'ALL', 'n'), 'jev', 34, NA, ''),
 ('P1-15', P, '§1', '-', 'no kept source 29/51', 29, 'lossmap-K-vpara-s42.json', lambda: lossmap()['nokept_n'], 'Opus + jev', 51, 's42', 'n_kept == 0'),
 ('P1-16', P, '§1', '-', 'those carry 58 % of the loss', 0.58, 'lossmap-K-vpara-s42.json', lambda: lossmap()['nokept_share'], 'Opus + jev', 51, 's42', ''),
 ('P1-17', P, '§1', 'H', 'ladder 4B 0.26 floor-adj', 0.26, DV, lambda: g(DV, 'floorK', 'above_min', 'point'), OP, 51, '2', ''),
 ('P1-18', P, '§1', 'H', 'ladder deep 0.33', 0.33, DV, lambda: g(DV, 'floorD', 'above_min', 'point'), OP, 51, '2', ''),
 ('P1-19', P, '§1', 'H', 'ladder deep + think 512 0.44', 0.44, DT, lambda: g(DT, 'H', 'above_min', 'point'), OP, 51, '2', ''),
 ('P1-20', P, '§1', '-', '1.7B = 4B - 0.07..0.11', 0.07, 'CRITIQUE-2026-10-16 (md)', None, HK, NA, NA, 'prose only'),
 ('P1-21', P, '§1', '-', 'Codex +0.10 on each rung', 0.10, 'blind/V-para/runs-xfam (XFAM-REPORT.md; off-limits here)', None, 'Codex gpt-5.6-sol', 51, '2', 'blind-only source: coordinator must re-derive'),
 ('P1-22', P, '§1', 'H', 'deep + think Codex 0.577', 0.577, 'blind/V-para/runs-xfam', None, 'Codex gpt-5.6-sol', 51, '2', 'blind-only source'),
 ('P1-23', P, '§1', '-', 'win-rate ~0 everywhere', 0, 'CLAIM-RESULTS-cut6 / XFAM (md, blind)', None, 'both', NA, NA, 'prose only'),
 ('P1-24', P, '§1', '-', '+0.03 reading (DEEPREAD)', 0.03, 'arms/deepread (md)', None, OP, NA, NA, 'prose only'),
 # PLAN §1 05:xx update
 ('P1u-01', P, '§1u', 'H', 'gate visible CE 7 (Opus)', 7, RU, lambda: g(RU, 'ceu_C'), OP, 177, '1', ''),
 ('P1u-02', P, '§1u', 'H', 'gate visible CE 3 (Opus)', 3, RU, lambda: g(RU, 'ceu_R'), OP, 177, '1', ''),
 ('P1u-03', P, '§1u', '-', 'of 177', 177, RU, lambda: g(RU, 'n'), OP, 177, '1', ''),
 ('P1u-04', P, '§1u', '-', 'Haiku was 10 -> 4', 10, 'arms/refuse-unsupported/ce-opus-ru/ceopusru-haiku.json', lambda: g('rnd/research/coordinator/arms/refuse-unsupported/ce-opus-ru/ceopusru-haiku.json', 'ceu_C'), HK, 177, '1', ''),
 ('P1u-05', P, '§1u', '-', 'Haiku 4', 4, 'arms/refuse-unsupported/ce-opus-ru/ceopusru-haiku.json', lambda: g('rnd/research/coordinator/arms/refuse-unsupported/ce-opus-ru/ceopusru-haiku.json', 'ceu_R'), HK, 177, '1', ''),
 ('P1u-06', P, '§1u', '-', 'FR 0/14', 0, RU, lambda: g(RU, 'fr_k'), OP, 14, '1', ''),
 ('P1u-07', P, '§1u', '-', 'FR denominator 14', 14, RU, lambda: g(RU, 'fr_n'), OP, 14, '1', ''),
 ('P1u-08', P, '§1u', '-', '6 Opus-correct answers refused', 6, RU, lambda: g(RU, 'refused_corr_ge4'), OP, 177, '1', ''),
 ('P1u-09', P, '§1u', '-', 'fact-added real -0.010 (dup)', -0.010, FP, lambda: g(FP, 'contrasts', 'present', '1.7B K3-K0 | MAIN 97', 'a: present in K3 only', 'd'), HK, 10, '1', ''),
 ('P1u-10', P, '§1u', '-', 'self-tests +0.139 (dup)', 0.139, FP, lambda: g(FP, 'contrasts', 'oracle (self-tests, fact chunk id kept)', '1.7B K3-K0 | self-tests topical 60', 'a: present in K3 only', 'd'), HK, 27, '1', ''),
 ('P1u-11', P, '§1u', '-', 'matching pack -0.023 (dup)', -0.023, IS, lambda: g(IS, 'matching_pack_MAIN', 'K3-K0 on health+firstaid+country (pack added by K3)', 'd'), HK, 17, '1', ''),
 ('P1u-12', P, '§1u', '-', 'oracle +0.015 (dup)', 0.015, OR, lambda: g(OR, 'dU_oracle_minus_ctl_mini', 'd'), HK, 30, '1', ''),
 ('P1u-13', P, '§1u', '-', 'oracle CI low -0.029 (dup)', -0.029, OR, lambda: g(OR, 'dU_oracle_minus_ctl_mini', 'ci')[0], HK, 30, '1', ''),
 ('P1u-14', P, '§1u', '-', 'oracle CI high +0.059 (dup)', 0.059, OR, lambda: g(OR, 'dU_oracle_minus_ctl_mini', 'ci')[1], HK, 30, '1', ''),
 ('P1u-15', P, '§1u', '-', '1.7B-1.5B +0.040 (dup)', 0.040, RV2, lambda: g(RV2, 'primary_51', 'pairs', 'L1-L0', 'dU'), HK, 51, '2', ''),
 ('P1u-16', P, '§1u', '-', 'CI low -0.019 (dup)', -0.019, RV2, lambda: g(RV2, 'primary_51', 'pairs', 'L1-L0', 'dU_ci')[0], HK, 51, '2', ''),
 ('P1u-17', P, '§1u', '-', 'CI high +0.096 (dup)', 0.096, RV2, lambda: g(RV2, 'primary_51', 'pairs', 'L1-L0', 'dU_ci')[1], HK, 51, '2', ''),
 ('P1u-18', P, '§1u', 'H', '4B over Gemma +0.117', 0.117, RV2, lambda: g(RV2, 'primary_51', 'pairs', 'L3-L2', 'dU'), HK, 51, '2', ''),
]


def decimals(v):
    if isinstance(v, str):
        return len(v.split('.')[1]) if '.' in v else 0
    s = repr(float(v))
    if 'e' in s:
        return 6
    s = s.rstrip('0')
    return max(0, len(s.split('.')[1])) if '.' in s else 0


def run():
    out = []
    for (eid, doc, sec, tag, quote, val, src, fn, judge, n, seeds, note) in M:
        dec = decimals(val)
        val = float(val)
        rec = dict(id=eid, doc=doc, section=sec, headline=(tag == 'H'), quote=quote, doc_value=val, source=src,
                   judge=judge, n=n, seeds=seeds, note=note, recomputed=None, status=None, diff=None)
        if fn is None:
            rec['status'] = 'UNSOURCED'
        else:
            try:
                x = fn()
                if x is None:
                    rec['status'] = 'UNSOURCED'
                    rec['note'] = (note + '; key absent').strip('; ')
                else:
                    x = float(x)
                    d = dec
                    rec['recomputed'] = round(x, 4)
                    rec['diff'] = round(round(x, d) - val, 4)
                    rec['status'] = 'MATCH' if abs(round(x, d) - val) <= 0.001 + 1e-9 else 'MISMATCH'
            except FileNotFoundError as e:
                rec['status'] = 'MISSING-SRC'
                rec['note'] = (note + '; ' + str(e)).strip('; ')
            except (KeyError, IndexError, TypeError) as e:
                rec['status'] = 'MISSING-SRC'
                rec['note'] = (note + '; key error ' + repr(e)).strip('; ')
        out.append(rec)
    return out


def summary(out):
    s = {}
    for r in out:
        s[r['status']] = s.get(r['status'], 0) + 1
    checked = s.get('MATCH', 0) + s.get('MISMATCH', 0)
    s['total'] = len(out)
    s['checked'] = checked
    s['mismatch_rate_of_checked'] = round(s.get('MISMATCH', 0) / checked, 4) if checked else None
    s['unsourced_rate_of_total'] = round((s.get('UNSOURCED', 0) + s.get('MISSING-SRC', 0)) / len(out), 4)
    s['headline_mismatch'] = [r['id'] for r in out if r['headline'] and r['status'] == 'MISMATCH']
    s['headline_unsourced'] = [r['id'] for r in out if r['headline'] and r['status'] in ('UNSOURCED', 'MISSING-SRC')]
    return s


if __name__ == '__main__':
    out = run()
    s = summary(out)
    args = sys.argv[1:]
    if '--json' in args:
        p = args[args.index('--json') + 1]
        json.dump({'criterion': 'ruler/CV5-criterion.md', 'summary': s, 'numbers': out}, open(p, 'w'), indent=1)
    if '--table' in args:
        p = args[args.index('--table') + 1]
        with open(p, 'w') as f:
            f.write('| id | doc | sec | H | number | doc | recomputed | status | judge | n | seeds | source | note |\n|---|---|---|---|---|---|---|---|---|---|---|---|---|\n')
            for r in out:
                f.write('| %s | %s | %s | %s | %s | %s | %s | %s | %s | %s | %s | %s | %s |\n' % (
                    r['id'], r['doc'], r['section'], 'H' if r['headline'] else '', r['quote'].replace('|', '/'), ('%g' % r['doc_value']),
                    '' if r['recomputed'] is None else ('%g' % r['recomputed']), r['status'], r['judge'], r['n'], r['seeds'],
                    r['source'].replace('rnd/research/coordinator/', '').replace('|', '/'), r['note'].replace('|', '/')))
    for r in out:
        if r['status'] != 'MATCH':
            print('%-12s %-10s doc=%s rec=%s | %s | %s' % (r['id'], r['status'], r['doc_value'], r['recomputed'], r['quote'], r['note']))
    print(json.dumps(s))
