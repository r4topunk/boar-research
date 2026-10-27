# Verdict-shaped questions (yes/no or binary comparison). Frozen with protocol.md.
import re
VERDICT = re.compile(r"^\s*(?:(?:did|does|do|is|are|was|were|can|could|has|have|will|would|should)\b(?!.*\b(?:how|why|what|which)\b)|which\b[^?]{0,60}\b(?:more|less|bigger|larger|smaller|denser|older|newer|longer|shorter|higher|lower|faster|slower|heavier|lighter|first|earlier|later)\b|(?:is|are|was|were)\b[^?]{0,80}\b(?:more|less|bigger|larger|smaller|denser|older|longer|higher|faster|heavier)\b[^?]{0,40}\bthan\b)", re.I)
def is_verdict(q): return bool(VERDICT.search(q))
