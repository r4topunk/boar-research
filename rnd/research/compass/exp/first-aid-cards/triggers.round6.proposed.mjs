// Round 6 trigger proposals (Compass, 2026-10-03): cpradult / cprchild / cprinfant (age-routed) and poisoning.
// Same conventions as triggers.proposed.mjs (B/E = Unicode word boundary; u() makes \w Unicode-aware). Not merged
// into triggers.proposed.mjs (another process may be editing it); merge PROPOSED6 into PROPOSED when wiring round 6.
// Run: node triggers.round6.proposed.mjs  → self-test (EN/PT/ES × 4 cards × 3 positives + 3 look-alikes, plus age
// routing), then a collision report against the round 1–5 triggers if triggers.proposed.mjs can be imported.
const B = String.raw`(?<![\p{L}\p{N}_])`, E = String.raw`(?![\p{L}\p{N}_])`;
const W = String.raw`[\p{L}\p{N}_]`;
const u = (src) => src.replaceAll("\\w", W);

// ---- age routing: baby (<1 year) → cprinfant; child word → cprchild; else → cpradult
const INFANT = String.raw`${B}(?:bab(?:y|ies)|infants?|newborns?|beb[êeé]s?|rec[ée]m.nascid\w*|reci[ée]n nacid\w*|lactantes?|[0-9]{1,2}.?(?:months?|meses).?(?:old|de idade|de edad)?|de [0-9]{1,2} meses)${E}`;
const CHILD = String.raw`${B}(?:child|children|kids?|son|daughter|toddler|boy|girl|grandson|granddaughter|nephew|niece|[0-9]{1,2}.?(?:year|yr).?old|crian[çc]as?|filh[oa]s?|menin[oa]s?|net[oa]s?|sobrinh[oa]s?|ni[ñn][oa]s?|hij[oa]s?|nenes?|nietos?|nietas?|peque[ñn][oa]s?|[0-9]{1,2} (?:anos|años))${E}`;

// ---- arrest / CPR cues
const ARREST = String.raw`(?:${B}cpr${E}|${B}rcp${E}|chest compressions?|not breathing|isn'?t breathing|stopped breathing|no pulse|no heartbeat|cardiac arrest|unresponsive and (?:not|isn'?t) breathing|n[ãa]o (?:est[áa] )?respira(?:ndo)?|parou de respirar|sem respirar|sem pulso|parada card[íi]aca|parada cardiorrespirat[óo]ria|massagem card[íi]aca|compress(?:ões|ao|ão) (?:no peito|tor[áa]cicas?)|${B}no (?:est[áa] )?respira(?:ndo)?${E}|dej[óo] de respirar|sin respirar|sin pulso|paro card[íi]aco|paro cardiorrespiratorio|masaje card[íi]aco|reanimaci[óo]n cardiopulmonar|compresiones (?:en el pecho|tor[áa]cicas))`;
// not an emergency: courses/prices/learning; nose/sinus; apnoea/snoring; plus conditions with their own cards
// (drowning/water rescue, choking) so the engine does not get two cards (MULTI → generic).
const NOT_ARREST = String.raw`(?:course|class(?:es)?${E}|training|certif|price|cost|near me|how much|learn|curso|aula|treinamento|capacita|pre[çc]o|quanto custa|aprender|precio|cu[áa]nto cuesta|taller|through (?:my|his|her|the) nose|pelo nariz|por la nariz|nariz entupid|nariz tapad|apn[ée]?ia|apnea|drown|afog|ahog|out of the (?:water|pool|lake|sea|river|ocean)|(?:da|do) (?:piscina|mar|[áa]gua|lago|rio)${E}|(?:del|de la) (?:agua|piscina|alberca|mar|lago|r[íi]o)${E}|chok|engasg|atragant|same thing|difference between|mesma coisa|diferen[çc]a entre|lo mismo|diferencia entre|movie|filme|pel[íi]cula|${B}tv${E}|novela|series?${E})`;

// ---- poisoning cues
const INGEST = String.raw`(?:swallow\w*|${B}(?:ate|eaten|drank|drunk|ingest\w*)${E}|got into (?:the|my|some)|engol\w*|${B}(?:comeu|bebeu|ingeriu)${E}|trag[óo]|se trag\w*|${B}(?:comi[óo]|bebi[óo]|ingiri[óo])${E}|(?:took|tak\w+|tomou|tomei|tom[óo]|tom[ée])[^.?!]{0,50}(?:twice|two times|double dose|duas vezes|dose dupla|dos veces|doble dosis|dosis doble))`;
const SUBST = String.raw`(?:${B}pills?${E}|${B}tablets?${E}|medicines?|medications?|${B}meds${E}|paracetamol|acetaminophen|tylenol|ibuprofen|aspirin|bleach|detergent|laundry pods?|dishwasher|cleaning (?:product|liquid|spray)|${B}cleaner|chemicals?|pesticide|insecticide|weed ?killer|rat poison|antifreeze|kerosene|paraffin|gasoline|petrol|lamp oil|lighter fluid|drain cleaner|nail polish remover|essential oil|poison(?:ous)? (?:mushroom|berr|plant)|wild (?:mushroom|berr)|${B}poison${E}|rem[ée]dios?|comprimidos?|p[íi]lulas?|medicamentos?|[áa]gua sanit[áa]ria|c[âa]ndida|soda c[áa]ustica|produtos? de limpeza|desinfetante|detergente|chumbinho|raticida|veneno|inseticida|agrot[óo]xico|querosene|gasolina|thinner|solvente|acetona|cogumelo|pastillas?|medicinas?|cloro|lej[íi]a|producto de limpieza|desinfectante|matarratas|insecticida|plaguicida|queroseno|hongos? (?:silvestres?|venenosos?)|setas? venenosas?)`;
const OVERDOSE = String.raw`(?:overdos\w*|sobredosis|superdosagem|took (?:too many|a lot of|a bunch of|a handful of|all (?:of )?(?:the|her|his|my)|the whole|a whole|most of (?:a|the|my|her|his))|tomou (?:muitos|v[áa]rios|todos os|todas as|a cartela|remédio demais)|(?:se )?tom[óo] (?:muchas|demasiadas|todas las|todos los))`;
const POISONED = String.raw`(?:${B}poisoned${E}|poisoning|envenen\w*|intoxica[çc][ãa]o|intoxicad\w*|intoxicaci[óo]n|poison control|poison cent(?:er|re)|centro de (?:informa[çc][ãa]o )?toxicol[óo]gic|${B}ciatox${E}|centro de toxicolog|centro (?:nacional )?de intoxicaciones)`;
// separate cards or out of scope: battery/coin/magnet, CO/gas, food poisoning, alcohol-only, venomous animals, poison ivy, eye splash (eyechem)
const NOT_POISON = String.raw`(?:poison ivy|poison oak|sumac|hiedra venenosa|hera venenosa|food poisoning|intoxica[çc][ãa]o alimentar|intoxicaci[óo]n alimentaria|comida (?:estragada|en mal estado)|button batter|${B}batter(?:y|ies)${E}|${B}pilhas?${E}|${B}pilas?${E}|bater[íi]as?${E}|${B}coins?${E}|moedas?${E}|monedas?${E}|magnets?${E}|${B}[íi]m[ãa]s?${E}|imanes${E}|carbon monoxide|mon[óo]xido|gas leak|fuga de gas|vazamento de g[áa]s|snake|cobra|serpiente|v[íi]bora|spider|aranha|ara[ñn]a|scorpion|escorpi|alacr[áa]n|${B}bees?${E}|abelha|abeja|wasp|jellyfish|(?:in|into) (?:his|her|my|the) eyes?|no olho|nos olhos|en el ojo|en los ojos|${B}(?:dog|cat|puppy|kitten|pet|perr[oa]|gat[oa]|cachorr[oa]|mascota)s?${E}|minecraft|video ?game|${B}game${E}|${B}jogo${E}|personagem|po[çc][ãa]o|potion|videojuego|${B}juego${E}|personaje)`;
const ALCOHOL_ONLY = String.raw`(?:alcohol poisoning|intoxica[çc][ãa]o alco[óo]lica|coma alco[óo]lico|intoxicaci[óo]n (?:et[íi]lica|alcoh[óo]lica|por alcohol)|${B}(?:drunk|b[êe]bad[oa]|borrach[oa])${E})`;
const FORAGE = String.raw`(?=.*(?:mushroom|toadstool|berr(?:y|ies)|${B}plants?${E}|leaves|cogumelos?|frutinhas?|${B}plantas?${E}|folhas|hongos?|${B}setas?${E}|bayas?|frutos? silvestres))(?=.*(?:found|picked|wild|forest|woods|garden|yard|encontr\w*|colh\w*|silvestre|bosque|${B}mato${E}|campo|jard[íi]n|quintal|trilha|sendero|caminar))(?=.*(?:${B}(?:ate|eaten|ate some)${E}|swallow\w*|comeu|comeram|comemos|comi[óo]|comimos|comieron|nos los comimos|${B}com[ií]${E}|ingeri\w*|ingiri\w*|trag\w*|engol\w*))`;
const POISON_CORE = String.raw`(?:${FORAGE}|(?=.*${INGEST})(?=.*${SUBST})|(?=.*${OVERDOSE})|(?=.*${POISONED})(?!.*${ALCOHOL_ONLY}))`;

// weak cue: not responding / won't wake (breathing unknown). The CPR card's first step checks breathing and its last
// step covers the side (recovery) position. Not for devices/messages, and not when another condition card owns it.
const UNRESP = String.raw`(?:not responding|isn'?t responding|unresponsive|won'?t wake|can'?t wake (?:him|her|them)|unconscious|passed out and (?:is )?not|n[ãa]o (?:est[áa] )?respond\w*|n[ãa]o acorda|desacordad\w*|inconscient[e]${E}|${B}no responde${E}|no despierta|no reacciona|no abre los ojos|n[ãa]o abre os olhos|(?:doesn'?t|won'?t) open (?:his|her|their) eyes)`;
const NOT_UNRESP = String.raw`(?:texts?|messages?|mensagens?|mensajes?|e-?mails?|calls?|liga[çc][õo]es|llamadas|whatsapp|${B}zap${E}|${B}app${E}|computer|laptop|phone (?:is|isn)|screen|program|site|website|celular|computador|tela|aplicativo|pantalla|programa|subconscious|inconsciente colectivo|inconsciente coletivo|seizure|convuls|${B}fits?${E}|epilep|epil[ée]p|head|cabe[çc]a|cabeza|diabet|insulin|sugar|a[çc][úu]car|az[úu]car|heat|calor|sun|${B}sol${E}|electric|el[ée]tric|choque|descarga|allerg|al[ée]rgi|anaphyl|anafil|stroke|derrame|${B}avc${E}|ictus|hypotherm|hipoterm|${B}co${E}|mon[óo]xido|carbon monoxide|${B}gas${E}|g[áa]s${E}|scorpion|escorpi|alacr|snake|cobra|serpiente|bee|abelha|abeja|battery|bateria|pila)`;
const ARREST_GATE = `^(?!.*${NOT_ARREST})(?:(?=.*${ARREST})|(?=.*${UNRESP})(?!.*${NOT_UNRESP}))`;
export const PROPOSED6 = {
  cprinfant: new RegExp(u(`${ARREST_GATE}(?=.*${INFANT})`), "isu"),
  cprchild: new RegExp(u(`${ARREST_GATE}(?!.*${INFANT})(?=.*${CHILD})`), "isu"),
  cpradult: new RegExp(u(`${ARREST_GATE}(?!.*${INFANT})(?!.*${CHILD})`), "isu"),
  // poisoning + not breathing → the CPR card (the poisoning card also says 'start CPR'); battery/CO/food/alcohol-only/venom → other cards or none
  poisoning: new RegExp(u(`^(?!.*${NOT_POISON})(?!.*${ARREST})${POISON_CORE}`), "isu"),
};

const T = [
  // ---- cpradult: EN / PT / ES positives, then look-alikes (must fire none of the 4 keys)
  ["my dad collapsed and he's not breathing, what do I do", "cpradult"],
  ["how do I do CPR on my husband? he isn't breathing", "cpradult"],
  ["a man fell down in the street, no pulse, unresponsive", "cpradult"],
  ["CPR course price in London", null],
  ["I'm not breathing well through my nose because of the cold", null],
  ["my husband snores and stopped breathing for a few seconds, is it sleep apnea?", null],
  ["meu pai desmaiou e não está respirando", "cpradult"],
  ["como fazer massagem cardíaca? minha mãe não respira", "cpradult"],
  ["acho que é uma parada cardíaca, o homem caiu e não respira", "cpradult"],
  ["quanto custa um curso de RCP?", null],
  ["não respiro bem pelo nariz entupido", null],
  ["quero aprender RCP no fim de semana", null],
  ["mi esposo se desmayó y no respira", "cpradult"],
  ["cómo hago RCP? mi abuela dejó de respirar", "cpradult"],
  ["creo que es un paro cardíaco, el señor está sin pulso", "cpradult"],
  ["¿cuánto cuesta un curso de RCP?", null],
  ["no respiro bien por la nariz tapada", null],
  ["mi papá tiene apnea del sueño y ronca", null],
  // ---- cprchild
  ["my 6 year old son collapsed and isn't breathing", "cprchild"],
  ["how do I do CPR on a child? my daughter stopped breathing", "cprchild"],
  ["the kid is unresponsive and not breathing at the playground", "cprchild"],
  ["paediatric CPR training for teachers", null],
  ["my son is breathing fast with a fever", null],
  ["my daughter choked on a grape and now she's not breathing", "choking-only (null here)"],
  ["minha filha de 5 anos não está respirando", "cprchild"],
  ["meu filho parou de respirar, como faço a RCP?", "cprchild"],
  ["a criança desmaiou e está sem respirar", "cprchild"],
  ["curso de RCP infantil para escola", null],
  ["meu filho está com o nariz entupido e não respira pelo nariz", null],
  ["tiramos meu filho da piscina e ele não respira", "drowning-only (null here)"],
  ["mi hijo de 7 años no respira", "cprchild"],
  ["la niña dejó de respirar, ¿cómo le hago RCP?", "cprchild"],
  ["mi nieto se desmayó y está sin respirar", "cprchild"],
  ["taller de RCP para niños en la escuela", null],
  ["mi hija no respira bien por la nariz", null],
  ["sacamos a mi hijo del agua y no respira", "drowning-only (null here)"],
  // ---- cprinfant
  ["my baby isn't breathing", "cprinfant"],
  ["how to do infant CPR, my 4 month old stopped breathing", "cprinfant"],
  ["newborn not breathing and limp", "cprinfant"],
  ["infant CPR class near me", null],
  ["my baby is breathing fast with a cold", null],
  ["my baby is choking and not breathing", "chokinginfant-only (null here)"],
  ["meu bebê não está respirando", "cprinfant"],
  ["bebê de 3 meses parou de respirar, como faço a RCP?", "cprinfant"],
  ["o recém-nascido está sem respirar e mole", "cprinfant"],
  ["curso de primeiros socorros para bebê, preço", null],
  ["meu bebê está com apneia do sono?", null],
  ["meu bebê engasgou e não respira", "chokinginfant-only (null here)"],
  ["mi bebé no respira", "cprinfant"],
  ["bebé de 2 meses dejó de respirar, ¿cómo le hago RCP?", "cprinfant"],
  ["el recién nacido está sin respirar", "cprinfant"],
  ["curso de RCP para bebés, precio", null],
  ["mi bebé respira rápido por la nariz tapada", null],
  ["mi bebé se atragantó y no respira", "chokinginfant-only (null here)"],
  // ---- poisoning
  ["my toddler swallowed some bleach", "poisoning"],
  ["she took too many pills, what do I do", "poisoning"],
  ["I think my son drank kerosene from a bottle", "poisoning"],
  ["how to get rid of a poison ivy rash", null],
  ["I had mild food poisoning yesterday, now fine", null],
  ["my son swallowed a button battery", "battery-only (null here)"],
  ["meu filho engoliu água sanitária", "poisoning"],
  ["minha mãe tomou muitos comprimidos de uma vez", "poisoning"],
  ["acho que ele bebeu veneno de rato (chumbinho)", "poisoning"],
  ["estou com intoxicação alimentar leve desde ontem", null],
  ["tomei meu remédio de pressão hoje cedo", null],
  ["minha filha engoliu uma pilha", "battery-only (null here)"],
  ["mi hijo se tragó cloro", "poisoning"],
  ["mi mamá se tomó muchas pastillas", "poisoning"],
  ["creo que el niño bebió veneno para ratas", "poisoning"],
  ["tuve una intoxicación alimentaria leve ayer", null],
  ["me tomé la pastilla para el dolor de cabeza", null],
  ["la hiedra venenosa me dio sarpullido", null],
  // ---- routing edge cases
  ["she swallowed rat poison and now she's not breathing", "cpradult"],          // poison + not breathing → CPR (adult)
  ["my son drank bleach and isn't breathing", "cprchild"],
  ["my friend has alcohol poisoning, he's very drunk", null],                    // alcohol only: out of scope (no card)
  ["intoxicação por monóxido de carbono em casa", null],                         // CO card, not poisoning
  ["my 2 year old got into the cleaning products and swallowed some", "poisoning"],
  // added after the emergency-dev run (dev; see REVIEW-6.md): pets, games, explainers
  ["my dog ate a whole tablet of dark chocolate", null],
  ["no jogo meu personagem está envenenado, qual poção usar?", null],
  ["is cardiac arrest the same thing as a heart attack?", null],
  ["minha mãe tomou o remédio da pressão e está tonta", null],
  // weak cue (not responding, breathing unknown) and phrasings added after the emergency-dev run (see REVIEW-6.md)
  ["my brother collapsed and isn't responding", "cpradult"],
  ["meu avô caiu e não responde, está respirando estranho, tipo ronco", "cpradult"],
  ["mi tío está inconsciente en el piso", "cpradult"],
  ["my son isn't responding to my texts", null],
  ["o aplicativo não está respondendo", null],
  ["she had a seizure and is unconscious", null],                                  // seizure card's job
  ["I took most of a bottle of sleeping pills", "poisoning"],
  ["comimos unos hongos que encontramos en el bosque y ahora tiene vómitos", "poisoning"],
  ["we had mushroom risotto for dinner", null],             // a normal dose is not a poisoning
  ["mi papá se tomó la pastilla de la presión dos veces hoy", "poisoning"],  // double dose → poison centre
];
const KEYS = Object.keys(PROPOSED6);
let ok = 0;
for (const [q, want] of T) {
  const hits = KEYS.filter((k) => PROPOSED6[k].test(q));
  const got = hits.length === 1 ? hits[0] : hits.length ? "MULTI:" + hits.join("+") : null;
  const exp = typeof want === "string" && want.includes("-only") ? null : want;  // "x-only (null here)": another card's job
  const good = got === exp; ok += good;
  if (!good) console.log("MISS", JSON.stringify(q), "want", exp, "got", got);
}
console.log(`round-6 triggers self-test: ${ok}/${T.length}`);

// ---- collision report against round 1–5 triggers (informational; not part of the pass/fail count)
try {
  const log = console.log; console.log = () => {};            // silence the old file's own self-test output
  const { PROPOSED } = await import("./triggers.proposed.mjs");
  console.log = log;
  const coll = [];
  for (const [q] of T) {
    const mine = KEYS.filter((k) => PROPOSED6[k].test(q));
    const old = Object.keys(PROPOSED).filter((k) => PROPOSED[k].test(q));
    if (mine.length && old.length) coll.push(`${JSON.stringify(q)}: ${mine.join("+")} + old ${old.join("+")}`);
  }
  console.log(`collisions with round 1-5 triggers: ${coll.length}`); for (const c of coll) console.log("  " + c);
} catch (e) { console.log("collision report skipped:", e.message); }
process.exitCode = ok === T.length ? 0 : 1;
