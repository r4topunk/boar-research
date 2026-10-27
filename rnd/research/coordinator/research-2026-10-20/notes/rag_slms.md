# Small LMs (<= 3B) trained for grounded RAG / citations / faithfulness: notes

Date: 2026-10-20. Angle: SLMs trained or fine-tuned for grounded RAG with citations or context faithfulness, permissive licence, GGUF availability, numbers vs Qwen3-1.7B or similar.
Scope of this pass: 13 searches (standard mode), 14 page fetches. Primary pages opened are marked [opened]. Items marked [snippet] come from a search result only and were not opened.

## Context for reading the numbers

- BOAR's walls (from the task text): reading wall (the 1.7B receives general-pack text but does not use it), 28 % confident errors, prompt fixes closed <= 2 % of the gap to 4B.
- Most published numbers below are vendor-reported and use metrics that are not BOAR's: In-Acc (gold string is a substring of the prediction), F1, MR (memorisation ratio, lower is better), R-Acc (fraction of answers saying "not enough information"). None uses the BOAR Haiku-judged floor-adjusted score. Treat every number as a lead to re-measure on the frozen BOAR ruler, not as a result.
- The OCC-RAG table is the only one found that puts a Qwen3-1.7B baseline and a 1.7B grounded model side by side on the same metrics. It is the most useful row for BOAR, and it is still a single-paper claim.

## Findings

### F1. OCC-RAG-1.7B (and 0.6B), arXiv 2606.00683, submitted 30 May 2026 [opened, abstract + HTML tables]
- Base: Qwen3-1.7B-Base, mid-trained on ~3.25M synthetic QA pairs (2.78M single-hop, 262k multi-hop single-context, 165k multi-hop multi-context, 43k abstain), ~9 x 10^9 tokens per model. Output: structured reasoning traces with citations as literal quotes from the context; abstention trained in.
- Table 2 (paper's own, no-thinking Qwen3-1.7B baseline vs OCC-RAG-1.7B):
  - HotpotQA In-Acc: 47.7 -> 60.9
  - MuSiQue In-Acc: 20.1 -> 38.2
  - TAT-QA F1: 74.4 -> 81.0
  - ConFiQA In-Acc: 64.8 -> 81.4; ConFiQA MR (lower better): 12.7 -> 5.0
  - MuSiQue-Un R-Acc (refusal): 54.7 -> 87.2
  - Qwen3-1.7B with thinking: HotpotQA 60.9, MuSiQue 30.7, ConFiQA 70.4, MR 8.3, MuSiQue-Un 82.8.
- OCC-RAG-0.6B: HotpotQA 57.6, MuSiQue 36.6, TAT-QA 75.0, ConFiQA 79.9, MR 5.2, MuSiQue-Un 86.9.
- Baselines in the same table: Qwen3-4B (no think) HotpotQA 60.6, MuSiQue 33.1, ConFiQA 69.7, MR 10.3, MuSiQue-Un 64.1; Qwen3-8B MuSiQue-Un 90.7; Gemma-3-1B ConFiQA 62.1; Gemma-3-4B MuSiQue-Un 55.8.
- Metric caveat: In-Acc is substring match, so it rewards long answers that contain the gold string. The paper's own text says the 1.7B matches or beats models 2-6x larger, and "closes the gap with Qwen3-4B on HotpotQA and MuSiQue". The authors do not report the baseline prompts, a judge agreement check, or a BOAR-style correctness rubric.
- Licence: MIT (per the Featherless model page). Context 32k. Weights: "Open Weights", HF repo occ-ai/OCC-RAG-1.7B; the page also lists 3 finetunes. GGUF was NOT verified (the Featherless page does not say; the HF card was not opened).
- Note: the Featherless page lists "Model Size: 2B", while the description says 1.7B. Use 1.7B.
- Source URLs opened: https://arxiv.org/abs/2606.00683 ; https://arxiv.org/html/2606.00683 ; https://featherless.ai/models/occ-ai/OCC-RAG-1.7B

### F2. Pleias-RAG-1B (family: Pleias-RAG-350M, Pleias-RAG-1B), arXiv 2504.18225 (v2) [opened]
- Trained to quote literal source passages and cite them; does routing, reformulation and reranking inside the same model. Mid-training on 3,126,691 synthetic RAG examples (~9.47B tokens), trained at context 4,096 tokens. Synthetic data from Common Corpus with Gemma-3 generators.
- The paper's own claims: the models "outperform SLMs below 4 billion parameters" on HotpotQA and 2Wiki; "currently SOTA on 2WikiMultiHopQA" (350M and 1.2B). Numbers are only in Figures 8-9, which I could not read.
- Judge: Gemma-3-12B-it as LLM-as-match, keep "yes" only on HotpotQA/2Wiki.
- Independent numbers (OCC-RAG Table 2, third-party run, not the Pleias paper): Pleias-RAG-1.2B HotpotQA In-Acc 48.5, MuSiQue 15.0, TAT-QA F1 8.4 (very low), ConFiQA 37.3, ConFiQA MR 25.3 (worse than Qwen3-1.7B), MuSiQue-Un R-Acc 21.9. So the third-party run does not support the "beats 4B" claim on the same metrics. The OCC table is the only independent numbers found.
- Licence: apache-2.0 (HF model card, Pleias-RAG-1B; opened). GGUF: yes, unquantised GGUF at huggingface.co/PleIAs/Pleias-RAG-1B-gguf (opened). Size on card: 1.2B params, BF16.
- Deployment note from card: about 20 s for a complex generation on 8 GB RAM and below (vendor claim, desktop-class hardware not stated). Needs the Pleias-RAG-Library for the special tokens; a manual template is not documented on the card.
- Pleias's own multilingual leaderboard placed Pleias-nano-1.2B-RAG third behind Qwen2.5-7B and Llama-3.2-8B (from a search snippet of the Pleias pages, not opened). Vendor-run.
- Source URLs opened: https://arxiv.org/abs/2504.18225 ; https://arxiv.org/html/2504.18225v2 ; https://huggingface.co/PleIAs/Pleias-RAG-1B

### F3. OCC-RAG and Pleias share the same baseline table; SmolLM3-3B and Gemma-3-1B reference rows [opened, same table as F1]
- SmolLM3-3B (no think / think): HotpotQA 49.9 / 56.5; MuSiQue 21.5 / 29.4; TAT-QA 71.1 / 69.7; ConFiQA 58.6 / 60.5; MR 15.4 / 13.3; MuSiQue-Un 32.1 / 77.1.
- Gemma-3-1B-it: HotpotQA 30.8; MuSiQue 12.8; ConFiQA 62.1; MR 7.7; MuSiQue-Un R-Acc 2.2.
- Relevance: SmolLM3-3B is the strongest published 3B reference on these tasks in this table, but still below OCC-RAG-1.7B on HotpotQA and ConFiQA with no training for grounding.
- Source URL opened: https://arxiv.org/html/2606.00683

### F4. IBM Granite 3.3 8B RAG intrinsics (LoRA), granite-3.3-8b-rag-agent-lib [opened, model card]
- Six LoRA intrinsics on granite-3.3-8b-instruct: Query Rewrite (QR); Context Relevance (CR); Answerability Determination (AD); Uncertainty Quantification (UQ); Hallucination Detection (HD, risk per sentence of the answer against passages); Citation Generation (CG, sentence-level citations).
- Licence: apache-2.0. Base is 8B; no small variant mentioned on the card. Not phone-deployable at 8 GB (8B Q4 is ~4.5-5 GB weights alone; uncertain on a 8 GB device with the rest of the app — my estimate, not measured).
- Use for BOAR: a possible offline checker or teacher for citation labels (CG, HD), not a phone component. BOAR has closed "open small judges for the headline", so use only as a diagnostic.
- Earlier IBM RAG LoRAs for Granite 3.2 8B (hallucination detection, citation generation, answerability, uncertainty, query rewrite) appear in a search snippet from an IBM developer forum reply. Not opened.
- Source URL opened: https://huggingface.co/ibm-granite/granite-3.3-8b-rag-agent-lib

### F5. LFM2-1.2B-RAG (Liquid AI) [opened, model card]
- 1.2B (BF16 on card, 1B listed); fine-tuned on 1M+ multi-turn and multi-document samples (mixed curated open-source and synthetic); languages: English, Arabic, Chinese, French, German, Japanese, Korean, Portuguese, Spanish; GGUF available (LFM2-1.2B-RAG-GGUF, 9 quantised variants).
- Licence: "lfm1.0" (Liquid Foundation Model licence), NOT an Apache/MIT licence. Redistribution terms need reading before any BOAR use; not checked in this pass.
- No RAG faithfulness or citation numbers on the card. Card recommends greedy decoding, temperature 0.
- Source URL opened: https://huggingface.co/LiquidAI/LFM2-1.2B-RAG

### F6. B1ade-1B (arXiv 2607.27506, 2026) [opened, abstract only]
- 1B SLM trained with GRPO on 723M tokens (2.2M context-question pairs); reward only on answer similarity. Reports an average of 0.654 across correctness, completeness, coherence and faithfulness, "a 10.8 % improvement over the SFT".
- Standard QA: PopQA 81.82 %, PubMedQA 65.8 %, FEVER 51.09 %. Claims 42.4 % of responses cite retrieved passages (citation emerged without training on citations).
- Judge: not stated on the abstract page, but a search snippet says Claude Sonnet 4 — conflict; treat the judge as unknown.
- Licence and GGUF: not stated on the abstract page.
- Source URL opened: https://arxiv.org/abs/2607.27506

### F7. Finetune-RAG (arXiv 2505.10792, May 2025, v3 Dec 2025) [opened, abstract only]
- "First-of-its-kind RAG training dataset constructed to mimic real-world imperfections" (noisy/irrelevant retrieval); reports a 21.2 % factual-accuracy improvement over the base model. Base model and size are NOT on the abstract page. Code and dataset claimed open-sourced; licence not stated on the page. Bench-RAG is an LLM-judge stress test.
- Unknown: whether any 1B-3B model was used. Needs the full text before it can be used. Follow-up: read https://arxiv.org/html/2505.10792v3.
- Source URL opened: https://arxiv.org/abs/2505.10792

### F8. HalluGuard (ACL Findings 2026, 4B) [snippet only, page returned 404 on fetch]
- A 4B reasoning classifier for grounded/hallucinated claims (not a generator). Search snippet claims 84.4 % balanced accuracy on RAGTruth subset of LLM-AggreFact, beating MiniCheck (7B) and Granite Guardian 3.3 (8B). Not verified.
- Source URL (not opened successfully): https://preview.aclanthology.org/ingest-acl/2026.findings-acl.835/

### F9. RAGTruth (ACL 2024) [snippet only]
- ~18,000 naturally generated RAG responses from several LLMs with word-level hallucination labels; authors say a fine-tuned small model reaches detection performance competitive with prompt-based GPT-4. Sizes and per-model numbers not in the snippet. Code: github.com/ParticleMedia/RAGTruth (from snippet).
- Useful as an external labelled set for measuring the 28 % confident-error problem; check licence before use.
- Source URL (snippet): https://aclanthology.org/2024.acl-long.585

### F10. Granite 4.0 Micro (3.4B) RAG adapters: none found [search only]
- Search turned up no IBM RAG LoRA for granite-4.0-micro. One listing says 3.4B, Oct 2025, context unclear. Hybrid architecture may limit LoRA support (per a listing). Not verified on HF.

### F11. Phi-4-mini / Gemma 3n / MiniCPM / Llama 3.2 small RAG faithfulness: not found [search only]
- A Phi-4-mini RAG search found only Phi-4 14B as a RAGTruth judge (F1 0.894 in one blog, the 14B model), not Phi-4-mini. No Gemma 3n or MiniCPM RAG-faithfulness numbers came back. Llama 3.2 1B/3B RAG numbers were not found beyond a Quran-RAG study (snippet): Llama 3.2 3B "very good on faithfulness", no numbers, not trained for citations. Not opened.

### F12. Preference-optimisation hallucination SLMs (arXiv 2601.04212, TrueBrief) [opened, abstract only]
- TrueBrief: faithful summarisation with small LMs via preference optimisation on injected hallucinations. Model sizes, metrics and licence are not on the abstract page. Not useful for BOAR yet; listed for completeness.
- Source URL opened: https://arxiv.org/abs/2601.04212

## What I searched and did not find
- Searched: small grounded-RAG SLMs (2025-2026); Pleias RAG; IBM Granite RAG LoRAs (3.2, 3.3, 4.0 Micro); LFM2 RAG; faithful-RAG fine-tunes at 1.5B; Phi-4-mini RAGTruth; RAGTruth small-model results; Llama 3.2 / Qwen3 RAGTruth.
- Not searched (gap): Gemma 3 1B/270M RAG fine-tunes, SmolLM3 RAG fine-tunes, MiniCPM 4 RAG, Qwen3 small faithfulness fine-tunes on HF, MiniCheck 0.4B/0.8B (a small grounding checker, not a generator), LongCite-style citation SFT at 1-3B, the "hallucination injection" preference paper (no title captured), and any Hugging Face model-hub search for GGUF of OCC-RAG.
- Not found: any independent (non-vendor) faithfulness benchmark for 1B-3B RAG models with a BOAR-style correctness rubric; any measured phone speed for OCC-RAG or Pleias-RAG on a Tensor G3 / 8 GB device.

## What this means for BOAR

1. The reading wall is the target. The 1.7B gets text and does not use it. OCC-RAG-1.7B and Pleias-RAG-1B were both trained to do exactly that step (literal-quote citations, abstention). The BOAR prompt fixes (quote-first, abstain) failed because the model paraphrases; these models moved that behaviour into training. This is the only lever found that targets the reading wall directly and is not closed.
2. Same-size swap is the cheapest test. OCC-RAG-1.7B is mid-trained from Qwen3-1.7B-Base, so the architecture is the same as BOAR's main model. GGUF conversion should be routine (Qwen3 arch), but this is unverified. Test it as a drop-in on the frozen ruler (v0.4, public decision 2026-10-31) before anything else.
3. Pleias-RAG-1B is the other candidate: Apache-2.0, GGUF released, ~1.2B. But the third-party run gives TAT-QA F1 8.4 and ConFiQA MR 25.3, so it may fail on general factual answers even if it cites well. Needs its own Pleias template and a 4k context check.
4. Caution on the closed fine-tune line. The project notes record a closed "fine-tune DATA" line (Opus teacher 16/20 faithful, human CLAPnq+HAGRID 6/20) for the 4B. OCC-RAG's claim rests on ~3.25M synthetic examples, far larger than that test. The closure does not cover scale, but it does mean a small in-house SFT is not a quick win. Prefer testing the released weights before building our own.
5. Judge and metric mismatch. Every published number here uses substring or classifier metrics. A 1.7B that scores +13 points on In-Acc may still fail the BOAR judge on correctness. Re-measure on the BOAR ruler; do not quote OCC-RAG numbers as BOAR results.
6. Licences: OCC-RAG (MIT per Featherless, verify on HF), Pleias-RAG (Apache-2.0), Granite 3.3 adapters (Apache-2.0, 8B only), LFM2-1.2B-RAG (lfm1.0, not checked, treat as restricted until read).

## UNKNOWN
- OCC-RAG GGUF availability and the exact HF licence file (only the Featherless page was read).
- Pleias-RAG template and whether the GGUF runs in the BOAR llama.cpp build.
- Finetune-RAG base model size.
- Judge used by B1ade (sources disagree).
- Real on-device speed for any 1-2B grounded model on the Tensor G3.
