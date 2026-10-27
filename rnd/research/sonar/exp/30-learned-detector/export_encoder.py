"""Save the fine-tuned encoder alone (ModernBertModel, no head) for convert_hf_to_gguf.py; the head goes to JS (export_head.py).
usage: export_encoder.py <tag>"""
import sys
from transformers import AutoModelForSequenceClassification, AutoTokenizer
tag = sys.argv[1]; m = AutoModelForSequenceClassification.from_pretrained(f'results/{tag}.model')
enc = m.model; enc.config.architectures = ['ModernBertModel']
enc.save_pretrained(f'results/{tag}.encoder'); AutoTokenizer.from_pretrained(f'results/{tag}.model').save_pretrained(f'results/{tag}.encoder')
print('ok')
