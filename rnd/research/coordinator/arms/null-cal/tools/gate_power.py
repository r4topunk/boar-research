#!/usr/bin/env python3
"""GATE v2 calibration arithmetic (0 LLM). Usage: python3 -I gate_power.py   (numbers are the 4 null runs of arms/null-cal/arms/*/aggregates/*.gate2.json, typed below from those files)
Two noise models for the null net count: (a) binomial(P, p) with p = pooled null net rate of that pack set (upper bound on the variance: every item equally likely to flip),
(b) normal with the EMPIRICAL between-run sd (pooled over K0/K1, 2 df: optimistic, items are heterogeneous and only 2 draws per set).
A lever with extra effect d fixes a further share d of the problems the null does not fix: mean net = mu + d (P - mu)."""
import math
NULL = {"K0": dict(P=30, net=[6, 8]), "K1": dict(P=21, net=[6, 7])}
BAR = {k: max(v["net"]) + 2 for k, v in NULL.items()}
def btail(n, p, k): return sum(math.comb(n, j) * p**j * (1 - p)**(n - j) for j in range(k, n + 1))
def ntail(mu, sd, k): return 0.5 * math.erfc((k - 0.5 - mu) / (sd * math.sqrt(2)))
var = [sum((x - sum(v["net"]) / 2) ** 2 for x in v["net"]) for v in NULL.values()]; sd_emp = math.sqrt(sum(var) / len(var))  # pooled, 1 df each -> /2 sets
print(f"empirical pooled sd of null net = {sd_emp:.2f} (2 df)")
for k, v in NULL.items():
    P, mu = v["P"], sum(v["net"]) / 2; p = mu / P; bar = BAR[k]
    print(f"\n{k}: P={P} null net {v['net']} mean {mu:.1f} (rate {p:.3f}) bar = max+2 = {bar} ({bar / P:.0%} of problems)")
    print(f"  false GO under null: binomial {btail(P, p, bar):.3f} | normal(sd_emp) {ntail(mu, sd_emp, bar):.3f} | normal(sd binomial {math.sqrt(P * p * (1 - p)):.2f}) {ntail(mu, math.sqrt(P * p * (1 - p)), bar):.3f}")
    for d in (0.1, 0.2, 0.3, 0.4, 0.5):
        m = mu + d * (P - mu); pp = m / P
        print(f"  lever fixes extra {d:.0%} of the remaining problems (+{d * (P - mu):.1f} net): power binomial {btail(P, pp, bar):.2f} | normal(sd_emp) {ntail(m, sd_emp, bar):.2f}")
    for d in [x / 100 for x in range(5, 100, 5)]:
        if btail(P, (mu + d * (P - mu)) / P, bar) >= 0.8: print(f"  80% power (binomial) first reached at d = {d:.0%} = +{d * (P - mu):.1f} net fixes = {(mu + d * (P - mu)) / P:.0%} of problems"); break
