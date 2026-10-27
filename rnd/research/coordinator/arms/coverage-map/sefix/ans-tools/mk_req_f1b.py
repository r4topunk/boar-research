#!/usr/bin/env python3
"""F1b answer screen requests = ARM-G requests (compose/screen/req) with arm id cut7-headpass-x2+litepacks+f1b, settings packDense2 'extra' (packHeadPass a2 kept), kit shas of qa-cooking-se / qa-money-se = the v3 files. python3 -I mk_req_f1b.py"""
import json
A = "<workspace>/rnd/research/coordinator/arms/coverage-map"
V3 = {"qa-cooking-se": "79ed2699bccbb301965e48358352a120c7489622109e9eca0557076ee47a6678", "qa-money-se": "87e4a4cd2a0168b9f3895f566bcd256072958d1e4ae292113f284f224d2aeb4b"}
out = []
for l in open(A + "/compose/screen/req/cmp-G-K10-main-s42.requests.jsonl"):
    r = json.loads(l); r["runId"] = "f1b-main-s42"; c = r["config"]
    c["arm"] = "cut7-headpass-x2+litepacks+f1b"; c["settings"] = dict(c["settings"], packDense2="extra")
    for k in c["kit"]:
        if k["id"] in V3: k["sha256"] = V3[k["id"]]
    out.append(json.dumps(r))
open(A + "/sefix/ans-req/f1b-main-s42.requests.jsonl", "w").write("\n".join(out) + "\n")
print(len(out), json.loads(out[0])["config"]["settings"])
