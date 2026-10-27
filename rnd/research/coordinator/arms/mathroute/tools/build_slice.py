"""MATHROUTE slice builder (0 LLM calls). Writes boar-eval/bench/slices/mathroute-v1/{questions.jsonl,gold.jsonl,NOTICE.md,SHA256SUMS}.
26 EN items: 2 public v0.1 items that took the calculator path on the POCO cut 7 run (vit-sci-003, vit-trv-004; question text copied
from bench/v0.1/questions.public.jsonl) + 24 agent-written (Claude Opus 5.5, 2026-10-15; dev data): 8 unit (u), 8 arithmetic word
problems (a), 8 trap (t: a plain number is the answer but the phrasing invites context). Written before reading calculators.ts /
arithmetic.ts (no tuning to the calculator's patterns).
gold: accept = [[value, abs_tol], ...] (any number in the answer within tol of any value), patterns = regexes (case-insensitive)
that also count as correct (clock times, 'h min' forms)."""
import json, hashlib, os
D = "<workspace>/boar-eval/bench/slices/mathroute-v1"
H = r"(?:h|hr|hrs|hour|hours)\.?,?\s*(?:and\s*)?"
I = [
 # id, group, question, accept, patterns, note
 ("vit-sci-003", "v01", "My phone generates 10 tokens per second and processes the prompt at 30 tokens per second. With 1,300 tokens of sources and a 400-token answer, how long until the answer is finished?",
  [[83.33, 1.0]], [r"1\s*(?:min|minute)s?\.?,?\s*(?:and\s*)?2[23]\s*(?:s|sec)", r"\b1:2[23]\b"], "1300/30 + 400/10 = 83.3 s (v0.1 rubric: 82-84 / 1 min 23)"),
 ("vit-trv-004", "v01", "How far is it to walk from Paris to Rome and back?",
  [[2800, 400]], [], "round trip 2,400-3,200 km (v0.1 rubric ~2,700-2,900 km, never < 2,000); km only"),
 ("mr-u01", "unit", "What is 25 °C in Fahrenheit?", [[77, 0.5]], [], "25*9/5+32"),
 ("mr-u02", "unit", "Convert 98.6 °F to Celsius.", [[37, 0.2]], [], "(98.6-32)*5/9"),
 ("mr-u03", "unit", "How many kilometres is 26.2 miles?", [[42.16, 0.15]], [], "26.2*1.609344"),
 ("mr-u04", "unit", "How many pounds is 70 kg?", [[154.32, 0.6]], [], "70*2.20462"),
 ("mr-u05", "unit", "What is -40 degrees Celsius in Fahrenheit?", [[-40, 0.5]], [r"minus\s*40", r"[-−]\s?40\s*°?\s*F", r"same\s+(?:number|value|temperature)"], "-40 C = -40 F"),
 ("mr-u06", "unit", "How many litres are in 5 US gallons?", [[18.93, 0.1]], [], "5*3.78541"),
 ("mr-u07", "unit", "My tyre pressure gauge says 2.2 bar. What is that in psi?", [[31.91, 0.4]], [], "2.2*14.5038"),
 ("mr-u08", "unit", "How many feet is 3,000 metres?", [[9842.5, 15]], [], "3000/0.3048"),
 ("mr-a01", "arith", "My car uses 6.5 litres per 100 km. How many litres do I need for a 420 km trip?", [[27.3, 0.2]], [], "6.5*4.2"),
 ("mr-a02", "arith", "A bus leaves at 9:40 and the trip takes 2 hours 35 minutes. What time does it arrive?", [], [r"\b12[:.]15\b"], "12:15"),
 ("mr-a03", "arith", "If 1 euro is 1.08 US dollars, how many euros do I get for 250 dollars?", [[231.48, 0.6]], [], "250/1.08"),
 ("mr-a04", "arith", "My power bank is 20,000 mAh at 3.7 V. How many watt-hours is that?", [[74, 0.5]], [], "20 Ah * 3.7 V"),
 ("mr-a05", "arith", "Using Naismith's rule, how long does a 12 km hike with 600 m of ascent take?", [[3.4, 0.05], [204, 1]], [r"3\s*" + H + r"24\s*(?:m|min)"], "12/5 h + 600/600 h = 3.4 h = 3 h 24 min"),
 ("mr-a06", "arith", "A jacket costs [usage detail removed] and is 35% off. What is the sale price?", [[52, 0.01]], [], "80*0.65"),
 ("mr-a07", "arith", "I walk at 5 km/h. How long does it take to walk 18 km?", [[3.6, 0.05], [216, 1]], [r"3\s*" + H + r"36\s*(?:m|min)"], "18/5 = 3.6 h = 3 h 36 min"),
 ("mr-a08", "arith", "A 60 W bulb runs 5 hours a day for 30 days. How many kWh is that?", [[9, 0.05], [9000, 1]], [], "60*5*30 = 9000 Wh = 9 kWh"),
 ("mr-t01", "trap", "Is 30 °C hot? What is it in Fahrenheit?", [[86, 0.5]], [], "30*9/5+32"),
 ("mr-t02", "trap", "I'm flying to the US and the forecast says 50 °F. What is that in Celsius, roughly?", [[10, 0.6]], [], "(50-32)*5/9"),
 ("mr-t03", "trap", "The speed limit on Italian motorways is 130 km/h. What is that in mph?", [[80.78, 0.6]], [], "130/1.609344"),
 ("mr-t04", "trap", "My baby's thermometer reads 38.5 °C. What is that in Fahrenheit?", [[101.3, 0.2]], [], "38.5*9/5+32 (health phrasing: detector may fire)"),
 ("mr-t05", "trap", "Mount Everest is 8,849 metres tall. How many feet is that?", [[29032, 30]], [], "8849/0.3048"),
 ("mr-t06", "trap", "Bitcoin's supply is capped at 21 million coins. If 19.8 million have been mined, what percentage is that?", [[94.29, 0.15]], [], "19.8/21 (crypto kit invites context)"),
 ("mr-t07", "trap", "Tokyo is 9 hours ahead of London. If it's 3 pm in London, what time is it in Tokyo?", [], [r"midnight", r"\b12(?::00)?\s*a\.?\s?m\b", r"\b0?0:00\b", r"\b24:00\b"], "15:00 + 9 h = 00:00 (midnight)"),
 ("mr-t08", "trap", "The Eiffel Tower is 330 m tall. How many times taller is it than a 1.8 m person?", [[183.3, 0.5]], [], "330/1.8"),
]
assert len(I) == 26 and len({i[0] for i in I}) == 26
q = "".join(json.dumps({"id": i, "group": g, "question": t, "lang": "en"}, ensure_ascii=False) + "\n" for i, g, t, *_ in I)
gl = "".join(json.dumps({"id": i, "accept": a, "patterns": p, "note": n}, ensure_ascii=False) + "\n" for i, g, t, a, p, n in I)
open(f"{D}/questions.jsonl", "w").write(q); open(f"{D}/gold.jsonl", "w").write(gl)
open(f"{D}/NOTICE.md", "w").write("# mathroute-v1 licence\n\nLicense: CC BY 4.0 (24 questions and gold values written by BOAR R&D agents, 2026-10-15). "
 "vit-sci-003 and vit-trv-004 are copied from bench/v0.1/questions.public.jsonl (same terms as there). Dev data, English only.\n")
s = "".join(f"{hashlib.sha256(open(f'{D}/{f}','rb').read()).hexdigest()}  {f}\n" for f in ("questions.jsonl", "gold.jsonl"))
open(f"{D}/SHA256SUMS", "w").write(s); print(s, end="")
