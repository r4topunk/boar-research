/**
 * English search words for a Portuguese question, so it can find the
 * knowledge packs, which are in English. Sextant, 2026-09-26: "Como faço para
 * parar um sangramento no nariz?" retrieved nothing from the Preparedness
 * pack. A fixed dictionary of health, first-aid and emergency terms: no model
 * call, so it is instant and can't invent a query. Null when no term is known
 * (the question is searched as written).
 */

// Longest phrases first: "sangramento no nariz" before "sangramento".
const PT_EN: Array<[RegExp, string]> = [
  [/sangramento (no|do|pelo) nariz|sangramento nasal|sangue (no|do|pelo) nariz|nariz[^.?!]{0,20}sangr\w*|sangr\w*[^.?!]{0,20}nariz|epistaxe/i, "nosebleed nose bleed"],
  [/primeiros socorros/i, "first aid"],
  [/picada de (cobra|serpente)|mordida de (cobra|serpente)|picad[ao] por (uma )?(cobra|serpente)|mordid[ao] por (uma )?(cobra|serpente)|(cobra|serpente)[^.]{0,30}(picou|mordeu)|(picou|mordeu)[^.]{0,30}(cobra|serpente)/i, "snakebite snake bite"],
  [/picada de (abelha|vespa)|ferroada/i, "bee sting"],
  [/picada de escorpi[ãa]o/i, "scorpion sting"],
  [/parada card[íi]aca/i, "cardiac arrest"],
  [/ataque card[íi]aco|infarto/i, "heart attack"],
  [/\bavc\b|derrame/i, "stroke"],
  [/\brcp\b|reanima[çc][ãa]o( cardiopulmonar)?|massagem card[íi]aca/i, "cpr"],
  // A scald is a burn: "derramou água fervente no braço" must find Burn, not the physics of boiling.
  [/(derram|caiu|queim|escald|jog)\w*[^.]{0,40}(água|[áa]gua|[óo]leo|caf[ée]|ch[áa]|sopa|leite) (fervente|fervendo|quente|escaldante)|(água|[áa]gua|[óo]leo) (fervente|fervendo|quente|escaldante)[^.]{0,40}(derram|caiu|queim|escald)\w*|escaldadura|escaldou|se queimou|queimou (o|a|a m[ãa]o|o bra[çc]o)/i, "burn scald"],
  [/[áa]gua (fervente|fervendo)|[áa]gua quente/i, "boiling water"],
  // Shivering, confused, slurred speech in the cold: hypothermia.
  [/(tremend\w*|tremores?|calafrios?)[^.]{0,80}\bfrio\b|\bfrio\b[^.]{0,80}(tremend\w*|tremores?|calafrios?)/i, "hypothermia"],
  [/[áa]gua pot[áa]vel|[áa]gua (segura|limpa) para beber|tornar a [áa]gua (segura|pot[áa]vel)/i, "safe drinking water"],
  [/[áa]gua contaminada/i, "contaminated water"],
  [/insola[çc][ãa]o|golpe de calor/i, "heatstroke heat stroke"],
  [/rea[çc][ãa]o al[ée]rgica|choque anafil[áa]tico|anafilaxia/i, "anaphylaxis allergic reaction"],
  [/sangramento|hemorragia|sangrando/i, "bleeding"],
  [/queimadura|queimou|queimad[oa]/i, "burn"],
  [/cobra|serpente/i, "snake"],
  [/engasg\w*|asfixia/i, "choking"],
  [/afogamento|afogad[oa]/i, "drowning"],
  [/hipotermia/i, "hypothermia"],
  [/desidrata[çc][ãa]o/i, "dehydration"],
  [/desmai\w*/i, "fainting"],
  [/convuls[ãa]o|convuls\w*/i, "seizure"],
  [/fratura|osso quebrado|quebrou o (bra[çc]o|perna|osso)/i, "fracture broken bone"],
  [/tor[çc][ãa]o|entorse/i, "sprain"],
  [/envenenamento|envenenad[oa]|veneno/i, "poisoning"],
  [/ferida|ferimento|machucad[oa]|corte profundo/i, "wound"],
  [/febre/i, "fever"],
  [/alergia/i, "allergy"],
  // Before "terremoto": the plates (Sextant RF-1, "…perto das bordas das placas?").
  [/(bordas?|limites?|fronteiras?) (das|entre as) placas|placas? tect[ôo]nicas?|tect[ôo]nica de placas/i, "plate tectonics plate boundary"],
  [/terremoto|sismo|tremor de terra/i, "earthquake"],
  [/enchente|inunda[çc][ãa]o|alagamento/i, "flood"],
  [/furac[ãa]o|tuf[ãa]o|ciclone/i, "hurricane"],
  [/inc[êe]ndio|fogo/i, "fire"],
  [/evacua[çc][ãa]o|evacuar/i, "evacuation"],
  [/nariz/i, "nose"],
  [/crian[çc]a|beb[êe]/i, "child"],
  [/parar|estancar|interromper/i, "stop"],
  [/tratar|tratamento|cuidar/i, "treat"],
  [/prevenir|evitar/i, "prevent"],
];

export function englishSearchTerms(query: string): string | null {
  const out: string[] = [];
  let rest = query;
  for (const [re, en] of PT_EN) {
    if (re.test(rest)) {
      rest = rest.replace(new RegExp(re.source, "gi"), " ");
      if (!out.includes(en)) out.push(en);
    }
  }
  return out.length ? out.join(" ") : null;
}

// English first-aid questions phrased as a story ("I just got bitten by a snake while hiking")
// share few words with the articles (Snakebite, Burn, Hypothermia): search with their names.
const EN_CANONICAL: Array<[RegExp, string]> = [
  [/\b(bitten|bit) by (a |an )?(snake|viper|rattlesnake|cobra)|\bsnake ?bites?\b/i, "snakebite snake bite"],
  [/\b(spill\w*|splash\w*|scald\w*|pour\w*)\b[^.]{0,40}\b(boiling|hot) (water|oil|coffee|tea)|\b(boiling|hot) (water|oil)[^.]{0,40}\b(spill\w*|scald\w*|burn\w*)|\bscalds?\b/i, "burn scald"],
  [/\bshiver\w*[^.]{0,80}\bcold\b|\bcold\b[^.]{0,80}\bshiver\w*/i, "hypothermia"],
  [/\bnose ?bleeds?\b|\bbleed\w*[^.?!]{0,20}\bnose\b|\bnose\b[^.?!]{0,20}\bbleed\w*/i, "nosebleed nose bleed"],
  // Any other bleeding ("My arm is bleeding a lot"): the articles' word, not the story's.
  [/\bbleed(s|ing)?\b/i, "bleeding"],
  [/\bchok(e|ing)\b/i, "choking"],
  // Earthquakes and floods: the question's own words find the "During an earthquake" sections better.
];
// No "first aid" added: it pulls in generic first-aid articles ("Mental health first aid").

/** Canonical English search words for an English first-aid question, or null. */
export function canonicalHealthTerms(query: string): string | null {
  const out = EN_CANONICAL.filter(([re]) => re.test(query)).map(([, t]) => t);
  // A nosebleed is not generic bleeding (it would pull in "Emergency bleeding control").
  if (out.includes("nosebleed nose bleed")) out.splice(out.indexOf("bleeding"), out.includes("bleeding") ? 1 : 0);
  if (!out.length) return null;
  return out.join(" ");
}
