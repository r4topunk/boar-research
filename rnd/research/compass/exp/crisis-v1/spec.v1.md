# Crisis detector v1 (supersedes v0 5c9c36e4 after crisis1 FAIL): frozen spec
Gate on every message, BEFORE retrieval:
1. METHOD backstop (method_backstop.py) matches → crisis card (both tiers).
2. p = sigmoid(w·bge(query)+b) with crisis-head.v1.json (trained only on train.json).
3. Android (Qwen3-4B-Instruct-2507, resident): if p ≥ 0.20 → ask the model with prompt.txt (grammar yes|no, temp 0, user turn "Message: <query>"); yes → crisis card. Run the check in parallel with retrieval.
4. iPhone (Qwen2.5-1.5B, resident): if p ≥ 0.30 → ask the model with prompt.txt; yes and p ≥ 0.60 → crisis card; yes and 0.30 ≤ p < 0.60 → normal answer + support footer.
5. Otherwise: normal answer; if the message mentions suicide/self-harm topically (v0 tier-2 regex in ../crisis/detect.py, T2 minus EXCLUDE), add the support footer.
Card texts and crisis lines unchanged from the self-harm-crisis-card (../crisis/crisis-lines.json).
