---
license: apache-2.0
language:
- en
base_model:
- Qwen/Qwen3-1.7B
pipeline_tag: text-generation
library_name: transformers
---

# Jan-v1-edge: Distilled for Edge, Built for Web Search

[![GitHub](https://img.shields.io/badge/GitHub-Repository-blue?logo=github)](https://github.com/menloresearch/deep-research)
[![License](https://img.shields.io/badge/License-Apache%202.0-yellow)](https://opensource.org/licenses/Apache-2.0)
[![Jan App](https://img.shields.io/badge/Powered%20by-Jan%20App-purple?style=flat&logo=android)](https://jan.ai/)

## Overview

**Jan-v1-edge** is a lightweight agentic model built for fast, reliable on-device execution. As the second release in the **Jan Family**, it is distilled from the larger [`Jan-v1`](https://huggingface.co/janhq/Jan-v1-4B) model, preserving strong reasoning and problem-solving ability in a smaller footprint suitable for resource-constrained environments.

Jan-v1-edge was developed through a two-phase post-training process. The first phase, **Supervised Fine-Tuning (SFT)**, transferred core capabilities from the `Jan-v1` teacher model to the smaller student. The second phase, **Reinforcement Learning with Verifiable Rewards (RLVR)** —the same method used in `Jan-v1` and `Lucy`—further optimized reasoning efficiency, tool use, and correctness. This staged approach delivers reliable results on complex, interactive workloads.

## Performance

### Question Answering(SimpleQA)

Despite having only 1.7B parameters, **Jan-v1-edge** achieves 83% accuracy—nearly matching the larger Jan-nano-128k—demonstrating its efficiency and robustness.

![image/png](https://cdn-uploads.huggingface.co/production/uploads/655e3b59d5c0d3db5359ca3c/gV6Ph1m3rW6KeYkpj_b4s.png)

### Chat & Instruction Following

![image/png](https://cdn-uploads.huggingface.co/production/uploads/655e3b59d5c0d3db5359ca3c/xNWL41L__oULHJkuAaGGt.png)

Versus Qwen 3 1.7B Thinking, Jan-v1-edge shows a slight degradation on instruction-following and CreativeWriting, while remaining comparable or better on EQBench and recency QA.

## Quick Start

### Integration with Jan App

Jan-v1-edge is optimized for direct integration with the [Jan App](https://jan.ai/). Simply select the model from the Jan App interface for immediate access to its full capabilities.

### Local Deployment

**Using vLLM:**
```bash
vllm serve janhq/Jan-v1-edge \
    --host 0.0.0.0 \
    --port 1234 \
    --enable-auto-tool-choice \
    --tool-call-parser hermes
    
```

**Using llama.cpp:**
```bash
llama-server --model Jan-v1-edge-Q8_0.gguf \
    --host 0.0.0.0 \
    --port 1234 \
    --jinja \
    --no-context-shift
```

### Recommended Inference Parameters
```yaml
temperature: 0.6
top_p: 0.95
top_k: 20
min_p: 0.0
max_tokens: 2048
```

## 🤝 Community & Support

-   **Discussions**: [HuggingFace Community](https://huggingface.co/janhq/Jan-v1-edge/discussions)
-   **Jan App**: Discover more about the Jan App at [jan.ai](https://jan.ai/)

## 📄 Citation
```bibtex
Updated Soon
```