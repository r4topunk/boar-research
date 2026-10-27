"""Generate REVIEWER-DECISIONS-6.{md,json} (opus-reviewer-2) and check the revised texts with safety v0.8.9."""
import json, re, sys, hashlib, copy, importlib.util, unicodedata
from pathlib import Path

D = Path("<workspace>/rnd/research/compass/exp/first-aid-cards")
sys.path.insert(0, str(D))
import round6  # noqa: E402

def sha(p): return hashlib.sha256((D / p).read_bytes()).hexdigest()
def st(text, *c): return {"text": text, "cites": list(c)}
def L(t, s, c): return {"title": t, "steps": s, "call": c}

R6 = {c["id"]: c for c in round6.build(st, L)}
CJ = {c["id"]: c for c in json.loads((D / "cards.json").read_text())["cards"]}
DATE = "2026-10-03"
REV = "opus-reviewer-2"

# ---------------------------------------------------------------- new / replacement source rows
NEW_ROWS = {
 # round 6 additions
 "CPR-ERC-CHILD": ("European Resuscitation Council, The ERC Guidelines 2025 on Resuscitation for Everyone (layperson book)", "https://www.erc.edu/media/p5ymaeej/gl2025_layperson_book_ipdf-v11-e.pdf",
    "When rescuing a child, the operator will direct the rescuer to start by immediately performing five rescue breaths. / The untrained rescuer should then begin performing CPR with a ratio of 30 compressions to two rescue breaths. / If the rescuer is hesitant, the dispatcher will guide them in the chest-compression-only technique.", "snapshots-rev6/erc-2025-layperson.txt", "ok (curl PDF → pdftotext, whitespace collapsed, line-break hyphens removed)"),
 "CPR-ERC-CALL": ("European Resuscitation Council, The ERC Guidelines 2025 on Resuscitation for Everyone (layperson book)", "https://www.erc.edu/media/p5ymaeej/gl2025_layperson_book_ipdf-v11-e.pdf",
    "If you are alone, make the call, put in speaker mode and place the phone near to you.", "snapshots-rev6/erc-2025-layperson.txt", "ok (paediatric section)"),
 "CPR-ERC-INFANT": ("European Resuscitation Council, The ERC Guidelines 2025 on Resuscitation for Everyone (layperson book)", "https://www.erc.edu/media/p5ymaeej/gl2025_layperson_book_ipdf-v11-e.pdf",
    "The ERC recommends the two-thumb encircling technique for performing chest compressions on infants because it is very effective, straightforward to do and is easily described over the phone by a dispatcher to an untrained rescuer.", "snapshots-rev6/erc-2025-layperson.txt", "ok; settles r6-infant-technique (with RCUK 2025; AHA 2025 also dropped two fingers, secondary sources only: AHA pages 403)"),
 "CPR-ERC-TEEN": ("European Resuscitation Council, The ERC Guidelines 2025 on Resuscitation for Everyone (layperson book)", "https://www.erc.edu/media/p5ymaeej/gl2025_layperson_book_ipdf-v11-e.pdf",
    "Since it is often hard to distinguish an adolescent and an adult, when in doubt, use directions for adults.", "snapshots-rev6/erc-2025-layperson.txt", "ok; trigger: route teen words to cpradult"),
 "CPR-ERC-ADULT": ("European Resuscitation Council, The ERC Guidelines 2025 on Resuscitation for Everyone (layperson book)", "https://www.erc.edu/media/p5ymaeej/gl2025_layperson_book_ipdf-v11-e.pdf",
    "each compression must push the chest down 5 to 6 cm.", "snapshots-rev6/erc-2025-layperson.txt", "ok; settles r6-adult-depth"),
 "CPR-RCUK-BABY-PUSH": ("Resuscitation Council UK, How to do CPR (baby)", "https://www.resus.org.uk/public-resource/how-do-cpr",
    "Use the two-thumb encircling technique for infants: place both thumbs together in the centre of the chest with the hands encircling the chest and fingers on the baby’s back. / Push down about a third of the depth of the chest (4 cm) and then release. / Use the one-hand or two-hand technique in children older than 1 year, or when unable to give high-quality chest compressions with the two-thumb-encircling technique.", "snapshots-6/rcuk-howcpr.txt", "ok (already in the round-6 snapshot)"),
 "CPR-RCUK-BABY-CALL": ("Resuscitation Council UK, How to do CPR (baby)", "https://www.resus.org.uk/public-resource/how-do-cpr",
    "Put the phone on loudspeaker and tell them you are with a baby who is not responding.", "snapshots-6/rcuk-howcpr.txt", "ok (already in the round-6 snapshot)"),
 # MedlinePlus replacements
 "SCORPA-WASH-SP": ("Secretaria de Estado da Saúde de São Paulo (CVE), Acidentes com escorpiões (alerta à população)", "https://www.saude.sp.gov.br/resources/cve-centro-de-vigilancia-epidemiologica/areas-de-vigilancia/doencas-de-transmissao-por-vetores-e-zoonoses/escorpiao-evento/alerta23_populacao_escorpiao.pdf",
    "Limpar o local com água e sabão", "snapshots-rev6/sessp-escorpiao.txt", "ok; replaces SCORPA-CARE / SCORPA-CARE-ES (washing)"),
 "SCORPA-SIGNS-SP": ("Secretaria de Estado da Saúde de São Paulo (CVE), Acidentes com escorpiões (alerta à população)", "https://www.saude.sp.gov.br/resources/cve-centro-de-vigilancia-epidemiologica/areas-de-vigilancia/doencas-de-transmissao-por-vetores-e-zoonoses/escorpiao-evento/alerta23_populacao_escorpiao.pdf",
    "sonolência, tremores, produção excessiva de saliva (começa a babar).", "snapshots-rev6/sessp-escorpiao.txt", "ok; replaces SCORPA-SEVERE (drooling, shaking)"),
 "SCORPA-SEVERE-BR": ("Ministério da Saúde (BR), Acidentes por Escorpiões", "https://www.gov.br/saude/pt-br/assuntos/saude-de-a-a-z/a/animais-peconhentos/acidentes-por-escorpioes",
    "há presença de uma ou mais das seguintes manifestações: vômitos profusos e incoercíveis, sudorese profusa, sialorreia intensa, prostração, convulsão, coma, bradicardia, insuficiência cardíaca, edema pulmonar agudo e choque.", "snapshots-rev6/ms-escorpioes.txt", "ok (severe form); replaces SCORPA-SEVERE (convulsions/jerking, drooling, sweating, vomiting)"),
 "SEA-STINGRAY-SJWA": ("St John Ambulance Western Australia, Marine stings (stingray)", "https://www.stjohnwa.com.au/online-resources/first-aid-information-and-resources/marine-stings",
    "Stingray Urgent medical aid. Call Triple Zero (000) for an ambulance. / DO NOT remove the embedded stingray spines especially from an injury to the chest, abdomen, neck, head, groin, or bone. This is a medical emergency.", "snapshots-rev6/sjwa-marine.txt", "ok (page heading 'Stingray' and the 'DO NOT' label joined by whitespace collapse); replaces SEA-CHEST-MEDL. NOTE: St John WA calls 000 for EVERY stingray injury (stricter than NHS minor-injuries tier)"),
 "SEA-STINGRAY-PC": ("Poison Control, National Capital Poison Center (US), Stingray injuries: prevention and treatment", "https://www.poison.org/articles/how-to-prevent-and-treat-stingray-injuries-201",
    "Death is extremely rare and results not from the venom but from the puncture wound itself if it is in the chest, abdomen, or neck. / Medical evaluation and treatment in a hospital is necessary if there are any retained spines in the wound, if the puncture is deep, or if it involves the chest, abdomen, or neck.", "snapshots-rev6/pc-stingray.txt", "ok; replaces SEA-CHEST-MEDL (second source)"),
 "SEA-DEEP-HD": ("healthdirect (AU), Sea creature bites and stings", "https://www.healthdirect.gov.au/sea-creature-stings",
    "If you have a deep wound or a lot of pain go to the hospital.", "snapshots-rev6/hd-sea.txt", "ok (fish/stingray section)"),
}

def verify_rows():
    norm = lambda s: re.sub(r"\s+", " ", unicodedata.normalize("NFKC", s)).strip()
    bad = []
    for k, (org, url, q, snap, flag) in NEW_ROWS.items():
        t = norm((D / snap).read_text())
        for piece in q.split(" / "):
            if norm(piece) not in t: bad.append((k, piece[:60]))
    return bad

REMOVED = {
 "SCORPA-CARE": "MedlinePlus EN (A.D.A.M.) 002850. Washing → SCORP-2 + SCORPA-WASH-SP. 'Keep the limb still' and 'remove rings' → no allowed scorpion source found (Brazil MS/SES-SP, Mexico CONAPRA/Guanajuato/NOM-033, Saudi MOH scorpion section, CDC/NIOSH): both clauses DROPPED from scorpion + scorpionadult.",
 "SCORPA-CARE-ES": "MedlinePlus ES (A.D.A.M.) 002850. Same as SCORPA-CARE; ES cards now cite SCORP-4 / SCORP-2 / SCORPA-WASH-SP.",
 "SCORPA-ICE": "MedlinePlus EN. Only used by the scorpionadult ALTERNATIVE (ice 10 on/10 off), which decision scorpa-cold keeps off the card. Alternative trimmed to CDC/NIOSH wording (SCORPA-CDC); '10 minutes on/off' dropped.",
 "SCORPA-US": "MedlinePlus EN. Conflict note only (US 'most stings need no treatment'); no card text depends on it. Delete; decision scorpa-when (stricter Brazil/Mexico tier) stands on SES-SP/MS/Mexico rows.",
 "SCORPA-SEVERE": "MedlinePlus EN. scorpionadult call line → SCORPA-911-MX + SCORPA-SIGNS-BR + SCORPA-SEVERE-BR (convulsão, sialorreia, sudorese, vômitos) + SCORPA-SIGNS-SP (tremores, babar). Call text unchanged.",
 "SEA-CHEST-MEDL": "MedlinePlus EN 002849 (stingray). marinepuncture call line → SEA-STINGRAY-SJWA + SEA-STINGRAY-PC (+ SEA-DEEP-HD for 'deep wound'). Call text unchanged.",
}

# ---------------------------------------------------------------- decisions
DEC = [
 ("r6-child-order", "cprchild, cprinfant", "breaths-first",
  "Keep 5 rescue breaths first, then 30:2. ERC 2025 lay guidance ('the operator will direct the rescuer to start by immediately performing five rescue breaths'), RCUK 2025, St John UK and British Red Cross agree, and the drowning card already does it. Paediatric arrest is usually hypoxic. AHA (compressions first) and ANZCOR/healthdirect differ; there the call handler will guide. Change: an untrained or hesitant rescuer must never freeze at the breaths step, so step 'give 5 breaths' now ends with 'If you can't or won't give breaths, go straight to pressing on the chest' (BRC, healthdirect, ERC compression-only fallback)."),
 ("r6-infant-technique", "cprinfant", "two-thumbs",
  "Change to two-thumb encircling, with heel of one hand as the fallback. ERC 2025 ('recommends the two-thumb encircling technique … easily described over the phone … to an untrained rescuer'), RCUK 2025 public page (verbatim in snapshots-6) and AHA 2025 (two-finger no longer recommended; secondary sources, AHA site 403) all moved away from two fingers, which gives compressions that are too shallow. The two-finger sources (SJA, BRC, healthdirect, MS 2016 protocol, AR) predate 2025. Fallback 'heel of one hand' = RCUK one-hand clause + healthdirect 'you may need to use one hand'. Consistency: chokinginfant still says two fingers for CHEST THRUSTS (a different manoeuvre); ERC 2025 reportedly moved those to thumbs too (not verified from primary text): follow-up item, see residual risks."),
 ("r6-infant-aed", "cprinfant", "nothing",
  "Keep: say nothing about an AED on the infant card. ERC 2025/RCUK allow an AED (paediatric mode if available) in infants; healthdirect (ANZCOR) says 'Do not use an AED on children under 1 year of age'. Direct regional conflict, so region-neutral wins: the card already says to stay on the line and follow the call handler, who decides. The AED only shocks a shockable rhythm, so a bystander who follows its prompts is not exposed to a new hazard."),
 ("r6-adult-depth", "cpradult", "5-6cm",
  "Keep 'about 5 to 6 cm'. ERC 2025 lay ('each compression must push the chest down 5 to 6 cm'), St John UK, MS Brazil, Argentina MS; AHA 2025 = at least 5 cm, not more than 6 cm. 'About a third' (healthdirect) is for children in most sources and harder for adults. Add CPR-ERC-ADULT to step 3's cites."),
 ("r6-lone-rescuer", "cprchild, cprinfant", "call-first-1-minute-fallback",
  "Keep '1 minute of CPR before calling' (SJA, BRC; not Argentina's 2 minutes) but only as the fallback when you can't call hands-free. Default for a lone rescuer = call immediately on speaker, phone next to you, then start (ERC 2025 lay 'If you are alone, make the call, put in speaker mode', RCUK 2025, and the same as the adult card). The dispatcher then coaches the untrained rescuer through breaths and compressions, which matters most for children. Baby: 'taking the baby with you' kept for the no-speaker case (SJA)."),
 ("r6-child-age", "cprchild", "over-1-year",
  "Keep the title 'over 1 year' (RCUK 1–18; ERC child 1–12). Trigger: route explicit adolescent words (teen, teenager, adolescent, adolescente) to cpradult, per ERC 2025 'when in doubt, use directions for adults'. 'son/daughter' may stay on the child card: the card already says to use two hands for a big child, and 5 initial breaths in a teenager are harmless."),
 ("r6-pois-drink", "poisoning", "nothing",
  "Keep: nothing to eat or drink, not even water or milk, unless the poison centre or emergency service says so (NHS, St John, BRC, CIATox-ES, Cruz Roja AR; same as the battery card). The poison.org caustic exception is NOT adopted, not even as an alternative: it is US-only, applies to a narrow case (caustic, fully awake, can swallow) that a lay bystander can't reliably judge, and 'milk' feeds the 'neutralise it' myth. For safety v0.9 (Compass): 'give milk/water' with no poison-centre/emergency-advice condition = UNSAFE; any 'dilute/neutralise' framing = UNSAFE; a drink explicitly conditioned on poison-centre or emergency-service advice = no fire."),
 ("r6-pois-tier", "poisoning", "as-drafted",
  "Keep as drafted: emergency services or a poison centre now, even if they seem fine; emergency services at once for drowsiness/unresponsiveness, breathing trouble or seizure; emergency first in the call line (NHS, BRC, SJA, healthdirect, poison.org). Change: delete the sentence 'Many countries have a poison information line.' It is an unsourced generalisation from 4 countries, and without a number it gives the reader nothing to do (no inline numbers on cards)."),
 ("r6-pois-skin-time", "poisoning", "15-min",
  "Add 'for at least 15 minutes' to the skin rinse (poison.org, already quoted in POIS-PC-SKIN). A stop time prevents the known short-rinse error, which the checker already treats as a hazard for eyes (eye-short-rinse). 'At least 15' doesn't contradict the 20 minutes on the eye and burn cards."),
 ("r6-medlineplus", "scorpion, scorpionadult, marinepuncture (rounds 4–5); round 6 uses none", "replace",
  "Replace every MedlinePlus row; none stays. The A.D.A.M. footer forbids automated access and any AI use, so the rows can't be kept as citations. 6 rows removed: SCORPA-CARE, SCORPA-CARE-ES, SCORPA-ICE, SCORPA-US, SCORPA-SEVERE, SEA-CHEST-MEDL. Replacements, all fetched with curl on 2026-10-03 and exact substrings of snapshots-rev6/: SCORPA-WASH-SP, SCORPA-SIGNS-SP (SES-SP), SCORPA-SEVERE-BR (Ministério da Saúde), SEA-STINGRAY-SJWA (St John WA), SEA-STINGRAY-PC (poison.org), SEA-DEEP-HD (healthdirect). Where no allowed source exists, the text was rewritten: 'keep the stung arm or leg still' (both scorpion cards) and 'take off rings' (adult) are dropped. This reverses decision scorpa-still, which rested only on MedlinePlus. Also: delete the MedlinePlus mentions in round5.py/round6.py review_flags and gen_sources.py, and do not fetch medlineplus.gov again."),
]

# ---------------------------------------------------------------- card verdicts + exact edits
E = lambda where, en, pt, es, cites: {"where": where, "en": en, "pt": pt, "es": es, "cites": cites}
CARDS = {
 "cpradult": ("change",
  "Medically correct against ERC 2025 lay guidance, RCUK, St John and healthdirect: check → call on speaker → push hard and fast 5–6 cm at 100–120/min → breaths only if trained → AED → recovery position. EN and PT approved as written. ES only: 'durante hasta 10 segundos' is clumsy, so it is reworded. Add CPR-ERC-ADULT to step 3.",
  [E("step 1 (ES only)", "(unchanged)", "(unchanged)",
     "Compruebe si responde: sacuda sus hombros con suavidad y pregúntele en voz alta si está bien. Incline la cabeza hacia atrás, levante el mentón y observe hasta 10 segundos si respira con normalidad. Las bocanadas aisladas (jadeos) no son respiración normal.",
     "CPR-SJA-CHECK, CPR-BRC-GASP, CPR-RCUK-CALL, CPR-AR-ADULT"),
   E("step 3 (cites only)", "(unchanged)", "(unchanged)", "(unchanged)",
     "CPR-SJA-PUSH, CPR-BRC-PUSH, CPR-RCUK-PUSH, CPR-MS-ADULT, CPR-AR-ADULT, CPR-CRAR, CPR-ERC-ADULT")]),
 "cprchild": ("change",
  "Order kept (5 breaths first; decision r6-child-order). Changes: a lone rescuer calls first on speaker, with 1 minute of CPR only if they can't call hands-free (r6-lone-rescuer). The breaths step gets an explicit way out for a rescuer who can't or won't give breaths. ES step 1 reworded as on the adult card. Trigger: teen words → cpradult (r6-child-age).",
  [E("step 1 (ES only)", "(unchanged)", "(unchanged)",
     "Compruebe si el niño responde: llámelo por su nombre y tóquele los hombros. Incline la cabeza un poco hacia atrás, levante el mentón con dos dedos y observe hasta 10 segundos si respira con normalidad.",
     "CPR-BRC-CHILD-CHECK, CPR-RCUK-CHILD"),
   E("step 2 (replace)",
     "If they're not breathing normally, ask someone to call emergency services. If you're alone, call now with the phone on speaker next to you and start; if you can't use a speaker, give 1 minute of CPR first, then call.",
     "Se ela não respira normalmente, peça a alguém que ligue para a emergência. Se estiver sozinho, ligue já com o celular no viva-voz ao seu lado e comece; se não tiver viva-voz, faça 1 minuto de RCP antes de ligar.",
     "Si no respira con normalidad, pida a alguien que llame a emergencias. Si está solo, llame ya con el teléfono en altavoz a su lado y empiece; si no tiene altavoz, haga 1 minuto de RCP antes de llamar.",
     "CPR-ERC-CALL, CPR-RCUK-CHILD, CPR-SJA-CHILD-CALL, CPR-BRC-CHILD"),
   E("step 3 (replace)",
     "Give 5 rescue breaths: pinch the nose, seal your mouth over theirs and blow gently and steadily until the chest rises. If you can't or won't give breaths, go straight to pressing on the chest.",
     "Faça 5 respirações de resgate: tape o nariz, cubra a boca da criança com a sua e sopre devagar e de forma constante até o peito subir. Se não conseguir ou não quiser fazer as respirações, passe direto às compressões no peito.",
     "Dé 5 respiraciones de rescate: tápele la nariz, cubra su boca con la suya y sople de forma suave y constante hasta que el pecho suba. Si no puede o no quiere dar respiraciones, pase directamente a las compresiones en el pecho.",
     "CPR-SJA-CHILD-5, CPR-RCUK-CHILD-5, CPR-BRC-CHILD, CPR-ERC-CHILD")]),
 "cprinfant": ("change",
  "Compressions change to two thumbs with the hands around the chest, with the heel of one hand as the fallback (r6-infant-technique: ERC 2025, RCUK 2025, AHA 2025). A lone rescuer calls first on speaker (r6-lone-rescuer). The breaths step gets an explicit way out, and the repeat step a compression-only branch. Head tilt, mouth-and-nose seal, 4 cm and 100–120/min are correct. No AED line (r6-infant-aed). ES step 2 reworded.",
  [E("step 2 (ES only)", "(unchanged)", "(unchanged)",
     "Acueste al bebé boca arriba sobre una superficie firme. Incline la cabeza hacia atrás solo un poquito, hasta que la cara mire hacia arriba, y levante el mentón con la punta de un dedo; inclinarla demasiado puede cerrar el paso del aire. Observe hasta 10 segundos si respira con normalidad.",
     "CPR-SJA-BABY-AIRWAY, CPR-RCUK-BABY, CPR-HD-INFANT, CPR-AR-BEBE, CPR-BRC-BABY"),
   E("step 3 (replace)",
     "If the baby isn't breathing normally, ask someone to call emergency services. If you're alone, call now with the phone on speaker next to you and start; if you can't use a speaker, give 1 minute of CPR first, then call, taking the baby with you.",
     "Se o bebê não respira normalmente, peça a alguém que ligue para a emergência. Se estiver sozinho, ligue já com o celular no viva-voz ao seu lado e comece; se não tiver viva-voz, faça 1 minuto de RCP antes de ligar, levando o bebê com você.",
     "Si el bebé no respira con normalidad, pida a alguien que llame a emergencias. Si está solo, llame ya con el teléfono en altavoz a su lado y empiece; si no tiene altavoz, haga 1 minuto de RCP antes de llamar, llevando al bebé con usted.",
     "CPR-ERC-CALL, CPR-RCUK-BABY-CALL, CPR-SJA-BABY-CALL, CPR-BRC-BABY-CALL"),
   E("step 4 (replace)",
     "Give 5 rescue breaths: cover the baby's mouth and nose with your mouth and blow gently, just enough to make the chest rise. If you can't or won't give breaths, go straight to pressing on the chest.",
     "Faça 5 respirações de resgate: cubra a boca e o nariz do bebê com a sua boca e sopre de leve, só o bastante para o peito subir. Se não conseguir ou não quiser fazer as respirações, passe direto às compressões no peito.",
     "Dé 5 respiraciones de rescate: cubra la boca y la nariz del bebé con su boca y sople suavemente, solo lo necesario para que el pecho suba. Si no puede o no quiere dar respiraciones, pase directamente a las compresiones en el pecho.",
     "CPR-SJA-BABY-5, CPR-RCUK-BABY-5, CPR-BRC-BABY, CPR-AR-BEBE, CPR-ERC-CHILD, CPR-HD-UNTIL"),
   E("step 5 (replace)",
     "Then press 30 times in the centre of the chest: put both thumbs side by side there, with your hands around the chest and your fingers on the baby's back. Press down about a third of the chest's depth (about 4 cm), 100 to 120 times a minute, letting the chest come back up fully. If your hands don't fit around the chest, press with the heel of one hand.",
     "Depois faça 30 compressões no centro do peito: coloque os dois polegares lado a lado ali, com as mãos envolvendo o peito e os dedos nas costas do bebê. Afunde o peito cerca de um terço da altura (uns 4 cm), de 100 a 120 vezes por minuto, deixando o peito voltar totalmente. Se as suas mãos não conseguirem envolver o peito, use a base de uma mão.",
     "Luego haga 30 compresiones en el centro del pecho: ponga los dos pulgares juntos ahí, con las manos alrededor del pecho y los dedos en la espalda del bebé. Hunda el pecho alrededor de un tercio de su altura (unos 4 cm), de 100 a 120 veces por minuto, dejando que vuelva a subir del todo. Si sus manos no alcanzan a rodear el pecho, use el talón de una mano.",
     "CPR-RCUK-BABY-PUSH, CPR-ERC-INFANT, CPR-SJA-BABY-PUSH, CPR-HD-INFANT, CPR-MS-PED"),
   E("step 6 (replace)",
     "Give 2 gentle breaths and keep repeating 30 presses and 2 breaths (if you're not giving breaths, keep pressing without stopping) until help takes over or the baby starts breathing normally. If the baby starts breathing normally, hold them on their side (for example along your forearm) and keep checking their breathing.",
     "Faça 2 respirações leves e continue repetindo 30 compressões e 2 respirações (se não estiver fazendo as respirações, continue as compressões sem parar) até a equipe de socorro assumir ou o bebê voltar a respirar normalmente. Se ele voltar a respirar normalmente, segure-o de lado (por exemplo, apoiado no seu antebraço) e continue verificando a respiração.",
     "Dé 2 respiraciones suaves y siga repitiendo 30 compresiones y 2 respiraciones (si no está dando respiraciones, siga con las compresiones sin parar) hasta que la ayuda tome el relevo o el bebé vuelva a respirar con normalidad. Si vuelve a respirar con normalidad, sosténgalo de lado (por ejemplo, apoyado en su antebrazo) y siga comprobando su respiración.",
     "CPR-SJA-BABY-REPEAT, CPR-BRC-BABY, CPR-HD-INFANT, CPR-HD-UNTIL")]),
 "poisoning": ("change",
  "Correct and conservative: no vomiting, no food or drink, keep the packaging, call now even if they seem fine, side position or CPR if they stop responding, an emergency call line with red flags. Scope exclusions are right (battery, CO, food poisoning, eye splash → own cards). Changes: drop the unsourced 'many countries…' sentence (r6-pois-tier) and add 'at least 15 minutes' to the skin rinse (r6-pois-skin-time). The deliberate-overdose items must also get the crisis path (out of scope; see residual risks).",
  [E("step 4 (replace)",
     "Call emergency services or a poison centre now, even if they seem fine; don't wait for symptoms.",
     "Ligue para a emergência ou para um centro de informação toxicológica agora, mesmo que a pessoa pareça bem; não espere aparecerem sintomas.",
     "Llame ahora a emergencias o a un centro de toxicología, aunque la persona parezca estar bien; no espere a que aparezcan síntomas.",
     "POIS-BRC, POIS-HD-CALL, POIS-PC-HELP, POIS-SJA (ES + POIS-CRAR)"),
   E("step 6 (replace)",
     "If it's on the skin, protect your hands, take off soaked clothing and rinse the skin with lots of cool running water for at least 15 minutes. If it's in the eyes, use the chemical-in-the-eye card and start rinsing right away.",
     "Se o produto caiu na pele, proteja as mãos, tire a roupa molhada com ele e lave a pele com bastante água corrente fria por pelo menos 15 minutos. Se caiu nos olhos, use o cartão de produto químico no olho e comece a lavar já.",
     "Si el producto cayó en la piel, protéjase las manos, quítele la ropa mojada con el producto y enjuague la piel con abundante agua corriente fresca durante al menos 15 minutos. Si cayó en los ojos, use la tarjeta de producto químico en el ojo y empiece a enjuagar de inmediato.",
     "POIS-HD-FA, POIS-PC-SKIN, POIS-CIATOX-ES-GEN")]),
}

# licence edits on earlier-round cards (not re-verdicts; recorded under r6-medlineplus)
LIC = {
 "scorpion": [E("step 2 (replace; reverts scorpa-still)",
     "Keep the child calm and away from the scorpion.",
     "Acalme a criança e afaste-a do escorpião.",
     "Calme al niño y aléjelo del alacrán.", "SCORP-4")],
 "scorpionadult": [
   E("step 1 (replace)", "Stay calm and move away from the scorpion.", "Mantenha a calma e afaste-se do escorpião.",
     "Mantenga la calma y aléjese del alacrán.", "SCORP-4, SCORPA-CDC (ES: SCORP-4)"),
   E("step 2 (replace)", "Wash the sting with soap and water.", "Lave o local com água e sabão.",
     "Lave la picadura con agua y jabón.", "SCORP-2, SCORPA-WASH-SP"),
   E("call (cites only)", "(unchanged)", "(unchanged)", "(unchanged)",
     "SCORPA-911-MX, SCORPA-SIGNS-BR, SCORPA-SEVERE-BR, SCORPA-SIGNS-SP"),
   E("alt_steps (ice ALTERNATIVE; not on the card per scorpa-cold)",
     "For pain, put ice on the sting, but don't put the arm or leg in ice water.",
     "Para a dor, ponha gelo sobre a picada, mas não mergulhe o braço ou a perna em água gelada.",
     "Para el dolor, ponga hielo sobre la picadura, pero no meta el brazo o la pierna en agua helada.", "SCORPA-CDC")],
 "marinepuncture": [
   E("step 2 (cites only)", "(unchanged)", "(unchanged)", "(unchanged)", "SEA-SPINE, SEA-STONEFISH, BLEED-OBJECT, SEA-STINGRAY-SJWA"),
   E("call (cites only)", "(unchanged)", "(unchanged)", "(unchanged)", "SEA-CALL, SEA-STONEFISH, SEA-STINGRAY-SJWA, SEA-STINGRAY-PC, SEA-DEEP-HD")],
}

TRIGGERS = [
 "cprchild → cpradult for explicit adolescent words (teen, teenager, adolescent, adolescente, 'N years' ≥ 13 / 'N anos|años' ≥ 13); ERC 2025 'when in doubt, use directions for adults' (CPR-ERC-TEEN).",
 "Fix the drowning trigger for 'out of the hotel pool' (ed-en-051) so the water exclusion routes it to drowning, not cprchild.",
 "Fix the altitude trigger's ES 'hace' (= 'ago') false positive (ed-es-086).",
 "Deliberate overdose (ed-pt-101, ed-es-086, ed-en-042): the poisoning card AND the crisis/self-harm path must both run.",
]

SAFETY_V09 = [
 "r6-pois-drink (for Compass): exception NOT adopted. 'give (them) milk/water' with no poison-centre/emergency-advice condition → UNSAFE; 'to dilute/neutralise' framing → UNSAFE; a drink only 'if the poison centre/emergency service tells you' → no fire.",
 "infant set: 'heel of ONE hand' is now the card's sanctioned fallback for babies, so infant-cpr-hands must fire only on 'heel of (both|two) hands' / adult depth (5–6 cm); 'two fingers' is the pre-2025 official technique (SJA/BRC/healthdirect/MS): at most REVIEW, never UNSAFE.",
 "undertriage-unresponsive doctor regex: add PT 'lev\\w+ … ao médico' and ES 'lleve … (a ver a un|al) médico' (rule bug, REVIEW-6 #4) before shipping the CPR cards.",
 "Add cpr-delay / cpr-shallow and child-leave-to-call (status REVIEW) from REVIEW-6 #5/#7; poison-induce-vomit with PT 'faça (a pessoa|ele|ela) vomitar'.",
]

RISKS = [
 "No human clinical or native-speaker review; these are the highest-stakes cards in the set and the review is by an AI model. A first-aid trainer should read the 3 CPR cards before release.",
 "AHA 2025 positions (compressions-first C-A-B for children; two-finger infant technique removed) come from secondary summaries: cpr.heart.org and heart.org are 403 to curl and to the fetch tool. US users get a breaths-first child card; a US call handler may coach compressions first. Either order is lifesaving, and the card defers to the call handler.",
 "chokinginfant still says 'two fingers' for chest thrusts (prior decision infant-thrusts). ERC 2025 reportedly moved choking chest thrusts to two-thumb as well (secondary source; the primary ERC PLS text was 403). Recommend a follow-up review of chokinginfant step 2 with a verified ERC/RCUK quote. Until then the two cards use different hand positions for different manoeuvres. That isn't a contradiction, but a stressed parent could find it confusing.",
 "Infant AED: regional conflict (ERC/RCUK allow it, ANZCOR forbids it under 1 year); the card is silent and defers to the call handler.",
 "Scorpion cards lose 'keep the limb still' and 'take off rings' (no allowed source after MedlinePlus). Neither changes outcome, and the priority (get to care fast) is intact. Re-add only with an allowed official quote (e.g. a reachable Mexican Secretaría de Salud page; gob.mx/IMSS/Michoacán pages timed out or had TLS errors from here).",
 "marinepuncture: St John WA (new source) calls 000 for EVERY stingray injury, stricter than the card's NHS tier (minor-injuries unit unless red flags/deep/chest/belly). Not changed here (outside round 6). Flagged for the next pass.",
 "Poisoning: no numbers on the card. 'Poison centre' may mean nothing to a traveller, which is why emergency services come first. The deliberate-overdose cases need the crisis path in parallel.",
 "Trigger routing: 'son/daughter' always goes to the child card, even for an adult child. The card's 'two hands if big' limits harm, but adult CPR depth for a grown son is 5–6 cm vs 'about 5 cm/a third'. 'learn/course' in the same message suppresses the CPR card (REVIEW-6).",
 "New text is not yet checked with safety v0.9 (the rules don't exist yet). It passes v0.8.9 (see 'Checks'), but v0.8.9 has no infant/poison rules, so a clean v0.8.9 result says little here.",
 "Snapshot normalisation: the ERC lay book is a PDF (pdftotext, whitespace collapsed, line-break hyphens removed); on the St John WA page the 'Stingray' heading and the 'DO NOT' label join the sentence after whitespace collapse. Both are exact substrings of the saved snapshots-rev6 files, not of the raw HTML/PDF.",
 "MedlinePlus pages were fetched by automated tools in earlier rounds (SOURCES.raw-6 says round 6 fetched and then deleted them). Nothing from them remains cited after this pass. The card wording those rows supported was original wording, but a legal check of past use was not part of this review.",
 "check_cards.py / gen_sources.py will fail citations until the new rows (13) are merged into SOURCES and the 6 MedlinePlus rows are removed; round6.py's S6/SNAP6 need the 7 CPR rows and snapshots-rev6.",
]

def apply(cid, card, edits):
    c = copy.deepcopy(card)
    for e in edits:
        w = e["where"]
        if "cites only" in w or w.startswith("alt_steps"): continue
        for lg in ("en", "pt", "es"):
            t = e[lg]
            if t.startswith("(unchanged"): continue
            m = re.match(r"step (\d+)", w)
            if m: c["langs"][lg]["steps"][int(m.group(1)) - 1]["text"] = t
            elif w.startswith("call"): c["langs"][lg]["call"]["text"] = t
    return c

def safety(cards):
    S89 = D.parent / "safety-v089"
    spec = importlib.util.spec_from_file_location("sc", S89 / "safety_check.v0.8.9.py")
    sc = importlib.util.module_from_spec(spec); spec.loader.exec_module(sc)
    S = sc.load(rules_path=S89 / "rules.v0.8.9.json", overlay_path=S89 / "overlay.v0.4.json")
    text = lambda x: "\n".join([x["title"]] + [s["text"] for s in x["steps"]] + [x["call"]["text"]])
    out = []
    for c in cards:
        for lg in ("en", "pt", "es"):
            topic = sc.rules_by_topic(c["topic"][lg], S)
            rules = sorted(set(c.get("rules") or []) | set(topic))
            hits = sc.check(text(c["langs"][lg]), rules, S)
            u = [h for h in hits if h.get("status", "unsafe") == "unsafe"]; rv = [h for h in hits if h.get("status") == "review"]
            out.append((c["id"], lg, rules, len(u), len(rv), [(h["rule"], h.get("match")) for h in u + rv]))
    return out

if __name__ == "__main__":
    bad = verify_rows()
    revised = [apply(k, R6[k], CARDS[k][2]) for k in CARDS] + [apply(k, CJ[k], LIC[k]) for k in LIC]
    res = safety(revised)
    pt_num = [(c["id"], s["text"]) for c in revised for s in c["langs"]["pt"]["steps"] + [c["langs"]["pt"]["call"]]
              if re.search(r"SAMU|Bombeiros|Disque|\b(?:190|192|193|136|0800)\b|\d{4}[ -]?\d{4}", s["text"])]
    unsafe = sum(r[3] for r in res); review = sum(r[4] for r in res)
    checks = {"new_rows_exact": f"{len(NEW_ROWS) - len({b[0] for b in bad})}/{len(NEW_ROWS)} rows, all pieces exact" if not bad else f"FAIL {bad}",
              "safety_v0.8.9_revised_texts": f"{len(res)} texts (4 round-6 cards + scorpion, scorpionadult, marinepuncture × EN/PT/ES): unsafe={unsafe}, review={review}",
              "pt_inline_numbers": pt_num or "none",
              "steps_per_card": {c["id"]: [len(c["langs"][lg]["steps"]) for lg in ("en", "pt", "es")] for c in revised}}
    for r in res:
        if r[3] or r[4]: print("HIT", r)
    print(json.dumps(checks, ensure_ascii=False, indent=1))

    inputs = {p: sha(p) for p in ["round6.py", "REVIEW-6.md", "SOURCES.raw-6.md", "conditionCards.v1.json", "cards.json", "REVIEWER-DECISIONS.json"]}
    J = {"reviewer": REV, "date": DATE,
         "inputs": inputs,
         "scope_note": "Round-6 cards are not in conditionCards.v1.json yet (REVIEW-6: not wired); reviewed from round6.py build() output = REVIEW-6.md text.",
         "decisions": {i: {"card": c, "choice": ch, "note": n} for i, c, ch, n in DEC},
         "cards": {k: {"choice": v[0], "note": v[1], "edits": v[2]} for k, v in CARDS.items()},
         "licence": {"removed_rows": REMOVED,
                     "new_rows": {k: {"org": v[0], "url": v[1], "quote": v[2], "snapshot": v[3], "flag": v[4], "fetched": DATE} for k, v in NEW_ROWS.items()},
                     "card_edits": LIC},
         "triggers": TRIGGERS, "safety_v0.9_notes": SAFETY_V09, "checks": checks, "residual_risks": RISKS}
    (D / "REVIEWER-DECISIONS-6.json").write_text(json.dumps(J, ensure_ascii=False, indent=1) + "\n")

    # ---------------- markdown
    md = []
    nA = sum(1 for v in CARDS.values() if v[0] == "approve"); nC = sum(1 for v in CARDS.values() if v[0] == "change"); nR = sum(1 for v in CARDS.values() if v[0] == "reject")
    md.append(f"# First-aid cards round 6: independent reviewer decisions ({REV}, {DATE})\n")
    md.append(f"TL;DR: **{len(DEC)} decisions** made (the 9 r6 flags plus the MedlinePlus licence decision). **4 cards** reviewed: **{nA} approved, {nC} changed, {nR} rejected**. "
              "Main calls: child/infant keep **5 rescue breaths first**, with an explicit 'can't or won't → go straight to pressing' fallback. Infant compressions switch to **two thumbs with the hands around the chest** (ERC 2025, RCUK 2025, AHA 2025). A lone rescuer **calls first on speaker**. Poisoning: **no drinks** (poison.org exception not adopted). "
              "**All 6 MedlinePlus rows are replaced or removed** (13 new verbatim rows, snapshots in `snapshots-rev6/`). This review is final (no human review will follow) and was done by an AI model: read the residual risks. "
              "Machine-readable twin: `REVIEWER-DECISIONS-6.json`. The choices are also recorded on the review artifact (collections `decisions`, `cards`; reviewer `opus-reviewer-2`).\n")
    md.append("Principles: same as REVIEWER-DECISIONS.md. Text must be safe for an untrained, stressed bystander in any country. Where sources conflict, the more conservative or region-neutral wording wins, and current 2025 resuscitation guidance (ERC/RCUK; AHA where readable) beats older lay pages. ES uses usted, neutral Latin-American Spanish. PT has no inline numbers. Every card says when to call. No dosing.\n")
    md.append("Inputs (sha256): " + ", ".join(f"`{k}` {v[:12]}…" for k, v in inputs.items()) + ". The round-6 cards are not in conditionCards.v1.json yet; the text reviewed is round6.py `build()`, which is the same as REVIEW-6.md.\n")
    md.append(f"## Decisions ({len(DEC)})\n")
    md.append("| id | card | choice | rationale |\n|---|---|---|---|")
    for i, c, ch, n in DEC: md.append(f"| `{i}` | {c} | **{ch}** | {n} |")
    md.append(f"\n## Cards ({len(CARDS)})\n")
    md.append("| key | verdict | summary |\n|---|---|---|")
    for k, v in CARDS.items(): md.append(f"| `{k}` | **{v[0]}** | {v[1]} |")
    md.append("\n### Exact edits (EN / PT / ES)\nStep numbers are the current round6.py card's. `(unchanged)` = keep that language as is. 'cites' = the citation ids the new text should carry (new rows below).\n")
    for k, v in CARDS.items():
        md.append(f"#### {k}")
        for e in v[2]:
            md.append(f"- **{e['where']}**  <sub>cites: {e['cites']}</sub>")
            for lg in ("en", "pt", "es"):
                if not e[lg].startswith("(unchanged"): md.append(f"  - {lg.upper()}: {e[lg]}")
        md.append("")
    md.append("## Licence: MedlinePlus rows replaced (r6-medlineplus)\n")
    md.append("MedlinePlus A.D.A.M. footer: no automated access and no AI use without written consent. Round 6 cites none. Earlier rounds cited 6 rows; every one is removed:\n")
    md.append("| removed row | what replaces it |\n|---|---|")
    for k, v in REMOVED.items(): md.append(f"| `{k}` | {v} |")
    md.append("\n### Replacement / new source rows (all curl 2026-10-03; exact substrings of the snapshot named)\n")
    md.append("| id | source | URL | exact quote | snapshot | note |\n|---|---|---|---|---|---|")
    for k, v in NEW_ROWS.items(): md.append(f"| `{k}` | {v[0]} | {v[1]} | \"{v[2]}\" | `{v[3]}` | {v[4]} |")
    md.append("\n### Card edits from the licence decision (earlier-round cards; prior verdicts otherwise stand)\n")
    for k, es in LIC.items():
        md.append(f"#### {k}")
        for e in es:
            md.append(f"- **{e['where']}**  <sub>cites: {e['cites']}</sub>")
            for lg in ("en", "pt", "es"):
                if not e[lg].startswith("(unchanged"): md.append(f"  - {lg.upper()}: {e[lg]}")
        md.append("")
    md.append("## Trigger changes\n" + "\n".join(f"- {t}" for t in TRIGGERS) + "\n")
    md.append("## Notes for safety v0.9 (Compass)\n" + "\n".join(f"- {t}" for t in SAFETY_V09) + "\n")
    md.append("## Checks (run by the reviewer on the revised text)\n```")
    md.append(json.dumps(checks, ensure_ascii=False, indent=1))
    md.append("```\nReproduce: `python3 reviewer6.py` (applies the edits above to round6.build() / cards.json and runs safety v0.8.9). After merging: `python3 round6.py`, `check_cards.py`.\n")
    md.append("## Residual risks\n" + "\n".join(f"- {t}" for t in RISKS) + "\n")
    md.append("Sources consulted for the decisions (not all are card citations): ERC Guidelines 2025 layperson book (erc.edu, read in full for the CPR sections); RCUK 'How to do CPR' 2025 (snapshots-6); St John UK, British Red Cross, healthdirect, MS Brazil SAMU, Argentina MS, Cruz Roja AR (round-6 snapshots); AHA 2025 positions via secondary summaries only (AHA 403).\n")
    (D / "REVIEWER-DECISIONS-6.md").write_text("\n".join(md))
    print("written")
