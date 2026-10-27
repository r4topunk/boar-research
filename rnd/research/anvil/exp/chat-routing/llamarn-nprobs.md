# llama.rn 0.13.0-rc.4 `n_probs`: desk-check (Anvil, 2026-10-02)

**TL;DR:** rc.4 reports **post-sampling** probabilities, and the classic `completion()` path returns **stale** probabilities from the 2nd call on (issue #401; both confirmed in the code we ship). The B4 gate at threshold 0.5 still works on rc.4 with 3 workarounds, so it doesn't need an rc.5 bump. A bump becomes worthwhile only for a calibrated threshold other than 0.5.

Source read: `boar-app/node_modules/llama.rn` (0.13.0-rc.4, the version locked in boar-app `package-lock.json` at 0cfd4a77); rc.5 from `npm pack llama.rn@0.13.0-rc.5`; issue text from `gh api repos/mybigday/llama.rn/issues/401` (closed, "Released v0.13.0-rc.5").

## Findings (rc.4)

| # | Claim | Evidence (rc.4 file:line) |
|---|---|---|
| 1 | Probabilities are read **after** the sampler chain | `cpp/rn-completion.cpp:1635-1643`: `common_sampler_sample(...)`, then `common_sampler_get_candidates(ctx_sampling, true)` → `cur_p.data[i].p`. The same holds in the parallel path, `cpp/rn-slot-manager.cpp:1240-1245`. |
| 2 | Chain = logit_bias (if any) → `params.samplers` (penalties, dry, top_n_sigma, top_k, typical, top_p, min_p, xtc, temperature) → `dist` | `vendor/llama.cpp/common/sampling.cpp:336-415`. `dist` softmaxes over the **surviving** candidates and normalizes them all (`src/llama-sampler.cpp:1150-1214`). |
| 3 | Greedy (temperature ≤ 0) gives **one-hot** probabilities | `llama-sampler.cpp:270-285`: temp ≤ 0 sets every logit except the max to −inf, then `dist` → p = 1 / 0. The rc.4 docstring (`src/types.ts`, "probabilities still calculated via a simple softmax of the logits") is **wrong** for this code. |
| 4 | **Stale:** `generated_token_probs` is never cleared on the classic path | It is pushed in `rn-completion.cpp:1719-1722`; `rewind()` (`:34-64`) doesn't clear it; `JSICompletion.h:156` serializes the whole vector. So from the 2nd `completion()`, `completion_probabilities[0]` is the **first ever** call's token, and the array keeps growing. The parallel slot path clears it (`rn-slot.cpp:88`). |
| 5 | Sampling params are **sticky** on the context | `JSIParams.cpp:430-460`: each one defaults to the *previous* value (`getPropertyAsInt(params, "n_probs", sparams.n_probs)`, same for top_k / top_p / min_p / temperature). BOAR's `generate()` sets only `temperature`, `n_predict`, `stop` (`LlamaEngine.ts:509-528` @0cfd4a77). So a gate call's `n_probs` / top_k / … **leak into the next answer** unless they are reset. |
| 6 | `logit_bias` and `ignore_eos` crash natively (out-of-bounds vector write) | #401 item 1. BOAR uses neither (`git grep` @0cfd4a77: 0 hits). The gate must not use them. |
| 7 | Prompt tokens are **not** fed into the sampler | `rn-completion.cpp` loadPrompt comment: penalties see only generated tokens. Labels appearing in the gate's examples are not penalized. |

## rc.5 (2026-09-23)
- New `post_sampling_probs` completion param. **Its default is `true` (still post-sampling)**; `false` gives a softmax of the raw logits over the full vocabulary (`get_token_probabilities`, rc.5 `rn-completion.cpp:35-80`).
- Fixes the stale vector and the logit_bias crash (per #401). rc.6 also exists (2026-09-26); not read.
- The vendored `common/sampling.cpp` and `src/llama-sampler.cpp` are byte-identical to rc.4 (the probs diff is only in rn-* / JSI / types).

## Does the B4 gate need rc.5? **No, for threshold 0.5.**

Why the decision survives post-sampling: with both labels in the surviving set, p(S)/(p(S)+p(A)) = sigmoid((l_S − l_A)/T). This has the same sign as the raw logit gap for any T > 0. Truncation (top_k / top_p / min_p) can only drop the *lower* label, which yields 0 or 1 on the same side. Greedy gives one-hot argmax, also the same side whenever a label is the top token (desktop label mass ≥ 0.93). **So the 0.5 decision equals the raw-softmax decision. Only the score's calibration changes.**

Required rc.4 workarounds (they go in the engine patch):
1. **Read the fresh entry:** the last element of `completion_probabilities` (n_predict 1 → exactly one push per call, EOG included). If no label is in the top 20, fall back to SEARCH (the safe side).
2. **Reset sticky params:** every answer `completion()` passes `n_probs: 0`, and the gate passes only `n_probs` and `temperature`, never top_k / top_p / min_p. Then the answer sampling is unchanged: the answer always sets its own temperature, and top_k / top_p / min_p are never touched.
3. **Never** use `logit_bias` / `ignore_eos` / grammar for the gate.

Residual cost of the stale vector: +1 entry (20 probs) per gate call, serialized on every gate call (O(messages); ~1k msgs ≈ 20k small JSON objects). Negligible for a probe, but it is a real leak. It's a reason to take rc.5/rc.6 with the next planned dependency bump, not a blocker.

**When a bump would be needed:** a threshold other than 0.5 (the 1.5B's 0.05 search bias, or an "unsure band"). That needs raw scores, i.e. rc.5 with `post_sampling_probs: false`. With rc.4, raw scores come only from temperature 1 with all truncation disabled, and that is sticky (workaround 2 would then have to restore top_k 40 / top_p 0.95 / min_p 0.05 on every answer). Not worth it.

Device check (goes into the probe spec): the gate's decision on the device matches the desktop decision on 10 slice items, and the device score is one-hot or calibrated as predicted for the temperature used.
