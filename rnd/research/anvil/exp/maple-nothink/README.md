# Maple no-think template (Anvil, 2026-10-02 cycle 21)

- `maple-original.jinja`: `tokenizer.chat_template` read from the GGUF header of `deepgrove/maple-preview-GGUF` @ `f5466f918e` `maple-preview-TQ2_0-head-Q4_K.gguf` (20 MB range request; no model download). sha256 `83e4c58ca602ade89b126cc75a036eb8bd06d373d4fd94b09d2277d609131089`.
- `maple-nothink.jinja`: identical except the generation prompt, `<|im_start|>assistant\n<think>\n` → `<|im_start|>assistant\n<think>\n\n</think>\n\n` (an empty, closed think block: what Qwen3 renders for enable_thinking=false). sha256 `d31980a447791cb1a55c899960663c2544cfd444da8492b15510fcb9ccb5410a`.
- Use: llama-server `--chat-template-file maple-nothink.jinja` (boar-eval server backend); in the app, llama.rn completion param `chat_template` (per request, `node_modules/llama.rn/src/index.ts` ~278/440).
