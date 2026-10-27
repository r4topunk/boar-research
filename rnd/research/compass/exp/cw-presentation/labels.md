# Hand labels for replay-s44.json (Compass, after freezing guard.frozen.md; v0.1 dev, s44 only)
| item | sentence (short) | G1 | label vs source | outcome |
|---|---|---|---|---|
| lan-cmp-002 | polar bears generally larger than grizzlies | block (larger) | NOT SUPPORTED (source: "massive, as ferocious as the grizzly") | correct block |
| vit-cry-004 | PeerDAS samples a subset… without full downloads | block (without) | SUPPORTED (paraphrase of "downloading only a subset") | loss |
| lan-cmp-003 | No country is bigger than India by area | block (no) | WRONG | correct block |
| lan-exp-005 | Sahara largest hot desert, "covering about 9." | block (9) | SUPPORTED; "9" is the engine's own sentence split on "9.2" | loss (number artifact) |
| lan-ref-005 | venues "already in use or not designed to be permanent" | block (not) | WRONG (source: "beyond use or never planned") | correct block |
| lan-rsn-006 | fought between the Kingdom of England and Kingdom of France | keep | NOT SUPPORTED (source is England/Scotland history) | miss |
| 8 others | mosquitoes/dengue, ECDSA→AA, Glamsterdam ePBS, Civil War 1865, pronghorn, Rio 2016, doorways, frostbite warming | keep | SUPPORTED | correct keep |
- Base attribution: 14 added [n], 4 unsupported or wrong (29 %). With G1: 9 kept, 1 unsupported (11 %); 3 of 4 bad ones blocked; 2 correct lost (1 is the number artifact).
