import { normalizeCitations as N } from "./citationNormalize.ts";
const cases = [["temporary camps [1, 3].",4],["groups. [1, 2, 6]",6],["x = [1, 2] and arr[1, 2]",4],["see `[1, 2]` code",4],["[Source 2] says",3],["(source 1, 3) ok",3],["【2】 x",2],["fact[^2] here\n[^2]: def",3],["km² and 10^100 and (1) item",3],["[1-3] [0, 1] [1, 1] [1, 9]",4],["plain [1] cite",3]];
for (const [t,k] of cases) console.log(JSON.stringify(t), "->", JSON.stringify(N(t,k)));
