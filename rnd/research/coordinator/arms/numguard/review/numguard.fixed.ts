// NUMGUARD (coordinator arm, criterion arms/numguard 03587d67): a plain numeric question (a unit conversion, a clock time, an
// arithmetic word problem) never takes the learned detector's health refusal. Used only with NUMGUARD=1 (answer.ts).
import { calculate } from "./calculators";
import { isHealthQuestion, isSpanishQuestion } from "./context";
import { isCardEmergency } from "./conditionCards";

// arithmetic.ts HEALTH + DANGER (verbatim): health, injury, medication or body words, and situations rather than word problems.
const HEALTH =
  /\b(?:heart|pulse|bpm|breath\w*|blood|dos(?:e|es|age|ing)|mg|mcg|ml|iv|drip|infusion|insulin|tablets?|pills?|fever|contractions?|labou?r|pain\w*|bleed\w*|injur\w*|symptoms?|medic\w*|drugs?|overdos\w*|poison\w*|bab(?:y|ies)|toddlers?|infants?|calories?|kcal|glucose|oxygen|sp[o0]2)\b/i;
const DANGER =
  /\b(?:trapped|stuck|rising|flood\w*|fire|smoke|drown\w*|sinking|emergency|leak\w*|gas|danger\w*|unsafe|collaps\w*|avalanche|hurricane|tornado|lost|dying|dead|unconscious|attack\w*|bitten|bite|stung|hypotherm\w*|frostbite|choking|suicid\w*|kill\w*)\b/i;
// A short explicit list on top: people, care settings and symptoms the two lists above do not name.
const PERSON_CARE =
  /\b(?:pregnan\w*|child(?:ren)?|kids?|son|daughter|sick|ill|illness|hospital|doctor|nurse|vomit\w*|diarrh\w*|rash|cough\w*|headaches?|ache\w*|dizz\w*|nause\w*|thermometer|body temperature|my temperature|weigh(?:t|s)? loss|bmi|alcohol|drunk|safe(?:ly)?|hurt\w*|wound\w*|burn\w*|cpr|(?:my|his|her|their|your|our) (?:temp|temperature)|\d+[\s-]*(?:year|month|week|day)s?[\s-]*old|paracetamol|acetaminophen|ibuprofen|aspirin|tylenol|advil|benadryl|antibiotic\w*|amoxicillin|units? of|urin\w*|pee\w*|poop\w*|stool|toxic\w*|bleach|ingest\w*|swallow\w*|drank|drink\w*|beers?|wine|vodka|bac|sober|bp|blood pressure|saturation|unconscious|wake up|survive|surviv\w*|without (?:food|water)|fell|fall(?:s|en)?|hit (?:his|her|my|their)? ?head|faint\w*)\b/i;

const NUM = String.raw`\d[\d,]*(?:\.\d+)?`;
// A number followed by a unit, a currency or a percent.
const UNIT = new RegExp(
  String.raw`(?:[$€£¥]\s?${NUM}|${NUM}\s?(?:%|°\s?[cf]?\b|degrees?\b|(?:k?m|cm|mm|km\/h|kph|mph|mi|miles?|ft|feet|foot|inch(?:es)?|yards?|metres?|meters?|kilomet(?:re|er)s?|kg|g|lbs?|pounds?|ounces?|oz|tons?|tonnes?|l|litres?|liters?|gallons?|gal|pints?|cups?|bar|psi|kpa|hpa|mah|wh|kwh|w|watts?|v|volts?|amps?|hz|ghz|mhz|gb|mb|kb|tb|tokens?|bytes?|bits?|sec(?:ond)?s?|min(?:ute)?s?|h|hrs?|hours?|days?|weeks?|dollars?|euros?|usd|eur|gbp|cents?|btc|eth|sats?|gwei|coins?|million|billion|thousand)\b))`,
  "i"
);
const CLOCK = /\b\d{1,2}(?::\d{2}\s?(?:am|pm)?|\s?(?:am|pm))\b/i;
const OPERATOR =
  /(?:\d\s*[+\-×x*\/÷^]\s*\d|\b(?:plus|minus|times|multiplied|divided|percent(?:age)?|convert\w*|how many|how much|how long|how far|how fast|what time|in (?:fahrenheit|celsius|kelvin|psi|bar|mph|km\/h|feet|metres|meters|miles|kilometres|kilometers|pounds|kg|litres|liters|gallons|watt-hours|kwh|wh))\b)/i;

// A conversion target ("in psi", "to Celsius", "convert") or a clock question: the shape of a misfire, not of a situation.
const CONVERT =
  /\b(?:convert\w*|(?:in|to|into) (?:fahrenheit|celsius|kelvin|psi|bar|kpa|hpa|mph|km\/h|kph|feet|ft|inches|cm|mm|metres|meters|miles|kilomet(?:re|er)s|yards|pounds|lbs|kg|kilograms|grams|ounces|oz|litres|liters|gallons|pints|cups|ml|watt-hours|wh|kwh|euros?|dollars?|usd|eur|gbp))\b/i;
const HOW_MANY_UNIT =
  /\bhow many (?:kilomet(?:re|er)s|km|miles|feet|ft|metres|meters|inches|cm|yards|pounds|lbs|kg|kilograms|grams|ounces|oz|litres|liters|gallons|pints|cups|psi|watt-hours|wh|kwh) (?:is|are|in|make)\b/i;
const WHEN = /\b(?:what time|when (?:does|do|will|did)|arrive|arrives)\b/i;

/** True when the question names a health, injury, danger or person-care word: the detector's call stands. */
export function numguardHealthLexicon(query: string): boolean {
  return HEALTH.test(query) || DANGER.test(query) || PERSON_CARE.test(query) || isHealthQuestion(query) || isCardEmergency(query);
}

/** A number plus a unit, a clock time, a currency, a percent or an arithmetic / conversion operator. */
export function numericIntent(query: string): boolean {
  // Identifiers ("EIP-4444", "DS-160") and years or decades ("in 1900", "the 1600s", "mid-2012") are not quantities.
  const q = query.replace(/\b[A-Za-z]+-\d+\b/g, " ").replace(/\b(?:1[5-9]\d\d|20\d\d)s?\b/g, " ");
  if (!/\d/.test(q)) return false;
  return (UNIT.test(q) && (CONVERT.test(q) || HOW_MANY_UNIT.test(q))) || (CLOCK.test(q) && WHEN.test(q));
}

/** The guard: no health lexicon AND (a calculator match OR numeric intent). */
export function numericGuard(query: string, pt: boolean, userTurns: string[] = []): boolean {
  // EN only (the lexicon is English, like the arithmetic and travel shortcuts); any earlier user turn with a health word keeps the refusal.
  if (pt || isSpanishQuestion(query)) return false;
  if ([query, ...userTurns].some(numguardHealthLexicon)) return false;
  return calculate(query, pt) !== null || numericIntent(query);
}
