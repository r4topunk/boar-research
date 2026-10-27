# KIT-X2b (H-A, META 2026-10-16 13:xx): X2b on the claim kit, 0-call gate: FAIL, closed at S2 (CLOSED R93)
0 LLM / 0 judge / 0 paid. Script-only on blind (v0.2 110, scoped exception 10-16 13:xx); counts only. Tool: gate_kitx2b.py; output gate.json.

**Portability (from headpass-x2b.vs-cut7.patch):** the X1 half is portable: packs.ts HEADPASS_KIT = {boar-crypto, boar-wikivoyage-en} is the only thing that keeps it off the kit; both kit stores are format-2 packs with chunks(article_id, start) so headChunksOf runs unchanged. The dense half is not: it needs a chunk_vecs sidecar; the kit stores carry lead_vecs only, and the v3proto sidecar copies of both kit packs (DENSECHUNK-ST2, 10-13) were deleted (manifests remain; re-embed of ~603k chunks, ~+240 MB wikivoyage).

**Gate (traces = TK2FIX-V02 cut 7 kit replay, pass 1):** gold on v0.2 is article-level (0/129 entries carry #section), so a neighbour chunk of an already-kept article adds 0 gold-in-kept by construction.
| count | value |
|---|---|
| gold items / gold kept (today) / gold in raw top-6 | 86 / 15 / 18 |
| X1 on kit fires (first raw pack passage) / anchor article already kept | 88 / 42 |
| X1 on kit: new gold-in-kept items | **0** |
| upper bound any raw-6 gold not kept | 3 (ceiling 3 x 0.18 / 110 = 0.005) |
| gold title exists in a kit store (any) / of these not in raw-6 | 41 / 25 (oracle dense ceiling 0.041; at the X2b pack capture rate 30/108 ~ 28 % -> ~7 items -> ~0.011) |
| items needed for MDE 0.025 at 0.18/item | 15.3 |

**Verdict:** FAIL vs MDE 0.025 (neighbour half 0.000; raw-6 bound 0.005; realistic dense half ~0.011, oracle 0.041 only with perfect reach). Closed at S2. Reopen = a kit set with section-level gold, or a kit re-embed already paid for by another arm (then measure dense reach of the 25 in-store items first).
