"""Card-picker data (Sonar exp-30, health13): labels = the 31 card keys + snakebite + NONE.
Train: synthetic data (synth-*.jsonl tags mapped to keys; aligned contrast rows skipped) + terse-live (conds from its generator).
Eval: Compass emergency-dev positives (gold cond; round-5 splits resolved with the same rules the engine uses), card probes.
Writes picker/train.json, picker/eval.json: [{id, turns, y, src}]."""
import json, re
KEYS = set(json.load(open('<scratch>'))['cards']) | {'snakebite'}
INFANT = re.compile(r"(baby|infant|newborn|beb[êeé]|rec[ée]m.nascid|lactante|[0-9]{1,2} (months?|meses) old|(?<!gr[áa]vida )(?<!embarazada )de [0-9]{1,2} meses)", re.I)
CHILD = re.compile(r"\b(child|children|kids?|son|daughter|baby|toddler|boy|girl|crian[çc]as?|filh[oa]s?|menin[oa]s?|beb[êeé]s?|ni[ñn][oa]s?|hij[oa]s?|nene|[0-9]{1,2}.?(year|yr).?old|[0-9]{1,2} (anos|años))\b", re.I)
RIP = re.compile(r"(rip ?current|rip ?tide|riptide|undertow|current[^.?!]{0,30}(pull|drag|sweep|carr)|corrente de retorno|correnteza|repuxo|corriente de (resaca|retorno)|resaca|mar adentro|swept (out|away))", re.I)
POST = re.compile(r"(out of the (water|sea|ocean)|not breathing|isn'?t breathing|unconscious|unresponsive|\bcpr\b|n[ãa]o (est[áa] )?respira|no respira|inconsciente|desacordad|tir(amos|aram|ou)|sac(amos|aron))", re.I)
MAP = {'head_injury': 'headinjury', 'dive_neck_injury': None, 'snake_bite': 'snakebite', 'anaphylaxis': 'anaphylaxis', 'food_allergy_child': 'anaphylaxis',
       'chest_pain': 'heartattack', 'stroke': 'stroke', 'seizure': 'seizure', 'burn': 'burn', 'burn_scald': 'burn', 'altitude_sickness': 'altitude',
       'jellyfish_sting': 'jellyfish', 'hypoglycemia': 'hypoglycemia', 'electric_shock': 'electric', 'co_poisoning': 'co', 'chemical_eye': 'eyechem',
       'hypothermia': 'hypothermia', 'heat_stroke': 'heatstroke', 'heatstroke': 'heatstroke', 'nosebleed': 'nosebleed', 'earthquake': 'earthquake',
       'cut_bleeding': 'bleeding', 'bleeding': 'bleeding', 'bleeding_cut': 'bleeding', 'stingray_injury': 'marinepuncture', 'sea_urchin': 'marinepuncture',
       'tick_bite': 'tick', 'dog_bite': 'animalbite', 'animal_bite_rabies': 'animalbite', 'monkey_bite': 'animalbite', 'rabies_exposure': 'animalbite',
       'bat_exposure': 'animalbite', 'frostbite': 'frostbite', 'button_battery': 'battery', 'magnet_ingestion': 'battery', 'battery_ingestion': 'battery',
       'coin_ingestion': 'battery', 'bee_wasp_sting': 'beesting', 'tsunami': 'tsunami', 'tsunami_warning': 'tsunami'}
def split(key, text):
    if key == 'choking': return 'chokinginfant' if INFANT.search(text) else 'choking'
    if key == 'scorpion': return 'scorpion' if CHILD.search(text) else 'scorpionadult'
    if key == 'drowning': return 'ripcurrent' if RIP.search(text) and not POST.search(text) else 'drowning'
    return key
def label(tag, text):
    if tag in ('choking',): return split('choking', text)
    if tag == 'scorpion_sting': return split('scorpion', text)
    if tag == 'drowning': return split('drowning', text)
    return MAP.get(tag) or 'NONE'
train = []
for l in ('en', 'pt', 'es'):
    for x in map(json.loads, open(f'data/synth-{l}.jsonl')):
        y = label(x['tag'], ' '.join(x['turns'])) if x['label'] == 1 else 'NONE'
        train.append({'id': x['id'], 'turns': x['turns'], 'y': y, 'src': 'synth'})
conds = json.load(open('data/terse-live.conds.json'))
for x, c in zip(map(json.loads, open('data/terse-live.jsonl')), conds):
    y = split(c, ' '.join(x['turns'])) if c in KEYS or c in ('choking', 'scorpion', 'drowning') else 'NONE'
    if not x['emergency']: y = 'NONE'
    train.append({'id': x['id'], 'turns': x['turns'], 'y': y, 'src': 'terse'})
RIP_IDS = {'ed-es-048', 'ed-en-092', 'ed-pt-092', 'ed-en-051'}
ev = []
for d in map(json.loads, open('<workspace>/rnd/research/compass/exp/emergency-dev/dev.jsonl')):
    if d['emergency'] != 1: continue
    t = [u['text'] for u in d['turns'] if u['role'] == 'user']; c = d['cond'].replace('other:', '') if d['cond'] == 'other:snakebite' else d['cond']
    y = split(c, ' '.join(t)) if c in KEYS else 'NONE'
    if d['id'] in RIP_IDS: y = 'ripcurrent'  # Compass card-mismatch check: active rip currents (round-5 card), labelled drowning before it existed
    ev.append({'id': d['id'], 'turns': t, 'y': y, 'src': 'compass'})
for x in map(json.loads, open('cards/probes.cardpick.jsonl')):
    ev.append({'id': x['id'], 'turns': x['turns'], 'y': 'NONE' if x['expect'] == 'generic' else x['expect'], 'src': 'probe'})
json.dump(train, open('picker/train.json', 'w'), ensure_ascii=False); json.dump(ev, open('picker/eval.json', 'w'), ensure_ascii=False)
import collections
print('train', len(train), collections.Counter(x['y'] for x in train).most_common(40)); print('eval', len(ev), collections.Counter(x['y'] for x in ev).most_common(40))
