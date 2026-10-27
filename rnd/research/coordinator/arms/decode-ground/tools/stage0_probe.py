#!/usr/bin/env python3
"""DECODE-GROUND stage 0: llama-server b11010 capability probe (token-id prompts, n_probs, cache_prompt, grammar, logit_bias, id_slot).
Usage: python3 -I stage0_probe.py <base url>   (prints one JSON object per check)"""
import json, sys, time, urllib.request
B = sys.argv[1].rstrip("/")
def post(path, body):
    r = urllib.request.Request(B + path, data=json.dumps(body).encode(), headers={"Content-Type": "application/json"})
    t = time.time(); j = json.loads(urllib.request.urlopen(r, timeout=600).read()); return j, (time.time() - t) * 1000
out = {}
msgs = [{"role": "system", "content": "You are a helpful assistant. " + " ".join(f"Fact {i}: the river number {i} flows north into lake {i*7}." for i in range(1, 120))},
        {"role": "user", "content": "Which way does river 12 flow? Answer in one sentence."}]
tpl, _ = post("/apply-template", {"messages": msgs, "chat_template_kwargs": {"enable_thinking": False}})
prompt = tpl["prompt"]; out["apply_template_tail"] = prompt[-60:]
tok, _ = post("/tokenize", {"content": prompt, "add_special": False, "parse_special": True})
ids = tok["tokens"]; out["prompt_tokens"] = len(ids)
det, _ = post("/detokenize", {"tokens": ids}); out["roundtrip_equal"] = det["content"] == prompt
# 1. token-id prompt + n_probs, pre vs post sampling
g = {"temperature": 0, "top_k": 1, "seed": 42, "n_probs": 40, "cache_prompt": True, "id_slot": 0}
r1, ms1 = post("/completion", {"prompt": ids, "n_predict": 1, **g})
cp = r1["completion_probabilities"][0]; tp = cp["top_logprobs"]
out["c1_first_call_ms"] = round(ms1); out["c1_keys"] = sorted(tp[0].keys()); out["c1_n_top"] = len(tp)
out["c1_top3"] = [(x["id"], x["token"], round(x["logprob"], 3)) for x in tp[:3]]
out["c1_sampled_is_argmax"] = cp["id"] == tp[0]["id"]
rp, _ = post("/completion", {"prompt": ids, "n_predict": 1, **g, "post_sampling_probs": True})
out["c1_post_sampling_top3"] = [(x["id"], x["token"], round(x.get("prob", x.get("logprob", 0)), 3)) for x in rp["completion_probabilities"][0].get("top_probs", rp["completion_probabilities"][0].get("top_logprobs", []))[:3]]
out["c1_post_sampling_n_top"] = sorted(rp["completion_probabilities"][0].keys())
r07, _ = post("/completion", {"prompt": ids, "n_predict": 1, "temperature": 0.7, "top_k": 40, "top_p": 0.95, "min_p": 0.05, "seed": 42, "n_probs": 40, "cache_prompt": True, "id_slot": 0})
out["c1_pre_sampling_same_at_t07"] = [x["logprob"] for x in r07["completion_probabilities"][0]["top_logprobs"][:5]] == [x["logprob"] for x in tp[:5]]
# 2. cache_prompt: token-by-token
seq = list(ids); times = []; gen = []
for k in range(12):
    r, ms = post("/completion", {"prompt": seq, "n_predict": 1, **g})
    t = r["completion_probabilities"][0]["id"]; seq.append(t); gen.append(t); times.append(round(ms, 1))
    out.setdefault("c2_cached", []).append(r.get("tokens_cached")); out.setdefault("c2_prompt_n", []).append(r["timings"]["prompt_n"])
out["c2_ms_per_call"] = times
full, _ = post("/completion", {"prompt": ids, "n_predict": 12, **g})
out["c2_tokbytok_equals_oneshot"] = post("/detokenize", {"tokens": gen})[0]["content"] == full["content"]
chat, _ = post("/v1/chat/completions", {"messages": msgs, "max_tokens": 12, "temperature": 0, "top_k": 1, "seed": 42, "chat_template_kwargs": {"enable_thinking": False}, "cache_prompt": False})
out["c2_chat_equals_tokenid"] = chat["choices"][0]["message"]["content"] == full["content"]; out["c2_chat_prompt_tokens"] = chat["usage"]["prompt_tokens"]
# 3. grammar: ~30 literal sentences + NO_EVIDENCE
sents = [f'River {i} flows "north" into lake {i*7} — naïve café №{i}.' for i in range(1, 30)]
esc = lambda s: '"' + s.replace("\\", "\\\\").replace('"', '\\"') + '"'
gram = "root ::= " + " | ".join(esc(s) for s in sents + ["NO_EVIDENCE"])
um = [{"role": "user", "content": "Question: Which way does river 12 flow?\nSentences:\n" + "\n".join(f"{i+1}. {s}" for i, s in enumerate(sents)) + "\nCopy the one sentence that answers the question, or NO_EVIDENCE."}]
gr, msg = post("/v1/chat/completions", {"messages": um, "max_tokens": 80, "temperature": 0, "grammar": gram, "chat_template_kwargs": {"enable_thinking": False}})
c = gr["choices"][0]["message"]["content"]; out["c3_output"] = c; out["c3_exact_alternative"] = c in sents + ["NO_EVIDENCE"]; out["c3_ms"] = round(msg)
um2 = [{"role": "user", "content": "Question: What is the capital of France?\nSentences:\n" + "\n".join(f"{i+1}. {s}" for i, s in enumerate(sents)) + "\nCopy the one sentence that answers the question, or NO_EVIDENCE."}]
gr2, _ = post("/v1/chat/completions", {"messages": um2, "max_tokens": 80, "temperature": 0, "grammar": gram, "chat_template_kwargs": {"enable_thinking": False}})
out["c3_offtopic_output"] = gr2["choices"][0]["message"]["content"]
# 4. logit_bias
tgt = tp[1]["id"]
lb, _ = post("/completion", {"prompt": ids, "n_predict": 1, **g, "logit_bias": [[tgt, 30.0]]})
out["c4_logit_bias_forces_second"] = lb["completion_probabilities"][0]["id"] == tgt
lb0, _ = post("/completion", {"prompt": ids, "n_predict": 1, **g, "logit_bias": [[tp[0]["id"], False]]})
out["c4_ban_first"] = lb0["completion_probabilities"][0]["id"] != tp[0]["id"]
# 5. id_slot: alternate two prompts on two slots, both stay cached
ids_b = post("/tokenize", {"content": post("/apply-template", {"messages": [msgs[1]], "chat_template_kwargs": {"enable_thinking": False}})[0]["prompt"], "add_special": False, "parse_special": True})[0]["tokens"]
post("/completion", {"prompt": ids_b, "n_predict": 1, **{**g, "id_slot": 1}})
alt = []
sa, sb = list(ids), list(ids_b)
for k in range(4):
    ra, ma = post("/completion", {"prompt": sa, "n_predict": 1, **g}); sa.append(ra["completion_probabilities"][0]["id"])
    rb, mb = post("/completion", {"prompt": sb, "n_predict": 1, **{**g, "id_slot": 1}}); sb.append(rb["completion_probabilities"][0]["id"])
    alt.append((ra["timings"]["prompt_n"], round(ma), rb["timings"]["prompt_n"], round(mb)))
out["c5_alternating_promptn_ms"] = alt
print(json.dumps(out, ensure_ascii=False, indent=1))
