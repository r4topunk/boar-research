# SFT4B stage 1 step 4: pin the chat template to Qwen's original and run the gate.
# usage: python s4_template.py <mlx8 dir> <base-config dir> <train.jsonl>  -> prints JSON, exit 0 only if PASS
import hashlib, json, sys, pathlib
M, B, T = map(pathlib.Path, sys.argv[1:4])
sha = lambda b: hashlib.sha256(b).hexdigest()
tc = json.loads((B / "tokenizer_config.json").read_bytes())
tmpl = tc["chat_template"]
jinja = M / "chat_template.jinja"
old = jinja.read_bytes() if jinja.exists() else b""
jinja.write_text(tmpl)
out = {"tokenizer_config_sha": sha((B / "tokenizer_config.json").read_bytes()), "old_jinja_sha": sha(old),
       "new_jinja_sha": sha(jinja.read_bytes()), "template_sha": sha(tmpl.encode())}
# also make sure tokenizer_config.json in M does not carry a different chat_template
mtc_p = M / "tokenizer_config.json"
mtc = json.loads(mtc_p.read_bytes())
if "chat_template" in mtc and mtc["chat_template"] != tmpl:
    mtc["chat_template"] = tmpl; mtc_p.write_text(json.dumps(mtc, indent=2, ensure_ascii=False)); out["mlx_tokenizer_config_patched"] = True
from mlx_lm.utils import load_tokenizer
tok = load_tokenizer(M)
ex = json.loads(T.open().readline())["messages"]
ans = ex[-1]["content"]
full = tok.apply_chat_template(ex, tokenize=False)
prompt = tok.apply_chat_template(ex[:-1], tokenize=False, add_generation_prompt=True)
target = full[len(prompt) - len("<|im_start|>assistant\n"):] if full.startswith(prompt) else None
ids_full = tok.apply_chat_template(ex, return_dict=False); ids_prompt = tok.apply_chat_template(ex[:-1], add_generation_prompt=True, return_dict=False)
tgt_ids_text = tok.decode(ids_full[len(ids_prompt):])
out.update({
  "no_think": "<think>" not in full,
  "prompt_is_prefix": full.startswith(prompt),
  "prompt_ends_gen": prompt.endswith("<|im_start|>assistant\n"),
  "target_exact": target in ("<|im_start|>assistant\n" + ans + "<|im_end|>", "<|im_start|>assistant\n" + ans + "<|im_end|>\n"),
  "target_repr": repr(target[:40] + " … " + target[-20:]) if target else None,
  "trained_tokens_text_tail": repr(tgt_ids_text[-25:]),
  "trained_text_eq_answer_im_end": tgt_ids_text.rstrip("\n") == ans + "<|im_end|>",
  "token_prefix_ok": ids_full[:len(ids_prompt)] == ids_prompt,
})
out["PASS"] = all(out[k] for k in ("no_think", "prompt_is_prefix", "prompt_ends_gen", "target_exact", "trained_text_eq_answer_im_end", "token_prefix_ok"))
print(json.dumps(out, indent=1)); sys.exit(0 if out["PASS"] else 2)
