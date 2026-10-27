# G1 polarity/number guard for citation ATTRIBUTION (frozen 2026-10-02 before the replay's hand check)
An attribution (the engine adding [n] to an uncited sentence, `attributeCitations`) is blocked if the sentence contains a token from one of these classes that the source text (title + body) does not contain:
- negation: no, not, never, cannot, can't, isn't, aren't, wasn't, weren't, doesn't, don't, didn't, won't, none, nothing, neither, nor, without
- number: any digit run (commas/spaces inside numbers removed on both sides)
- comparison/exclusivity: only, largest, biggest, smallest, highest, lowest, longest, most, least, larger, bigger, smaller, higher, lower, more, less, first, last
CT-1 (keeping the model's own citations) is untouched. Health answers are untouched (attribution already skips them).
Judging the replay: for each attribution G1 blocks, Compass hand-labels the sentence vs its source as SUPPORTED (block = loss) or NOT SUPPORTED/WRONG (block = correct). For each attribution G1 keeps, the same label (kept-but-unsupported = miss).
