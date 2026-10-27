# Denylist v0 match rule (frozen with denylist.v0.json)
- Scope: every retrieved chunk, at context build (before the chunk becomes a numbered source), all routes including health.
- Title match: the chunk's article title with any "<Source>: " display prefix removed (e.g. "Wikivoyage: Cold weather" -> "Cold weather"), compared case-insensitively and exactly to an entry's `title`. Pack is not required to match (the "Cold weather" sentence exists in both packs).
- Sentence match: normalize both texts (Unicode NFC, collapse whitespace runs to one space, trim). An entry matches if its normalized `sentence` is a substring of the normalized chunk body. Remove that span, plus a directly preceding list marker ("- ") if present.
- If the chunk's remaining body has < 40 non-space characters, drop the chunk.
- Nothing else changes: no fuzzy matching, no rule regexes at runtime, no PT translation.
