/**
 * Small talk answered without the model: a greeting, thanks, "who are you", the time. These never
 * get better from the library (classify.ts already skips retrieval for them), and on a phone a cold
 * model load plus generation is seconds for "hi". Deterministic, like the calculator and the emergency
 * numbers: same message, same reply. Anything else (a joke, a real question after "hi,") returns null
 * and goes the normal way.
 */

const norm = (s: string) =>
  s.trim().toLowerCase().normalize("NFD").replace(/[̀-ͯ]/g, "").replace(/[!.?~,;]+/g, " ").replace(/\s+/g, " ").trim();

type Kind = "hello" | "morning" | "afternoon" | "evening" | "night" | "howareyou" | "thanks" | "bye" | "ok";

const PHRASES: Array<[Kind, RegExp]> = [
  ["morning", /^(good morning|morning|bom dia)$/],
  ["afternoon", /^(good afternoon|boa tarde)$/],
  ["evening", /^(good evening|boa noite)$/],
  ["night", /^(good night|night)$/],
  ["howareyou", /^(how are you|how(?:'s| is) it going|how are things|what'?s up|sup|tudo (bem|bom|certo|joia)|como vai|como (voce )?esta|e ai|eai|beleza|blz)$/],
  ["thanks", /^(thanks?( you)?( so much| a lot)?|thx|ty|obrigad[oa]( mesmo)?|valeu|vlw|brigad[oa])$/],
  ["bye", /^(bye|goodbye|see ya|see you|tchau|ate mais|ate logo|falou)$/],
  ["ok", /^(ok(ay)?|cool|nice|great|perfect|got it|beleza|show|massa|legal|blz|certo|entendi)$/],
  ["hello", /^(hi|hello|hey|hey there|yo|hiya|oi|ola|ola tudo bem|opa|e ai boar|oi boar|hi boar|hello boar|hey boar)$/],
];

/** The kinds of every segment, or null when one segment isn't small talk ("hi, what is a monsoon"). */
function kinds(message: string): Kind[] | null {
  // Split before norm(), which turns the commas into spaces.
  const segments = message
    .split(/[,;]|\band\b/i)
    .map(norm)
    .filter(Boolean);
  if (!segments.length) return null;
  const out: Kind[] = [];
  for (const seg of segments) {
    const hit = PHRASES.find(([, re]) => re.test(seg));
    if (!hit) return null;
    out.push(hit[0]);
  }
  return out;
}

const ABOUT_RE =
  /^(what'?s? (is )?your name|who are you|what are you|what can you do|how can you help( me)?|how do you work|are you (an? )?(ai|bot|robot|human|real|person|online|offline)|qual (e )?(o )?seu nome|quem e voce|quem (e )?vc|o que (e )?voce|o que voce (faz|pode fazer)|como voce funciona|voce e (uma? )?(ia|robo|humano|pessoa))( please| por favor)?$/;
const TIME_RE = /^(what time is it|what'?s? (is )?the time|que horas sao|que hora e)( now| agora)?$/;
const DATE_RE = /^(what day is (it( today)?|today)|what'?s? (is )?today'?s date|what is the date( today)?|que dia e hoje|qual (e )?a data( de)? hoje)$/;

const PT_WORDS =
  /\b(oi|ola|opa|bom|boa|tudo|como|obrigad[oa]|brigad[oa]|valeu|vlw|tchau|ate|falou|beleza|blz|show|massa|legal|certo|entendi|eai|qual|quem|voce|vc|que|hoje|horas|seu)\b/;

const REPLY: Record<Kind, { en: string; pt: string }> = {
  hello: { en: "Hi! What would you like to know?", pt: "Oi! O que você quer saber?" },
  morning: { en: "Good morning! What would you like to know?", pt: "Bom dia! O que você quer saber?" },
  afternoon: { en: "Good afternoon! What would you like to know?", pt: "Boa tarde! O que você quer saber?" },
  evening: { en: "Good evening! What would you like to know?", pt: "Boa noite! O que você quer saber?" },
  night: { en: "Good night!", pt: "Boa noite!" },
  howareyou: { en: "All good, and ready offline. What would you like to know?", pt: "Tudo certo, e pronto offline. O que você quer saber?" },
  thanks: { en: "You're welcome!", pt: "De nada!" },
  bye: { en: "Bye! I'll be here, offline.", pt: "Tchau! Estou aqui, offline." },
  ok: { en: "Great. Ask me anything else.", pt: "Beleza. Pode perguntar mais." },
};

const ABOUT = {
  en: "I'm BOAR, a research assistant that runs entirely on this phone. I answer from the library on it (Wikipedia and the packs you installed) and show the sources behind each answer. Nothing you ask leaves the phone.",
  pt: "Sou o BOAR, um assistente de pesquisa que roda inteiro neste celular. Respondo a partir da biblioteca dele (a Wikipédia e os pacotes que você instalou) e mostro as fontes de cada resposta. Nada do que você pergunta sai do celular.",
};

export interface SmallTalkReply {
  text: string;
  kind: "greeting" | "about" | "time" | "date";
}

/** A reply for pure small talk, or null when the message needs the normal answer path. */
export function smallTalkReply(message: string, pt: boolean, now: Date = new Date()): SmallTalkReply | null {
  const n = norm(message);
  if (!n || n.length > 80) return null;
  // "oi" or "valeu" is too short for a language detector: the phrase itself says Portuguese.
  const lang = pt || PT_WORDS.test(n) ? "pt" : "en";
  if (ABOUT_RE.test(n)) return { kind: "about", text: ABOUT[lang] };
  if (TIME_RE.test(n)) {
    const t = now.toLocaleTimeString(lang === "pt" ? "pt-BR" : "en-US", { hour: "2-digit", minute: "2-digit" });
    return { kind: "time", text: lang === "pt" ? `São ${t}, pelo relógio deste celular.` : `It's ${t} by this phone's clock.` };
  }
  if (DATE_RE.test(n)) {
    const d = now.toLocaleDateString(lang === "pt" ? "pt-BR" : "en-US", { weekday: "long", year: "numeric", month: "long", day: "numeric" });
    return { kind: "date", text: lang === "pt" ? `Hoje é ${d}, pelo relógio deste celular.` : `Today is ${d}, by this phone's clock.` };
  }
  const k = kinds(message);
  if (!k) return null;
  // The reply of the most meaningful part: "hi, how are you?" answers how-are-you, "ok thanks" answers thanks.
  const order: Kind[] = ["howareyou", "thanks", "bye", "night", "morning", "afternoon", "evening", "hello", "ok"];
  const pick = order.find((o) => k.includes(o))!;
  return { kind: "greeting", text: REPLY[pick][lang] };
}
